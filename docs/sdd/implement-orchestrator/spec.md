---
title: Implement orchestrator
slug: implement-orchestrator
branch: feature/implement-orchestrator
status: approved
owner: Conner Donohoo
created: 2026-11-02
updated: 2026-11-02
approved_hash: 4485cb3ff02f
description: Moves `sdd-implement` from building every task in-session to orchestrating one fresh implementer agent per slice and committing each verified slice. The result is a build free of the planning session's bias, one user QA pass at the end, and one review instead of two.
---

# Implement orchestrator

## Summary

`sdd-implement` builds every task of an approved `tasks.md` inside the session that invokes it, running `tdd` inline, and the user commits each slice by hand.
That session accumulates every file read, test run and judgment call of the whole build, and nothing separates the context that builds a slice from the one that checks it.
A long task list fills the context until the skill tells the user to restart between slices, and the user still has to stop at every slice to commit.
After the build, a separate `refine` pass rewrites the branch to the standards before `sdd-review` reviews it again, so standards are judged twice and code changes after it was built.
This change turns `sdd-implement` into an orchestrator that dispatches one fresh `implementer` agent per slice, verifies the agent's work, and commits it, then hands the user one QA pass at the end.
Each slice is built in a clean context from pointers into the approved spec, plan and tasks, and is checked by a context that did not write it, while standards checks move inside the slice where the code is written.
When the work is done, the branch holds one commit per slice, `refine` is gone, and `sdd-review`, whose reviewers each run in a fresh context, is the single review before the pull request.

## Problem and context

- `.claude/skills/sdd-implement/SKILL.md` runs `tdd` through the Skill tool once per task in the invoking session, and closes each slice by proposing a commit that the user makes.
- `.claude/rules/skill-authoring.md` requires that "code work runs in agents" and exempts `sdd-implement` so "the user's gates sit between tasks".
  The skill has no gate between tasks: its only gates are the slice commit and the stop-and-ask conditions in section 10 of `.claude/sdd/spec-driven-development.md`.
- History: commit `94af300` built each slice through a fresh `builder` agent; commit `f323246` removed `builder` when the SDD chain replaced the old spec suite, and added the exemption.
- `refine` dispatches a `refiner` agent that rewrites a finished branch to `docs/standards/`, then runs a `render-checker` pass and a human QA script.
  `sdd-review` then dispatches `standards-reviewer` against the same `docs/standards/` files, so standards are judged twice and the code is rewritten between build and review.
- `render-checker` passes are slow and token-heavy, and run automatically inside `refine` whenever a change touches a user-facing surface.
- The SDD document's principle 10, its Roles table, section 1 and the quick reference say the user commits and the agent never does.
  That wording came from a workplace that restricts AI commits; this template is for the owner's personal workspace, where the owner QAs at the end and trusts the build to commit against a spec approved through the chain.
- With one agent per slice built serially, the `[P]` parallel-task marker in `tasks.md` and its lint in `.claude/sdd/bin/sdd` have no consumer.
- `CLAUDE.md`, `README.md`, `.ai-starter.yaml` and `scripts/test/ai-starter-version.battery.mjs` still describe the `template-sync` and `template-feedback` skills, which commit `e1407c8` deleted, and `CLAUDE.md` counts twelve skills where ten exist.
  `docs/specs/001-refine.md` documents the retired `refine` and `builder` flow.

## Goals

- G1: Every slice of an approved `tasks.md` is built by a fresh agent whose brief carries only pointers and the user's decisions, and the orchestrating session writes only the files FR-002 allows.
- G2: A run in which no interruption in G3 fires ends with every slice committed and no commit made by the user.
- G3: The user is interrupted during a run only by an interruption the Glossary lists, and once at the end for QA.
- G4: Standards are judged once inside each slice and once by `sdd-review`, against the same set of standards files, with no post-build rewrite pass.
- G5: Every tracked file outside `docs/sdd/` and `CHANGELOG.md` describes only the skills, agents and flow that exist after the change.

## Non-goals

- Building slices in parallel; slices run one at a time in `tasks.md` order.
- Changing `sdd-outline` or `sdd-plan` behavior, beyond the cross-references the docs sweep corrects.
- Changing the `sdd` helper's state machine or content hash.
- Running render checks automatically from any skill or agent.
- A correctness review of a trunk change during the build; `sdd-review`'s `code-review` covers the whole branch.
- Restoring `template-sync`, or porting this change into projects created from the template; porting to Fantasy Draft Lab is a separate follow-up done by hand.
- Changing who commits gate artifacts (`spec.md`, `plan.md`, `tasks.md` approvals) or `sdd-review` fixes; the user still commits those.

## User scenarios

### P1: Orchestrated slice build

As the owner, I want `sdd-implement` to build each slice through a fresh agent and commit it after checking it, so that the build follows the approved spec without the planning session's bias and without me committing by hand.
Independent test: a fresh session given the gut-check prompts that `.claude/rules/skill-authoring.md` requires, for a two-slice spec with an undecided trunk change, describes one commit per slice plus one trunk commit and no orchestrator write outside FR-002.

- Given an approved `tasks.md` with two slices, when the user runs `sdd-implement` in a fresh session, then the orchestrator dispatches one `implementer` per slice, verifies each, and commits each before dispatching the next.
- Given a slice agent that finds a trunk change the spec did not decide, when it stops, then the orchestrator dispatches `skeptic`, puts the decision to the user with the skeptic's case, and on approval commits the trunk change alone before the slice continues.

### P2: End-of-run QA and report

As the owner, I want one QA pass after every slice is committed, then a report of where the build stalled and what was decided along the way, so that I confirm the result once and know what to scrutinize.
Independent test: a fresh session given the gut-check prompts for a run with a trunk stop and a QA bug describes the bug fixed in its own commit, a report naming the trunk stop and its resolution, and `/sdd-review` in the same session as the next step.

- Given every slice committed, when the orchestrator reaches QA, then it starts the app when the change has a runnable surface, hands over a QA script and waits.
- Given a bug the user reports in QA, when the orchestrator handles it, then a fresh `implementer` fixes it red-first and the orchestrator verifies and commits the fix.

### P3: Retire refine; render checks on demand

As the owner, I want `refine` gone and render checks run only when I ask, so that the chain has one review pass and no automatic token-heavy step.
Independent test: no tracked file outside the FR-028 exclusions names `refine`, `refiner` or `code-reviewer`; `/render-check` dispatches `render-checker`; the model cannot invoke `render-check` on its own.

- Given a finished branch with a UI change, when the user runs `/render-check`, then it starts or reuses the app, dispatches `render-checker` and reports pass or fail per surface, width and theme.

### P4: Docs reflect the repository

As the owner, I want every document to describe the skills, agents and flow that exist, so that a fresh session is never misled by a stale reference.
Independent test: the FR-028 grep finds no reference to a removed skill or agent, and `CLAUDE.md` and `README.md` state no count of skills or agents.

## Requirements

### Functional

Orchestrator: dispatch

- FR-001: The `sdd-implement` skill shall build each slice whose close-out item is unchecked by dispatching one fresh `implementer` agent through the Agent tool, one slice at a time in `tasks.md` order, and shall never invoke `tdd` itself.
  - Acceptance: Given `.claude/skills/sdd-implement/SKILL.md`, when a reviewer reads its steps, then each slice is built by dispatching `implementer`, `tdd` is not invoked by the skill, and the next slice is dispatched only after the previous one is committed.
- FR-002: The orchestrator shall write only: `tasks.md`'s `status` field and slice close-out boxes, the spec's `branch` field, git staging and commits, and the processes it starts and stops; every other file is written only by an `implementer`.
  - Acceptance: Given the skill, when a reviewer reads it, then it lists exactly those writes as the orchestrator's and assigns every other edit to an `implementer`.
- FR-003: The brief to an `implementer` building a slice shall carry only the slug, the slice heading, the notes earlier slices reported, and any decisions the user made for this slice.
  - Acceptance: Given the skill's dispatch step, when a reviewer reads it, then the brief lists exactly those four inputs and states that the agent loads its tasks, requirements, plan sections and seams itself.

Implementer agent

- FR-004: A new `.claude/agents/implementer.md` shall define the agent, with `tdd` preloaded through its `skills:` frontmatter, building each task of its slice through `tdd` with the task as the behavior and the task's seam as the seam, and running each task's Done-when check.
  - Acceptance: Given the file, when a reviewer reads it, then its frontmatter lists `tdd` under `skills:` and its method states each of those steps.
- FR-005: Before reporting, the `implementer` shall check its own diff against every `docs/standards/` file whose `applies-to:` globs match a changed path, treating a file with no `applies-to:` key as matching every change, and fix what it finds.
  - Acceptance: Given the agent file, when a reviewer reads its method, then a standards self-check precedes the report and states both the glob rule and the no-key rule, the same rule `.claude/agents/standards-reviewer.md` uses.
- FR-006: The `implementer` shall check off each finished task of its slice and write exactly one `- Evidence:` line under it in `tasks.md`, may add entries under Follow-ups, shall make no other `tasks.md` edit, and shall never commit, push or switch branches.
  - Acceptance: Given the agent file, when a reviewer reads it, then it states those `tasks.md` edits as its only ones, leaves the close-out box to the orchestrator, and forbids commit, push and branch switch.
- FR-007: The `implementer` shall stop and report `BLOCKED`, leaving the tree as it is, when: a gap would change observable behavior a requirement or acceptance criterion describes, or would cross a non-goal or invariant; the spec contradicts itself or the code; a task needs an action on the project's "Ask first" list; the same approach has failed twice; or the work needs a trunk change the spec did not decide.
  - Acceptance: Given the agent file, when a reviewer reads its stop section, then it lists exactly those five conditions, names the "Ask first" list's source as the project's `CLAUDE.md` boundaries when present and otherwise section 6 of the SDD document, and states that a trunk change the spec decided is built without stopping.
- FR-008: The `implementer` shall decide every gap that changes only how the slice is built (naming, structure, module layout, seams within the plan) and list each decision in its report.
  - Acceptance: Given the agent file, when a reviewer reads it, then it states that such gaps are decided without stopping and reported as judgment calls.
- FR-009: The `implementer`'s final message shall be a report with: a status of `DONE`, `DONE_WITH_CONCERNS` with the doubt, `BLOCKED` with the condition, the decision that would clear it and what is uncommitted, or `TRUNK_READY` (FR-015); the files changed; the test files added, changed or deleted, and the command that runs them; each judgment call with its reason; and notes for later slices, limited to facts found in the code such as a convention, a gotcha or where a helper lives.
  - Acceptance: Given the agent file, when a reviewer reads its report section, then it lists those statuses and fields and forbids advice in notes.

Orchestrator: stops and trunk changes

- FR-010: When an `implementer` reports `BLOCKED`, the orchestrator shall put the question to the user with options and a recommendation, then resume the same agent with the answer through `SendMessage`; when that agent is no longer reachable, it shall dispatch a fresh `implementer` with the user's answer as a decision for the slice.
  - Acceptance: Given the skill, when a reviewer reads its handling of `BLOCKED`, then it asks the user, waits, resumes the same agent, and names the fresh-dispatch fallback.
- FR-011: When the `BLOCKED` condition is an undecided trunk change, the orchestrator shall first dispatch `skeptic` with the intent, the agent's description of the proposed change and the consumers of each touched symbol, and include the skeptic's verdict and strongest case against the change in the question to the user.
  - Acceptance: Given the skill, when a reviewer reads it, then `skeptic` is dispatched before the user is asked and its brief carries a description, not a staged diff.
- FR-012: `.claude/agents/skeptic.md` shall read the proposed change from its brief instead of `git diff --cached`, and its description shall name the `sdd-implement` orchestrator as its dispatcher and drop `refiner` and `code-reviewer`.
  - Acceptance: Given the file, when a reviewer reads its description and method, then neither reads the index, and neither names `refiner` or `code-reviewer`.
- FR-013: When the user approves a trunk change, the resumed `implementer` shall apply the proof bar before building it: every consumer is in the repository and updated with it, and the change does not alter a published package API, an external HTTP contract or a schema holding live data.
  - Acceptance: Given the agent file, when a reviewer reads it, then it states the proof bar and that a change failing it is reported `BLOCKED` again rather than built.
- FR-014: The `implementer` shall build an approved trunk change and its consumer updates before any further slice work, then report `TRUNK_READY` with the trunk change's paths.
  - Acceptance: Given the agent file, when a reviewer reads it, then trunk work comes first and ends in a `TRUNK_READY` report.
- FR-015: On `TRUNK_READY`, the orchestrator shall run the full suite, commit those paths alone with a body that opens with a `Trunk change:` line naming the touch point and its consumer count and records the skeptic's verdict and the user's decision, then resume the same agent to finish the slice.
  - Acceptance: Given the skill, when a reviewer reads it, then the trunk commit is verified by the full suite, made before the slice commit with that body, and followed by a resume.

Orchestrator: verify and commit

- FR-016: After an `implementer` reports `DONE` or `DONE_WITH_CONCERNS`, the orchestrator shall verify before committing:
  rerun each Done-when check of the slice;
  run the full suite with the repo's test tiers;
  confirm the reported test files equal the test files changed in the working tree;
  confirm, by diffing `tasks.md` against `HEAD`, that only this slice's task boxes went from unchecked to checked, each checked task gained exactly one Evidence line under it, Follow-ups gained only entries, and nothing else changed;
  and confirm `sdd status` reports `tasks.md` unchanged since approval.
  - Acceptance: Given the skill, when a reviewer reads its verify step, then it lists those five checks.
- FR-017: When a full-suite test fails, the orchestrator shall run that test at `HEAD` in a temporary git worktree; a test that also fails there is recorded as pre-existing and does not block the commit, and any other failure fails verification.
  - Acceptance: Given the skill, when a reviewer reads its failure handling, then it uses a temporary worktree, never the working tree, and records pre-existing failures in the commit body and the final report.
- FR-018: When verification fails, the orchestrator shall resume the same agent once with what it found; when verification fails again, it shall stop and report the failure to the user without committing.
  - Acceptance: Given the skill, when a reviewer reads its verification-failure handling, then it allows exactly one resume and then stops with the evidence.
- FR-019: When verification passes, the orchestrator shall check the slice's close-out box, stage the slice's files and `tasks.md` by explicit path, refuse the default branch, and commit without asking the user, with a body that records the slice's judgment calls from the report and any the orchestrator made.
  - Acceptance: Given the skill, when a reviewer reads its commit step, then the close-out box is checked before the commit so it lands in the same commit, `git add -A` and `git add .` are forbidden, the default branch is refused, no user prompt precedes the commit, and the body carries the judgment calls.

Orchestrator: resume

- FR-020: On start, the skill shall resume at the first slice whose close-out box is unchecked; when it starts with uncommitted changes, it shall list them and ask the user to choose between handing them to a fresh `implementer` to continue the slice and setting them aside by hand, and shall never discard them itself.
  - Acceptance: Given the skill, when a reviewer reads its start, then it states the resume point, the two options, and that it never discards work.
- FR-021: When the skill starts with every close-out box checked and `tasks.md` still `in-progress`, it shall resume at QA.
  - Acceptance: Given the skill, when a reviewer reads its start, then this state routes to QA.

Orchestrator: QA and finish

- FR-022: When every close-out box is checked, the orchestrator shall run `sdd lint` for the slug, then hand the user a QA script whose each observation maps to a Done-when check or an acceptance criterion, and wait.
  When the change has a runnable surface, it shall first start the app in the checkout (a `run-*` project skill when one exists, otherwise the repo's dev command as a background task) and reuse a server already running; when the change has none, or the app fails to start, the script names the commands and files to inspect instead, and a launch failure is reported once with its cause.
  - Acceptance: Given the skill, when a reviewer reads its QA step, then it states the lint, the mapping rule, the launch order, the no-surface and launch-failure behavior, and that it waits.
- FR-023: When the user reports a QA bug, the orchestrator shall dispatch a fresh `implementer` with the slug, the bug in the user's words with its reproduction steps, and the requirement IDs it touches, to fix it red-first; it shall verify the fix with the full suite and the test-file check, and commit it with a body naming the bug, the red test and its pass, then return to QA.
  - Acceptance: Given the skill, when a reviewer reads its QA-bug handling, then the brief, the two checks, the commit body and the return to QA are stated.
- FR-024: When the user confirms QA, the orchestrator shall set `tasks.md` to `done`, commit that change, stop every process it started while leaving any reused server running, and report: what was built, each stop with its resolution, the judgment calls of the agents and the orchestrator, any pre-existing failures, and the Follow-ups.
  - Acceptance: Given the skill, when a reviewer reads its finish step, then the status change follows QA confirmation and the report lists those five parts.
- FR-025: The orchestrator shall end by recommending `/sdd-review` in the same session, noting that the user may run it in a fresh session instead, and shall start it only when the user asked for an end-to-end run.
  - Acceptance: Given the skill's Next section, when a reviewer reads it, then it recommends `/sdd-review` in the same session, names the fresh-session alternative, and starts it only on an end-to-end request.

Render check

- FR-026: A new `render-check` skill with `disable-model-invocation: true` shall:
  take optional arguments naming the surfaces and a `--base` ref;
  find the base as the merge-base of `HEAD` with the `--base` ref or the default branch;
  take the touched surfaces from the arguments, else from changed paths matching the `applies-to:` globs of `docs/standards/ux-standards.md`, else from a spec whose scenarios or requirements name a surface;
  start the app or reuse a running one;
  dispatch `render-checker` with the URL, the surfaces and their states, the shipped themes, and the bar (the spec's requirements when there is one, `DESIGN.md`, and the `ux-standards.md` floors);
  report pass or fail per surface, width and theme with no fix loop;
  and stop every process it started.
  - Acceptance: Given `.claude/skills/render-check/SKILL.md`, when a reviewer reads it, then its frontmatter sets `disable-model-invocation: true` and its body states each of those steps.
- FR-027: `.claude/agents/render-checker.md`'s description shall name the `render-check` skill as its only dispatcher.
  - Acceptance: Given the file, when a reviewer reads its description, then it names `render-check` and not `refine`.

Removals and docs

- FR-028: The `refine` skill, the `refiner` and `code-reviewer` agents, and `docs/specs/` shall be deleted, and every tracked file outside `docs/sdd/` and `CHANGELOG.md` shall name only skills and agents that exist; the changelog is excluded because its entries must name what they removed.
  - Acceptance: Given the repository, when a reviewer runs `git grep -nwE 'refine|refiner|code-reviewer|template-sync|template-feedback|builder|implement-spec|run-skill-generator'` outside those exclusions, then no match names a skill or agent, and `CLAUDE.md` and `README.md` list skills and agents by name without stating a count.
- FR-029: The `[P]` task marker shall be removed from the SDD document's task shape and rules, Appendix C and the generated tasks template, and the helper's `[P]` lint and its tests shall be removed.
  - Acceptance: Given the branch, when a reviewer greps the SDD document, `.claude/sdd/templates/` and `.claude/sdd/bin/sdd` for `[P]`, then nothing matches, and the helper's unittest suite passes.
- FR-030: `.claude/rules/skill-authoring.md` shall drop the `sdd-implement` exemption from "code work runs in agents".
  - Acceptance: Given the rule file, when a reviewer reads it, then no exemption names `sdd-implement`.
- FR-031: The SDD document shall state that the `sdd-implement` orchestrator commits slice work, approved trunk changes, QA fixes and the `done` status against the approved spec, that the user QAs at the end, that the user still commits gate artifacts and `sdd-review` fixes, and that nothing is pushed.
  - Acceptance: Given `.claude/sdd/spec-driven-development.md`, when a reviewer reads the whole document, then no line says the user commits slice work or that a fresh session is needed between slices or before `sdd-review`, section 4's exit gate allows recorded pre-existing failures, section 12's Fixes no longer compares itself to a slice commit, and section 4's gate rules carry no `sdd-implement` exception.
- FR-032: Section 10 of the SDD document shall describe the orchestrated flow of FR-001 to FR-025.
  - Acceptance: Given section 10, when a reviewer compares it with the skill, then their steps agree and `.claude/sdd/bin/sdd templates sync --check` and `check-refs` pass.
- FR-033: `CHANGELOG.md`'s unreleased v0.3.0 entry shall absorb this change: rewrite its lines this change makes false, and add what changed, why, and adaptation notes for projects with a customized `sdd-implement` or `refine`.
  - Acceptance: Given `CHANGELOG.md`, when a reviewer reads the v0.3.0 entry, then it has those three parts for this change and no line contradicts the repository.
- FR-034: `CLAUDE.md` shall state the skill body budget the rule uses (5000 tokens), and `.ai-starter.yaml` and `scripts/test/ai-starter-version.battery.mjs` shall not describe `template-sync`.
  - Acceptance: Given those files, when a reviewer reads them, then `CLAUDE.md` matches `.claude/rules/skill-authoring.md` and no line names `template-sync`.

Review

- FR-035: When the user picks findings to fix, `sdd-review` shall dispatch a fresh `implementer` per finding with the slug (when there is one), the finding verbatim with its `file:line`, and the requirement IDs it touches, to fix it red-first; it shall verify the report with the full suite and the changed-path match FR-016 describes, and commit only on the user's word.
  - Acceptance: Given `.claude/skills/sdd-review/SKILL.md` and section 12 of the SDD document, when a reviewer reads their Fixes steps, then the fix is built by a fresh `implementer` with that brief, the session never builds it through `tdd` itself, and the verification and commit rule are stated.
- FR-036: `sdd-review` shall run every reviewer in a fresh context whose brief carries only pointers (the artifact paths, the repository root, the base and the range), and the SDD document shall say so, naming that `code-review` runs as a forked skill that does not see the conversation.
  - Acceptance: Given section 12 and the skill, when a reviewer reads them, then each of the conformance subagent, `code-review` and `standards-reviewer` is described as running in a fresh context with a pointer-only brief, and section 12 states that the session running the review may be the one that ran the build.

### Non-functional

- NFR-001: Every changed skill body shall stay within the 5000-token budget in `.claude/rules/skill-authoring.md`, measured before landing.
- NFR-002: `pnpm test:scripts` shall pass on the branch, covering the helper's unittest suite, the template drift check and the section-reference check.
- NFR-003: Removed 2026-11-02: the fixture dry run is replaced by the gut-check handoff `.claude/rules/skill-authoring.md` already requires.

## Invariants

- INV-001: The orchestrator shall never write a file outside the writes FR-002 allows.
- INV-002: No skill or agent shall push, open a pull request, or commit on the default branch.
- INV-003: No skill or agent shall dispatch `render-checker` except the `render-check` skill.
- INV-004: Removed 2026-11-02: `sdd-implement` may start `sdd-review` on an end-to-end request, since the review's independence comes from its fresh-context reviewers, not a fresh session.
- INV-005: No skill or agent shall discard uncommitted work it did not create.

## Edge cases and failure behavior

- The run starts on the default branch: the orchestrator proposes the spec's branch and asks before creating it, as section 10 does today.
- An `implementer` edits `tasks.md` outside what FR-006 allows: verification fails and the agent is resumed once to revert that edit.
- A slice has no test files (documentation-only): the test-file check passes when both the report and the diff list none.
- The user declines a trunk change: the agent is resumed with the decision and builds around the change, or reports `BLOCKED` again when the slice cannot finish without it.
- The trunk commit's full suite fails: verification fails as in FR-018, with the trunk paths as the scope.
- A `BLOCKED` agent is lost because the session ended: FR-010's fresh-dispatch fallback applies on resume, with the user's answer as a decision for the slice.
- The app fails to start for QA: FR-022's launch-failure behavior applies.

## Existing behavior

These exist today and are reused, not rebuilt:

- The `sdd` helper's `status`, `lint`, `hash`, `set-status` and `approve` commands, and the content hash that resets checkboxes and drops Evidence lines and Follow-ups.
- Section 10's branch check, Evidence line format and slice close-out item.
- The `tdd` skill and its discovery reference `.claude/skills/tdd/references/discover.md`.
- `refine`'s `BLOCKED` and `SendMessage` resume pattern, its app lifecycle rules, its QA script rules, and its base and touched-surface discovery, which move into `sdd-implement` and `render-check`.
- The `render-checker` agent's behavior; only its dispatcher changes.
- The `guard-main` hook in `.claude/hooks/guard-main.mjs`, which blocks default-branch pushes and commits.

## Assumptions

- A-001: Orchestrator commits are limited to `sdd-implement` (slice work, approved trunk changes, QA fixes and the `done` status); gate artifacts and `sdd-review` fixes stay user-committed. Accepted by Conner Donohoo.
- A-002: Porting this change into Fantasy Draft Lab is a hand copy after merge, outside this spec. Accepted by Conner Donohoo.

## Glossary

| Term          | Meaning                                                                                                                                                                                       |
| ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Orchestrator  | The session running `sdd-implement`: dispatches, verifies, commits and talks to the user, writing only what FR-002 allows.                                                                    |
| Implementer   | The `implementer` agent: builds one slice, one trunk change, one QA fix or one review fix in a fresh context and reports back.                                                                |
| Trunk change  | A change to a shared utility, public interface, schema or config that existed before the branch.                                                                                              |
| Judgment call | A decision that changes only how the slice is built, made by an agent or the orchestrator without asking the user.                                                                            |
| Interruption  | A point where the orchestrator waits for the user: a `BLOCKED` report (FR-007), a second verification failure (FR-018), uncommitted work at start (FR-020), or a start on the default branch. |
| Proof bar     | The FR-013 test an approved trunk change must pass before it is built.                                                                                                                        |

## Changelog

- 2026-11-02: Removed NFR-003 (fixture dry run) at the owner's request; P1 and P2 are proven through the skill-authoring gut-check prompts instead. CLAUDE.md and README.md drop skill and agent counts rather than keep them in sync.
- 2026-11-02: After review, `sdd-implement` recommends `sdd-review` in the same session (FR-025 revised, INV-004 removed), since the review's independence comes from its fresh-context reviewers; review fixes go to a fresh `implementer` (FR-035); every reviewer runs on a pointer-only brief (FR-036); FR-028 excludes all of `CHANGELOG.md`, as the owner decided during the build.
