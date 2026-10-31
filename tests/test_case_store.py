"""Tests for viva_prep/tools/case_store.py."""

from __future__ import annotations

import json
import pathlib

import pytest

from viva_prep.tools.case_store import (
    get_approved_questions,
    get_records,
    get_round_status,
    save_record,
)


# ---------------------------------------------------------------------------
# Fixture: isolated store path
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def isolated_store(tmp_path, monkeypatch):
    """Point VIVA_STORE_PATH at a temporary file for every test."""
    store_file = tmp_path / "records.json"
    monkeypatch.setenv("VIVA_STORE_PATH", str(store_file))
    # Also point submissions dir at the real data directory so
    # get_round_status can scan student files.
    data_dir = pathlib.Path(__file__).parent.parent / "data"
    monkeypatch.setenv("VIVA_DATA_DIR", str(data_dir))
    yield store_file


# ---------------------------------------------------------------------------
# save_record / get_records round-trip
# ---------------------------------------------------------------------------

class TestSaveAndGet:
    def test_save_returns_record_with_expected_keys(self):
        record = save_record("S01", "transcript", "Hello world")
        assert set(record.keys()) == {"student_id", "kind", "content", "version", "saved_at"}

    def test_save_echoes_input_fields(self):
        record = save_record("S02", "briefing", "Some briefing text")
        assert record["student_id"] == "S02"
        assert record["kind"] == "briefing"
        assert record["content"] == "Some briefing text"

    def test_save_first_record_has_version_1(self):
        record = save_record("S01", "question_plan", "plan content")
        assert record["version"] == 1

    def test_version_increments_per_student_kind(self):
        save_record("S01", "question_plan", "v1")
        r2 = save_record("S01", "question_plan", "v2")
        r3 = save_record("S01", "question_plan", "v3")
        assert r2["version"] == 2
        assert r3["version"] == 3

    def test_version_is_independent_across_kinds(self):
        r_plan = save_record("S01", "question_plan", "plan")
        r_transcript = save_record("S01", "transcript", "transcript")
        assert r_plan["version"] == 1
        assert r_transcript["version"] == 1

    def test_version_is_independent_across_students(self):
        save_record("S01", "briefing", "s01 briefing")
        r = save_record("S02", "briefing", "s02 briefing")
        assert r["version"] == 1

    def test_saved_at_is_iso_utc_string(self):
        record = save_record("S01", "briefing", "x")
        # Must be parseable and contain timezone offset
        saved_at = record["saved_at"]
        assert isinstance(saved_at, str)
        assert "T" in saved_at  # ISO 8601 separator
        assert saved_at.endswith("+00:00") or saved_at.endswith("Z")

    def test_get_records_returns_saved_record(self):
        save_record("S03", "transcript", "content A")
        result = get_records("S03", "transcript")
        assert len(result) == 1
        assert result[0]["content"] == "content A"

    def test_get_records_returns_oldest_first(self):
        save_record("S01", "question_plan", "first")
        save_record("S01", "question_plan", "second")
        save_record("S01", "question_plan", "third")
        result = get_records("S01", "question_plan")
        assert [r["content"] for r in result] == ["first", "second", "third"]

    def test_get_records_no_kind_filter_returns_all_kinds(self):
        save_record("S04", "question_plan", "plan")
        save_record("S04", "briefing", "brief")
        save_record("S04", "transcript", "trans")
        result = get_records("S04")
        assert len(result) == 3

    def test_get_records_kind_filter_excludes_other_kinds(self):
        save_record("S05", "question_plan", "plan")
        save_record("S05", "briefing", "brief")
        result = get_records("S05", "briefing")
        assert len(result) == 1
        assert result[0]["kind"] == "briefing"

    def test_get_records_returns_empty_for_unknown_student(self):
        result = get_records("S99")
        assert result == []

    def test_get_records_returns_empty_for_unrecorded_kind(self):
        save_record("S01", "briefing", "x")
        result = get_records("S01", "transcript")
        assert result == []


# ---------------------------------------------------------------------------
# Unknown kind
# ---------------------------------------------------------------------------

class TestUnknownKind:
    def test_unknown_kind_returns_error_dict(self):
        result = save_record("S01", "invalid_kind", "x")
        assert result == {"error": "unknown_kind"}

    def test_unknown_kind_does_not_persist_to_store(self):
        save_record("S01", "bad_kind", "should not be stored")
        result = get_records("S01")
        assert result == []


# ---------------------------------------------------------------------------
# Class summary uses "CLASS" student_id
# ---------------------------------------------------------------------------

class TestClassSummary:
    def test_class_summary_saved_under_CLASS(self):
        record = save_record("CLASS", "class_summary", "overall summary")
        assert record["student_id"] == "CLASS"
        assert record["kind"] == "class_summary"

    def test_class_summary_retrievable(self):
        save_record("CLASS", "class_summary", "summary text")
        result = get_records("CLASS", "class_summary")
        assert len(result) == 1
        assert result[0]["content"] == "summary text"


# ---------------------------------------------------------------------------
# File persistence: survive a module reload
# ---------------------------------------------------------------------------

class TestFilePersistence:
    def test_records_survive_reload(self, isolated_store):
        save_record("S01", "question_plan", "persisted plan")
        # Verify by reading the JSON file directly (simulates a new process)
        raw = json.loads(isolated_store.read_text(encoding="utf-8"))
        assert len(raw) == 1
        assert raw[0]["student_id"] == "S01"
        assert raw[0]["kind"] == "question_plan"
        assert raw[0]["content"] == "persisted plan"

    def test_multiple_records_all_persisted(self, isolated_store):
        save_record("S01", "question_plan", "plan")
        save_record("S01", "transcript", "trans")
        save_record("S02", "briefing", "brief")
        raw = json.loads(isolated_store.read_text(encoding="utf-8"))
        assert len(raw) == 3

    def test_second_call_appends_not_overwrites(self, isolated_store):
        save_record("S01", "briefing", "first")
        save_record("S01", "briefing", "second")
        raw = json.loads(isolated_store.read_text(encoding="utf-8"))
        assert len(raw) == 2


# ---------------------------------------------------------------------------
# get_round_status
# ---------------------------------------------------------------------------

class TestGetRoundStatus:
    def test_returns_list_for_all_submission_students(self):
        result = get_round_status()
        ids = [r["student_id"] for r in result]
        # All 18 students should appear (S01..S18)
        assert len(result) == 18
        assert "S01" in ids
        assert "S18" in ids

    def test_sorted_by_student_id(self):
        result = get_round_status()
        ids = [r["student_id"] for r in result]
        assert ids == sorted(ids)

    def test_all_flags_false_when_no_records(self):
        result = get_round_status()
        for entry in result:
            assert entry["has_plan"] is False
            assert entry["plan_approved"] is False
            assert entry["has_transcript"] is False
            assert entry["has_briefing"] is False

    def test_has_plan_true_after_save(self):
        save_record("S03", "question_plan", "plan content")
        result = {r["student_id"]: r for r in get_round_status()}
        assert result["S03"]["has_plan"] is True
        assert result["S03"]["plan_approved"] is False

    def test_plan_approved_true_after_approval_save(self):
        save_record("S05", "plan_approval", json.dumps(["Q1", "Q2"]))
        result = {r["student_id"]: r for r in get_round_status()}
        assert result["S05"]["plan_approved"] is True

    def test_has_transcript_true_after_save(self):
        save_record("S07", "transcript", "transcript text")
        result = {r["student_id"]: r for r in get_round_status()}
        assert result["S07"]["has_transcript"] is True

    def test_has_briefing_true_after_save(self):
        save_record("S10", "briefing", "briefing text")
        result = {r["student_id"]: r for r in get_round_status()}
        assert result["S10"]["has_briefing"] is True

    def test_flags_independent_across_students(self):
        save_record("S01", "transcript", "t")
        result = {r["student_id"]: r for r in get_round_status()}
        # S02 should remain untouched
        assert result["S02"]["has_transcript"] is False

    def test_required_keys_present(self):
        result = get_round_status()
        for entry in result:
            assert set(entry.keys()) == {
                "student_id", "has_plan", "plan_approved",
                "has_transcript", "has_briefing"
            }


# ---------------------------------------------------------------------------
# get_approved_questions
# ---------------------------------------------------------------------------

class TestGetApprovedQuestions:
    def test_not_approved_before_any_save(self):
        result = get_approved_questions("S01")
        assert result == {"error": "not_approved", "student_id": "S01"}

    def test_returns_not_approved_when_only_other_kinds_exist(self):
        save_record("S02", "briefing", "some briefing")
        save_record("S02", "transcript", "some transcript")
        result = get_approved_questions("S02")
        assert result["error"] == "not_approved"

    def test_returns_questions_after_approval_saved(self):
        questions = ["What is X?", "Explain Y.", "Discuss Z."]
        save_record("S03", "plan_approval", json.dumps(questions))
        result = get_approved_questions("S03")
        assert result == {"student_id": "S03", "questions": questions}

    def test_questions_is_a_list_of_strings(self):
        questions = ["Q1", "Q2"]
        save_record("S04", "plan_approval", json.dumps(questions))
        result = get_approved_questions("S04")
        assert isinstance(result["questions"], list)
        for q in result["questions"]:
            assert isinstance(q, str)

    def test_briefing_never_appears_in_output(self):
        questions = ["Only question"]
        save_record("S05", "plan_approval", json.dumps(questions))
        save_record("S05", "briefing", "DO NOT RETURN THIS")
        result = get_approved_questions("S05")
        assert "briefing" not in str(result)
        assert "DO NOT RETURN THIS" not in str(result)
        assert result["questions"] == questions

    def test_returns_latest_approval_when_multiple_versions(self):
        save_record("S06", "plan_approval", json.dumps(["Old Q1"]))
        save_record("S06", "plan_approval", json.dumps(["New Q1", "New Q2"]))
        result = get_approved_questions("S06")
        assert result["questions"] == ["New Q1", "New Q2"]

    def test_other_students_approval_not_returned(self):
        save_record("S07", "plan_approval", json.dumps(["Q for S07"]))
        result = get_approved_questions("S08")
        assert result["error"] == "not_approved"

    def test_result_has_no_other_record_kinds(self):
        """The returned dict must only have student_id and questions."""
        save_record("S09", "plan_approval", json.dumps(["Q1"]))
        save_record("S09", "transcript", "secret transcript")
        result = get_approved_questions("S09")
        assert set(result.keys()) == {"student_id", "questions"}


# ---------------------------------------------------------------------------
# Read-only file system
# ---------------------------------------------------------------------------

class TestReadOnlyStore:
    """Behaviour when VIVA_STORE_PATH points at a location that cannot be written."""

    @pytest.fixture()
    def readonly_store(self, tmp_path, monkeypatch):
        """Point the store at a path inside a read-only directory."""
        readonly_dir = tmp_path / "readonly_store"
        readonly_dir.mkdir()
        readonly_dir.chmod(0o555)  # r-xr-xr-x  — no write permission
        store_file = readonly_dir / "records.json"
        monkeypatch.setenv("VIVA_STORE_PATH", str(store_file))
        data_dir = pathlib.Path(__file__).parent.parent / "data"
        monkeypatch.setenv("VIVA_DATA_DIR", str(data_dir))
        yield store_file
        # Restore write permission so tmp_path cleanup succeeds.
        readonly_dir.chmod(0o755)

    def test_save_record_returns_error_dict_not_writable(self, readonly_store):
        result = save_record("S01", "transcript", "hello")
        assert result == {"error": "store_not_writable"}

    def test_save_record_does_not_raise(self, readonly_store):
        # Must never raise — Orchestrate tools must always return a value.
        try:
            save_record("S01", "transcript", "hello")
        except Exception as exc:
            pytest.fail(f"save_record raised unexpectedly: {exc}")

    def test_get_records_returns_empty_when_store_missing(self, readonly_store):
        # The store file was never created (write failed) — should return [].
        result = get_records("S01")
        assert result == []

    def test_get_round_status_returns_students_when_store_missing(self, readonly_store):
        # get_round_status reads submission files; the store is missing but that
        # is fine — all flags should be False.
        result = get_round_status()
        assert len(result) == 18
        for entry in result:
            assert entry["has_plan"] is False
            assert entry["plan_approved"] is False

    def test_get_approved_questions_returns_not_approved_when_store_missing(
        self, readonly_store
    ):
        result = get_approved_questions("S01")
        assert result == {"error": "not_approved", "student_id": "S01"}
