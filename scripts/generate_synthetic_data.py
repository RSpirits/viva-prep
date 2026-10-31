"""
Generate synthetic course materials and student submissions for
STAT 110 – Introduction to Statistics.

Standard-library only. Fixed random seed (42) for reproducibility.

Output layout
─────────────
data/course/
  syllabus.md
  rubric.md
  learning_objectives.md
  lecture_notes_hypothesis_testing.md

data/submissions/
  S01.md … S18.md

data/answer_key/
  answer_key.json
"""

import json
import os
import random

SEED = 42

# ---------------------------------------------------------------------------
# Course materials
# ---------------------------------------------------------------------------

SYLLABUS_MD = """\
# STAT 110 – Introduction to Statistics
## Course Syllabus

| Week | Topic |
|------|-------|
| 1 | Descriptive statistics: measures of centre and spread |
| 2 | Probability fundamentals and random variables |
| 3 | Sampling distributions and the Central Limit Theorem |
| 4 | Confidence intervals for means and proportions |
| 5 | Introduction to hypothesis testing: concepts and procedure |
| 6 | Hypothesis testing in practice: two-sample tests and interpretation |

### Assignment schedule
- Assignment 1 (Week 2): Probability problems
- Assignment 2 (Week 3): Sampling distributions
- Assignment 3 (Week 4): Confidence intervals
- **Assignment 4 (Week 6): Interpreting a hypothesis test**
"""

RUBRIC_MD = """\
# Assignment 4: Interpreting a Hypothesis Test
## Grading Rubric

### Task description
Students are given the following study summary and asked to write **250–400 words**
explaining what the result means:

> A researcher compared two study methods (Method A and Method B) in a college
> statistics course. Forty students were randomly assigned to each method (n = 40
> per group). At the end of the semester, the mean exam score for Method A was
> 4.1 points higher than for Method B. An independent-samples t-test yielded
> p = 0.03.

---

### Criteria (20 points total)

| # | Criterion | Points |
|---|-----------|--------|
| 1 | **Correct meaning of the p-value** – explains that p = 0.03 is the probability of observing a difference at least this large *if the null hypothesis were true*, not the probability that the null hypothesis is true | 4 |
| 2 | **Correct conclusion about the null hypothesis** – rejects H₀ at α = 0.05; does not claim the null is "proven false" or "proven true" | 4 |
| 3 | **Statistical vs. practical significance** – acknowledges that statistical significance does not by itself imply the difference is large, meaningful, or educationally important | 4 |
| 4 | **Assumptions and limitations** – mentions at least one relevant limitation (e.g. random assignment scope, generalisability, effect size, or confounders) | 4 |
| 5 | **Clear reasoning in own words** – explanation is coherent and the student demonstrates genuine understanding rather than restating definitions | 4 |

**Total: 20 points**
"""

LEARNING_OBJECTIVES_MD = """\
# STAT 110 – Learning Objectives

By the end of Week 6 students will be able to:

1. **Define the p-value correctly** – state that the p-value is the probability of
   obtaining a test statistic at least as extreme as the one observed, *given that
   the null hypothesis is true*, and avoid the common error of treating it as the
   probability that the null hypothesis is true.

2. **Reach and communicate a decision about the null hypothesis** – compare the
   p-value to a pre-specified significance level (α), reject or fail to reject H₀,
   and explain what that decision does and does not imply.

3. **Distinguish statistical significance from practical significance** – recognise
   that a statistically significant result may have a small effect size and may not
   be practically meaningful, and vice versa.

4. **Identify key assumptions and limitations of a two-sample t-test** – list
   conditions required for the test (approximate normality or large n, independence,
   equal or unequal variances) and articulate at least one limitation that affects
   how broadly the conclusion can be applied.

5. **Communicate statistical reasoning in plain language** – translate technical
   output (test statistic, p-value, confidence interval) into clear, accurate
   prose that a non-specialist could understand.
"""

LECTURE_NOTES_MD = """\
# Lecture Notes – Hypothesis Testing (Week 6)

## 1. What is a hypothesis test?

A hypothesis test is a formal procedure for deciding whether sample data provide
enough evidence to reject a default assumption about a population. That default
assumption is called the **null hypothesis (H₀)**. The competing claim is the
**alternative hypothesis (H₁ or Hₐ)**.

For a two-sample comparison of means the hypotheses are usually:

- H₀: μ₁ − μ₂ = 0 (the two population means are equal)
- Hₐ: μ₁ − μ₂ ≠ 0 (they differ; two-tailed) or a one-directional version

## 2. The p-value – what it is and what it is not

The **p-value** is the probability of observing a test statistic at least as extreme
as the one computed from the sample, *under the assumption that H₀ is true*.

A small p-value means the observed data would be surprising if H₀ were true, which
provides evidence *against* H₀.

**Common misconception:** The p-value is *not* the probability that H₀ is true.
That quantity is a posterior probability and requires a Bayesian framework with a
prior. The p-value lives entirely in a frequentist world where H₀ is either true or
false – it has no probability of its own.

## 3. Making a decision

We compare p to a pre-specified **significance level α** (commonly 0.05):

| Result | Decision |
|--------|----------|
| p ≤ α | Reject H₀; the result is *statistically significant* at level α |
| p > α | Fail to reject H₀; insufficient evidence to conclude H₀ is false |

Failing to reject H₀ does **not** prove the null is true. It means the data did not
provide sufficient evidence to overturn it. The two populations could still differ –
we simply lacked the power to detect it.

## 4. Statistical significance vs. practical significance

A result can be statistically significant yet practically unimportant. With large
enough sample sizes, even a trivially small difference will produce p < 0.05.
Conversely, a meaningful difference may go undetected in a small study.

To judge practical significance we use **effect sizes** (e.g. Cohen's d) or
**confidence intervals** for the difference, which show the plausible range of the
true effect. A 4-point difference on a 100-point exam might be educationally
meaningful – or not – depending on context.

## 5. Assumptions of the independent-samples t-test

1. **Independence** – observations within and between groups are independent.
2. **Approximate normality (or large n)** – each group's data come from a roughly
   normal distribution, or n is large enough for the Central Limit Theorem to apply
   (n ≥ 30 is a common rule of thumb).
3. **Homogeneity of variance** (for Student's t; relaxed in Welch's t-test) – the
   two populations have similar variances.

If any assumption is violated, the p-value may be inaccurate and the conclusion
should be stated with appropriate caution.

## 6. Putting it together: an example

Suppose a study finds p = 0.03 for a two-sample t-test comparing exam scores under
two study methods (n = 40 per group, mean difference = 4.1 points).

- We **reject H₀** at α = 0.05 because 0.03 < 0.05.
- We conclude there is statistically significant evidence that the two methods
  produce different mean scores in the study population.
- We **cannot** conclude that Method A *proves* better for all students everywhere –
  the study was conducted in one course, and we should consider effect size and
  generalisability before making policy decisions.
- The 4.1-point difference may or may not be educationally important; that is a
  separate question from whether it is statistically detectable.
"""

# ---------------------------------------------------------------------------
# Student data and submission templates
# ---------------------------------------------------------------------------

NAMES = [
    "Amara", "Ben", "Chloe", "Diego", "Elena",
    "Felix", "Grace", "Hiro", "Imani", "Jordan",
    "Kai", "Leila", "Marcus", "Nina", "Omar",
    "Priya", "Quinn", "Rosa",
]

# Each misconception key maps to a short label for reference
MISCONCEPTIONS = {
    "M1": "The p-value is the probability that the null hypothesis is true.",
    "M2": "p = 0.03 proves the new study method works.",
    "M3": "Statistically significant means the difference is large or important.",
    "M4": "Failing to reject would mean the two methods are exactly the same.",
    "M5": "no assumptions or limitations mentioned at all",
    "M6": "correct terms used, but the explanation contradicts itself between two paragraphs",
}

# ---------------------------------------------------------------------------
# Submissions
# Each answer is written in a natural student voice and is 250–400 words
# (body only, not counting the YAML header).
# Planted misconception sentences are unique per student and appear verbatim
# in EVIDENCE_SENTENCES below.
# ---------------------------------------------------------------------------

SUBMISSIONS = [
    # ── S01 – no misconceptions ─────────────────────────────────────────────
    (
        "S01", "Amara", [],
        """\
The study compared two study methods using an independent-samples t-test, and the result
was p = 0.03 with a mean score difference of 4.1 points. I want to explain what this
actually tells us, because I think a lot of people misread p-values.

The p-value of 0.03 tells us that, assuming the null hypothesis is true — that the two
methods produce the same average exam score — there would be only a 3% chance of
observing a difference at least as large as 4.1 points just by random chance. Because
0.03 is less than the conventional significance level of 0.05, we reject the null
hypothesis. That is a specific, careful statement: the data provide enough evidence to
conclude the methods likely produce different average scores. It does not mean we have
discovered a universal truth or that every student will benefit equally.

Now, statistical significance is not the same as practical significance. A 4.1-point
difference on an exam sounds meaningful, but we need to consider the scale. If the exam
is out of 100 points, 4.1 points is modest. We would want to look at an effect size,
like Cohen's d, or a confidence interval for the true difference to judge whether the
result is educationally important. Statistical significance just tells us the difference
probably did not arise from sampling variation alone; it does not tell us whether the
difference is large enough to matter in classrooms or curricula.

There are also real limitations here. The study used 40 students per group, which is
reasonable but not large. We need to ask whether the students were randomly selected from
a broader population, or just drawn from one class. If it was one class, we cannot
automatically generalise to other institutions, subjects, or student demographics. We also
need to trust that random assignment to methods was properly done, so that confounding
variables such as prior knowledge and study habits are controlled.

In summary, the result is statistically significant and gives us reason to investigate
Method A further, but it does not prove Method A is universally superior, and the
4.1-point difference may or may not matter in practice depending on the educational
context. Replication across multiple settings would be needed before any policy change.""",
    ),

    # ── S02 – M1 ────────────────────────────────────────────────────────────
    (
        "S02", "Ben", ["M1"],
        """\
When I first read the study summary I thought the p-value would be straightforward to
explain, but after working through the lecture notes I realise there is more nuance than
I expected. Let me walk through the result carefully.

The p-value here is 0.03. To me, this number represents how likely it is that the null
hypothesis is correct: a p-value of 0.03 is the chance that the null hypothesis is true,
so there is only a 3% probability it is right. Because that is well below our 0.05
threshold, we reject the null and conclude that Method A really does lead to higher
average scores than Method B. The smaller the p-value, the more confident we can be that
the null is wrong.

The mean difference of 4.1 points adds more context. We need to ask whether a 4.1-point
improvement is meaningful in the real world. The lectures covered the idea that statistical
significance and practical significance are separate things. Even if the result passes the
significance test, a 4.1-point bump may not actually change how much students learn in any
meaningful way, depending on the overall exam scale and what teachers are trying to achieve.
On a 60-point exam, 4.1 points is a larger fraction than on a 200-point exam, so context
matters a great deal.

One limitation I can see is that the study only involved 40 students per group. That is not
a very large sample, and if the students were all from the same institution or even the same
class, we cannot be sure the finding generalises. Different types of students, different
instructors, and different course content could all affect whether Method A continues to
outperform Method B. Future studies should sample from multiple institutions and course types
to get a more reliable picture.

Overall, the study provides interesting evidence that the two methods produce different
average scores, but there is still a lot we do not know before recommending a policy change.
The 4.1-point advantage deserves further investigation rather than immediate adoption.""",
    ),

    # ── S03 – M2 ────────────────────────────────────────────────────────────
    (
        "S03", "Chloe", ["M2"],
        """\
This assignment asked us to interpret the results of a hypothesis test comparing two study
methods. I will go through the key parts of the result step by step.

First, what does p = 0.03 mean? The p-value measures how surprising the data would be if
the null hypothesis were true. A p-value of 0.03 means there is only a 3% chance of seeing
a difference this large by chance if there were really no effect. Because this is below 0.05,
we reject the null hypothesis. This is the standard frequentist conclusion: the data are
inconsistent enough with the null that we feel confident dismissing it.

Now, does this mean Method A is definitely better? There is no ambiguity: getting p = 0.03 proves conclusively that the new study method works and that the difference we observed is real. The evidence is strong enough that educators can act on it. The significance level was precisely chosen to filter out results that could plausibly be noise, and this one clears that bar.

We should still think about practical significance. A 4.1-point difference might be
meaningful in some contexts and minor in others. If a course uses a 200-point exam, 4.1 is
a small fraction. If the exam is out of 50, it is quite large. Effect size measures like
Cohen's d would help put the number in perspective and tell us whether the difference is
large enough to matter educationally.

Regarding limitations, the study enrolled 40 students per group, which satisfies the common
n ≥ 30 rule for the Central Limit Theorem. Still, generalising to all students everywhere
requires caution. The specific course, instructor quality, and student background could all
influence the result. Future research should replicate the study across multiple institutions
and course types before any definitive recommendations are made. The t-test also assumes
independence and approximate normality, which are plausible here but worth verifying.""",
    ),

    # ── S04 – M3 ────────────────────────────────────────────────────────────
    (
        "S04", "Diego", ["M3"],
        """\
A hypothesis test is a tool for deciding whether observed data are consistent with a null
assumption. In this study, the null hypothesis is that there is no difference in mean exam
scores between Method A and Method B. The alternative is that there is a difference, and
the independent-samples t-test was the right choice here because the two groups are separate
and we are comparing means.

With p = 0.03, we reject the null at the conventional α = 0.05 significance level.
A result being statistically significant implies the difference is genuinely large and practically important, so this 4.1-point advantage for Method A is not just noise — it reflects a substantial effect that instructors and curriculum designers should take seriously and act on.

The p-value itself represents the probability of observing a difference at least this extreme
if the null were true. At 3%, that probability is low enough to cast serious doubt on the null,
which is why we reject it. This is a frequentist decision procedure, not a guarantee of truth,
and we should remember that about 5% of correct null hypotheses would be rejected just by
chance at this significance level.

There are, of course, limitations. The sample size is 40 per group. While this is adequate
for the Central Limit Theorem to apply, it is not a very large study. The results may not
transfer to other courses, other populations of students, or other instructors. The study
also presumably took place in a specific academic environment, which may not mirror all
possible settings. Possible confounders include instructor enthusiasm and prior student
knowledge, both of which could differ between groups even with random assignment in a
relatively small sample.

In practice, before changing curricula I would want to see the confidence interval for the
difference and at least one independent replication. A 4.1-point difference could matter a
lot for students on grade boundaries, but we need more evidence before scaling up.""",
    ),

    # ── S05 – M4 ────────────────────────────────────────────────────────────
    (
        "S05", "Elena", ["M4"],
        """\
Hypothesis testing is something I found confusing at first, but working through this example
helped clarify my thinking. Let me walk through the study results carefully and explain what
each part of the output means.

The null hypothesis here is that the two study methods produce the same mean exam score.
With p = 0.03 and α = 0.05, we reject the null hypothesis because the p-value falls below the
threshold. This means we have statistically significant evidence that the two methods do not
produce equal population means. It is important to note that we are not proving Method A is
universally better; we are saying the data are incompatible with there being no difference.

It is worth thinking about what would have happened if we had not rejected. If p had been,
say, 0.15, we would fail to reject the null hypothesis. A failure to reject the null would mean the two methods are identical in their effects, so we could comfortably ignore any observed difference in scores and would have no reason to prefer one method over the other in any situation.

Back to the actual result: the 4.1-point difference is our observed effect size in raw units.
Whether this is practically meaningful depends on context. A 4.1-point edge on a 100-point
exam is not enormous, and I would want to see a standardised effect size or confidence
interval before recommending a policy change. We should not assume statistical significance
automatically implies practical importance.

The study also has limitations. Random assignment within the study is good for internal
validity, but the study was run in a single course with 40 students per group. Generalising
to other institutions, subject areas, and student demographics requires more evidence. We
should also ask whether the exam used to measure performance was the same across both groups
and whether scoring was blinded to condition to avoid bias from the graders.""",
    ),

    # ── S06 – M5 (no assumptions/limitations) ───────────────────────────────
    (
        "S06", "Felix", ["M5"],
        """\
The study compared Method A and Method B using a two-sample t-test. The null hypothesis was
that the two methods produce the same average score on a final exam. Because p = 0.03 is
less than 0.05, we reject the null hypothesis and conclude that the difference in average
scores — 4.1 points — is statistically significant.

The p-value of 0.03 represents the probability of observing a difference this large or
larger purely by chance, assuming no true difference exists between the methods. It is not
the probability that the null hypothesis is true; that is a frequent mistake that conflates
two very different quantities. The correct interpretation keeps the null hypothesis fixed
and asks how surprising our data would be in that world.

Regarding practical significance: finding a statistically significant result does not
automatically mean the difference is educationally important. A 4.1-point difference could
matter for students near a grade boundary, or it could be negligible if the course uses
partial credit generously and the total scale is very large. The statistical test tells us
the result is unlikely to be random noise, but it cannot tell us whether teachers should
change their methods based on this number alone. Effect size measures such as Cohen's d
or a confidence interval around the difference would help answer that separate question.

Policy decisions about teaching methods should weigh multiple factors beyond the statistical
result. Cost, feasibility, student engagement, and instructor training all play a role. A
4.1-point average improvement is an encouraging signal, but it should be the starting point
for a broader conversation rather than an immediate mandate to switch all students to
Method A.

Overall, the study provides evidence that Method A leads to higher exam scores on average.
The effect is statistically detectable, but whether it rises to the level of educational
significance is a judgment call that goes beyond the numbers themselves.""",
    ),

    # ── S07 – M1, M3 ────────────────────────────────────────────────────────
    (
        "S07", "Grace", ["M1", "M3"],
        """\
I found this assignment interesting because I had never really thought carefully about what
p-values mean before. Here is my interpretation of the study, covering the test result, what
significance means, and the broader context.

The p-value is 0.03. In my understanding, the p-value gives you the probability that the null hypothesis itself is true, so a value of 0.03 means there is only a 3 in 100 chance the null is correct. Since that probability is very small, we reject the null hypothesis and accept the
alternative — that Method A produces higher exam scores than Method B.

Something that strikes me is how we should interpret "significant." When a test comes back
significant, it tells you the difference is real and important, not just a statistical blip. Being statistically significant is the same as saying the result matters and the effect is meaningfully large. With a difference of 4.1 points, we are looking at a gap that instructors and policymakers should pay close attention to. The threshold of 0.05 was chosen to filter out trivial noise, so clearing it means the finding has genuine importance.

The n = 40 per group satisfies the standard requirements for the t-test. The Central Limit
Theorem tells us the sampling distribution of the mean will be approximately normal at this
sample size, so the statistical assumptions for the test are satisfied. This gives me
confidence in the result.

One limitation I will mention is that the study was conducted in a single course. Whether
the same advantage for Method A would appear in different disciplines, with different student
populations, or with different instructors is genuinely an open question. Replication in
diverse settings is needed before implementing Method A as a universal recommendation. There
is also the question of long-term retention: did Method A produce durable learning or just
short-term exam performance?""",
    ),

    # ── S08 – M6 ────────────────────────────────────────────────────────────
    (
        "S08", "Hiro", ["M6"],
        """\
Hypothesis testing allows researchers to make principled decisions about population
parameters based on sample data. In the study described, an independent-samples t-test
was used to compare mean exam scores under Method A and Method B, with 40 students
randomly assigned to each condition.

The p-value of 0.03 is the probability of observing a difference at least as large as
4.1 points if the null hypothesis were true. Since 0.03 < 0.05, we reject the null and
conclude that Method A likely produces higher average scores. This decision is made at the
5% significance level, meaning we accept a 5% chance of rejecting a true null hypothesis.

However, we must be careful not to overinterpret this result. A statistically significant
finding does not guarantee the difference is large or important in practice. The 4.1-point
difference might be modest depending on the exam's total points, and we should examine
effect size and confidence intervals before drawing strong conclusions about educational
relevance. Statistical significance is a statement about sampling variability, not about
the size of the effect.

Crucially though, when a result achieves statistical significance, it means the observed difference is guaranteed to be real and educationally important, because the significance threshold is designed to allow only genuine and substantial effects through. So any p-value below 0.05 automatically signals that practitioners should act on the result without further consideration of effect size.

Turning to assumptions: the t-test requires independence and approximate normality (or
large n). With n = 40, the Central Limit Theorem supports normality. Independence is
plausible if students were randomly assigned. One limitation is that the study may not
generalise beyond the specific course context, and future research should test the finding
in a broader range of institutions and student populations.""",
    ),

    # ── S09 – no misconceptions ─────────────────────────────────────────────
    (
        "S09", "Imani", [],
        """\
The study used an independent-samples t-test to determine whether two study methods led
to different mean exam scores. Students were randomly assigned to one of the two methods,
with 40 in each group. The mean score for Method A was 4.1 points higher, and the test
yielded p = 0.03.

Because the p-value (0.03) is less than the standard significance level of 0.05, we reject
the null hypothesis. The null hypothesis stated that the two methods produce the same
population mean score. Rejecting it means the data give us sufficient evidence to conclude
the methods differ on average. Notice that this is a probabilistic statement: we could
still be wrong. In roughly 5% of studies where H₀ is true, we would get a result at least
this extreme — this is what the significance level controls for.

The p-value is defined as the probability of obtaining a test statistic at least as extreme
as the observed one, given that H₀ is true. It is not the probability that the null
hypothesis is true, which would require a Bayesian framework and a prior probability.
Confusing the two is one of the most common errors in interpreting statistical tests.

A 4.1-point difference may or may not be educationally meaningful. We would need to know
the exam scale and consider a standardised effect size to judge practical significance.
Statistical significance only tells us the result is unlikely due to chance, not that the
difference is large or important in any absolute sense.

Key limitations: the study was conducted in a single course. Generalisability to other
institutions, subjects, or student demographics is uncertain. Confounding variables could
include teaching style differences, student motivation, prior preparation, and time
available for studying outside of class. The t-test also assumes independence and
approximate normality, which are plausible given n = 40 but should be checked.""",
    ),

    # ── S10 – M2, M4 ────────────────────────────────────────────────────────
    (
        "S10", "Jordan", ["M2", "M4"],
        """\
Interpreting hypothesis test results can be tricky, but I will do my best to explain what
the study found and what it means for educational practice.

The two-sample t-test produced p = 0.03, which is below the standard α = 0.05 threshold.
We therefore reject the null hypothesis. Obtaining p = 0.03 proves beyond reasonable doubt that the new method works and is effective; the data are decisive, and the probability of seeing this result by chance is only 3%. Instructors should feel confident adopting Method A
based on this evidence alone.

Now suppose the outcome had been different and p > 0.05. If the p-value had not been
significant, failing to reject the null would prove the two methods are completely identical and interchangeable. There would be no reason to prefer one over the other, and any observed score difference would be entirely attributable to random sampling variation.

The 4.1-point difference deserves attention regardless. On a 100-point exam, 4.1 is
noticeable but not dramatic. We should be careful not to assume statistical significance
automatically implies the gap is big enough to change educational practice. Effect size
measures and a confidence interval would help us judge whether this difference is
educationally meaningful before committing to a curriculum overhaul.

There are some assumptions behind the t-test: the two groups should be independent, and the
data should come from roughly normal distributions (or the samples should be large enough
for the Central Limit Theorem to apply). With n = 40 per group, the CLT assumption holds.
There is also the question of whether only one class was involved, which would limit how
broadly we can generalise the findings. Students in one course may differ systematically
from those in other institutions or disciplines.""",
    ),

    # ── S11 – M1, M5 ────────────────────────────────────────────────────────
    (
        "S11", "Kai", ["M1", "M5"],
        """\
In this study, 80 students were split equally between two study methods and their exam
scores were compared using an independent-samples t-test. The result was a mean difference
of 4.1 points in favour of Method A and a p-value of 0.03.

What does the p-value mean? As I understand it, the p-value is essentially the probability that the null hypothesis is true given the data we observed. With p = 0.03, there is only a 3% chance the null hypothesis holds, which is low enough to reject it at the conventional 5% level. This means we can be 97% confident that the null hypothesis is wrong and that the two methods truly do produce different average exam scores.

Statistical significance must be distinguished from practical significance. A 4.1-point
difference is statistically detectable, but whether it matters educationally depends on
scale and context. A 4.1-point improvement on a 60-point exam is a much larger proportional
gain than the same improvement on a 200-point exam. Without knowing the scale and the
distribution of grades, it is difficult to say whether this is a meaningful improvement for
students. We should examine an effect size measure to answer that question properly.

Method A appears to produce better exam outcomes, and while the p-value confirms this is
unlikely to be due to random chance, we need further evidence before recommending a
universal curriculum change. A replication study in multiple course settings, with diverse
student populations and different instructors, would substantially increase our confidence
in the finding. Cost and feasibility of implementing Method A should also be considered
before any institution commits to a change in teaching practice.""",
    ),

    # ── S12 – M3, M4 ────────────────────────────────────────────────────────
    (
        "S12", "Leila", ["M3", "M4"],
        """\
This study examined whether two study methods lead to different exam outcomes. The
independent-samples t-test is appropriate here because we are comparing the means of two
separate, independent groups of students.

With p = 0.03 and α = 0.05, we reject the null hypothesis. The p-value represents the
probability of observing a difference this large or larger under the assumption that there
is no true effect. Since 3% is below our threshold, the result clears the bar for
statistical significance.

What does statistical significance tell us about importance? A finding being statistically significant is the same as saying the result has a large effect size and is practically meaningful. The 4.1-point gap therefore signals a result that is both detectable by the test and important in educational terms. Method A appears to be the clearly better choice.

On the other hand, consider what would have happened if p > 0.05. If we had failed to
reject, that result would show the two methods are genuinely the same in effect, not merely statistically indistinguishable. The methods would be truly equivalent and we would have strong grounds for treating the choice between them as arbitrary.

One limitation worth noting is sample size. Forty students per group is adequate for the
t-test's normality assumption under the Central Limit Theorem, but a larger study would
give more precise estimates of the true difference and a narrower confidence interval.
Future research should also check whether the result holds in other academic settings,
with students at different preparation levels, and under different exam formats. External
validity is a concern any time a study is conducted in a single course at one institution.""",
    ),

    # ── S13 – M2, M5 ────────────────────────────────────────────────────────
    (
        "S13", "Marcus", ["M2", "M5"],
        """\
Let me walk through the hypothesis test step by step to explain what this result means.

The null hypothesis is that Methods A and B produce the same mean exam score in the
population. The alternative is that they differ. With p = 0.03, we reject the null at
the 5% significance level. The p-value is the probability of seeing a result at least
this extreme if the null were true. At just 3%, the data are quite inconsistent with the
idea of no difference.

Does this mean the new method definitively works? Yes: a p-value of 0.03 definitively proves that Method A is effective and that the study method genuinely improves student performance. The significance threshold was set precisely to distinguish real signals from noise, and this result clears it with room to spare, so there is no reason to doubt the conclusion.

A 4.1-point mean difference contributes to this picture. In practical terms, this is the
additional score students using Method A obtained on average. Whether 4.1 points is
educationally important depends on context — the scale of the exam, the distribution of
grades, and what counts as a meaningful improvement for students and instructors. We
should interpret the effect size alongside the p-value to get a complete picture of what
this result means for teaching practice. A Cohen's d or a confidence interval would help.

In summary, the hypothesis test supports the conclusion that Method A leads to higher exam
scores on average. The result is statistically significant, which tells us the observed
difference is very unlikely to be due to chance, and the magnitude of 4.1 points appears
to be practically noteworthy. Replication across multiple settings would further strengthen
the case for adopting Method A more broadly in statistics education.""",
    ),

    # ── S14 – M6, M5 ────────────────────────────────────────────────────────
    (
        "S14", "Nina", ["M6", "M5"],
        """\
Hypothesis testing gives researchers a systematic way to evaluate claims about population
parameters using sample data. Here, the parameter of interest is the difference in mean
exam scores between two study methods, and the independent-samples t-test is the right
tool for comparing them.

The p-value of 0.03 means: if the null hypothesis were true, there would be only a 3%
chance of obtaining a difference as large as 4.1 points. Since 0.03 falls below α = 0.05,
we reject the null hypothesis. We can therefore conclude that the two methods are likely
to produce different average scores in the population from which these students were drawn.

Next, we should separate statistical from practical significance. Statistical significance
only tells us the difference is unlikely to be noise. Whether 4.1 points matters in
education is a separate question requiring judgment about the exam scale and student needs.

However, it is also important to recognise that whenever a study achieves p < 0.05, the effect is automatically guaranteed to be educationally meaningful and worth implementing, because the significance threshold is specifically calibrated to let only real and important effects through. This means the caution about practical significance raised earlier does not actually apply here — the result is both statistically and practically significant by definition.

So while the statistical test provides strong quantitative evidence, educators should still
consider the wider context when making decisions. The 4.1-point difference may benefit
students near grade boundaries more than those comfortably passing. In conclusion, the
result clearly supports Method A and the evidence is strong enough to warrant further
investigation and potential adoption.""",
    ),

    # ── S15 – no misconceptions ─────────────────────────────────────────────
    (
        "S15", "Omar", [],
        """\
I will explain what p = 0.03 means and why we need to be careful about how we interpret
this study, covering the p-value, the hypothesis decision, practical significance, and
the limitations of the design.

A p-value is calculated under the null hypothesis. In this study, H₀ says both methods
produce the same average score. The p-value of 0.03 tells us: if that null were true,
the probability of randomly getting a sample difference of 4.1 points or more would be
3%. That is low, so we reject H₀ at α = 0.05. This decision is probabilistic: we are
not certain the null is false, but the data provide enough evidence to dismiss it.

Rejecting H₀ does not mean we have proved Method A is better; it means the data are
sufficiently inconsistent with the idea of no effect. There is still a 5% false positive
rate built into the α = 0.05 decision rule. We could be wrong, and that is a feature of
frequentist testing rather than a flaw in this particular study.

Practical significance is a different question from statistical significance. A 4.1-point
difference on a 100-point exam could shift a student's grade from a B to a B+, which might
matter a lot. It might also be within the noise of grading variation. We need effect size
metrics and a confidence interval to say more about whether this matters educationally.

Limitations matter here. The study was run in one course with 40 students per group.
Confounders such as student prior knowledge, time spent studying, and instructor enthusiasm
could differ across groups even with random assignment in a small sample. Wider replication
is needed across different institutions and disciplines. The t-test also assumes independence
and approximate normality, which are plausible given n = 40 but should be formally checked.""",
    ),

    # ── S16 – M1, M4 ────────────────────────────────────────────────────────
    (
        "S16", "Priya", ["M1", "M4"],
        """\
The study gave us a p-value of 0.03 from a two-sample t-test comparing exam scores under
Method A and Method B, with a mean difference of 4.1 points in favour of Method A. I want
to explain carefully what each part of this result means.

Starting with the p-value: as I see it, the p-value equals the probability that the null hypothesis is actually true, which in this case is just 3%. That is a very small probability, so we comfortably reject the null hypothesis and conclude that Method A is associated with higher exam scores on average.

Now think about the counterfactual. If the test had produced p = 0.20, we would fail to
reject the null hypothesis. Not rejecting the null would mean the two methods are definitively identical in their effects on student performance, and there would be no reason to prefer one over the other regardless of what the sample means showed. Fortunately that is not the case here.

Turning to practical significance: rejecting the null does not automatically mean the
4.1-point gap matters in practice. We need to look at the exam scale and compute an effect
size. If the exam runs to 50 points, 4.1 is substantial. If it is a 200-point exam, the
same gap is small relative to the scale. Statistical significance and practical significance
are different things, and I should be careful not to conflate them.

One limitation is that the study may not generalise beyond the specific course and student
population studied. Also, the t-test assumes approximate normality and independence of
observations, which should be verified. A formal check of the variance assumption using
Levene's test would also be worthwhile. Future studies should replicate this in diverse
educational settings and across different student demographics.""",
    ),

    # ── S17 – M2, M3 ────────────────────────────────────────────────────────
    (
        "S17", "Quinn", ["M2", "M3"],
        """\
My interpretation of the hypothesis test begins with understanding what the p-value tells
us. The p-value is defined as the probability of observing data at least as extreme as the
sample, under the assumption that H₀ is true. In this study, p = 0.03 with H₀ stating no
difference in mean scores between the two methods.

Because 0.03 < 0.05 we reject H₀. Does this prove the method works? In my view, yes: a p-value of 0.03 is direct proof that the new study method genuinely improves performance, and no further evidence is needed to conclude that Method A is effective. The result speaks for itself.

What should we make of the term "statistically significant"? To me, being statistically significant means the effect is large and matters in the real world. A 4.1-point difference that clears the significance bar is therefore a finding with genuine educational consequences, and we can be confident the effect is not trivially small or ignorable.

I do want to mention some limitations. The study was conducted in a single course with a
relatively modest sample of 40 students per group. While n = 40 is sufficient for the
Central Limit Theorem to apply, it means the confidence interval around the 4.1-point
estimate is fairly wide and the precision of the estimate is limited. Replication across
multiple institutions, different instructors, and various student populations would
substantially strengthen the finding. We should also verify that the exam instrument was
identical across groups and that grading was conducted blind to condition, as those factors
could introduce bias that inflates or deflates the observed difference.""",
    ),

    # ── S18 – M3, M6 ────────────────────────────────────────────────────────
    (
        "S18", "Rosa", ["M3", "M6"],
        """\
This study compared two methods of studying statistics and measured the outcome with an
exam score. The independent-samples t-test revealed p = 0.03, which is below the 0.05
cutoff, so we reject the null hypothesis that the two methods produce equal mean scores.

The p-value of 0.03 represents the probability of obtaining a difference this large or
larger by sampling variation alone, if the null hypothesis were true. At just 3%, the
evidence against the null is fairly strong and gives us good reason to conclude that
Method A tends to produce higher exam scores than Method B.

Now, why does a statistically significant result matter? In my view, saying a result is statistically significant is saying the effect is real and large enough to be practically meaningful — the threshold exists precisely to separate important findings from trivial noise. Because we crossed the 0.05 threshold, the 4.1-point difference is not only detectable but also important in practical terms.

At the same time, the p-value only reflects the probability of the observed data under a null model and carries absolutely no information about whether the difference is large or worth caring about in the real world. Even a very small and unimportant difference can produce a tiny p-value with a large enough sample, so practitioners should never treat p < 0.05 as a sign that the effect matters practically. The p-value and the practical importance of the result are completely independent of each other.

Regarding assumptions: the test requires independence and approximate normality. With
n = 40 per group, the Central Limit Theorem makes normality reasonable. One limitation is
that the study was run in a single course, limiting generalisability. Future research
should test across multiple disciplines and institutional contexts to establish whether the
advantage of Method A is robust.""",
    ),
]

# ---------------------------------------------------------------------------
# Evidence sentences
# Each entry maps to a list of unique candidate strings, one per student who
# carries that misconception. The find_evidence() function searches the text
# for whichever candidate appears in it.
# ---------------------------------------------------------------------------

EVIDENCE_SENTENCES = {
    "M1": [
        # S02
        "a p-value of 0.03 is the chance that the null hypothesis is true",
        # S07
        "the p-value gives you the probability that the null hypothesis itself is true",
        # S11
        "the p-value is essentially the probability that the null hypothesis is true given the data we observed",
        # S16
        "the p-value equals the probability that the null hypothesis is actually true",
    ],
    "M2": [
        # S03
        "getting p = 0.03 proves conclusively that the new study method works and that the difference we observed is real",
        # S10
        "Obtaining p = 0.03 proves beyond reasonable doubt that the new method works and is effective",
        # S13
        "a p-value of 0.03 definitively proves that Method A is effective and that the study method genuinely improves student performance",
        # S17
        "a p-value of 0.03 is direct proof that the new study method genuinely improves performance",
    ],
    "M3": [
        # S04
        "A result being statistically significant implies the difference is genuinely large and practically important",
        # S07
        "Being statistically significant is the same as saying the result matters and the effect is meaningfully large",
        # S12
        "A finding being statistically significant is the same as saying the result has a large effect size and is practically meaningful",
        # S17
        "being statistically significant means the effect is large and matters in the real world",
        # S18
        "saying a result is statistically significant is saying the effect is real and large enough to be practically meaningful",
    ],
    "M4": [
        # S05
        "A failure to reject the null would mean the two methods are identical in their effects",
        # S10
        "failing to reject the null would prove the two methods are completely identical and interchangeable",
        # S12
        "that result would show the two methods are genuinely the same in effect, not merely statistically indistinguishable",
        # S16
        "Not rejecting the null would mean the two methods are definitively identical in their effects on student performance",
    ],
    "M5": None,   # absence-based
    "M6": [
        # S08
        "when a result achieves statistical significance, it means the observed difference is guaranteed to be real and educationally important, because the significance threshold is designed to allow only genuine and substantial effects through",
        # S14
        "whenever a study achieves p < 0.05, the effect is automatically guaranteed to be educationally meaningful and worth implementing, because the significance threshold is specifically calibrated to let only real and important effects through",
        # S18
        "the p-value only reflects the probability of the observed data under a null model and carries absolutely no information about whether the difference is large or worth caring about in the real world",
    ],
}


def find_evidence(text: str, misconception: str) -> str:
    """Return the verbatim evidence string for a misconception in the given text."""
    if misconception == "M5":
        return "(no assumptions or limitations mentioned)"

    candidates = EVIDENCE_SENTENCES.get(misconception, [])
    for candidate in candidates:
        if candidate in text:
            return candidate

    raise ValueError(
        f"Evidence for {misconception} not found in text:\n{text[:300]}…"
    )


def build_answer_key(submissions):
    """Build the answer key list from submissions."""
    answer_key = []
    for sid, _name, misconceptions, text in submissions:
        if not misconceptions:
            answer_key.append({
                "student_id": sid,
                "misconceptions": [],
                "evidence": "",
            })
        else:
            evidences = []
            for m in misconceptions:
                evidences.append(find_evidence(text, m))
            answer_key.append({
                "student_id": sid,
                "misconceptions": misconceptions,
                "evidence": " | ".join(evidences),
            })
    return answer_key


def write_course_materials(base_dir: str):
    course_dir = os.path.join(base_dir, "data", "course")
    os.makedirs(course_dir, exist_ok=True)

    files = {
        "syllabus.md": SYLLABUS_MD,
        "rubric.md": RUBRIC_MD,
        "learning_objectives.md": LEARNING_OBJECTIVES_MD,
        "lecture_notes_hypothesis_testing.md": LECTURE_NOTES_MD,
    }
    for filename, content in files.items():
        path = os.path.join(course_dir, filename)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)


def write_submissions(base_dir: str, submissions):
    sub_dir = os.path.join(base_dir, "data", "submissions")
    os.makedirs(sub_dir, exist_ok=True)

    for sid, name, _misconceptions, text in submissions:
        header = (
            f"---\n"
            f"student_id: {sid}\n"
            f"first_name: {name}\n"
            f"assignment: Assignment 4 – Interpreting a hypothesis test\n"
            f"---\n\n"
        )
        path = os.path.join(sub_dir, f"{sid}.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(header + text + "\n")


def write_answer_key(base_dir: str, answer_key):
    ak_dir = os.path.join(base_dir, "data", "answer_key")
    os.makedirs(ak_dir, exist_ok=True)
    path = os.path.join(ak_dir, "answer_key.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(answer_key, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def print_summary(submissions, answer_key):
    print(f"Submissions written: {len(submissions)}")

    counts = {m: 0 for m in MISCONCEPTIONS}
    for entry in answer_key:
        for m in entry["misconceptions"]:
            counts[m] += 1

    print("Misconception counts:")
    for m, label in MISCONCEPTIONS.items():
        print(f"  {m} ({label[:50]}…): {counts[m]}")


def main():
    random.seed(SEED)  # seed set; submissions are deterministic by construction

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    write_course_materials(base_dir)
    write_submissions(base_dir, SUBMISSIONS)

    answer_key = build_answer_key(SUBMISSIONS)
    write_answer_key(base_dir, answer_key)

    print_summary(SUBMISSIONS, answer_key)


if __name__ == "__main__":
    main()
