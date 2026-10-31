"""Watsonx Orchestrate tools for reading student submissions."""

from __future__ import annotations

import os
import pathlib

try:
    from ibm_watsonx_orchestrate.agent_builder.tools import tool
except ImportError:
    def tool(fn):  # type: ignore[misc]
        """No-op fallback when the ADK is not installed."""
        return fn


# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

def _data_dir() -> pathlib.Path:
    """Return the data directory, honouring VIVA_DATA_DIR if set."""
    env = os.environ.get("VIVA_DATA_DIR")
    if env:
        return pathlib.Path(env)
    # data/ lives two levels above this file: viva_prep/tools/submissions.py
    return pathlib.Path(__file__).parent.parent.parent / "data"


def _submissions_dir() -> pathlib.Path:
    return _data_dir() / "submissions"


def _rubric_path() -> pathlib.Path:
    return _data_dir() / "course" / "rubric.md"


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_front_matter(text: str) -> dict[str, str]:
    """Parse a minimal YAML front-matter block delimited by '---' lines.

    Only handles simple ``key: value`` pairs (no nesting, no lists).
    Returns an empty dict if no valid front-matter block is found.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fields: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields


def _body_after_front_matter(text: str) -> str:
    """Return the submission body that follows the closing '---' delimiter."""
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text
    # Skip until the closing delimiter
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            return "".join(lines[idx + 1:]).lstrip("\n")
    return text


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@tool
def list_submissions(assignment: str = "Assignment 4") -> list[dict]:
    """List every student submission for a given assignment.

    Scans data/submissions/ for Markdown files, reads their YAML front-matter,
    and returns a lightweight roster sorted by student_id.

    Args:
        assignment: Free-text assignment name used to label the result set.
            Defaults to "Assignment 4".  (Currently all files in the directory
            are returned regardless of this value; the parameter is exposed so
            the agent can pass context to downstream tools.)

    Returns:
        A list of dicts, each containing:
        - ``student_id`` (str): identifier parsed from front-matter, e.g. "S01".
        - ``first_name`` (str): student's first name parsed from front-matter.
        Sorted ascending by ``student_id``.
    """
    submissions_dir = _submissions_dir()
    results: list[dict] = []

    for md_file in sorted(submissions_dir.glob("*.md")):
        text = md_file.read_text(encoding="utf-8")
        meta = _parse_front_matter(text)
        student_id = meta.get("student_id", md_file.stem)
        first_name = meta.get("first_name", "")
        results.append({"student_id": student_id, "first_name": first_name})

    results.sort(key=lambda r: r["student_id"])
    return results


@tool
def get_submission(student_id: str) -> dict:
    """Retrieve the full submission and rubric for a single student.

    Looks up the Markdown file whose front-matter ``student_id`` matches the
    requested ID, then attaches the course rubric so the grading agent has
    everything it needs in one call.

    Args:
        student_id: The student identifier to look up, e.g. ``"S03"``.

    Returns:
        On success, a dict with:
        - ``student_id`` (str): the student's ID.
        - ``first_name`` (str): the student's first name.
        - ``assignment`` (str): assignment title from front-matter.
        - ``text`` (str): the body of the submission (front-matter stripped).
        - ``rubric`` (str): full text of data/course/rubric.md.

        On failure (ID not found), a dict with:
        - ``error`` (str): ``"not_found"``.
        - ``student_id`` (str): the requested ID echoed back.
    """
    submissions_dir = _submissions_dir()

    for md_file in submissions_dir.glob("*.md"):
        raw = md_file.read_text(encoding="utf-8")
        meta = _parse_front_matter(raw)
        if meta.get("student_id") == student_id:
            rubric = _rubric_path().read_text(encoding="utf-8")
            return {
                "student_id": student_id,
                "first_name": meta.get("first_name", ""),
                "assignment": meta.get("assignment", ""),
                "text": _body_after_front_matter(raw),
                "rubric": rubric,
            }

    return {"error": "not_found", "student_id": student_id}
