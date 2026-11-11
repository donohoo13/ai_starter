---
name: sdd-plan
description: Turn an approved spec into an approved plan.md. Research with sources, present each significant decision as options with a recommendation, name the seam each slice's tests run at, check the plan against project principles, and fill the traceability table. Use when the user says "plan this spec", "write the plan", "sdd plan", or a spec is approved and the next question is how to build it. Phase 3 of spec-driven development, section 9 of .claude/sdd/spec-driven-development.md.
argument-hint: "[slug]"
allowed-tools: Bash(.claude/sdd/bin/sdd *)
---

# SDD Plan (phase 3)

Decide how the approved spec will be built.
The rules live in section 9 (Plan) of `.claude/sdd/spec-driven-development.md`; this file is only the procedure.
Where the two differ, the document wins.

Arguments: `$ARGUMENTS`, an optional slug.

## Preconditions

- `.claude/sdd/bin/sdd status <slug> --json` reports `phase` `3. Plan`: the spec is approved, unchanged since approval, with no clarification markers, and any design is approved and current or skipped covering every listed UI surface.
- An earlier phase, `2. Design` included: stop, tell the user the phase and the skill `status` names (`sdd-design` for a design that is requested, changed or stale), and do no other phase's work.
  A later phase means the plan is approved and current: ask whether the user wants to revise it (section 14 (Changing course)), warn that the tasks go stale, and continue only on yes.
- `3. Plan` on a spec whose UI surfaces section lists a surface, with no `design.md`: before any other step, ask whether to run `sdd-design` first or skip the design, recommending `sdd-design` when a surface is new.
  A run: stop, write nothing, and name `sdd-design`.
  A skip: run `.claude/sdd/bin/sdd set-status <slug> design skipped`, which records the user's git `user.name`, the date and the surfaces it covers; write their reason under `design.md`'s Skip reason and "None" under every other section, stage `<folder>/design.md` by explicit path and propose a commit message only when `mode` is `shared`, and continue planning.
  Record the skip only on the user's word.
- A `plan.md` that already exists is revised or resumed.
  A stale plan is refreshed, not rewritten: read the spec's Changelog and any change to `design.md`, revise every section the change touches, set `based_on` to the new `approved_hash` of its upstream (the design while it is approved, otherwise the spec), then lint.
  `approve` refuses while `based_on` is set to an old hash.

## Start (section 4 (The workflow), start protocol)

1. Read sections 1–5 of the document once per session, then section 9 (Plan).
2. Resolve the slug: the argument, else `.claude/sdd/bin/sdd find`, else list the folders it prints and ask.
3. Run `.claude/sdd/bin/sdd status <slug> --json` and check the preconditions.
   When it refuses because the spec is in another worktree, or on a branch no worktree has checked out, this session started outside the spec's worktree: move into it as the refusal says (section 5 (Working files), The branch and its worktree), then run `status` again there.
   Note the spec's `approved_hash`, and the design's when `artifacts.design.status` is `approved`.
   Note `folder` and `mode` too (section 5 (Working files)): every spec file is read and written under `folder`, the spec folder's absolute path, which in a private repository is the main checkout's and can sit outside the current directory.
4. Load only what this phase needs: the project context (section 6 (Project principles and context)), the approved spec, the approved `design.md` with its artboard list when there is one, and the existing plan if any.

## Steps (section 9 (Plan), Steps)

1. **Research** every fact the plan depends on: library versions, API behavior, service limits, pricing.
   Use WebSearch, Context7 and official documentation.
   Never rely on memory for a version-specific fact.
   Record each finding with its source under Research notes.
   For a scoped question that would stall the conversation, dispatch the `research-analyst` agent with the question, why it matters, the source order, pinned Context7 library IDs when the repo's `CLAUDE.md` lists them, and a scope bound, and keep working.
2. **Draft `plan.md`** from `.claude/sdd/templates/plan.md` into `<folder>/plan.md`.
   Set `title` and the H1 from the spec's title, `slug`, `updated`, and `based_on` to the design's `approved_hash` when the design is approved, otherwise the spec's.
   Keep every template heading, since lint requires them; write "None" under a heading that does not apply.
   Replace or delete every `<...>` placeholder, since lint reports any that remain.
3. **Offer options.**
   For each significant decision, use the AskUserQuestion tool with at least two options, their trade-offs, and the recommended option listed first.
   Record the choice, and the options rejected under Alternatives considered.
   Decisions are the user's; do not make them.
4. **Name the seams.**
   Open `.claude/skills/tdd/SKILL.md`, run the discovery its Before the first test section names (`references/discover.md`) unless its findings are already in context, then read its Seams section.
   For each slice, name the seam and the test types in the vocabulary the discovery found, so `sdd-implement` and `tdd` test exactly where the plan says.
   Repo knowledge lives only in `tdd` and the repo's own files; never restate it here.
5. **Check the principles.**
   Fill the Principles check table against every project principle; justify each deviation with the simpler option rejected.
6. **Route spec gaps back.**
   If planning exposes a gap or contradiction in the spec, stop, describe it, and name `sdd-outline`.
   Do not patch the gap in the plan.
7. **Fill Traceability**: one row per `FR-`, `NFR-` and `INV-` with components, seam and tests.
   With an approved design, Affected code and Traceability name the components that build each designed surface by its UI ID, and plan nothing `design.md` lists under Not built, since the user excluded it at the design gate.
8. **Lint**: `.claude/sdd/bin/sdd lint <slug> plan`.
   Fix every error.

## Outputs

- `plan.md` in the spec folder, status `approved`, `approved_hash` and `based_on` recorded by the helper.

## Finish (section 4 (The workflow), finish protocol)

1. Exit checks: `.claude/sdd/bin/sdd lint <slug> plan` reports 0 errors; every requirement maps to plan elements and a seam.
2. Present the plan, the decisions it records with the options rejected, the principle deviations, and any open question.
   Ask for approval.
3. Only after the user approves in the conversation, run `.claude/sdd/bin/sdd approve <slug> plan`.
   Never approve on their behalf.
   Then, when `mode` is `shared`, stage `<folder>/plan.md` by explicit path and propose a commit message in the repo's convention; the user commits.
   When it is `private`, stage nothing and propose no commit, and never force a spec file in with `git add -f`: git ignores the folder so that it stays out of the repository, and the file alone records the approval.
4. Name `sdd-task` as the next skill.
   Do not start it unless the user said to run end to end.

## Next

`sdd-task`, with the spec folder as the handoff.
