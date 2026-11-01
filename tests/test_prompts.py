"""Tests for prompts/ files and agents/*.yaml files.

Run after scripts/build_agents.py has been executed so that agents/*.yaml
files exist and can be checked.

Test matrix
-----------
1. Every prompts/*.md file contains all four shared rules.
2. Every agents/<name>.yaml ``instructions`` field equals the text of
   its matching prompts/<name>.md (build_agents.py must be run first).
3. No file in prompts/ mentions "answer_key".
4. No file in agents/ mentions "answer_key".
5. No file in prompts/ contains a misconception code M1–M6.
6. No file in agents/ (excluding course_knowledge.yaml) contains a
   misconception code M1–M6.
7. Every prompts/*.md file is under 400 words.
8. Two additional shared sentences appear verbatim in every prompts/*.md file:
   the guardrail-before-output sentence and the tool-failure retry sentence.
"""

from __future__ import annotations

import pathlib
import re

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO = pathlib.Path(__file__).parent.parent
PROMPTS_DIR = REPO / "prompts"
AGENTS_DIR = REPO / "agents"
BUILD_SCRIPT = REPO / "scripts" / "build_agents.py"

PROMPT_FILES = sorted(PROMPTS_DIR.glob("*.md"))
AGENT_NAMES = ["coordinator", "question_planner", "practice_partner",
               "briefing_writer", "class_insights"]

# ---------------------------------------------------------------------------
# Shared-rules fixture
# ---------------------------------------------------------------------------

SHARED_RULES = [
    # Rule 1 — no grades
    "Never give a grade, score, mark or pass/fail verdict.",
    # Rule 2 — no authorship judgment
    "Never say or suggest whether the work was written by AI or by someone else.",
    # Rule 3 — guardrail before output
    "check_output(text, audience)",
    # Rule 4 — no invented content
    "Do not invent course content.",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _parse_yaml_instructions(yaml_text: str) -> str:
    """Extract the literal-block ``instructions`` value from a YAML file.

    Works without a YAML parser: the ADK YAML written by build_agents.py
    uses a literal block scalar (``instructions: |\\n  <indented lines>``).
    The block ends at the first line that is not indented (or at EOF).
    """
    lines = yaml_text.splitlines(keepends=True)
    in_block = False
    block_indent: int = 0
    collected: list[str] = []

    for line in lines:
        if not in_block:
            stripped = line.lstrip()
            if stripped.startswith("instructions:"):
                remainder = stripped[len("instructions:"):].strip()
                if remainder == "|":
                    in_block = True
                    # block_indent will be determined by the first content line
                    block_indent = 0
            continue

        # Inside the literal block
        if line.strip() == "":
            # Blank lines are part of the block
            collected.append("\n")
            continue

        leading_spaces = len(line) - len(line.lstrip(" "))
        if block_indent == 0:
            block_indent = leading_spaces

        if leading_spaces < block_indent and line.strip():
            # Non-empty line less indented than block — block has ended
            break

        # Strip exactly block_indent spaces
        collected.append(line[block_indent:])

    return "".join(collected).rstrip("\n")


# ---------------------------------------------------------------------------
# Test 1 — every prompts file contains all four shared rules
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("prompt_file", PROMPT_FILES, ids=lambda p: p.name)
@pytest.mark.parametrize("rule", SHARED_RULES, ids=lambda r: r[:40])
def test_prompts_contain_shared_rules(prompt_file: pathlib.Path, rule: str) -> None:
    text = _load_text(prompt_file)
    assert rule in text, (
        f"{prompt_file.name} is missing shared rule: {rule!r}"
    )


# ---------------------------------------------------------------------------
# Test 2 — agents/*.yaml instructions equals prompts/*.md
# (build_agents.py must have been run before this test)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("name", AGENT_NAMES)
def test_agent_instructions_match_prompt(name: str) -> None:
    prompt_path = PROMPTS_DIR / f"{name}.md"
    agent_path = AGENTS_DIR / f"{name}.yaml"

    if not agent_path.exists():
        pytest.skip(
            f"{agent_path} not found — run scripts/build_agents.py first"
        )

    expected = _load_text(prompt_path).rstrip("\n")
    yaml_text = _load_text(agent_path)
    actual = _parse_yaml_instructions(yaml_text)

    assert actual == expected, (
        f"agents/{name}.yaml instructions field does not match prompts/{name}.md.\n"
        f"First difference at char {_first_diff_pos(expected, actual)}."
    )


def _first_diff_pos(a: str, b: str) -> int:
    for i, (ca, cb) in enumerate(zip(a, b)):
        if ca != cb:
            return i
    return min(len(a), len(b))


# ---------------------------------------------------------------------------
# Test 3 — no prompts file mentions answer_key
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("prompt_file", PROMPT_FILES, ids=lambda p: p.name)
def test_prompts_no_answer_key(prompt_file: pathlib.Path) -> None:
    text = _load_text(prompt_file)
    assert "answer_key" not in text, (
        f"{prompt_file.name} must not mention 'answer_key'."
    )


# ---------------------------------------------------------------------------
# Test 4 — no agents file mentions answer_key
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "agent_file",
    sorted(AGENTS_DIR.glob("*.yaml")) if AGENTS_DIR.exists() else [],
    ids=lambda p: p.name,
)
def test_agents_no_answer_key(agent_file: pathlib.Path) -> None:
    text = _load_text(agent_file)
    assert "answer_key" not in text, (
        f"{agent_file.name} must not mention 'answer_key'."
    )


# ---------------------------------------------------------------------------
# Test 5 — no prompts file contains misconception codes M1–M6
# ---------------------------------------------------------------------------

_MISCONCEPTION_RE = re.compile(r"\bM[1-6]\b")


@pytest.mark.parametrize("prompt_file", PROMPT_FILES, ids=lambda p: p.name)
def test_prompts_no_misconception_codes(prompt_file: pathlib.Path) -> None:
    text = _load_text(prompt_file)
    matches = _MISCONCEPTION_RE.findall(text)
    assert not matches, (
        f"{prompt_file.name} must not contain misconception codes; found: {matches}"
    )


# ---------------------------------------------------------------------------
# Test 6 — no agents file contains misconception codes M1–M6
# (course_knowledge.yaml is excluded because it only lists filenames)
# ---------------------------------------------------------------------------

_AGENT_YAML_FILES = [
    AGENTS_DIR / f"{name}.yaml" for name in AGENT_NAMES
    if (AGENTS_DIR / f"{name}.yaml").exists()
]


@pytest.mark.parametrize(
    "agent_file",
    _AGENT_YAML_FILES,
    ids=lambda p: p.name,
)
def test_agents_no_misconception_codes(agent_file: pathlib.Path) -> None:
    text = _load_text(agent_file)
    matches = _MISCONCEPTION_RE.findall(text)
    assert not matches, (
        f"{agent_file.name} must not contain misconception codes; found: {matches}"
    )


# ---------------------------------------------------------------------------
# Test 7 — every prompts file is under 400 words
# ---------------------------------------------------------------------------

_WORD_LIMIT = 400


@pytest.mark.parametrize("prompt_file", PROMPT_FILES, ids=lambda p: p.name)
def test_prompts_under_400_words(prompt_file: pathlib.Path) -> None:
    text = _load_text(prompt_file)
    word_count = len(text.split())
    assert word_count < _WORD_LIMIT, (
        f"{prompt_file.name} is {word_count} words — must be under {_WORD_LIMIT}."
    )


# ---------------------------------------------------------------------------
# Test 8 — two additional shared sentences appear verbatim in every prompts file
# ---------------------------------------------------------------------------

SHARED_VERBATIM_SENTENCES = [
    # Guardrail-before-output sentence
    (
        'Before any text is shown to a person, call `check_output(text, audience)`. '
        'If it is blocked, rewrite once and check again. '
        'If it is still blocked, return `"needs attention"` instead of the text.'
    ),
    # Tool-failure retry sentence
    (
        'If a tool call fails, retry once. '
        'If it fails again, return `"needs attention"` and name the tool.'
    ),
]


@pytest.mark.parametrize("prompt_file", PROMPT_FILES, ids=lambda p: p.name)
@pytest.mark.parametrize(
    "sentence",
    SHARED_VERBATIM_SENTENCES,
    ids=["guardrail_before_output", "tool_failure_retry"],
)
def test_prompts_contain_verbatim_sentences(
    prompt_file: pathlib.Path, sentence: str
) -> None:
    text = _load_text(prompt_file)
    assert sentence in text, (
        f"{prompt_file.name} is missing verbatim shared sentence:\n  {sentence!r}"
    )


# ---------------------------------------------------------------------------
# Test 9 — practice_partner step 1 mentions both get_approved_questions and
#           the session-start message
# ---------------------------------------------------------------------------

def test_practice_partner_step1_mentions_get_approved_questions_and_session_start() -> None:
    text = _load_text(PROMPTS_DIR / "practice_partner.md")
    assert "get_approved_questions" in text, (
        "practice_partner.md step 1 must mention get_approved_questions"
    )
    assert "session-start message" in text, (
        "practice_partner.md step 1 must mention the session-start message"
    )


# ---------------------------------------------------------------------------
# Test 10 — agents/coordinator.yaml lists practice_partner as a collaborator
# ---------------------------------------------------------------------------

def test_coordinator_yaml_lists_practice_partner_collaborator() -> None:
    agent_path = AGENTS_DIR / "coordinator.yaml"
    if not agent_path.exists():
        pytest.skip(f"{agent_path} not found — run scripts/build_agents.py first")
    text = _load_text(agent_path)
    # The collaborators block is a YAML list; check that practice_partner appears
    # as a list item (e.g. "  - practice_partner")
    assert re.search(r"^\s*-\s*practice_partner\s*$", text, re.MULTILINE), (
        "agents/coordinator.yaml must list practice_partner as a collaborator"
    )


# ---------------------------------------------------------------------------
# Test 11 — prompts/coordinator.md says only approved question texts are passed
#            to practice_partner
# ---------------------------------------------------------------------------

def test_coordinator_passes_only_approved_question_texts_to_practice_partner() -> None:
    text = _load_text(PROMPTS_DIR / "coordinator.md")
    assert "approved question texts only" in text, (
        "prompts/coordinator.md must state that only the approved question texts "
        "are passed to practice_partner"
    )
