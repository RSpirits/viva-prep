"""Watsonx Orchestrate tools for storing per-student viva records.

Persistence between sessions inside the Orchestrate trial instance is not yet
confirmed; if files do not persist there, the Coordinator passes the record
JSON between agents instead.
"""

from __future__ import annotations

import json
import os
import pathlib
import tempfile
from datetime import datetime, timezone

try:
    from ibm_watsonx_orchestrate.agent_builder.tools import tool
except ImportError:
    def tool(fn):  # type: ignore[misc]
        """No-op fallback when the ADK is not installed."""
        return fn


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_KINDS = frozenset(
    {"question_plan", "plan_approval", "transcript", "briefing",
     "student_summary", "class_summary"}
)

_DEFAULT_STORE_PATH = "./store/records.json"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _store_path() -> pathlib.Path:
    env = os.environ.get("VIVA_STORE_PATH")
    return pathlib.Path(env) if env else pathlib.Path(_DEFAULT_STORE_PATH)


def _load_records() -> list[dict]:
    path = _store_path()
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def _save_records(records: list[dict]) -> bool:
    """Write *records* to the store file.  Returns True on success, False if
    the file system is read-only or otherwise unwritable."""
    path = _store_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    except OSError:
        return False
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(records, fh, indent=2)
        os.replace(tmp, path)
        return True
    except OSError:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        return False


def _submissions_dir() -> pathlib.Path:
    """Return data/submissions/, honoring VIVA_DATA_DIR if set."""
    env = os.environ.get("VIVA_DATA_DIR")
    base = pathlib.Path(env) if env else pathlib.Path(__file__).parent.parent.parent / "data"
    return base / "submissions"


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def save_record(student_id: str, kind: str, content: str) -> dict:
    """Append a versioned record for a student and return it.

    Args:
        student_id: The student identifier, e.g. ``"S03"``. Use ``"CLASS"``
            for ``kind="class_summary"``.
        kind: One of ``"question_plan"``, ``"plan_approval"``,
            ``"transcript"``, ``"briefing"``, ``"student_summary"``,
            ``"class_summary"``.
        content: The record payload (free text or JSON string).

    Returns:
        The saved record dict with keys ``student_id``, ``kind``,
        ``content``, ``version`` (1-based, incrementing per student+kind),
        ``saved_at`` (UTC ISO-8601), and ``saved`` (bool).
        When the write succeeds, ``saved`` is ``True`` and there is no
        ``"note"`` key.
        When the store cannot be written (e.g. a read-only file system),
        ``saved`` is ``False``, ``reason`` is ``"store_not_writable"``, and
        ``note`` is set to explain that this is expected and not a failed tool
        call; there is no ``"error"`` key in this case so agents can continue.
        Returns ``{"error": "unknown_kind"}`` for an unrecognised kind.
    """
    if kind not in VALID_KINDS:
        return {"error": "unknown_kind"}

    records = _load_records()

    # Compute next version for this (student_id, kind) pair.
    version = sum(
        1 for r in records
        if r["student_id"] == student_id and r["kind"] == kind
    ) + 1

    record = {
        "student_id": student_id,
        "kind": kind,
        "content": content,
        "version": version,
        "saved_at": datetime.now(timezone.utc).isoformat(),
    }
    records.append(record)
    if not _save_records(records):
        return {
            **record,
            "saved": False,
            "reason": "store_not_writable",
            "note": (
                "This environment cannot store records. This is expected and"
                " is not a failed tool call: do not retry, and continue with"
                " your task."
            ),
        }
    return {**record, "saved": True}


@tool
def get_records(student_id: str, kind: str = "") -> list[dict]:
    """Return stored records for a student, oldest first.

    Args:
        student_id: The student identifier to query.
        kind: Optional kind filter. When omitted (or empty string) all
            record kinds for the student are returned.

    Returns:
        A list of record dicts sorted by insertion order (oldest first).
    """
    records = _load_records()
    result = [r for r in records if r["student_id"] == student_id]
    if kind:
        result = [r for r in result if r["kind"] == kind]
    return result


@tool
def get_round_status() -> list[dict]:
    """Return a readiness summary for every student with a submission file.

    Scans ``data/submissions/`` for student IDs and cross-references the
    record store to report which pipeline stages have been completed.

    Returns:
        A list of dicts (one per student, sorted by student_id), each with:

        - ``student_id`` (str)
        - ``has_plan`` (bool): at least one ``"question_plan"`` record exists.
        - ``plan_approved`` (bool): at least one ``"plan_approval"`` record exists.
        - ``has_transcript`` (bool): at least one ``"transcript"`` record exists.
        - ``has_briefing`` (bool): at least one ``"briefing"`` record exists.
    """
    records = _load_records()
    kinds_by_student: dict[str, set[str]] = {}
    for r in records:
        kinds_by_student.setdefault(r["student_id"], set()).add(r["kind"])

    student_ids: list[str] = sorted(
        md.stem
        for md in _submissions_dir().glob("*.md")
    )

    result = []
    for sid in student_ids:
        kinds = kinds_by_student.get(sid, set())
        result.append({
            "student_id": sid,
            "has_plan": "question_plan" in kinds,
            "plan_approved": "plan_approval" in kinds,
            "has_transcript": "transcript" in kinds,
            "has_briefing": "briefing" in kinds,
        })
    return result


@tool
def get_approved_questions(student_id: str) -> dict:
    """Return the approved question list for a student (Practice Partner use only).

    This is the only record-store tool exposed to the student-facing Practice
    Partner agent.  It returns nothing but the approved questions — other record
    kinds are never surfaced.

    Args:
        student_id: The student identifier, e.g. ``"S03"``.

    Returns:
        On success: ``{"student_id": ..., "questions": [str, ...]}``.
        If no approval exists yet: ``{"error": "not_approved", "student_id": ...}``.
    """
    records = _load_records()

    # Find the latest plan_approval record for this student.
    approvals = [
        r for r in records
        if r["student_id"] == student_id and r["kind"] == "plan_approval"
    ]
    if not approvals:
        return {"error": "not_approved", "student_id": student_id}

    latest = max(approvals, key=lambda r: r["version"])
    questions: list[str] = json.loads(latest["content"])
    return {"student_id": student_id, "questions": questions}
