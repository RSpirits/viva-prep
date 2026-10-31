"""Run the submission_only Viva Prep pipeline for every student, outside Orchestrate.

Usage:
    python scripts/run_batch.py --backend dummy
    python scripts/run_batch.py --backend dummy --out /tmp/my_run
    python scripts/run_batch.py --backend watsonx
    python scripts/run_batch.py --backend watsonx --limit 5
    python scripts/run_batch.py --backend watsonx --students S01,S05

Backends:
    dummy    Deterministic canned replies built from submission text, no network.
    watsonx  IBM watsonx.ai chat endpoint (Dallas region, urllib only).

Environment variables (watsonx backend):
    WATSONX_APIKEY        IBM Cloud API key
    WATSONX_PROJECT_ID    watsonx.ai project ID
    WATSONX_URL           watsonx.ai service URL
    WATSONX_MODEL_ID      Model identifier

Output folder: --out DIR  (default: results/run_<UTC timestamp>/)
    S##.json       Per-student result
    CLASS.json     Class-level insights
    run_meta.json  Run metadata
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Put the repo root on sys.path so that viva_prep is importable.
# ---------------------------------------------------------------------------
import pathlib as _pathlib
import sys as _sys

_REPO_ROOT = _pathlib.Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_REPO_ROOT))
# ---------------------------------------------------------------------------

import argparse
import hashlib
import json
import re
import time
from datetime import datetime, timezone

from viva_prep.tools.submissions import get_submission, list_submissions
from viva_prep.tools.guardrail import check_output


# ---------------------------------------------------------------------------
# Runtime note appended to every system message
# ---------------------------------------------------------------------------

_RUNTIME_NOTE = (
    "\n\nRuntime note: in this run all inputs are included in the user message, "
    "no tools are available, and the script itself runs check_output on your reply. "
    "Do not describe tool calls; reply with the JSON only."
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_prompt(name: str) -> str:
    """Read prompts/<name>.md and append the runtime note."""
    path = _REPO_ROOT / "prompts" / f"{name}.md"
    return path.read_text(encoding="utf-8") + _RUNTIME_NOTE


def _load_course_file(name: str) -> str:
    return (_REPO_ROOT / "data" / "course" / name).read_text(encoding="utf-8")


def _extract_json(text: str) -> dict:
    """Parse a JSON object from *text*.

    Tries in order:
    1. Strip a single ```json ... ``` or ``` ... ``` fence that wraps the
       entire text (original behaviour).
    2. Fall back to the substring from the first '{' to the last '}' and
       parse that — handles text before/after a bare JSON object.
    """
    stripped = text.strip()

    # Try full-text fence match first
    fenced = re.match(r"^```(?:json)?\s*([\s\S]+?)\s*```$", stripped)
    if fenced:
        return json.loads(fenced.group(1).strip())

    # Try direct parse (no wrapper at all)
    try:
        return json.loads(stripped)
    except json.JSONDecodeError:
        pass

    # Fall back: find the outermost { ... } and try that
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start != -1 and end != -1 and end > start:
        return json.loads(stripped[start: end + 1])

    # If nothing worked, re-raise a clear error
    raise json.JSONDecodeError("No JSON object found in text", stripped, 0)


def _hash_file(path: _pathlib.Path) -> str:
    """Return hex SHA-256 of a file."""
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest


# ---------------------------------------------------------------------------
# Backend interface
# ---------------------------------------------------------------------------

class _Backend:
    def chat(self, system: str, user: str) -> str:
        """Send a chat request and return the assistant text."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Dummy backend — deterministic, no network
# ---------------------------------------------------------------------------

class _DummyBackend(_Backend):
    """Produce canned JSON replies derived from the submission text."""

    BACKEND_NAME = "dummy"
    MODEL_ID = "dummy-model-v1"

    def chat(self, system: str, user: str) -> str:
        # Identify which agent is being called by looking for a distinctive
        # phrase in the system message.
        if "Question Planner" in system:
            return self._question_planner_reply(user)
        elif "Briefing Writer" in system:
            return self._briefing_writer_reply(user)
        elif "Class Insights" in system:
            return self._class_insights_reply(user)
        return json.dumps({"error": "unknown_agent"})

    # ------------------------------------------------------------------

    def _question_planner_reply(self, user: str) -> str:
        # Extract student_id from the user block header (e.g. "### S03 Submission")
        m = re.search(r"### (S\d{2}) Submission", user)
        student_id = m.group(1) if m else "S00"

        # Pull a quoted span from the submission text (first 80 chars after headers)
        # Find the submission section
        sub_match = re.search(r"### S\d{2} Submission\n([\s\S]{80,})", user)
        if sub_match:
            body = sub_match.group(1)
            # Grab 6 consecutive words
            words = body.split()
            if len(words) >= 6:
                quoted_span = " ".join(words[:6])
            else:
                quoted_span = " ".join(words)
        else:
            quoted_span = "the null hypothesis is true"

        questions = [
            {
                "question": (
                    f'Can you walk me through what you meant by '
                    f'"{quoted_span} ..." in your submission?'
                ),
                "quoted_span": quoted_span,
                "rubric_criterion": 1,
            },
            {
                "question": (
                    "What does statistical significance mean to you "
                    "in the context of this study?"
                ),
                "quoted_span": "statistical significance",
                "rubric_criterion": 2,
            },
            {
                "question": (
                    "How did you distinguish between statistical and practical "
                    "significance in your answer?"
                ),
                "quoted_span": "practical significance",
                "rubric_criterion": 3,
            },
        ]
        return json.dumps({"student_id": student_id, "questions": questions})

    def _briefing_writer_reply(self, user: str) -> str:
        m = re.search(r"### (S\d{2}) Submission", user)
        student_id = m.group(1) if m else "S00"

        sub_match = re.search(r"### S\d{2} Submission\n([\s\S]+?)(?:\n###|\Z)", user)
        if sub_match:
            body = sub_match.group(1).strip()
            first_sentence = re.split(r"[.!?]", body)[0].strip()
            if len(first_sentence) > 120:
                first_sentence = first_sentence[:120]
        else:
            first_sentence = "The student discussed the hypothesis test."

        briefing = (
            "Based on the submission only (no practice conversation). "
            f"The student demonstrates understanding of the p-value interpretation. "
            f'They wrote: "{first_sentence}." '
            "The student correctly identified that p = 0.03 leads to rejecting the null "
            "hypothesis at the 0.05 level. However, the relationship between statistical "
            "and practical significance could be developed further."
        )
        return json.dumps({
            "student_id": student_id,
            "mode": "submission_only",
            "briefing": briefing,
            "suggested_questions": [
                "Can you explain what the p-value represents in your own words?",
                "How would you distinguish statistical from practical significance here?",
            ],
            "findings": [
                {
                    "claim": "Student correctly interprets p = 0.03 as evidence against the null.",
                    "evidence_quote": first_sentence[:80],
                    "rubric_criterion": 1,
                    "confidence": "high",
                },
                {
                    "claim": "Practical significance not fully addressed.",
                    "evidence_quote": "",
                    "rubric_criterion": 3,
                    "confidence": "medium",
                },
            ],
        })

    def _class_insights_reply(self, user: str) -> str:
        # Count how many briefings appear in the user message
        n = len(re.findall(r"### S\d{2} Briefing", user))
        summary = (
            f"{n} student briefing(s) were reviewed for this round. "
            "Criterion 1 (2 students): Several students conflated the p-value with the "
            "probability that the null hypothesis is true. "
            "Criterion 3 (2 students): The distinction between statistical significance "
            "and practical significance was underexplored. "
            "Criterion 5 (2 students): Assumptions and limitations of the t-test were "
            "not mentioned. "
            "Consider revisiting the interpretation of p-values and effect size in the "
            "next lecture, building on the hypothesis testing notes."
        )
        return json.dumps({"summary": summary})


# ---------------------------------------------------------------------------
# watsonx backend — urllib only, no third-party libraries
# ---------------------------------------------------------------------------

class _WatsonxBackend(_Backend):
    """Call the watsonx.ai chat completions endpoint."""

    BACKEND_NAME = "watsonx"

    def __init__(self) -> None:
        import os
        import urllib.request
        import urllib.parse

        # Load .env if present (never logs the values)
        env_file = _REPO_ROOT / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = val

        self._project_id = os.environ["WATSONX_PROJECT_ID"]
        self._url = os.environ["WATSONX_URL"].rstrip("/")
        self.MODEL_ID = os.environ["WATSONX_MODEL_ID"]

        # Obtain IAM token — never log the API key or the token
        api_key = os.environ["WATSONX_APIKEY"]
        iam_data = urllib.parse.urlencode({
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "apikey": api_key,
        }).encode()
        req = urllib.request.Request(
            "https://iam.cloud.ibm.com/identity/token",
            data=iam_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            iam_resp = json.loads(resp.read().decode())
        self._token = iam_resp["access_token"]  # never printed or logged

        # Keep a reference so we can make HTTP calls in chat()
        self._urllib = urllib

    def chat(self, system: str, user: str) -> str:
        import urllib.request
        import urllib.error

        endpoint = f"{self._url}/ml/v1/text/chat?version=2024-05-31"
        # Fix 6: /ml/v1/text/chat uses top-level max_tokens and temperature,
        # not a nested "parameters" block (which is the /text/generation format).
        payload = json.dumps({
            "model_id": self.MODEL_ID,
            "project_id": self._project_id,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": 4000,
            "temperature": 0,
        }).encode()

        req = urllib.request.Request(
            endpoint,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._token}",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=180) as resp:
            result = json.loads(resp.read().decode())

        # watsonx chat response: result["choices"][0]["message"]["content"]
        return result["choices"][0]["message"]["content"]


# ---------------------------------------------------------------------------
# Backend factory
# ---------------------------------------------------------------------------

def _make_backend(name: str) -> _Backend:
    if name == "dummy":
        return _DummyBackend()
    elif name == "watsonx":
        return _WatsonxBackend()
    else:
        raise ValueError(f"Unknown backend: {name!r}")


# ---------------------------------------------------------------------------
# One LLM call with one retry on HTTP error or JSON parse failure
# ---------------------------------------------------------------------------

def _http_body(exc: Exception) -> str:
    """Short excerpt of an HTTP error body; watsonx.ai explains 4xx errors there."""
    try:
        body = exc.read().decode("utf-8", "replace").strip()  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        return ""
    import os
    for name in ("WATSONX_APIKEY", "WATSONX_PROJECT_ID", "WATSONX_URL"):
        val = os.environ.get(name)
        if val:
            body = body.replace(val, f"<{name}>")
    return f" - {body[:300]}" if body else ""


def _call_with_retry(backend: _Backend, system: str, user: str) -> tuple[dict | None, str | None]:
    """Return (parsed_dict, None) on success or (None, error_message) on failure."""
    import urllib.error

    last_err: str = ""
    for attempt in range(2):
        try:
            raw = backend.chat(system, user)
            parsed = _extract_json(raw)
            return parsed, None
        except urllib.error.HTTPError as exc:
            last_err = f"HTTP {exc.code}: {exc.reason}{_http_body(exc)}"
        except urllib.error.URLError as exc:
            last_err = f"URLError: {exc.reason}"
        except (json.JSONDecodeError, ValueError) as exc:
            last_err = f"JSON parse error: {exc}"
        except Exception as exc:  # noqa: BLE001
            last_err = f"Unexpected error: {type(exc).__name__}: {exc}"
        if attempt == 0:
            # Brief pause before retry
            time.sleep(1)

    return None, last_err


# ---------------------------------------------------------------------------
# Per-student pipeline
# ---------------------------------------------------------------------------

def _run_student(
    backend: _Backend,
    student_id: str,
    rubric: str,
    learning_objectives: str,
    lecture_notes: str,
    qp_system: str,
    bw_system: str,
) -> dict:
    """Run question_planner → briefing_writer → guardrail for one student.

    Returns a result dict suitable for writing to S##.json.

    status rules:
    - "needs_attention": model call failed or reply could not be parsed.
    - "ok": pipeline completed (guardrail.allowed may still be False).
    """
    sub = get_submission(student_id)
    if "error" in sub:
        return {
            "student_id": student_id,
            "questions": [],
            "briefing": "",
            "suggested_questions": [],
            "findings": [],
            "guardrail": {"allowed": True, "reasons": [], "text": ""},
            "status": "needs_attention",
            "error": f"get_submission returned error: {sub['error']}",
        }

    submission_text = sub["text"]

    # -----------------------------------------------------------------------
    # Step 1: question_planner
    # -----------------------------------------------------------------------
    qp_user = (
        f"### Rubric\n{rubric}\n\n"
        f"### Learning Objectives\n{learning_objectives}\n\n"
        f"### Lecture Notes\n{lecture_notes}\n\n"
        f"### {student_id} Submission\n{submission_text}"
    )
    qp_result, qp_err = _call_with_retry(backend, qp_system, qp_user)

    if qp_result is None:
        return {
            "student_id": student_id,
            "questions": [],
            "briefing": "",
            "suggested_questions": [],
            "findings": [],
            "guardrail": {"allowed": True, "reasons": [], "text": ""},
            "status": "needs_attention",
            "error": f"question_planner failed: {qp_err}",
        }

    question_objects: list[dict] = qp_result.get("questions", [])
    question_strings: list[str] = [q["question"] for q in question_objects if "question" in q]

    # -----------------------------------------------------------------------
    # Step 2: briefing_writer (submission_only mode)
    # -----------------------------------------------------------------------
    bw_user = (
        f"### Rubric\n{rubric}\n\n"
        f"### {student_id} Submission\n{submission_text}\n\n"
        f"### Planner Questions\n"
        + "\n".join(f"- {q}" for q in question_strings)
    )
    bw_result, bw_err = _call_with_retry(backend, bw_system, bw_user)

    if bw_result is None:
        return {
            "student_id": student_id,
            "questions": question_strings,
            "briefing": "",
            "suggested_questions": [],
            "findings": [],
            "guardrail": {"allowed": True, "reasons": [], "text": ""},
            "status": "needs_attention",
            "error": f"briefing_writer failed: {bw_err}",
        }

    briefing: str = bw_result.get("briefing", "")
    suggested_questions: list[str] = bw_result.get("suggested_questions", [])
    findings: list[dict] = bw_result.get("findings", [])

    # -----------------------------------------------------------------------
    # Step 3: guardrail on the briefing text field (Fix 3: not json.dumps)
    # Status stays "ok" regardless; guardrail.allowed=False is counted as
    # forbidden by evaluate.py (Fix 2).
    # -----------------------------------------------------------------------
    guardrail = check_output(briefing, "instructor")

    return {
        "student_id": student_id,
        "questions": question_strings,
        "briefing": briefing,
        "suggested_questions": suggested_questions,
        "findings": findings,
        "guardrail": guardrail,
        "status": "ok",
    }


# ---------------------------------------------------------------------------
# Class insights (Fix 4)
# ---------------------------------------------------------------------------

def _run_class_insights(
    backend: _Backend,
    student_results: list[dict],
    ci_system: str,
) -> dict:
    """Run the class_insights agent over all student briefings.

    Accepts either a plain-text reply (stored as {"summary": text}) or a
    JSON reply with a "summary" field.  Also runs check_output on the
    summary text with the instructor audience.
    """
    briefings_block = "\n\n".join(
        f"### {r['student_id']} Briefing\n{r['briefing']}"
        for r in student_results
        if r.get("briefing")
    )
    ci_user = f"### Student Briefings\n\n{briefings_block}"

    import urllib.error

    last_err: str = ""
    for attempt in range(2):
        try:
            raw = backend.chat(ci_system, ci_user)
            # Try to parse as JSON; if that fails, treat the whole reply as
            # plain text and wrap it.
            try:
                parsed = _extract_json(raw)
                summary = parsed.get("summary", raw.strip())
            except (json.JSONDecodeError, ValueError):
                summary = raw.strip()
            guardrail = check_output(summary, "instructor")
            return {"summary": summary, "guardrail": guardrail}
        except urllib.error.HTTPError as exc:
            last_err = f"HTTP {exc.code}: {exc.reason}{_http_body(exc)}"
        except urllib.error.URLError as exc:
            last_err = f"URLError: {exc.reason}"
        except Exception as exc:  # noqa: BLE001
            last_err = f"Unexpected error: {type(exc).__name__}: {exc}"
        if attempt == 0:
            time.sleep(1)

    return {"summary": "", "error": f"class_insights failed: {last_err}",
            "guardrail": {"allowed": True, "reasons": [], "text": ""}}


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def run(
    backend_name: str,
    limit: int | None = None,
    students: list[str] | None = None,
    out_dir: _pathlib.Path | str | None = None,
) -> _pathlib.Path:
    """Run the batch pipeline; return the output folder path.

    Parameters
    ----------
    backend_name:  "dummy" or "watsonx"
    limit:         process only the first N students
    students:      explicit list of student IDs to process
    out_dir:       output folder; defaults to results/run_<timestamp>
    """
    start_time = datetime.now(tz=timezone.utc)
    if out_dir is None:
        ts = start_time.strftime("%Y%m%dT%H%M%SZ")
        out_dir = _REPO_ROOT / "results" / f"run_{ts}"
    out_dir = _pathlib.Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    backend = _make_backend(backend_name)

    # Load course materials once
    rubric = _load_course_file("rubric.md")
    learning_objectives = _load_course_file("learning_objectives.md")
    lecture_notes = _load_course_file("lecture_notes_hypothesis_testing.md")

    # Load and augment system prompts once
    qp_system = _load_prompt("question_planner")
    bw_system = _load_prompt("briefing_writer")
    ci_system = _load_prompt("class_insights")

    # Determine student list
    all_students = [s["student_id"] for s in list_submissions()]
    if students:
        run_students = [s for s in all_students if s in students]
    else:
        run_students = all_students
    if limit is not None:
        run_students = run_students[:limit]

    # Per-student loop
    student_results: list[dict] = []
    for sid in run_students:
        result = _run_student(
            backend=backend,
            student_id=sid,
            rubric=rubric,
            learning_objectives=learning_objectives,
            lecture_notes=lecture_notes,
            qp_system=qp_system,
            bw_system=bw_system,
        )
        student_results.append(result)

        # Write per-student file
        out_file = out_dir / f"{sid}.json"
        out_data: dict = {
            "student_id": result["student_id"],
            "questions": result["questions"],
            "briefing": result["briefing"],
            "suggested_questions": result["suggested_questions"],
            "findings": result["findings"],
            "guardrail": result["guardrail"],
            "status": result["status"],
        }
        if "error" in result:
            out_data["error"] = result["error"]
        out_file.write_text(json.dumps(out_data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"  [{result['status'].upper():>13}]  {sid}")

    # Class insights
    ci_result = _run_class_insights(backend, student_results, ci_system)
    class_path = out_dir / "CLASS.json"
    class_path.write_text(json.dumps(ci_result, indent=2, ensure_ascii=False), encoding="utf-8")

    end_time = datetime.now(tz=timezone.utc)

    # Prompt file hashes
    prompts_dir = _REPO_ROOT / "prompts"
    prompt_hashes = {
        p.name: _hash_file(p)
        for p in sorted(prompts_dir.glob("*.md"))
    }

    n_ok = sum(1 for r in student_results if r["status"] == "ok")
    n_needs_attention = sum(1 for r in student_results if r["status"] == "needs_attention")

    model_id = getattr(backend, "MODEL_ID", "unknown")

    run_meta = {
        "backend": backend_name,
        "model_id": model_id,
        "prompt_hashes": prompt_hashes,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "n_students": len(student_results),
        "n_ok": n_ok,
        "n_needs_attention": n_needs_attention,
    }
    meta_path = out_dir / "run_meta.json"
    meta_path.write_text(json.dumps(run_meta, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nRun complete: {n_ok} ok, {n_needs_attention} needs_attention")
    print(f"Output: {out_dir}")
    return out_dir


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run Viva Prep submission_only pipeline for all students."
    )
    parser.add_argument(
        "--backend",
        choices=["dummy", "watsonx"],
        default="dummy",
        help="LLM backend to use (default: dummy).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        metavar="N",
        help="Process only the first N students.",
    )
    parser.add_argument(
        "--students",
        type=str,
        default=None,
        metavar="S01,S05",
        help="Comma-separated student IDs to process.",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        metavar="DIR",
        help="Output folder (default: results/run_<timestamp>).",
    )
    args = parser.parse_args()

    student_list: list[str] | None = None
    if args.students:
        student_list = [s.strip() for s in args.students.split(",") if s.strip()]

    run(
        backend_name=args.backend,
        limit=args.limit,
        students=student_list,
        out_dir=args.out,
    )


if __name__ == "__main__":
    main()
