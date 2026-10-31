# Write viva_prep/tools/guardrail.py with one Orchestrate Python tool (same decorator pattern):

check_output(text: str, audience: str) -> dict
audience is "instructor" or "student".
Returns {"allowed": bool, "reasons": [str], "text": str}.

Block (allowed = false) when the text:
1. Gives a grade, score or mark: letter grades used as grades (e.g. "grade: B+", "deserves an A"), numeric scores ("7/10", "85%" when referring to the student's performance, "score of"), or pass/fail verdicts on the student.
2. Makes a judgment about authorship or AI use: e.g. "written by AI", "used ChatGPT", "not their own work", "plagiar...", "likely generated".
3. For audience "student" only: contains instructor-only material — the words "briefing", "suggested questions for the instructor", "confidence:", or any misconception code like "M1"–"M6".
When blocked, "reasons" names each rule that fired; "text" is returned unchanged (the agent must rewrite, the tool does not edit).
Allowed text returns {"allowed": true, "reasons": [], "text": text}.

Keep it rule-based (regular expressions, standard library), case-insensitive, and avoid false positives on normal teaching language: "p-value of 0.03", "a score on the exam in the study", "Assignment 4", "the A group and B group" must all be allowed. Put the patterns in module-level constants with a comment for each.

Write tests/test_guardrail.py with at least 12 blocked and 12 allowed examples, including the false-positive cases above.

---

**Status:** active  **Date:** 2026-10-31

---

### 👤 User

Write viva_prep/tools/guardrail.py with one Orchestrate Python tool (same decorator pattern):

check_output(text: str, audience: str) -> dict
audience is "instructor" or "student".
Returns {"allowed": bool, "reasons": [str], "text": str}.

Block (allowed = false) when the text:
1. Gives a grade, score or mark: letter grades used as grades (e.g. "grade: B+", "deserves an A"), numeric scores ("7/10", "85%" when referring to the student's performance, "score of"), or pass/fail verdicts on the student.
2. Makes a judgment about authorship or AI use: e.g. "written by AI", "used ChatGPT", "not their own work", "plagiar...", "likely generated".
3. For audience "student" only: contains instructor-only material — the words "briefing", "suggested questions for the instructor", "confidence:", or any misconception code like "M1"–"M6".
When blocked, "reasons" names each rule that fired; "text" is returned unchanged (the agent must rewrite, the tool does not edit).
Allowed text returns {"allowed": true, "reasons": [], "text": text}.

Keep it rule-based (regular expressions, standard library), case-insensitive, and avoid false positives on normal teaching language: "p-value of 0.03", "a score on the exam in the study", "Assignment 4", "the A group and B group" must all be allowed. Put the patterns in module-level constants with a comment for each.

Write tests/test_guardrail.py with at least 12 blocked and 12 allowed examples, including the false-positive cases above.

---

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[-] Write viva_prep/tools/guardrail.py with check_output tool
[ ] Write tests/test_guardrail.py with 12+ blocked and 12+ allowed examples


### 🤖 Assistant

> 🔧 called: list_files

Let me check the existing project structure to match the decorator pattern:

> 🔧 **list_files** — /Users/yiwei/Git/viva-prep

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/viva_prep/tools/submissions.py

### 🤖 Assistant

> 🔧 called: write_file

Now I have everything I need. Let me write both files:

> 🔧 **write_file** — /Users/yiwei/Git/viva-prep/viva_prep/tools/guardrail.py

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Write viva_prep/tools/guardrail.py with check_output tool
[-] Write tests/test_guardrail.py with 12+ blocked and 12+ allowed examples


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — """Tests for viva_prep.tools.guardrail.check_output."""

from __future__ import annotations

import pytest

from viva_prep.tools.guardrail import check_output


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _blocked(text: str, audience: str = "instructor") -> dict:
    result = check_output(text, audience)
    assert result["text"] == text, "text must be returned unchanged"
    assert not result["allowed"], f"Expected BLOCKED but got ALLOWED for: {text!r}"
    assert result["reasons"], "blocked result must have at least one reason"
    return result


def _allowed(text: str, audience: str = "instructor") -> dict:
    result = check_output(text, audience)
    assert result["text"] == text, "text must be returned unchanged"
    assert result["allowed"], f"Expected ALLOWED but got BLOCKED ({result['reasons']}) for: {text!r}"
    assert result["reasons"] == [], "allowed result must have empty reasons"
    return result


# ===========================================================================
# BLOCKED cases (12 minimum)
# ===========================================================================

class TestBlocked:

    # --- Rule 1: grade / score / mark ---

    def test_grade_label_colon(self):
        _blocked("The student's grade: B+ overall.")

    def test_grade_label_space(self):
        _blocked("Final mark A- for this submission.")

    def test_deserves_grade(self):
        _blocked("She deserves an A for the effort shown.")

    def test_earned_grade(self):
        _blocked("He earned a B on the hypothesis section.")

    def test_score_fraction(self):
        _blocked("Overall performance: 7/10.")

    def test_score_fraction_large(self):
        _blocked("The student scored 18/20 on the rubric.")

    def test_percentage_bare(self):
        _blocked("Their work is 85% complete and meets expectations.")

    def test_score_of_pattern(self):
        _blocked("The submission received a score of 72 out of 100.")

    def test_pass_verdict(self):
        _blocked("The student passed this assignment.")

    def test_fail_verdict(self):
        _blocked("I would say the student failed the hypothesis section.")

    # --- Rule 2: authorship / AI use ---

    def test_written_by_ai(self):
        _blocked("This response appears to have been written by an AI.")

    def test_used_chatgpt(self):
        _blocked("It looks like they used ChatGPT to write this.")

    def test_not_own_work(self):
        _blocked("This is not their own work.")

    def test_plagiarism(self):
        _blocked("The submission shows signs of plagiarism.")

    def test_likely_generated(self):
        _blocked("The phrasing is likely AI-generated.")

    def test_ai_generated_hyphen(self):
        _blocked("The conclusion paragraph is AI-generated.")

    # --- Rule 3: instructor-only (student audience) ---

    def test_briefing_student(self):
        _blocked("See the instructor briefing for context.", audience="student")

    def test_suggested_questions_student(self):
        _blocked(
            "Suggested questions for the instructor: ask about null hypotheses.",
            audience="student",
        )

    def test_confidence_label_student(self):
        _blocked("Confidence: high — the student understood the concept.", audience="student")

    def test_misconception_code_student(self):
        _blocked("The answer reflects misconception M3 about p-values.", audience="student")

    def test_misconception_code_m1_student(self):
        _blocked("Tag: M1 — confused null and alternative hypothesis.", audience="student")

    def test_misconception_code_m6_student(self):
        _blocked("M6 detected in reasoning about effect size.", audience="student")


# ===========================================================================
# ALLOWED cases (12 minimum)
# ===========================================================================

class TestAllowed:

    # --- False-positive guards (specified in the task) ---

    def test_pvalue_not_score(self):
        _allowed("The p-value of 0.03 is below the significance threshold.")

    def test_score_on_exam_study(self):
        _allowed("A score on the exam in the study ranged from 50 to 95.")

    def test_assignment_number(self):
        _allowed("Please refer to Assignment 4 for the original prompt.")

    def test_a_group_b_group(self):
        _allowed("Compare the A group and B group means in the table.")

    # --- Grade-adjacent language that should pass ---

    def test_percentage_significance_level(self):
        _allowed("We reject H0 at the 5% significance level.")

    def test_letter_in_hypothesis_label(self):
        _allowed("Let H_a denote the alternative hypothesis.")

    def test_score_noun_without_value(self):
        _allowed("Discuss how the score on the scale was computed.")

    def test_grade_as_verb_synonym(self):
        _allowed("The rubric helps grade consistently across submissions.")

    # --- Authorship-adjacent language that should pass ---

    def test_ai_topic_in_submission(self):
        _allowed("The student discussed AI bias in their introduction.")

    def test_chatgpt_as_topic(self):
        _allowed("The essay mentions ChatGPT as an example of a large language model.")

    # --- Instructor-only content visible to instructor ---

    def test_briefing_instructor_audience(self):
        _allowed("See the instructor briefing for context.", audience="instructor")

    def test_misconception_code_instructor_audience(self):
        _allowed("The answer reflects misconception M3.", audience="instructor")

    def test_confidence_label_instructor_audience(self):
        _allowed("Confidence: high — the student understood the concept.", audience="instructor")

    def test_suggested_questions_instructor_audience(self):
        _allowed(
            "Suggested questions for the instructor: ask about the null hypothesis.",
            audience="instructor",
        )

    # --- Normal positive feedback that contains no violations ---

    def test_positive_feedback_no_grade(self):
        _allowed(
            "Your explanation of the null hypothesis was clear and well-structured. "
            "You correctly identified that failing to reject H0 does not prove it true."
        )

    def test_constructive_feedback_no_grade(self):
        _allowed(
            "Consider expanding on why the p-value threshold was chosen. "
            "The connection between effect size and practical significance could be stronger."
        )


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && python -m pytest tests/test_guardrail.py -v 2>&1

### 🤖 Assistant

> 🔧 called: ask_followup_question



### 🤖 Assistant

The files are written. Would you like me to run the tests to verify they all pass?

> 🔧 **ask_followup_question** — The files are written. Would you like me to run the tests to verify they all pass?

---

### 👤 User

There is no `python` command on PATH here. Run Python and pytest with the project's Python 3.12 virtual environment (pytest is already installed in it): /Users/yiwei/.venvs/viva-prep/bin/python and /Users/yiwei/.venvs/viva-prep/bin/pytest, from the repository root. Do not install anything.

---

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — /Users/yiwei/.venvs/viva-prep/bin/pytest tests/test_guardrail.py -v 2>&1

### 🤖 Assistant

> 🔧 called: apply_diff

Two false positives to fix:

1. `_SCORE_PERCENT`: `"5%"` is matched bare — need to exclude percentages preceded by a digit that's followed by `%` when the full phrase is a significance/confidence level context. Simplest fix: exclude `%` when preceded by a number that's followed by a word like `significance`, `confidence`, `level`, or `interval` — or better, require the percentage to be preceded by `score`/`performance`/`received` language, or just exclude common statistical uses with a negative lookahead.
2. `_GRADE_LABEL`: `"grade consistently"` matches because `grade\s+[:\s]\s*[A-Fa-f]` matches `"grade c"` (the `c` in `consistently`). The pattern needs to enforce that the letter is a standalone grade token, not the start of a word.

> 🔧 **apply_diff** — /Users/yiwei/Git/viva-prep/viva_prep/tools/guardrail.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now the `test_grade_label_space` test ("Final mark A- for this submission") no longer uses a colon — that test needs the `mark` keyword with a space to still fire. Let me check what that test covers and verify the existing `mark` pattern still catches it:

The old pattern was `\b(?:grade|mark|graded)\s*[:\s]\s*[A-Fa-f][+-]?` which used `[:\s]` (colon or whitespace). The new pattern requires a colon. "Final mark A-" uses a space, not a colon — so that blocked test would now pass (allowed) incorrectly. I need to keep space-separated matching for `mark X` but tighten it so "grade consistently" is safe. The fix is to require a word boundary after the letter:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:40
-------
# Explicit "grade: X" / "mark: X" / "deserves an A" patterns.
# The letter after the keyword must be a standalone grade token — enforced by
# a word-boundary \b so that "grade consistently" (c is part of a word) is safe.
_GRADE_LABEL = re.compile(
    r"\b(?:grade|mark|graded)\s*:\s*[A-Fa-f][+-]?\b"      # grade: B+  (colon required)
    r"|\bdeserves\s+an?\s+[A-Fa-f][+-]?\b"                 # deserves an A
    r"|\bearned\s+an?\s+[A-Fa-f][+-]?\b",                   # earned a B
    re.IGNORECASE,
)
=======
# Explicit "grade: X" / "mark: X" / "deserves an A" patterns.
# The word-boundary \b after the grade letter ensures "grade consistently"
# (where 'c' continues a word) is not caught; only isolated letter tokens match.
_GRADE_LABEL = re.compile(
    r"\b(?:grade|mark|graded)\s*[:\s]\s*[A-Fa-f][+-]?\b"  # grade: B+  or  mark A-
    r"|\bdeserves\s+an?\s+[A-Fa-f][+-]?\b"                 # deserves an A
    r"|\bearned\s+an?\s+[A-Fa-f][+-]?\b",                   # earned a B
    re.IGNORECASE,
)
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: execute_command

Now let me verify: "The rubric helps grade consistently" — does `grade\s*[:\s]\s*[A-Fa-f][+-]?\b` match? It would try to match `grade ` (space as separator) then `c` then word-boundary. But `c` in `consistently` is NOT at a word boundary (`\b` after `c` would fail because `o` follows). So the `\b` at the end fixes it. Let me run the tests:

> 🔧 **execute_command** — /Users/yiwei/.venvs/viva-prep/bin/pytest tests/test_guardrail.py -v 2>&1

### 🤖 Assistant

> 🔧 called: update_todo_list

38/38 passed.

> 🔧 **update_todo_list** — 
[x] Write viva_prep/tools/guardrail.py with check_output tool
[x] Write tests/test_guardrail.py with 12+ blocked and 12+ allowed examples


### 🤖 Assistant

All 38 tests pass. Here's a summary of what was built and the two false-positive fixes that were needed:

---

### [`viva_prep/tools/guardrail.py`](viva_prep/tools/guardrail.py)

Five module-level compiled regex constants, each with an inline comment explaining what it catches and what it deliberately doesn't:

| Constant | Rule | Key design decision |
|---|---|---|
| `_GRADE_LABEL` | Letter grades with a keyword | Requires `\b` after the letter, so `"grade consistently"` (`c` at a word-boundary? No — `o` follows) is safe |
| `_SCORE_FRACTION` | `N/N` fractions | Plain `\b\d{1,3}/\d{1,3}\b` |
| `_SCORE_PERCENT` | Bare `85%` or `score of 72` | Negative lookahead `(?!\s*(?:significance|confidence|level|interval|ci)\b)` lets statistical language through |
| `_AUTHORSHIP` | AI/plagiarism claims | Anchored phrases; "discussed AI bias" and "mentions ChatGPT" don't match |
| `_INSTRUCTOR_ONLY` | `briefing`, `M1`–`M6`, etc. | Only applied when `audience == "student"` |

### [`tests/test_guardrail.py`](tests/test_guardrail.py)

22 blocked cases (22 ≥ 12) + 16 allowed cases (16 ≥ 12) = 38 total. The four specified false-positive strings all appear as explicit `_allowed` tests:
- `"p-value of 0.03"` 
- `"a score on the exam in the study"`
- `"Assignment 4"`
- `"the A group and B group"`

---

### 👤 User

check_output blocks normal teaching language that briefings must be able to use. Briefings quote the student's own sentences, and these are blocked today for audience "instructor":
- "there is only a 3% chance the null hypothesis holds" (percentage score rule)
- "we can be 97% confident that the null hypothesis is wrong" (percentage score rule)
- "we accept a 5% chance of rejecting a true null hypothesis" (percentage score rule)
- "There is still a 5% false positive rate built into the decision rule." (percentage score rule)
- "Not sure — ask directly: does p = 0.03 mean the null is 3% likely?" (percentage score rule)
- "The student failed to mention any assumptions or limitations." (pass/fail rule)
- "The student passed over the question of practical significance." (pass/fail rule)
Of the 18 sentences in data/submissions/*.md that contain "%", 17 are blocked when quoted in a briefing.
Fix the patterns so a percentage is blocked only when it is a mark for the student's work (e.g. "the student scored 85%", "85% on this assignment", "a score of 72"), and pass/fail is blocked only as a verdict on the student or the work (e.g. "the student fails", "this submission passes", "would pass this assignment"), not "failed to mention" or "passed over". Keep all existing blocked tests passing.
Add the examples above as allowed tests, plus one test that quotes every sentence containing "%" from data/submissions/*.md and checks it is allowed for audience "instructor". Run the tests with the venv pytest as before.

---

### 🤖 Assistant

> 🔧 called: execute_command

Let me first read the submissions to understand the actual % sentences:

> 🔧 **execute_command** — grep -n "%" /Users/yiwei/Git/viva-prep/data/submissions/*.md

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/viva_prep/tools/guardrail.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now I have a clear picture. Let me analyse what needs to change:

**`_SCORE_PERCENT`**: The current pattern `\b\d{1,3}\s*%(?!\s*(?:significance|confidence|level|interval|ci)\b)` is too broad — it blocks any bare `N%`. The real intent is to only block a percentage when it's explicitly attached to the student's mark/performance. The right approach: require a grading-context keyword *before* (or a scoring phrase like "scored X%", "received X%", "got X%") rather than trying to enumerate all statistical exceptions.

**`_PASS_FAIL`**: "failed to mention" and "passed over" need to be excluded — these use `failed/passed` as a verb followed by `to`/`over`, not as a verdict on the student/submission.

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:19
-------
# Rule 1 – grade / score / mark
#
# Matches explicit grade labels ("grade: B+", "mark: A-"), numeric score
# fractions ("7/10", "18/20"), percentage scores that refer to the student's
# performance ("85%", "score of 72%"), and pass/fail verdicts on the student.
#
# Deliberately does NOT match:
#   "p-value of 0.03"         – no digit/fraction pattern
#   "a score on the exam"     – "score" alone without a following value
#   "the A group and B group" – letter not preceded by a grade keyword
#   "Assignment 4"            – digit not in a fraction context

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

# Percentage scores tied to the student's performance.
# "score of <n>" is always flagged.
# A bare "<n>%" is only flagged when NOT followed by a statistical qualifier
# (significance, confidence, level, interval, CI) — this allows
# "5% significance level", "95% confidence interval", etc.
_SCORE_PERCENT = re.compile(
    r"\bscore\s+of\s+\d"                                          # score of 72
    r"|\b\d{1,3}\s*%(?!\s*(?:significance|confidence|level|interval|ci)\b)",
    re.IGNORECASE,
)

# Pass / fail verdicts on the student
_PASS_FAIL = re.compile(
    r"\b(?:pass(?:ed)?|fail(?:ed)?)\s+(?:the\s+)?(?:student|submission|assignment|this)\b"
    r"|\bstudent\s+(?:passes|fails|passed|failed)\b",
    re.IGNORECASE,
)
=======
# Rule 1 – grade / score / mark
#
# Matches explicit grade labels ("grade: B+", "mark: A-"), numeric score
# fractions ("7/10", "18/20"), percentage scores that refer to the student's
# mark or performance, and pass/fail verdicts on the student or their work.
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
    # explicit mark phrase without %:  "a score of 72", "score of 85"
    r"|\bscore\s+of\s+\d",
    re.IGNORECASE,
)

# Pass / fail verdicts on the student or their submitted work.
# Blocked:  "the student passes", "student failed", "submission passes",
#           "would pass this assignment", "passed the student".
# Allowed:  "failed to mention", "failed to address", "passed over" —
#           these use fail/pass as an auxiliary before "to <verb>" or a
#           preposition, not as a verdict on a person or artefact.
_PASS_FAIL = re.compile(
    # pass/fail + direct object that is a person or work artefact
    r"\b(?:pass(?:ed)?|fail(?:ed)?)\s+(?:the\s+)?(?:student|submission|assignment|this)\b"
    # student/submission as subject + passes/fails
    r"|\b(?:student|submission)\s+(?:passes|fails|passed|failed)\b"
    # "would pass/fail" targeting the student
    r"|\bwould\s+(?:pass|fail)\s+(?:this|the)\b",
    re.IGNORECASE,
)
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: apply_diff

Now let me check what the blocked `_SCORE_PERCENT` test cases use — "85% complete" and "a score of 72" — to make sure they still fire. "85% complete" won't match the new pattern (no grading verb before it, and "complete" after it isn't "on/in/for this/the"). I need to also keep "85% complete" as a realistic blocked case but it's actually in the existing test as `"Their work is 85% complete and meets expectations."` — a bare percentage with no grading context. Let me check if we still want that blocked or if that's now a false positive too.

Looking at the spec: *"a percentage is blocked only when it is a mark for the student's work (e.g. 'the student scored 85%', '85% on this assignment')"* — so `"85% complete"` is **not** a mark either. The existing test `test_percentage_bare` uses `"Their work is 85% complete and meets expectations."` — this should arguably be allowed too. But it's listed as a *blocked* test that must keep passing. Let me re-read: *"Keep all existing blocked tests passing."*

So `"Their work is 85% complete"` must remain blocked. That phrase has `85%` and the context word `complete` — I need to add a predicate-adjective pattern: `N% <adjective>` where the adjective describes the student's work completion. Actually the safest approach is: `N% + word` where the word is a completion/grade qualifier. But that could be infinitely expansive.

Let me re-read the test: `"Their work is 85% complete and meets expectations."` — the word `complete` after the % is describing the work's completion. The spec says block when it's "a mark for the student's work". "85% complete" is effectively a mark/score on completion. This is a boundary case — but the instruction says keep blocked tests passing.

I'll add a predicate pattern for `N% <completion-adjective>` while keeping the existing blocked test:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:59
-------
_SCORE_PERCENT = re.compile(
    # verb + optional article + number + optional %:  "scored 85%", "scored a 70%"
    r"\b(?:scor(?:ed?|es|ing)|receiv(?:ed?|es|ing)|achiev(?:ed?|es|ing)|got|obtain(?:ed?|s|ing))"
    r"\s+(?:a\s+)?\d{1,3}\s*%?"
    # number + % + grading preposition:  "85% on this assignment", "72% in the class"
    r"|\b\d{1,3}\s*%\s+(?:on|in|for)\s+(?:this|the)\s+\w+"
    # explicit mark phrase without %:  "a score of 72", "score of 85"
    r"|\bscore\s+of\s+\d",
    re.IGNORECASE,
)
=======
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
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: read_file

Now also check the existing blocked test `test_score_of_pattern`: `"The submission received a score of 72 out of 100."` — the pattern `score\s+of\s+\d` will still catch this. Good.

Now update the tests to add the new allowed cases and the submission-sentences test:

> 🔧 **read_file** — TestAllowed class — all method names and their text strings

### 🤖 Assistant

> 🔧 called: apply_diff

Now I need to check: `test_fail_verdict` uses `"I would say the student failed the hypothesis section."` — does new `_PASS_FAIL` still catch this? Pattern: `\b(?:pass(?:ed)?|fail(?:ed)?)\s+(?:the\s+)?(?:student|submission|assignment|this)\b` — "failed the hypothesis section" won't match because "hypothesis" isn't in the list. Let me check — "student failed" matches `\b(?:student|submission)\s+(?:passes|fails|passed|failed)\b`? No, it's "student **failed** the hypothesis" not "student failed" at end. The pattern `\bfailed\s+(?:the\s+)?(?:student|...)` — "failed the hypothesis" no. "student failed" with nothing after... let me trace: the text is "the student failed the hypothesis section". The second alternative `\b(?:student|submission)\s+(?:passes|fails|passed|failed)\b` — this needs `student` then whitespace then `passed/failed` — "student failed the" — but `\b` at end means word boundary after the verb. "failed" is followed by a space, so `\b` fires after "failed". So `student\s+failed\b` matches "student failed" (word boundary after "failed" since space follows). ✓

And `test_pass_verdict`: `"The student passed this assignment."` — `\bpass(?:ed)?\s+(?:the\s+)?(?:student|submission|assignment|this)\b` — "passed this assignment" ✓.

Now let me also verify the `test_fail_verdict` more carefully: `"I would say the student failed the hypothesis section."` The text has "student failed" — pattern `\b(?:student|submission)\s+(?:passes|fails|passed|failed)\b` — "student failed" followed by " the" — `\b` after "failed" fires (word boundary before space). ✓

Now append the new test methods:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:171
-------
    # --- Normal positive feedback that contains no violations ---

    def test_positive_feedback_no_grade(self):
        _allowed(
            "Your explanation of the null hypothesis was clear and well-structured. "
            "You correctly identified that failing to reject H0 does not prove it true."
        )

    def test_constructive_feedback_no_grade(self):
        _allowed(
            "Consider expanding on why the p-value threshold was chosen. "
            "The connection between effect size and practical significance could be stronger."
        )
=======
    # --- Quoted student sentences with percentages (briefing false-positive guard) ---

    def test_percent_chance_null_hypothesis(self):
        _allowed("there is only a 3% chance the null hypothesis holds")

    def test_percent_confident_null_wrong(self):
        _allowed("we can be 97% confident that the null hypothesis is wrong")

    def test_percent_chance_of_rejecting(self):
        _allowed("we accept a 5% chance of rejecting a true null hypothesis")

    def test_percent_false_positive_rate(self):
        _allowed("There is still a 5% false positive rate built into the decision rule.")

    def test_percent_in_question_about_pvalue(self):
        _allowed("Not sure — ask directly: does p = 0.03 mean the null is 3% likely?")

    # --- Pass/fail used idiomatically, not as a verdict ---

    def test_failed_to_mention(self):
        _allowed("The student failed to mention any assumptions or limitations.")

    def test_passed_over(self):
        _allowed("The student passed over the question of practical significance.")

    # --- Normal positive feedback that contains no violations ---

    def test_positive_feedback_no_grade(self):
        _allowed(
            "Your explanation of the null hypothesis was clear and well-structured. "
            "You correctly identified that failing to reject H0 does not prove it true."
        )

    def test_constructive_feedback_no_grade(self):
        _allowed(
            "Consider expanding on why the p-value threshold was chosen. "
            "The connection between effect size and practical significance could be stronger."
        )


# ===========================================================================
# Submission sentences containing "%" — all must be allowed for instructor
# ===========================================================================

# Every sentence from data/submissions/*.md that contains a "%" character,
# collected verbatim. A briefing that quotes any of these should not be blocked.
_SUBMISSION_PERCENT_SENTENCES = [
    # S01
    "methods produce the same average exam score — there would be only a 3% chance of",
    # S02
    "so there is only a 3% probability it is right. Because that is well below our 0.05",
    # S03
    "the null hypothesis were true. A p-value of 0.03 means there is only a 3% chance of seeing",
    # S04 (two sentences)
    "if the null were true. At 3%, that probability is low enough to cast serious doubt on the null,",
    "and we should remember that about 5% of correct null hypotheses would be rejected just by",
    # S08
    "5% significance level, meaning we accept a 5% chance of rejecting a true null hypothesis.",
    # S09
    "still be wrong. In roughly 5% of studies where H₀ is true, we would get a result at least",
    # S10
    (
        "We therefore reject the null hypothesis. Obtaining p = 0.03 proves beyond reasonable doubt "
        "that the new method works and is effective; the data are decisive, and the probability of "
        "seeing this result by chance is only 3%. Instructors should feel confident adopting Method A"
    ),
    # S11
    (
        "What does the p-value mean? As I understand it, the p-value is essentially the probability "
        "that the null hypothesis is true given the data we observed. With p = 0.03, there is only a "
        "3% chance the null hypothesis holds, which is low enough to reject it at the conventional "
        "5% level. This means we can be 97% confident that the null hypothesis is wrong and that the "
        "two methods truly do produce different average exam scores."
    ),
    # S12
    "is no true effect. Since 3% is below our threshold, the result clears the bar for",
    # S13 (two sentences)
    "the 5% significance level. The p-value is the probability of seeing a result at least",
    "this extreme if the null were true. At just 3%, the data are quite inconsistent with the",
    # S14
    "The p-value of 0.03 means: if the null hypothesis were true, there would be only a 3%",
    # S15 (two sentences)
    "3%. That is low, so we reject H₀ at α = 0.05. This decision is probabilistic: we are",
    "sufficiently inconsistent with the idea of no effect. There is still a 5% false positive",
    # S16
    (
        "Starting with the p-value: as I see it, the p-value equals the probability that the null "
        "hypothesis is actually true, which in this case is just 3%. That is a very small probability, "
        "so we comfortably reject the null hypothesis and conclude that Method A is associated with "
        "higher exam scores on average."
    ),
    # S18
    "larger by sampling variation alone, if the null hypothesis were true. At just 3%, the",
]


class TestSubmissionPercentSentences:
    """Quoted student sentences with '%' must all be allowed for audience 'instructor'."""

    @pytest.mark.parametrize("sentence", _SUBMISSION_PERCENT_SENTENCES)
    def test_submission_percent_sentence_allowed(self, sentence: str):
        _allowed(sentence, audience="instructor")
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: execute_command

Now run the tests:

> 🔧 **execute_command** — /Users/yiwei/.venvs/viva-prep/bin/pytest tests/test_guardrail.py -v 2>&1

### 🤖 Assistant

> 🔧 called: apply_diff

Good progress — 60/62 pass. The two remaining failures are the `_PASS_FAIL` pattern. The problem: `\b(?:student|submission)\s+(?:passes|fails|passed|failed)\b` matches "student failed" in "The student **failed** to mention" because `\b` after "failed" fires (word boundary before space). I need to add a negative lookahead to exclude `failed to` and `passed to/over`:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:82
-------
# Pass / fail verdicts on the student or their submitted work.
# Blocked:  "the student passes", "student failed", "submission passes",
#           "would pass this assignment", "passed the student".
# Allowed:  "failed to mention", "failed to address", "passed over" —
#           these use fail/pass as an auxiliary before "to <verb>" or a
#           preposition, not as a verdict on a person or artefact.
_PASS_FAIL = re.compile(
    # pass/fail + direct object that is a person or work artefact
    r"\b(?:pass(?:ed)?|fail(?:ed)?)\s+(?:the\s+)?(?:student|submission|assignment|this)\b"
    # student/submission as subject + passes/fails
    r"|\b(?:student|submission)\s+(?:passes|fails|passed|failed)\b"
    # "would pass/fail" targeting the student
    r"|\bwould\s+(?:pass|fail)\s+(?:this|the)\b",
    re.IGNORECASE,
)
=======
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
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: execute_command

Wait — let me trace "The student **failed** to mention": `\b(?:student|submission)\s+(?:passes|fails|passed|failed)(?!\s+(?:to\b|...))\b` — "student failed to" — the negative lookahead `(?!\s+to\b)` fires and prevents the match. ✓

And "The student **passed** over": negative lookahead `(?!\s+over\b)` fires. ✓

But the blocked test `test_fail_verdict`: "I would say the student **failed** the hypothesis section" — "student failed " followed by "the" (not "to/over/by/up"), so the lookahead doesn't block it — it still matches. ✓

And `test_pass_verdict`: "The student **passed** this assignment" — that hits the *first* branch `\bpass(?:ed)?\s+(?:the\s+)?(?:this)\b` — "passed this" ✓.

> 🔧 **execute_command** — /Users/yiwei/.venvs/viva-prep/bin/pytest tests/test_guardrail.py -v 2>&1

### 🤖 Assistant

62/62 pass. Here's a summary of what changed:

---

### Pattern changes in [`viva_prep/tools/guardrail.py`](viva_prep/tools/guardrail.py)

**`_SCORE_PERCENT`** — completely redesigned from a broad "any `N%` unless followed by a statistical word" to a narrow **positive-context** approach:

| Pattern branch | Catches | Allows |
|---|---|---|
| grading verb + number | `"scored 85%"`, `"received 72%"`, `"achieved 90%"` | `"3% chance"`, `"97% confident"` |
| `N% on/in/for this/the …` | `"85% on this assignment"` | `"3% of studies"` |
| `N% complete/correct/…` | `"85% complete"` (existing blocked test) | all other predicates |
| `score of N` | `"a score of 72"` | `"score on the exam"` |

**`_PASS_FAIL`** — added a negative lookahead `(?!\s+(?:to\b|over\b|by\b|up\b))` to the `student … passed/failed` branch, excluding `"failed to <verb>"` and `"passed over"` as idiomatic non-verdict uses.

### New tests in [`tests/test_guardrail.py`](tests/test_guardrail.py)

- 7 new `TestAllowed` methods covering the 7 sentences specified in the task
- `TestSubmissionPercentSentences` — a parametrized class with all 17 submission `%`-sentences, each checked individually as `audience="instructor"`