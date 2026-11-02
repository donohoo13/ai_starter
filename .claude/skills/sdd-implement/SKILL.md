---
name: sdd-implement
description: Build an approved tasks.md one task at a time, each through the tdd skill. Close every slice with the full suite, staging by explicit path and a proposed commit, and keep tasks.md current so a fresh session can resume. Use when the user says "implement the tasks", "build the spec", "sdd implement", "resume implementation", or tasks are approved and ready to build. Phase 4 of spec-driven development, section 10 of .claude/sdd/spec-driven-development.md.
argument-hint: "[slug]"
allowed-tools: Bash(.claude/sdd/bin/sdd *)
---

# SDD Implement (phase 4)

Build the tasks one at a time, each through `tdd`, and hand the user one commit per slice.
The rules live in section 10 (Implement) of `.claude/sdd/spec-driven-development.md`; this file is only the procedure.
Where the two differ, the document wins.

Arguments: `$ARGUMENTS`, an optional slug.

## Preconditions

- `.claude/sdd/bin/sdd status <slug> --json` reports `phase` `4. Implement`: tasks approved or in progress, unchanged since approval and not stale.
- Anything else: stop, tell the user the phase and the skill `status` names, and do no other phase's work.
- This skill resumes at the first unchecked item.
  A fresh session needs nothing but `docs/sdd/<slug>/`.

## Start (section 4 (The workflow), start protocol)

1. Read sections 1–5 of the document once per session, then section 10 (Implement).
2. Resolve the slug: the argument, else `.claude/sdd/bin/sdd find`, else list the folders it prints and ask.
3. Run `.claude/sdd/bin/sdd status <slug> --json` and check the preconditions.
   Note `tasks.next`.
4. Load the project context (section 6 (Project principles and context)), the commands `CLAUDE.md` names, or the ones the `tdd` discovery in `.claude/skills/tdd/references/discover.md` finds for this repo, and `tasks.md`. Load the plan and spec per task, not whole.

## Steps (section 10 (Implement), Steps)

1. **Check the branch.**
   The spec's `branch` field names the feature branch.
   On it: continue.
   On the default or a shared branch: propose creating the spec's branch, ask, then create it, through `scripts/setup/gwt-add.sh --no-open <branch>` and the EnterWorktree tool when this checkout should stay on the default branch; if the user picks another name, set the spec's `branch` field to it (frontmatter sits outside the content hash, so the spec stays approved).
   On a different feature branch: ask whether to switch to the spec's branch or record the current one the same way.
   If `git status` shows changes that are not this work, list them and ask what to do.
2. **Mark in progress**: `.claude/sdd/bin/sdd set-status <slug> tasks in-progress` (a no-op when already in progress).
3. **For each unchecked task**, in order:
   1. Load the task, its requirements from the spec, the plan sections it touches, and its seam.
   2. Invoke `tdd` through the Skill tool, once per task, with these arguments: the task title as the behavior, `Seam:` from the task, `Files:` from the task, `Done when:` from the task, and this instruction verbatim: "Unit of work: this task.
      The caller runs the full suite at slice close."
   3. Run the task's Done when check and show the command and its result.
   4. Self-check: list the task's requirements and mark each met with evidence, or not met.
      A requirement not met means the task is not done.
   5. Check the box and add exactly one sub-bullet `- Evidence: <the check and its result, on one line>` under the task, including any appearance assertions `tdd` removed.
      Record anything out of scope under `## Follow-ups (out of scope)`.
      Only the checkbox, that single `- Evidence:` line and the Follow-ups section sit outside the content hash; any other edit changes the approved tasks and routes the work back to `sdd-task`.
4. **Close each slice** when its last task is checked:
   1. Run the full suite once with the repo's test tiers: the commands `CLAUDE.md` names, or the ones the `tdd` discovery in `.claude/skills/tdd/references/discover.md` finds for this repo.
   2. On a failure, check whether it existed before your changes (stash, rerun, compare) and say which failures were already there.
   3. Stage by explicit path, including `docs/sdd/<slug>/tasks.md` so the progress log lands with the slice.
      Never `git add -A` or `git add .`.
   4. Propose a commit message in the repo's convention.
      Commit only on the user's word.
      Never push.
   5. Check the slice's close-out item.
5. **Finish**: when every item is checked, run `.claude/sdd/bin/sdd lint <slug>` as the exit check, then `.claude/sdd/bin/sdd set-status <slug> tasks done`, stage `docs/sdd/<slug>/tasks.md` by explicit path with a proposed commit message, and name `sdd-review`, or `refine` first when the branch should be brought up to the standards before review.

## While working

- Follow the plan; follow existing patterns; stay in scope; never weaken a check to make it pass.
  Section 10 (Implement) lists these and the stop-and-ask conditions: a gap or contradiction in the spec, an "Ask first" action, or the same approach failing twice.
  Stop there and describe, with options and a recommendation.
- `tasks.md` is your memory.
  Update it after every task, so `sdd status` resumes a fresh session at the right item.
  Use a fresh session per slice on a long list.

## Outputs

- Code and tests, the user's commits, and `tasks.md` fully checked with status `done`.

## Exit gate (section 4 (The workflow))

Every task and close-out checked, each slice's full suite green, the tree clean, `tasks.md` at `done`.

## Next

`sdd-review`.
Do not start it unless the user said to run end to end.
