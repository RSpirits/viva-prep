"""Watsonx Orchestrate tool for guardrailing agent output before delivery."""

from __future__ import annotations

import re

try:
    from ibm_watsonx_orchestrate.agent_builder.tools import tool
except ImportError:
    def tool(fn):  # type: ignore[misc]
        """No-op fallback when the ADK is not installed."""
        return fn


# ---------------------------------------------------------------------------
# Rule patterns
# ---------------------------------------------------------------------------

# Rule 1 – grade / score / mark / criterion verdict
#
# Matches explicit grade labels ("grade: B+", "mark: A-"), numeric score
# fractions ("7/10", "18/20"), percentage scores that refer to the student's
# mark or performance, pass/fail verdicts on the student or their work, and
# statements that a rubric criterion is met.
#
# Deliberately does NOT match:
#   "p-value of 0.03"               – no % sign
#   "3% chance"                     – probability language, not a mark
#   "5% significance level"         – statistical threshold
#   "97% confident"                 – statistical confidence
#   "5% false positive rate"        – methodological rate
#   "a score on the exam"           – "score" alone without a following value
#   "the A group and B group"       – letter not preceded by a grade keyword
#   "Assignment 4"                  – digit not in a fraction context
#   "failed to mention"             – "failed to <verb>" is not a verdict
#   "passed over"                   – idiomatic phrase, not a verdict
#   "this relates to criterion 3"   – referential, not a verdict
#   "Criterion 4 asks for …"        – descriptive, not a verdict
#   "under criterion 1 the student" – framing, not a verdict

# Explicit "grade: X" / "mark: X" / "deserves an A" patterns.
# The word-boundary \b after the grade letter ensures "grade consistently"
# (where 'c' continues a word) is not caught; only isolated letter tokens match.
_GRADE_LABEL = re.compile(
    r"\b(?:grade|mark|graded)\s*[:\s]\s*[A-Fa-f][+-]?\b"  # grade: B+  or  mark A-
    r"|\bdeserves\s+an?\s+[A-Fa-f][+-]?\b"                 # deserves an A
    r"|\bearned\s+an?\s+[A-Fa-f][+-]?\b",                   # earned a B
    re.IGNORECASE,
)

# Numeric fraction scores: digits/digits  e.g. "7/10", "18/20"
# Allow trailing non-digit so "S01" is not caught; require both sides numeric.
_SCORE_FRACTION = re.compile(
    r"\b\d{1,3}/\d{1,3}\b",
    re.IGNORECASE,
)

# Percentage scores tied to the student's mark or performance.
# A percentage is only blocked when a grading-context verb or noun immediately
# precedes or follows it — e.g. "scored 85%", "85% on this assignment",
# "received 72%", "achieved 90%", "scored a 70%".
# Plain statistical/probabilistic percentages ("3% chance", "5% significance",
# "97% confident", "false positive rate") are not blocked.
# "score of <n>" (without %) is also blocked as an explicit mark phrase.
_SCORE_PERCENT = re.compile(
    # verb + optional article + number + optional %:  "scored 85%", "scored a 70%"
    r"\b(?:scor(?:ed?|es|ing)|receiv(?:ed?|es|ing)|achiev(?:ed?|es|ing)|got|obtain(?:ed?|s|ing))"
    r"\s+(?:a\s+)?\d{1,3}\s*%?"
    # number + % + grading preposition:  "85% on this assignment", "72% in the class"
    r"|\b\d{1,3}\s*%\s+(?:on|in|for)\s+(?:this|the)\s+\w+"
    # number + % as a completion/quality predicate on the student's work:
    #   "85% complete", "72% correct", "90% accurate", "100% relevant"
    r"|\b\d{1,3}\s*%\s+(?:complete|correct|accurate|relevant|done|finished|adequate|sufficient)"
    # explicit mark phrase without %:  "a score of 72", "score of 85"
    r"|\bscore\s+of\s+\d",
    re.IGNORECASE,
)

# Pass / fail verdicts on the student or their submitted work.
# Blocked:  "the student passes", "student failed", "submission passes",
#           "would pass this assignment", "passed the student".
# Allowed:  "failed to mention", "failed to address", "passed over" —
#           these use fail/pass as an auxiliary before "to <verb>" or a
#           preposition ("over", "by"), not as a verdict on a person.
#           Excluded via negative lookahead: (?!\s+(?:to\b|over\b|by\b|up\b)).
_PASS_FAIL = re.compile(
    # pass/fail + direct object that is a person or work artefact
    r"\b(?:pass(?:ed)?|fail(?:ed)?)\s+(?:the\s+)?(?:student|submission|assignment|this)\b"
    # student/submission as subject + passes/fails,
    # but NOT when followed by "to <verb>", "over", "by", "up" (idiomatic uses)
    r"|\b(?:student|submission)\s+(?:passes|fails|passed|failed)(?!\s+(?:to\b|over\b|by\b|up\b))\b"
    # "would pass/fail" targeting the student
    r"|\bwould\s+(?:pass|fail)\s+(?:this|the)\b",
    re.IGNORECASE,
)

# Rule 1b – criterion verdict
#
# Blocks statements that a rubric criterion is met/satisfied/fulfilled.
# Allowed: "this relates to criterion 3", "Criterion 4 asks for …",
#          "under criterion 1 the student defines the p-value"
_CRITERION_MET = re.compile(
    # "meets/meeting/met criterion N"
    r"\b(?:meets?|meeting|met)\s+criterion\s+\d"
    # "satisfying/satisfies/satisfy the ... criterion" or "satisfying criterion N"
    r"|\bsatisfy?i(?:ng|es?)\s+(?:the\s+\w+\s+)?criterion\b"
    # "fulfils/fulfills/fulfilling criterion N"
    r"|\bfulfil(?:ls?|s|led|ling)\s+criterion\s+\d"
    # "criterion N is met"
    r"|\bcriterion\s+\d\s+is\s+met\b",
    re.IGNORECASE,
)

# Rule 2 – authorship / AI-use judgment
#
# Flags any claim that the work was AI-generated, plagiarised, or not the
# student's own — while leaving normal teaching language untouched.
#
# Also blocks vouching for authorship via "own words" language:
#   Blocked: "in their own words", "in the student's own words",
#            "uses own words", "using own words", "this is their own work"
#   Allowed: "explain in your own words", "restate … in their own words"
#            "ask the student to … in their own words"  (teaching requests)
#
# Because Python's re module does not support variable-width lookbehinds,
# the own-words check uses a two-step approach: (a) a broad pattern detects
# any "own words" phrase, then (b) a separate allowlist pattern checks whether
# the match sits inside a teaching request — if so, it is exempt.
_AUTHORSHIP_CORE = re.compile(
    r"\bwritten\s+by\s+(?:an?\s+)?ai\b"
    r"|\bused?\s+(?:chat\s*gpt|gpt[-\s]?\d|llm|an?\s+ai\b)"
    r"|\bnot\s+(?:their|his|her|the\s+student['']?s?)\s+own\s+work\b"
    r"|\bplagiar\w*"
    r"|\blikely\s+(?:ai[-\s]?)?generated\b"
    r"|\bai[-\s]generated\b"
    r"|\bthis\s+is\s+their\s+own\s+work\b",
    re.IGNORECASE,
)

# Broad "own words" detector — matches any sentence containing the phrase.
# Handles:
#   "in their/his/her/your/the student's own words"
#   "using/uses own words" or "using their own words" (1–2 word prefix before "own")
_OWN_WORDS_ANY = re.compile(
    r"\bin\s+(?:their|his|her|your|the\s+student[''\u2019]?s?)\s+own\s+words\b"
    r"|\b(?:uses?|using)\s+(?:\w+\s+)?own\s+words\b",
    re.IGNORECASE,
)

# Teaching-request forms that make "own words" legitimate.
# Matches sentences/clauses that explicitly instruct someone to use their own words
# (imperative verb, "ask … to", or "can you") — these must stay allowed.
_OWN_WORDS_TEACHING = re.compile(
    r"\b(?:explain|restate|describe|summarise|summarize|put|phrase|express|state|say)\b"
    r".*?\bin\s+(?:their|his|her|your|the\s+student[''\u2019]?s?)\s+own\s+words\b"
    r"|\bask\b.*?\bin\s+(?:their|his|her|your|the\s+student[''\u2019]?s?)\s+own\s+words\b"
    r"|\bcan\s+you\b.*?\bin\s+(?:their|his|her|your|the\s+student[''\u2019]?s?)\s+own\s+words\b",
    re.IGNORECASE | re.DOTALL,
)


def _authorship_violation(text: str) -> bool:
    """Return True if the text contains an authorship or AI-use violation."""
    if _AUTHORSHIP_CORE.search(text):
        return True
    # "own words" check: block unless every occurrence is within a teaching request.
    if _OWN_WORDS_ANY.search(text):
        # If the full text matches a teaching-request form that accounts for
        # the "own words" phrase, it is allowed; otherwise block.
        if not _OWN_WORDS_TEACHING.search(text):
            return True
    return False


# Keep a single name for the module-level pattern (used in the tool function).
_AUTHORSHIP = _AUTHORSHIP_CORE  # kept for backwards-compat; full check via _authorship_violation

# Rule 3 – instructor-only material (student audience only)
#
# Blocks the literal word "briefing", the phrase "suggested questions for the
# instructor", "confidence:" labels, and misconception codes M1–M6.
_INSTRUCTOR_ONLY = re.compile(
    r"\bbriefing\b"
    r"|\bsuggested\s+questions\s+for\s+the\s+instructor\b"
    r"|\bconfidence\s*:"
    r"|\bM[1-6]\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Tool
# ---------------------------------------------------------------------------

@tool
def check_output(text: str, audience: str) -> dict:
    """Check agent-generated text for policy violations before delivery.

    Applies rule-based guardrails to prevent grades, authorship judgements, and
    instructor-only content from reaching the wrong audience.

    Args:
        text: The text to evaluate.
        audience: Either ``"instructor"`` or ``"student"``.  When ``"student"``,
            an additional check for instructor-only material is applied.

    Returns:
        A dict with:
        - ``allowed`` (bool): ``True`` when no rules fired.
        - ``reasons`` (list[str]): Human-readable descriptions of each rule that
          fired; empty when ``allowed`` is ``True``.
        - ``text`` (str): The original text, unchanged.  The caller is
          responsible for rewriting if ``allowed`` is ``False``.
    """
    reasons: list[str] = []

    if _GRADE_LABEL.search(text):
        reasons.append("Contains an explicit grade or mark label.")

    if _SCORE_FRACTION.search(text):
        reasons.append("Contains a numeric score fraction (e.g. 7/10).")

    if _SCORE_PERCENT.search(text):
        reasons.append("Contains a percentage score or 'score of <n>' referring to student performance.")

    if _PASS_FAIL.search(text):
        reasons.append("Contains a pass/fail verdict on the student.")

    if _CRITERION_MET.search(text):
        reasons.append("Contains a statement that a rubric criterion is met.")

    if _authorship_violation(text):
        reasons.append("Contains a judgment about authorship or AI use.")

    if audience == "student" and _INSTRUCTOR_ONLY.search(text):
        reasons.append("Contains instructor-only material not suitable for students.")

    return {
        "allowed": len(reasons) == 0,
        "reasons": reasons,
        "text": text,
    }
