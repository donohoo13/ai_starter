---
title: Implement orchestrator tasks
slug: implement-orchestrator
status: in-progress
updated: 2026-11-02
based_on: a3a4636ee56d
approved_hash: d21c47a34aa8
---

# Implement orchestrator tasks

## P1: Orchestrated slice build

- [x] T001 The implementer agent exists, preloads `tdd` and pins `opus`, and a battery guards both
  - Requirements: FR-004
  - Seam: the new battery, run by `pnpm test:scripts`
  - Files: scripts/test/process-suite.battery.mjs, .claude/agents/implementer.md
  - Done when: `node scripts/test/process-suite.battery.mjs` passes, after failing on the missing `implementer.md`
  - Evidence: red `FAIL .claude/agents/implementer.md exists with frontmatter`; green 3 ok (exists, preloads tdd, pins model opus), prettier clean
- [x] T002 The implementer builds each task of its slice through `tdd`, self-checks its diff against the matching standards, and edits `tasks.md` only in its own boxes, Evidence lines and Follow-ups
  - Requirements: FR-004, FR-005, FR-006
  - Seam: read by the conformance pass
  - Files: .claude/agents/implementer.md
  - Depends on: T001
  - Done when: `grep -c 'applies-to' .claude/agents/implementer.md` is at least 1 and the method names the task as the behavior, the task's seam, the Done-when check, the no-key rule, and forbids commit, push and branch switch
  - Evidence: grep counts applies-to 1, behavior/seam/Done-when 2, no-key rule 1, commit/push/switch ban 1; Build a slice, Check against the standards and Boundaries sections read against FR-004 to FR-006
- [x] T003 The implementer stops on the five conditions and decides only how-it-is-built gaps itself
  - Requirements: FR-007, FR-008
  - Seam: read by the conformance pass
  - Files: .claude/agents/implementer.md
  - Depends on: T001
  - Done when: the stop section lists exactly the five FR-007 conditions, names the "Ask first" source, exempts spec-decided trunk changes, and states FR-008's decide-and-report rule
  - Evidence: When to stop holds 5 bullets; "Ask first" source (CLAUDE.md, else SDD section 6) 1, spec-decided trunk exemption 1, judgment-call rule 1
- [x] T004 The implementer applies the proof bar and builds an approved trunk change first, ending in `TRUNK_READY`
  - Requirements: FR-013, FR-014
  - Seam: read by the conformance pass
  - Files: .claude/agents/implementer.md
  - Depends on: T003
  - Done when: `grep -c 'TRUNK_READY' .claude/agents/implementer.md` is at least 1 and the trunk section states the proof bar and the re-`BLOCKED` path
  - Evidence: `grep -c TRUNK_READY` 2; Trunk changes section states the proof bar (in-repo consumers; no published API, external contract or live-data schema), build-first, and BLOCKED again on failure
- [x] T005 The implementer ends with the report contract
  - Requirements: FR-009
  - Seam: read by the conformance pass
  - Files: .claude/agents/implementer.md
  - Depends on: T004
  - Done when: the report section lists the four statuses and the five fields of FR-009 and forbids advice in notes
  - Evidence: Report section has 5 bold fields, the status line lists DONE, DONE_WITH_CONCERNS, BLOCKED and TRUNK_READY, and notes say "never advice"
- [x] T006 The orchestrator dispatches one implementer per slice with a pointer-only brief at effort high, and writes only what FR-002 allows
  - Requirements: FR-001, FR-002, FR-003, INV-001
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T005
  - Done when: `grep -c 'Skill tool' .claude/skills/sdd-implement/SKILL.md` is 0, the skill names `implementer`, `effort: high` with the per-run override, the four brief inputs, and the FR-002 write list
  - Evidence: `grep -c 'Skill tool'` 0; implementer 7, effort-high-with-override 1, four-input brief 1, "What this session writes" lists 4 writes
- [x] T007 The orchestrator handles `BLOCKED` by asking the user and resuming the same agent, dispatching `skeptic` first for a trunk change, and `skeptic` reads its brief instead of the index
  - Requirements: FR-010, FR-011, FR-012
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md, .claude/agents/skeptic.md
  - Depends on: T006
  - Done when: `grep -cE 'diff --cached|refiner|code-reviewer' .claude/agents/skeptic.md` is 0 and the skill states the `SendMessage` resume and the fresh-dispatch fallback
  - Evidence: skeptic stale-reference grep 0; skill SendMessage 3, fresh-dispatch fallback 1, skeptic dispatched before the user is asked 1
- [x] T008 The orchestrator commits a verified trunk change alone and resumes the agent
  - Requirements: FR-015
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T007
  - Done when: the skill runs the full suite on `TRUNK_READY`, commits with a body opening `Trunk change:`, and resumes the same agent
  - Evidence: Trunk commit section has the full suite 1, the `Trunk change: <touch point>` body 1, the same-agent resume 1
- [x] T009 The orchestrator verifies every slice with five checks, separates pre-existing failures in a temporary worktree, and allows one retry
  - Requirements: FR-016, FR-017, FR-018
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T008
  - Done when: `grep -c 'git worktree' .claude/skills/sdd-implement/SKILL.md` is at least 1 and the verify step lists the five FR-016 checks and the single resume
  - Evidence: `grep -c 'git worktree'` 1; Verify lists 5 numbered checks; resume-once 1, second failure stops without a commit
- [x] T010 The orchestrator ticks the close-out and commits the slice without asking, refusing the default branch
  - Requirements: FR-019, INV-002
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T009
  - Done when: the commit step ticks the close-out before committing, forbids `git add -A` and `git add .`, refuses the default branch, never pushes, and records judgment calls in the body
  - Evidence: Slice commit has close-out-first 1, add -A/. ban 1, default-branch refusal 1, Never push 1, judgment calls in body 1
- [x] T011 The orchestrator resumes at the first unchecked close-out, routes a fully closed list to QA, and never discards uncommitted work
  - Requirements: FR-020, FR-021, INV-005
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T010
  - Done when: the start section states both resume points and the two options for uncommitted work, with no discard step
  - Evidence: Start has first-unchecked-close-out 1, all-closed-and-in-progress route 1 (to Finish until T014 adds QA), two options 1, no-discard 1
- [x] T012 Skill-authoring no longer exempts `sdd-implement` from code work in agents
  - Requirements: FR-030
  - Seam: read by the conformance pass
  - Files: .claude/rules/skill-authoring.md
  - Done when: `grep -c 'sdd-implement' .claude/rules/skill-authoring.md` is 0
  - Evidence: `grep -c 'sdd-implement' .claude/rules/skill-authoring.md` 0; rules-frontmatter battery passes
- [x] T013 The SDD document gives slice commits to the orchestrator and describes the orchestrated build in section 10
  - Requirements: FR-031, FR-032, INV-001
  - Seam: `sdd templates sync --check` and `sdd check-refs` through `sdd-helper.battery.mjs`
  - Files: .claude/sdd/spec-driven-development.md
  - Depends on: T011
  - Done when: `node scripts/test/sdd-helper.battery.mjs` passes and no line in sections 1, 2, 4, 10, 11 or 15 says the user commits slice work or recommends a fresh session between slices
  - Evidence: sdd-helper battery 3/3 (unit tests, templates in sync, 46 refs 0 mismatched); scan of sections 1-4, 10-11, 15 finds only gate-artifact commit lines; section 9 rule and Appendix C close-out also updated, tasks template regenerated
- [x] P1 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## P2: End-of-run QA and report

- [x] T014 After the last slice, the orchestrator lints, launches or reuses the app when there is a runnable surface, and hands over a QA script mapped to the checks
  - Requirements: FR-022
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Done when: the QA step states the lint, the launch order, server reuse, the no-surface and launch-failure scripts, the mapping rule, and that it waits
  - Evidence: QA section greps: sdd lint 1, run-\* then dev-command launch 1, server reuse 1, no-surface script 1, launch failure 1, mapping rule 1, stop and wait 1
- [x] T015 A QA bug goes to a fresh implementer as a red-first fix, verified and committed, then QA resumes
  - Requirements: FR-023
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md, .claude/agents/implementer.md
  - Depends on: T014
  - Done when: the skill states the QA-fix brief, the full suite and test-file checks, the commit body, and the return to QA, and the agent describes its QA-fix mode
  - Evidence: QA bug greps: user's-words brief 1, full suite and test-file check 1, red-test body 1, return to QA 1; implementer has `## Fix a QA bug` 1
- [x] T016 On QA confirmation the orchestrator sets `done`, commits it, stops its processes, and reports the five parts
  - Requirements: FR-024
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T015
  - Done when: the finish step follows QA confirmation, commits the status change, keeps reused servers running, and lists the five report parts
  - Evidence: Finish greps: after QA confirmation 1, commits the status change 1, reused server left running 1, five-part report line 1
- [x] T017 The orchestrator recommends `/sdd-review` in a fresh session and never starts it, and the SDD document carries the end-to-end exception, the pre-existing-failure exit gate and section 12's new Fixes wording
  - Requirements: FR-025, FR-031
  - Seam: `sdd check-refs` through `sdd-helper.battery.mjs`
  - Files: .claude/skills/sdd-implement/SKILL.md, .claude/sdd/spec-driven-development.md
  - Depends on: T016
  - Done when: `node scripts/test/sdd-helper.battery.mjs` passes, the skill's Next forbids starting `sdd-review` in every case, and `grep -c 'exactly as for a slice' .claude/sdd/spec-driven-development.md` is 0
  - Evidence: sdd-helper battery 3/3; skill Next "Never start it from here, even when the user asked for an end-to-end run" 1; doc `exactly as for a slice` 0; section 4 gate rule exception and exit gate with pre-existing failures and QA added
- [x] P2 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## P3: Retire refine; render checks on demand

- [x] T018 A user-only `render-check` skill discovers its base, surfaces and bar, runs `render-checker`, and only reports
  - Requirements: FR-026
  - Seam: the battery
  - Files: .claude/skills/render-check/SKILL.md, scripts/test/process-suite.battery.mjs
  - Done when: `node scripts/test/process-suite.battery.mjs` passes its new `render-check` user-only check, after failing on the missing skill
  - Evidence: red `FAIL .claude/skills/render-check/SKILL.md exists with frontmatter`; green `ok ... is user-only`; skill covers base, surfaces, states, themes, bar, app, dispatch, report-only, cleanup (~885 est tokens)
- [x] T019 Only `render-check` dispatches `render-checker`, with `refine` deleted
  - Requirements: FR-027, FR-028, INV-003
  - Seam: the battery
  - Files: .claude/agents/render-checker.md, .claude/skills/refine/SKILL.md, scripts/test/process-suite.battery.mjs
  - Depends on: T018
  - Done when: `node scripts/test/process-suite.battery.mjs` passes its sole-dispatcher check, after failing while `refine` named `render-checker`
  - Evidence: red `FAIL only render-check dispatches render-checker — also named in .claude/skills/refine/SKILL.md`; green after the description retarget and `git rm -r .claude/skills/refine`
- [x] T020 No agent is orphaned, with `refiner`, `code-reviewer` and `docs/specs/` deleted
  - Requirements: FR-028
  - Seam: the battery
  - Files: .claude/agents/refiner.md, .claude/agents/code-reviewer.md, docs/specs/001-refine.md, scripts/test/process-suite.battery.mjs
  - Depends on: T019
  - Done when: `node scripts/test/process-suite.battery.mjs` passes its no-orphan check, after failing on `refiner` and `code-reviewer`, and `test ! -e docs/specs` succeeds
  - Evidence: red FAIL for code-reviewer and refiner (no skill names them); green after `git rm`, 5 remaining agents each named by a skill; `test ! -e docs/specs` succeeds
- [x] P3 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## P4: Docs reflect the repository

- [x] T021 The `sdd` helper no longer parses or lints a parallel marker, and the document, template and `sdd-task` no longer offer one
  - Requirements: FR-029
  - Seam: the helper's `unittest` suite
  - Files: .claude/sdd/bin/sdd, .claude/sdd/tests/test_lint_tasks.py, .claude/sdd/tests/test_status.py, .claude/sdd/tests/helpers.py, .claude/sdd/spec-driven-development.md, .claude/sdd/templates/tasks.md, .claude/skills/sdd-task/SKILL.md
  - Done when: `node scripts/test/sdd-helper.battery.mjs` passes, including a new test that two tasks sharing a file and depending on each other lint clean, which failed before the change
  - Evidence: new test red ("T002 is [P] but depends on T001 in the same slice", 2 errors), green after removing TASK_TEXT's group and lint_parallel; sdd-helper battery 3/3; `[P]` count across doc, templates and helper 0
- [x] T022 No tracked file outside `docs/sdd/` and released changelog entries names a removed skill or agent, and no doc states a skill or agent count
  - Requirements: FR-028, FR-034
  - Seam: the battery
  - Files: scripts/test/process-suite.battery.mjs, CLAUDE.md, README.md, .claude/skills/README.md, .claude/sdd/README.md, .ai-starter.yaml, scripts/test/ai-starter-version.battery.mjs
  - Depends on: T021
  - Done when: `node scripts/test/process-suite.battery.mjs` passes its removed-name check, after failing on `CLAUDE.md`, and `CLAUDE.md` states the 5000-token budget
  - Evidence: red with 20 matches incl. CLAUDE.md:67; green `ok no tracked file names a removed skill or agent` after the sweep (also .claude/rules/template-dev.md); CLAUDE.md:70 says 5000 tokens; count grep finds none
- [x] T023 The unreleased v0.3.0 changelog entry describes this change and nothing in it contradicts the repository
  - Requirements: FR-033
  - Seam: read by the conformance pass
  - Files: CHANGELOG.md
  - Depends on: T022
  - Done when: the v0.3.0 entry has what, why and adaptation notes for this change, and `node scripts/test/process-suite.battery.mjs` still passes
  - Evidence: v0.3.0 gains 7 What bullets, 3 Why lines and 4 adaptation notes; stale refine, skill-authoring, template-sync and sync-worded lines rewritten; process-suite battery passes
- [x] T024 Every changed skill body measures under the token budget
  - Requirements: NFR-001
  - Seam: measurement
  - Files: .claude/skills/sdd-implement/SKILL.md, .claude/skills/render-check/SKILL.md, .claude/skills/sdd-task/SKILL.md
  - Depends on: T023
  - Done when: for each file, the body's `wc -c` divided by 4 is under 4500, with each figure recorded in the Evidence line
  - Evidence: body chars/4: sdd-implement 9741/4 ≈ 2435, render-check 3080/4 ≈ 770, sdd-task 4421/4 ≈ 1105, all under 4500
- [x] T025 The gut-check prompts for `sdd-implement`, `implementer` and `render-check` are written for a fresh session
  - Requirements: FR-001, FR-022, FR-026
  - Seam: read by the owner
  - Files: docs/sdd/implement-orchestrator/gut-check.md
  - Depends on: T024
  - Done when: the file holds two or three task prompts with expected behavior per skill, and should-trigger and near-miss should-not-trigger prompts for each changed description
  - Evidence: gut-check.md has 3 sdd-implement and 2 render-check task prompts, 1 implementer report check, 5 should-trigger and 4+3 near-miss prompts, 6 "Passes when" expectations
- [x] P4 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## P5: Same-session review

- [ ] T026 `sdd-implement` recommends `/sdd-review` in the same session, names the fresh-session alternative, and starts it only on an end-to-end request, and the SDD document drops the `sdd-implement` exception
  - Requirements: FR-025, FR-031
  - Seam: `sdd check-refs` through `sdd-helper.battery.mjs`
  - Files: .claude/skills/sdd-implement/SKILL.md, .claude/sdd/spec-driven-development.md
  - Done when: `node scripts/test/sdd-helper.battery.mjs` passes, `grep -c 'never starts .sdd-review.' .claude/sdd/spec-driven-development.md` is 0, and the skill's Next names the same session, the fresh-session alternative and the end-to-end start
- [ ] T027 `sdd-review` builds each picked fix through a fresh `implementer`, verifies it, and leaves the commit to the user
  - Requirements: FR-035
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-review/SKILL.md, .claude/agents/implementer.md, .claude/sdd/spec-driven-development.md
  - Depends on: T026
  - Done when: the skill's and section 12's Fixes dispatch `implementer` with the finding brief and never invoke `tdd` themselves, and the agent describes its review-fix mode
- [ ] T028 `sdd-review` and section 12 state that every reviewer runs in a fresh context on a pointer-only brief, with `code-review` as a forked skill
  - Requirements: FR-036
  - Seam: `sdd check-refs` through `sdd-helper.battery.mjs`
  - Files: .claude/skills/sdd-review/SKILL.md, .claude/sdd/spec-driven-development.md
  - Depends on: T027
  - Done when: `node scripts/test/sdd-helper.battery.mjs` passes and section 12 names the fresh contexts, the pointer-only briefs, the forked `code-review`, and that the reviewing session may be the one that built
- [ ] T029 The skills README, the changelog and the gut-check prompts describe the same-session review
  - Requirements: FR-025, FR-033
  - Seam: the battery
  - Files: .claude/skills/README.md, CHANGELOG.md, docs/sdd/implement-orchestrator/gut-check.md
  - Depends on: T028
  - Done when: `node scripts/test/process-suite.battery.mjs` passes and `grep -c 'fresh session without' .claude/skills/README.md CHANGELOG.md docs/sdd/implement-orchestrator/gut-check.md` reports 0 for each
- [ ] P5 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## Verified elsewhere

- NFR-002: every slice close-out runs `pnpm test:scripts`, which runs the helper suite, the template drift check, the section-reference check and the process-suite battery. Decided by Conner Donohoo.

## Follow-ups (out of scope)

- The pre-commit hook runs `prettier --write` after `sdd approve` records a hash, so an approved artifact reads as changed; the gate skills or the helper should format before hashing.
- FR-028 says only released changelog entries may name removed skills, but FR-033 requires the unreleased entry to name `refine` in its adaptation notes; the owner chose to exclude `CHANGELOG.md` from the removed-name check, so FR-028's exclusion wording should say so.
- `.claude/rules/template-dev.md` still describes the template's release process around `.ai-starter.yaml`; with `template-sync` gone, whether that file and `ai-starter-version.battery.mjs` still earn their place is the owner's call.
