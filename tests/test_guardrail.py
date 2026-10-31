"""Tests for viva_prep.tools.guardrail.check_output."""

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

    # --- Rule 1b: criterion verdict ---

    def test_meets_criterion_1(self):
        _blocked("The student's explanation meets criterion 1 of the rubric.")

    def test_meeting_criterion_5(self):
        _blocked("The student is meeting criterion 5 with this answer.")

    def test_satisfying_clarity_criterion(self):
        _blocked("The response is satisfying the clarity criterion.")

    def test_fulfils_criterion_4(self):
        _blocked("The conclusion fulfils criterion 4 on limitations.")

    def test_criterion_3_is_met(self):
        _blocked("criterion 3 is met by the definition provided.")

    def test_criterion_blocked_student(self):
        _blocked("The answer meets criterion 2.", audience="student")

    # --- Rule 2 (extended): authorship vouching via "own words" ---

    def test_own_words_declarative_their(self):
        _blocked("The explanation is coherent and in their own words.")

    def test_own_words_declarative_their_student(self):
        _blocked("The explanation is coherent and in their own words.", audience="student")

    def test_own_words_curly_apostrophe(self):
        _blocked("The writing is in the student\u2019s own words and shows a clear structure.")

    def test_own_words_curly_apostrophe_student(self):
        _blocked(
            "The writing is in the student\u2019s own words and shows a clear structure.",
            audience="student",
        )

    def test_own_words_straight_apostrophe(self):
        _blocked("The response is coherent and largely in the student's own words.")

    def test_own_words_straight_apostrophe_student(self):
        _blocked(
            "The response is coherent and largely in the student's own words.",
            audience="student",
        )

    def test_own_words_uses_own_words(self):
        _blocked("The rest of the explanation is coherent and uses own words.")

    def test_own_words_uses_own_words_student(self):
        _blocked(
            "The rest of the explanation is coherent and uses own words.",
            audience="student",
        )

    def test_own_words_using_their_own_words(self):
        _blocked("The reasoning is not fully coherent despite using their own words.")

    def test_own_words_using_their_own_words_student(self):
        _blocked(
            "The reasoning is not fully coherent despite using their own words.",
            audience="student",
        )

    def test_own_work_declarative(self):
        _blocked("This is their own work.")

    def test_own_work_declarative_student(self):
        _blocked("This is their own work.", audience="student")


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

    # --- Rule 1b: criterion references that must stay allowed ---

    def test_criterion_relates_to(self):
        _allowed("this relates to criterion 3 of the rubric.")

    def test_criterion_asks_for(self):
        _allowed("Criterion 4 asks for limitations of the study.")

    def test_criterion_under_framing(self):
        _allowed("under criterion 1 the student defines the p-value correctly.")

    # --- Rule 2 (extended): teaching "own words" requests must stay allowed ---

    def test_own_words_teaching_can_you(self):
        _allowed("Can you explain, in your own words, what the p-value of 0.03 means?")

    def test_own_words_teaching_ask_student(self):
        _allowed("Ask the student to restate the definition in their own words.")

    def test_own_words_teaching_explain_imperative(self):
        _allowed("Explain in your own words why we reject the null hypothesis.")

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
