---
title: Claude design integration tasks
slug: claude-design-integration
status: in-progress
updated: 2026-11-09
based_on: cdcad58a478f
approved_hash: b625a3cfc01a
---

# Claude design integration tasks

Commands used below: one helper test file is `python3 -m unittest discover -s .claude/sdd/tests -p '<file>'` with the file named in the task; the helper battery is `pnpm exec node scripts/test/sdd-helper.battery.mjs`; the process battery is `pnpm exec node scripts/test/process-suite.battery.mjs`; the full suite is `pnpm format:check && pnpm test:scripts`.
Every task that edits `CLAUDE.md`, a `README.md`, a `docs/standards/` file or the DESIGN.md template loads `curate-context` first, and every task that edits a skill follows `.claude/rules/skill-authoring.md`.

## P1: Approve a design before planning

- [ ] T001 Generate the design record template from a new Appendix B and scan `sdd-design` in `check-refs`
  - Requirements: FR-001
  - Seam: the helper CLI through `helpers.py`'s in-process runner
  - Files: .claude/sdd/bin/sdd, .claude/sdd/spec-driven-development.md, .claude/sdd/templates/design.md, .claude/sdd/tests/helpers.py, .claude/sdd/tests/test_templates.py
  - Done when: `test_templates.py` passes with sync writing five templates including `design.md` from Appendix B and the plan, tasks and review templates from Appendices C, D and E, and `check-refs` listing `sdd-design` among its scanned skills; the helper battery passes
- [ ] T002 Define the Design phase in the SDD document and renumber the phases and sections everywhere they are cited
  - Requirements: FR-001, FR-004
  - Seam: skill and document text, checked by `check-refs`
  - Files: .claude/sdd/spec-driven-development.md, .claude/sdd/README.md, .claude/skills/sdd-outline/SKILL.md, .claude/skills/sdd-plan/SKILL.md, .claude/skills/sdd-task/SKILL.md, .claude/skills/sdd-implement/SKILL.md, .claude/skills/sdd-review/SKILL.md, .claude/skills/sdd-outline/references/adversarial-review.md, .claude/skills/sdd-review/references/conformance-review.md
  - Depends on: T001
  - Done when: the helper battery passes; section 8 is Phase 2: Design (`sdd-design`) with steps, prompt, snapshot, misses, gaps and gate; sections 4 and 5 list `2. Design` and `design.md`; every skill precondition cites the renumbered label; `grep -rn "phase \`2. Plan\`\|phase \`5. Validate\`" .claude/skills` prints nothing
- [ ] T003 Add the UI surfaces section to the spec template and reject malformed or duplicate UI IDs in spec lint
  - Requirements: FR-007
  - Seam: the helper CLI through `helpers.py`'s in-process runner
  - Files: .claude/sdd/bin/sdd, .claude/sdd/spec-driven-development.md, .claude/sdd/templates/spec.md, .claude/sdd/tests/test_lint_spec.py, .claude/sdd/tests/helpers.py
  - Depends on: T001
  - Done when: `test_lint_spec.py` passes with cases for a valid `- UI-001: Settings screen (new)` line, a malformed ID and a duplicate ID; the regenerated spec template carries `## UI surfaces`; the helper battery passes
- [ ] T004 Record a design request, skip or approval in `design.md` through `set-status` and `approve`, linted
  - Requirements: FR-002, FR-024
  - Seam: the helper CLI through `helpers.py`'s in-process runner
  - Files: .claude/sdd/bin/sdd, .claude/sdd/tests/test_design.py, .claude/sdd/tests/test_approve.py, .claude/sdd/tests/helpers.py
  - Depends on: T001, T003
  - Done when: `test_design.py` and `test_approve.py` pass with cases for `set-status design requested` creating `design.md`, `set-status design skipped` recording `decided_by`, `surfaces` and `based_on`, `approve design` refusing on a lint error or a missing `link`, `version` or `read`, and approval recording `approved_hash` and `based_on`
- [ ] T005 Report `2. Design` while a design is requested, changed or stale, and the renumbered labels otherwise
  - Requirements: FR-003, FR-004, FR-005
  - Seam: the helper CLI through `helpers.py`'s in-process runner
  - Files: .claude/sdd/bin/sdd, .claude/sdd/tests/test_status.py, .claude/sdd/tests/test_design.py
  - Depends on: T004
  - Done when: `test_status.py` passes with only its phase labels renumbered, and `test_design.py` passes with a `requested` design reporting `2. Design` and `sdd-design`, and a `skipped` design reporting `3. Plan`
- [ ] T006 Make the plan build on an approved design, so a later design approval or design change stales the plan and tasks
  - Requirements: FR-006
  - Seam: the helper CLI through `helpers.py`'s in-process runner
  - Files: .claude/sdd/bin/sdd, .claude/sdd/tests/test_design.py
  - Depends on: T005
  - Done when: `test_design.py` passes with a re-approved design staling the plan and tasks, a design approved after the plan staling the plan, and plan approval recording the design's `approved_hash` as `based_on`
- [ ] T007 Re-offer design when a re-approved spec lists a UI ID the skip does not cover
  - Requirements: FR-011
  - Seam: the helper CLI through `helpers.py`'s in-process runner
  - Files: .claude/sdd/bin/sdd, .claude/sdd/tests/test_design.py
  - Depends on: T005
  - Done when: `test_design.py` passes with a skip covering `UI-001` and a re-approved spec adding `UI-002` reporting `2. Design`, and a re-approved spec with no new ID reporting `3. Plan`
- [ ] T008 Write the `sdd-design` skill that acts on `design.md`'s state: request, skip, cancel, record, re-check and approve, each staged on the user's word
  - Requirements: FR-010, FR-012, FR-013, FR-019, FR-024, FR-025, INV-001, INV-002
  - Seam: skill and document text, checked by `check-refs`
  - Files: .claude/skills/sdd-design/SKILL.md
  - Depends on: T002, T004
  - Done when: the helper battery passes; reading it meets each listed requirement's acceptance criterion, including no `/design` invocation and no artifact publish
- [ ] T009 Write the design prompt template
  - Requirements: FR-014, FR-015, FR-016, FR-017, FR-018, INV-004
  - Seam: skill and document text
  - Files: .claude/skills/sdd-design/references/design-prompt.md
  - Depends on: T008
  - Done when: reading it meets each listed acceptance criterion; `grep -n "—" .claude/skills/sdd-design/references/design-prompt.md` prints nothing
- [ ] T010 Write the record procedure: read the link, save the snapshot, list artboards, and put each miss and gap to the user
  - Requirements: FR-020, FR-021, FR-022, FR-023
  - Seam: skill and document text
  - Files: .claude/skills/sdd-design/references/record-design.md
  - Depends on: T008
  - Done when: reading it meets each listed acceptance criterion and covers the edge cases for an unreadable link, no Artifact tool, another owner's artifact, an unexpected file layout and a mismatched design system
- [ ] T011 Have `sdd-outline` write the UI surfaces section and offer `sdd-design` or record a skip at its finish
  - Requirements: FR-008, INV-002
  - Seam: skill and document text
  - Files: .claude/skills/sdd-outline/SKILL.md, .claude/sdd/spec-driven-development.md
  - Depends on: T003, T004
  - Done when: reading the skill and section 7 meets FR-008's acceptance criterion; the helper battery passes
- [ ] T012 Have `sdd-plan` ask about design for an undecided UI spec and load an approved design into Affected code and Traceability
  - Requirements: FR-009, FR-026
  - Seam: skill and document text
  - Files: .claude/skills/sdd-plan/SKILL.md, .claude/sdd/spec-driven-development.md
  - Depends on: T004
  - Done when: reading the skill and the Plan section meets both acceptance criteria; the helper battery passes
- [ ] T013 Have the `implementer` read a designed surface's artboards and skip what `design.md` records as not built
  - Requirements: FR-027
  - Seam: agent text
  - Files: .claude/agents/implementer.md
  - Depends on: T010
  - Done when: the Load section names `design.md` and the matching artboard files for a task on a designed surface and the not-built list; the process battery passes
- [ ] P1 close: full suite green, changes staged by explicit path, slice verified and committed

## P2: Opt into render checks when the build starts

- [ ] T014 Ask for render-check surfaces at the start of a build, recommend by criterion, record the answer in `tasks.md`'s frontmatter, and allow `sdd-implement` to name `render-checker` in the process-suite battery
  - Requirements: FR-028, FR-029, FR-030, FR-035
  - Seam: skill and agent text
  - Files: .claude/skills/sdd-implement/SKILL.md, .claude/sdd/spec-driven-development.md, scripts/test/process-suite.battery.mjs
  - Done when: the process battery fails once the skill names `render-checker` before the allowlist change, passes after it, and still fails for a scratch skill naming `render-checker`, which is then removed, all three runs in the Evidence line; reading the skill and the Implement section meets the three acceptance criteria, including the amended write list and the commit before the next dispatch; the helper battery passes
- [ ] T015 Dispatch `render-checker` once before QA for the approved surfaces and put its failures into the QA script
  - Requirements: FR-031, FR-032, NFR-002
  - Seam: skill and agent text
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T014
  - Done when: reading the skill meets the acceptance criteria and NFR-002; the process battery passes
- [ ] T016 Judge render checks against the floors, DESIGN.md and the design snapshot, and accept both dispatchers
  - Requirements: FR-033, FR-034, FR-043
  - Seam: skill and agent text
  - Files: .claude/agents/render-checker.md, .claude/skills/render-check/SKILL.md
  - Depends on: T014
  - Done when: reading both files meets FR-033 and FR-034's acceptance criteria and states the absent-DESIGN.md case; `grep -n "Design Requirements\|44×44" .claude/agents/render-checker.md` prints nothing; the process battery passes
- [ ] P2 close: full suite green, changes staged by explicit path, slice verified and committed

## P3: Design values each project decides

- [ ] T017 Rewrite `ux-standards.md` to WCAG 2.2 AA floors and labeled starting values
  - Requirements: FR-036, FR-040, INV-005
  - Seam: the standards and agent files themselves
  - Files: docs/standards/ux-standards.md
  - Done when: reading the file meets FR-036 and FR-040's acceptance criteria; `grep -n "WCAG 2.1" docs/standards/ux-standards.md` prints nothing; `pnpm format:check` passes
- [ ] T018 Rewrite `frontend-styling.md`'s units as a principle and state that designs are references
  - Requirements: FR-038, FR-040, FR-041, FR-043, INV-003
  - Seam: the standards and agent files themselves
  - Files: docs/standards/frontend-styling.md
  - Done when: reading the file meets each listed acceptance criterion, keeps the `svh`-first rule with its fixed-or-sticky caveat, and states the absent-DESIGN.md case; `pnpm format:check` passes
- [ ] T019 Rewrite `html-tables.md` to keep markup floors and label styling choices as starting values
  - Requirements: FR-038, FR-039, FR-040
  - Seam: the standards and agent files themselves
  - Files: docs/standards/html-tables.md
  - Done when: reading the file meets each listed acceptance criterion; `grep -n "never \`px\`" docs/standards/html-tables.md`prints nothing;`pnpm format:check` passes
- [ ] T020 Have the `implementer` self-check and `standards-reviewer` judge surface diffs against DESIGN.md, the floors and runtime markup
  - Requirements: FR-042, FR-043, INV-003, INV-005
  - Seam: the standards and agent files themselves
  - Files: .claude/agents/implementer.md, .claude/agents/standards-reviewer.md
  - Depends on: T017
  - Done when: reading both files meets FR-042's acceptance criterion, states the absent-DESIGN.md case, and `standards-reviewer` names `<x-dc>`, `<dc-import>`, `data-dc-script` and `support.js` as findings; the process battery passes
- [ ] P3 close: full suite green, changes staged by explicit path, slice verified and committed

## P4: Generate DESIGN.md from the skill's own template

- [ ] T021 Rewrite the DESIGN.md template inside `design-init` with the deferred-value decisions and the Claude Design System section, and delete the root DESIGN.md
  - Requirements: FR-037
  - Seam: `design-init`'s files and `pnpm exec designmd lint` on the run's output
  - Files: .claude/skills/design-init/references/design-template.md, DESIGN.md
  - Done when: `test -e DESIGN.md` fails; `grep -n "npx\|Nintendo" .claude/skills/design-init/references/design-template.md` prints nothing; the template holds section-table decisions for target size, reading width, motion timing, units and table styling and a `## Claude Design System` section; `pnpm format:check` passes
- [ ] T022 Write the mapping from DESIGN.md onto the Design System artifact type
  - Requirements: FR-051, INV-006, INV-007
  - Seam: `design-init`'s files and `pnpm exec designmd lint` on the run's output
  - Files: .claude/skills/design-init/references/claude-design-system.md
  - Depends on: T021
  - Done when: reading it maps colors with their `-dark` siblings, typography, spacing, radius, brand prose and component prose, directs the build to the type's own `SKILL.md` read at run time, and names no `/design-sync` or `/design-login`
- [ ] T023 Rewrite `design-init`'s inputs, brief and decision rounds
  - Requirements: FR-043, FR-044, FR-045, FR-046, FR-047
  - Seam: `design-init`'s files and `pnpm exec designmd lint` on the run's output
  - Files: .claude/skills/design-init/SKILL.md
  - Depends on: T021
  - Done when: reading the skill meets each listed acceptance criterion and states the absent or unfilled DESIGN.md case
- [ ] T024 Finish `design-init` on lint and its own checks, guard an existing DESIGN.md, refuse values below a floor, and offer the Claude Design System build
  - Requirements: FR-048, FR-049, FR-050, FR-051, INV-005
  - Seam: `design-init`'s files and `pnpm exec designmd lint` on the run's output
  - Files: .claude/skills/design-init/SKILL.md
  - Depends on: T022, T023
  - Done when: reading the skill meets each listed acceptance criterion and contains no offer to delete itself
- [ ] T025 Have `curate-context` refuse values below a floor, state the absent-DESIGN.md case, and offer a warned re-sync after a DESIGN.md edit
  - Requirements: FR-043, FR-049, FR-052, INV-006
  - Seam: `design-init`'s files and `pnpm exec designmd lint` on the run's output
  - Files: .claude/skills/curate-context/SKILL.md
  - Depends on: T022
  - Done when: reading the skill meets each listed acceptance criterion
- [ ] T026 Describe `sdd-design` and every changed behavior in `CLAUDE.md`, the root `README.md`, `.claude/skills/README.md` and `.claude/sdd/README.md`
  - Requirements: FR-043, FR-053, INV-007
  - Seam: skill and document text, checked by `check-refs`
  - Files: CLAUDE.md, README.md, .claude/skills/README.md, .claude/sdd/README.md
  - Depends on: T011, T014, T016, T024, T025
  - Done when: reading the four files meets FR-053's acceptance criterion and states the absent-DESIGN.md case in `CLAUDE.md` and `README.md`; `git grep -n "design-sync\|design-login" -- .claude CLAUDE.md README.md docs/standards` prints nothing; the helper battery passes
- [ ] T027 Hand over the gut-check prompts for each changed skill
  - Requirements: NFR-003, FR-013, FR-028, FR-042, FR-048
  - Seam: skill and document text
  - Files: docs/sdd/claude-design-integration/gut-check.md
  - Depends on: T026
  - Done when: `gut-check.md` holds two or three task prompts with expected behavior per changed skill, and should-trigger and should-not-trigger prompts for each changed description; `pnpm format:check && pnpm test:scripts` passes
- [ ] P4 close: full suite green, changes staged by explicit path, slice verified and committed

## Verified elsewhere

- None

## Follow-ups (out of scope)

- None
