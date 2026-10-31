"""Tests for viva_prep/tools/submissions.py."""

from __future__ import annotations

import ast
import pathlib

import pytest

from viva_prep.tools.submissions import get_submission, list_submissions

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

DATA_DIR = pathlib.Path(__file__).parent.parent / "data"
SUBMISSIONS_DIR = DATA_DIR / "submissions"
ANSWER_KEY_DIR = DATA_DIR / "answer_key"
TOOLS_DIR = pathlib.Path(__file__).parent.parent / "viva_prep" / "tools"


# ---------------------------------------------------------------------------
# list_submissions
# ---------------------------------------------------------------------------

class TestListSubmissions:
    def test_returns_18_entries(self):
        result = list_submissions()
        assert len(result) == 18

    def test_sorted_by_student_id(self):
        result = list_submissions()
        ids = [r["student_id"] for r in result]
        assert ids == sorted(ids)

    def test_each_entry_has_required_keys(self):
        result = list_submissions()
        for entry in result:
            assert "student_id" in entry
            assert "first_name" in entry

    def test_first_entry_is_s01(self):
        result = list_submissions()
        assert result[0]["student_id"] == "S01"

    def test_last_entry_is_s18(self):
        result = list_submissions()
        assert result[-1]["student_id"] == "S18"

    def test_assignment_parameter_accepted(self):
        """list_submissions must accept the assignment keyword without error."""
        result = list_submissions(assignment="Assignment 4")
        assert len(result) == 18


# ---------------------------------------------------------------------------
# get_submission
# ---------------------------------------------------------------------------

class TestGetSubmission:
    def test_known_id_returns_required_keys(self):
        result = get_submission("S01")
        assert "error" not in result
        for key in ("student_id", "first_name", "assignment", "text", "rubric"):
            assert key in result, f"missing key: {key}"

    def test_student_id_echoed_correctly(self):
        result = get_submission("S05")
        assert result["student_id"] == "S05"

    def test_text_is_non_empty_string(self):
        result = get_submission("S01")
        assert isinstance(result["text"], str)
        assert len(result["text"]) > 0

    def test_text_does_not_contain_front_matter(self):
        result = get_submission("S01")
        # The body must not start with the YAML delimiter
        assert not result["text"].strip().startswith("---")
        # Front-matter keys must not appear as literal lines in the body
        assert "student_id:" not in result["text"]
        assert "first_name:" not in result["text"]

    def test_rubric_is_non_empty_string(self):
        result = get_submission("S01")
        assert isinstance(result["rubric"], str)
        assert len(result["rubric"]) > 0

    def test_rubric_matches_file_on_disk(self):
        rubric_path = DATA_DIR / "course" / "rubric.md"
        expected = rubric_path.read_text(encoding="utf-8")
        result = get_submission("S01")
        assert result["rubric"] == expected

    def test_first_name_matches_roster(self):
        # S01 is Amara per the fixture file
        result = get_submission("S01")
        assert result["first_name"] == "Amara"

    def test_unknown_id_returns_error_dict(self):
        result = get_submission("S99")
        assert result.get("error") == "not_found"
        assert result.get("student_id") == "S99"

    def test_unknown_id_does_not_raise(self):
        """get_submission must return a dict, never raise, for unknown IDs."""
        result = get_submission("DOES_NOT_EXIST")
        assert isinstance(result, dict)

    def test_unknown_id_has_no_extra_keys(self):
        result = get_submission("MISSING")
        assert set(result.keys()) == {"error", "student_id"}


# ---------------------------------------------------------------------------
# answer_key isolation — no tool may ever read data/answer_key/
# ---------------------------------------------------------------------------

class TestAnswerKeyIsolation:
    """Statically verify that no source file under viva_prep/tools/ references
    the answer_key path, and dynamically confirm the real functions do not
    open any file inside that directory."""

    def _collect_tool_sources(self) -> list[pathlib.Path]:
        return list(TOOLS_DIR.rglob("*.py"))

    def test_no_static_reference_to_answer_key_in_tool_sources(self):
        """No Python source file in viva_prep/tools/ should contain the
        literal string 'answer_key'."""
        for src in self._collect_tool_sources():
            text = src.read_text(encoding="utf-8")
            assert "answer_key" not in text, (
                f"{src} contains a reference to 'answer_key'"
            )

    def test_list_submissions_does_not_open_answer_key(self, monkeypatch):
        """Patch builtins.open to detect any access inside answer_key/."""
        import builtins

        real_open = builtins.open
        answer_key_str = str(ANSWER_KEY_DIR.resolve())

        def guarded_open(file, *args, **kwargs):
            resolved = str(pathlib.Path(file).resolve())
            assert not resolved.startswith(answer_key_str), (
                f"list_submissions opened a file in answer_key/: {file}"
            )
            return real_open(file, *args, **kwargs)

        monkeypatch.setattr(builtins, "open", guarded_open)
        list_submissions()  # must not touch answer_key/

    def test_get_submission_does_not_open_answer_key(self, monkeypatch):
        """Patch builtins.open to detect any access inside answer_key/."""
        import builtins

        real_open = builtins.open
        answer_key_str = str(ANSWER_KEY_DIR.resolve())

        def guarded_open(file, *args, **kwargs):
            resolved = str(pathlib.Path(file).resolve())
            assert not resolved.startswith(answer_key_str), (
                f"get_submission opened a file in answer_key/: {file}"
            )
            return real_open(file, *args, **kwargs)

        monkeypatch.setattr(builtins, "open", guarded_open)
        get_submission("S01")
        get_submission("S99")  # also check the not-found path
