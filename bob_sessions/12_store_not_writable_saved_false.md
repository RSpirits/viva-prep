# Fix after the first run in watsonx Orchestrate. In Orchestrate, Python tools run on a read-only file system, so save_record returned {"error": "store_not_writable"}. The agents follow the shared rule "if a tool call fails twice, return needs attention", so question_planner threw away a question plan it had already built and checked. An unwritable store must not look like a failed tool call, but the result must still say clearly that nothing was saved.

Only change viva_prep/tools/case_store.py, tests/test_case_store.py and the "Records may not persist in Orchestrate" bullet in README.md. Do not change prompts/, agents/, data/, results/, scripts/ or any other file. Do not run the watsonx backend, and do not create, read or edit .env or any credential file.

1. viva_prep/tools/case_store.py, save_record: when the store cannot be written, return the record dict that would have been saved (student_id, kind, content, version, saved_at) plus "saved": false and "reason": "store_not_writable". There must be no "error" key in this case. When the write succeeds, return the record with "saved": true. Keep {"error": "unknown_kind"} unchanged for an unknown kind. Update the docstring to match. Do not add any fallback location such as a temporary directory.

2. tests/test_case_store.py: replace the test that expects {"error": "store_not_writable"} with tests that check, on a read-only store: no "error" key, "saved" is False, "reason" is "store_not_writable", and student_id, kind and content are returned. Add a test that a successful save has "saved": True. Update any other test that compares the whole returned record. All other tests must still pass.

3. README.md, the "Records may not persist in Orchestrate" bullet under Known limitations: replace it with this text:
- **Records are not saved in Orchestrate.** Python tools in Orchestrate run on a read-only file system (confirmed in the first Orchestrate run). `save_record` then returns the record with `"saved": false` and `"reason": "store_not_writable"` instead of an error, so the agents can continue. The demo therefore runs in a single conversation, with the approved questions passed in that conversation. Practice Partner's separation from briefings then rests only on its instructions, no longer on which tools it can reach.

When done, run from the repo root with the venv only, and show me the output:
/Users/yiwei/.venvs/viva-prep/bin/pytest -q && git status --short && git diff --stat

---

**Status:** active  **Date:** 2026-11-01

---

### 👤 User

Fix after the first run in watsonx Orchestrate. In Orchestrate, Python tools run on a read-only file system, so save_record returned {"error": "store_not_writable"}. The agents follow the shared rule "if a tool call fails twice, return needs attention", so question_planner threw away a question plan it had already built and checked. An unwritable store must not look like a failed tool call, but the result must still say clearly that nothing was saved.

Only change viva_prep/tools/case_store.py, tests/test_case_store.py and the "Records may not persist in Orchestrate" bullet in README.md. Do not change prompts/, agents/, data/, results/, scripts/ or any other file. Do not run the watsonx backend, and do not create, read or edit .env or any credential file.

1. viva_prep/tools/case_store.py, save_record: when the store cannot be written, return the record dict that would have been saved (student_id, kind, content, version, saved_at) plus "saved": false and "reason": "store_not_writable". There must be no "error" key in this case. When the write succeeds, return the record with "saved": true. Keep {"error": "unknown_kind"} unchanged for an unknown kind. Update the docstring to match. Do not add any fallback location such as a temporary directory.

2. tests/test_case_store.py: replace the test that expects {"error": "store_not_writable"} with tests that check, on a read-only store: no "error" key, "saved" is False, "reason" is "store_not_writable", and student_id, kind and content are returned. Add a test that a successful save has "saved": True. Update any other test that compares the whole returned record. All other tests must still pass.

3. README.md, the "Records may not persist in Orchestrate" bullet under Known limitations: replace it with this text:
- **Records are not saved in Orchestrate.** Python tools in Orchestrate run on a read-only file system (confirmed in the first Orchestrate run). `save_record` then returns the record with `"saved": false` and `"reason": "store_not_writable"` instead of an error, so the agents can continue. The demo therefore runs in a single conversation, with the approved questions passed in that conversation. Practice Partner's separation from briefings then rests only on its instructions, no longer on which tools it can reach.

When done, run from the repo root with the venv only, and show me the output:
/Users/yiwei/.venvs/viva-prep/bin/pytest -q && git status --short && git diff --stat

---

### 🤖 Assistant

> 🔧 called: update_todo_list



> 🔧 **update_todo_list** — 
[-] Read case_store.py and the current test file to understand existing code
[ ] Update save_record in viva_prep/tools/case_store.py
[ ] Update tests/test_case_store.py
[ ] Update README.md bullet
[ ] Run pytest and git status/diff


### 🤖 Assistant

> 🔧 called: read_file, read_file, grep



> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/tests/test_case_store.py

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/viva_prep/tools/case_store.py

> 🔧 **grep** — Records may not persist in Orchestrate

### 🤖 Assistant

> 🔧 called: update_todo_list

Now I have a clear picture. Let me make all three changes:

> 🔧 **update_todo_list** — 
[x] Read case_store.py and the current test file to understand existing code
[-] Update save_record in viva_prep/tools/case_store.py
[ ] Update tests/test_case_store.py
[ ] Update README.md bullet
[ ] Run pytest and git status/diff


### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — /Users/yiwei/Git/viva-prep/viva_prep/tools/case_store.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now the `save_record` return shape changed — tests that compare the whole returned dict need updating. Let me update the test file:

> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:39
-------
    def test_save_returns_record_with_expected_keys(self):
        record = save_record("S01", "transcript", "Hello world")
        assert set(record.keys()) == {"student_id", "kind", "content", "version", "saved_at"}
=======
    def test_save_returns_record_with_expected_keys(self):
        record = save_record("S01", "transcript", "Hello world")
        assert set(record.keys()) == {"student_id", "kind", "content", "version", "saved_at", "saved"}

    def test_successful_save_has_saved_true(self):
        record = save_record("S01", "transcript", "Hello world")
        assert record["saved"] is True
>>>>>>> REPLACE

<<<<<<< SEARCH
:start_line:316
-------
    def test_save_record_returns_error_dict_not_writable(self, readonly_store):
        result = save_record("S01", "transcript", "hello")
        assert result == {"error": "store_not_writable"}

    def test_save_record_does_not_raise(self, readonly_store):
=======
    def test_save_record_readonly_has_no_error_key(self, readonly_store):
        result = save_record("S01", "transcript", "hello")
        assert "error" not in result

    def test_save_record_readonly_saved_is_false(self, readonly_store):
        result = save_record("S01", "transcript", "hello")
        assert result["saved"] is False

    def test_save_record_readonly_reason_is_store_not_writable(self, readonly_store):
        result = save_record("S01", "transcript", "hello")
        assert result["reason"] == "store_not_writable"

    def test_save_record_readonly_returns_student_id_kind_content(self, readonly_store):
        result = save_record("S01", "transcript", "hello")
        assert result["student_id"] == "S01"
        assert result["kind"] == "transcript"
        assert result["content"] == "hello"

    def test_save_record_does_not_raise(self, readonly_store):
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: read_file

Now update the README bullet:

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/README.md

### 🤖 Assistant

> 🔧 called: apply_diff



> 🔧 **apply_diff** — <<<<<<< SEARCH
:start_line:137
-------
- **Records may not persist in Orchestrate.** According to the ADK documentation, Python tools in Orchestrate run on a read-only file system. In that case `save_record` returns `{"error": "store_not_writable"}` instead of failing. The fallback is to run the demo in a single conversation, with the approved questions passed in that conversation. Practice Partner's separation from briefings then rests only on its instructions, no longer on which tools it can reach.
=======
- **Records are not saved in Orchestrate.** Python tools in Orchestrate run on a read-only file system (confirmed in the first Orchestrate run). `save_record` then returns the record with `"saved": false` and `"reason": "store_not_writable"` instead of an error, so the agents can continue. The demo therefore runs in a single conversation, with the approved questions passed in that conversation. Practice Partner's separation from briefings then rests only on its instructions, no longer on which tools it can reach.
>>>>>>> REPLACE


### 🤖 Assistant

> 🔧 called: update_todo_list

Now run the tests and git status/diff:

> 🔧 **update_todo_list** — 
[x] Read case_store.py and the current test file to understand existing code
[x] Update save_record in viva_prep/tools/case_store.py
[x] Update tests/test_case_store.py
[x] Update README.md bullet
[-] Run pytest and git status/diff


### 🤖 Assistant

> 🔧 called: execute_command



> 🔧 **execute_command** — /Users/yiwei/.venvs/viva-prep/bin/pytest -q && git status --short && git diff --stat

### 🤖 Assistant

389 passed, 2 skipped. Here's what changed:

---

**[`viva_prep/tools/case_store.py`](viva_prep/tools/case_store.py)**

[`save_record`](viva_prep/tools/case_store.py:86) now always builds the full record dict before attempting the write. On success it returns `{…, "saved": True}`; when the file system is unwritable it returns `{…, "saved": False, "reason": "store_not_writable"}` — no `"error"` key, so the agent framework's failure-detection logic never sees it as a failed tool call. The `{"error": "unknown_kind"}` path is untouched.

---

**[`tests/test_case_store.py`](tests/test_case_store.py)**

- `test_save_returns_record_with_expected_keys` — updated expected key set to include `"saved"`.
- `test_successful_save_has_saved_true` — new test verifying the happy path.
- `test_save_record_returns_error_dict_not_writable` — replaced with four targeted assertions on a read-only store: no `"error"` key, `"saved"` is `False`, `"reason"` is `"store_not_writable"`, and `student_id`/`kind`/`content` are returned.

---

**[`README.md`](README.md:137)**

The "Known limitations" bullet is replaced verbatim with the text you specified, noting the Orchestrate run confirmed the read-only filesystem and that `save_record` now returns `"saved": false` rather than an error.