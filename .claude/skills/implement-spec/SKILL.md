---
name: implement-spec
description: Build a docs/specs/ file on a dedicated worktree or non-main branch by orchestrating one fresh builder agent per slice, verifying each slice's commit and tests, forwarding notes between slices, running the full suite and a render pass on an app the session launches itself, and flipping the spec to built; never edits source itself, pushes, or opens a PR. Use when the user points at a spec file to build, says "implement this spec", "build the spec", or resumes an in-progress spec in a fresh session.
argument-hint: "[path to a docs/specs/*.md file, or blank to pick from ready specs]"
---

# Implement Spec

The design is settled: build what the spec says and never re-decide architecture.
This session orchestrates and the `builder` agent writes.
Each slice is built in a fresh context that sees only the spec, the code, and the notes earlier slices left, so no slice inherits the bias of the conversation that planned it.
The session runs the gates, talks to the user, flips spec status, owns the app server, dispatches agents, and verifies their claims with `git` and test runs; it never edits source or tests.
Every worker it dispatches or resumes is waited on, because the next step acts on that worker's report.
Never take the next step until the report is in; when it has not arrived, end the turn and resume from the report when it does.
A one-slice spec runs the same loop as a ten-slice one, once.

## Gate

- Read the spec named in the argument; with none, list `docs/specs/` files at `status: ready` or `in-progress` and confirm which to build.
- Build only a `ready` or `in-progress` spec whose slices each carry a done-when and whose Architecture carries no `TBD`.
  Otherwise name what is missing, recommend `/sdd` on the file, and stop; an under-specified spec gets its gaps invented silently.
- A spec that proves wrong against the code is `BLOCKED`: surface it, never redesign silently.

## Workspace

- Never build on `main` unless specifically dictated by the user, and never switch branches in a shared checkout carelessly; another session may be working there.
- Derive the branch from the filename, `docs/specs/NNN-<slug>.md` to `<type>/<slug>` with `type` feature, bug, or chore by the spec's nature.
  Offer one confirm for a dedicated worktree via `scripts/setup/gwt-add.sh --no-open <branch>` entered with `EnterWorktree`; a decline means the user names a non-main branch and the build runs there.
  A checkout already on the spec's branch is simply continued.
- Before the tree splits, check `git status` for uncommitted `docs/**`, `CLAUDE.md`, `BRANDING.md`, and `.claude/**` changes, reading the tree rather than session memory.
  Make one offer to stage exactly those paths and hand back a commit message for the user to commit on `main`; a declined offer leaves them behind by the user's choice.
  Never stage other dirt, which may be another session's work in flight.
  The spec file itself must exist on the branch before the first slice.
- When Architecture says the existing implementation is stripped first, delete those files as the first commit and build from the spec rather than from memory of the old code.
  A rewrite lands cleaner when the old shape is gone from the tree than when it is patched around, so weigh that call against the spec rather than defaulting to keeping what compiles.

## Slices

Flip the spec to `status: in-progress` before the first dispatch; the first builder's commit carries the flip.
List order is build order, and a resumed spec starts at its first unticked slice.
Per slice:

1. Dispatch a fresh `builder` with the spec path, the slice's checkbox text, and every note earlier builders reported, verbatim, then wait for its report.
   Nothing else rides in the brief: no plan, no opinion, no summary of this conversation, because whatever the orchestrator adds is the bias the fresh context exists to keep out.
2. On `BLOCKED`, put the builder's question to the user, then resume the same builder with the answer through `SendMessage` so it keeps its full context.
   On `DONE_WITH_CONCERNS`, keep the doubt for the final report and continue.
3. Verify before moving on: every reported commit exists on this branch, the slice's tests pass when this session runs them, and the slice's checkbox is ticked in the committed spec.
   A claim that fails verification goes back to the same builder through `SendMessage` with what this session found.
4. Report the slice in one line, its commits and status, and carry its notes into the next brief.

## Land

- Run the full suite once.
  A failure goes to a fresh `builder` briefed with the spec path and the failing output; verify its fix commit, then run the suite again.
- Run the render pass when the branch touches a user-facing surface: a changed path matching the `applies-to:` globs in `docs/standards/ux-standards.md`, or a spec with Design Requirements.
  Launch the app (below), then dispatch `render-checker` with the URL, the touched surfaces and the states the spec names, the themes the app ships, and the bar: the spec's Design Requirements and `BRANDING.md`.
  Failures go to a fresh `builder` briefed with the spec path and the findings, followed by one re-check; what still fails after that is reported, not looped on.
  A skipped pass is noted in the spec beneath its slices, with the reason, so a later reader knows the gap.
- Flip the spec to `status: built`, commit the flip and any skip note alone, and report: each slice's commits and status, the concerns kept, the suite result, and the render result with its screenshots.
- Stop there.
  The build is working and validated but not yet made right, so this skill hands over no QA script and never flips `done`.
  Never push or open a PR from here.

## App lifecycle

- Launch in this checkout: a recorded `run-*` project skill under `.claude/skills/` when one exists, otherwise `pnpm dev` as a background task.
- Read `.logs/dev-server.log` for readiness and the real URL.
  When `pnpm dev` reports a server already running with its pid, reuse that server.
- Stop only a server this session started (`kill $(cat .logs/dev-server.pid)` for `pnpm dev`), at the end of the skill.
  The session owns the server rather than an agent because the server must outlive several checker runs.
- Tell the user about a launch failure once, with its cause and `/run-skill-generator` as the one-time fix that records a launch recipe for later runs; that run's render pass is skipped and noted.
