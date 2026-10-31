# Round 1 review (run_20261031T213144Z)

Model `openai/gpt-oss-120b` on watsonx.ai (us-south), 18 students, 18 ok, 0 needs_attention, 12.5 minutes.
Evaluation: `eval_20261031T214421Z.csv`.

| Target | Result |
|---|---|
| Questions tied to a specific passage ≥ 90% | 97.4% (75/77) — pass |
| Planted misconception named ≥ 80% | 87.5% (21/24) — pass |
| Every briefing ≤ 250 words | 18/18 (123–178 words) — pass |
| Forbidden outputs = 0 | 0 — pass |

## Manual reading of all 18 briefings

The evaluation is rule-based, so every briefing was also read against the answer key.

- **The 21 counted detections are real.** In each one the briefing presents the student's sentence as a mistake, not as a correct point.
- **One detection the rules missed.** S12's briefing names the second misconception (M4, "failing to reject would show the methods are genuinely the same"), but it does not use the word "identical" that the M4 keyword rule needs. The rules were not changed after seeing results, so the official number stays 21/24.
- **Two real misses, both M5 (no limitations or assumptions).** S06's briefing treats a remark about policy and costs as a study limitation. S11's briefing treats "we need further evidence before recommending a universal curriculum change" as a limitation; that sentence is close to one, so this case is partly a data ambiguity.
- **No invented problems** in the three briefings for students without a planted misconception (S01, S09, S15). S01 and S09 get one minor suggestion each.
- **Class summary** names 18 students and the three main gaps (p-value meaning, statistical vs practical significance, missing limitations). Its per-criterion student counts (10 / 9 / 5) do not match a manual count of the briefings exactly; treat them as approximate.

## Problems found, to fix in round 2

1. **Authorship wording.** 10 of 18 briefings say the work is "in the student's own words" (it comes from rubric criterion 5, "Clear reasoning in own words"). That is a statement about who wrote the work, which the shared rules forbid in either direction. `check_output` did not block it.
2. **Rubric verdicts.** S01's briefing says the student "meets criterion 1" … "meeting criterion 5"; one S14 finding says "satisfying the clarity criterion". These are pass/fail statements on rubric criteria.
3. **Limitations.** Criterion 4 is about limitations and assumptions of this study. Two briefings accepted general remarks instead.
