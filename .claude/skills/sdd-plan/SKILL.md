---
name: sdd-plan
description: Turn an approved spec into an approved plan.md. Research with sources, present each significant decision as options with a recommendation, name the seam each slice's tests run at, check the plan against project principles, and fill the traceability table. Use when the user says "plan this spec", "write the plan", "sdd plan", or a spec is approved and the next question is how to build it. Phase 2 of spec-driven development, section 8 of .claude/sdd/spec-driven-development.md.
argument-hint: "[slug]"
allowed-tools: Bash(.claude/sdd/bin/sdd *)
---

# SDD Plan (phase 2)

Decide how the approved spec will be built.
The rules live in section 8 (Plan) of `.claude/sdd/spec-driven-development.md`; this file is only the procedure.
Where the two differ, the document wins.

Arguments: `$ARGUMENTS`, an optional slug.

## Preconditions

- `.claude/sdd/bin/sdd status <slug> --json` reports `phase` `2. Plan`: the spec is approved, unchanged since approval, with no clarification markers.
- An earlier phase: stop, tell the user the phase and the skill `status` names, and do no other phase's work.
  A later phase means the plan is approved and current: ask whether the user wants to revise it (section 13 (Changing course)), warn that the tasks go stale, and continue only on yes.
- A `plan.md` that already exists is revised or resumed.
  A stale plan is refreshed, not rewritten: read the spec's Changelog, revise every section the change touches, set `based_on` to the spec's new `approved_hash`, then lint.
  `approve` refuses while `based_on` is set to an old hash.

## Start (section 4 (The workflow), start protocol)

1. Read sections 1–5 of the document once per session, then section 8 (Plan).
2. Resolve the slug: the argument, else `.claude/sdd/bin/sdd find`, else list the folders it prints and ask.
3. Run `.claude/sdd/bin/sdd status <slug> --json` and check the preconditions.
   Note the spec's `approved_hash`.
4. Load only what this phase needs: the project context (section 6 (Project principles and context)), the approved spec, and the existing plan if any.

## Steps (section 8 (Plan), Steps)

1. **Research** every fact the plan depends on: library versions, API behavior, service limits, pricing.
   Use WebSearch, Context7 and official documentation.
   Never rely on memory for a version-specific fact.
   Record each finding with its source under Research notes.
   For a scoped question that would stall the conversation, dispatch the `research-analyst` agent with the question, why it matters, the source order, pinned Context7 library IDs when the repo's `CLAUDE.md` lists them, and a scope bound, and keep working.
2. **Draft `plan.md`** from `.claude/sdd/templates/plan.md` into `docs/sdd/<slug>/plan.md`. Set `title` and the H1 from the spec's title, `slug`, `updated`, and `based_on` to the spec's `approved_hash`.
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
8. **Lint**: `.claude/sdd/bin/sdd lint <slug> plan`.
   Fix every error.

## Outputs

- `docs/sdd/<slug>/plan.md`, status `approved`, `approved_hash` and `based_on` recorded by the helper.

## Finish (section 4 (The workflow), finish protocol)

1. Exit checks: `.claude/sdd/bin/sdd lint <slug> plan` reports 0 errors; every requirement maps to plan elements and a seam.
2. Present the plan, the decisions it records with the options rejected, the principle deviations, and any open question.
   Ask for approval.
3. Only after the user approves in the conversation, run `.claude/sdd/bin/sdd approve <slug> plan`.
   Never approve on their behalf.
   Then stage `docs/sdd/<slug>/plan.md` by explicit path and propose a commit message in the repo's convention; the user commits.
4. Name `sdd-task` as the next skill.
   Do not start it unless the user said to run end to end.

## Next

`sdd-task`, with `docs/sdd/<slug>/` as the handoff.
