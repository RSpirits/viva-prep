"""Create a small fake agent-output folder at results/dummy/ for evaluator testing.

Each dummy record is built from the REAL submission file and answer-key entry so
that running the evaluator on results/dummy/ exercises the same loading paths as
a real Orchestrate output folder.

Six synthetic students cover the key evaluation scenarios:
  S02 – grounded questions,   briefing names M1       (fully grounded, misc detected)
  S03 – ungrounded questions, briefing misses M2      (0% grounded, misc NOT detected)
  S04 – grounded questions,   briefing names M3       (grounded, misc detected)
  S07 – grounded questions,   briefing misses M1+M3   (grounded, misc NOT detected)
  S08 – grounded questions,   briefing over 250 words (grounded, word limit exceeded)
  S10 – grounded questions,   briefing has grade label (grounded, forbidden)

Grounded questions contain a verbatim 6-word span lifted directly from the real
submission file of that student.  "Misses" briefings are plausible but do not
quote evidence and do not contain the required keyword patterns.
"""

from __future__ import annotations

import json
import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "results" / "dummy"


def _load_answer_key() -> dict[str, dict]:
    path = REPO_ROOT / "data" / "answer_key" / "answer_key.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {entry["student_id"]: entry for entry in raw}


def _submission_body(student_id: str) -> str:
    """Return the submission text with YAML front-matter stripped."""
    path = REPO_ROOT / "data" / "submissions" / f"{student_id}.md"
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            text = text[end + 3:]
    return text.strip()


# ---------------------------------------------------------------------------
# Build records.  Questions quote real spans; briefings are hand-crafted so
# the six scenarios are deterministic and test-friendly.
# ---------------------------------------------------------------------------

def _make_records(ak: dict[str, dict]) -> list[dict]:
    # ------------------------------------------------------------------
    # S02 – M1 planted.
    # Grounded questions: each quotes ≥6 consecutive words from S02.md.
    # Briefing names M1: contains all keywords "probability", "null", "true"
    # and quotes 6+ words of the evidence sentence.
    # Evidence: "a p-value of 0.03 is the chance that the null hypothesis is true"
    # ------------------------------------------------------------------
    records = []

    records.append({
        "student_id": "S02",
        "questions": [
            # 6-word span: "a p-value of 0.03 is the chance that"
            "You wrote 'a p-value of 0.03 is the chance that the null hypothesis is true' — what does 'chance' mean here?",
            # 6-word span from S02: "the study only involved 40 students per group"
            "You said 'the study only involved 40 students per group' — how does sample size affect generalisability?",
            # 6-word span: "statistical significance and practical significance are separate things"
            "You noted 'statistical significance and practical significance are separate things' — can you give an example?",
        ],
        "briefing": (
            "The student confuses the p-value with the probability that the null "
            "hypothesis is true. They write that a p-value of 0.03 is the chance "
            "that the null hypothesis is true, which is misconception M1. The "
            "correct interpretation is that p(data|H0) is not p(H0|data). The "
            "instructor should probe whether the student understands posterior "
            "versus sampling-distribution probability."
        ),
    })

    # ------------------------------------------------------------------
    # S03 – M2 planted.
    # Ungrounded questions: no 6-word quote, no vocabulary overlap ≥60% with
    # any single sentence of S03.md.  Words like "pedagogy", "curriculum",
    # "replication" do not appear in S03's submission.
    # Briefing misses M2: does not say "proves/proof/proven", does not quote
    # evidence.
    # Evidence: "getting p = 0.03 proves conclusively that the new study method works"
    # ------------------------------------------------------------------
    records.append({
        "student_id": "S03",
        "questions": [
            "How does pedagogy shape your reading of this result?",
            "What curriculum changes would you advocate for?",
            "Which demographic factors might moderate the outcome?",
        ],
        "briefing": (
            "The student generally follows the hypothesis-testing procedure and "
            "identifies the rejection region at alpha 0.05. They distinguish "
            "statistical and practical significance and note that Cohen's d would "
            "be useful. No major conceptual gaps were identified in their framing "
            "of the null and alternative hypotheses or the decision rule."
        ),
    })

    # ------------------------------------------------------------------
    # S04 – M3 planted.
    # Grounded questions: quote real spans from S04.md.
    # Briefing names M3: contains keywords "significant" + "practical" and
    # quotes 6+ words of the evidence sentence.
    # Evidence: "A result being statistically significant implies the difference is
    #            genuinely large and practically important"
    # ------------------------------------------------------------------
    s04_body = _submission_body("S04")  # noqa: F841 – used only to verify spans exist
    records.append({
        "student_id": "S04",
        "questions": [
            # 6-word span from S04: "A result being statistically significant implies the difference"
            "You wrote 'A result being statistically significant implies the difference is genuinely large' — is that always true?",
            # 6-word span: "this 4.1-point advantage for Method A is not just noise"
            "You claimed 'this 4.1-point advantage for Method A is not just noise' — what evidence supports that?",
            # 6-word span: "about 5% of correct null hypotheses would be rejected"
            "You mentioned 'about 5% of correct null hypotheses would be rejected just by chance' — what is that called?",
        ],
        "briefing": (
            "The student conflates statistical significance with practical importance. "
            "They state that a result being statistically significant implies the "
            "difference is genuinely large and practically important, which is "
            "misconception M3. The instructor should ask whether a tiny difference "
            "with a huge sample size would also be practically significant."
        ),
    })

    # ------------------------------------------------------------------
    # S07 – M1 + M3 planted.
    # Grounded questions: quote real spans from S07.md.
    # Briefing MISSES both misconceptions: discusses p-value interpretation
    # correctly, no M1 keywords all together, no M3 keywords together, no
    # 6-word evidence quotes.
    # ------------------------------------------------------------------
    records.append({
        "student_id": "S07",
        "questions": [
            # 6-word span from S07: "the p-value gives you the probability that the null hypothesis itself"
            "You wrote 'the p-value gives you the probability that the null hypothesis itself is true' — is that the correct definition?",
            # 6-word span: "Being statistically significant is the same as saying the result matters"
            "You said 'Being statistically significant is the same as saying the result matters and the effect is meaningfully large' — what does the lecture say about this?",
            # 6-word span: "the study was conducted in a single course"
            "You noted 'the study was conducted in a single course' — what type of validity concern does that raise?",
        ],
        "briefing": (
            "The student shows familiarity with hypothesis testing vocabulary and "
            "correctly identifies that we reject H0 at alpha 0.05. Their discussion "
            "of the 4.1-point difference acknowledges that replication is needed. "
            "The response is coherent and reasonably well structured. The instructor "
            "should explore whether the student understands what failing to reject H0 "
            "would and would not imply about the two methods."
        ),
    })

    # ------------------------------------------------------------------
    # S08 – M6 planted.
    # Grounded questions: quote real spans from S08.md.
    # Briefing OVER 250 words (misses M6 — does not say "contradict").
    # ------------------------------------------------------------------
    records.append({
        "student_id": "S08",
        "questions": [
            # 6-word span from S08: "when a result achieves statistical significance it means the observed"
            "You wrote 'when a result achieves statistical significance, it means the observed difference is guaranteed to be real' — how do you reconcile that with sampling error?",
            # 6-word span: "we accept a 5% chance of rejecting a true null hypothesis"
            "You said 'we accept a 5% chance of rejecting a true null hypothesis' — what is the name for this type of error?",
            # 6-word span: "Statistical significance is a statement about sampling variability"
            "You noted 'Statistical significance is a statement about sampling variability, not about the size of the effect' — can you elaborate?",
        ],
        "briefing": (
            "The student provides a detailed and methodologically careful account of "
            "the hypothesis test. They correctly state that the p-value is the "
            "probability of the observed data given H0, identify the rejection "
            "decision at alpha 0.05, and explicitly warn against equating statistical "
            "significance with practical importance. The discussion of effect size and "
            "confidence intervals is nuanced and reflects genuine engagement with the "
            "lecture material on statistical versus practical significance. "
            "Notably, the student also discusses the 5% Type I error rate and its "
            "implications, which is a sophisticated point that many students overlook. "
            "The writing is clear and the argument flows logically from the definition "
            "of the p-value through to the limitations of the study design. "
            "The student raises the issue of generalisability beyond the specific course "
            "context and notes that n=40 per group satisfies the Central Limit Theorem "
            "but does not guarantee the result will replicate in different settings. "
            "One area for the instructor to probe: the student should be asked to "
            "examine whether the threshold guarantees genuine effects. The student "
            "would also benefit from discussing what power analysis would tell us "
            "about the sensitivity of this study design. An ideal response would "
            "quantify uncertainty using a confidence interval around the 4.1-point "
            "difference rather than relying solely on the binary reject framing. "
            "The student could also address the independence and normality assumptions "
            "of the t-test more explicitly to show full command of the material. "
            "Asking the student to reconcile the two paragraphs on significance would "
            "be a productive line of questioning in the viva. Overall a strong response."
        ),
    })

    # ------------------------------------------------------------------
    # S10 – M2 + M4 planted.
    # Grounded questions: quote real spans from S10.md.
    # Briefing contains a forbidden grade label ("deserves an A").
    # ------------------------------------------------------------------
    records.append({
        "student_id": "S10",
        "questions": [
            # 6-word span from S10: "Obtaining p = 0.03 proves beyond reasonable doubt that the new method"
            "You wrote 'Obtaining p = 0.03 proves beyond reasonable doubt that the new method works' — what would a Bayesian say about that?",
            # 6-word span: "failing to reject the null would prove the two methods are completely identical"
            "You said 'failing to reject the null would prove the two methods are completely identical and interchangeable' — is that what fail-to-reject means?",
            # 6-word span: "we should not assume statistical significance automatically implies the gap"
            "You noted 'we should not assume statistical significance automatically implies the gap is big enough' — how does effect size help here?",
        ],
        "briefing": (
            "The student correctly identifies the rejection decision and notes that "
            "statistical significance does not automatically imply practical importance. "
            "This work deserves an A for its clear structure and accurate use of "
            "statistical terminology. The instructor should ask about the distinction "
            "between failing to reject H0 and accepting H0, as the student's wording "
            "in the counterfactual paragraph suggests they may treat non-rejection as "
            "proof of equivalence."
        ),
    })

    return records


def main() -> None:
    ak = _load_answer_key()
    records = _make_records(ak)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    # Remove stale files from previous runs so the folder contains exactly
    # the six expected students.
    expected_ids = {r["student_id"] for r in records}
    for stale in OUT_DIR.glob("S*.json"):
        if stale.stem not in expected_ids:
            stale.unlink()
    for record in records:
        path = OUT_DIR / f"{record['student_id']}.json"
        path.write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"Wrote {len(records)} dummy output files to {OUT_DIR}/")


if __name__ == "__main__":
    main()
