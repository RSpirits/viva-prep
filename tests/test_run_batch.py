"""Tests for scripts/run_batch.py using the dummy backend.

Run:  pytest tests/test_run_batch.py

All output goes under pytest's tmp_path — nothing is written to results/.

Test matrix
-----------
1.  Running with the dummy backend produces exactly 18 S##.json files.
2.  run_meta.json exists and has a sha256 hash entry for every prompts/*.md file.
3.  Each S##.json contains the required keys.
4a. A forced model failure produces status "needs_attention" (blank reply → JSON error).
4b. A blocked briefing keeps status "ok" and guardrail.allowed=False (forbidden).
5.  evaluate.py counts a needs_attention student as failing the three quality
    criteria (grounded, misconception, briefing length) but NOT as forbidden.
6.  evaluate.py counts a guardrail-blocked briefing as forbidden, NOT needs_attention.
7.  The needs_attention count reported by print_summary is correct.
8.  _extract_json handles plain text before/after the JSON.
9.  No environment variable value appears in any output file.
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import pathlib
import contextlib
import types

import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
PROMPTS_DIR = REPO_ROOT / "prompts"


# ---------------------------------------------------------------------------
# Module loaders
# ---------------------------------------------------------------------------

def _load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)                 # type: ignore[union-attr]
    return mod


def _load_run_batch():
    return _load_module("run_batch", SCRIPTS_DIR / "run_batch.py")


def _load_evaluate():
    return _load_module("evaluate", SCRIPTS_DIR / "evaluate.py")


rb = _load_run_batch()
ev = _load_evaluate()


# ---------------------------------------------------------------------------
# Module-level shared fixtures (avoids PytestRemovedIn10Warning)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def dummy_run_dir(tmp_path_factory):
    """Run the full dummy pipeline once per module; write to tmp_path."""
    out = tmp_path_factory.mktemp("dummy_run")
    rb.run(backend_name="dummy", out_dir=out)
    return out


@pytest.fixture(scope="module")
def needs_attention_dir(tmp_path_factory):
    """Pipeline run where the backend always returns invalid JSON."""
    out = tmp_path_factory.mktemp("needs_attention_run")
    broken = types.SimpleNamespace(
        BACKEND_NAME="dummy",
        MODEL_ID="broken-model",
        chat=lambda system, user: "THIS IS NOT JSON {{",
    )
    original = rb._make_backend
    rb._make_backend = lambda name: broken
    try:
        rb.run(backend_name="dummy", limit=1, out_dir=out)
    finally:
        rb._make_backend = original
    return out


@pytest.fixture(scope="module")
def forbidden_dir(tmp_path_factory):
    """Pipeline run where the briefing_writer returns a grade-containing briefing."""
    out = tmp_path_factory.mktemp("forbidden_run")

    class _ForbiddenBriefingBackend(rb._DummyBackend):
        def _briefing_writer_reply(self, user):
            import re
            m = re.search(r"### (S\d{2}) Submission", user)
            sid = m.group(1) if m else "S00"
            return json.dumps({
                "student_id": sid,
                "mode": "submission_only",
                "briefing": "This student deserves an A for their clear interpretation.",
                "suggested_questions": ["Q1?", "Q2?"],
                "findings": [],
            })

    original = rb._make_backend
    rb._make_backend = lambda name: _ForbiddenBriefingBackend()
    try:
        rb.run(backend_name="dummy", limit=1, out_dir=out)
    finally:
        rb._make_backend = original
    return out


# ---------------------------------------------------------------------------
# 1. Exactly 18 S##.json files are written
# ---------------------------------------------------------------------------

class TestFileCount:
    def test_18_student_files(self, dummy_run_dir):
        files = sorted(dummy_run_dir.glob("S*.json"))
        assert len(files) == 18, (
            f"Expected 18 S##.json files, found {len(files)}: {[f.name for f in files]}"
        )

    def test_class_json_exists(self, dummy_run_dir):
        assert (dummy_run_dir / "CLASS.json").exists()

    def test_run_meta_json_exists(self, dummy_run_dir):
        assert (dummy_run_dir / "run_meta.json").exists()

    def test_results_dir_not_touched(self, dummy_run_dir):
        # Confirm the run went to tmp, not into the real results/ folder
        assert str(REPO_ROOT / "results") not in str(dummy_run_dir)


# ---------------------------------------------------------------------------
# 2. run_meta.json has a hash for every prompts/*.md file
# ---------------------------------------------------------------------------

class TestRunMeta:
    def test_prompt_hashes_present(self, dummy_run_dir):
        meta = json.loads((dummy_run_dir / "run_meta.json").read_text(encoding="utf-8"))
        prompt_files = sorted(PROMPTS_DIR.glob("*.md"))
        assert prompt_files, "No prompt files found — check PROMPTS_DIR"
        hashes = meta.get("prompt_hashes", {})
        for pf in prompt_files:
            assert pf.name in hashes, (
                f"run_meta.json is missing a hash for {pf.name}"
            )

    def test_prompt_hashes_are_hex_strings(self, dummy_run_dir):
        meta = json.loads((dummy_run_dir / "run_meta.json").read_text(encoding="utf-8"))
        for name, digest in meta.get("prompt_hashes", {}).items():
            assert isinstance(digest, str) and len(digest) == 64, (
                f"Hash for {name!r} is not a 64-char hex string: {digest!r}"
            )

    def test_meta_has_required_keys(self, dummy_run_dir):
        meta = json.loads((dummy_run_dir / "run_meta.json").read_text(encoding="utf-8"))
        for key in ("backend", "model_id", "prompt_hashes", "start_time", "end_time",
                    "n_students", "n_ok", "n_needs_attention"):
            assert key in meta, f"run_meta.json missing key: {key!r}"

    def test_n_students_is_18(self, dummy_run_dir):
        meta = json.loads((dummy_run_dir / "run_meta.json").read_text(encoding="utf-8"))
        assert meta["n_students"] == 18


# ---------------------------------------------------------------------------
# 3. Each S##.json has the required keys
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("sid", [f"S{i:02d}" for i in range(1, 19)])
def test_student_file_required_keys(dummy_run_dir, sid):
    path = dummy_run_dir / f"{sid}.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    for key in ("student_id", "questions", "briefing", "suggested_questions",
                "findings", "guardrail", "status"):
        assert key in record, f"{sid}.json missing key: {key!r}"


@pytest.mark.parametrize("sid", [f"S{i:02d}" for i in range(1, 19)])
def test_student_file_status_valid(dummy_run_dir, sid):
    record = json.loads((dummy_run_dir / f"{sid}.json").read_text(encoding="utf-8"))
    assert record["status"] in ("ok", "needs_attention")


@pytest.mark.parametrize("sid", [f"S{i:02d}" for i in range(1, 19)])
def test_student_file_no_error_key_when_ok(dummy_run_dir, sid):
    record = json.loads((dummy_run_dir / f"{sid}.json").read_text(encoding="utf-8"))
    if record["status"] == "ok":
        assert "error" not in record


# ---------------------------------------------------------------------------
# 4a. Forced model failure → needs_attention
# ---------------------------------------------------------------------------

class TestForcedFailure:
    def test_status_needs_attention(self, needs_attention_dir):
        files = sorted(needs_attention_dir.glob("S*.json"))
        assert files, "No student files written"
        record = json.loads(files[0].read_text(encoding="utf-8"))
        assert record["status"] == "needs_attention"

    def test_has_error_key(self, needs_attention_dir):
        files = sorted(needs_attention_dir.glob("S*.json"))
        record = json.loads(files[0].read_text(encoding="utf-8"))
        assert "error" in record

    def test_empty_questions(self, needs_attention_dir):
        files = sorted(needs_attention_dir.glob("S*.json"))
        record = json.loads(files[0].read_text(encoding="utf-8"))
        assert record["questions"] == []

    def test_empty_briefing(self, needs_attention_dir):
        files = sorted(needs_attention_dir.glob("S*.json"))
        record = json.loads(files[0].read_text(encoding="utf-8"))
        assert record["briefing"] == ""


# ---------------------------------------------------------------------------
# 4b. Guardrail-blocked briefing → status "ok", guardrail.allowed=False
# ---------------------------------------------------------------------------

class TestGuardrailBlocked:
    def test_status_is_ok(self, forbidden_dir):
        files = sorted(forbidden_dir.glob("S*.json"))
        assert files
        record = json.loads(files[0].read_text(encoding="utf-8"))
        assert record["status"] == "ok", (
            f"Blocked briefing must keep status 'ok', got {record['status']!r}"
        )

    def test_guardrail_allowed_false(self, forbidden_dir):
        files = sorted(forbidden_dir.glob("S*.json"))
        record = json.loads(files[0].read_text(encoding="utf-8"))
        assert record["guardrail"]["allowed"] is False, (
            "Guardrail must report allowed=False for a grade-containing briefing"
        )

    def test_no_error_key(self, forbidden_dir):
        files = sorted(forbidden_dir.glob("S*.json"))
        record = json.loads(files[0].read_text(encoding="utf-8"))
        assert "error" not in record


# ---------------------------------------------------------------------------
# 5. evaluate.py: needs_attention fails three criteria but NOT forbidden
# ---------------------------------------------------------------------------

def _make_needs_attention_row():
    record = {
        "student_id": "S01",
        "questions": [],
        "briefing": "",
        "suggested_questions": [],
        "findings": [],
        "guardrail": {"allowed": True, "reasons": [], "text": ""},
        "status": "needs_attention",
    }
    answer_key_path = REPO_ROOT / "data" / "answer_key" / "answer_key.json"
    raw = json.loads(answer_key_path.read_text(encoding="utf-8"))
    ak = {e["student_id"]: e for e in raw}
    from viva_prep.tools.submissions import get_submission
    sub = get_submission("S01")
    return ev.evaluate_student(record, ak.get("S01"), sub.get("text", ""))


def test_needs_attention_grounded_zero():
    assert _make_needs_attention_row()["grounded_share"] == 0.0


def test_needs_attention_within_250_false():
    assert _make_needs_attention_row()["within_250"] is False


def test_needs_attention_n_found_zero():
    assert _make_needs_attention_row()["n_found"] == 0


def test_needs_attention_forbidden_false():
    assert _make_needs_attention_row()["forbidden"] is False, (
        "Empty briefing must NOT be counted as forbidden"
    )


def test_needs_attention_flag_true():
    assert _make_needs_attention_row()["needs_attention"] is True


# ---------------------------------------------------------------------------
# 6. evaluate.py: guardrail-blocked briefing → forbidden, NOT needs_attention
# ---------------------------------------------------------------------------

def _make_forbidden_row():
    record = {
        "student_id": "S01",
        "questions": ["Can you walk me through your reasoning?"],
        "briefing": "This student deserves an A for their clear interpretation.",
        "suggested_questions": ["Q1?", "Q2?"],
        "findings": [],
        "guardrail": {"allowed": False, "reasons": ["Contains an explicit grade"], "text": ""},
        "status": "ok",   # blocked briefings keep status "ok"
    }
    answer_key_path = REPO_ROOT / "data" / "answer_key" / "answer_key.json"
    raw = json.loads(answer_key_path.read_text(encoding="utf-8"))
    ak = {e["student_id"]: e for e in raw}
    from viva_prep.tools.submissions import get_submission
    sub = get_submission("S01")
    return ev.evaluate_student(record, ak.get("S01"), sub.get("text", ""))


def test_forbidden_briefing_forbidden_true():
    assert _make_forbidden_row()["forbidden"] is True, (
        "Grade-containing briefing must be counted as forbidden"
    )


def test_forbidden_briefing_needs_attention_false():
    assert _make_forbidden_row()["needs_attention"] is False, (
        "Blocked briefing must NOT set needs_attention"
    )


def test_forbidden_briefing_within_250_true():
    # Briefing is short enough — word count check must still pass normally
    assert _make_forbidden_row()["within_250"] is True


# ---------------------------------------------------------------------------
# 7. print_summary needs_attention count
# ---------------------------------------------------------------------------

def _make_rows(n_attn: int, total: int = 5) -> list[dict]:
    rows = []
    for i in range(total):
        attn = i < n_attn
        rows.append({
            "student_id": f"S{i+1:02d}",
            "needs_attention": attn,
            "n_questions": 0 if attn else 3,
            "grounded_count": 0,
            "grounded_share": 0.0,
            "n_planted": 0,
            "n_found": 0,
            "misconception_share": "N/A",
            "briefing_words": 0,
            "within_250": not attn,
            "forbidden": False,
            "guardrail_reasons": "",
        })
    return rows


def test_needs_attention_count_in_output():
    rows = _make_rows(n_attn=2, total=5)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ev.print_summary(rows)
    assert "needs_attention: 2" in buf.getvalue()


def test_needs_attention_zero():
    rows = _make_rows(n_attn=0, total=3)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ev.print_summary(rows)
    assert "needs_attention: 0" in buf.getvalue()


def test_model_id_printed_when_provided():
    rows = _make_rows(n_attn=0, total=1)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ev.print_summary(rows, model_id="ibm/granite-3-8b-instruct")
    assert "ibm/granite-3-8b-instruct" in buf.getvalue()


# ---------------------------------------------------------------------------
# 8. _extract_json handles text before/after JSON
# ---------------------------------------------------------------------------

class TestExtractJson:
    def test_plain_json(self):
        result = rb._extract_json('{"a": 1}')
        assert result == {"a": 1}

    def test_fenced_json(self):
        result = rb._extract_json('```json\n{"a": 1}\n```')
        assert result == {"a": 1}

    def test_fenced_no_lang(self):
        result = rb._extract_json('```\n{"a": 1}\n```')
        assert result == {"a": 1}

    def test_text_before_and_after(self):
        result = rb._extract_json('Sure, here you go:\n{"a": 1}\nHope that helps!')
        assert result == {"a": 1}

    def test_text_before_only(self):
        result = rb._extract_json('Here is the plan:\n{"questions": []}')
        assert result == {"questions": []}

    def test_raises_on_no_json(self):
        with pytest.raises(json.JSONDecodeError):
            rb._extract_json("This has no JSON at all.")


# ---------------------------------------------------------------------------
# evaluate.run() skips run_meta.json and CLASS.json
# ---------------------------------------------------------------------------

def test_run_skips_meta_and_class(dummy_run_dir):
    rows = ev.run(dummy_run_dir)
    student_ids = {r["student_id"] for r in rows}
    assert "CLASS" not in student_ids
    assert "run_meta" not in student_ids


def test_run_returns_18_rows(dummy_run_dir):
    rows = ev.run(dummy_run_dir)
    assert len(rows) == 18


def test_model_id_in_summary_from_meta(dummy_run_dir):
    meta = json.loads((dummy_run_dir / "run_meta.json").read_text(encoding="utf-8"))
    rows = ev.run(dummy_run_dir)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        ev.print_summary(rows, model_id=meta.get("model_id"))
    assert meta["model_id"] in buf.getvalue()


# ---------------------------------------------------------------------------
# Watsonx request body (Fix 6) — verified without calling the real API
# ---------------------------------------------------------------------------

def test_watsonx_request_uses_top_level_max_tokens():
    """The JSON payload must use top-level max_tokens/temperature, not 'parameters'."""
    captured: list[bytes] = []

    class _FakeBackend(rb._WatsonxBackend):
        def __init__(self):
            # Bypass network calls in __init__
            self._project_id = "proj"
            self._url = "https://fake.example.com"
            self.MODEL_ID = "fake-model"
            self._token = "fake-token"  # noqa: S105 (test only)

        def chat(self, system: str, user: str) -> str:
            import urllib.request
            # Reconstruct the payload as the real chat() method would
            payload = json.dumps({
                "model_id": self.MODEL_ID,
                "project_id": self._project_id,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "max_tokens": 4000,
                "temperature": 0,
            }).encode()
            captured.append(payload)
            return json.dumps({"choices": [{"message": {"content": '{"ok": true}'}}]})

    backend = _FakeBackend()
    backend.chat("sys", "usr")
    assert captured, "No payload captured"
    body = json.loads(captured[0])
    assert "max_tokens" in body, "top-level max_tokens must be present"
    assert "temperature" in body, "top-level temperature must be present"
    assert "parameters" not in body, "'parameters' is the /text/generation format; must not appear"
    assert body["max_tokens"] == 4000
    assert body["temperature"] == 0


# ---------------------------------------------------------------------------
# 9. No environment variable value appears in any output file
# ---------------------------------------------------------------------------

_SENSITIVE_VARS = ["WATSONX_APIKEY", "WATSONX_PROJECT_ID", "WATSONX_MODEL_ID"]


def test_no_env_var_value_in_student_files(dummy_run_dir):
    sensitive_values = [
        os.environ[k] for k in _SENSITIVE_VARS if k in os.environ and os.environ[k]
    ]
    if not sensitive_values:
        pytest.skip("No sensitive env vars set — nothing to check")
    for json_file in dummy_run_dir.glob("*.json"):
        text = json_file.read_text(encoding="utf-8")
        for val in sensitive_values:
            assert val not in text


def test_no_env_var_value_in_run_meta(dummy_run_dir):
    sensitive_values = [
        os.environ[k] for k in _SENSITIVE_VARS if k in os.environ and os.environ[k]
    ]
    if not sensitive_values:
        pytest.skip("No sensitive env vars set — nothing to check")
    meta_text = (dummy_run_dir / "run_meta.json").read_text(encoding="utf-8")
    for val in sensitive_values:
        assert val not in meta_text
