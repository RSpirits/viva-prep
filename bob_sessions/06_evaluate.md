# Write scripts/evaluate.py to measure the MVP success criteria. Input: a folder of agent outputs, one JSON file per student, named S##.json, with fields {"student_id", "questions": [str], "briefing": str}. (We will export these from Orchestrate test runs; for now also write scripts/make_dummy_outputs.py that creates a small fake output folder at results/dummy/ so the evaluator can be tested.)

For each student, compute:
1. grounded_questions: share of questions that quote or closely paraphrase a specific passage of that student's submission. Rule: a question counts as grounded if it contains a quoted span of 6 or more consecutive words found in the submission, or if 60%+ of its content words (lowercased, stopwords removed) appear in a single sentence of the submission.
2. misconception_found: for each planted misconception in data/answer_key/answer_key.json, whether the briefing refers to it. Rule: the briefing contains 6+ consecutive words from the evidence sentence, or contains a keyword set defined per misconception in a dict at the top of the script (e.g. M1: ["probability", "null", "true"] all present).
3. briefing_words: word count of the briefing.
4. forbidden: whether viva_prep.tools.guardrail.check_output(briefing, "instructor") blocks it.

Print a summary table and these totals against the targets:
- grounded questions >= 90%
- planted misconceptions detected >= 80%
- briefings <= 250 words: share meeting it
- forbidden outputs = 0
Mark each target PASS or FAIL. Save the per-student results to results/eval_<timestamp>.csv.
The answer key is only read here, never by the tools.

Write tests/test_evaluate.py using the dummy outputs: one fully grounded student, one ungrounded, one briefing that names its misconception, one that misses it, one over 250 words, one with a grade in it.

---

**Status:** active  **Date:** 2026-10-31

---

### 👤 User

Write scripts/evaluate.py to measure the MVP success criteria. Input: a folder of agent outputs, one JSON file per student, named S##.json, with fields {"student_id", "questions": [str], "briefing": str}. (We will export these from Orchestrate test runs; for now also write scripts/make_dummy_outputs.py that creates a small fake output folder at results/dummy/ so the evaluator can be tested.)

For each student, compute:
1. grounded_questions: share of questions that quote or closely paraphrase a specific passage of that student's submission. Rule: a question counts as grounded if it contains a quoted span of 6 or more consecutive words found in the submission, or if 60%+ of its content words (lowercased, stopwords removed) appear in a single sentence of the submission.
2. misconception_found: for each planted misconception in data/answer_key/answer_key.json, whether the briefing refers to it. Rule: the briefing contains 6+ consecutive words from the evidence sentence, or contains a keyword set defined per misconception in a dict at the top of the script (e.g. M1: ["probability", "null", "true"] all present).
3. briefing_words: word count of the briefing.
4. forbidden: whether viva_prep.tools.guardrail.check_output(briefing, "instructor") blocks it.

Print a summary table and these totals against the targets:
- grounded questions >= 90%
- planted misconceptions detected >= 80%
- briefings <= 250 words: share meeting it
- forbidden outputs = 0
Mark each target PASS or FAIL. Save the per-student results to results/eval_<timestamp>.csv.
The answer key is only read here, never by the tools.

Write tests/test_evaluate.py using the dummy outputs: one fully grounded student, one ungrounded, one briefing that names its misconception, one that misses it, one over 250 words, one with a grade in it.

---

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[-] Explore existing codebase structure to understand what's already there
[ ] Create data/answer_key/answer_key.json with planted misconceptions
[ ] Write scripts/make_dummy_outputs.py
[ ] Write scripts/evaluate.py
[ ] Write tests/test_evaluate.py
[ ] Run tests to validate


### 🤖 Assistant

> 🔧 called: list_files



> 🔧 **list_files** — /Users/yiwei/Git/viva-prep

### 🤖 Assistant

> 🔧 called: read_file, read_file, read_file



> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/pyproject.toml

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/data/answer_key/answer_key.json

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/viva_prep/tools/guardrail.py

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — submission content, key phrases that could be used for grounding tests

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have everything I need. Let me build all the files:

> 🔧 **update_todo_list** — 
[x] Explore existing codebase structure to understand what's already there
[-] Create data/answer_key/answer_key.json with planted misconceptions
[ ] Write scripts/make_dummy_outputs.py
[ ] Write scripts/evaluate.py
[ ] Write tests/test_evaluate.py
[ ] Run tests to validate


### 🤖 Assistant

> 🔧 called: write_file

The answer key already exists. Now I'll write all three new files simultaneously:

> 🔧 **write_file** — /Users/yiwei/Git/viva-prep/scripts/make_dummy_outputs.py

### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — /Users/yiwei/Git/viva-prep/scripts/evaluate.py

### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — """Tests for scripts/evaluate.py using the dummy output folder.

Run:  pytest tests/test_evaluate.py

Each test targets one of the six synthetic students generated by
scripts/make_dummy_outputs.py.  The tests call scripts/evaluate.py's
functions directly (no subprocess) so they are fast and give clear failure
messages.

Dummy-student scenarios
-----------------------
S01 – fully grounded questions, briefing mentions M1  →  grounded=1.0, misc detected
S02 – ungrounded questions,     briefing mentions M2  →  grounded=0.0, misc detected
S03 – grounded questions,       briefing MISSES M3    →  grounded=1.0, misc NOT detected
S04 – grounded questions,       briefing MISSES M4    →  grounded=1.0, misc NOT detected
S05 – grounded questions,       briefing OVER 250 w   →  grounded=1.0, within_250=False
S06 – grounded questions,       briefing has grade    →  grounded=1.0, forbidden=True
"""

from __future__ import annotations

import importlib
import json
import pathlib
import subprocess
import sys

import pytest

# ---------------------------------------------------------------------------
# Helpers to locate modules without installing the package
# ---------------------------------------------------------------------------

REPO_ROOT = pathlib.Path(__file__).parent.parent
DUMMY_DIR = REPO_ROOT / "results" / "dummy"
SCRIPTS_DIR = REPO_ROOT / "scripts"


def _ensure_dummy_outputs() -> None:
    """Generate the dummy output folder if it doesn't exist yet."""
    if not DUMMY_DIR.exists() or not any(DUMMY_DIR.glob("S*.json")):
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "make_dummy_outputs.py")],
            check=True,
            cwd=str(REPO_ROOT),
        )


def _load_evaluate():
    """Import evaluate.py as a module (adds scripts/ to sys.path if needed)."""
    scripts_str = str(SCRIPTS_DIR)
    if scripts_str not in sys.path:
        sys.path.insert(0, scripts_str)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "evaluate", SCRIPTS_DIR / "evaluate.py"
    )
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# Import once for the whole module
_ensure_dummy_outputs()
ev = _load_evaluate()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _row(student_id: str) -> dict:
    """Run the evaluator on the dummy folder and return the row for *student_id*."""
    rows = ev.run(DUMMY_DIR)
    matched = [r for r in rows if r["student_id"] == student_id]
    assert matched, f"No row found for {student_id}"
    return matched[0]


# ---------------------------------------------------------------------------
# S01 – fully grounded questions
# ---------------------------------------------------------------------------

class TestS01FullyGrounded:
    def test_all_questions_grounded(self):
        row = _row("S01")
        assert row["grounded_share"] == 1.0, (
            f"Expected all questions grounded, got {row['grounded_share']}"
        )

    def test_misconception_m1_detected(self):
        row = _row("S01")
        assert row["n_planted"] >= 1
        assert row["n_found"] >= 1, "M1 should be detected via keyword set (probability, null, true)"


# ---------------------------------------------------------------------------
# S02 – ungrounded questions
# ---------------------------------------------------------------------------

class TestS02Ungrounded:
    def test_no_questions_grounded(self):
        row = _row("S02")
        assert row["grounded_share"] == 0.0, (
            f"Expected 0 grounded questions, got {row['grounded_share']}"
        )

    def test_misconception_m2_detected(self):
        row = _row("S02")
        assert row["n_found"] >= 1, "M2 should be detected (briefing contains 'proves/proof')"


# ---------------------------------------------------------------------------
# S03 – briefing MISSES misconception M3
# ---------------------------------------------------------------------------

class TestS03MissingMisconception:
    def test_questions_grounded(self):
        row = _row("S03")
        assert row["grounded_share"] == 1.0

    def test_misconception_m3_not_detected(self):
        row = _row("S03")
        # S03 has M3 planted; the briefing deliberately omits it
        assert row["n_found"] == 0, (
            f"M3 should NOT be detected in S03 briefing, but got {row['n_found']} found"
        )


# ---------------------------------------------------------------------------
# S04 – briefing MISSES misconception M4
# ---------------------------------------------------------------------------

class TestS04MissingMisconception:
    def test_questions_grounded(self):
        row = _row("S04")
        assert row["grounded_share"] == 1.0

    def test_misconception_m4_not_detected(self):
        row = _row("S04")
        assert row["n_found"] == 0, (
            f"M4 should NOT be detected in S04 briefing, but got {row['n_found']} found"
        )


# ---------------------------------------------------------------------------
# S05 – briefing over 250 words
# ---------------------------------------------------------------------------

class TestS05OverWordLimit:
    def test_questions_grounded(self):
        row = _row("S05")
        assert row["grounded_share"] == 1.0

    def test_briefing_over_250_words(self):
        row = _row("S05")
        assert row["briefing_words"] > 250, (
            f"Expected briefing > 250 words, got {row['briefing_words']}"
        )

    def test_within_250_flag_false(self):
        row = _row("S05")
        assert row["within_250"] is False


# ---------------------------------------------------------------------------
# S06 – briefing contains a forbidden grade label
# ---------------------------------------------------------------------------

class TestS06ForbiddenOutput:
    def test_questions_grounded(self):
        row = _row("S06")
        assert row["grounded_share"] == 1.0

    def test_briefing_is_forbidden(self):
        row = _row("S06")
        assert row["forbidden"] is True, (
            "Briefing contains 'deserves an A' – guardrail should block it"
        )

    def test_guardrail_reason_mentions_grade(self):
        row = _row("S06")
        assert row["guardrail_reasons"], "Guardrail should report a reason"


# ---------------------------------------------------------------------------
# Unit tests for core helper functions
# ---------------------------------------------------------------------------

class TestIsQuestionGrounded:
    def test_six_word_exact_quote(self):
        submission = "The p-value of 0.03 means we reject the null hypothesis."
        question = "You wrote 'p-value of 0.03 means we reject the null' – what does that mean?"
        assert ev.is_question_grounded(question, submission)

    def test_content_word_overlap(self):
        submission = "Statistical significance and practical significance are distinct concepts."
        # 4 out of ~4 content words overlap: statistical, significance, practical, distinct
        question = "Why are statistical significance and practical significance distinct?"
        assert ev.is_question_grounded(question, submission)

    def test_ungrounded_short_question(self):
        submission = "The result was significant at alpha 0.05."
        question = "Did you consider effect size?"
        assert not ev.is_question_grounded(question, submission)

    def test_ungrounded_vague_question(self):
        submission = "The p-value of 0.03 provides evidence against the null hypothesis."
        question = "What about replication?"
        assert not ev.is_question_grounded(question, submission)


class TestMisconceptionDetection:
    def test_m1_keywords(self):
        briefing = "The student believes the probability that the null hypothesis is true is 0.03."
        assert ev._briefing_refers_to_misconception(briefing, "M1", "")

    def test_m1_six_word_evidence(self):
        evidence = "a p-value of 0.03 is the chance that the null hypothesis is true"
        briefing = "The student wrote that a p-value of 0.03 is the chance that the null hypothesis is true."
        assert ev._briefing_refers_to_misconception(briefing, "M1", evidence)

    def test_m2_keyword_proves(self):
        briefing = "The student claims the result proves that the intervention works."
        assert ev._briefing_refers_to_misconception(briefing, "M2", "")

    def test_m5_negative_no_mention(self):
        # M5: student omitted assumptions/limitations – briefing should note this
        briefing = "The student did not mention any assumptions or limitations of the test."
        assert ev._briefing_refers_to_misconception(briefing, "M5", "")

    def test_m5_negative_assumptions_mentioned(self):
        # If the briefing says assumptions are present, M5 is NOT detected
        briefing = "The student correctly identifies the assumptions of normality and independence."
        assert not ev._briefing_refers_to_misconception(briefing, "M5", "")

    def test_m3_not_detected_without_keywords(self):
        briefing = "The student applies the test correctly and identifies the threshold."
        assert not ev._briefing_refers_to_misconception(briefing, "M3", "")


class TestWordCount:
    def test_short_briefing_within_250(self):
        row = _row("S01")
        assert row["within_250"] is True

    def test_long_briefing_over_250(self):
        row = _row("S05")
        assert row["briefing_words"] > 250


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Explore existing codebase structure to understand what's already there
[x] Create data/answer_key/answer_key.json with planted misconceptions
[x] Write scripts/make_dummy_outputs.py
[x] Write scripts/evaluate.py
[x] Write tests/test_evaluate.py
[-] Run tests to validate


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && python scripts/make_dummy_outputs.py

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && python scripts/make_dummy_outputs.py && python scripts/evaluate.py results/dummy

---

### 👤 User

There is no `python` command on PATH here. Run Python and pytest with the project's Python 3.12 virtual environment (pytest is already installed in it): /Users/yiwei/.venvs/viva-prep/bin/python and /Users/yiwei/.venvs/viva-prep/bin/pytest, from the repository root. Do not install anything.

---

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && /Users/yiwei/.venvs/viva-prep/bin/python scripts/make_dummy_outputs.py && /Users/yiwei/.venvs/viva-prep/bin/python scripts/evaluate.py results/dummy

### 🤖 Assistant

> 🔧 called: execute_command

The venv doesn't have the package installed. I'll use the repo root in the path:

> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && PYTHONPATH=. /Users/yiwei/.venvs/viva-prep/bin/python scripts/evaluate.py results/dummy

### 🤖 Assistant

> 🔧 called: execute_command

The evaluator runs but the dummy data doesn't match the grounding and misconception rules. The issues are:

1. **Grounding** – questions in the dummy records quote from their own embedded submission text, but the evaluator loads `data/submissions/S01.md` etc. Those real submission files have different text. The dummy records need their questions grounded against the *real* submissions OR the dummy needs to use real submission excerpts.
2. **Misconception detection** – the briefings use M-code labels like "M1" and "M2" but `_INSTRUCTOR_ONLY` in the guardrail blocks those, and more importantly, the keyword sets and 6-word evidence rule aren't matching.
3. **S05 word count** – 250 exactly, not > 250.

Let me inspect what's going wrong precisely:

> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && PYTHONPATH=. /Users/yiwei/.venvs/viva-prep/bin/python -c "
import json, pathlib, sys
sys.path.insert(0, '.')
import importlib.util, re

spec = importlib.util.spec_from_file_location('evaluate', 'scripts/evaluate.py')
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)

# Debug S01 grounding
s01 = json.loads(pathlib.Path('results/dummy/S01.json').read_text())
sub_text = pathlib.Path('data/submissions/S01.md').read_text()
print('=== S01 questions vs real submission ===')
for q in s01['questions']:
    g = ev.is_question_grounded(q, sub_text)
    print(f'  grounded={g}: {q[:80]}')

print()
print('=== S01 briefing misconception M1 check ===')
# S01 has no misconceptions planted in answer_key
import json as j
ak = j.loads(pathlib.Path('data/answer_key/answer_key.json').read_text())
s01_ak = next(e for e in ak if e['student_id'] == 'S01')
print('S01 answer key:', s01_ak)
print()

# Check S02 misconception M2
s02 = json.loads(pathlib.Path('results/dummy/S02.json').read_text())
s02_ak = next(e for e in ak if e['student_id'] == 'S02')
print('=== S02 briefing M2 check ===')
print('Evidence:', s02_ak['evidence'])
print('Briefing:', s02['briefing'][:200])
result = ev._briefing_refers_to_misconception(s02['briefing'], 'M2', s02_ak['evidence'])
print('Detected:', result)

# Check keywords
print('Keywords for M2:', ev.MISCONCEPTION_KEYWORDS.get('M2'))
print('proves in briefing:', 'proves' in s02['briefing'].lower())
print('proof in briefing:', 'proof' in s02['briefing'].lower())
"


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && PYTHONPATH=. /Users/yiwei/.venvs/viva-prep/bin/python - <<'EOF'
import json, pathlib, sys, importlib.util

spec = importlib.util.spec_from_file_location('evaluate', 'scripts/evaluate.py')
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)

ak = json.loads(pathlib.Path('data/answer_key/answer_key.json').read_text())
ak_by_id = {e['student_id']: e for e in ak}

for sid in ['S01','S02','S03','S04','S05','S06']:
    rec = json.loads(pathlib.Path(f'results/dummy/{sid}.json').read_text())
    sub = pathlib.Path(f'data/submissions/{sid}.md').read_text() if pathlib.Path(f'data/submissions/{sid}.md').exists() else ''
    print(f'--- {sid} submission first 120 chars: {sub[:120]!r}')
    for q in rec['questions']:
        g = ev.is_question_grounded(q, sub)
        print(f'  grounded={g}: {q[:90]}')
    print()

print('=== Misconception keyword checks ===')
for sid, mid in [('S02','M2'),('S03','M3'),('S04','M4')]:
    rec = json.loads(pathlib.Path(f'results/dummy/{sid}.json').read_text())
    ak_e = ak_by_id[sid]
    evidence = ak_e.get('evidence','')
    briefing = rec['briefing']
    result = ev._briefing_refers_to_misconception(briefing, mid, evidence)
    print(f'{sid}/{mid}: detected={result}  evidence={evidence[:60]!r}')
    kws = ev.MISCONCEPTION_KEYWORDS.get(mid, [])
    print(f'  keywords={kws}, all_present={all(k in briefing.lower() for k in kws)}')
    print(f'  briefing snippet: {briefing[:150]!r}')
EOF


---

### 👤 User

Review found five problems. Please fix all of them in this task. Do not change anything under data/ or viva_prep/.

1. The acceptance command is plain `python scripts/evaluate.py results/dummy` from the repo root, without PYTHONPATH. Today it fails with ModuleNotFoundError for viva_prep. Make scripts/evaluate.py put the repository root on sys.path itself (near the top, before the guardrail import). Add a test that runs the script as a subprocess with sys.executable, cwd = repo root, and an environment without PYTHONPATH, and checks exit code 0 and that "TARGET RESULTS" is printed.

2. The dummy outputs do not match the data the evaluator reads. run() grounds questions against data/submissions/S##.md and reads data/answer_key/answer_key.json, but make_dummy_outputs.py writes questions and briefings based on its own inline SUBMISSION_S01..S06 texts and its own idea of which misconception each student has (for example the real S01 has no planted misconception and the real S02 has M1, not M2). So running the CLI on results/dummy gives meaningless numbers, and the tests never exercise the real loading path. Rewrite make_dummy_outputs.py so each dummy record is built from the real submission file and answer-key entry of that student (pick six students that have planted misconceptions): grounded questions quote real sentences of that student's submission, the "names its misconception" briefing quotes 6+ words of the real evidence sentence, the "misses" briefing does not. Write the folder relative to the repo root, not the current directory. Then change tests/test_evaluate.py so the per-student cases call run() on the dummy folder (or a tmp copy of it) and check the resulting rows: one fully grounded, one ungrounded, one misconception found, one missed, one over 250 words, one forbidden. Keep the small unit tests for the helper functions.

3. The keyword sets do not match the real misconception list. The definitions are in the MISCONCEPTIONS dict of scripts/generate_synthetic_data.py. M6 there is "correct terms used, but the explanation contradicts itself between two paragraphs", not "statistical significance guarantees a real effect". M2 currently requires both "proves" and "proof", which a normal briefing would not contain. Re-derive the keyword sets for M1, M2, M3, M4 and M6 from those definitions, matching word stems as substrings (for example "contradict" for M6, "prove" for M2), and keep each set small enough that a briefing naming the problem in plain words would match.

4. The M5 rule cannot match most negation words. In the regex, the stems omit, miss, lack, ignor and fail are followed by \b, so "omits", "missing", "lacks", "ignores" and "failed" never match, and "ignor" can never match at all. Fix the regex so inflected forms match, and require the negation word and "assumption"/"limitation" to be in the same sentence of the briefing (today any "not" anywhere in the briefing counts). Add tests for "The student omits any discussion of assumptions." (found) and a briefing that mentions assumptions in one sentence and says "not" only in another unrelated sentence (not found).

5. The success criterion agreed earlier is "every briefing is at most 250 words", not 80% of them. Keep printing the share, but mark that target PASS only when 100% of briefings are within 250 words, and update the docstring and any test that assumed 80%.

When done, run from the repo root, using only the project venv:
/Users/yiwei/.venvs/viva-prep/bin/python scripts/make_dummy_outputs.py && /Users/yiwei/.venvs/viva-prep/bin/python scripts/evaluate.py results/dummy && /Users/yiwei/.venvs/viva-prep/bin/pytest -q
and show me the output.

---

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[-] Fix #1: make evaluate.py add repo root to sys.path itself
[ ] Fix #2: rewrite make_dummy_outputs.py to use real submissions/answer-key data
[ ] Fix #3: re-derive keyword sets from generate_synthetic_data.py misconception definitions
[ ] Fix #4: fix M5 regex for inflected forms + sentence-scoped negation check
[ ] Fix #5: change 250-word target to 100% threshold (not 80%)
[ ] Update tests/test_evaluate.py for all fixes
[ ] Run full validation command and show output


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Explore existing codebase structure to understand what's already there
[x] Create data/answer_key/answer_key.json with planted misconceptions
[x] Write scripts/make_dummy_outputs.py (initial version)
[x] Write scripts/evaluate.py (initial version)
[x] Write tests/test_evaluate.py (initial version)
[-] Fix #1: make evaluate.py add repo root to sys.path itself; add subprocess test
[ ] Fix #2: rewrite make_dummy_outputs.py to use real submissions/answer-key data
[ ] Fix #3: re-derive keyword sets from generate_synthetic_data.py misconception definitions
[ ] Fix #4: fix M5 regex for inflected forms + sentence-scoped negation check
[ ] Fix #5: change 250-word target to 100% threshold (not 80%)
[ ] Update tests/test_evaluate.py for all fixes
[ ] Run full validation command and show output


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Explore existing codebase structure to understand what's already there
[x] Create data/answer_key/answer_key.json with planted misconceptions
[x] Write scripts/make_dummy_outputs.py
[x] Write scripts/evaluate.py
[x] Write tests/test_evaluate.py
[-] Fix #1: make evaluate.py add repo root to sys.path itself; add subprocess test
[ ] Fix #2: rewrite make_dummy_outputs.py to use real submissions/answer-key data
[ ] Fix #3: re-derive keyword sets from generate_synthetic_data.py misconception definitions
[ ] Fix #4: fix M5 regex for inflected forms + sentence-scoped negation check
[ ] Fix #5: change 250-word target to 100% threshold (not 80%)
[ ] Update tests/test_evaluate.py for all fixes
[ ] Run full validation command and show output


### 🤖 Assistant

> 🔧 called: read_file, read_file

First, let me read the generate_synthetic_data.py to get the canonical misconception definitions:

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/data/submissions/S02.md

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/scripts/generate_synthetic_data.py

### 🤖 Assistant

> 🔧 called: read_file, read_file, read_file

Now I have everything. Let me read a few more submission files to get good evidence sentences for the six dummy students I'll pick:

> 🔧 **read_file** — full submission body text

> 🔧 **read_file** — full submission body text

> 🔧 **read_file** — full submission body text

### 🤖 Assistant

> 🔧 called: write_file

Now I have everything I need. Let me now make all the fixes in one pass:

**Plan:**
- **Six dummy students** (all have planted misconceptions in the real answer key):
  - **S02** (M1) – grounded questions, briefing names M1 ✓
  - **S03** (M2) – grounded questions, briefing names M2 ✓  
  - **S07** (M1, M3) – ungrounded questions, briefing names M1 ✓
  - **S08** (M6) – grounded questions, briefing misses M6
  - **S10** (M2, M4) – grounded questions, briefing over 250 words
  - **S04** (M3) – grounded questions, briefing contains grade (forbidden)

Wait - I need to re-read the requirements more carefully. The six scenarios needed are: fully grounded, ungrounded, names misconception, misses misconception, over 250 words, forbidden. Let me pick the right students:

- **S02** (M1) – grounded questions, briefing names M1
- **S03** (M2) – ungrounded questions, briefing misses M2  
- **S04** (M3) – grounded questions, briefing names M3
- **S07** (M1+M3) – grounded questions, briefing misses M1
- **S08** (M6) – grounded questions, briefing over 250 words
- **S10** (M2+M4) – grounded questions, briefing contains grade (forbidden)

> 🔧 **write_file** — /Users/yiwei/Git/viva-prep/scripts/make_dummy_outputs.py

### 🤖 Assistant

> 🔧 called: write_file

Now let me rewrite `scripts/evaluate.py` with all fixes applied:

> 🔧 **write_file** — """Evaluate agent outputs against MVP success criteria.

Usage:
    python scripts/evaluate.py <output_folder>

Input:  folder of JSON files named S##.json, each with:
            { "student_id": str,
              "questions": [str],
              "briefing": str }

Output: per-student CSV at results/eval_<timestamp>.csv
        summary table + PASS/FAIL targets printed to stdout

Targets
-------
- grounded questions    >= 90 %
- planted misconceptions detected >= 80 %
- briefings <= 250 words: ALL briefings must meet this (100%)
- forbidden outputs     = 0
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
# ALL listed substrings must be present for the rule to fire.
# ---------------------------------------------------------------------------

MISCONCEPTION_KEYWORDS: dict[str, list[str]] = {
    "M1": ["probabilit", "null", "true"],      # "probability … null … true"
    "M2": ["prove"],                            # "proves / proof / proven"
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

    # Rule 2 – keyword substring set
    keywords = MISCONCEPTION_KEYWORDS.get(misconception_id, [])
    if keywords and all(kw in briefing_lower for kw in keywords):
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
    """
    from viva_prep.tools.guardrail import check_output

    student_id = record["student_id"]
    questions: list[str] = record.get("questions", [])
    briefing: str = record.get("briefing", "")

    # 1. Grounded questions
    if questions:
        grounded_count = sum(
            1 for q in questions if is_question_grounded(q, submission_text)
        )
        grounded_share = grounded_count / len(questions)
    else:
        grounded_count = 0
        grounded_share = 0.0

    # 2. Misconception detection
    planted: list[str] = []
    found: list[str] = []
    if answer_key_entry:
        planted = answer_key_entry.get("misconceptions", [])
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
    briefing_words = len(briefing.split())

    # 4. Forbidden output
    guardrail_result = check_output(briefing, "instructor")
    forbidden = not guardrail_result["allowed"]

    return {
        "student_id": student_id,
        "n_questions": len(questions),
        "grounded_count": grounded_count,
        "grounded_share": round(grounded_share, 4),
        "n_planted": n_planted,
        "n_found": n_found,
        "misconception_share": (
            round(misconception_share, 4) if misconception_share is not None else "N/A"
        ),
        "briefing_words": briefing_words,
        "within_250": briefing_words <= 250,
        "forbidden": forbidden,
        "guardrail_reasons": "; ".join(guardrail_result["reasons"]),
    }


# ---------------------------------------------------------------------------
# Summary & targets
# ---------------------------------------------------------------------------

def print_summary(rows: list[dict]) -> None:
    """Print a per-student table and aggregate target results."""
    header = (
        f"{'ID':<6} {'Q':>3} {'Grnd':>5} {'Grnd%':>6}  "
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
        print(
            f"{r['student_id']:<6} "
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

def run(output_folder: str | _pathlib.Path) -> list[dict]:
    """Evaluate all S##.json files in *output_folder*; return list of result rows."""
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
    if len(_sys.argv) < 2:
        print("Usage: python scripts/evaluate.py <output_folder>", file=_sys.stderr)
        _sys.exit(1)

    rows = run(_sys.argv[1])
    if not rows:
        print("No S##.json files found.", file=_sys.stderr)
        _sys.exit(1)

    print_summary(rows)

    csv_path = save_csv(rows, _REPO_ROOT / "results")
    print(f"Results saved to {csv_path}")


if __name__ == "__main__":
    main()


### 🤖 Assistant

> 🔧 called: write_file

Now rewrite the tests completely:

> 🔧 **write_file** — """Tests for scripts/evaluate.py using the dummy output folder.

Run:  pytest tests/test_evaluate.py

Each test targets one of the six synthetic students generated by
scripts/make_dummy_outputs.py.  The tests call evaluate.py's functions
directly so they are fast and give clear failure messages.

Dummy-student scenarios (built from real submissions + answer key):
  S02 – grounded questions,   briefing names M1       (misc detected)
  S03 – ungrounded questions, briefing misses M2      (0% grounded, misc NOT detected)
  S04 – grounded questions,   briefing names M3       (misc detected)
  S07 – grounded questions,   briefing misses M1+M3   (misc NOT detected)
  S08 – grounded questions,   briefing over 250 words (word limit)
  S10 – grounded questions,   briefing has grade      (forbidden)
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DUMMY_DIR = REPO_ROOT / "results" / "dummy"
SCRIPTS_DIR = REPO_ROOT / "scripts"


# ---------------------------------------------------------------------------
# Import evaluate as a module (avoids relying on installation)
# ---------------------------------------------------------------------------

def _load_evaluate():
    spec = importlib.util.spec_from_file_location(
        "evaluate", SCRIPTS_DIR / "evaluate.py"
    )
    mod = importlib.util.module_from_spec(spec)   # type: ignore[arg-type]
    spec.loader.exec_module(mod)                  # type: ignore[union-attr]
    return mod


# Generate the dummy folder once before the test session starts.
def pytest_configure(config):  # noqa: ARG001 – pytest hook
    """Ensure dummy outputs exist before any test runs."""
    if not DUMMY_DIR.exists() or not any(DUMMY_DIR.glob("S*.json")):
        subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "make_dummy_outputs.py")],
            check=True,
            cwd=str(REPO_ROOT),
        )


ev = _load_evaluate()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _row(student_id: str) -> dict:
    rows = ev.run(DUMMY_DIR)
    matched = [r for r in rows if r["student_id"] == student_id]
    assert matched, f"No row found for {student_id}"
    return matched[0]


# ---------------------------------------------------------------------------
# S02 – grounded questions + M1 detected
# ---------------------------------------------------------------------------

class TestS02GroundedMisconceptionFound:
    def test_all_questions_grounded(self):
        row = _row("S02")
        assert row["grounded_share"] == 1.0, (
            f"Expected 100% grounded, got {row['grounded_share']}"
        )

    def test_misconception_m1_detected(self):
        row = _row("S02")
        assert row["n_planted"] >= 1
        assert row["n_found"] >= 1, (
            "M1 should be detected: briefing contains 'probability', 'null', 'true'"
        )


# ---------------------------------------------------------------------------
# S03 – ungrounded questions + M2 NOT detected
# ---------------------------------------------------------------------------

class TestS03UngroundedMisconceptionMissed:
    def test_no_questions_grounded(self):
        row = _row("S03")
        assert row["grounded_share"] == 0.0, (
            f"Expected 0% grounded, got {row['grounded_share']}"
        )

    def test_misconception_m2_not_detected(self):
        row = _row("S03")
        assert row["n_found"] == 0, (
            f"M2 should NOT be detected in S03 briefing, got {row['n_found']} found"
        )


# ---------------------------------------------------------------------------
# S04 – grounded questions + M3 detected
# ---------------------------------------------------------------------------

class TestS04MisconceptionFound:
    def test_all_questions_grounded(self):
        row = _row("S04")
        assert row["grounded_share"] == 1.0

    def test_misconception_m3_detected(self):
        row = _row("S04")
        assert row["n_found"] >= 1, (
            "M3 should be detected: briefing contains 'significant' + 'practical'"
        )


# ---------------------------------------------------------------------------
# S07 – grounded questions + M1+M3 NOT detected
# ---------------------------------------------------------------------------

class TestS07MisconceptionMissed:
    def test_all_questions_grounded(self):
        row = _row("S07")
        assert row["grounded_share"] == 1.0

    def test_misconceptions_not_detected(self):
        row = _row("S07")
        assert row["n_found"] == 0, (
            f"M1/M3 should NOT be detected in S07 briefing, got {row['n_found']} found"
        )


# ---------------------------------------------------------------------------
# S08 – grounded questions + briefing over 250 words
# ---------------------------------------------------------------------------

class TestS08OverWordLimit:
    def test_all_questions_grounded(self):
        row = _row("S08")
        assert row["grounded_share"] == 1.0

    def test_briefing_over_250_words(self):
        row = _row("S08")
        assert row["briefing_words"] > 250, (
            f"Expected briefing > 250 words, got {row['briefing_words']}"
        )

    def test_within_250_flag_false(self):
        row = _row("S08")
        assert row["within_250"] is False


# ---------------------------------------------------------------------------
# S10 – grounded questions + briefing contains grade (forbidden)
# ---------------------------------------------------------------------------

class TestS10ForbiddenOutput:
    def test_all_questions_grounded(self):
        row = _row("S10")
        assert row["grounded_share"] == 1.0

    def test_briefing_is_forbidden(self):
        row = _row("S10")
        assert row["forbidden"] is True, (
            "Briefing contains 'deserves an A' – guardrail should block it"
        )

    def test_guardrail_reason_mentions_grade(self):
        row = _row("S10")
        assert row["guardrail_reasons"], "Guardrail should report a reason"


# ---------------------------------------------------------------------------
# Subprocess test (Fix #1): script adds repo root to sys.path itself
# ---------------------------------------------------------------------------

class TestCLISubprocess:
    def test_exit_zero_without_pythonpath(self):
        """evaluate.py must run without PYTHONPATH set, finding viva_prep itself."""
        env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "evaluate.py"), str(DUMMY_DIR)],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            env=env,
        )
        assert result.returncode == 0, (
            f"evaluate.py exited non-zero:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        assert "TARGET RESULTS" in result.stdout, (
            f"'TARGET RESULTS' not found in output:\n{result.stdout}"
        )


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------

class TestIsQuestionGrounded:
    def test_six_word_exact_quote(self):
        submission = "The p-value of 0.03 means we reject the null hypothesis."
        question = "You wrote 'p-value of 0.03 means we reject the null' – what does that mean?"
        assert ev.is_question_grounded(question, submission)

    def test_content_word_overlap(self):
        submission = "Statistical significance and practical significance are distinct concepts."
        question = "Why are statistical significance and practical significance distinct?"
        assert ev.is_question_grounded(question, submission)

    def test_ungrounded_short_question(self):
        submission = "The result was significant at alpha 0.05."
        question = "Did you consider effect size?"
        assert not ev.is_question_grounded(question, submission)

    def test_ungrounded_vague_question(self):
        submission = "The p-value of 0.03 provides evidence against the null hypothesis."
        question = "What about replication?"
        assert not ev.is_question_grounded(question, submission)


class TestMisconceptionDetection:
    def test_m1_keywords_stem(self):
        # "probability" stem + "null" + "true"
        briefing = "The student believes the probability that the null hypothesis is true is 0.03."
        assert ev._briefing_refers_to_misconception(briefing, "M1", "")

    def test_m1_six_word_evidence(self):
        evidence = "a p-value of 0.03 is the chance that the null hypothesis is true"
        briefing = "The student wrote that a p-value of 0.03 is the chance that the null hypothesis is true."
        assert ev._briefing_refers_to_misconception(briefing, "M1", evidence)

    def test_m2_keyword_proves(self):
        briefing = "The student claims the result proves that the intervention works."
        assert ev._briefing_refers_to_misconception(briefing, "M2", "")

    def test_m2_keyword_proof(self):
        briefing = "The student offers this as proof that Method A is superior."
        assert ev._briefing_refers_to_misconception(briefing, "M2", "")

    def test_m6_keyword_contradict(self):
        briefing = "The two paragraphs contradict each other on practical significance."
        assert ev._briefing_refers_to_misconception(briefing, "M6", "")

    def test_m3_not_detected_without_keywords(self):
        briefing = "The student applies the test correctly and identifies the threshold."
        assert not ev._briefing_refers_to_misconception(briefing, "M3", "")

    # M5 sentence-scoped negation
    def test_m5_same_sentence_omits(self):
        briefing = "The student omits any discussion of assumptions."
        assert ev._briefing_refers_to_misconception(briefing, "M5", ""), (
            "Should detect M5: 'omits' + 'assumptions' in same sentence"
        )

    def test_m5_same_sentence_not(self):
        briefing = "The student does not mention limitations or assumptions of the test."
        assert ev._briefing_refers_to_misconception(briefing, "M5", ""), (
            "Should detect M5: 'not' + 'limitations'/'assumptions' in same sentence"
        )

    def test_m5_negation_in_different_sentence(self):
        # "assumptions" in sentence 1, "not" only in a completely different sentence 2
        briefing = (
            "The student correctly identifies the assumptions of normality and independence. "
            "However, I do not think the conclusion is well supported."
        )
        assert not ev._briefing_refers_to_misconception(briefing, "M5", ""), (
            "Should NOT detect M5: 'assumptions' and 'not' are in different sentences"
        )

    def test_m5_assumptions_mentioned_positively(self):
        briefing = "The student correctly identifies the assumptions of normality and independence."
        assert not ev._briefing_refers_to_misconception(briefing, "M5", ""), (
            "Should NOT detect M5: assumptions mentioned positively, no negation in same sentence"
        )


# ---------------------------------------------------------------------------
# 250-word target must be 100%, not 80%
# ---------------------------------------------------------------------------

class TestWordLimitTarget:
    def test_summary_target_label_is_100_percent(self):
        """print_summary target line should say 100 % (all), not 80 %."""
        import io, contextlib
        buf = io.StringIO()
        rows = ev.run(DUMMY_DIR)
        with contextlib.redirect_stdout(buf):
            ev.print_summary(rows)
        output = buf.getvalue()
        assert "100 %" in output, (
            f"Expected '100 %' in target label, got:\n{output}"
        )

    def test_target_fails_when_any_briefing_over_250(self):
        """If even one briefing exceeds 250 words the target must be FAIL."""
        rows = ev.run(DUMMY_DIR)
        # S08 is over 250 words, so all_within_250 must be False
        n_within = sum(1 for r in rows if r["within_250"])
        assert n_within < len(rows), "S08 briefing should exceed 250 words"


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[x] Explore existing codebase structure to understand what's already there
[x] Create data/answer_key/answer_key.json with planted misconceptions
[x] Write scripts/make_dummy_outputs.py
[x] Write scripts/evaluate.py
[x] Write tests/test_evaluate.py
[x] Fix #1: make evaluate.py add repo root to sys.path itself; add subprocess test
[x] Fix #2: rewrite make_dummy_outputs.py to use real submissions/answer-key data
[x] Fix #3: re-derive keyword sets from generate_synthetic_data.py misconception definitions
[x] Fix #4: fix M5 regex for inflected forms + sentence-scoped negation check
[x] Fix #5: change 250-word target to 100% threshold (not 80%)
[x] Update tests/test_evaluate.py for all fixes
[-] Run full validation command and show output


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && /Users/yiwei/.venvs/viva-prep/bin/python scripts/make_dummy_outputs.py && /Users/yiwei/.venvs/viva-prep/bin/python scripts/evaluate.py results/dummy && /Users/yiwei/.venvs/viva-prep/bin/pytest -q 2>&1

### 🤖 Assistant

> 🔧 called: execute_command

Good progress. I can see there are stale dummy files from before (S01, S05, S06 still exist). Also the evaluator is picking up those old files. Let me look at the actual issues:

1. **S03 grounding** – 2 of 3 "ungrounded" questions are actually matching S03's real submission (S03 is Chloe's submission which discusses effect size, assumptions, sample size). Need vaguer questions that truly don't match.
2. **S08 word count** – briefing is only 215 words, not > 250. Need to add more words.
3. **Stale S01/S05/S06** – old dummy files in folder. Run will also see old dummy files with old IDs. Need the run to delete old files first OR remove the stale ones.
4. **M2 "proof"** – keyword is "prove" but "proof" contains "roo" not "prove". The stem "prove" doesn't match "proof". Need to also include "proof" as a separate check, or change the stem to something that covers both.

Let me fix all of these:

> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && /Users/yiwei/.venvs/viva-prep/bin/python -c "
import pathlib, re

# Check which questions on S03 are matching
sub = pathlib.Path('data/submissions/S03.md').read_text()
questions = [
    'Did you consider effect size?',
    'What about the assumptions of the test?',
    'Is the sample large enough?',
]

def tokenise(text):
    return re.findall(r'[a-z]+', text.lower())

STOPWORDS = frozenset('a an the and or but in on at to for of with is are was were be been being have has had do does did will would could should may might must shall can this that these those it its i we you he she they them their there here from by not no so if as when what which who how all any some more most very also just about than then only even though although because since while after before'.split())

def content_words(text):
    return [w for w in tokenise(text) if w not in STOPWORDS]

def ngrams(tokens, n):
    for i in range(len(tokens) - n + 1):
        yield ' '.join(tokens[i:i+n])

def sentences(text):
    return [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]

for q in questions:
    q_words = set(content_words(q))
    print(f'Q: {q!r}')
    print(f'  content words: {q_words}')
    for sent in sentences(sub):
        sent_words = set(content_words(sent))
        overlap = len(q_words & sent_words) / len(q_words) if q_words else 0
        if overlap > 0.3:
            print(f'  overlap={overlap:.0%}: {sent[:80]!r}')
    print()
"


### 🤖 Assistant

> 🔧 called: execute_command

The S03 submission happens to contain "effect size", "sample", "assumptions" etc. — those innocent questions accidentally match. I need truly ungrounded questions that don't touch S03's vocabulary at all. Let me also check what the S08 briefing actually has in the dummy file and fix the word count issue:

> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && /Users/yiwei/.venvs/viva-prep/bin/python -c "
import json, pathlib
rec = json.loads(pathlib.Path('results/dummy/S08.json').read_text())
briefing = rec['briefing']
words = briefing.split()
print(f'Word count: {len(words)}')
print(briefing[:200])
"


### 🤖 Assistant

> 🔧 called: apply_diff

The dummy file has 215 words but we need >250. That's what's in the already-generated file. I need to make the script write a longer briefing, and also delete old stale files. Let me fix make_dummy_outputs.py with:
1. Delete stale old files before writing
2. Longer S08 briefing (>250 words)
3. Truly ungrounded S03 questions (no stats vocabulary that appears in S03.md)
4. Fix M2 keyword to cover "proof" as well

> 🔧 **apply_diff** — /Users/yiwei/Git/viva-prep/scripts/make_dummy_outputs.py

### 🤖 Assistant

> 🔧 called: read_file

The file was already saved with the new content. Let me read the current file to get exact content:

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/scripts/make_dummy_outputs.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now I can make the targeted fixes. I need to:
1. Change S03 questions to truly ungrounded ones
2. Extend S08 briefing to >250 words
3. Clean old stale files in main()
4. Fix M2 keyword in evaluate.py to cover "proof" (it's a separate root from "prove")

> 🔧 **apply_diff** — /Users/yiwei/Git/viva-prep/scripts/make_dummy_outputs.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now fix the M2 keyword in evaluate.py to cover "proof" as well as "prove":

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:48
-------
MISCONCEPTION_KEYWORDS: dict[str, list[str]] = {
    "M1": ["probabilit", "null", "true"],      # "probability … null … true"
    "M2": ["prove"],                            # "proves / proof / proven"
    "M3": ["significant", "practical"],         # conflates stat sig with practical
    "M4": ["identical", "null"],                # "null → methods identical"
    # M5 handled separately (negative pattern)
    "M6": ["contradict"],                       # self-contradictory explanation
}
=======
MISCONCEPTION_KEYWORDS: dict[str, list[str]] = {
    "M1": ["probabilit", "null", "true"],       # "probability … null … true"
    # M2: "prove" covers "proves/proven"; "proof" shares no stem with "prove"
    # so we list both as alternatives – the OR is implemented below.
    "M2": ["prov"],                             # "proves / proven / proof / disprove"
    "M3": ["significant", "practical"],         # conflates stat sig with practical
    "M4": ["identical", "null"],                # "null → methods identical"
    # M5 handled separately (negative pattern)
    "M6": ["contradict"],                       # self-contradictory explanation
}
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: apply_diff

Wait - "prov" matches "proves", "proven", "proof" (p-r-o-v is a substring of "proof"? No: p-r-o-o-f. "prov" is NOT in "proof". Let me check: p-r-o-o-f vs p-r-o-v. The 4th character is 'o' vs 'v' — "prov" is NOT a substring of "proof". I need to keep both stems:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:54
-------
# ALL listed substrings must be present for the rule to fire.
# ---------------------------------------------------------------------------

MISCONCEPTION_KEYWORDS: dict[str, list[str]] = {
    "M1": ["probabilit", "null", "true"],       # "probability … null … true"
    # M2: "prove" covers "proves/proven"; "proof" shares no stem with "prove"
    # so we list both as alternatives – the OR is implemented below.
    "M2": ["prov"],                             # "proves / proven / proof / disprove"
    "M3": ["significant", "practical"],         # conflates stat sig with practical
    "M4": ["identical", "null"],                # "null → methods identical"
    # M5 handled separately (negative pattern)
    "M6": ["contradict"],                       # self-contradictory explanation
}
=======
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
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: read_file

Now I need to update the `_briefing_refers_to_misconception` function to use `any()` for M2 instead of `all()`:

> 🔧 **read_file** — _briefing_refers_to_misconception Rule 2 keyword check implementation

### 🤖 Assistant

> 🔧 called: read_file



> 🔧 **read_file** — _briefing_refers_to_misconception Rule 2 keyword check implementation

### 🤖 Assistant

> 🔧 called: apply_diff

The current code uses `all()` for all keyword sets. For M2 (["prove", "proof"]), we want `any()`. For M1, M3, M4, M6 we still want `all()`. Let me make M2 a special case using a dedicated OR-list approach. The cleanest approach: use `any()` for M2 specifically since the list is OR alternatives, not AND requirements:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:174
-------
    # Rule 2 – keyword substring set
    keywords = MISCONCEPTION_KEYWORDS.get(misconception_id, [])
    if keywords and all(kw in briefing_lower for kw in keywords):
        return True
=======
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
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: execute_command

Now also check: the S07 "misses M1" test – the S07 briefing currently contains "H0" and "reject" but NOT "probability"+"null"+"true" together. Let me verify quickly and also check if the S03 new questions will now truly be ungrounded:

> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && /Users/yiwei/.venvs/viva-prep/bin/python - <<'EOF'
import re, pathlib

STOPWORDS = frozenset('a an the and or but in on at to for of with is are was were be been being have has had do does did will would could should may might must shall can this that these those it its i we you he she they them their there here from by not no so if as when what which who how all any some more most very also just about than then only even though although because since while after before'.split())

def tokenise(t): return re.findall(r'[a-z]+', t.lower())
def content_words(t): return [w for w in tokenise(t) if w not in STOPWORDS]
def ngrams(tokens, n):
    for i in range(len(tokens)-n+1): yield ' '.join(tokens[i:i+n])
def sentences(t): return [s.strip() for s in re.split(r'[.!?]+', t) if s.strip()]

def is_grounded(q, sub):
    sub_toks = tokenise(sub)
    sub6 = set(ngrams(sub_toks, 6))
    q_toks = tokenise(q)
    for gram in ngrams(q_toks, 6):
        if gram in sub6: return True, '6gram'
    q_words = set(content_words(q))
    if not q_words: return False, 'empty'
    for sent in sentences(sub):
        sw = set(content_words(sent))
        overlap = len(q_words & sw) / len(q_words)
        if overlap >= 0.6: return True, f'overlap={overlap:.0%}'
    return False, 'none'

s03 = pathlib.Path('data/submissions/S03.md').read_text()
print('S03 new questions:')
for q in ['How does pedagogy shape your reading of this result?',
          'What curriculum changes would you advocate for?',
          'Which demographic factors might moderate the outcome?']:
    g, reason = is_grounded(q, s03)
    print(f'  {g} ({reason}): {q}')

print()
# Check S07 M1 keywords in its briefing
briefing_s07 = ("The student shows familiarity with hypothesis testing vocabulary and "
    "correctly identifies that we reject H0 at alpha 0.05. Their discussion "
    "of the 4.1-point difference acknowledges that replication is needed. "
    "The response is coherent and reasonably well structured. The instructor "
    "should explore whether the student understands what failing to reject H0 "
    "would and would not imply about the two methods.")
bl = briefing_s07.lower()
print(f'S07 M1 check: probabilit={bool("probabilit" in bl)}, null={bool("null" in bl)}, true={bool("true" in bl)}')
print(f'S07 M3 check: significant={bool("significant" in bl)}, practical={bool("practical" in bl)}')

# check S08 briefing word count
briefing_s08 = ("The student provides a detailed and methodologically careful account of "
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
    "Overall a strong and well-structured response worth developing further.")
print(f'\nS08 briefing word count: {len(briefing_s08.split())}')

# check M2 test "proof"
print(f'\nM2 "proof" in "offers this as proof": {"proof" in "The student offers this as proof that Method A is superior.".lower()}')
EOF


### 🤖 Assistant

> 🔧 called: apply_diff

S03 ungrounded ✓, S07 M1/M3 not detected ✓, M2 "proof" ✓. But S08 briefing is 242 words — still not > 250. I need 9 more words. Let me add a sentence:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:188
-------
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
            "Overall a strong and well-structured response worth developing further."
=======
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
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && /Users/yiwei/.venvs/viva-prep/bin/python - <<'EOF'
b = ("The student provides a detailed and methodologically careful account of "
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
    "be a productive line of questioning in the viva. Overall a strong response.")
print(len(b.split()))
EOF


### 🤖 Assistant

> 🔧 called: execute_command

257 words — over 250. Now run the full validation:

> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && /Users/yiwei/.venvs/viva-prep/bin/python scripts/make_dummy_outputs.py && /Users/yiwei/.venvs/viva-prep/bin/python scripts/evaluate.py results/dummy && /Users/yiwei/.venvs/viva-prep/bin/pytest -q 2>&1

### 🤖 Assistant

> 🔧 called: update_todo_list

All 155 tests pass. The evaluator runs correctly end-to-end. Let me verify the output makes sense:

- **S02** – 3/3 grounded ✓, M1 detected ✓
- **S03** – 0/3 grounded ✓, M2 not detected ✓  
- **S04** – 3/3 grounded ✓, M3 detected ✓
- **S07** – 3/3 grounded ✓, M1+M3 not detected (0/2) ✓
- **S08** – 3/3 grounded ✓, 257 words > 250 ✓, within_250=no ✓
- **S10** – 3/3 grounded ✓, forbidden ✓ (grade label)
- S10 gets 1/2 misconceptions found (50%) — M2 detected ("proves" in S10 submission), M4 not detected — that's expected since the S10 briefing about "proof of equivalence" only mentions proof, not "identical"+"null" together
- Targets FAIL as expected (dummy data is intentionally mixed)

> 🔧 **update_todo_list** — 
[x] Explore existing codebase structure to understand what's already there
[x] Create data/answer_key/answer_key.json with planted misconceptions
[x] Write scripts/make_dummy_outputs.py
[x] Write scripts/evaluate.py
[x] Write tests/test_evaluate.py
[x] Fix #1: make evaluate.py add repo root to sys.path itself; add subprocess test
[x] Fix #2: rewrite make_dummy_outputs.py to use real submissions/answer-key data
[x] Fix #3: re-derive keyword sets from generate_synthetic_data.py misconception definitions
[x] Fix #4: fix M5 regex for inflected forms + sentence-scoped negation check
[x] Fix #5: change 250-word target to 100% threshold (not 80%)
[x] Update tests/test_evaluate.py for all fixes
[x] Run full validation command and show output


### 🤖 Assistant

All 155 tests pass. Here's the full output of the acceptance command:

```
Wrote 6 dummy output files to /…/results/dummy/
ID       Q  Grnd  Grnd%  Plant Found  Misc%  Words  <=250   Forb
----------------------------------------------------------------
S02      3     3   100%      1     1   100%     55    yes     no
S03      3     0     0%      1     0     0%     48    yes     no
S04      3     3   100%      1     1   100%     47    yes     no
S07      3     3   100%      2     0     0%     59    yes     no
S08      3     3   100%      1     0     0%    257     no     no
S10      3     3   100%      2     1    50%     65    yes    YES

TARGET RESULTS
------------------------------------------------------------
  [FAIL]  Grounded questions >= 90 %
          83.3% (15/18)
  [FAIL]  Misconceptions detected >= 80 %
          37.5% (3/8)
  [FAIL]  Briefings <= 250 words: 100 % (all)
          83.3% (5/6)
  [FAIL]  Forbidden outputs = 0
          1 forbidden

155 passed in 0.15s
```

Summary of all five fixes:

**Fix 1 — `sys.path` self-repair**: [`evaluate.py`](scripts/evaluate.py:31) resolves `_REPO_ROOT` from `__file__` and inserts it into `sys.path` before any `viva_prep` import. [`TestCLISubprocess`](tests/test_evaluate.py:173) runs the script as a subprocess with `PYTHONPATH` stripped from the environment and asserts exit code 0 and `"TARGET RESULTS"` in stdout.

**Fix 2 — dummy outputs from real data**: [`make_dummy_outputs.py`](scripts/make_dummy_outputs.py) now reads real `data/submissions/S##.md` files and `data/answer_key/answer_key.json`. Questions quote verbatim 6-word spans from the real submissions; the `main()` function deletes stale files from prior runs. Tests call `run(DUMMY_DIR)` which exercises the actual loading path.

**Fix 3 — keyword sets**: [`MISCONCEPTION_KEYWORDS`](scripts/evaluate.py:58) re-derived from `generate_synthetic_data.py`'s `MISCONCEPTIONS` dict: M1 uses stem `"probabilit"`, M2 uses `["prove", "proof"]` with `any()`, M3 stays `["significant", "practical"]`, M6 uses `"contradict"`. M2 uses `any()` since the two stems are alternatives, not conjunctions.

**Fix 4 — M5 sentence-scoped regex**: [`_briefing_refers_to_misconception`](scripts/evaluate.py:155) for M5 splits the briefing into sentences and requires both `\bassumption|\blimitation` AND a negation pattern (including `omit`, `omits`, `omitted`, `miss`, `misses`, `lacks`, `ignores`, `failed`, etc.) in the **same sentence**. Tests confirm "The student omits any discussion of assumptions." fires and a briefing where "assumptions" and "not" are in different sentences does not.

**Fix 5 — 100% word-limit target**: [`print_summary`](scripts/evaluate.py:298) marks the briefing-length target `PASS` only when `n_within_250 == len(rows)` (all briefings ≤ 250 words), and the label reads `"Briefings <= 250 words: 100 % (all)"`.