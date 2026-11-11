---
name: sdd-outline
description: Turn an idea, brief, ticket or bug into an approved spec.md under docs/sdd/. Size the change, ground in the code, play the problem back for the user to confirm, interview in focused batches, run an adversarial review, then gate on the user's approval. Use when the user says "spec this out", "outline a feature", "write a spec", "start SDD", or brings a new feature idea. Phase 1 of spec-driven development, section 7 of .claude/sdd/spec-driven-development.md.
argument-hint: "[slug] [brief]"
allowed-tools: Bash(.claude/sdd/bin/sdd *)
---

# SDD Outline (phase 1)

Turn intent into an approved `spec.md`. The rules live in section 7 (Outline) of `.claude/sdd/spec-driven-development.md`; this file is only the procedure.
Where the two differ, the document wins.

Arguments: `$ARGUMENTS`.
The first token is the slug when it contains a hyphen or names an existing `docs/sdd/` folder; otherwise the whole argument is the brief.

## Preconditions

- Section 3 (Sizing) sizes the change as medium or larger.
  Trivial: say so and recommend making the change directly, with `tdd` only if behavior changes.
  Small: recommend `tdd` as a one-shot, then `sdd-review` before the PR.
  Continue only if the user still wants the chain.
- If `docs/sdd/<slug>/spec.md` already exists, this run revises or resumes it.
  Start over only when the user asks.

## Start (section 4 (The workflow), start protocol)

1. Read sections 1–5 of the document once per session, then section 7 (Outline).
2. Resolve the slug: the argument; else `.claude/sdd/bin/sdd find`; else, on a feature branch, the branch name in kebab-case (section 5 (Working files)); else list the folders `find` prints and, when none fits, propose a short kebab-case slug and confirm it.
3. Run `.claude/sdd/bin/sdd status <slug> --json`.
   When a spec exists and `phase` is later than `1. Outline`, the spec is approved: ask whether the user wants to revise it (section 14 (Changing course)), warn that the design, plan and tasks built on it go stale, and continue only on yes.
4. Create the folder when it is missing.
   On a shared branch, one that other work also merges into such as `main` or `staging`, propose `feature/<slug>` (the `<type>/<kebab-slug>` convention in `CLAUDE.md`) and record it: `.claude/sdd/bin/sdd init <slug> --branch <name>`.
   Otherwise `.claude/sdd/bin/sdd init <slug>`.
   `init` also records the spec's base, the branch this work is cut from and merges back into, as the remote's default branch that git reports, so ask nothing about it; add `--base <name>` only when the user has said the work builds on another branch.
   When `init` prints that git could not tell, ask the user and record their answer: `.claude/sdd/bin/sdd set-base <slug> <branch>`.
   The folder is tracked by git; nothing ignores it.
5. Load only what this phase needs: the project context (section 6 (Project principles and context)) and the existing spec, if any.

## Steps (section 7 (Outline), Steps)

1. **Ground yourself in the code.**
   Explore read-only.
   Delegate wide searches to Explore subagents and keep their conclusions.
   Before writing, name the files, interfaces and existing behavior involved.
   Establish why the problem happens, reading how each system involved behaves, its vendor's documentation included when it is third-party.
2. **Play back the problem** in the conversation as section 7 (Outline) Steps describes, then end your turn.
   Interview only after the user confirms or corrects the playback.
3. **Interview** when the brief is thin, with the AskUserQuestion tool, in batches of two to four related questions, the most load-bearing first, each with a recommended option listed first.
   Ask only what the code cannot tell you: edge cases, failure behavior, trade-offs, constraints, who the work is for, what success looks like.
   Keep options to behavior or hard constraints, and ask once per problem when the answer differs per problem.
   An assumption the user accepts goes under Assumptions with their name.
   Anything unresolved becomes `[NEEDS CLARIFICATION: <specific question>]`.
4. **Draft `spec.md`** in place, keeping the frontmatter `init` wrote.
   Follow section 7 (Outline) for the description, summary, requirements, scenarios, invariants and existing behavior.
   Delete every placeholder you do not fill, including the sample clarification line under Open questions, and drop the optional sections the sections table does not call for; lint reports every `<...>` placeholder left from the template as an error.
   List every screen, page, view, component or email template the change creates or edits under UI surfaces, as section 7 (Outline) describes, since the design offer at the finish and the later skills read that list; leave the section out when there is none.
   When revising an approved spec, add a dated entry under Changelog with the reason.
5. **Check it.**
   Run the spec readiness checklist from section 7 (Outline) and `.claude/sdd/bin/sdd lint <slug> spec`.
   Fix every error; answer every warning with a number or a rewrite.
6. **Adversarial review.**
   Dispatch a general-purpose subagent with the prompt in [references/adversarial-review.md](references/adversarial-review.md), its three placeholders filled in: the spec path, the project context paths, and the repository root.
   Turn each finding into a fix or a clarification marker, then lint again.
7. **Interview again** for the markers the review raised, then clear them.

## Outputs

- `docs/sdd/<slug>/spec.md`, with status `approved` and `approved_hash` recorded by the helper.

## Finish (section 4 (The workflow), finish protocol)

1. Exit checks: `.claude/sdd/bin/sdd lint <slug> spec` reports 0 errors, no marker remains, the readiness checklist passes.
2. Present the spec, the decisions it records, the assumptions and any open question.
   Ask for approval.
3. Only after the user approves in the conversation, run `.claude/sdd/bin/sdd approve <slug> spec`.
   Never approve on their behalf.
   Then stage `docs/sdd/<slug>/spec.md` by explicit path and propose a commit message in the repo's convention; the user commits.
4. Name the next skill.
   When `design.md` exists, offer no skip and name the skill `sdd status` reports: `sdd-design` at `2. Design` for a requested or approved design, which it re-checks against the revised spec, or for a skip that misses a surface the spec now lists.
   When `design.md` is absent and the UI surfaces section lists a surface, name each listed surface and offer `sdd-design` for a Claude Design mockup before planning, with `sdd-plan` as the alternative.
   When the user skips the design, run `.claude/sdd/bin/sdd set-status <slug> design skipped`, which records their git `user.name`, the date and the surfaces the skip covers; write their reason under `design.md`'s Skip reason and "None" under every other section, then stage `docs/sdd/<slug>/design.md` by explicit path and propose a commit message.
   Record a skip only on the user's word, never by default.
   When the spec lists no UI surface, name `sdd-plan` only and write no `design.md`.
   Do not start the next skill unless the user said to run end to end.

## Next

`sdd-design` when `sdd status` reports `2. Design`, or the spec lists a UI surface and the user wants a design, otherwise `sdd-plan`, with `docs/sdd/<slug>/` as the handoff.
