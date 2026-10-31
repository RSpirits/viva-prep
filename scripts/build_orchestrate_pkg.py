"""Build the watsonx Orchestrate import package.

Usage:
    python scripts/build_orchestrate_pkg.py [--out DIR]

The output directory (default: build/orchestrate_pkg) is deleted and
recreated with exactly the files needed for `orchestrate tools import`,
`orchestrate knowledge-bases import`, and `orchestrate agents import`.
"""

from __future__ import annotations

import argparse
import shutil
import pathlib

# ---------------------------------------------------------------------------
# Repository root is two levels above this script (scripts/build_…py)
# ---------------------------------------------------------------------------

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

COURSE_MD_NAMES = [
    "syllabus.md",
    "lecture_notes_hypothesis_testing.md",
    "learning_objectives.md",
    "rubric.md",
]

KNOWLEDGE_BASE_YAML_TEMPLATE = """\
spec_version: v1
kind: knowledge_base
name: course_knowledge
description: >
  Course materials for the viva-preparation system: syllabus, lecture notes,
  learning objectives, and rubric. Used by question_planner, briefing_writer,
  class_insights, and coordinator to ground all agent output in authoritative
  course content.

documents:
{doc_lines}
"""

PACKAGE_ENTRIES = {"viva_prep", "data", "knowledge", "agents", "requirements.txt"}

REQUIREMENTS_TXT = """\
# viva_prep tools use only the Python standard library.
# No third-party packages are required.
"""


def _copy_tree_no_pycache(src: pathlib.Path, dst: pathlib.Path) -> None:
    """Copy a directory tree, skipping __pycache__ folders."""
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(
        src,
        dst,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )


def build(out_dir: pathlib.Path) -> None:
    # -----------------------------------------------------------------------
    # 1. Clean slate
    # -----------------------------------------------------------------------
    out_dir = out_dir.resolve()
    if out_dir.exists():
        # Only ever delete a folder that holds nothing but a previous package.
        if out_dir == REPO_ROOT or out_dir in REPO_ROOT.parents:
            raise SystemExit(f"Refusing to delete {out_dir}: it contains the repository.")
        unexpected = {p.name for p in out_dir.iterdir()} - PACKAGE_ENTRIES
        if unexpected:
            raise SystemExit(
                f"Refusing to delete {out_dir}: it holds files that are not part of a package "
                f"({', '.join(sorted(unexpected))})."
            )
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    # -----------------------------------------------------------------------
    # 2. viva_prep/ package (no __pycache__)
    # -----------------------------------------------------------------------
    _copy_tree_no_pycache(REPO_ROOT / "viva_prep", out_dir / "viva_prep")

    # -----------------------------------------------------------------------
    # 3. data/submissions/*.md
    # -----------------------------------------------------------------------
    dst_submissions = out_dir / "data" / "submissions"
    dst_submissions.mkdir(parents=True)
    for md in sorted((REPO_ROOT / "data" / "submissions").glob("*.md")):
        shutil.copy2(md, dst_submissions / md.name)

    # -----------------------------------------------------------------------
    # 4. data/course/*.md
    # -----------------------------------------------------------------------
    dst_course = out_dir / "data" / "course"
    dst_course.mkdir(parents=True)
    for name in COURSE_MD_NAMES:
        shutil.copy2(REPO_ROOT / "data" / "course" / name, dst_course / name)

    # -----------------------------------------------------------------------
    # 5. requirements.txt
    # -----------------------------------------------------------------------
    (out_dir / "requirements.txt").write_text(REQUIREMENTS_TXT, encoding="utf-8")

    # -----------------------------------------------------------------------
    # 6. knowledge/ with .txt copies and course_knowledge.yaml
    # -----------------------------------------------------------------------
    dst_knowledge = out_dir / "knowledge"
    dst_knowledge.mkdir()

    txt_names: list[str] = []
    for name in COURSE_MD_NAMES:
        txt_name = pathlib.Path(name).stem + ".txt"
        txt_names.append(txt_name)
        src_md = REPO_ROOT / "data" / "course" / name
        (dst_knowledge / txt_name).write_text(
            src_md.read_text(encoding="utf-8"), encoding="utf-8"
        )

    doc_lines = "\n".join(f"  - {n}" for n in txt_names)
    kb_yaml = KNOWLEDGE_BASE_YAML_TEMPLATE.format(doc_lines=doc_lines)
    (dst_knowledge / "course_knowledge.yaml").write_text(kb_yaml, encoding="utf-8")

    # -----------------------------------------------------------------------
    # 7. agents/ — all agents/*.yaml except course_knowledge.yaml
    # -----------------------------------------------------------------------
    dst_agents = out_dir / "agents"
    dst_agents.mkdir()
    for yaml_file in sorted((REPO_ROOT / "agents").glob("*.yaml")):
        if yaml_file.name == "course_knowledge.yaml":
            continue
        shutil.copy2(yaml_file, dst_agents / yaml_file.name)

    print(f"Built Orchestrate package: {out_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default=str(REPO_ROOT / "build" / "orchestrate_pkg"),
        help="Output directory (default: build/orchestrate_pkg)",
    )
    args = parser.parse_args()
    build(pathlib.Path(args.out))


if __name__ == "__main__":
    main()
