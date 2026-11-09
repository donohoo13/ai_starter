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

- [x] T001 Generate the design record template from a new Appendix B and scan `sdd-design` in `check-refs`
  - Requirements: FR-001
  - Seam: the helper CLI through `helpers.py`'s in-process runner
  - Files: .claude/sdd/bin/sdd, .claude/sdd/spec-driven-development.md, .claude/sdd/templates/design.md, .claude/sdd/tests/helpers.py, .claude/sdd/tests/test_templates.py
  - Done when: `test_templates.py` passes with sync writing five templates including `design.md` from Appendix B and the plan, tasks and review templates from Appendices C, D and E, and `check-refs` listing `sdd-design` among its scanned skills; the helper battery passes
  - Evidence: `python3 -m unittest discover -s .claude/sdd/tests -p test_templates.py` Ran 8 tests OK (red first: sync refused "Appendix B (Plan template) not found", sdd-design ref unchecked); `sdd templates sync` wrote design.md; helper battery all 3 checks passed
- [x] T002 Define the Design phase in the SDD document and renumber the phases and sections everywhere they are cited
  - Requirements: FR-001, FR-004
  - Seam: skill and document text, checked by `check-refs`
  - Files: .claude/sdd/spec-driven-development.md, .claude/sdd/README.md, .claude/skills/sdd-outline/SKILL.md, .claude/skills/sdd-plan/SKILL.md, .claude/skills/sdd-task/SKILL.md, .claude/skills/sdd-implement/SKILL.md, .claude/skills/sdd-review/SKILL.md, .claude/skills/sdd-outline/references/adversarial-review.md, .claude/skills/sdd-review/references/conformance-review.md
  - Depends on: T001
  - Done when: the helper battery passes; section 8 is Phase 2: Design (`sdd-design`) with steps, prompt, snapshot, misses, gaps and gate; sections 4 and 5 list `2. Design` and `design.md`; every skill precondition cites the renumbered label; `grep -rn "phase \`2. Plan\`\|phase \`5. Validate\`" .claude/skills` prints nothing
  - Evidence: helper battery all 3 checks passed (check-refs 47 references, 0 mismatched); section 8 holds State, Steps, The prompt, The snapshot, Misses and gaps, Gate; sections 4 and 5 list `2. Design` and `design.md`; preconditions cite `3. Plan`, `4. Tasks`, `5. Implement`, `6. Validate` and name `sdd-design` for `2. Design`; the grep printed nothing (exit 1)
- [x] T003 Add the UI surfaces section to the spec template and reject malformed or duplicate UI IDs in spec lint
  - Requirements: FR-007
  - Seam: the helper CLI through `helpers.py`'s in-process runner
  - Files: .claude/sdd/bin/sdd, .claude/sdd/spec-driven-development.md, .claude/sdd/templates/spec.md, .claude/sdd/tests/test_lint_spec.py, .claude/sdd/tests/helpers.py
  - Depends on: T001
  - Done when: `test_lint_spec.py` passes with cases for a valid `- UI-001: Settings screen (new)` line, a malformed ID and a duplicate ID; the regenerated spec template carries `## UI surfaces`; the helper battery passes
  - Evidence: `python3 -m unittest discover -s .claude/sdd/tests -p test_lint_spec.py` Ran 15 tests OK (red first: malformed and duplicate cases exited 0); `.claude/sdd/templates/spec.md` gained `## UI surfaces`; helper battery all 3 checks passed
- [x] T004 Record a design request, skip or approval in `design.md` through `set-status` and `approve`, linted
  - Requirements: FR-002, FR-024
  - Seam: the helper CLI through `helpers.py`'s in-process runner
  - Files: .claude/sdd/bin/sdd, .claude/sdd/tests/test_design.py, .claude/sdd/tests/test_approve.py, .claude/sdd/tests/helpers.py
  - Depends on: T001, T003
  - Done when: `test_design.py` and `test_approve.py` pass with cases for `set-status design requested` creating `design.md`, `set-status design skipped` recording `decided_by`, `surfaces` and `based_on`, `approve design` refusing on a lint error or a missing `link`, `version` or `read`, and approval recording `approved_hash` and `based_on`
  - Evidence: `test_design.py` Ran 8 tests OK and `test_approve.py` Ran 16 tests OK (red first: argparse rejected `design` for set-status and approve); cases cover request creating design.md, skip recording decided_by/surfaces/based_on, refusal on an unfilled placeholder and on each missing link/version/read, and approval recording approved_hash and based_on
- [x] T005 Report `2. Design` while a design is requested, changed or stale, and the renumbered labels otherwise
  - Requirements: FR-003, FR-004, FR-005
  - Seam: the helper CLI through `helpers.py`'s in-process runner
  - Files: .claude/sdd/bin/sdd, .claude/sdd/tests/test_status.py, .claude/sdd/tests/test_design.py
  - Depends on: T004
  - Done when: `test_status.py` passes with only its phase labels renumbered, and `test_design.py` passes with a `requested` design reporting `2. Design` and `sdd-design`, and a `skipped` design reporting `3. Plan`
  - Evidence: `test_status.py` Ran 14 tests OK with only phase labels renumbered (test_approve.py's two labels too); `test_design.py` Ran 14 tests OK with requested reporting `2. Design`/`sdd-design`, skipped and approved reporting `3. Plan`, changed or stale approved design back at `2. Design`, no design.md at `3. Plan` (red first: KeyError 'design' and '2. Plan' labels)
- [x] T006 Make the plan build on an approved design, so a later design approval or design change stales the plan and tasks
  - Requirements: FR-006
  - Seam: the helper CLI through `helpers.py`'s in-process runner
  - Files: .claude/sdd/bin/sdd, .claude/sdd/tests/test_design.py
  - Depends on: T005
  - Done when: `test_design.py` passes with a re-approved design staling the plan and tasks, a design approved after the plan staling the plan, and plan approval recording the design's `approved_hash` as `based_on`
  - Evidence: `test_design.py` Ran 18 tests OK: re-approved design stales plan and tasks, design approved after the plan stales it, plan approval records the design's approved_hash, a stale plan refreshes against it (red first: plan based_on held the spec hash and stale was False)
- [x] T007 Re-offer design when a re-approved spec lists a UI ID the skip does not cover
  - Requirements: FR-011
  - Seam: the helper CLI through `helpers.py`'s in-process runner
  - Files: .claude/sdd/bin/sdd, .claude/sdd/tests/test_design.py
  - Depends on: T005
  - Done when: `test_design.py` passes with a skip covering `UI-001` and a re-approved spec adding `UI-002` reporting `2. Design`, and a re-approved spec with no new ID reporting `3. Plan`
  - Evidence: `test_design.py` Ran 21 tests OK: skip covering UI-001 plus re-approved spec adding UI-002 reports `2. Design`, a re-approved spec with no new ID reports `3. Plan`, a second skip covers both (red first: the no-new-ID case reported the skip stale)
- [x] T008 Write the `sdd-design` skill that acts on `design.md`'s state: request, skip, cancel, record, re-check and approve, each staged on the user's word
  - Requirements: FR-010, FR-012, FR-013, FR-019, FR-024, FR-025, INV-001, INV-002
  - Seam: skill and document text, checked by `check-refs`
  - Files: .claude/skills/sdd-design/SKILL.md
  - Depends on: T002, T004
  - Done when: the helper battery passes; reading it meets each listed requirement's acceptance criterion, including no `/design` invocation and no artifact publish
  - Evidence: helper battery all 3 checks passed (check-refs 53 references across 13 files, sdd-design included); SKILL.md covers Request (FR-013), Skip or cancel (FR-010), staging and a proposed commit after each (FR-012), Revise the prompt (FR-019), Approve refused while a miss or gap is open (FR-024), Re-check (FR-025), never invoking `/design` or publishing (INV-001), every write on the user's word (INV-002)
- [x] T009 Write the design prompt template
  - Requirements: FR-014, FR-015, FR-016, FR-017, FR-018, INV-004
  - Seam: skill and document text
  - Files: .claude/skills/sdd-design/references/design-prompt.md
  - Depends on: T008
  - Done when: reading it meets each listed acceptance criterion; `grep -n "—" .claude/skills/sdd-design/references/design-prompt.md` prints nothing
  - Evidence: the em-dash grep printed nothing (exit 1); the template stands alone with no path, command or tool name (FR-014), carries goal, audience, every UI surface with its states and requirement IDs, widths and non-goals in product terms (FR-015), asks for two or three directions on a named primary screen then one titled artboard per screen and state (FR-016), covers the three DESIGN.md cases with no token restated beside a link (FR-017), states the WCAG 2.2 AA floors, the three deferred values and the no-em-dash copy rule (FR-018), and bars secrets, credentials, PII and restricted material (INV-004)
- [x] T010 Write the record procedure: read the link, save the snapshot, list artboards, and put each miss and gap to the user
  - Requirements: FR-020, FR-021, FR-022, FR-023
  - Seam: skill and document text
  - Files: .claude/skills/sdd-design/references/record-design.md
  - Depends on: T008
  - Done when: reading it meets each listed acceptance criterion and covers the edge cases for an unreadable link, no Artifact tool, another owner's artifact, an unexpected file layout and a mismatched design system
  - Evidence: record-design.md reads the link, lists and fetches `project/canvas.json`, every `project/*.dc.html` and `tokens.json`, deletes earlier artboards before saving (FR-020), records link, read, version, design_system and one artboard line per file with its PNG (FR-021), asks revise-or-accept per miss (FR-022) and add-or-exclude per gap with `sdd-outline` routing (FR-023), and stops with no snapshot for an unreadable link, no Artifact tool, another owner's artifact and an unexpected layout, asking on a mismatched design system; prettier passes
- [x] T011 Have `sdd-outline` write the UI surfaces section and offer `sdd-design` or record a skip at its finish
  - Requirements: FR-008, INV-002
  - Seam: skill and document text
  - Files: .claude/skills/sdd-outline/SKILL.md, .claude/sdd/spec-driven-development.md
  - Depends on: T003, T004
  - Done when: reading the skill and section 7 meets FR-008's acceptance criterion; the helper battery passes
  - Evidence: sdd-outline's Draft step writes UI surfaces and its Finish names each listed surface, offers `sdd-design` with `sdd-plan` as the alternative, records a skip only on the user's word through `set-status design skipped` with name, date and covered surfaces, and names only `sdd-plan` with no design.md when no surface is listed; section 7's Gate says the same (FR-008, INV-002); helper battery all 3 checks passed
- [x] T012 Have `sdd-plan` ask about design for an undecided UI spec and load an approved design into Affected code and Traceability
  - Requirements: FR-009, FR-026
  - Seam: skill and document text
  - Files: .claude/skills/sdd-plan/SKILL.md, .claude/sdd/spec-driven-development.md
  - Depends on: T004
  - Done when: reading the skill and the Plan section meets both acceptance criteria; the helper battery passes
  - Evidence: sdd-plan's Preconditions ask run-or-skip for a UI spec with no design.md and record a skip with name, date and covered surfaces before planning (FR-009); Start loads an approved design.md, `based_on` follows the design's approved_hash, and Fill Traceability names the components per designed surface by UI ID and plans nothing under Not built (FR-026); section 9 gains Settle the design and the Affected code and Traceability rules; helper battery all 3 checks passed
- [x] T013 Have the `implementer` read a designed surface's artboards and skip what `design.md` records as not built
  - Requirements: FR-027
  - Seam: agent text
  - Files: .claude/agents/implementer.md
  - Depends on: T010
  - Done when: the Load section names `design.md` and the matching artboard files for a task on a designed surface and the not-built list; the process battery passes
  - Evidence: implementer.md's Load section directs a task on a designed surface to `design.md`'s Artboards lines and the matching `*.dc.html` files, building from the project's tokens and components and nothing under Not built (FR-027); `pnpm exec node scripts/test/process-suite.battery.mjs` all process-suite checks passed
- [x] P1 close: full suite green, changes staged by explicit path, slice verified and committed

## P2: Opt into render checks when the build starts

- [x] T014 Ask for render-check surfaces at the start of a build, recommend by criterion, record the answer in `tasks.md`'s frontmatter, and allow `sdd-implement` to name `render-checker` in the process-suite battery
  - Requirements: FR-028, FR-029, FR-030, FR-035
  - Seam: skill and agent text
  - Files: .claude/skills/sdd-implement/SKILL.md, .claude/sdd/spec-driven-development.md, scripts/test/process-suite.battery.mjs
  - Done when: the process battery fails once the skill names `render-checker` before the allowlist change, passes after it, and still fails for a scratch skill naming `render-checker`, which is then removed, all three runs in the Evidence line; reading the skill and the Implement section meets the three acceptance criteria, including the amended write list and the commit before the next dispatch; the helper battery passes
  - Evidence: process battery red with the skill naming `render-checker` ("FAIL only render-check dispatches render-checker — also named in .claude/skills/sdd-implement/SKILL.md", exit 1), green after the allowlist change (exit 0), red again for scratch `.claude/skills/zz-scratch/SKILL.md` (exit 1, then removed); sdd-implement Steps step 3 and section 11 step 3 ask on first start or resume with the four criteria, record `render_check` in frontmatter, commit before the next dispatch, run nothing on `none` (FR-028 to FR-030), both write lists amended; helper battery all 3 checks passed
- [x] T015 Dispatch `render-checker` once before QA for the approved surfaces and put its failures into the QA script
  - Requirements: FR-031, FR-032, NFR-002
  - Seam: skill and agent text
  - Files: .claude/skills/sdd-implement/SKILL.md
  - Depends on: T014
  - Done when: reading the skill meets the acceptance criteria and NFR-002; the process battery passes
  - Evidence: sdd-implement QA step 3 dispatches `render-checker` once for every approved surface before the script, with the URL, UI IDs with states from the spec and Artboards lines, themes from DESIGN.md and the app's theme styles, and the FR-033 bar (FR-031), skipped with no render results on `none`; step 4 lists each failure with evidence and screenshot path and QA bug sends only picked failures, one fresh `implementer` each (FR-032); the brief asks for the report with paths and never images, kept off this session (NFR-002); `pnpm exec node scripts/test/process-suite.battery.mjs` all process-suite checks passed
- [x] T016 Judge render checks against the floors, DESIGN.md and the design snapshot, and accept both dispatchers
  - Requirements: FR-033, FR-034, FR-043
  - Seam: skill and agent text
  - Files: .claude/agents/render-checker.md, .claude/skills/render-check/SKILL.md
  - Depends on: T014
  - Done when: reading both files meets FR-033 and FR-034's acceptance criteria and states the absent-DESIGN.md case; `grep -n "Design Requirements\|44×44" .claude/agents/render-checker.md` prints nothing; the process battery passes
  - Evidence: the grep printed nothing (exit 1); render-checker's bar names the WCAG 2.2 AA floors, DESIGN.md or the starting values with the absent-or-unfilled case and brand decisions undecided until `design-init` (FR-043), and the snapshot's states, controls and labeled fields minus Not built, measures targets against DESIGN.md or 38×38px with the 24×24 floor, and compares no copy, sample data or pixels (FR-033); its description names both dispatchers, `/render-check` keeps its arguments and its bar step names the same sources plus the spec's UI surfaces and states (FR-034); process battery all process-suite checks passed
- [x] P2 close: full suite green, changes staged by explicit path, slice verified and committed

## P3: Design values each project decides

- [x] T017 Rewrite `ux-standards.md` to WCAG 2.2 AA floors and labeled starting values
  - Requirements: FR-036, FR-040, INV-005
  - Seam: the standards and agent files themselves
  - Files: docs/standards/ux-standards.md
  - Done when: reading the file meets FR-036 and FR-040's acceptance criteria; `grep -n "WCAG 2.1" docs/standards/ux-standards.md` prints nothing; `pnpm format:check` passes
  - Evidence: `grep -n "WCAG 2.1"` printed nothing (exit 1; red first: line 14 matched); Floors cite WCAG 2.2 AA SCs 2.5.8 (24×24 CSS px), 1.4.3, 1.4.11, 2.1.1, 2.4.3, 2.4.7, 2.4.11, 4.1.2 and the Core Web Vitals thresholds, Starting values label 38×38px target size, `70ch` reading width, 100–300ms motion, feedback timing and the Data tables monospaced numerics and hairline dividers (FR-036, INV-005), the absent/placeholder/silent statement appears once (FR-040); `prettier --check` passes on the file, and `pnpm format:check` fails only on the pre-existing `design-init/references/design-template.md`
- [x] T018 Rewrite `frontend-styling.md`'s units as a principle and state that designs are references
  - Requirements: FR-038, FR-040, FR-041, FR-043, INV-003
  - Seam: the standards and agent files themselves
  - Files: docs/standards/frontend-styling.md
  - Done when: reading the file meets each listed acceptance criterion, keeps the `svh`-first rule with its fixed-or-sticky caveat, and states the absent-DESIGN.md case; `pnpm format:check` passes
  - Evidence: "Do not use px" and "never with `vh`" removed (ban grep exit 1); units principle names rem, em, %, `clamp()`, `svh` and `dvh` (FR-038), the `svh`-first rule with its fixed-or-sticky caveat and one-line reason is a labeled starting value, the absent/placeholder/silent statement appears once with brand decisions undecided until `design-init` (FR-040, FR-043), Designs are references states snapshots and Claude Design markup are references built from tokens and components and bars `<x-dc>`, `<dc-import>`, `data-dc-script` and `support.js` (FR-041, INV-003); `prettier --check` passes on the file, `pnpm format:check` fails only on the pre-existing design-template.md
- [x] T019 Rewrite `html-tables.md` to keep markup floors and label styling choices as starting values
  - Requirements: FR-038, FR-039, FR-040
  - Seam: the standards and agent files themselves
  - Files: docs/standards/html-tables.md
  - Done when: reading the file meets each listed acceptance criterion; `grep -n "never \`px\`" docs/standards/html-tables.md`prints nothing;`pnpm format:check` passes
  - Evidence: the Done-when never-px grep printed nothing (exit 1; red first: line 24 matched); Markup and Layout read as requirements (caption, `th` scope, no layout tables), Styling (starting values) labels cell padding, row separation, header treatment and caption, units follow the scaling principle with `%`, `ch`, `clamp()`, `em` and `rem`, and a viewport-height scroll wrapper takes `svh`, or `dvh` only without a sticky or fixed descendant, as a labeled starting value (FR-038, FR-039); the absent/placeholder/silent statement appears once (FR-040); `prettier --check` passes on the file, `pnpm format:check` fails only on the pre-existing design-template.md
- [x] T020 Have the `implementer` self-check and `standards-reviewer` judge surface diffs against DESIGN.md, the floors and runtime markup
  - Requirements: FR-042, FR-043, INV-003, INV-005
  - Seam: the standards and agent files themselves
  - Files: .claude/agents/implementer.md, .claude/agents/standards-reviewer.md
  - Depends on: T017
  - Done when: reading both files meets FR-042's acceptance criterion, states the absent-DESIGN.md case, and `standards-reviewer` names `<x-dc>`, `<dc-import>`, `data-dc-script` and `support.js` as findings; the process battery passes
  - Evidence: implementer's Check against the standards step 2 and standards-reviewer's Method step 5 add `DESIGN.md` to the bar on a `ux-standards.md` path, the starting values when it is absent, holds bracket placeholders or is silent with brand decisions undecided until `design-init`, and the floor with the `DESIGN.md` line named when a value falls below it (FR-042, FR-043, INV-005); standards-reviewer reports `<x-dc>`, `<dc-import>`, `data-dc-script` and `support.js` in a surface path as a finding (INV-003); `pnpm exec node scripts/test/process-suite.battery.mjs` all process-suite checks passed
- [x] P3 close: full suite green, changes staged by explicit path, slice verified and committed

## P4: Generate DESIGN.md from the skill's own template

- [x] T021 Rewrite the DESIGN.md template inside `design-init` with the deferred-value decisions and the Claude Design System section, and delete the root DESIGN.md
  - Requirements: FR-037
  - Seam: `design-init`'s files and `pnpm exec designmd lint` on the run's output
  - Files: .claude/skills/design-init/references/design-template.md, DESIGN.md
  - Done when: `test -e DESIGN.md` fails; `grep -n "npx\|Nintendo" .claude/skills/design-init/references/design-template.md` prints nothing; the template holds section-table decisions for target size, reading width, motion timing, units and table styling and a `## Claude Design System` section; `pnpm format:check` passes
  - Evidence: `test -e DESIGN.md` exit 1 and the npx/Nintendo grep exit 1 (red first: exit 0 and 7 matches); the template is the root scaffold with `pnpm exec designmd`, one sentence per line, decision tables for reading width (Typography Measure), target size with its 24×24 floor (Layout Accessibility), units (Layout Units), motion timing (Motion) and row separation, numeric type and caption (Components Data), each naming its starting value, and a `## Claude Design System` `- Link:` section; `designmd lint` on it reports the scaffold's 57 placeholder errors and 0 warnings, identical to the root's; `pnpm format:check` passes
- [x] T022 Write the mapping from DESIGN.md onto the Design System artifact type
  - Requirements: FR-051, INV-006, INV-007
  - Seam: `design-init`'s files and `pnpm exec designmd lint` on the run's output
  - Files: .claude/skills/design-init/references/claude-design-system.md
  - Depends on: T021
  - Done when: reading it maps colors with their `-dark` siblings, typography, spacing, radius, brand prose and component prose, directs the build to the type's own `SKILL.md` read at run time, and names no `/design-sync` or `/design-login`
  - Evidence: the design-sync/design-login grep exit 1 (the file did not exist before); claude-design-system.md maps color roles with each `-dark` sibling as the same token's dark-theme value, typography styles and families, spacing, radius, the Overview, Voice & Copy and Do's and Don'ts brand book and per-component READMEs (FR-051), reads the Design System type's `SKILL.md` through the Artifact tool at run time and lets it win on shapes, writes only from DESIGN.md and copies nothing back (INV-006), names neither command (INV-007), and covers build, warned re-sync and refusal; `prettier --check` passes
- [x] T023 Rewrite `design-init`'s inputs, brief and decision rounds
  - Requirements: FR-043, FR-044, FR-045, FR-046, FR-047
  - Seam: `design-init`'s files and `pnpm exec designmd lint` on the run's output
  - Files: .claude/skills/design-init/SKILL.md
  - Depends on: T021
  - Done when: reading the skill meets each listed acceptance criterion and states the absent or unfilled DESIGN.md case
  - Evidence: design-init's Start states that an absent or bracket-placeholder DESIGN.md leaves the starting values applying and brand decisions undecided until this run (FR-043); Inputs names the overview as authority with the four facts asked when it is unfilled, the user's context, an optional reference by path or URL treated as data, and an optional mood board whose absence never stops the run (FR-044); The reference carries the listed structure, replaces identifying elements, writes prose fresh and fixes defects (FR-045); The brief and five rounds in order with the Do's and Don'ts harvest (FR-046); two to four questions each with a recommendation, one-line reason, alternatives, computed contrast ratios and the "go with your recommendations" shortcut (FR-047); `prettier --check` and the process battery pass
- [x] T024 Finish `design-init` on lint and its own checks, guard an existing DESIGN.md, refuse values below a floor, and offer the Claude Design System build
  - Requirements: FR-048, FR-049, FR-050, FR-051, INV-005
  - Seam: `design-init`'s files and `pnpm exec designmd lint` on the run's output
  - Files: .claude/skills/design-init/SKILL.md
  - Depends on: T022, T023
  - Done when: reading the skill meets each listed acceptance criterion and contains no offer to delete itself
  - Evidence: the self-deletion grep exit 1 (red first: line 83 offered to delete `.claude/skills/design-init/`); Finish writes DESIGN.md with every placeholder filled, `omitted:` and the authoring comment deleted, and ends only on `designmd lint` 0 errors, no contrast warnings and `-dark`-only orphans plus a search for restated values, unpaired Don'ts and reference residue (FR-048); Floors refuses a below-floor value naming 2.5.8 for a 20×20px target (FR-049, INV-005); Start asks before any write to a filled DESIGN.md, offers a revision and reports its blast radius and `designmd diff` before it lands (FR-050); The Design System in Claude offers a build or re-sync through `references/claude-design-system.md`, records the link on success and deletes the section on a decline, no Artifact tool or refused first build (FR-051); `prettier --check` and the process battery pass
- [x] T025 Have `curate-context` refuse values below a floor, state the absent-DESIGN.md case, and offer a warned re-sync after a DESIGN.md edit
  - Requirements: FR-043, FR-049, FR-052, INV-006
  - Seam: `design-init`'s files and `pnpm exec designmd lint` on the run's output
  - Files: .claude/skills/curate-context/SKILL.md
  - Depends on: T022
  - Done when: reading the skill meets each listed acceptance criterion
  - Evidence: before the edit the skill had no below-floor refusal, absent-DESIGN.md clause or re-sync offer (its only "floor" match was the routing line); its new DESIGN.md section states that an absent or bracket-placeholder DESIGN.md leaves the starting values applying and brand decisions undecided until `design-init` runs (FR-043), refuses a below-floor value naming 2.5.8 for a 20×20px target (FR-049), and, once an approved edit lands with a recorded link, offers a re-sync through `design-init/references/claude-design-system.md` after warning that edits made in Claude will be replaced, copying nothing back (FR-052, INV-006); `prettier --check` and the process battery pass
- [x] T026 Describe `sdd-design` and every changed behavior in `CLAUDE.md`, the root `README.md`, `.claude/skills/README.md` and `.claude/sdd/README.md`
  - Requirements: FR-043, FR-053, INV-007
  - Seam: skill and document text, checked by `check-refs`
  - Files: CLAUDE.md, README.md, .claude/skills/README.md, .claude/sdd/README.md
  - Depends on: T011, T014, T016, T024, T025
  - Done when: reading the four files meets FR-053's acceptance criterion and states the absent-DESIGN.md case in `CLAUDE.md` and `README.md`; `git grep -n "design-sync\|design-login" -- .claude CLAUDE.md README.md docs/standards` prints nothing; the helper battery passes
  - Evidence: red first, the four files said "five SDD skills", "one and done", "offers to delete itself" and "runs a render pass only when the user starts it"; now each lists `sdd-design` with the SDD skills, the skills README renumbers phases 2 to 6 and describes the changed `sdd-outline`, `sdd-plan`, `sdd-implement`, `render-check`, `design-init` and `curate-context`, none has `design-init` deleting itself or render passes only through `/render-check`, and every description of `render-checker` names `render-check` and `sdd-implement` (FR-053); `CLAUDE.md` and `README.md` state that an absent or bracket-placeholder DESIGN.md leaves the starting values applying and brand decisions undecided until `design-init` writes it (FR-043); the design-sync/design-login `git grep` exit 1 (INV-007); helper battery all 3 checks passed (check-refs 54 references across 15 files)
- [x] T027 Hand over the gut-check prompts for each changed skill
  - Requirements: NFR-003, FR-013, FR-028, FR-042, FR-048
  - Seam: skill and document text
  - Files: docs/sdd/claude-design-integration/gut-check.md
  - Depends on: T026
  - Done when: `gut-check.md` holds two or three task prompts with expected behavior per changed skill, and should-trigger and should-not-trigger prompts for each changed description; `pnpm format:check && pnpm test:scripts` passes
  - Evidence: `gut-check.md` holds two or three task prompts with a stated pass per changed skill (`sdd-design`, `sdd-outline`, `sdd-plan`, `sdd-task`, `sdd-implement`, `sdd-review`, `render-check`, `design-init`, `curate-context`), covering FR-013, FR-028, FR-042 and FR-048, should-trigger and near-miss should-not-trigger prompts for each skill whose description changed against `main`, agent checks and a Results section; `pnpm format:check && pnpm test:scripts` exit 0, every battery passed
- [x] P4 close: full suite green, changes staged by explicit path, slice verified and committed

## Verified elsewhere

- None

## Follow-ups (out of scope)

- `docs/standards/transactional-email.md` line 28 calls its 44×44px CTA target "the `ux-standards.md` touch-target floor"; once T017 sets the floor at 24×24 and 38×38px as a starting value, that cross-reference is wrong, and no task touches the file.
- `docs/standards/frontend-styling.md` line 9 links `[DESIGN.md](../../DESIGN.md)`, which resolves to nothing in the template now that the root DESIGN.md is gone, and resolves again in a project once `design-init` writes it; no task in this slice touches that file.
- `.claude/skills/design-init/references/brand-research.md` lines 13 and 21 still call the mood board a "gate"; `design-init` now treats the board as an optional input that never stops a run, and no task in this slice touches that file.
