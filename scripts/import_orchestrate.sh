#!/usr/bin/env bash
# import_orchestrate.sh — Build the Orchestrate package and import all assets.
#
# Prerequisites:
#   • The Orchestrate CLI is installed and activated:
#       orchestrate env add -n <name> -u <service instance URL> \
#         --type ibm_iam --activate
#     (The CLI prompts for the API key interactively; never pass it here.)
#   • The project virtual environment has been activated or PYTHON is set.
#
# Usage:
#   bash scripts/import_orchestrate.sh           # build and import
#   DRY_RUN=1 bash scripts/import_orchestrate.sh # build and print commands only

set -euo pipefail

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PYTHON="${PYTHON:-python3}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PKG_DIR="${PKG_DIR:-$REPO_ROOT/build/orchestrate_pkg}"
DRY_RUN="${DRY_RUN:-0}"

# ---------------------------------------------------------------------------
# Helper: print a command, then run it unless DRY_RUN=1
# ---------------------------------------------------------------------------

run() {
    echo "+ $*"
    if [ "$DRY_RUN" != "1" ]; then
        "$@"
    fi
}

# ---------------------------------------------------------------------------
# Step 1: Build the package
# ---------------------------------------------------------------------------

echo "==> Building Orchestrate package..."
"$PYTHON" "$SCRIPT_DIR/build_orchestrate_pkg.py" --out "$PKG_DIR"

# ---------------------------------------------------------------------------
# Step 2: Import tools
#   Each tool file is imported with the package root so that relative imports
#   inside viva_prep/ resolve correctly.
# ---------------------------------------------------------------------------

echo ""
echo "==> Importing tools..."

run orchestrate tools import \
    -k python \
    -p "$PKG_DIR" \
    -f "$PKG_DIR/viva_prep/tools/submissions.py" \
    -r "$PKG_DIR/requirements.txt"

run orchestrate tools import \
    -k python \
    -p "$PKG_DIR" \
    -f "$PKG_DIR/viva_prep/tools/case_store.py" \
    -r "$PKG_DIR/requirements.txt"

run orchestrate tools import \
    -k python \
    -p "$PKG_DIR" \
    -f "$PKG_DIR/viva_prep/tools/guardrail.py" \
    -r "$PKG_DIR/requirements.txt"

# ---------------------------------------------------------------------------
# Step 3: Import knowledge base
#   Run from inside knowledge/ so the bare file names in course_knowledge.yaml
#   resolve correctly regardless of whether the ADK resolves paths relative to
#   the YAML file or the current directory.
# ---------------------------------------------------------------------------

echo ""
echo "==> Importing knowledge base..."

run bash -c "cd '$PKG_DIR/knowledge' && orchestrate knowledge-bases import -f course_knowledge.yaml"

# ---------------------------------------------------------------------------
# Step 4: Import agents (collaborators before coordinator)
# ---------------------------------------------------------------------------

echo ""
echo "==> Importing agents..."

run orchestrate agents import -f "$PKG_DIR/agents/question_planner.yaml"
run orchestrate agents import -f "$PKG_DIR/agents/practice_partner.yaml"
run orchestrate agents import -f "$PKG_DIR/agents/briefing_writer.yaml"
run orchestrate agents import -f "$PKG_DIR/agents/class_insights.yaml"

# coordinator references the four agents above as collaborators, so it is
# imported last.
run orchestrate agents import -f "$PKG_DIR/agents/coordinator.yaml"

echo ""
if [ "$DRY_RUN" = "1" ]; then
    echo "==> Dry run complete. No commands were executed."
else
    echo "==> Import complete."
fi
