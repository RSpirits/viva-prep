# Second fix for save_record in watsonx Orchestrate. After task 12, save_record on a read-only store returns the record with "saved": false and "reason": "store_not_writable". In Orchestrate the agents still treated that as a failed tool call: they retried once and returned "needs attention". A test build that added a "note" field to this result fixed it (the briefing writer continued and returned its JSON). Make that change in the repository.

Only change viva_prep/tools/case_store.py, tests/test_case_store.py and the "Records are not saved in Orchestrate" bullet in README.md. Do not change prompts/, agents/, data/, results/, scripts/ or any other file. Do not run the watsonx backend, and do not create, read or edit .env or any credential file.

1. viva_prep/tools/case_store.py, save_record: when the store cannot be written, also include this exact field in the returned dict:
   "note": "This environment cannot store records. This is expected and is not a failed tool call: do not retry, and continue with your task."
   Keep "saved": false and "reason": "store_not_writable". Do not add the note to a successful save. Update the docstring to match.

2. tests/test_case_store.py: on a read-only store, check that "note" equals that exact text. On a successful save, check that there is no "note" key. All other tests must still pass.

3. README.md, in the "Records are not saved in Orchestrate" bullet, replace the sentence that starts with "`save_record` then returns" with:
`save_record` then returns the record with `"saved": false`, `"reason": "store_not_writable"` and a note that this is expected and not a failed tool call. Without the note, the agents treated the unsaved record as a failed call, retried once and returned "needs attention".

When done, run from the repo root with the venv only, and show me the output:
/Users/yiwei/.venvs/viva-prep/bin/pytest -q && git status --short && git diff --stat

---

**Status:** active  **Date:** 2026-11-01

---

### 👤 User

Second fix for save_record in watsonx Orchestrate. After task 12, save_record on a read-only store returns the record with "saved": false and "reason": "store_not_writable". In Orchestrate the agents still treated that as a failed tool call: they retried once and returned "needs attention". A test build that added a "note" field to this result fixed it (the briefing writer continued and returned its JSON). Make that change in the repository.

Only change viva_prep/tools/case_store.py, tests/test_case_store.py and the "Records are not saved in Orchestrate" bullet in README.md. Do not change prompts/, agents/, data/, results/, scripts/ or any other file. Do not run the watsonx backend, and do not create, read or edit .env or any credential file.

1. viva_prep/tools/case_store.py, save_record: when the store cannot be written, also include this exact field in the returned dict:
   "note": "This environment cannot store records. This is expected and is not a failed tool call: do not retry, and continue with your task."
   Keep "saved": false and "reason": "store_not_writable". Do not add the note to a successful save. Update the docstring to match.

2. tests/test_case_store.py: on a read-only store, check that "note" equals that exact text. On a successful save, check that there is no "note" key. All other tests must still pass.

3. README.md, in the "Records are not saved in Orchestrate" bullet, replace the sentence that starts with "`save_record` then returns" with:
`save_record` then returns the record with `"saved": false`, `"reason": "store_not_writable"` and a note that this is expected and not a failed tool call. Without the note, the agents treated the unsaved record as a failed call, retried once and returned "needs attention".

When done, run from the repo root with the venv only, and show me the output:
/Users/yiwei/.venvs/viva-prep/bin/pytest -q && git status --short && git diff --stat

---

### 🤖 Assistant

> 🔧 called: read_file, read_file, read_file

Let me read the relevant files first.

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/README.md

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/tests/test_case_store.py

> 🔧 **read_file** — /Users/yiwei/Git/viva-prep/viva_prep/tools/case_store.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now I have everything I need. Let me make all three changes:

> 🔧 **apply_diff** — /Users/yiwei/Git/viva-prep/viva_prep/tools/case_store.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now update the tests:

> 🔧 **apply_diff** — /Users/yiwei/Git/viva-prep/tests/test_case_store.py

### 🤖 Assistant

> 🔧 called: apply_diff

Now update the README:

> 🔧 **apply_diff** — /Users/yiwei/Git/viva-prep/README.md

### 🤖 Assistant

> 🔧 called: execute_command

Now run the validation:

> 🔧 **execute_command** — /Users/yiwei/.venvs/viva-prep/bin/pytest -q && git status --short && git diff --stat

### 🤖 Assistant

391 passed, 2 skipped. All three files changed, nothing else touched.

Summary of what was done:

- **[`case_store.py`](viva_prep/tools/case_store.py:125)** — [`save_record()`](viva_prep/tools/case_store.py:86): the read-only branch now includes `"note": "This environment cannot store records. This is expected and is not a failed tool call: do not retry, and continue with your task."`. The successful-save branch is unchanged (no `"note"` key). Docstring updated to match.

- **[`test_case_store.py`](tests/test_case_store.py:46)** — Two new tests added:
  - [`test_successful_save_has_no_note_key`](tests/test_case_store.py:46) in `TestSaveAndGet` — asserts `"note"` is absent on success.
  - [`test_save_record_readonly_note_has_expected_text`](tests/test_case_store.py:332) in `TestReadOnlyStore` — asserts `"note"` equals the exact text.

- **[`README.md`](README.md:137)** — The "Records are not saved in Orchestrate" bullet now replaces the old sentence with the new wording describing the `"note"` field and explaining why it was added.