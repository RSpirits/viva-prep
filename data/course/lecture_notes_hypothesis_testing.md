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
