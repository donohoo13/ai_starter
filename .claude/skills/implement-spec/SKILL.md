---
name: implement-spec
description: Build a docs/specs/ file slice by slice on a dedicated worktree or non-main branch, planning, testing first, validating, and committing each slice, keeping the spec's status current, and gating done on human QA; never pushes or opens a PR. Use when the user points at a spec file to build, says "implement this spec", "build the spec", or resumes an in-progress spec in a fresh session.
argument-hint: "[path to a docs/specs/*.md file, or blank to pick from ready specs]"
---

# Implement Spec

The design is settled: build what the spec says and never re-decide architecture. A one-slice spec runs the same loop as a ten-slice one, once.

## Gate

- Read the spec named in the argument; with none, list `docs/specs/` files at `status: ready` or `in-progress` and confirm which to build.
- Build only a `ready` or `in-progress` spec whose slices each carry a done-when and whose Architecture carries no `TBD`. Otherwise name what is missing, recommend `/sdd` on the file, and stop; an under-specified spec gets its gaps invented silently.
- A spec that proves wrong against the code is `BLOCKED`: surface it, never redesign silently.

## Workspace

- Never build on `main` unless specifically dictated by the user, and never switch branches in a shared checkout carelessly; another session may be working there.
- Derive the branch from the filename, `docs/specs/NNN-<slug>.md` to `<type>/<slug>` with `type` feature, bug, or chore by the spec's nature. Offer one confirm for a dedicated worktree via `scripts/setup/gwt-add.sh --no-open <branch>` entered with `EnterWorktree`; a decline means the user names a non-main branch and the build runs there. A checkout already on the spec's branch is simply continued.
- Before the tree splits, check `git status` for uncommitted `docs/**`, `CLAUDE.md`, `BRANDING.md`, and `.claude/**` changes, reading the tree rather than session memory. Make one offer to stage exactly those paths and hand back a commit message for the user to commit on `main`; a declined offer leaves them behind by the user's choice. Never stage other dirt, which may be another session's work in flight. The spec file itself must exist on the branch before the first slice.
- When Architecture says the existing implementation is stripped first, delete those files as the first commit and build from the spec rather than from memory of the old code. A rewrite lands cleaner when the old shape is gone from the tree than when it is patched around, so weigh that call against the spec rather than defaulting to keeping what compiles.

## Slice loop

Flip the spec to `status: in-progress` before the first slice; it rides in that slice's commit. List order is build order. Per slice:

1. **Plan**: re-read the slice against Architecture and References, read the code at the touch points, confirm consumers of shared types with LSP find-references. Present files, sequence, test seams, and risks, end with `Proceeding unless you interrupt.`, and keep working in the same turn. A slice that cannot proceed without an answer reports `BLOCKED` and says why.
2. **Build** with `/tdd`: red before green, one seam at a time. A surface slice holds the floors in `docs/standards/ux-standards.md`.
3. **Validate**: the project's own typecheck, lint, format, and the slice's test files, discovered from `CLAUDE.md` and the manifest rather than assumed. Fix until clean. The full suite waits for Land.
4. **Commit**: verify the branch, stage by explicit path (the slice's files plus the spec with its checkbox ticked), message naming the slice's behavior.
5. **Audit** after multi-file changes: schemas, constant maps, and imports updated consistently; orphaned code removed or reported, never left.

Report `DONE`, `DONE_WITH_CONCERNS` (continue, note the doubt), or `BLOCKED` (stop, surface, wait).

## Land

- Run the full suite once, its first run; a failure is a real regression to fix and commit.
- When any slice touched a user-facing surface, offer a render pass: the user starts the app (hand the command with the worktree's absolute path, since a terminal in the main checkout serves `main`), then screenshot each touched surface at mobile and desktop width, in every theme shipped, with the UI tool named in `CLAUDE.md`. Judge against the spec's Design Requirements, `BRANDING.md`, and the `ux-standards.md` floors; fix what fails. A declined pass is noted in the spec so a later reader knows the gap.
- Hand over a QA script: exact commands, URLs, and actions, each observation mapped to a slice's done-when. Servers are user-run; give instructions, never start one. Stop and wait. Green checks prove the code does what the tests say; only the user confirms it does what they meant, so recommend nothing downstream until then. Issues found go back through the loop, then the suite runs again.
- On confirmation flip `status: done`, commit the flip, and stop. Never push or open a PR from here.
