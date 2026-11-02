---
title: Implement orchestrator plan
slug: implement-orchestrator
status: approved
updated: 2026-11-02
based_on: d36a6638a637
approved_hash: 1f38a952fdb6
---

# Implement orchestrator plan

## Approach

Rewrite `.claude/skills/sdd-implement/SKILL.md` as an orchestrator over a new `implementer` agent, modelled on the dispatch, `BLOCKED` and `SendMessage` resume pattern `refine` uses today.
The skill keeps every gate and every user interaction; the agent holds the build method, the stop rules, the proof bar and the report contract.
Section 10 of the SDD document is rewritten to match, and the commit-authority lines across the document change once, in the same slice.
`refine`'s QA and app-lifecycle rules move into `sdd-implement`, its base and surface discovery move into a new user-only `render-check` skill, and `refine`, `refiner`, `code-reviewer` and `docs/specs/` are deleted.
The `[P]` marker leaves the document, the template and the helper.
A new battery, `scripts/test/process-suite.battery.mjs`, locks the structural rules that must always hold, growing one slice at a time so each slice opens red.
The work ships in four slices, each leaving the chain usable.

## Technical context

- Stack and versions: Markdown skills and agents under `.claude/`, read by Claude Code; Node batteries under `scripts/test/` run by `pnpm test:scripts` on the pinned Node; the `sdd` helper in Python 3 standard library with a `unittest` suite, run by `scripts/test/sdd-helper.battery.mjs`.
- Dependencies: none added.
- Platform limits:
  - Agent frontmatter supports `skills:` (full content preloaded at start), `model` (alias or full ID), `effort`, `tools` and `disallowedTools`.
  - `disable-model-invocation: true` stops the model from invoking a skill; the user still runs it as `/name`.
  - `SendMessage` resumes a subagent with its history inside the same session; resuming from a different session is not documented, which FR-010's fresh-dispatch fallback covers.
  - Subagents can nest up to three levels; the plan nests none, since the orchestrator dispatches `skeptic` itself.
  - Whether a per-dispatch `effort` overrides an agent's frontmatter `effort` is not documented, so the plan pins no effort in frontmatter.
  - No local tokenizer exists for the 5000-token skill budget; see Trade-offs and risks.

## Principles check

| Principle                                                                                    | Pass/Fail | Notes                                                                                                                                              |
| -------------------------------------------------------------------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| No stubs, TODOs or placeholder logic                                                         | Pass      | Every slice ships finished prose and checks.                                                                                                       |
| Do not leave dead or orphaned code                                                           | Pass      | `refine`, `refiner`, `code-reviewer`, `docs/specs/` and the `[P]` lint are deleted, not left unreferenced; the battery fails on an orphaned agent. |
| Never hand-edit generated files                                                              | Pass      | `.claude/sdd/templates/tasks.md` is regenerated with `sdd templates sync` after Appendix C changes.                                                |
| Comments only for a dangerous action or a costly fact                                        | Pass      | The battery carries one header comment stating what it guards, matching `rules-frontmatter.battery.mjs`.                                           |
| Commit only from a non-main branch                                                           | Pass      | The orchestrator refuses the default branch before every commit, and `guard-main` blocks it underneath.                                            |
| Markdown: one sentence per line, escaped pipes, lists over long tables                       | Pass      | Applies to every changed Markdown file.                                                                                                            |
| Context-file edits load `curate-context` first                                               | Pass      | Slices touching `CLAUDE.md`, `README.md` or `.claude/rules/` load it before editing.                                                               |
| Skill-authoring: body budget, description as trigger, code work in agents, gut-check handoff | Pass      | The exemption is removed and `sdd-implement` now complies; gut-check prompts close P1, P2 and P3.                                                  |
| Simplicity: fewest moving parts                                                              | Pass      | One new agent, one new skill, one new battery; no shared reference file between skills.                                                            |
| Agent-facing output (`docs/standards/agent-facing-output.md`, applies to `scripts/**`)       | Pass      | The battery prints one `ok` or `FAIL` line per check and a final outcome line, like the existing batteries.                                        |
| JavaScript and TypeScript standard (applies to `**/*.mjs`)                                   | Pass      | The battery follows it.                                                                                                                            |

### Deviations

None.

## Architecture

- **`sdd-implement` (orchestrator skill).**
  Owns: the start protocol and resume points (FR-020, FR-021), the branch check, dispatch (FR-001, FR-003), `BLOCKED` handling and the `skeptic` dispatch (FR-010, FR-011), the trunk commit (FR-015), verification (FR-016 to FR-018), the slice commit (FR-019), QA and the app lifecycle (FR-022, FR-023), the finish and report (FR-024), and the handoff (FR-025).
  Writes only what FR-002 allows.
  Dispatches every `implementer` with `effort: high` unless the user named another level for this run.
  The QA and app-lifecycle rules sit in the body; if the body measures over budget, they move to `sdd-implement/references/qa.md`, one hop away.
- **`implementer` (new agent).**
  Frontmatter: `name`, `description`, `skills: [tdd]`, `model: opus`; no `effort`, no `tools` restriction.
  Owns: loading its slice from the slug, building each task through `tdd`, the standards self-check (FR-005), its `tasks.md` edits (FR-006), the stop rules (FR-007, FR-008), the proof bar and trunk sequence (FR-013, FR-014), and the report (FR-009).
  Three modes, set by the brief: slice, trunk continuation (a resume), and QA fix.
  Never commits, pushes or switches branches.
- **`skeptic` (existing agent, edited).**
  Reads the proposed change from its brief, not the index; dispatched by the orchestrator (FR-012).
- **`render-check` (new skill, user-only).**
  Owns base discovery, surface discovery, the bar, the app lifecycle for its own run, and the report (FR-026).
  The only dispatcher of `render-checker` (INV-003).
- **`render-checker` (existing agent).**
  Description names `render-check` (FR-027); behavior unchanged.
- **SDD document, templates and helper.**
  Section 10 describes the orchestrated flow; commit authority, the end-to-end exception and the pre-existing-failure exit gate change across sections 1, 2, 4, 9, 10, 12 and 15 (FR-031, FR-032); `[P]` leaves sections 9 and Appendix C, the generated template, `sdd-task`, and the helper (FR-029).
- **`scripts/test/process-suite.battery.mjs` (new).**
  Locks the structural invariants listed under Interfaces and contracts.

Boundary: the orchestrator never reads code to judge it and never edits it; the implementer never talks to the user; `skeptic` and `render-checker` stay read-only.

## Data model

None.
The `tasks.md` shape is unchanged except that a task line no longer carries `[P]`; the helper's content hash is unchanged.

## Interfaces and contracts

**Orchestrator to implementer briefs** (pointers only):

- Slice: the slug, the slice heading (`P1: ...`), the notes earlier slices reported, and the user's decisions for this slice.
- QA fix: the slug, the bug in the user's words with its reproduction steps, and the requirement IDs it touches.
- Trunk continuation is a `SendMessage` resume carrying the user's decision, or a fresh slice brief with that decision when the agent is gone.

**Implementer report** (its final message):

- `Status:` one of `DONE`, `DONE_WITH_CONCERNS` (with the doubt), `BLOCKED` (the condition, the decision that would clear it, what is uncommitted), `TRUNK_READY` (the trunk paths, the touch point, its consumer count).
- `Files changed:` every path.
- `Tests:` the test files added, changed or deleted, and the command that runs them; "none" for a documentation-only slice.
- `Judgment calls:` one line each, with its reason.
- `Notes for later slices:` facts found in the code only.

**Orchestrator to skeptic brief:** the intent (spec path and slice), the agent's description of the proposed change, and the consumers of each touched symbol.

**Orchestrator to render-checker brief** (from `render-check`; unchanged from `refine`'s): the URL, the surfaces with the states to reach, the shipped themes, and the bar.

**Commit messages** (repo convention: 50-character imperative subject, a body that explains why):

- Slice: subject names the slice's behavior; body lists judgment calls and any pre-existing failures.
- Trunk: body opens `Trunk change: <touch point> (<n> consumers)`, then the skeptic's verdict and the user's decision.
- QA fix: subject names the bug; body names the red test and its pass.
- Done: `tasks.md` status to `done`.

**Battery checks** (`process-suite.battery.mjs`), each one `ok`/`FAIL` line:

- Every agent in `.claude/agents/` is named by at least one skill or agent file (no orphans).
- `implementer.md` frontmatter lists `tdd` under `skills:` and sets `model: opus`.
- Among `.claude/skills/*/SKILL.md` and `.claude/agents/*.md`, only `render-check` and `render-checker` itself name `render-checker`.
- `render-check/SKILL.md` frontmatter sets `disable-model-invocation: true`.
- `git grep -nw` finds no removed name (`refine`, `refiner`, `code-reviewer`, `template-sync`, `template-feedback`, `builder`, `implement-spec`, `run-skill-generator`) outside `docs/sdd/` and released `CHANGELOG.md` entries.

## Affected code

- Change: `.claude/skills/sdd-implement/SKILL.md`, rewritten as the orchestrator (P1), then QA and finish (P2).
- Create: `.claude/agents/implementer.md`, the slice builder (P1).
- Change: `.claude/agents/skeptic.md`, brief-based method and new dispatcher (P1).
- Change: `.claude/rules/skill-authoring.md`, drop the `sdd-implement` exemption (P1).
- Change: `.claude/sdd/spec-driven-development.md`, sections 1, 2, 4, 10, 11 and 15 for commit authority and the orchestrated flow (P1); sections 4, 10 and 12 for QA, the end-to-end exception and the exit gate (P2); sections 9 and Appendix C for `[P]` (P4).
- Create: `scripts/test/process-suite.battery.mjs`, the structural guard (P1, extended in P3 and P4).
- Create: `.claude/skills/render-check/SKILL.md`, the user-only render check (P3).
- Change: `.claude/agents/render-checker.md`, description names `render-check` (P3).
- Delete: `.claude/skills/refine/`, `.claude/agents/refiner.md`, `.claude/agents/code-reviewer.md`, `docs/specs/` (P3).
- Change: `.claude/sdd/bin/sdd`, remove `[P]` parsing and `lint_parallel` (P4).
- Change: `.claude/sdd/tests/test_lint_tasks.py`, `.claude/sdd/tests/test_status.py`, `.claude/sdd/tests/helpers.py`, drop `[P]` cases and fixtures (P4).
- Change: `.claude/sdd/templates/tasks.md`, regenerated (P4).
- Change: `.claude/skills/sdd-task/SKILL.md`, drop the `[P]` instruction (P4).
- Change: `.claude/skills/README.md`, `.claude/sdd/README.md`, `CLAUDE.md`, `README.md`, `CHANGELOG.md`, `.ai-starter.yaml`, `scripts/test/ai-starter-version.battery.mjs`, the docs sweep (P4).
- Pattern to follow: `.claude/skills/refine/SKILL.md` for dispatch, `BLOCKED`, resume, verify, app lifecycle and QA; the deleted `builder.md` (`git show f323246^:.claude/agents/builder.md`) for the agent's stop section, trunk protocol and report; `scripts/test/rules-frontmatter.battery.mjs` for the battery; `.claude/sdd/tests/test_lint_tasks.py` for helper tests.

## Seams and test strategy

The repo's established seams for this kind of code are the `scripts/test/*.battery.mjs` scripts for structural rules over repository files, and the helper's `unittest` suite for `sdd` behavior.
Skill and agent prose has no executable seam: its acceptance criteria are judged by reading, by `sdd-review`'s spec-conformance pass, and by the gut-check prompts the skill-authoring rule requires.

### P1: Orchestrated slice build

- Seam: the new battery, run by `pnpm test:scripts`; `sdd templates sync --check` and `sdd check-refs` through `sdd-helper.battery.mjs`.
- Test types: battery assertions over files; the helper's drift and reference checks.
- Acceptance criteria to tests:
  - FR-004 (frontmatter) → battery: `implementer.md` lists `tdd` and sets `model: opus` (red until the file exists).
  - FR-012 → read by the conformance pass; the no-orphan check lands in P3, where deletions make it bite.
  - FR-032 → `check-refs` and `templates sync --check` pass after section 10 changes.
  - FR-001 to FR-021, FR-030, FR-031 (commit authority) → read by `sdd-review`'s conformance pass and the P1 gut-check prompts.

### P2: End-of-run QA and report

- Seam: `check-refs` and `templates sync --check`; the P2 gut-check prompts.
- Test types: the helper's drift and reference checks.
- Acceptance criteria to tests: FR-022 to FR-025 and FR-031 (end-to-end exception, exit gate, section 12) → read by the conformance pass and the gut-check prompts.

### P3: Retire refine; render checks on demand

- Seam: the battery.
- Test types: battery assertions over files.
- Acceptance criteria to tests:
  - FR-026 → battery: `render-check` sets `disable-model-invocation: true` (red until the skill exists).
  - FR-027, INV-003 → battery: only `render-check` and `render-checker` name `render-checker` among skills and agents (red while `refine` exists).
  - FR-028 (deletions) → battery: no orphan agents after `refiner` and `code-reviewer` go.

### P4: Docs reflect the repository

- Seam: the helper's `unittest` suite for `[P]`; the battery for the sweep.
- Test types: helper unit tests; battery assertions.
- Acceptance criteria to tests:
  - FR-029 → helper test: two tasks in one slice that share a file and depend on each other lint clean, and a task line's text is kept whole (red while `lint_parallel` runs); `templates sync --check` passes after regeneration.
  - FR-028 (sweep), FR-034 → battery: the removed-name `git grep` check (red until the sweep lands).
  - FR-033 → read by the conformance pass.

## Alternatives considered

- Parallel slices in worktrees: rejected by the owner; dependency inference, a shared checkout, a shared database and serial suite runs made it costly for little gain.
- Keeping `refine` as a post-build pass: rejected; it rewrites code after it was built and judges standards a second time before `sdd-review` does.
- Reviving `builder` with agent-made commits: rejected; the orchestrator commits so it can verify first, and the agent's context stays on building.
- Automatic render checks on surface changes: rejected by the owner as slow and token-heavy.
- Pinning `effort: high` in `implementer.md`: rejected because per-dispatch override precedence is undocumented; the orchestrator passes the effort instead, so the user can change it per run.
- A fixture dry run before landing: rejected by the owner; the gut-check handoff covers it.
- Keeping skill and agent counts and testing them: rejected by the owner; dropping the numbers removes the drift.
- A one-time grep instead of a battery: rejected by the owner; the battery keeps the rules from regressing.
- A shared app-lifecycle reference used by both `sdd-implement` and `render-check`: rejected; skills stay self-contained and the rules run a few lines in each.

## Trade-offs and risks

- No local tokenizer for the 5000-token body budget: estimate with `wc -c` divided by 4 and hold each body under an estimated 4500; when `sdd-implement` exceeds that, move QA and the app lifecycle to `references/qa.md`.
- Resuming a `BLOCKED` agent across sessions is undocumented: FR-010's fresh-dispatch fallback carries the user's answer, so nothing depends on it.
- The orchestrator commits without asking: verification (FR-016) runs before every commit, `guard-main` blocks the default branch, and nothing is pushed.
- `effort: high` on every dispatch costs more than a lower level: the user can name another level per run.
- The removed-name check can false-positive on an ordinary English "refine" or "builder": the check reads `.claude/`, root docs and `scripts/` with `-w`, and any legitimate use is reworded rather than excluded.
- This branch's own build runs on today's in-session `sdd-implement`: the slices are prose and checks, which that flow handles, and P1 lands the new skill for later specs.

## Rollout

1. P1, orchestrated slice build: the new `implementer`, the orchestrator skill with its dispatch, stop, trunk, verify, commit and resume steps, the `skeptic` change, the rule change, section 10 and the commit-authority lines, and the battery's first checks; the finish step temporarily keeps today's behavior (lint, set `done`, name `sdd-review`). Rollback: revert the slice commit.
2. P2, QA and finish: QA before `done`, the QA-fix loop, the report, the no-start handoff, and the document's end-to-end exception, exit gate and section 12 wording. Rollback: revert the slice commit; P1's finish returns.
3. P3, retire `refine`: create `render-check`, retarget `render-checker`, delete `refine`, `refiner`, `code-reviewer` and `docs/specs/`, and extend the battery. Rollback: revert the slice commit.
4. P4, docs and `[P]`: remove `[P]` from the document, template, `sdd-task` and helper, sweep every stale reference, rewrite the v0.3.0 changelog entry, and add the battery's removed-name check. Rollback: revert the slice commit.

## Traceability

| Requirement | Components                                   | Seam            | Tests                                                                |
| ----------- | -------------------------------------------- | --------------- | -------------------------------------------------------------------- |
| FR-001      | sdd-implement                                | read            | conformance pass; P1 gut-check                                       |
| FR-002      | sdd-implement                                | read            | conformance pass; P1 gut-check                                       |
| FR-003      | sdd-implement                                | read            | conformance pass                                                     |
| FR-004      | implementer                                  | battery         | process-suite: implementer frontmatter                               |
| FR-005      | implementer                                  | read            | conformance pass                                                     |
| FR-006      | implementer                                  | read            | conformance pass                                                     |
| FR-007      | implementer                                  | read            | conformance pass; P1 gut-check                                       |
| FR-008      | implementer                                  | read            | conformance pass                                                     |
| FR-009      | implementer                                  | read            | conformance pass                                                     |
| FR-010      | sdd-implement                                | read            | conformance pass; P1 gut-check                                       |
| FR-011      | sdd-implement                                | read            | conformance pass; P1 gut-check                                       |
| FR-012      | skeptic, sdd-implement                       | read            | conformance pass; P1 gut-check                                       |
| FR-013      | implementer                                  | read            | conformance pass                                                     |
| FR-014      | implementer                                  | read            | conformance pass                                                     |
| FR-015      | sdd-implement                                | read            | conformance pass; P1 gut-check                                       |
| FR-016      | sdd-implement                                | read            | conformance pass                                                     |
| FR-017      | sdd-implement                                | read            | conformance pass                                                     |
| FR-018      | sdd-implement                                | read            | conformance pass                                                     |
| FR-019      | sdd-implement                                | read            | conformance pass; P1 gut-check                                       |
| FR-020      | sdd-implement                                | read            | conformance pass                                                     |
| FR-021      | sdd-implement                                | read            | conformance pass                                                     |
| FR-022      | sdd-implement                                | read            | conformance pass; P2 gut-check                                       |
| FR-023      | sdd-implement                                | read            | conformance pass; P2 gut-check                                       |
| FR-024      | sdd-implement                                | read            | conformance pass; P2 gut-check                                       |
| FR-025      | sdd-implement                                | read            | conformance pass; P2 gut-check                                       |
| FR-026      | render-check                                 | battery         | process-suite: render-check user-only                                |
| FR-027      | render-checker                               | battery         | process-suite: sole render-checker dispatcher                        |
| FR-028      | deletions, docs sweep                        | battery         | process-suite: no orphans; removed names                             |
| FR-029      | sdd helper, SDD document, template, sdd-task | helper unittest | test_lint_tasks: shared files no longer lint; templates sync --check |
| FR-030      | skill-authoring rule                         | read            | conformance pass                                                     |
| FR-031      | SDD document                                 | read            | conformance pass; check-refs                                         |
| FR-032      | SDD document                                 | helper checks   | check-refs; templates sync --check                                   |
| FR-033      | CHANGELOG                                    | read            | conformance pass                                                     |
| FR-034      | CLAUDE.md, .ai-starter.yaml, version battery | battery         | process-suite: removed names                                         |
| NFR-001     | every changed skill                          | measurement     | `wc -c` estimate per body, recorded as Evidence                      |
| NFR-002     | all                                          | battery         | `pnpm test:scripts`                                                  |
| INV-001     | sdd-implement                                | read            | conformance pass; P1 gut-check                                       |
| INV-002     | sdd-implement, implementer, guard-main       | existing hook   | guard-main.battery.mjs; conformance pass                             |
| INV-003     | render-check, render-checker                 | battery         | process-suite: sole render-checker dispatcher                        |
| INV-004     | sdd-implement, SDD document                  | read            | conformance pass                                                     |
| INV-005     | sdd-implement, implementer                   | read            | conformance pass                                                     |

## Research notes

- Agent frontmatter supports `skills` (full skill content injected at startup), `model` (`sonnet`, `opus`, `haiku`, `fable`, a full ID, or `inherit`), `effort` (`low` to `max`), `tools`, `disallowedTools`, `isolation` and others: https://code.claude.com/docs/en/sub-agents.md
- `disable-model-invocation: true` blocks model invocation and preloading into subagents while `/name` still works: https://code.claude.com/docs/en/skills.md
- `SendMessage` resumes a subagent with its full history in the same session; transcripts are kept for `cleanupPeriodDays` (default 30); resuming from an unrelated session is not documented: https://code.claude.com/docs/en/sub-agents.md
- Subagents can spawn subagents up to three levels deep by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`): https://code.claude.com/docs/en/sub-agents.md
- Skill guidance: keep `SKILL.md` under 500 lines; after compaction the latest invocation of each skill is re-attached keeping its first 5,000 tokens: https://code.claude.com/docs/en/skills.md
- Token counting exists only as the Messages API `count_tokens` endpoint, which needs an API key: https://platform.claude.com/docs/en/build-with-claude/token-counting.md
- The Agent tool's `model` parameter overrides an agent's frontmatter `model`; its `effort` parameter's precedence over frontmatter `effort` is not stated: the Agent tool's own parameter descriptions in this Claude Code build.
