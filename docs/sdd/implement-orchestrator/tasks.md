---
title: Implement orchestrator tasks
slug: implement-orchestrator
status: approved
updated: 2026-11-02
based_on: 1f38a952fdb6
approved_hash: e2f23863cfe8
---

# Implement orchestrator tasks

## P1: Orchestrated slice build

- [ ] T001 The implementer agent exists, preloads `tdd` and pins `opus`, and a battery guards both
  - Requirements: FR-004
  - Seam: the new battery, run by `pnpm test:scripts`
  - Files: scripts/test/process-suite.battery.mjs, .claude/agents/implementer.md
  - Done when: `node scripts/test/process-suite.battery.mjs` passes, after failing on the missing `implementer.md`
- [ ] T002 The implementer builds each task of its slice through `tdd`, self-checks its diff against the matching standards, and edits `tasks.md` only in its own boxes, Evidence lines and Follow-ups
  - Requirements: FR-004, FR-005, FR-006
  - Seam: read by the conformance pass
  - Files: .claude/agents/implementer.md
  - Depends on: T001
  - Done when: `grep -c 'applies-to' .claude/agents/implementer.md` is at least 1 and the method names the task as the behavior, the task's seam, the Done-when check, the no-key rule, and forbids commit, push and branch switch
- [ ] T003 The implementer stops on the five conditions and decides only how-it-is-built gaps itself
  - Requirements: FR-007, FR-008
  - Seam: read by the conformance pass
  - Files: .claude/agents/implementer.md
  - Depends on: T001
  - Done when: the stop section lists exactly the five FR-007 conditions, names the "Ask first" source, exempts spec-decided trunk changes, and states FR-008's decide-and-report rule
- [ ] T004 The implementer applies the proof bar and builds an approved trunk change first, ending in `TRUNK_READY`
  - Requirements: FR-013, FR-014
  - Seam: read by the conformance pass
  - Files: .claude/agents/implementer.md
  - Depends on: T003
  - Done when: `grep -c 'TRUNK_READY' .claude/agents/implementer.md` is at least 1 and the trunk section states the proof bar and the re-`BLOCKED` path
- [ ] T005 The implementer ends with the report contract
  - Requirements: FR-009
  - Seam: read by the conformance pass
  - Files: .claude/agents/implementer.md
  - Depends on: T004
  - Done when: the report section lists the four statuses and the five fields of FR-009 and forbids advice in notes
- [ ] T006 The orchestrator dispatches one implementer per slice with a pointer-only brief at effort high, and writes only what FR-002 allows
  - Requirements: FR-001, FR-002, FR-003, INV-001
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T005
  - Done when: `grep -c 'Skill tool' .claude/skills/sdd-implement/SKILL.md` is 0, the skill names `implementer`, `effort: high` with the per-run override, the four brief inputs, and the FR-002 write list
- [ ] T007 The orchestrator handles `BLOCKED` by asking the user and resuming the same agent, dispatching `skeptic` first for a trunk change, and `skeptic` reads its brief instead of the index
  - Requirements: FR-010, FR-011, FR-012
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md, .claude/agents/skeptic.md
  - Depends on: T006
  - Done when: `grep -cE 'diff --cached|refiner|code-reviewer' .claude/agents/skeptic.md` is 0 and the skill states the `SendMessage` resume and the fresh-dispatch fallback
- [ ] T008 The orchestrator commits a verified trunk change alone and resumes the agent
  - Requirements: FR-015
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T007
  - Done when: the skill runs the full suite on `TRUNK_READY`, commits with a body opening `Trunk change:`, and resumes the same agent
- [ ] T009 The orchestrator verifies every slice with five checks, separates pre-existing failures in a temporary worktree, and allows one retry
  - Requirements: FR-016, FR-017, FR-018
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T008
  - Done when: `grep -c 'git worktree' .claude/skills/sdd-implement/SKILL.md` is at least 1 and the verify step lists the five FR-016 checks and the single resume
- [ ] T010 The orchestrator ticks the close-out and commits the slice without asking, refusing the default branch
  - Requirements: FR-019, INV-002
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T009
  - Done when: the commit step ticks the close-out before committing, forbids `git add -A` and `git add .`, refuses the default branch, never pushes, and records judgment calls in the body
- [ ] T011 The orchestrator resumes at the first unchecked close-out, routes a fully closed list to QA, and never discards uncommitted work
  - Requirements: FR-020, FR-021, INV-005
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T010
  - Done when: the start section states both resume points and the two options for uncommitted work, with no discard step
- [ ] T012 Skill-authoring no longer exempts `sdd-implement` from code work in agents
  - Requirements: FR-030
  - Seam: read by the conformance pass
  - Files: .claude/rules/skill-authoring.md
  - Done when: `grep -c 'sdd-implement' .claude/rules/skill-authoring.md` is 0
- [ ] T013 The SDD document gives slice commits to the orchestrator and describes the orchestrated build in section 10
  - Requirements: FR-031, FR-032, INV-001
  - Seam: `sdd templates sync --check` and `sdd check-refs` through `sdd-helper.battery.mjs`
  - Files: .claude/sdd/spec-driven-development.md
  - Depends on: T011
  - Done when: `node scripts/test/sdd-helper.battery.mjs` passes and no line in sections 1, 2, 4, 10, 11 or 15 says the user commits slice work or recommends a fresh session between slices
- [ ] P1 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## P2: End-of-run QA and report

- [ ] T014 After the last slice, the orchestrator lints, launches or reuses the app when there is a runnable surface, and hands over a QA script mapped to the checks
  - Requirements: FR-022
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Done when: the QA step states the lint, the launch order, server reuse, the no-surface and launch-failure scripts, the mapping rule, and that it waits
- [ ] T015 A QA bug goes to a fresh implementer as a red-first fix, verified and committed, then QA resumes
  - Requirements: FR-023
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md, .claude/agents/implementer.md
  - Depends on: T014
  - Done when: the skill states the QA-fix brief, the full suite and test-file checks, the commit body, and the return to QA, and the agent describes its QA-fix mode
- [ ] T016 On QA confirmation the orchestrator sets `done`, commits it, stops its processes, and reports the five parts
  - Requirements: FR-024
  - Seam: read by the conformance pass
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T015
  - Done when: the finish step follows QA confirmation, commits the status change, keeps reused servers running, and lists the five report parts
- [ ] T017 The orchestrator recommends `/sdd-review` in a fresh session and never starts it, and the SDD document carries the end-to-end exception, the pre-existing-failure exit gate and section 12's new Fixes wording
  - Requirements: FR-025, FR-031, INV-004
  - Seam: `sdd check-refs` through `sdd-helper.battery.mjs`
  - Files: .claude/skills/sdd-implement/SKILL.md, .claude/sdd/spec-driven-development.md
  - Depends on: T016
  - Done when: `node scripts/test/sdd-helper.battery.mjs` passes, the skill's Next forbids starting `sdd-review` in every case, and `grep -c 'exactly as for a slice' .claude/sdd/spec-driven-development.md` is 0
- [ ] P2 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## P3: Retire refine; render checks on demand

- [ ] T018 A user-only `render-check` skill discovers its base, surfaces and bar, runs `render-checker`, and only reports
  - Requirements: FR-026
  - Seam: the battery
  - Files: .claude/skills/render-check/SKILL.md, scripts/test/process-suite.battery.mjs
  - Done when: `node scripts/test/process-suite.battery.mjs` passes its new `render-check` user-only check, after failing on the missing skill
- [ ] T019 Only `render-check` dispatches `render-checker`, with `refine` deleted
  - Requirements: FR-027, FR-028, INV-003
  - Seam: the battery
  - Files: .claude/agents/render-checker.md, .claude/skills/refine/SKILL.md, scripts/test/process-suite.battery.mjs
  - Depends on: T018
  - Done when: `node scripts/test/process-suite.battery.mjs` passes its sole-dispatcher check, after failing while `refine` named `render-checker`
- [ ] T020 No agent is orphaned, with `refiner`, `code-reviewer` and `docs/specs/` deleted
  - Requirements: FR-028
  - Seam: the battery
  - Files: .claude/agents/refiner.md, .claude/agents/code-reviewer.md, docs/specs/001-refine.md, scripts/test/process-suite.battery.mjs
  - Depends on: T019
  - Done when: `node scripts/test/process-suite.battery.mjs` passes its no-orphan check, after failing on `refiner` and `code-reviewer`, and `test ! -e docs/specs` succeeds
- [ ] P3 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## P4: Docs reflect the repository

- [ ] T021 The `sdd` helper no longer parses or lints a parallel marker, and the document, template and `sdd-task` no longer offer one
  - Requirements: FR-029
  - Seam: the helper's `unittest` suite
  - Files: .claude/sdd/bin/sdd, .claude/sdd/tests/test_lint_tasks.py, .claude/sdd/tests/test_status.py, .claude/sdd/tests/helpers.py, .claude/sdd/spec-driven-development.md, .claude/sdd/templates/tasks.md, .claude/skills/sdd-task/SKILL.md
  - Done when: `node scripts/test/sdd-helper.battery.mjs` passes, including a new test that two tasks sharing a file and depending on each other lint clean, which failed before the change
- [ ] T022 No tracked file outside `docs/sdd/` and released changelog entries names a removed skill or agent, and no doc states a skill or agent count
  - Requirements: FR-028, FR-034
  - Seam: the battery
  - Files: scripts/test/process-suite.battery.mjs, CLAUDE.md, README.md, .claude/skills/README.md, .claude/sdd/README.md, .ai-starter.yaml, scripts/test/ai-starter-version.battery.mjs
  - Depends on: T021
  - Done when: `node scripts/test/process-suite.battery.mjs` passes its removed-name check, after failing on `CLAUDE.md`, and `CLAUDE.md` states the 5000-token budget
- [ ] T023 The unreleased v0.3.0 changelog entry describes this change and nothing in it contradicts the repository
  - Requirements: FR-033
  - Seam: read by the conformance pass
  - Files: CHANGELOG.md
  - Depends on: T022
  - Done when: the v0.3.0 entry has what, why and adaptation notes for this change, and `node scripts/test/process-suite.battery.mjs` still passes
- [ ] T024 Every changed skill body measures under the token budget
  - Requirements: NFR-001
  - Seam: measurement
  - Files: .claude/skills/sdd-implement/SKILL.md, .claude/skills/render-check/SKILL.md, .claude/skills/sdd-task/SKILL.md
  - Depends on: T023
  - Done when: for each file, the body's `wc -c` divided by 4 is under 4500, with each figure recorded in the Evidence line
- [ ] T025 The gut-check prompts for `sdd-implement`, `implementer` and `render-check` are written for a fresh session
  - Requirements: FR-001, FR-022, FR-026
  - Seam: read by the owner
  - Files: docs/sdd/implement-orchestrator/gut-check.md
  - Depends on: T024
  - Done when: the file holds two or three task prompts with expected behavior per skill, and should-trigger and near-miss should-not-trigger prompts for each changed description
- [ ] P4 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## Verified elsewhere

- NFR-002: every slice close-out runs `pnpm test:scripts`, which runs the helper suite, the template drift check, the section-reference check and the process-suite battery. Decided by Conner Donohoo.

## Follow-ups (out of scope)

- The pre-commit hook runs `prettier --write` after `sdd approve` records a hash, so an approved artifact reads as changed; the gate skills or the helper should format before hashing.
