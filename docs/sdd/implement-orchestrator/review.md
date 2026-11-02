---
title: Implement orchestrator review
slug: implement-orchestrator
status: accepted
base: main
range: main..50c18c5
effort: high
max_findings: 5
updated: 2026-11-02
---

# Implement orchestrator review

## Spec conformance

Evidence run on the clean tree: `pnpm test:scripts` exit 0 (7 batteries, including process-suite 12 ok and sdd-helper 3/3), `pnpm format:check` clean, `pnpm test` no packages.

| Requirement      | Met     | Evidence                                                                                                                                                           |
| ---------------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| FR-001 to FR-003 | yes     | `.claude/skills/sdd-implement/SKILL.md:16-26,57-61`; conformance read                                                                                              |
| FR-004           | yes     | `.claude/agents/implementer.md:4-6,22-28`; process-suite "preloads tdd", "pins model opus"                                                                         |
| FR-005, FR-006   | yes     | `implementer.md:27-43,83`; matches `standards-reviewer.md:18`                                                                                                      |
| FR-007           | partial | `implementer.md:53-60` lists the five conditions, but `:85` and section 10's "If the plan turns out to be wrong, stop" add stops outside the "only when" list (C6) |
| FR-008 to FR-014 | yes     | `implementer.md:62-95`; `SKILL.md:65-77`; `skeptic.md:3,11,14`                                                                                                     |
| FR-015 to FR-019 | yes     | `SKILL.md:72-103`, with the defects in C1 to C4                                                                                                                    |
| FR-020 to FR-025 | yes     | `SKILL.md:44-47,109-142`                                                                                                                                           |
| FR-026, FR-027   | yes     | `render-check/SKILL.md:5`, `render-checker.md:3`; process-suite "is user-only", "only render-check dispatches render-checker"                                      |
| FR-028           | partial | Deletions done; removed-name check passes; the check excludes all of `CHANGELOG.md`, wider than the spec's "released entries" (R2)                                 |
| FR-029           | yes     | `.claude/sdd/bin/sdd:274`; `test_lint_tasks.py::test_tasks_in_a_slice_may_share_files_and_depend_on_each_other`                                                    |
| FR-030 to FR-034 | yes     | `skill-authoring.md` diff; `spec-driven-development.md:62-63,84-86,136-140,169,222,230,572-635,742,807-818`; `CHANGELOG.md` v0.3.0; `CLAUDE.md:70`                 |
| NFR-001          | yes     | body chars/4: sdd-implement ≈ 2435, render-check ≈ 770, sdd-task ≈ 1105                                                                                            |
| NFR-002          | yes     | `pnpm test:scripts` exit 0 on the clean tree                                                                                                                       |
| INV-001 to 005   | yes     | conformance found no breaking path; INV-002 also held by `guard-main.mjs:222`                                                                                      |

## Correctness findings

- [high] `.claude/skills/sdd-implement/SKILL.md:89`: C1. The pre-existing-failure check runs the failing test in a fresh `git worktree` at `HEAD`, which lacks the slice's new test files and installed dependencies, so a regression in a test the slice added fails there too and is recorded as pre-existing.
- [medium] `.claude/skills/sdd-implement/SKILL.md:100`: C2. The slice commit stages only the report's files and Verify cross-checks only test files, so a non-test file the agent changed but left off the report is never committed; relatedly, after a trunk commit the agent's report can list already-committed trunk tests and fail the test-file check.
- [medium] `.claude/skills/sdd-implement/SKILL.md:86`: C3. Verify's `tasks.md` diff against `HEAD` allows only slice boxes, Evidence and Follow-ups, but on the first slice the orchestrator's own uncommitted `status: in-progress` is also in the diff, so a literal reading fails verification twice and stops the run.
- [low] `.claude/skills/sdd-implement/SKILL.md:54`: C4. The orchestrator may rewrite the spec's `branch` field but never stages `spec.md`, so the exit gate's clean tree cannot hold after a branch rename.
- [medium] `scripts/test/process-suite.battery.mjs:63`: C5. The battery requires `model: opus`, but the changelog tells projects to change `model:` for a different build model, so following the documented adaptation turns child CI red.
- [low] `.claude/agents/implementer.md:85`: C6 (from conformance G1). "Never weaken a check" routes to `BLOCKED` and section 10 says to stop when the plan is wrong, both outside the "only when" list of five stop conditions.

## Standards findings

- `.claude/sdd/tests/test_lint_tasks.py:77`: the test name omits the `[P]` marker the test exists for. Fails: "A test name states the behavior in the caller's words"
- `scripts/test/process-suite.battery.mjs:147-151`: `asName` is an unexplained ERE delimiter puzzle beside JS regexes. Fails: "No clever one-liners" / "Names say what a thing is or does"
- `.claude/skills/sdd-implement/SKILL.md:25`: an appositive list inside a sentence takes two reads; Blocked step 3 lacks "act on its next report" and Verify never says a pass goes to Slice commit. Fails: "Expressing and communicating ideas should always be expressed with simple and clear grammar"

## Reads well

- `implementer.md` separates `BLOCKED` conditions from judgment calls, and its Report names exactly what the orchestrator's Verify checks.
- Section 10, principle 10 and the MUST lists were rewritten under the new model rather than patched.
- `process-suite.battery.mjs` follows the sibling batteries: `check()`, `ok`/`FAIL` lines, one named function per check, a definitive last line.

## Rejected findings

- R1 (conformance G2): the removed-name check misses plain-prose "refine" and "builder". Kept by design: both are ordinary English ("builder functions", `builder.setName` in `docs/standards/design-principles.md:49`), so a plain match would fail on correct prose; the six unambiguous names still match anywhere.
- R2 (conformance G3): FR-028's text says released changelog entries, the battery excludes all of `CHANGELOG.md`. Not a code defect: the owner chose this during the build because FR-033 requires the unreleased entry to name `refine`; the spec wording is logged as a Follow-up in `tasks.md`.
- Correctness, unlisted: `docs/notes/` is not excluded from the removed-name check. No file there names a removed skill today; excluding it pre-emptively adds a rule nothing needs.
- Standards, out of lens: the battery resolves paths from `process.cwd()`. Every sibling battery does the same and `pnpm test:scripts` always runs from the root.

## Fixes

- C1 → Verify treats a failing test in a file the slice added or changed as the slice's own, and checks any other failure at `HEAD` in a temporary worktree with dependencies installed; section 10 matches.
- C2 → Verify matches the report's files against every path `git status --porcelain` lists, and the trunk-commit resume tells the agent to report only what it changes afterwards.
- C3, C4 → the orchestrator commits its own start writes (`status: in-progress`, a renamed `branch`) before the first dispatch, so later diffs hold only an agent's work and the tree can end clean.
- C5 → the battery requires a pinned model rather than `opus`; red shown in a throwaway worktree with `model: sonnet` (`FAIL ... pins model opus`), green after the change in both that worktree and the repo.
- C6 → `implementer.md` routes "no fix but weakening a check" to the same-approach-failed-twice condition, and section 10 routes a wrong plan to the contradiction condition, so the five stop conditions stay the whole list.
- Standards → the `[P]` test is renamed `test_a_leftover_parallel_marker_no_longer_constrains_shared_files_or_dependencies`; the battery's pattern is built from named delimiter parts; `SKILL.md` splits the appositive sentence, Blocked acts on the next report, and Verify names the hand-off to Slice commit.
- Validation: `pnpm test:scripts` exit 0, `pnpm format:check` clean, `sdd templates sync --check` in sync.
- Intent change after review → the owner moved the review into the same session (spec FR-025 revised, INV-004 removed, FR-035 and FR-036 added); built as slice P5 in `bbcf126`. The owner accepted the branch without rerunning the reviewers on the fixes or on P5.

## PR description draft

### Summary

`sdd-implement` built every task of an approved `tasks.md` inside the session that invoked it, and the user committed each slice by hand.
That session carried the whole build in one context, and nothing separated the context that wrote a slice from the one that checked it.
A long task list filled the context until the skill told the user to restart between slices, and a separate `refine` pass then rewrote finished code to the same standards `sdd-review` judged again.
This change makes `sdd-implement` an orchestrator that dispatches one fresh `implementer` agent per slice, verifies its work with its own checks, and commits each verified slice, then hands the user one QA pass.
Each slice is built from pointers into the approved artifacts in a context that never saw the planning, and checked by a session that did not write it.
`refine` is gone, render checks run only when the user starts `/render-check`, and `sdd-review` follows in the same session through reviewers that each run in a fresh context.

### What changed

- New `implementer` agent: builds one slice, one approved trunk change, or one QA or review fix, test-first under a preloaded `tdd`, self-checks against the matching `docs/standards/` files, stops only on five named conditions, and never commits.
- `sdd-implement` rewritten as the orchestrator: pointer-only briefs at `effort: high`, `BLOCKED` questions to the user with `skeptic` first for an undecided trunk change, a separately committed trunk change, five verification checks, a commit per slice, one QA pass before `done`, and a same-session handoff to `sdd-review`.
- `sdd-review` builds picked fixes through a fresh `implementer` and states that every reviewer runs in a fresh context; `skeptic` argues a proposed change from its brief.
- `refine`, `refiner`, `code-reviewer` and `docs/specs/` removed; `/render-check`, user-only, now runs `render-checker`.
- The SDD document gives slice commits to the orchestrator (principle 10, Roles, sections 1, 4, 9, 10, 12, 15), rewrites section 10, and drops the `[P]` marker with its template line, `sdd-task` instruction and helper lint.
- `scripts/test/process-suite.battery.mjs` locks the suite's structure: the implementer preloads `tdd` and pins a model, `render-check` is user-only and the only dispatcher of `render-checker`, every agent is named by a skill, and no tracked file outside `docs/sdd/` and `CHANGELOG.md` names a removed skill or agent.
- Docs sweep: `CLAUDE.md`, the READMEs, `template-dev.md`, `.ai-starter.yaml` and the version battery describe only what exists, without skill counts, and the v0.3.0 changelog entry records the change.

### How it was verified

- `pnpm test:scripts`: exit 0 at every slice close and on the final tree (7 batteries; process-suite 12 checks; sdd-helper unit tests, template drift and 46 section references).
- `pnpm format:check`: clean.
- Red first where a test could hold the behavior: each process-suite check failed before its change, the `[P]` helper test failed before the lint was removed, and the model check failed in a throwaway worktree with `model: sonnet`.
- `sdd-review` at `high`, cap 5: spec conformance found every requirement met but FR-007 and FR-028 partial; `code-review` reported five defects and the conformance pass one more, all fixed in `f5f048c`; three standards items fixed in the same commit.
- Not run: the gut-check prompts in `docs/sdd/implement-orchestrator/gut-check.md`, and a second review pass over the fixes and P5.

### Decisions and follow-ups

- The orchestrator commits slice work without asking; the user still commits gate artifacts and review fixes.
- The removed-name check excludes `CHANGELOG.md`, and matches `refine` and `builder` only as names so ordinary English passes.
- Follow-up: the pre-commit `prettier --write` changes an approved artifact's hash; the gate skills or the helper should format before `sdd approve`.
- Follow-up: decide whether `.ai-starter.yaml` and its battery still earn their place now that releases are taken by hand.
- Follow-up: port the change into Fantasy Draft Lab by hand.
