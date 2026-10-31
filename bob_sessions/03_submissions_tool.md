# Write viva_prep/tools/submissions.py with two functions that will be imported into IBM watsonx Orchestrate as Python tools.

Use the watsonx Orchestrate ADK tool decorator: `from ibm_watsonx_orchestrate.agent_builder.tools import tool` and decorate each function with `@tool`. Wrap the import in try/except ImportError and fall back to a no-op decorator, so the functions still run and test locally without the ADK installed.

1. list_submissions(assignment: str = "Assignment 4") -> list[dict]
   Returns [{"student_id", "first_name"}] for every file in data/submissions/, sorted by student_id.
2. get_submission(student_id: str) -> dict
   Returns {"student_id", "first_name", "assignment", "text", "rubric"} where rubric is the content of data/course/rubric.md.
   If the ID does not exist, return {"error": "not_found", "student_id": ...} instead of raising.

Rules:
- Every function has a full docstring (Orchestrate shows it to the agent): one-line summary, Args, Returns.
- Type hints on every parameter and return value.
- Data folder is resolved relative to this file, overridable with the environment variable VIVA_DATA_DIR.
- These tools must NEVER read data/answer_key/. Add a test that proves no function in viva_prep/tools touches that folder.
- Standard library only.

Write tests/test_submissions_tool.py covering: list returns 18 sorted entries; get returns text and rubric; unknown ID returns the error dict; answer_key is never read.

---

**Status:** active  **Date:** 2026-10-31

---

### 👤 User

Write viva_prep/tools/submissions.py with two functions that will be imported into IBM watsonx Orchestrate as Python tools.

Use the watsonx Orchestrate ADK tool decorator: `from ibm_watsonx_orchestrate.agent_builder.tools import tool` and decorate each function with `@tool`. Wrap the import in try/except ImportError and fall back to a no-op decorator, so the functions still run and test locally without the ADK installed.

1. list_submissions(assignment: str = "Assignment 4") -> list[dict]
   Returns [{"student_id", "first_name"}] for every file in data/submissions/, sorted by student_id.
2. get_submission(student_id: str) -> dict
   Returns {"student_id", "first_name", "assignment", "text", "rubric"} where rubric is the content of data/course/rubric.md.
   If the ID does not exist, return {"error": "not_found", "student_id": ...} instead of raising.

Rules:
- Every function has a full docstring (Orchestrate shows it to the agent): one-line summary, Args, Returns.
- Type hints on every parameter and return value.
- Data folder is resolved relative to this file, overridable with the environment variable VIVA_DATA_DIR.
- These tools must NEVER read data/answer_key/. Add a test that proves no function in viva_prep/tools touches that folder.
- Standard library only.

Write tests/test_submissions_tool.py covering: list returns 18 sorted entries; get returns text and rubric; unknown ID returns the error dict; answer_key is never read.

---

### 🤖 Assistant

> 🔧 called: list_files

Let me start by exploring the repository structure to understand the data layout.

> 🔧 **list_files** — /Users/yiwei/Git/viva-prep

### 🤖 Assistant

> 🔧 called: read_file, read_file, read_file



> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/pyproject.toml

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/data/submissions/S01.md

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/data/course/rubric.md

### 🤖 Assistant

> 🔧 called: read_file

Now I have a complete picture. Let me look at one more submission to confirm the front-matter format is consistent, then write both files.

> 🔧 **read_file** — student_id and first_name values in front matter

### 🤖 Assistant

> 🔧 called: update_todo_list

Good. The front matter is consistent across all files. Now I'll write both files.

> 🔧 **update_todo_list** — [-] Write viva_prep/tools/submissions.py
[ ] Write tests/test_submissions_tool.py
[ ] Run tests to validate


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — /Users/yiwei/Git/viva-prep/viva_prep/tools/submissions.py

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — [x] Write viva_prep/tools/submissions.py
[-] Write tests/test_submissions_tool.py
[ ] Run tests to validate


### 🤖 Assistant

> 🔧 called: write_file



> 🔧 **write_file** — """Tests for viva_prep/tools/submissions.py."""

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


### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — [x] Write viva_prep/tools/submissions.py
[x] Write tests/test_submissions_tool.py
[-] Run tests to validate


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — cd /Users/yiwei/Git/viva-prep && python -m pytest tests/test_submissions_tool.py -v 2>&1

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — python -m pytest tests/test_submissions_tool.py -v

---

### 👤 User

There is no `python` command on PATH here. Run Python and pytest with the project's Python 3.12 virtual environment (pytest is already installed in it), e.g.
/Users/yiwei/.venvs/viva-prep/bin/python -m pytest -q tests/test_submissions_tool.py
Do not install anything.

---

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — /Users/yiwei/.venvs/viva-prep/bin/python -m pytest -v tests/test_submissions_tool.py

### 🤖 Assistant

> 🔧 called: update_todo_list

19/19 passed in 20 ms.

> 🔧 **update_todo_list** — [x] Write viva_prep/tools/submissions.py
[x] Write tests/test_submissions_tool.py
[x] Run tests to validate


### 🤖 Assistant

All 19 tests pass. Here's a summary of what was built:

---

### [`viva_prep/tools/submissions.py`](viva_prep/tools/submissions.py)

**ADK decorator** — imported from `ibm_watsonx_orchestrate.agent_builder.tools` with a `try/except ImportError` fallback to a no-op `tool` decorator so everything runs locally without the ADK.

**Path resolution** — [`_data_dir()`](viva_prep/tools/submissions.py:14) checks `VIVA_DATA_DIR` first, then falls back to resolving `data/` relative to the source file. No hard-coded absolute paths.

**Front-matter parser** — [`_parse_front_matter()`](viva_prep/tools/submissions.py:37) is a minimal stdlib-only YAML parser for the `---`-delimited `key: value` header used in every submission file.

**`list_submissions(assignment)`** — globs `data/submissions/*.md`, reads front-matter only, returns `[{"student_id", "first_name"}, …]` sorted by `student_id`.

**`get_submission(student_id)`** — scans the same directory for a matching `student_id`, returns the full dict including stripped body text and the rubric; returns `{"error": "not_found", "student_id": …}` for unknown IDs without raising.

---

### [`tests/test_submissions_tool.py`](tests/test_submissions_tool.py)

| Class | What it covers |
|---|---|
| `TestListSubmissions` | 18 entries, sorted order, first/last IDs, required keys, keyword arg accepted |
| `TestGetSubmission` | known ID keys, echoed ID, non-empty text, front-matter stripped from body, rubric matches disk, correct first name, unknown ID error dict, no raise, exact error key set |
| `TestAnswerKeyIsolation` | static AST-free grep of all `viva_prep/tools/*.py` for the literal string `answer_key`; two `monkeypatch` guards on `builtins.open` that fail the test if either function ever opens a file inside `data/answer_key/` |

---

### 👤 User

The acceptance command fails. Running `pytest -q tests/test_submissions_tool.py` from the repository root (the venv's pytest, not `python -m pytest`) gives:
ImportError while importing test module '/Users/yiwei/Git/viva-prep/tests/test_submissions_tool.py'.
E   ModuleNotFoundError: No module named 'viva_prep'
Make plain `pytest` work from the repository root for all tests, without installing the package. Change only what is needed. To check, run:
/Users/yiwei/.venvs/viva-prep/bin/pytest -q

---

### 🤖 Assistant

> 🔧 called: read_file

The fix is a `conftest.py` at the repo root — pytest picks it up automatically and its presence adds the root to `sys.path`.

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/pyproject.toml

### 🤖 Assistant

> 🔧 called: apply_diff

The cleanest fix is `pythonpath = ["."]` in `[tool.pytest.ini_options]` — no extra files needed, and it's the standard pytest ≥ 7 mechanism.

> 🔧 **apply_diff** — /Users/yiwei/Git/viva-prep/pyproject.toml

### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — /Users/yiwei/.venvs/viva-prep/bin/pytest -q

### 🤖 Assistant

25 tests pass (the 19 new ones plus the 6 pre-existing ones in `tests/test_synthetic_data.py`).

The only change was adding two lines to [`pyproject.toml`](pyproject.toml:20):

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
```

`pythonpath` is a first-class pytest ≥ 7 setting that prepends the listed directories to `sys.path` before any test collection begins — no `conftest.py`, no `pip install -e .`, no `PYTHONPATH` export needed.