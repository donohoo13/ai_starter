# Gut-check prompts: Claude design integration

Run each prompt in a fresh Claude Code session in a repository built from this template, signed in to claude.ai so the Artifact tool is present, with no memory of the session that wrote these skills.
Each prompt states the behavior that passes; anything else is a fail worth a note in Results at the end.

Fixtures the prompts assume:

- A spec folder `docs/sdd/team-invites/` with an approved `spec.md` whose `## UI surfaces` lists `UI-001: Invite list screen (new)` and `UI-002: App header (edited)`, and whose FR-002 names the invite list's empty state.
- A Design artifact in your own claude.ai account showing the invite list, and one owned by someone else.
- A fixture `docs/company/company-overview.md` filled for a fictional product, and a reference DESIGN.md from another brand that includes one failing contrast pair.

## sdd-design (new)

### Task prompts

1. Setup: the team-invites spec approved, no `design.md`.
   Prompt: "spec for team-invites is approved, I want mockups before we plan it"
   - Passes when: the session offers a design for UI-001 and UI-002 or a skip; on "design it", writes the prompt into `design.md`'s Prompt section, shows the identical text as one copyable block, sets `requested` through the helper, stages `design.md` by explicit path, proposes a commit message and does not commit; the prompt names the empty state with FR-002, asks for two or three directions on one primary screen first, contains no repository path, shell command, SDD tool name or em-dash, and never runs `/design` or publishes an artifact.
2. Setup: the design `requested` and committed; your own Design artifact link at hand.
   Prompt: "design's done, here it is: `<your artifact link>`"
   - Passes when: the session reads the link, saves `canvas.json` and each `*.dc.html` under `docs/sdd/team-invites/design/`, records link, read date, version and design system in `design.md`, lists each artboard with its UI ID and state, asks you about every listed surface or state no artboard shows and every screen or control no requirement covers, and approves only after you answer each and say approve.
3. Setup: the same requested design; the link is the artifact someone else owns.
   Prompt: "here's the design link from my teammate: `<their artifact link>`"
   - Passes when: the session reports the read returned a summary rather than files, writes no snapshot, leaves the design `requested`, and asks you to copy the design into your own account and bring that link back.

### Should trigger

- "get me mockups for team-invites before we write the plan"
- "here's the claude design link, it's approved"
- "skip the design step for team-invites, the header change is trivial"
- "sdd status says sdd-design, carry on" (competes with `sdd-plan`; `sdd-design` wins because the phase is `2. Design`)

### Should not trigger

- "design the database schema for team invites" (no UI design; the plan's job)
- "build the invite list screen" (`sdd-implement` or `tdd`)
- "update our brand colors in DESIGN.md" (`curate-context`)
- "/design a landing page for the launch" (the user's own design conversation, no spec)

## sdd-outline

### Task prompts

1. Setup: no spec yet.
   Prompt: "spec out team invites: admins invite people by email and see pending invites in a list, plus a badge in the header"
   - Passes when: the drafted spec has a `## UI surfaces` section listing the invite list as new and the header as edited with `UI-` IDs, and at the finish the session names both surfaces and offers `sdd-design` with `sdd-plan` as the alternative; a skip is recorded only on your word, with your name, the date and both surfaces.
2. Setup: no spec yet.
   Prompt: "spec out a nightly job that prunes expired invite tokens"
   - Passes when: the spec lists no UI surface, the finish names only `sdd-plan`, and no `design.md` is written.

### Should trigger, should not trigger

The description did not change, so its triggering needs no new check.

## sdd-plan

### Task prompts

1. Setup: the team-invites spec approved, no `design.md`.
   Prompt: "plan team-invites"
   - Passes when: before planning, the session asks whether to run `sdd-design` or skip it; on skip it records `design.md` as `skipped` with your name, the date and the covered surfaces, then plans.
2. Setup: the design `requested`.
   Prompt: "write the plan for team-invites"
   - Passes when: the session refuses, writes nothing, and names `sdd-design`.
3. Setup: the design approved.
   Prompt: "plan it"
   - Passes when: the plan's Affected code and Traceability name the components that build UI-001 by its UI ID, `based_on` is the design's `approved_hash`, and nothing listed under Not built is planned.

### Should trigger

- "plan this spec"
- "team-invites spec and design are approved, how do we build it?"
- "sdd plan"

### Should not trigger

- "break the plan into tasks" (`sdd-task`)
- "write a spec for team invites" (`sdd-outline`)
- "get mockups for the invite screen" (`sdd-design`)

## sdd-task

### Task prompts

1. Setup: the plan approved.
   Prompt: "break the team-invites plan down into tasks"
   - Passes when: the session checks the phase is `4. Tasks`, cites the renumbered section 10, and writes `tasks.md` as before.
2. Setup: the design re-approved after the plan was approved.
   Prompt: "write the tasks"
   - Passes when: the session refuses because the plan is stale and names `sdd-plan`.

### Should trigger

- "write the tasks"
- "plan's approved, break it into slices"

### Should not trigger

- "plan team-invites" (`sdd-plan`)
- "start building the tasks" (`sdd-implement`)

## sdd-implement

### Task prompts

1. Setup: approved tasks for team-invites, an approved design for UI-001, no `render_check` key in `tasks.md`.
   Prompt: "tasks are approved, build team-invites"
   - Passes when: before the first dispatch, the session lists UI-001 and UI-002 and recommends UI-001 with the criteria that apply (new, approved design) and UI-002 not, each with a one-line reason, asks for any, all or none, records the answer as `render_check:` in `tasks.md`'s frontmatter, commits it, and `sdd status` still shows `tasks.md` unchanged since approval.
2. Setup: every slice committed, `render_check: UI-001`, the app able to start.
   Prompt: "pick up team-invites where we left off"
   - Passes when: the session dispatches `render-checker` once for UI-001 before the QA script, keeps only its report and screenshot paths in context, and lists each failure in the script with its evidence and screenshot path; a failure you pick goes to one fresh `implementer`, and one you leave stays unfixed in the final report.
3. Setup: as in 2 but `render_check: none`.
   Prompt: "resume implementation"
   - Passes when: no render check runs and the QA script carries no render results.

### Should trigger

- "build the spec for team-invites"
- "resume implementation, we were on P2"
- "sdd implement"

### Should not trigger

- "write the tasks for team-invites" (`sdd-task`)
- "does the invite list look right on mobile?" (no render pass from the model; mention `/render-check`)
- "review this branch before the PR" (`sdd-review`)

## sdd-review

### Task prompts

1. Setup: team-invites built and QA confirmed.
   Prompt: "run the final review on this branch"
   - Passes when: the session checks the phase is `6. Validate`, cites section 13, and runs the reviews as before.
2. Setup: a branch whose `.tsx` diff includes an `<x-dc>` element copied from a mockup.
   Prompt: "review this branch"
   - Passes when: `standards-reviewer`'s findings include the `<x-dc>` element as Claude Design runtime markup in shipped code.

### Should trigger

- "review this branch"
- "final review before I open the PR"

### Should not trigger

- "review the design mockup against the spec" (`sdd-design`)
- "check how the invite list renders" (`/render-check`, user-run)

## render-check (user-only)

### Task prompts

1. Setup: a branch that changed the invite list, with an approved `design.md` for UI-001, app not running.
   Prompt: `/render-check`
   - Passes when: the brief to `render-checker` carries the WCAG 2.2 AA floors, DESIGN.md or the standards' starting values, the spec's UI surfaces and states, and UI-001's artboard files and Not built list; target size is judged against DESIGN.md's value or 38×38px; no copy, sample data or pixel comparison.
2. Prompt: `/render-check invite-list --base main`
   - Passes when: it scopes to the invite list, uses the merge-base with `main`, and reports pass or fail per surface, width and theme without editing any file.

### Should not trigger (the model must never start it)

- "does the invite list look right on mobile?" (the session runs no render pass and mentions `/render-check`)

## design-init

### Task prompts

1. Setup: no DESIGN.md at the root, the fixture overview, the reference DESIGN.md at `tmp/reference-design.md`, an empty `docs/design/moodboard/`.
   Prompt: "set up our design system, use tmp/reference-design.md as the structural reference"
   - Passes when: the session states the mood board is empty and continues, opens with a brief of the structure it carries, what it replaces and which sections no input covers, then runs five rounds in order (foundations; color; typography; shape, density, motion and the deferred usability values; voice), two to four questions each with a recommendation tied to the overview, a one-line reason, one or two alternatives and a contrast ratio on every proposed color; "go with your recommendations" moves to the next round; the written DESIGN.md passes `pnpm exec designmd lint DESIGN.md` with 0 errors and no contrast warnings, keeps the reference's spacing scale, and contains none of its brand names, typefaces, hex values, failing pair or eight-word runs.
2. Setup: as in 1, during round 4.
   Prompt: "make the touch targets 20 by 20, we're desktop only"
   - Passes when: the session refuses, naming 2.5.8 Target Size (Minimum) and its 24×24 CSS px floor, and offers a value that clears it.
3. Setup: a filled DESIGN.md with no Claude Design System section.
   Prompt: "run design-init, I want to redo the color palette"
   - Passes when: the session asks before any write, offers a revision, reports the blast radius and a `designmd diff` before the revision lands, ends by offering to build the Design System in Claude, and on a decline deletes the `## Claude Design System` section; nowhere does it offer to delete itself.

### Should trigger

- "set up the brand for this project"
- "we don't have a DESIGN.md yet, can you make one from our company overview?"
- "derive our design system from this reference DESIGN.md: https://example.com/DESIGN.md"
- "build our design system in Claude from DESIGN.md" (competes with `curate-context`; `design-init` wins because no DESIGN.md edit is on the table)

### Should not trigger

- "change the primary color in DESIGN.md to a darker blue" (`curate-context`)
- "mock up the settings screen" (`sdd-design` or the user's own `/design`)
- "add a dark theme toggle to the header" (a build task)

## curate-context

### Task prompts

1. Setup: a filled DESIGN.md recording a Claude Design System link.
   Prompt: "bump the body text size in DESIGN.md up to 1.0625rem"
   - Passes when: the session reports the blast radius, lands the edit only after your approval and a clean lint, then offers to re-sync the Design System in Claude, warning first that edits made to it in Claude will be replaced, and re-syncs only on your word.
2. Prompt: "set the target size in DESIGN.md to 20×20px"
   - Passes when: the session refuses, naming 2.5.8 Target Size (Minimum).
3. Setup: no DESIGN.md.
   Prompt: "add a rule to DESIGN.md that buttons are pill-shaped"
   - Passes when: the session says DESIGN.md does not exist yet, so the starting values apply and brand decisions are undecided until `design-init` runs, and invents no brand decision.

### Should trigger, should not trigger

The description did not change, so its triggering needs no new check.

## Agents

Agents are not invoked from a prompt; check them through the runs above and by reading one report.

- `standards-reviewer`: on a surface diff with a 36×36px button, judges it against DESIGN.md's 44×44px target when DESIGN.md sets one, and against the 38×38px starting value when DESIGN.md is absent.
- `implementer`: on a task for a designed surface, reads that surface's artboards and builds nothing under Not built.
- `render-checker`: accepts a brief from `sdd-implement` as from `render-check`, and returns the report with screenshot paths, never images.

## Results

Record each run as its section and prompt number, pass or fail, and one line on what happened.

- None yet.
