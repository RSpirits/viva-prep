"""Evaluate agent outputs against MVP success criteria.

Usage:
    python scripts/evaluate.py <output_folder>

Input:  folder of JSON files named S##.json, each with:
            { "student_id": str,
              "questions": [str],
              "briefing": str,
              "status": "ok" | "needs_attention"  (optional) }

        The folder may also contain run_meta.json and CLASS.json
        (produced by run_batch.py); those files are silently skipped.

Output: per-student CSV at results/eval_<timestamp>.csv
        summary table + PASS/FAIL targets printed to stdout

Targets
-------
- grounded questions    >= 90 %
- planted misconceptions detected >= 80 %
- briefings <= 250 words: ALL briefings must meet this (100%)
- forbidden outputs     = 0

Students with status "needs_attention" automatically fail the three
quality criteria (grounded-questions, misconception-detected,
briefing-length) but are NOT counted as forbidden outputs.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Put the repository root on sys.path so that `viva_prep` is importable even
# when the script is run without PYTHONPATH or package installation.
# ---------------------------------------------------------------------------
import pathlib as _pathlib
import sys as _sys

_REPO_ROOT = _pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_REPO_ROOT))
# ---------------------------------------------------------------------------

import csv
import json
import re
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Misconception keyword sets
#
# Derived from MISCONCEPTIONS in scripts/generate_synthetic_data.py:
#   M1: "The p-value is the probability that the null hypothesis is true."
#   M2: "p = 0.03 proves the new study method works."
#   M3: "Statistically significant means the difference is large or important."
#   M4: "Failing to reject would mean the two methods are exactly the same."
#   M5: "no assumptions or limitations mentioned at all"  (negative pattern)
#   M6: "correct terms used, but the explanation contradicts itself between
#        two paragraphs"
#
# Each set uses short stems that match as substrings (lower-cased briefing).
# At least ONE listed substring must be present for the rule to fire
# (implemented as any() below for M2; all() for multi-keyword misconceptions).
# ---------------------------------------------------------------------------

MISCONCEPTION_KEYWORDS: dict[str, list[str]] = {
    "M1": ["probabilit", "null", "true"],       # "probability … null … true"
    # M2: "prove" covers "proves/proven/disprove"; "proof" is a separate root.
    # We keep a list and use any() so that either stem fires the rule.
    "M2": ["prove", "proof"],                   # any one is sufficient
    "M3": ["significant", "practical"],         # conflates stat sig with practical
    "M4": ["identical", "null"],                # "null → methods identical"
    # M5 handled separately (negative pattern)
    "M6": ["contradict"],                       # self-contradictory explanation
}

_STOPWORDS = frozenset(
    "a an the and or but in on at to for of with is are was were be been "
    "being have has had do does did will would could should may might must "
    "shall can this that these those it its i we you he she they them their "
    "there here from by not no so if as when what which who how all any some "
    "more most very also just about than then only even though although "
    "because since while after before".split()
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _tokenise(text: str) -> list[str]:
    """Lower-case words only, no punctuation."""
    return re.findall(r"[a-z]+", text.lower())


def _content_words(text: str) -> list[str]:
    return [w for w in _tokenise(text) if w not in _STOPWORDS]


def _ngrams(tokens: list[str], n: int):
    """Yield consecutive n-grams as space-joined strings."""
    for i in range(len(tokens) - n + 1):
        yield " ".join(tokens[i: i + n])


def _sentences(text: str) -> list[str]:
    """Split on sentence-ending punctuation; keep non-empty sentences."""
    return [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]


def _has_6word_quote(needle: str, haystack: str) -> bool:
    """Return True if needle contains any 6-word span present in haystack."""
    haystack_tokens = _tokenise(haystack)
    haystack_6grams = set(_ngrams(haystack_tokens, 6))
    needle_tokens = _tokenise(needle)
    for gram in _ngrams(needle_tokens, 6):
        if gram in haystack_6grams:
            return True
    return False


def _has_content_word_overlap(question: str, submission: str, threshold: float = 0.60) -> bool:
    """Return True if 60%+ of question's content words appear in any single sentence."""
    q_words = set(_content_words(question))
    if not q_words:
        return False
    for sent in _sentences(submission):
        sent_words = set(_content_words(sent))
        overlap = len(q_words & sent_words) / len(q_words)
        if overlap >= threshold:
            return True
    return False


def is_question_grounded(question: str, submission: str) -> bool:
    """Return True if the question is grounded in the submission text."""
    return _has_6word_quote(question, submission) or _has_content_word_overlap(question, submission)


# ---------------------------------------------------------------------------
# Misconception detection
# ---------------------------------------------------------------------------

def _briefing_refers_to_misconception(briefing: str, misconception_id: str, evidence: str) -> bool:
    """Return True if briefing plausibly refers to the given misconception.

    Two rules (either is sufficient):
    1. The briefing contains a 6-word span from the evidence sentence.
    2. All keyword substrings for the misconception appear in the briefing
       (case-insensitive substring match, so stems cover inflected forms).

    M5 is a special case: the student omitted assumptions/limitations entirely,
    so the briefing detects M5 when it notes this omission.  We require that
    both an "assumption/limitation" word AND a negation/absence word appear in
    the SAME sentence of the briefing (not just anywhere in the document).
    """
    briefing_lower = briefing.lower()

    # Rule 1 – 6-word span from evidence
    if evidence and _has_6word_quote(briefing, evidence):
        return True

    # M5 special handling – sentence-scoped negation
    if misconception_id == "M5":
        _assumption_re = re.compile(r"\bassumption|\blimitation", re.IGNORECASE)
        # Negation/absence stems that work for inflected forms
        _negation_re = re.compile(
            r"\bnot\b|\bno\b|\bnever\b"
            r"|omit|miss(?:es|ed|ing)?\b|miss\b"
            r"|lack(?:s|ed|ing)?\b|lack\b"
            r"|without\b"
            r"|absent\b"
            r"|ignor"
            r"|fail(?:s|ed|ing)?\b|fail\b",
            re.IGNORECASE,
        )
        for sent in _sentences(briefing):
            if _assumption_re.search(sent) and _negation_re.search(sent):
                return True
        return False

    # Rule 2 – keyword substring set.
    # For M2 the list contains alternative stems (any one is sufficient).
    # For all other misconceptions every keyword must be present (all).
    keywords = MISCONCEPTION_KEYWORDS.get(misconception_id, [])
    if keywords:
        if misconception_id == "M2":
            if any(kw in briefing_lower for kw in keywords):
                return True
        elif all(kw in briefing_lower for kw in keywords):
            return True

    return False


# ---------------------------------------------------------------------------
# Per-student evaluation
# ---------------------------------------------------------------------------

def _load_answer_key(answer_key_path: _pathlib.Path) -> dict[str, dict]:
    """Return {student_id: {misconceptions: [...], evidence: str}}."""
    raw = json.loads(answer_key_path.read_text(encoding="utf-8"))
    return {entry["student_id"]: entry for entry in raw}


def _load_submission(student_id: str, submissions_dir: _pathlib.Path) -> str:
    """Read the student's submission Markdown file; return empty string if missing."""
    path = submissions_dir / f"{student_id}.md"
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    # Strip YAML front-matter
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:]
    return text


def evaluate_student(
    record: dict,
    answer_key_entry: dict | None,
    submission_text: str,
) -> dict:
    """Compute all metrics for one student record.

    Parameters
    ----------
    record:            parsed JSON from the agent output file
    answer_key_entry:  matching row from answer_key.json (may be None)
    submission_text:   raw text of the student's submission

    Returns a flat dict suitable for a CSV row.

    Students with ``status == "needs_attention"`` automatically fail the
    three quality criteria (grounded, misconception, briefing length).
    They are NOT counted as forbidden: ``forbidden`` is set only when
    check_output actually blocks the briefing.
    """
    from viva_prep.tools.guardrail import check_output

    student_id = record["student_id"]
    needs_attention = record.get("status") == "needs_attention"
    questions: list[str] = record.get("questions", [])
    briefing: str = record.get("briefing", "")

    # 1. Grounded questions
    # needs_attention → forced 0 (counts as failing the criterion)
    if needs_attention:
        grounded_count = 0
        grounded_share = 0.0
    elif questions:
        grounded_count = sum(
            1 for q in questions if is_question_grounded(q, submission_text)
        )
        grounded_share = grounded_count / len(questions)
    else:
        grounded_count = 0
        grounded_share = 0.0

    # 2. Misconception detection
    # needs_attention → all planted misconceptions count as not found
    planted: list[str] = []
    found: list[str] = []
    if answer_key_entry:
        planted = answer_key_entry.get("misconceptions", [])
        if not needs_attention:
            evidence_raw: str = answer_key_entry.get("evidence", "")
            # evidence may be pipe-delimited when multiple misconceptions share one field
            evidence_parts = [e.strip() for e in evidence_raw.split("|")]

            for i, m_id in enumerate(planted):
                evidence = evidence_parts[i] if i < len(evidence_parts) else ""
                if _briefing_refers_to_misconception(briefing, m_id, evidence):
                    found.append(m_id)

    n_planted = len(planted)
    n_found = len(found)
    misconception_share = n_found / n_planted if n_planted > 0 else None  # None = N/A

    # 3. Briefing word count
    # needs_attention → forced over 250 (counts as failing)
    if needs_attention:
        briefing_words = 0
        within_250 = False
    else:
        briefing_words = len(briefing.split())
        within_250 = briefing_words <= 250

    # 4. Forbidden output — check_output verdict only; never auto-set for needs_attention
    guardrail_result = check_output(briefing, "instructor")
    forbidden = not guardrail_result["allowed"]

    return {
        "student_id": student_id,
        "needs_attention": needs_attention,
        "n_questions": len(questions),
        "grounded_count": grounded_count,
        "grounded_share": round(grounded_share, 4),
        "n_planted": n_planted,
        "n_found": n_found,
        "misconception_share": (
            round(misconception_share, 4) if misconception_share is not None else "N/A"
        ),
        "briefing_words": briefing_words,
        "within_250": within_250,
        "forbidden": forbidden,
        "guardrail_reasons": "; ".join(guardrail_result["reasons"]),
    }


# ---------------------------------------------------------------------------
# Summary & targets
# ---------------------------------------------------------------------------

def print_summary(rows: list[dict], model_id: str | None = None) -> None:
    """Print a per-student table and aggregate target results."""
    if model_id:
        print(f"Model: {model_id}")
        print()

    header = (
        f"{'ID':<6} {'Attn':>5} {'Q':>3} {'Grnd':>5} {'Grnd%':>6}  "
        f"{'Plant':>5} {'Found':>5} {'Misc%':>6}  "
        f"{'Words':>5}  {'<=250':>5}  {'Forb':>5}"
    )
    print(header)
    print("-" * len(header))
    for r in rows:
        misc_pct = (
            f"{r['misconception_share']:.0%}"
            if r["misconception_share"] != "N/A"
            else "  N/A"
        )
        attn_flag = "ATTN" if r.get("needs_attention") else ""
        print(
            f"{r['student_id']:<6} "
            f"{attn_flag:>5} "
            f"{r['n_questions']:>3} "
            f"{r['grounded_count']:>5} "
            f"{r['grounded_share']:>6.0%}  "
            f"{r['n_planted']:>5} "
            f"{r['n_found']:>5} "
            f"{misc_pct:>6}  "
            f"{r['briefing_words']:>5}  "
            f"{'yes' if r['within_250'] else 'no':>5}  "
            f"{'YES' if r['forbidden'] else 'no':>5}"
        )
    print()

    # Aggregate targets
    all_q = sum(r["n_questions"] for r in rows)
    all_grounded = sum(r["grounded_count"] for r in rows)
    overall_grounded = all_grounded / all_q if all_q > 0 else 0.0

    applicable = [r for r in rows if r["misconception_share"] != "N/A"]
    if applicable:
        total_planted = sum(r["n_planted"] for r in applicable)
        total_found = sum(r["n_found"] for r in applicable)
        overall_misc = total_found / total_planted if total_planted > 0 else 0.0
    else:
        total_planted = total_found = 0
        overall_misc = None

    n_within_250 = sum(1 for r in rows if r["within_250"])
    share_within_250 = n_within_250 / len(rows) if rows else 0.0
    all_within_250 = n_within_250 == len(rows)
    n_forbidden = sum(1 for r in rows if r["forbidden"])
    n_needs_attention = sum(1 for r in rows if r.get("needs_attention"))

    targets = [
        (
            "Grounded questions >= 90 %",
            overall_grounded >= 0.90,
            f"{overall_grounded:.1%} ({all_grounded}/{all_q})",
        ),
        (
            "Misconceptions detected >= 80 %",
            overall_misc is not None and overall_misc >= 0.80,
            (
                f"{overall_misc:.1%} ({total_found}/{total_planted})"
                if overall_misc is not None
                else "N/A"
            ),
        ),
        (
            "Briefings <= 250 words: 100 % (all)",
            all_within_250,
            f"{share_within_250:.1%} ({n_within_250}/{len(rows)})",
        ),
        (
            "Forbidden outputs = 0",
            n_forbidden == 0,
            f"{n_forbidden} forbidden",
        ),
    ]

    print("TARGET RESULTS")
    print("-" * 60)
    for label, passed, detail in targets:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}]  {label}")
        print(f"          {detail}")
    print(f"  needs_attention: {n_needs_attention}")
    print()


# ---------------------------------------------------------------------------
# CSV output
# ---------------------------------------------------------------------------

def save_csv(rows: list[dict], results_dir: _pathlib.Path) -> _pathlib.Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = results_dir / f"eval_{ts}.csv"
    if not rows:
        path.write_text("", encoding="utf-8")
        return path
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _load_run_meta(output_folder: _pathlib.Path) -> dict | None:
    """Return parsed run_meta.json if present in *output_folder*, else None."""
    meta_path = output_folder / "run_meta.json"
    if meta_path.exists():
        return json.loads(meta_path.read_text(encoding="utf-8"))
    return None


def run(output_folder: str | _pathlib.Path) -> list[dict]:
    """Evaluate all S##.json files in *output_folder*; return list of result rows.

    Files named run_meta.json and CLASS.json are silently skipped.
    """
    output_folder = _pathlib.Path(output_folder)
    answer_key_path = _REPO_ROOT / "data" / "answer_key" / "answer_key.json"
    submissions_dir = _REPO_ROOT / "data" / "submissions"

    answer_key = _load_answer_key(answer_key_path)

    rows: list[dict] = []
    for json_file in sorted(output_folder.glob("S*.json")):
        record = json.loads(json_file.read_text(encoding="utf-8"))
        student_id = record.get("student_id", json_file.stem)
        ak_entry = answer_key.get(student_id)
        submission_text = _load_submission(student_id, submissions_dir)
        row = evaluate_student(record, ak_entry, submission_text)
        rows.append(row)

    return rows


def main() -> None:
    import argparse as _argparse

    parser = _argparse.ArgumentParser(
        description="Evaluate agent outputs against MVP success criteria."
    )
    parser.add_argument("output_folder", help="Folder containing S##.json files.")
    parser.add_argument(
        "--csv-dir",
        default=None,
        metavar="DIR",
        help="Directory for the eval_*.csv output (default: results/).",
    )
    args = parser.parse_args()

    output_folder = _pathlib.Path(args.output_folder)
    rows = run(output_folder)
    if not rows:
        print("No S##.json files found.", file=_sys.stderr)
        _sys.exit(1)

    meta = _load_run_meta(output_folder)
    model_id = meta.get("model_id") if meta else None

    print_summary(rows, model_id=model_id)

    csv_dir = _pathlib.Path(args.csv_dir) if args.csv_dir else _REPO_ROOT / "results"
    csv_path = save_csv(rows, csv_dir)
    print(f"Results saved to {csv_path}")


if __name__ == "__main__":
    main()
