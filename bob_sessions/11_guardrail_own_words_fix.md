# Guardrail fix after round 2. The authorship rule added in round 2 (Rule 2 in viva_prep/tools/guardrail.py) now blocks normal teaching questions that ask the student to answer in their own words. Only change viva_prep/tools/guardrail.py and tests/test_guardrail.py. Do not change prompts/, agents/, data/, results/ or scripts/. Do not run the watsonx backend, and do not create, read or edit .env or any credential file.

1. These three questions come from the round 2 run. They ask the student to use their own words, so they must be allowed for both audiences:
   - "In your own words, how would you explain the meaning of the p‑value definition you provided?" (note the non-breaking hyphen in p‑value)
   - "In your own words, can you walk through how the 4.1‑point difference might be practically important for students?"
   - "Please elaborate in your own words on how you would communicate the findings to a non-specialist audience?"
   Also allow: "In your own words, what does it mean to reject the null hypothesis?" and "Tell me in your own words why the sample size matters."

2. Statements that vouch for authorship must stay blocked for both audiences. Keep all existing blocked tests passing and add these:
   - "Your answer is in your own words."
   - "This is clearly in your own words."
   - "The explanation is in their own words. Ask the student to restate the definition in their own words."
   The last one has a vouching sentence and a teaching sentence in the same text. At the moment the whole text is allowed as soon as any teaching form appears anywhere in it. Check each sentence that contains "own words" on its own, so a teaching sentence cannot excuse a vouching sentence elsewhere in the text.

3. Add a test for every example in items 1 and 2. All existing guardrail tests must still pass.

When done, run from the repo root with the venv only, and show me the output:
/Users/yiwei/.venvs/viva-prep/bin/pytest -q && git status --short && git diff --stat

---

**Status:** active  **Date:** 2026-10-31

---

### 👤 User

Guardrail fix after round 2. The authorship rule added in round 2 (Rule 2 in viva_prep/tools/guardrail.py) now blocks normal teaching questions that ask the student to answer in their own words. Only change viva_prep/tools/guardrail.py and tests/test_guardrail.py. Do not change prompts/, agents/, data/, results/ or scripts/. Do not run the watsonx backend, and do not create, read or edit .env or any credential file.

1. These three questions come from the round 2 run. They ask the student to use their own words, so they must be allowed for both audiences:
   - "In your own words, how would you explain the meaning of the p‑value definition you provided?" (note the non-breaking hyphen in p‑value)
   - "In your own words, can you walk through how the 4.1‑point difference might be practically important for students?"
   - "Please elaborate in your own words on how you would communicate the findings to a non-specialist audience?"
   Also allow: "In your own words, what does it mean to reject the null hypothesis?" and "Tell me in your own words why the sample size matters."

2. Statements that vouch for authorship must stay blocked for both audiences. Keep all existing blocked tests passing and add these:
   - "Your answer is in your own words."
   - "This is clearly in your own words."
   - "The explanation is in their own words. Ask the student to restate the definition in their own words."
   The last one has a vouching sentence and a teaching sentence in the same text. At the moment the whole text is allowed as soon as any teaching form appears anywhere in it. Check each sentence that contains "own words" on its own, so a teaching sentence cannot excuse a vouching sentence elsewhere in the text.

3. Add a test for every example in items 1 and 2. All existing guardrail tests must still pass.

When done, run from the repo root with the venv only, and show me the output:
/Users/yiwei/.venvs/viva-prep/bin/pytest -q && git status --short && git diff --stat

---

### 🤖 Assistant

> 🔧 called: read_file, read_file

Let me start by reading the current guardrail implementation and tests.

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/viva_prep/tools/guardrail.py

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/tests/test_guardrail.py

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have a clear picture. Let me analyze the problem:

**Problem**: `_authorship_violation` checks the *whole text* with `_OWN_WORDS_TEACHING`. So if any teaching sentence exists anywhere, it exempts the entire text — including vouching sentences in the same text.

**Also**: The teaching pattern `_OWN_WORDS_TEACHING` doesn't cover question forms like "In your own words, how would you..." or "Tell me in your own words why...".

**Fix needed**:
1. Change `_authorship_violation` to check *each sentence* containing "own words" individually (sentence-level isolation).
2. Extend `_OWN_WORDS_TEACHING` to cover the "In your own words, ..." question forms and "Tell me in your own words..." form.

> 🔧 **update_todo_list** — [-] Fix _OWN_WORDS_TEACHING pattern to cover "In your own words, ..." question forms and "Tell me in your own words" form
[-] Fix _authorship_violation to check each "own words" sentence individually (sentence-level isolation)
[ ] Add new blocked tests: vouching sentences and mixed vouching+teaching text
[ ] Add new allowed tests: the five round-2 teaching questions
[ ] Run pytest and verify all pass


### 🤖 Assistant

> 🔧 called: apply_diff

Now let me think through the sentence-splitting approach carefully. The mixed text from item 2.3 is:
> "The explanation is in their own words. Ask the student to restate the definition in their own words."

Sentence 1: "The explanation is in their own words." → vouching → BLOCKED  
Sentence 2: "Ask the student to restate the definition in their own words." → teaching → allowed

So the whole text must be BLOCKED. The current code allows it because `_OWN_WORDS_TEACHING` matches sentence 2.

For the teaching questions from item 1, `_OWN_WORDS_TEACHING` needs to match:
- "In your own words, how would you explain..." → starts with "in your own words", then asks a question
- "In your own words, can you walk through..." → already covers "can you"... but "own words" comes first
- "Please elaborate in your own words on how..."  → "elaborate" isn't in the teaching verb list
- "In your own words, what does it mean to reject..." → starts with "in your own words"
- "Tell me in your own words why..." → "tell" isn't in the teaching verb list

Let me design the fix:

> 🔧 **apply_diff** — /Users/yiwei/Git/viva-prep/viva_prep/tools/guardrail.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now let me add all the new tests:

> 🔧 **apply_diff** — /Users/yiwei/Git/viva-prep/tests/test_guardrail.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now add the allowed teaching-question tests. I'll insert them after the existing `test_own_words_teaching_explain_imperative` test:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:303
-------
    def test_own_words_teaching_explain_imperative(self):
        _allowed("Explain in your own words why we reject the null hypothesis.")

    # --- Normal positive feedback that contains no violations ---
=======
    def test_own_words_teaching_explain_imperative(self):
        _allowed("Explain in your own words why we reject the null hypothesis.")

    # New round-2 teaching questions — must be allowed for both audiences

    def test_own_words_teaching_pvalue_definition_instructor(self):
        # Non-breaking hyphen in p‑value (U+2011)
        _allowed(
            "In your own words, how would you explain the meaning of the"
            " p\u2011value definition you provided?"
        )

    def test_own_words_teaching_pvalue_definition_student(self):
        _allowed(
            "In your own words, how would you explain the meaning of the"
            " p\u2011value definition you provided?",
            audience="student",
        )

    def test_own_words_teaching_point_difference_instructor(self):
        _allowed(
            "In your own words, can you walk through how the 4.1\u2011point"
            " difference might be practically important for students?"
        )

    def test_own_words_teaching_point_difference_student(self):
        _allowed(
            "In your own words, can you walk through how the 4.1\u2011point"
            " difference might be practically important for students?",
            audience="student",
        )

    def test_own_words_teaching_elaborate_instructor(self):
        _allowed(
            "Please elaborate in your own words on how you would communicate"
            " the findings to a non-specialist audience?"
        )

    def test_own_words_teaching_elaborate_student(self):
        _allowed(
            "Please elaborate in your own words on how you would communicate"
            " the findings to a non-specialist audience?",
            audience="student",
        )

    def test_own_words_teaching_null_hypothesis_instructor(self):
        _allowed("In your own words, what does it mean to reject the null hypothesis?")

    def test_own_words_teaching_null_hypothesis_student(self):
        _allowed(
            "In your own words, what does it mean to reject the null hypothesis?",
            audience="student",
        )

    def test_own_words_teaching_tell_me_instructor(self):
        _allowed("Tell me in your own words why the sample size matters.")

    def test_own_words_teaching_tell_me_student(self):
        _allowed("Tell me in your own words why the sample size matters.", audience="student")

    # --- Normal positive feedback that contains no violations ---
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: execute_command

Now let me think through the edge cases before running tests:

1. **"Your answer is in your own words."** — `_OWN_WORDS_ANY` matches "in your own words". Sentence split: just one sentence. `_OWN_WORDS_TEACHING` checks: "your" isn't a teaching verb, no "ask", no "can you". The leading "in your own words, ..." pattern requires a comma/colon after "words" — "in your own words." ends with "." not ",". So this would be blocked. ✓

2. **"This is clearly in your own words."** — same analysis. ✓

3. **Mixed text**: "The explanation is in their own words. Ask the student to restate the definition in their own words."
   - Sentence split on ". " → ["The explanation is in their own words.", "Ask the student to restate the definition in their own words."]
   - Sentence 1: `_OWN_WORDS_ANY` matches. `_OWN_WORDS_TEACHING`? No teaching verb before "in their own words", no "ask", no "can you", no leading comma. → BLOCKED ✓
   - (We return True immediately.)

4. **"In your own words, how would you explain..."** — `_OWN_WORDS_ANY` matches. `_OWN_WORDS_TEACHING`: the leading pattern `\bin\s+your\s+own\s+words\s*[,:]` matches because there's a comma after "words". ✓

5. **"Please elaborate in your own words on how..."** — `_OWN_WORDS_ANY` matches. `_OWN_WORDS_TEACHING`: "elaborate" is in the verb list, and "in your own words" follows. ✓

6. **"Tell me in your own words why..."** — `_OWN_WORDS_ANY` matches. `_OWN_WORDS_TEACHING`: "tell" is in the verb list, and "in your own words" follows. ✓

7. **"In your own words, can you walk through..."** — leading comma pattern matches. ✓

Wait, I need to re-check "In your own words, can you walk through...". Let me trace:
- `_OWN_WORDS_ANY`: matches "in your own words". 
- `_OWN_WORDS_TEACHING` leading pattern: `\bin\s+your\s+own\s+words\s*[,:]` → matches "In your own words,". ✓

Now let me also verify the existing tests won't break:
- "Can you explain, in your own words, what the p-value of 0.03 means?" → `_OWN_WORDS_ANY` matches "in your own words". `_OWN_WORDS_TEACHING`: "can you" pattern: `\bcan\s+you\b.*?\bin\s+your\s+own\s+words\b` → matches. ✓
- "Ask the student to restate the definition in their own words." → single sentence; `_OWN_WORDS_TEACHING` "ask" pattern matches. ✓
- "Explain in your own words why we reject..." → "explain" is in verb list, "in your own words" follows. ✓

Now run the tests:

> 🔧 **execute_command** — /Users/yiwei/.venvs/viva-prep/bin/pytest -q && git status --short && git diff --stat

### 🤖 Assistant

> 🔧 called: update_todo_list

375 passed, 2 skipped (the 2 skips are pre-existing and unrelated). Here's a summary of what changed:

> 🔧 **update_todo_list** — [x] Fix _OWN_WORDS_TEACHING pattern to cover "In your own words, ..." question forms and "Tell me in your own words" form
[x] Fix _authorship_violation to check each "own words" sentence individually (sentence-level isolation)
[x] Add new blocked tests: vouching sentences and mixed vouching+teaching text
[x] Add new allowed tests: the five round-2 teaching questions
[x] Run pytest and verify all pass


### 🤖 Assistant

All 375 tests pass. Here's what was done:

---

### Changes

#### [`viva_prep/tools/guardrail.py`](viva_prep/tools/guardrail.py)

**1. Sentence-level isolation in [`_authorship_violation()`](viva_prep/tools/guardrail.py)** (the root bug):

The old logic called `_OWN_WORDS_TEACHING.search(text)` on the *entire text*, so a teaching sentence anywhere in the text exempted every vouching sentence too. The fix splits the text into sentences (on `. `, `? `, `! `) and checks each sentence that contains "own words" on its own — a teaching sentence in sentence 2 can no longer excuse a vouching sentence in sentence 1.

**2. Extended [`_OWN_WORDS_TEACHING`](viva_prep/tools/guardrail.py) pattern** to cover the three new forms missing from round 2:

| Form | Example | How it now matches |
|---|---|---|
| Leading "In your own words, …" | *"In your own words, how would you explain…"* | new `\bin…own\s+words\s*[,:]` branch |
| `elaborate` | *"Please elaborate in your own words on…"* | added `elaborate` to the verb list |
| `tell` | *"Tell me in your own words why…"* | added `tell` to the verb list |

#### [`tests/test_guardrail.py`](tests/test_guardrail.py)

**4 new blocked tests** in `TestBlocked`:
- `test_own_words_vouching_your` — "Your answer is in your own words."
- `test_own_words_vouching_clearly` — "This is clearly in your own words."
- `test_own_words_mixed_vouching_and_teaching` / `_student` — the mixed sentence that has a voucher followed by a teaching request

**10 new allowed tests** in `TestAllowed` (5 questions × 2 audiences):
- `p‑value definition` (with U+2011 non-breaking hyphen)
- `4.1‑point difference`
- `elaborate … non-specialist audience`
- `what does it mean to reject the null hypothesis`
- `Tell me … why the sample size matters`

---

### 👤 User

Review found that the new teaching forms are too loose. These five sentences vouch for authorship, but they are now allowed. They must be blocked for both audiences:
- "The explanation is coherent and in their own words, which shows understanding."
- "The response is clear and written in the student's own words, with good structure."
- "I can tell this is in your own words."
- "The student gave an elaborate answer in their own words."
- "Overall the reasoning is coherent and in their own words: it goes beyond definitions."

The cause: the "in … own words," branch and the verb branch match anywhere in the sentence. Tighten _OWN_WORDS_TEACHING so a sentence that contains "own words" counts as a teaching request only when one of these holds:
(a) the sentence starts (after optional quotes, spaces or "Please") with a request verb: explain, restate, describe, summarise, summarize, put, phrase, express, state, say, elaborate, ask, "tell me" or "tell us", "walk me through";
(b) the sentence starts with "In your own words," (second person only);
(c) the sentence asks "can you", "could you" or "would you" before the "own words" phrase.

Keep the per-sentence check. Add a blocked test for each of the five sentences above (both audiences). All existing tests, including the allowed questions you added, must still pass.

Then run the same command and show me the output:
/Users/yiwei/.venvs/viva-prep/bin/pytest -q && git status --short && git diff --stat

---

### 🤖 Assistant

> 🔧 called: read_file

Let me first verify the current state of the pattern and then think through the tightening carefully.

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/viva_prep/tools/guardrail.py

### 🤖 Assistant

> 🔧 called: apply_diff

Good. Now I need to trace exactly why the five false-negatives slip through:

1. **"The explanation is coherent and in their own words, which shows understanding."** — The `_OWN_WORDS_ANY` matches "in their own words". Then `_OWN_WORDS_TEACHING` checks the sentence. The *leading comma branch* `\bin\s+their\s+own\s+words\s*[,:]` fires because "own words," has a comma. That's the bug — the leading-comma branch was intended only for sentences that *start* with "In your own words," but it matches the comma anywhere.

2. **"The response is clear and written in the student's own words, with good structure."** — Same: "own words," has a comma, leading branch fires.

3. **"I can tell this is in your own words."** — The verb branch: `\btell\b.*?\bin\s+your\s+own\s+words\b` fires because "tell" appears before "in your own words".

4. **"The student gave an elaborate answer in their own words."** — The verb branch: `\belaborate\b.*?\bin\s+their\s+own\s+words\b` fires.

5. **"Overall the reasoning is coherent and in their own words: it goes beyond definitions."** — The leading colon branch: `\bin\s+their\s+own\s+words\s*[,:]` fires on the colon.

The fix: the spec says conditions (a), (b), (c) are defined by what the sentence **starts** with (after optional quotes/spaces/"Please"). I need to anchor all three branches to the start of the sentence (using `\A` since we're matching per-sentence strings).

Let me now write the tightened `_OWN_WORDS_TEACHING`:

- **(a)** Sentence starts with (optional leading junk then) a request verb: `\A[\s"'«]*(?:please\s+)?(?:explain|restate|...)\b.*\bin\s+...\s+own\s+words\b`
- **(b)** Sentence starts with "In your own words,": `\A[\s"'«]*[Ii]n\s+your\s+own\s+words\s*,`  — **second person only**
- **(c)** Sentence contains "can you / could you / would you" **before** the "own words" phrase: `\bcan\s+you\b|\bcould\s+you\b|\bwould\s+you\b` ... `\bin\s+...\s+own\s+words\b`

For (c), "can you" etc. don't need to be at the start — they naturally appear early in a question and before "own words".

For (b), note that the spec says **second person only** for the leading form — "In your own words," (not "in their own words,").

Let me also check which existing allowed tests touch these conditions to make sure I don't break them:

- `"Can you explain, in your own words, what the p-value of 0.03 means?"` → condition (c): "can you" before "in your own words" ✓
- `"Ask the student to restate the definition in their own words."` → condition (a): starts with "Ask" ✓  
- `"Explain in your own words why we reject the null hypothesis."` → condition (a): starts with "Explain" ✓
- `"In your own words, how would you explain the meaning of the p‑value…?"` → condition (b): starts with "In your own words," ✓
- `"In your own words, can you walk through how the 4.1‑point difference…?"` → condition (b): starts with "In your own words," ✓
- `"Please elaborate in your own words on how you would communicate…?"` → condition (a): starts with "Please elaborate" ✓
- `"In your own words, what does it mean to reject the null hypothesis?"` → condition (b): starts with "In your own words," ✓
- `"Tell me in your own words why the sample size matters."` → condition (a): starts with "Tell me" — but "tell me" is "tell" followed immediately by "me". Need to handle this — "tell" alone would match "I can tell", but "tell me / tell us" at sentence start is safe. The spec explicitly lists "tell me" and "tell us" as allowed request forms in condition (a).

So for "tell", I should require it to be followed by "me" or "us" (making it a direct address), or I should anchor on sentence-start so "I can tell" won't trigger.

With the `\A` anchor on sentence start, "I can tell this is in your own words." starts with "I", not a request verb — so condition (a) won't fire. And "Tell me in your own words..." starts with "Tell" → fires. 

Similarly "elaborate": "The student gave an elaborate answer in their own words." starts with "The", not "elaborate" — condition (a) won't fire. "Please elaborate in your own words..." starts with "Please elaborate" → fires. ✓

Now let me implement this:

> 🔧 **apply_diff** — /Users/yiwei/Git/viva-prep/viva_prep/tools/guardrail.py

### 🤖 Assistant

> 🔧 called: read_file

Now add the 10 new blocked tests (5 sentences × 2 audiences). I'll insert them right after the existing mixed-vouching-and-teaching tests:

> 🔧 **read_file** — test_own_words_mixed_vouching_and_teaching_student test location and line number

### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:154
-------
    def test_own_words_declarative_their(self):
        _blocked("The explanation is coherent and in their own words.")
=======
    # Tightening round — mid-sentence verbs / trailing commas/colons must not exempt

    def test_own_words_trailing_comma_coherent(self):
        _blocked("The explanation is coherent and in their own words, which shows understanding.")

    def test_own_words_trailing_comma_coherent_student(self):
        _blocked(
            "The explanation is coherent and in their own words, which shows understanding.",
            audience="student",
        )

    def test_own_words_trailing_comma_student_response(self):
        _blocked(
            "The response is clear and written in the student's own words, with good structure."
        )

    def test_own_words_trailing_comma_student_response_student(self):
        _blocked(
            "The response is clear and written in the student's own words, with good structure.",
            audience="student",
        )

    def test_own_words_midsentence_tell(self):
        _blocked("I can tell this is in your own words.")

    def test_own_words_midsentence_tell_student(self):
        _blocked("I can tell this is in your own words.", audience="student")

    def test_own_words_midsentence_elaborate(self):
        _blocked("The student gave an elaborate answer in their own words.")

    def test_own_words_midsentence_elaborate_student(self):
        _blocked("The student gave an elaborate answer in their own words.", audience="student")

    def test_own_words_trailing_colon(self):
        _blocked(
            "Overall the reasoning is coherent and in their own words:"
            " it goes beyond definitions."
        )

    def test_own_words_trailing_colon_student(self):
        _blocked(
            "Overall the reasoning is coherent and in their own words:"
            " it goes beyond definitions.",
            audience="student",
        )

    def test_own_words_declarative_their(self):
        _blocked("The explanation is coherent and in their own words.")
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: execute_command

Now let me mentally trace the tricky cases before running:

**Must-be-blocked with new pattern:**
- `"I can tell this is in your own words."` — `_OWN_WORDS_ANY` matches "in your own words". Sentence = full text. (a): starts with "I", not a request verb → no. (b): doesn't start with "In your own words," → no. (c): no "can/could/would you" before "in your own words" → no. → BLOCKED ✓
- `"The student gave an elaborate answer in their own words."` — (a): starts with "The" → no. (b): no. (c): no "you". → BLOCKED ✓
- `"...in their own words, which shows understanding."` — trailing comma. (a): starts with "The" → no. (b): no. (c): no "you". → BLOCKED ✓
- `"...in the student's own words, with good structure."` — (a): starts with "The" → no. (b): no. (c): no "you". → BLOCKED ✓
- `"...in their own words: it goes beyond definitions."` — trailing colon. (a): starts with "Overall" → no. (b): no. (c): no "you". → BLOCKED ✓

**Must-be-allowed with new pattern:**
- `"In your own words, how would you explain the meaning of..."` — (b): starts with "In your own words," ✓
- `"In your own words, can you walk through..."` — (b): starts with "In your own words," ✓  
- `"Please elaborate in your own words on how..."` — (a): starts with "Please elaborate" → `\A[\s...]*(?:please\s+)?elaborate\b.*\bin\s+your\s+own\s+words\b` ✓
- `"In your own words, what does it mean to reject..."` — (b): starts with "In your own words," ✓
- `"Tell me in your own words why the sample size matters."` — (a): starts with "Tell me" → `\A...\s*tell\s+(?:me|us)\b.*\bin\s+your\s+own\s+words\b` ✓
- `"Can you explain, in your own words, what the p-value..."` — (c): "can you" before "in your own words" ✓
- `"Ask the student to restate the definition in their own words."` — (a): starts with "Ask" ✓
- `"Explain in your own words why we reject..."` — (a): starts with "Explain" ✓

One edge case: the `re.IGNORECASE` flag is set, but branch (b) has `[Ii]n` which is redundant but harmless. More importantly, branch (b) uses `\A` which with `re.DOTALL` but **not** `re.MULTILINE` means start-of-string — which is exactly what we want since we're passing individual sentence strings.

Let me also verify the `re.compile` call builds correctly — the pattern is assembled with Python string concatenation using `+` and f-string. Let me double-check the final composed pattern doesn't have a syntax issue:

> 🔧 **execute_command** — /Users/yiwei/.venvs/viva-prep/bin/python -c "
from viva_prep.tools.guardrail import _OWN_WORDS_TEACHING, _authorship_violation
print('Pattern compiled OK')
print(_OWN_WORDS_TEACHING.pattern[:200])

# Spot-check the five must-block cases
cases_block = [
    'The explanation is coherent and in their own words, which shows understanding.',
    \"The response is clear and written in the student's own words, with good structure.\",
    'I can tell this is in your own words.',
    'The student gave an elaborate answer in their own words.',
    'Overall the reasoning is coherent and in their own words: it goes beyond definitions.',
]
for c in cases_block:
    r = _authorship_violation(c)
    print(f'BLOCK={r!s:5}  {c[:70]}')

# Spot-check must-allow cases
cases_allow = [
    'In your own words, how would you explain the meaning of the p\u2011value definition you provided?',
    'In your own words, can you walk through how the 4.1\u2011point difference might be practically important for students?',
    'Please elaborate in your own words on how you would communicate the findings to a non-specialist audience?',
    'In your own words, what does it mean to reject the null hypothesis?',
    'Tell me in your own words why the sample size matters.',
    'Can you explain, in your own words, what the p-value of 0.03 means?',
    'Ask the student to restate the definition in their own words.',
    'Explain in your own words why we reject the null hypothesis.',
]
for c in cases_allow:
    r = _authorship_violation(c)
    print(f'BLOCK={r!s:5}  {c[:70]}')
"


### 🤖 Assistant

> 🔧 called: execute_command

All 5 must-block cases are `True` and all 8 must-allow cases are `False`. Now run the full test suite:

> 🔧 **execute_command** — /Users/yiwei/.venvs/viva-prep/bin/pytest -q && git status --short && git diff --stat

### 🤖 Assistant

385 passed, 2 skipped (same pre-existing skips). Here's a summary of the changes:

---

### Root cause

The old `_OWN_WORDS_TEACHING` matched verbs and comma/colon punctuation anywhere inside a sentence. That meant:
- `"I can **tell** this is in your own words."` → "tell" mid-sentence triggered the verb branch
- `"**elaborate** answer in their own words."` → "elaborate" mid-sentence triggered the verb branch  
- `"…own words**,** which shows…"` / `"…own words**:** it goes…"` → the comma/colon after "own words" triggered the leading-punctuation branch, regardless of sentence position

### Fix in [`viva_prep/tools/guardrail.py`](viva_prep/tools/guardrail.py)

`_OWN_WORDS_TEACHING` is now anchored to `\A` (sentence start) for conditions (a) and (b), exactly matching the three conditions in the spec:

| Branch | Condition | Example that passes |
|--------|-----------|---------------------|
| **(a)** `\A…(please\s+)?<verb>\b.*\bin…own\s+words\b` | Sentence starts with a request verb | `"Explain in your own words…"`, `"Please elaborate in your own words…"`, `"Tell me in your own words…"`, `"Ask the student…in their own words."` |
| **(b)** `\A…[Ii]n\s+your\s+own\s+words\s*,` | Sentence starts with **"In your own words,"** (2nd-person only) | `"In your own words, how would you explain…"`, `"In your own words, what does it mean…"` |
| **(c)** `\b(can\|could\|would)\s+you\b.*?\bin…own\s+words\b` | Interrogative "can/could/would you" before the phrase | `"Can you explain, in your own words, what…"` |

### Tests added in [`tests/test_guardrail.py`](tests/test_guardrail.py)

10 new blocked tests (5 sentences × 2 audiences): trailing-comma vouching, trailing-colon vouching, mid-sentence "tell", mid-sentence "elaborate", and the student's-own-words-with-structure sentence.