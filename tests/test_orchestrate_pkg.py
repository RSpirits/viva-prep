"""Tests for the watsonx Orchestrate import package (built by build_orchestrate_pkg.py).

All output is written inside pytest's tmp_path; nothing is written outside it.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys

import pytest

# ---------------------------------------------------------------------------
# Repository root (two levels above this file)
# ---------------------------------------------------------------------------

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_AGENTS = REPO_ROOT / "agents"
IMPORT_SCRIPT = REPO_ROOT / "scripts" / "import_orchestrate.sh"

COURSE_MD_NAMES = [
    "syllabus.md",
    "lecture_notes_hypothesis_testing.md",
    "learning_objectives.md",
    "rubric.md",
]

# The first few bytes of the answer_key file are distinctive enough to test
# that no file inside the package contains them.
ANSWER_KEY_PATH = REPO_ROOT / "data" / "answer_key" / "answer_key.json"
ANSWER_KEY_SNIPPET = '"misconceptions"'  # appears only in the answer key


# ---------------------------------------------------------------------------
# Fixture: build the package once into tmp_path
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def pkg_dir(tmp_path_factory):
    out = tmp_path_factory.mktemp("orchestrate_pkg")
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "build_orchestrate_pkg.py"),
         "--out", str(out)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    return out


# ---------------------------------------------------------------------------
# 1. No answer_key material
# ---------------------------------------------------------------------------

class TestNoAnswerKey:
    def test_no_answer_key_folder(self, pkg_dir):
        assert not (pkg_dir / "data" / "answer_key").exists()

    def test_no_file_contains_answer_key_path_string(self, pkg_dir):
        for f in pkg_dir.rglob("*"):
            if f.is_file():
                try:
                    text = f.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                assert "answer_key" not in text, (
                    f"{f.relative_to(pkg_dir)} contains 'answer_key'"
                )

    def test_no_file_contains_answer_key_content(self, pkg_dir):
        for f in pkg_dir.rglob("*"):
            if f.is_file():
                try:
                    text = f.read_text(encoding="utf-8", errors="replace")
                except Exception:
                    continue
                assert ANSWER_KEY_SNIPPET not in text, (
                    f"{f.relative_to(pkg_dir)} contains answer-key content"
                )


# ---------------------------------------------------------------------------
# 2. Allowed top-level entries only
# ---------------------------------------------------------------------------

class TestTopLevelLayout:
    def test_only_allowed_top_level_entries(self, pkg_dir):
        allowed = {"viva_prep", "data", "knowledge", "agents", "requirements.txt"}
        actual = {p.name for p in pkg_dir.iterdir()}
        assert actual == allowed

    def test_data_contains_only_course_and_submissions(self, pkg_dir):
        data_children = {p.name for p in (pkg_dir / "data").iterdir()}
        assert data_children == {"course", "submissions"}


# ---------------------------------------------------------------------------
# 3. Tools work from within the package folder
# ---------------------------------------------------------------------------

class TestToolsRunInPackage:
    def _run(self, pkg_dir, code: str) -> str:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(pkg_dir)
        env.pop("VIVA_DATA_DIR", None)
        env.pop("VIVA_STORE_PATH", None)
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=str(pkg_dir),
            env=env,
        )
        assert result.returncode == 0, result.stderr
        return result.stdout.strip()

    def test_list_submissions_returns_18_students(self, pkg_dir):
        out = self._run(
            pkg_dir,
            "import json; from viva_prep.tools.submissions import list_submissions; "
            "print(json.dumps(list_submissions()))",
        )
        data = json.loads(out)
        assert len(data) == 18

    def test_get_submission_returns_text_and_rubric(self, pkg_dir):
        out = self._run(
            pkg_dir,
            "import json; from viva_prep.tools.submissions import get_submission; "
            "print(json.dumps(get_submission('S01')))",
        )
        data = json.loads(out)
        assert data.get("student_id") == "S01"
        assert len(data.get("text", "")) > 0, "submission text should be non-empty"
        assert len(data.get("rubric", "")) > 0, "rubric should be non-empty"


# ---------------------------------------------------------------------------
# 4. Knowledge base YAML and .txt files
# ---------------------------------------------------------------------------

class TestKnowledgeBase:
    def test_course_knowledge_yaml_has_kind_knowledge_base(self, pkg_dir):
        import yaml  # type: ignore[import]
        kb_yaml = (pkg_dir / "knowledge" / "course_knowledge.yaml").read_text(
            encoding="utf-8"
        )
        data = yaml.safe_load(kb_yaml)
        assert data["kind"] == "knowledge_base"

    def test_course_knowledge_yaml_lists_four_txt_files(self, pkg_dir):
        import yaml  # type: ignore[import]
        kb_yaml = (pkg_dir / "knowledge" / "course_knowledge.yaml").read_text(
            encoding="utf-8"
        )
        data = yaml.safe_load(kb_yaml)
        docs = data["documents"]
        assert len(docs) == 4
        for doc in docs:
            assert doc.endswith(".txt"), f"Expected .txt file, got: {doc}"
            # bare file name — no path separator
            assert "/" not in doc and "\\" not in doc

    def test_txt_files_exist(self, pkg_dir):
        for md_name in COURSE_MD_NAMES:
            txt_name = pathlib.Path(md_name).stem + ".txt"
            assert (pkg_dir / "knowledge" / txt_name).exists(), (
                f"Missing {txt_name} in knowledge/"
            )

    def test_txt_content_equals_md_source(self, pkg_dir):
        for md_name in COURSE_MD_NAMES:
            txt_name = pathlib.Path(md_name).stem + ".txt"
            md_text = (REPO_ROOT / "data" / "course" / md_name).read_text(
                encoding="utf-8"
            )
            txt_text = (pkg_dir / "knowledge" / txt_name).read_text(encoding="utf-8")
            assert txt_text == md_text, (
                f"{txt_name} content differs from {md_name}"
            )


# ---------------------------------------------------------------------------
# 5. Agent YAML files are identical to repository originals
# ---------------------------------------------------------------------------

class TestAgentYamls:
    def test_agent_yamls_identical_to_repo(self, pkg_dir):
        pkg_agents = pkg_dir / "agents"
        repo_yamls = {
            f.name: f
            for f in REPO_AGENTS.glob("*.yaml")
            if f.name != "course_knowledge.yaml"
        }
        for name, repo_file in repo_yamls.items():
            pkg_file = pkg_agents / name
            assert pkg_file.exists(), f"Missing agents/{name} in package"
            assert pkg_file.read_bytes() == repo_file.read_bytes(), (
                f"agents/{name} differs from repository original"
            )

    def test_course_knowledge_yaml_not_in_agents(self, pkg_dir):
        assert not (pkg_dir / "agents" / "course_knowledge.yaml").exists()


# ---------------------------------------------------------------------------
# 6. import_orchestrate.sh content checks
# ---------------------------------------------------------------------------

class TestImportScript:
    @pytest.fixture(scope="class")
    @classmethod
    def script_text(cls):
        return IMPORT_SCRIPT.read_text(encoding="utf-8")

    def test_names_submissions_tool_file(self, script_text):
        assert "submissions.py" in script_text

    def test_names_case_store_tool_file(self, script_text):
        assert "case_store.py" in script_text

    def test_names_guardrail_tool_file(self, script_text):
        assert "guardrail.py" in script_text

    def test_names_all_five_agent_files(self, script_text):
        for name in [
            "question_planner.yaml",
            "practice_partner.yaml",
            "briefing_writer.yaml",
            "class_insights.yaml",
            "coordinator.yaml",
        ]:
            assert name in script_text, f"Script does not mention {name}"

    def test_coordinator_imported_last(self, script_text):
        # coordinator.yaml must appear after all other agent yaml files
        pos_coordinator = script_text.rfind("coordinator.yaml")
        for name in [
            "question_planner.yaml",
            "practice_partner.yaml",
            "briefing_writer.yaml",
            "class_insights.yaml",
        ]:
            pos = script_text.rfind(name)
            assert pos < pos_coordinator, (
                f"{name} appears after coordinator.yaml"
            )

    def test_no_credentials_in_script(self, script_text):
        lower = script_text.lower()
        for forbidden in ("apikey", "api_key", "password"):
            assert forbidden not in lower, (
                f"Script contains forbidden credential token: {forbidden!r}"
            )


# ---------------------------------------------------------------------------
# 7. DRY_RUN=1 execution: exits 0, prints commands, needs no orchestrate binary
# ---------------------------------------------------------------------------

class TestDryRun:
    def test_dry_run_exits_zero(self, tmp_path):
        env = os.environ.copy()
        env["DRY_RUN"] = "1"
        env["PKG_DIR"] = str(tmp_path / "pkg")
        env["PYTHON"] = sys.executable
        result = subprocess.run(
            ["bash", str(IMPORT_SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(tmp_path),
        )
        assert result.returncode == 0, (
            f"DRY_RUN=1 exited {result.returncode}:\n{result.stderr}"
        )

    def test_dry_run_prints_tool_import_commands(self, tmp_path):
        env = os.environ.copy()
        env["DRY_RUN"] = "1"
        env["PKG_DIR"] = str(tmp_path / "pkg")
        env["PYTHON"] = sys.executable
        result = subprocess.run(
            ["bash", str(IMPORT_SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(tmp_path),
        )
        out = result.stdout
        for fname in ("submissions.py", "case_store.py", "guardrail.py"):
            assert fname in out, f"DRY_RUN output missing tool file: {fname}"

    def test_dry_run_prints_knowledge_base_import(self, tmp_path):
        env = os.environ.copy()
        env["DRY_RUN"] = "1"
        env["PKG_DIR"] = str(tmp_path / "pkg")
        env["PYTHON"] = sys.executable
        result = subprocess.run(
            ["bash", str(IMPORT_SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(tmp_path),
        )
        assert "knowledge-bases import" in result.stdout

    def test_dry_run_prints_agent_imports_in_order(self, tmp_path):
        env = os.environ.copy()
        env["DRY_RUN"] = "1"
        env["PKG_DIR"] = str(tmp_path / "pkg")
        env["PYTHON"] = sys.executable
        result = subprocess.run(
            ["bash", str(IMPORT_SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(tmp_path),
        )
        out = result.stdout
        agent_names = [
            "question_planner.yaml",
            "practice_partner.yaml",
            "briefing_writer.yaml",
            "class_insights.yaml",
            "coordinator.yaml",
        ]
        positions = [out.find(n) for n in agent_names]
        assert all(p != -1 for p in positions), (
            f"Not all agent files appear in DRY_RUN output: {list(zip(agent_names, positions))}"
        )
        assert positions == sorted(positions), (
            "Agent import order in DRY_RUN output is wrong; coordinator must be last"
        )

    def test_dry_run_does_not_require_orchestrate_binary(self, tmp_path):
        """orchestrate command must never be invoked under DRY_RUN=1."""
        # Provide a PATH that has no orchestrate binary; script must still exit 0.
        env = os.environ.copy()
        env["DRY_RUN"] = "1"
        env["PKG_DIR"] = str(tmp_path / "pkg")
        env["PYTHON"] = sys.executable
        # Strip PATH to just bare essentials (bash builtins + python + system utils).
        env["PATH"] = "/usr/bin:/bin"
        result = subprocess.run(
            ["bash", str(IMPORT_SCRIPT)],
            capture_output=True,
            text=True,
            env=env,
            cwd=str(tmp_path),
        )
        assert result.returncode == 0, (
            f"Script failed without orchestrate on PATH:\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


# ---------------------------------------------------------------------------
# 8. The build script only deletes a folder that holds a previous package
# ---------------------------------------------------------------------------

class TestBuildRefusesForeignFolder:
    def _build(self, out):
        return subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / "build_orchestrate_pkg.py"),
             "--out", str(out)],
            capture_output=True,
            text=True,
        )

    def test_refuses_folder_with_other_files(self, tmp_path):
        keep = tmp_path / "notes.txt"
        keep.write_text("keep me", encoding="utf-8")
        result = self._build(tmp_path)
        assert result.returncode != 0
        assert keep.read_text(encoding="utf-8") == "keep me"

    def test_rebuilds_over_previous_package(self, tmp_path):
        out = tmp_path / "pkg"
        assert self._build(out).returncode == 0
        assert self._build(out).returncode == 0
        assert (out / "requirements.txt").exists()
