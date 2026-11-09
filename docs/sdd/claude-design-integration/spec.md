---
title: Claude design integration
slug: claude-design-integration
branch: feature/claude-design-integration
status: approved
owner: Conner Donohoo
created: 2026-11-09
updated: 2026-11-09
approved_hash: eb9fb0dc5a14
description: Adds an optional Design phase to the SDD chain that hands a spec to Claude Design and records the approved mockups, and moves fixed design values from the standards into DESIGN.md. The result is approved designs before planning, project-owned design values and opt-in render checks.
---

# Claude design integration

## Summary

The template's spec-driven development chain goes from an approved spec straight to a technical plan, and its standards hard-code design values such as touch-target size, reading width and allowed CSS units.
No phase requests, waits for or records a UI design, so implementer agents decide layout and flow mid-build and the hard-coded values override each project's own design system.
Claude Design now runs as artifacts in Claude and in Claude Code, so a project can get mockups designed against its own design system before any plan exists.
Without a gate for that work, approved designs never reach the plan, design changes that imply new behavior bypass the spec, and nobody sees a layout until QA.
The change adds an optional Design phase that writes a Claude Design prompt from the approved spec and records the design the user approves, makes DESIGN.md the authority the standards defer to, and rebuilds design-init around a template it carries.
Design approval becomes a gate with its own state in the SDD helper, and every design value lives in one file that each project decides.
A UI spec now passes through an approved, committed design before planning, render checks run only on surfaces the user picks, and the design system in Claude is rebuilt from the repository.

## Problem and context

Who is affected: projects created from this template that ship a user interface, the user who approves each SDD gate, and the `implementer` agents that build UI slices.

Current state, from the code:

- `.claude/sdd/bin/sdd` hard-codes `ARTIFACTS = ("spec", "plan", "tasks", "review")` and `UPSTREAM = {"plan": "spec", "tasks": "plan"}`, and `derive_phase` moves from an approved spec straight to `2. Plan`.
  No artifact or state represents a design or a wait on a conversation outside the session, and `.claude/sdd/tests/test_status.py` asserts the labels `2. Plan` to `5. Validate`.
- No SDD skill produces or consumes a UI design.
  `.claude/agents/implementer.md` lets the agent decide any gap "that changes only how the slice is built", so layout and flow choices land as judgment calls the user first sees at QA.
- `.claude/agents/render-checker.md` reads "the spec's Design Requirements" as its bar, a section the spec template dropped when the SDD chain replaced the spec suite in the unreleased v0.3.0, and its method measures every control against a fixed 44×44px target.
  `.claude/skills/render-check/SKILL.md` is user-only (`disable-model-invocation: true`) and states that it never runs from another skill, `CLAUDE.md` says it runs "only when the user starts it", and `checkRenderCheckerHasOneDispatcher` in `scripts/test/process-suite.battery.mjs` fails CI when any file other than `render-check` names `render-checker`.
- The standards fix choices a project's design system should own.
  `docs/standards/ux-standards.md` sets 44×44px targets, a ~70ch reading width, 100–300ms motion, hairline row dividers and a monospaced family for numerics, and cites WCAG 2.1 AA.
  `docs/standards/frontend-styling.md` says "Do not use px" and "never with `vh`", and `docs/standards/html-tables.md` fixes cell padding at `0.5em`–`0.75em`, the row-separation device, and column widths in `%` or `ch`, "never `px`".
  The root DESIGN.md scaffold caps body text at ~65ch, contradicting the 70ch in `ux-standards.md`.
- The blank DESIGN.md scaffold ships at the repository root as its only working copy, and `design-init` fills it in place, so the template is gone after first use.
  A curated copy committed at `.claude/skills/design-init/references/design-template.md` has already drifted from the root: it calls `npx @google/design.md`, which `CLAUDE.md` denies to AI sessions, cites an analysis that is not in the repository, and holds paragraphs on single lines.
- `docs/company/company-overview.md` and the root DESIGN.md ship with bracket placeholders, so a new project can hold both files unfilled.
- The Google design.md format types a front-matter dimension only in `px`, `em` or `rem` (`node_modules/@google/design.md/dist/spec-config.yaml`), so a reading width in `ch` or a motion timing in `ms` has no typed front-matter slot; the template's authoring rule already puts such values in their section's own table.

Current state of Claude Design, verified on 2026-11-09:

- Claude Design is a template for artifacts, used from a Claude chat (Output > Design) or from Claude Code through the bundled `/design` skill (Claude Code v2.1.265 or later); the standalone site at claude.ai/design closes on 2026-12-14 ([Get started with Claude Design](https://support.claude.com/en/articles/14604416-get-started-with-claude-design); [Claude Code commands](https://code.claude.com/docs/en/commands.md)).
- A design system is a Design System artifact holding a README brand book, a `tokens.json` with a value per theme and a usage note per token, components with guidelines and previews, assets and fonts; a design copies its system's tokens when created and does not update after ([Design System artifact type](https://claude.ai/artifact/5M7UeXXcx16TP3vzVFNDzd), read in-session; [Claude Academy](https://academy.claude.com/tutorials/create-a-design-system-with-claude)).
- The Design artifact type's instructions tell the design conversation to use a design system the user names, before any default ([Design artifact type](https://claude.ai/artifact/QKN21svewxgyPb6SYRqWnd), read in-session).
- Sync runs one way, from a repository into Claude; nothing documented copies Claude-side edits back into a repository ([Claude Academy](https://academy.claude.com/tutorials/create-a-design-system-with-claude)).
- `/design-sync` and `/design-login` target the standalone site, and the design-sync tool states that the server refuses uploads to a design system moved into Claude ([Claude Code commands](https://code.claude.com/docs/en/commands.md); this session's DesignSync tool description).
- Claude Design has no version history, so a link cannot pin the version a user approved ([Get started with Claude Design](https://support.claude.com/en/articles/14604416-get-started-with-claude-design)).
- A Claude Code session reads a Design artifact's files through its link when the user owns it: reads of two Design canvases on 2026-11-09 listed `project/canvas.json`, one `project/*.dc.html` file per artboard, and the copied design system under `project/ds/`, with the artifact's version id.
  The Artifact tool returns a summary instead of files for an artifact someone else owns.

Distinct problems, all confirmed:

1. The chain has no gate where a UI design is produced and approved before the plan commits to components, files and states.
2. Nothing turns an approved spec into a prompt for a separate Claude Design conversation.
3. Nothing records an approved design in the repository, checks it against the spec, or holds the chain while the design is out.
4. A design review surfaces behavior the spec never covered, and the chain has no path for it back to the spec.
5. The chain cannot offer a render check, and `render-checker`'s bar points at a section that no longer exists.
6. The standards hard-code choices that belong to each project's design system.
7. `design-init` loses its template on first use, and nothing builds a design system in Claude from the repository.

## Goals

- G1: A spec that lists a UI surface can get a Claude Design mockup approved before planning, with the prompt and a snapshot of the approved design committed beside the spec.
- G2: The plan and the implementers build against the recorded design, and behavior the design adds reaches the spec before planning starts.
- G3: Render checks run in `sdd-implement` only on the surfaces the user approves, in a subagent, once before QA.
- G4: Every choice the rewritten standards leave to a project is a starting value DESIGN.md may change, and every value they fix is a cited WCAG 2.2 AA floor or Core Web Vitals threshold.
- G5: `design-init` writes a complete, lint-clean DESIGN.md from a template it carries, and offers a design system in Claude built from that DESIGN.md.

## Non-goals

- Moving DESIGN.md away from the repository root; the user decided it stays.
- Running or steering the design conversation from the SDD session, which only writes the prompt and records the result.
- Using `/design-sync` or `/design-login`, which target the standalone site that closes on 2026-12-14.
- Copying edits made to the design system in Claude back into the repository; changes flow from DESIGN.md into Claude only.
- Building live components (a compiled component bundle) into the design system in Claude from application code; it carries DESIGN.md's tokens, brand book and component guidelines.
- Comparing the built UI against the design pixel for pixel.
- Re-running a render check after a QA fix; the user confirms the fix during QA.
- Changing `docs/standards/transactional-email.md`, whose fixed values are email-client limits, not brand choices.
- A `CHANGELOG.md` entry for this change; the user plans to restart the changelog, decided by Conner Donohoo.
- Changing projects already created from the template; propagation is pull-only.
- A staged rollout across several pull requests; the change ships in one pull request, decided by Conner Donohoo.

## User scenarios

Skills are prompts, so each scenario's independent test pairs automated checks with the gut-check prompts `.claude/rules/skill-authoring.md` requires, which the user runs in a fresh session and records in `docs/sdd/claude-design-integration/gut-check.md`.

### P1: Approve a design before planning

As the user running the SDD chain on a spec with a UI surface, I want the chain to hand me a Claude Design prompt and record the design I approve, so that planning and the build follow an approved design.
Independent test: the helper's unit tests cover every design status and phase transition, and the user's gut-check run of `sdd-design` on a fixture spec produces a prompt and records one of the user's own Design artifact links as a committed snapshot.

- Given an approved spec listing a settings screen, when `sdd-outline` finishes, then it names the settings screen and offers `sdd-design` before `sdd-plan`.
- Given a requested design, when `sdd-plan` starts, then it stops and names `sdd-design`.
- Given an approved design link, when the user brings it back, then the snapshot and `design.md` are written, each gap and miss is put to the user, and approval is recorded only on the user's word.

### P2: Opt into render checks when the build starts

As the user starting `sdd-implement`, I want to pick which surfaces get a render check from a recommendation, so that only the risky surfaces cost the time.
Independent test: file-content checks on `sdd-implement`, `render-checker` and `render-check`, the process-suite battery passing with `sdd-implement` as a second dispatcher, and the user's gut-check run in a project that ships UI.

- Given a spec listing a new list screen and an edited header, when the build starts, then the user sees both with a recommendation and a reason each.
- Given no surface approved, when every slice is committed, then no render check runs and QA starts.
- Given an approved surface that fails, when QA starts, then the failure is in the QA script with its evidence and screenshot path.

### P3: Design values each project decides

As a project owner, I want the standards to state principles and starting values and defer the specifics to DESIGN.md, so that each project's design system can give the product its own character.
Independent test: reading the three rewritten standards finds every choice labeled a starting value and every fixed value cited to WCAG 2.2 AA or Core Web Vitals.

- Given a DESIGN.md that sets a 44×44px target size, when `standards-reviewer` judges a surface diff, then it judges target size against 44×44px.
- Given no DESIGN.md, when it judges the same diff, then it judges against the 38×38px starting value.

### P4: Generate DESIGN.md from the skill's own template

As the owner of a new project, I want `design-init` to interview me from the company overview and any reference I give, and write a complete DESIGN.md, so that the project's design system exists before the first surface is built.
Independent test: the template file checks of FR-037, and the user's gut-check run of `design-init` on a fixture overview and reference DESIGN.md, whose output passes `pnpm exec designmd lint` and the brand-residue check of FR-048.

- Given a new project with no DESIGN.md, when `design-init` finishes, then DESIGN.md exists at the root and lint reports 0 errors.
- Given a reference DESIGN.md for another brand, when `design-init` finishes, then its spacing scale is carried over and its brand names, palette and typefaces are not.

## Requirements

### Functional

#### Design phase in the chain

- FR-001: The SDD document shall define a Design phase between Outline and Plan, run by a new `sdd-design` skill, with its own section, rows in the workflow and state tables, and a `design.md` template in an appendix, and shall renumber the phases to `1. Outline`, `2. Design`, `3. Plan`, `4. Tasks`, `5. Implement` and `6. Validate`, with its later sections renumbered to match.
  - Acceptance: Given the document and the skills, when `.claude/sdd/bin/sdd templates sync --check` and `.claude/sdd/bin/sdd check-refs` run, then both pass, `sdd-design` is among the skills `check-refs` scans, and `.claude/sdd/templates/design.md` is generated from the appendix.
- FR-002: The helper shall track `design.md` with the statuses `requested`, `approved` and `skipped`, writing `based_on` as the spec's `approved_hash` when the design is requested, skipped or approved, and `approved_hash` at approval.
  - Acceptance: Given a spec folder, when the helper records a request, a skip or an approval, then `design.md`'s frontmatter shows that status and the spec's current `approved_hash` as `based_on`, and approval is refused while `sdd lint` reports an error in `design.md`.
- FR-003: While `design.md` is `requested`, or `approved` but changed or stale, `sdd status` shall report `2. Design` and name `sdd-design`.
  - Acceptance: Given an approved spec and a `requested` design, when `sdd status {slug} --json` runs, then `phase` is `2. Design` and `skill` is `sdd-design`.
- FR-004: While `sdd status` reports `2. Design`, `sdd-plan`, `sdd-task` and `sdd-implement` shall refuse to start and name `sdd-design`.
  - Acceptance: Given a `requested` design, when each of the three skills starts, then it writes nothing and names `sdd-design`.
- FR-005: When `design.md` is absent, or `skipped` and still covering every UI surface the spec lists, the helper shall derive the same phase sequence as before this change, under the renumbered labels.
  - Acceptance: Given the helper's existing status fixtures, none of which has a `design.md`, when the suite runs, then every existing assertion passes with only its phase label renumbered; given a `skipped` design, `phase` is `3. Plan`.
- FR-006: The plan shall record the design's `approved_hash` as its `based_on` when the design is approved, so that a design approved after the plan, or an approved design that changes or goes stale, makes the plan and every artifact downstream of it stale.
  - Acceptance: Given an approved spec, design and plan, when the design is re-approved with a new hash, then `sdd status` reports the plan and tasks stale; given an approved plan with no design, when a design is then approved, then the plan is stale.
- FR-007: The spec template and section 7 of the SDD document shall add a UI surfaces section that lists, once, each screen, page, view, component or email template the spec changes or creates, marking each new or edited; CLI output and API responses are not UI surfaces.
  - Acceptance: Given the spec template, then it carries the section; given a spec whose UI surfaces section lists a settings screen, then later skills read the list from that section.

#### Offering the design step

- FR-008: When `sdd-outline` finishes an approved spec whose UI surfaces section lists a surface, it shall offer `sdd-design` as the next skill with `sdd-plan` as the alternative, and on a skip record `design.md` as `skipped` with the date, the git `user.name`, and the surfaces the skip covers.
  - Acceptance: Given an approved spec listing a settings screen, when `sdd-outline` finishes, then its handoff names the settings screen and offers `sdd-design`, and a skip writes `design.md` as described; given a spec that lists no UI surface, it names `sdd-plan` only and writes no `design.md`.
- FR-009: When `sdd-plan` starts on an approved spec that lists a UI surface and has no `design.md`, it shall ask whether to run `sdd-design` or skip it, and record a skip as FR-008 does before planning.
  - Acceptance: Given that state, when the user picks skip, then `design.md` is `skipped` with the date, name and covered surfaces, and planning continues.
- FR-010: When the user cancels a requested design, `sdd-design` shall record it as `skipped` with the date, the git `user.name`, the reason and the surfaces it covers.
  - Acceptance: Given a `requested` design, when the user cancels it, then `design.md` is `skipped` with those fields and `sdd status` reports `3. Plan`.
- FR-011: When a re-approved spec lists a UI surface that a `skipped` design does not cover, the chain shall offer `sdd-design` again for the new surfaces before planning.
  - Acceptance: Given a skip covering a settings screen and a re-approved spec adding a profile screen, when `sdd status` runs, then it reports `2. Design`; given a re-approved spec with no new surface, it reports `3. Plan`.
- FR-012: `sdd-design` shall stage `design.md` by explicit path and propose a commit message whenever it records a request, a skip or a cancel, and the user commits.
  - Acceptance: Given each of the three events, then `design.md` is staged and uncommitted, and a commit message is proposed.

#### The design prompt

- FR-013: When the user requests a design, `sdd-design` shall write a design prompt into `design.md`'s Prompt section, show the same text in the conversation as one copyable block, and set the design to `requested`.
  - Acceptance: Given an approved UI spec, when the user requests a design, then the Prompt section and the shown block are identical and `design.md` is `requested`.
- FR-014: The prompt shall stand alone after `/design` in a Claude Code session or pasted into a Claude chat.
  - Acceptance: Given a generated prompt, then it contains no repository path, no shell command, no SDD tool name, and no reference to a document or context outside the prompt other than the design system link; requirement IDs are allowed.
- FR-015: The prompt shall carry the spec's goal and audience, every surface in the spec's UI surfaces section with each state the spec names (including empty, loading and error states from its edge cases) and the requirement IDs each serves, the devices or widths the spec requires, and the spec's non-goals restated in product terms as things not to design.
  - Acceptance: Given a spec whose FR-002 names the empty state of a listed list screen, when the prompt is generated, then it names that empty state with FR-002, and no non-goal appears with a path, command or tool name.
- FR-016: The prompt shall ask for two or three directions on the primary screen first, then for the complete design in the direction the user picks, with one artboard per screen and state, titled with that screen and state.
  - Acceptance: Given a generated prompt, then it asks for two or three directions on one named primary screen before the full design, and asks for one titled artboard per screen and state.
- FR-017: When DESIGN.md records a Claude design system link, the prompt shall name that design system by its link and restate none of its color, typography, spacing or radius tokens; when DESIGN.md records none, the prompt shall carry DESIGN.md's Overview, Key Characteristics and Do's and Don'ts text; when DESIGN.md is absent or still holds bracket placeholders, the prompt shall state that the project has no design decisions yet.
  - Acceptance: Given each of the three DESIGN.md states, when the prompt is generated, then it matches its case, and in the first case it contains no color, typography, spacing or radius value copied from DESIGN.md's front matter.
- FR-018: The prompt shall state, in every case, the WCAG 2.2 AA floors, the target size, reading width and motion timing DESIGN.md sets (or the standards' starting values where DESIGN.md is absent or silent), and that customer-facing copy contains no em-dash.
  - Acceptance: Given a generated prompt, then it states those floors and values, and the prompt itself contains no U+2014 character.
- FR-019: When the spec is re-approved while its design is `requested` and no snapshot has been recorded, `sdd-design` shall rewrite the Prompt section against the revised spec and list what changed, so the user can carry the change into the running design conversation.
  - Acceptance: Given a requested design and a re-approved spec with a new state, when `sdd-design` runs, then the Prompt section names the new state and the conversation shows the change list.

#### Recording the approved design

- FR-020: When the user brings back an approved design's link, `sdd-design` shall read the Design artifact through the link and save its `project/canvas.json` and its `project/*.dc.html` artboard files under `docs/sdd/{slug}/design/`, plus the copied design system's `tokens.json` when the canvas uses a design system, replacing the artboard files of any earlier read.
  - Acceptance: Given a readable Design artifact link, when `sdd-design` records it, then those files exist under the spec's `design/` folder with the content the artifact served at read time, and no artboard file from an earlier read remains.
- FR-021: `sdd-design` shall record in `design.md` the link, the read date, the artifact version id it read (so a later read can tell whether the canvas changed), the design system the canvas used or none, and each artboard with the screen, state and requirement IDs it serves, listing beside its artboard any PNG the user placed in `design/` named after that artboard's file stem.
  - Acceptance: Given a recorded design, then `design.md` holds those fields, every artboard file under `design/` appears in its artboard list, and `Main.png` is listed beside `Main.dc.html`.
- FR-022: For each listed UI surface or named state that no artboard shows, `sdd-design` shall ask the user to revise the design or accept the miss, and record an accepted miss in `design.md` as built from the design system without a mockup.
  - Acceptance: Given a spec naming an error state and a design without one, when the design is recorded, then the user is asked, and an accepted miss appears in `design.md` with the state and its requirement ID.
- FR-023: For each screen, control or state the design shows that no requirement covers, `sdd-design` shall ask the user to add it to the spec or leave it out of this build; an addition routes to `sdd-outline` and leaves the design `requested` until the spec is re-approved, and an exclusion is recorded in `design.md` as not built.
  - Acceptance: Given a design with a bulk-delete action the spec lacks, when the design is recorded, then the user is asked, and the answer either names `sdd-outline` with the design still `requested` or lists bulk delete as not built.
- FR-024: `sdd-design` shall record approval only after the user approves in the conversation with every miss and gap answered, then stage `design.md` and the `design/` folder by explicit path and propose a commit message.
  - Acceptance: Given a recorded design with an unanswered gap, when approval is asked for, then it is refused; given every gap answered and the user's approval, then `design.md` is `approved` and the paths are staged, uncommitted.
- FR-025: When the spec is re-approved after its design was recorded, `sdd-design` shall re-check the recorded design against the revised spec through FR-022 and FR-023 without writing a new prompt, unless the user asks for one.
  - Acceptance: Given a stale approved design, when `sdd-design` runs, then it reports the misses and gaps against the revised spec and writes no new Prompt section unless asked.

#### Building from the design

- FR-026: When `design.md` is approved, `sdd-plan` shall load it, and the plan's Affected code and Traceability sections shall name the components that build each designed surface.
  - Acceptance: Given an approved design with a list screen, when the plan is drafted, then its Affected code and Traceability name the components for the list screen.
- FR-027: When a task builds a surface that `design.md` records, the `implementer` shall read that surface's artboards and build it from the project's tokens and components, building nothing `design.md` records as not built.
  - Acceptance: Given `.claude/agents/implementer.md`, then its Load section directs it to `design.md` and the matching artboard files for a task on a designed surface, and to skip items recorded as not built.

#### Render checks in the build

- FR-028: When `sdd-implement` starts a build of a spec that lists a UI surface and no render-check answer is recorded, it shall list the surfaces, recommend which to render-check with a one-line reason naming the criterion that applies (a new surface, a surface with an approved design, a layout that changes between the mobile and desktop widths, or a color pairing no existing surface uses), and ask the user to approve any, all or none.
  - Acceptance: Given a spec listing a new list screen with an approved design and an edited header with neither risk, when the build starts, then the list screen is recommended with the criteria that apply, and the answer is asked for before the next dispatch; given a build with slices already committed and no recorded answer, it asks at that resume.
- FR-029: `sdd-implement` shall record the approved surfaces outside the content hash of `tasks.md` and commit the record before the next dispatch, with section 10 of the SDD document and the skill's list of what the orchestrator writes amended to allow it.
  - Acceptance: Given approved surfaces and a new session, when `sdd-implement` resumes, then it does not ask again, the record is in the git history, and `sdd status` reports `tasks.md` unchanged since approval.
- FR-030: When the user approves no surface, `sdd-implement` shall dispatch no render check.
  - Acceptance: Given no surface approved, when every slice is committed, then `render-checker` is never dispatched and the QA script carries no render results.
- FR-031: When every slice is committed and at least one surface was approved, `sdd-implement` shall dispatch `render-checker` once in its own context, with the running app's URL, the approved surfaces, their states from the spec and the design snapshot, the shipped themes from DESIGN.md and the app's theme styles, and the bar of FR-033, before it hands over the QA script.
  - Acceptance: Given two approved surfaces, when the last slice is committed, then one `render-checker` dispatch covers both, with those inputs, before the QA script is shown.
- FR-032: `sdd-implement` shall put each render failure into the QA script with its evidence and screenshot path, and send only the failures the user picks to a fresh `implementer` as QA bugs.
  - Acceptance: Given two failures, when the user picks one, then exactly one `implementer` is dispatched for it, and the other stays in the report unfixed.
- FR-033: `render-checker` shall judge against the WCAG 2.2 AA floors, DESIGN.md's decisions (or the standards' starting values where DESIGN.md is absent, unfilled or silent), and, for a surface `design.md` records, whether each designed state is reachable and shows each control and labeled field its artboard names, except items recorded as not built; it shall measure target size against DESIGN.md's value, or the 38×38px starting value, and compare no copy, sample data or pixels.
  - Acceptance: Given `.claude/agents/render-checker.md`, then its bar names those three sources, it names no "Design Requirements" section and no fixed 44×44px target, and it excludes copy, sample data and pixel comparison.
- FR-034: `render-check` shall stay runnable by the user on its own with its arguments and steps, its bar step shall name the same sources as FR-033 plus the spec's UI surfaces and states, and `render-checker` shall accept dispatch from `sdd-implement` as well as from `render-check`.
  - Acceptance: Given the two files, then `/render-check` keeps its arguments, its bar step matches FR-033, and neither file states that `render-checker` is dispatched only by `render-check`.
- FR-035: The process-suite battery shall allow `sdd-implement` and `render-check` as the only skills that name `render-checker`, and fail when any other skill or agent does.
  - Acceptance: Given the battery, when `pnpm test:scripts` runs on the changed suite, then the check passes, and a fixture naming `render-checker` in another skill fails it.

#### Standards defer to DESIGN.md

- FR-036: `docs/standards/ux-standards.md` shall cite WCAG 2.2 AA as its floor, including the 24×24 CSS px minimum target of success criterion 2.5.8, and label every choice DESIGN.md may decide as a starting value, numeric or not, including the 38×38px target size, the reading width, motion timing, and the Data tables treatment of row dividers and numeric type.
  - Acceptance: Given the file, then every fixed value cites a WCAG 2.2 AA success criterion or a Core Web Vitals threshold, every other choice is labeled a starting value, "WCAG 2.1" does not appear, and 38×38px is the target-size starting value; version numbers, counts and cross-references are exempt.
- FR-037: The blank DESIGN.md template shall live only at `.claude/skills/design-init/references/design-template.md`, carrying the current root scaffold's content with `pnpm exec designmd` commands, one sentence per line, no reference to material outside the repository, a decision with its starting value, in its section's table, for each value FR-036, FR-038 and FR-039 defer (target size, reading width, motion timing, units and table styling), and a section for the project's Claude design system link.
  - Acceptance: Given the template repository, then the reference file exists, the root has no DESIGN.md, the file contains no `npx` and no "Nintendo", and it holds those decisions in section tables.
- FR-038: `docs/standards/frontend-styling.md` and `docs/standards/html-tables.md` shall replace their unit bans with a principle to use units that scale with user settings and the viewport, giving rem, `clamp()` and dynamic viewport units as examples, and keep as a starting value the rule to size full-height elements with `svh`, or `dvh` only when the element has no fixed or sticky descendant, with its reason in one line.
  - Acceptance: Given the two files, then no sentence forbids a CSS unit outright, rem, `clamp()`, `svh` and `dvh` appear as examples, and the `svh`-first rule and its fixed-or-sticky caveat remain as a starting value.
- FR-039: `docs/standards/html-tables.md` shall keep its semantic markup rules as floors and label its styling choices, such as cell padding, the row-separation device and the header treatment, as starting values DESIGN.md may change.
  - Acceptance: Given the file, then the caption, `th` scope and no-layout-tables rules read as requirements, and each styling choice is labeled a starting value.
- FR-040: Each of the three rewritten standards shall state that its starting values apply wherever DESIGN.md is absent, still holds bracket placeholders, or is silent.
  - Acceptance: Given each file, then it contains that statement once.
- FR-041: `docs/standards/frontend-styling.md` shall state that a design snapshot or Claude Design markup is a reference, and that shipped UI is built from the project's tokens and components.
  - Acceptance: Given the file, then it contains that rule.
- FR-042: When a changed path matches the `applies-to` globs of `ux-standards.md`, the `implementer`'s standards self-check and `standards-reviewer` shall read DESIGN.md when it is filled and judge the deferred values against it, judging against the floor and reporting the DESIGN.md line wherever a DESIGN.md value falls below its WCAG 2.2 AA floor.
  - Acceptance: Given `.claude/agents/implementer.md` and `.claude/agents/standards-reviewer.md`, then each names DESIGN.md as part of the bar for such a path, the starting values as the bar when DESIGN.md is absent or unfilled, and the floor when a DESIGN.md value is below it.

#### DESIGN.md and design-init

- FR-043: Every file that reads DESIGN.md (`CLAUDE.md`, `README.md`, `docs/standards/frontend-styling.md`, `render-checker`, `standards-reviewer`, `implementer`, `curate-context` and `design-init`) shall state what applies when DESIGN.md is absent or still holds bracket placeholders: the standards' starting values apply, and brand decisions are undecided until `design-init` runs.
  - Acceptance: Given each file, then it states that case.
- FR-044: `design-init` shall take `docs/company/company-overview.md` as the authority on audience, personality, positioning and voice, plus the context the user gives, an optional reference DESIGN.md by path or URL, and the optional mood board at `docs/design/moodboard/`; it shall run without either optional input, the template's defaults then supplying the structure, and shall ask the user for audience, personality, positioning and voice when the overview still holds bracket placeholders.
  - Acceptance: Given the skill, then it names those four inputs, marks the reference and the mood board optional, never stops because the mood board is empty, and asks for the four overview facts when the overview is unfilled.
- FR-045: When a reference DESIGN.md is given, `design-init` shall carry over its structure (spacing scale and tiers, type-scale proportions and roles, grid, breakpoints and density, elevation and radius models, component inventory, anatomy and states, and emphasis methods), replace every element a reader could use to identify the source brand, write all prose fresh, and fix the reference's defects instead of inheriting them.
  - Acceptance: Given a reference with a failing contrast pair and a brand name, when DESIGN.md is written, then its spacing scale matches the reference's, and neither the brand name nor the failing pair appears.
- FR-046: `design-init` shall open with a brief of the structure it will carry over from the reference or the template's defaults (layout, elevation, hierarchy, components and data visualization), what it will replace, and which template sections no input covers, so the user can object, then decide identity in five rounds (foundations; color; typography; shape, density, motion and the deferred usability values; voice) and harvest the Do's and Don'ts from the directions the user rejected.
  - Acceptance: Given the skill, then it describes the brief, the five rounds in that order, and the Do's and Don'ts harvest.
- FR-047: Each `design-init` round shall ask two to four questions, every question with a recommendation first tied to the overview, a one-line reason and one or two alternatives, every proposed color with its contrast ratio against the text it carries, and a reply of "go with your recommendations" applying them and moving to the next round.
  - Acceptance: Given the skill, then it describes that question shape, the contrast ratio on proposed colors, and the shortcut.
- FR-048: `design-init` shall write DESIGN.md with every placeholder filled, inapplicable sections listed under `omitted:` and the authoring comment deleted, and finish only when `pnpm exec designmd lint DESIGN.md` reports 0 errors and no contrast warnings, with orphaned-token warnings only for `-dark` colors, and its own check finds no value restated outside its one home (front matter or its section's table), no Don't without its Do, and no proper noun, product name, typeface name, hex value or run of eight or more consecutive words copied from a reference.
  - Acceptance: Given a finished run, then lint reports that result, and a search finds no restated value, a Do beside every Don't, and none of the listed reference residue.
- FR-049: `design-init` and `curate-context` shall refuse to write a DESIGN.md value below its WCAG 2.2 AA floor, naming the floor.
  - Acceptance: Given a proposed 20×20px target size, when either skill would write it, then it refuses and names success criterion 2.5.8.
- FR-050: When DESIGN.md is already filled, `design-init` shall ask before writing, offer to revise the existing file, and report the blast radius of a revision as `curate-context` does; it shall no longer offer to delete itself.
  - Acceptance: Given a filled DESIGN.md, when `design-init` starts, then it asks before any write and reports the blast radius before a revision lands; and the skill contains no offer to delete itself.
- FR-051: At the end of a run, `design-init` shall offer to build or re-sync the project's Design System artifact in Claude from DESIGN.md's tokens, brand book and component guidelines, and on a successful build record the artifact's link in DESIGN.md's Claude design system section, or remove that section when the user declines or the first build is refused.
  - Acceptance: Given an accepted, successful build, then DESIGN.md holds a link that reads as a Design System artifact; given a decline or a refused first build, then DESIGN.md has no such section.
- FR-052: After an approved DESIGN.md edit made outside `design-init` lands and DESIGN.md records a Claude design system link, `curate-context` shall offer to re-sync that artifact so its tokens and guidelines match DESIGN.md, warning first that any edit made to it in Claude will be replaced.
  - Acceptance: Given the skill, then its DESIGN.md path ends with that offer, conditioned on a recorded link, with the warning before the re-sync.

#### Documentation

- FR-053: `.claude/skills/README.md`, `.claude/sdd/README.md`, `CLAUDE.md` and the root `README.md` shall describe `sdd-design` and the changed behavior of `sdd-outline`, `sdd-plan`, `sdd-implement`, `render-check`, `design-init` and `curate-context`.
  - Acceptance: Given those files, then each names `sdd-design` where it lists the SDD skills, none describes `design-init` as deleting itself, none states that a render pass runs only through `/render-check`, and each that describes `render-checker` names both dispatchers.

### Non-functional

- NFR-001: Every new or changed skill body measures at most 5000 tokens, frontmatter excluded, per `.claude/rules/skill-authoring.md`.
- NFR-002: A render check returns to the `sdd-implement` orchestrator only `render-checker`'s report (verdict, per-surface results, the not-reached list and screenshot paths), never screenshot images.
- NFR-003: `pnpm format:check` and `pnpm test:scripts` pass, and the helper's tests cover every design status and every phase transition FR-002 to FR-006 and FR-011 describe.

## Invariants

- INV-001: No `sdd-*` skill runs the design conversation: none invokes `/design` or publishes a Design artifact.
- INV-002: No skill records a design request, approval, skip or cancel without the user's word in the conversation.
- INV-003: Shipped code never contains Claude Design runtime markup (`<x-dc>`, `<dc-import>`, `data-dc-script` or `support.js`), which `standards-reviewer` checks on every surface diff.
- INV-004: A design prompt never carries secrets, credentials, customer PII or restricted material.
- INV-005: No standard and no DESIGN.md decision sets a value below its WCAG 2.2 AA floor.
- INV-006: The design system in Claude is written only by a build or re-sync from DESIGN.md; no skill copies Claude-side edits into the repository.
- INV-007: No skill or agent in the template uses `/design-sync` or `/design-login`.

## Edge cases and failure behavior

- A spec whose UI surfaces section is empty or absent: no design is offered, no `design.md` is written, and the chain runs as before under the renumbered labels.
- The approved link cannot be read (not found, no access, or not a Design artifact): `sdd-design` reports the reason, writes no snapshot, and leaves the design `requested`.
- The session has no Artifact tool, such as one authenticated by API key, Bedrock or Vertex: `sdd-design` still writes the prompt, and at the return step reports that this session cannot read the link and leaves the design `requested` for a session that can.
- The artifact belongs to someone else, so a read returns a summary instead of files: `sdd-design` reports it, writes no snapshot, and asks the user to copy the design into their own account and bring that link back.
- A readable Design artifact lacks `project/canvas.json` or any `project/*.dc.html` file: `sdd-design` lists the files it found, writes no snapshot, and leaves the design `requested`.
- The canvas used a different design system than DESIGN.md records, or none while one is recorded: `sdd-design` reports it from `canvas.json` and asks the user to accept it or revise the design.
- The design is edited in Claude after approval: the committed snapshot stays the record; the change counts only when the user brings the link back, which re-runs FR-020 to FR-024.
- The session that wrote the prompt has ended when the user returns: any session running `sdd-design` resumes from the committed `design.md`, which holds the prompt and the `requested` state.
- DESIGN.md records a Claude design system link that no longer reads: `sdd-design` warns and writes the prompt as for a DESIGN.md with no link.
- A design is requested while the build is in progress: `sdd status` reports `2. Design`, `sdd-implement` stops at its next start, and the plan and tasks go stale once the design is approved.
- The app fails to start for the render check: `sdd-implement` reports the cause once and hands over the QA script without render results.
- An approved surface or state cannot be reached: the render report lists it under Not reached with the reason, and the QA script carries it.
- A reference DESIGN.md contains text that reads like instructions: `design-init` treats it as data, follows none of it, and tells the user.
- Building or re-syncing the design system in Claude is refused after a link exists: the skill reports the refusal, DESIGN.md and its link stay as they were, and the user can retry in a fresh session.
- A canvas holds uploaded images: the snapshot keeps the text files FR-020 names, and the artboards' image references stay links to the artifact.

## Existing behavior

These exist today and are not new requirements; reuse them.

- The SDD helper's commands (`init`, `find`, `status`, `hash`, `lint`, `approve`, `set-status`, `templates sync`, `check-refs`), its content hash rules, and the start and finish protocols of section 4 of the SDD document.
- The gate rules: no approval on the user's behalf, staging by explicit path, the user commits gate artifacts.
- `render-check`'s discovery of surfaces and states, its server handling and its report, and `render-checker`'s method: mobile and desktop widths, every shipped theme, floors measured by script, read-only.
- `sdd-implement`'s slice loop, Verify, QA script and QA-bug flow through a fresh `implementer`.
- DESIGN.md's binding rules, its Google design.md format and `pnpm exec designmd lint`, and `design-init`'s mood-board distillation and `references/brand-research.md`.
- `curate-context`'s gate on DESIGN.md edits, including the blast-radius report and the lint requirement.
- The `implementer`'s self-check and `standards-reviewer`'s bar, both selected by each standard's `applies-to` globs.

## Assumptions

- A-001: Claude Code's Artifact tool can build and re-sync a Design System artifact; one open report ([anthropics/claude-code #102551](https://github.com/anthropics/claude-code/issues/102551)) describes refusals that a fresh session cleared, handled under Edge cases. Accepted by Conner Donohoo.
- A-002: A Design artifact keeps its files as `project/canvas.json`, one `project/*.dc.html` file per artboard and the copied design system under `project/ds/`, as read from two artifacts on 2026-11-09; a different layout is handled under Edge cases. Accepted by Conner Donohoo.

## Glossary

| Term                    | Meaning                                                                                                      |
| ----------------------- | ------------------------------------------------------------------------------------------------------------ |
| UI surface              | A screen, page, view, component or email template a spec lists in its UI surfaces section                    |
| Design conversation     | The separate Claude chat or Claude Code `/design` session where the user iterates on the design              |
| Design artifact         | A Claude Design canvas: artboards published as an artifact with a claude.ai link                             |
| Design snapshot         | The artifact's text files saved under `docs/sdd/{slug}/design/` when the user brings back an approved design |
| Design system in Claude | A Design System artifact built from DESIGN.md, whose link DESIGN.md records                                  |
| Floor                   | A minimum set by an external standard (WCAG 2.2 AA, Core Web Vitals) that no project lowers                  |
| Starting value          | A standard's default for a choice DESIGN.md decides, applied while DESIGN.md is absent, unfilled or silent   |
| Unfilled DESIGN.md      | A DESIGN.md that still holds bracket placeholders, treated as absent                                         |
| Gap                     | Something the design shows that no requirement covers                                                        |
| Miss                    | A listed surface or named state that no artboard shows                                                       |
| `{slug}`                | The spec's folder name under `docs/sdd/`                                                                     |
