---
name: sdd-task
description: Break an approved plan into tasks.md. One observable behavior per task with its requirements, seam, files and done-when check, grouped into slices that each end in a close-out. Use when the user says "write the tasks", "break this down", "sdd tasks", or a plan is approved and needs a task list. Phase 3 of spec-driven development, section 9 of .claude/sdd/spec-driven-development.md.
argument-hint: "[slug]"
allowed-tools: Bash(.claude/sdd/bin/sdd *)
---

# SDD Tasks (phase 3)

Break the approved plan into tasks a red-green loop can build one at a time.
The rules live in section 9 (Tasks) of `.claude/sdd/spec-driven-development.md`; this file is only the procedure.
Where the two differ, the document wins.

Arguments: `$ARGUMENTS`, an optional slug.

## Preconditions

- `.claude/sdd/bin/sdd status <slug> --json` reports `phase` `3. Tasks`: the plan is approved, unchanged since approval and not stale.
- An earlier phase: stop, tell the user the phase and the skill `status` names, and do no other phase's work.
  A later phase means the tasks are approved or in progress: ask whether the user wants to revise them (section 13 (Changing course)), warn that re-approval pauses implementation, and continue only on yes.
- A `tasks.md` that already exists is revised or resumed.
  Keep task IDs stable; never renumber.
  A stale task list is refreshed against the re-approved plan: revise the affected tasks, set `based_on` to the plan's new `approved_hash`, then lint.

## Start (section 4 (The workflow), start protocol)

1. Read sections 1–5 of the document once per session, then section 9 (Tasks).
2. Resolve the slug: the argument, else `.claude/sdd/bin/sdd find`, else list the folders it prints and ask.
3. Run `.claude/sdd/bin/sdd status <slug> --json` and check the preconditions.
   Note the plan's `approved_hash`.
4. Load only what this phase needs: the project context (section 6 (Project principles and context)); the commands `CLAUDE.md` names, or the ones the `tdd` discovery in `.claude/skills/tdd/references/discover.md` finds for this repo, which supply the commands for `Done when`; the approved plan in full; and from the spec only the requirement IDs, user scenarios and acceptance criteria.

## Steps (section 9 (Tasks), Task shape and Rules)

1. **Draft `tasks.md`** from `.claude/sdd/templates/tasks.md` into `docs/sdd/<slug>/tasks.md`. Set `title` and the H1 from the spec's title, `slug`, `updated`, and `based_on` to the plan's `approved_hash`.
   Replace or delete every `<...>` placeholder, since lint reports any that remain.
2. **Slices**: one `## P<n>: <story>` per user story, in the plan's order, so each slice ships alone.
   Within a slice, foundations before what depends on them.
3. **Tasks**: `- [ ] T001 <one observable behavior>` with sub-bullets `Requirements`, `Seam` (copied from the plan), `Files`, `Depends on` when needed, and `Done when` as a command from the repo's test tiers, or a check, that passes or fails.
   Its test is written inside the task, never in a separate testing task.
   Mark `[P]` only when the task shares no files and no dependency with the other `[P]` tasks in its slice.
4. **Close-outs and decisions**: end every slice with the close-out line from the template.
   Keep the `## Verified elsewhere` section for coverage decisions (step 5) and the `## Follow-ups (out of scope)` section for discoveries during implementation; write `- None` under either when it is empty.
5. **Lint**: `.claude/sdd/bin/sdd lint <slug> tasks`.
   Fix every error before presenting: a requirement without a task, an unknown or removed ID, a missing field, a `[P]` conflict, a slice without a close-out, a placeholder left from the template.
   An `NFR-` or `INV-` needs a task unless the user decides it is verified another way; record that decision under `## Verified elsewhere` as `- <ID>: <how it is verified>. Decided by <name>.`, which lint accepts in place of a task and the content hash guards after approval.
   Act on every warning: a test-only task is horizontal work, so fold the test into the task that makes it pass.

## Outputs

- `docs/sdd/<slug>/tasks.md`, status `approved`, `approved_hash` and `based_on` recorded by the helper.

## Finish (section 4 (The workflow), finish protocol)

1. Exit checks: `.claude/sdd/bin/sdd lint <slug> tasks` reports 0 errors; every requirement has a task, every task has a seam and a check.
2. Present the task list by slice, with counts and anything the plan left open.
   Ask for approval.
3. Only after the user approves in the conversation, run `.claude/sdd/bin/sdd approve <slug> tasks`.
   Never approve on their behalf.
   Then stage `docs/sdd/<slug>/tasks.md` by explicit path and propose a commit message in the repo's convention; the user commits.
4. Name `sdd-implement` as the next skill and recommend starting it in a fresh session.
   Do not start it unless the user said to run end to end.

## Next

`sdd-implement` in a fresh session, with `docs/sdd/<slug>/` as the handoff.
