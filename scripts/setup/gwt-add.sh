#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/setup/gwt-add.sh [--no-open] <branch-name> [git worktree add flags]
# Creates a git worktree at <main-checkout>/.claude/worktrees/<branch> (slashes
# in <branch> flattened to dashes, so feature/foo lands at feature-foo), copies
# env files, runs pnpm install, and opens the worktree in Zed. The in-repo
# location is the harness's default worktree home, so EnterWorktree needs no
# extra approval prompt; .gitignore and .prettierignore both exclude it.
# --no-open skips the editor launch (scripted/AI invocations, e.g. implement-spec).

no_open=0
if [[ "${1:-}" == "--no-open" ]]; then
  no_open=1
  shift
fi

if [[ $# -lt 1 || -z "${1:-}" ]]; then
  echo "Usage: $(basename "$0") [--no-open] <branch-name> [git worktree add flags]" >&2
  exit 1
fi

branch="$1"
shift

# The main checkout is always the first entry in `git worktree list`;
# rev-parse --show-toplevel would return the linked worktree's own path when
# invoked from inside one, nesting the new worktree under a sibling worktree.
# `|| true` is load-bearing: outside a repo, git fails and `pipefail` propagates
# that through the whole pipeline, so `set -e` would kill the script with a bare
# exit 128 and the friendly branch below would never run. Do not remove it.
main_root=$(git worktree list --porcelain 2>/dev/null | head -1 | sed 's/^worktree //') || true
if [[ -z "$main_root" ]]; then
  echo "Error: not inside a git repository" >&2
  exit 1
fi

# Flatten branch slashes to dashes so any branch convention (feature/foo,
# user/eng-123) yields one predictable directory level under the base.
target="$main_root/.claude/worktrees/${branch//\//-}"

# Re-running this script is the documented recovery from a failed dependency
# install, so creation is idempotent: a worktree already at $target is adopted
# and the run falls through to the install rather than dying on git's
# "'<target>' already exists". Without this, the retry the failure message asks
# for exits 128 and the half-built worktree can only be cleaned up by hand.
if git worktree list --porcelain | grep -qxF "worktree $target"; then
  echo "Worktree already exists at $target — reusing it."
  echo "  (re-running the dependency install; nothing is recreated)"
elif [[ -e "$target" ]]; then
  echo "Error: $target exists but is not a registered git worktree." >&2
  echo "  Remove it, or pick another branch name." >&2
  exit 1
else
  echo "Creating worktree at $target for branch $branch"
  if git rev-parse --verify --quiet "refs/heads/$branch" >/dev/null; then
    echo "Branch $branch already exists — attaching worktree to it."
    git worktree add "$target" "$branch" "$@"
  else
    git worktree add "$target" -b "$branch" "$@"
  fi
fi

echo "Copying local files..."
if [[ -f "$main_root/.env.local" ]]; then
  cp "$main_root/.env.local" "$target/.env.local"
else
  echo "  Skipped .env.local (not present at repo root)"
fi

# settings.local.json is gitignored, so a fresh worktree never inherits it —
# without this copy, locally-disabled MCP servers auto-start in every worktree.
if [[ -f "$main_root/.claude/settings.local.json" ]]; then
  mkdir -p "$target/.claude"
  cp "$main_root/.claude/settings.local.json" "$target/.claude/settings.local.json"
else
  echo "  Skipped .claude/settings.local.json (not present at repo root)"
fi

if [[ "$no_open" -eq 1 ]]; then
  echo "Skipping editor launch (--no-open)."
elif command -v zed >/dev/null 2>&1; then
  echo "Opening $target in Zed..."
  zed "$target"
else
  echo "Warning: 'zed' not found on PATH — skipping editor launch."
fi

echo "Installing dependencies..."
# A worktree without node_modules cannot build or test, so a failed install is a
# failed worktree — not a warning to print under a success banner. Callers
# (implement-spec, CI) branch on this exit code; reporting 0 here sends them off
# to run tests in an empty tree and blame their own changes for the failures.
if ! (cd "$target" && pnpm install); then
  # %q-quote every interpolated value: git accepts shell metacharacters in
  # branch names (`feature/a;id` passes check-ref-format), and these lines are
  # printed for the reader to copy and run.
  echo "" >&2
  echo "── Worktree UNUSABLE ─────────────────────────" >&2
  echo "  $target" >&2
  echo "" >&2
  echo "  The worktree exists, but pnpm install failed, so dependencies are" >&2
  echo "  missing: it cannot build or test in this state." >&2
  echo "" >&2
  echo "  Fix the install, then re-run this script — it reuses the worktree" >&2
  echo "  and retries the install:" >&2
  printf '    %s %q\n' "$0" "$branch" >&2
  echo "" >&2
  echo "  Or discard it, from the main checkout:" >&2
  printf '    (cd %q && scripts/setup/gwt-remove.sh %q)\n' "$main_root" "$branch" >&2
  echo "    Note: gwt-remove.sh deletes the branch too (git branch -d, so" >&2
  echo "    unmerged work is refused rather than lost)." >&2
  echo "──────────────────────────────────────────────" >&2
  exit 1
fi

echo ""
echo "── Worktree ready ────────────────────────────"
echo "  $target"
echo "──────────────────────────────────────────────"
