# Round 2 review (run_20261031T220129Z)

Model `openai/gpt-oss-120b` on watsonx.ai (us-south), 18 students, 18 ok, 0 needs_attention, 22.9 minutes (round 1: 12.5 minutes; the cause of the difference was not investigated).
Evaluation: `eval_20261031T222426Z.csv`.

## What changed from round 1

Made in Bob task 10 (`bob_sessions/10_round2_guardrail_prompt.md`), based on `round1_review.md`:

- `check_output` (Rule 2) blocks statements that the work is in the student's own words, even as praise. Requests to answer in one's own words stay allowed.
- `check_output` (Rule 1) blocks statements that a rubric criterion is met.
- `prompts/briefing_writer.md`:
  - New rule: never say whether the wording is the student's own, original or genuine, and never say whether a criterion is met.
  - Criterion 4 is defined as limitations or assumptions of this particular study.
  - Findings quote "the submission" instead of "their own words".
  - Known deviation: the word "verbatim" after `evidence_quote` was dropped while shortening the file.

`question_planner`, the other prompts, the data and both scripts were not changed.

## Targets

| Target | Round 1 | Round 2 |
|---|---|---|
| Questions tied to a specific passage ≥ 90% | 97.4% (75/77) | 92.1% (70/76) — pass |
| Planted misconception named ≥ 80% | 87.5% (21/24) | 87.5% (21/24) — pass |
| Every briefing ≤ 250 words | 18/18 (123–178) | 18/18 (101–201) — pass |
| Forbidden outputs = 0 | 0 | 0 — pass |

"Forbidden outputs" is `check_output` run on the briefing text by `evaluate.py`, using the guardrail as it stood when each evaluation ran.

## Effect of the guardrail change

The round-1 outputs were checked again with the round-2 guardrail, so the guardrail effect and the prompt effect can be told apart.

| Outputs | Briefings blocked | Student questions blocked | Finding claims blocked |
|---|---|---|---|
| Round 1, round-1 guardrail | 0/18 | 0/77 | 0/94 |
| Round 1, round-2 guardrail | 10/18 | 0/77 | 6/94 |
| Round 1, after the guardrail fix below | 10/18 | 0/77 | 6/94 |
| Round 2, round-2 guardrail | 0/18 | 3/76 | 0/95 |
| Round 2, after the guardrail fix below | 0/18 | 0/76 | 0/95 |

Two of these checks are outside the official count:

- `run_batch.py` and `evaluate.py` check only the briefing text, so the student-question and finding-claim columns come from a separate check of the stored outputs.
- In Orchestrate, each agent checks its own output before showing it.

## Guardrail fix after round 2 (no new model run)

The round-2 authorship rule blocked three of the 76 student questions (S09, S14, S17). All three ask the student to answer in their own words, for example "In your own words, how would you explain …". The round-2 task said this kind of request must stay allowed, so this was a defect against the agreed rule, not new tuning.

Bob task 11 (`bob_sessions/11_guardrail_own_words_fix.md`) fixed it:

- Each sentence that mentions "own words" is now checked on its own. Before, one teaching sentence anywhere in a text let a vouching sentence elsewhere through.
- Such a sentence counts as a teaching request only if:
  - it starts with a request verb ("Explain …", "Please elaborate …", "Ask the student …");
  - it starts with "In your own words,"; or
  - it asks "can/could/would you … in your own words".
- Tests were added for the three round-2 questions and for vouching sentences that must stay blocked. Five of those vouching sentences passed Bob's first version and were caught in review.
- 385 tests pass.

The fix was made after seeing the round-2 outputs and was measured on the same 18 students. It changed no model output; it only changes which stored outputs `check_output` lets through (table above).

## Manual reading of all 18 briefings

The evaluation is rule-based, so every briefing was also read against the answer key.

- **Authorship wording is gone.**
  - Round 1: 10 of 18 briefings said the work was in the student's own words.
  - Round 2: none do. The two regular-expression hits (S04, S12, "genuinely") are inside quotations of the student's own mistaken sentence.
- **Rubric verdicts.**
  - No briefing says a criterion "is met".
  - Three come close without being blocked:
    - S15 labels each paragraph "(criterion N, high confidence)";
    - S11 says a remark "aligns with the assumptions/limitations criterion";
    - S06 says a limitation "is required for criterion 4".
- **Misconceptions: 21 counted, 22 found on reading.**
  - S18's briefing names M3 ("statistical significance means the effect is real and practically important"). The M3 keyword rule needs the word "significant", and the briefing only says "significance". This is the same kind of rule miss as S12 in round 1. The rules were not changed after seeing results, so the official number stays 21/24.
- **Limitations (criterion 4): partly fixed.**
  - S06 is now flagged correctly ("does not identify any specific limitation or assumption").
  - S11 and S13 accept a recommendation to replicate the study as a limitation. S13 was flagged correctly in round 1.
  - Both submissions do contain such a sentence, so these two cases are partly an answer-key ambiguity.
- **Grounding dropped from 97.4% to 92.1%.**
  - S09's four questions all fail the rule (round 1: 4/4). On reading, they refer to real passages (the 4.1-point difference, the normality check, the single-course limitation, the p-value definition) but paraphrase them instead of quoting.
  - S10's one miss quotes the submission correctly. The rule ignores digits, so "p = 0.03 proves beyond reasonable doubt" is too short to match.
  - `question_planner` was not changed, so the cause of the drop is not established.
- **One invented quote.**
  - S06's fourth question asks about "the study was conducted in one course". S06's submission never says this, and it does not mention the course setting at all.
  - It attributes words to the student that they did not write. It also contradicts S06's own briefing, which says no limitation was given.
  - Nothing in the current tools checks a quotation against the submission.
- **Evidence quotes: 6 of 93 are not word for word (round 1: 5 of 94).**
  - S04 joins two passages and leaves out the sentence between them without marking the gap.
  - S17 shortens two phrases ("verify exam instrument", "grading blind to condition").
  - S06, S12, S15 and S18 change one to three words at the start, for example "p = 0.03" for "of 0.03" and "statistical significance" for "statistically significant".
  - The likely cause is that "verbatim" was dropped from the briefing writer's instructions. Two absence notes in square brackets (S05, S14) are not quotes and were not counted.
- **No invented problems** in the three briefings for students without a planted misconception (S01, S09, S15). S01 gets one minor suggestion, S09 two, S15 two.
- **Required opening sentence missing in 2 of 18.** S15 and S18 do not start with "Based on the submission only (no practice conversation)." Round 1: 18/18 had it.
- **Class summary** (173 words; round 1: 120) has the following problems:
  - Its per-criterion counts (7 / 7 / 4 / 5) are approximate.
  - Like round 1, it does not mention the "failing to reject means the methods are identical" mistake, which appears in four students (S05, S10, S12, S16).
  - Its criterion 5 bullet describes missing effect-size numbers, which is not what criterion 5 (clear reasoning) is about.

## Not fixed (the plan allows two prompt rounds)

1. **Invented quotes in student questions (S06).** This is the most serious remaining problem, because the student sees the question. A tool that checks every quotation against the submission before the question is shown would catch it.
2. **Limitations judgement (S11, S13).** Replication suggestions are still accepted as limitations.
3. **Near-verdict wording (S15, S11, S06)** that the guardrail does not catch.
4. **Evidence quotes** that are not word for word (6 of 93).
5. **The opening sentence** is missing in 2 briefings, and the **class summary** misses one common mistake.
