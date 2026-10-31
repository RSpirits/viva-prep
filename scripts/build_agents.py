"""Build agents/<name>.yaml from prompts/<name>.md.

Reads every Markdown file under prompts/ and writes a watsonx Orchestrate
ADK native-agent YAML file under agents/.  The ``instructions`` field is set
to the exact text of the matching prompts file.

ADK native-agent YAML schema reference:
  https://www.ibm.com/docs/en/watsonx/watson-orchestrate (agent_definition)

Fields used:
  spec_version    – "v1" (ADK current stable)
  kind            – "native"  (managed LLM agent, not a flow or tool)
  name            – agent identifier (filename stem, underscores)
  description     – one-line summary for the Orchestrate catalog
  instructions    – exact text of the matching prompts/*.md file
  tools           – list of tool identifiers the agent may call
  collaborators   – list of other agent names this agent may invoke
  knowledge_base  – list of knowledge-base names (ADK field name)

  # TODO: add an ``llm`` field once the exact model ID is confirmed in the
  #        Orchestrate instance.  The Lab administrator has locked the model
  #        to GPT-OSS 120B; confirm the exact llm id string in the instance
  #        settings before setting this field.  Omitting it uses the
  #        workspace default.
"""

from __future__ import annotations

import pathlib
import textwrap

# ---------------------------------------------------------------------------
# Agent metadata table
# ---------------------------------------------------------------------------
# Each entry defines everything except ``instructions``, which is read from
# the matching prompts file.

AGENTS: list[dict] = [
    {
        "name": "coordinator",
        "description": (
            "Manages a viva-preparation round for the instructor: "
            "builds question plans, collects approvals, and dispatches "
            "briefings and class insights."
        ),
        "tools": [
            "list_submissions",
            "get_round_status",
            "get_records",
            "save_record",
            "check_output",
        ],
        "collaborators": [
            "question_planner",
            "briefing_writer",
            "class_insights",
        ],
        "knowledge_base": ["course_knowledge"],
    },
    {
        "name": "question_planner",
        "description": (
            "Reads a student submission and rubric and returns a JSON "
            "question plan (3–5 open questions, each anchored to a verbatim "
            "quote from the submission) for instructor review."
        ),
        "tools": [
            "get_submission",
            "save_record",
            "check_output",
        ],
        "collaborators": [],
        "knowledge_base": ["course_knowledge"],
    },
    {
        "name": "practice_partner",
        "description": (
            "Student-facing conversational agent that asks approved viva "
            "questions one at a time, saves the transcript, and returns a "
            "neutral summary of what the student explained."
        ),
        "tools": [
            "get_approved_questions",
            "save_record",
            "check_output",
        ],
        "collaborators": [],
        "knowledge_base": [],
    },
    {
        "name": "briefing_writer",
        "description": (
            "Produces a structured JSON briefing for the instructor, "
            "covering what the student explained well and where the "
            "explanation broke down, with two suggested follow-up questions."
        ),
        "tools": [
            "get_submission",
            "get_records",
            "save_record",
            "check_output",
        ],
        "collaborators": [],
        "knowledge_base": ["course_knowledge"],
    },
    {
        "name": "class_insights",
        "description": (
            "Reads all student briefings for the round and returns a "
            "≤300-word plain-text summary of the 3–5 most common gaps, "
            "each with student count and rubric criterion."
        ),
        "tools": [
            "get_round_status",
            "get_records",
            "save_record",
            "check_output",
        ],
        "collaborators": [],
        "knowledge_base": ["course_knowledge"],
    },
]


# ---------------------------------------------------------------------------
# YAML helpers (stdlib only — no PyYAML dependency)
# ---------------------------------------------------------------------------

def _scalar(value: str) -> str:
    """Return a YAML literal-block scalar (|) for multi-line strings."""
    # Indent each line by 2 spaces; the leading '|\n' tells YAML parsers
    # this is a literal block with a single trailing newline.
    indented = textwrap.indent(value.rstrip("\n") + "\n", "  ")
    return "|\n" + indented


def _list_items(items: list[str], indent: int = 2) -> str:
    pad = " " * indent
    return "".join(f"{pad}- {item}\n" for item in items)


def _render_agent(meta: dict, instructions: str) -> str:
    """Render one agent definition as a YAML string."""
    lines: list[str] = []
    lines.append("spec_version: v1")
    lines.append("kind: native")
    lines.append(f"name: {meta['name']}")
    # TODO: add the llm field here once the exact id is confirmed in the Lab
    #   instance (the administrator locks it to GPT-OSS 120B; the ADK docs show
    #   "groq/openai/gpt-oss-120b", which must be checked before use).
    lines.append(f"description: {_quote_if_needed(meta['description'])}")
    lines.append(f"instructions: {_scalar(instructions)}")

    if meta["tools"]:
        lines.append("tools:")
        lines.append(_list_items(meta["tools"]).rstrip("\n"))
    else:
        lines.append("tools: []")

    if meta["collaborators"]:
        lines.append("collaborators:")
        lines.append(_list_items(meta["collaborators"]).rstrip("\n"))
    else:
        lines.append("collaborators: []")

    if meta["knowledge_base"]:
        lines.append("knowledge_base:")
        lines.append(_list_items(meta["knowledge_base"]).rstrip("\n"))
    else:
        lines.append("knowledge_base: []")

    return "\n".join(lines) + "\n"


def _quote_if_needed(value: str) -> str:
    """Wrap a YAML scalar in double quotes if it contains special characters."""
    needs_quoting = any(c in value for c in ":#{}[]|>&*!,")
    if needs_quoting:
        escaped = value.replace('"', '\\"')
        return f'"{escaped}"'
    return value


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build(
    prompts_dir: pathlib.Path,
    agents_dir: pathlib.Path,
) -> list[str]:
    """Build YAML files from prompts and return the list of written paths."""
    agents_dir.mkdir(parents=True, exist_ok=True)

    written: list[str] = []
    agent_index = {a["name"]: a for a in AGENTS}

    for md_path in sorted(prompts_dir.glob("*.md")):
        name = md_path.stem
        if name not in agent_index:
            print(f"  skip {md_path.name} — no entry in AGENTS table")
            continue

        instructions = md_path.read_text(encoding="utf-8")
        yaml_text = _render_agent(agent_index[name], instructions)
        out_path = agents_dir / f"{name}.yaml"
        out_path.write_text(yaml_text, encoding="utf-8")
        written.append(str(out_path))
        print(f"  wrote {out_path}")

    return written


if __name__ == "__main__":
    repo_root = pathlib.Path(__file__).parent.parent
    written = build(
        prompts_dir=repo_root / "prompts",
        agents_dir=repo_root / "agents",
    )
    print(f"\nDone — {len(written)} agent file(s) written.")
