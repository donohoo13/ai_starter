# Gut-check prompts: implement orchestrator

Run each prompt in a fresh Claude Code session in a repository built from this template, with no memory of the session that wrote these skills.
Each prompt states the behavior that passes; anything else is a fail worth a note.

## sdd-implement (orchestrator)

### Task prompts

1. Setup: a `docs/sdd/invoice-thumbnails/` folder with an approved two-slice `tasks.md`, on its feature branch, clean tree.
   Prompt: "tasks for invoice-thumbnails are approved, go ahead and build it"
   - Passes when: the session dispatches one `implementer` for P1 with only the slug, the slice heading and no extra context; edits no source or test file itself; reruns the Done-when checks and the full suite after the report; ticks P1's close-out and commits P1 without asking; only then dispatches P2.
2. Setup: same spec, P1 committed, and P2's agent reports `BLOCKED` because it needs to add a parameter to the shared `formatCurrency` util the spec never mentions.
   Prompt: "resume implementation on invoice-thumbnails"
   - Passes when: the session resumes at P2 (first unchecked close-out), dispatches `skeptic` with a description of the proposed change and its consumers, then asks you with options and a recommendation quoting the skeptic's verdict; on "yes", resumes the same agent, receives `TRUNK_READY`, runs the full suite, commits the trunk change alone with a body opening `Trunk change:`, and resumes the agent to finish P2.
3. Setup: every close-out checked, `tasks.md` still `in-progress`, the change touches a page the app serves.
   Prompt: "pick up invoice-thumbnails where we left off" then, after the QA script, "the placeholder icon shows on attachments that do exist, fix that"
   - Passes when: the session goes straight to QA (lint, starts or reuses the dev server, hands a QA script mapping each step to a Done-when check or acceptance criterion, waits); sends the bug to a fresh `implementer` red-first; verifies and commits the fix alone; returns to QA; on your confirmation sets `done`, commits it, stops the server it started, reports stops, judgment calls and follow-ups, and recommends `/sdd-review` next in the same session, mentioning a fresh session as an option, without running it.
4. Setup: a finished branch with `review.md` open and two findings.
   Prompt: "fix the first finding, leave the second"
   - Passes when: the session dispatches a fresh `implementer` with the finding verbatim, its `file:line` and the requirement IDs, edits no source or test file itself, verifies with the full suite and a file match against `git status`, proposes a commit message and waits for your word before committing.

### Should trigger

- "build the spec for invoice-thumbnails"
- "ok tasks look good, implement them"
- "resume implementation, I think we were midway through P2"
- "sdd implement"
- "the plan and tasks are approved, can you start coding it up?" (competes with `tdd`; `sdd-implement` wins because an approved `tasks.md` exists)

### Should not trigger

- "write the tasks for invoice-thumbnails" (`sdd-task`)
- "review this branch before I open the PR" (`sdd-review`)
- "fix this off-by-one in the pagination helper, test first" (`tdd` one-shot, no spec)
- "implement a debounce util for the search box" (no spec in flight; `tdd`)

## implementer (agent)

Agents are not invoked from a prompt; check them through the orchestrator runs above and by reading one report.

- Passes when: each report ends with Status, Files changed, Tests, Judgment calls and Notes for later slices; notes are facts only; a slice with only naming or layout choices comes back `DONE` with those listed as judgment calls rather than `BLOCKED`; the agent never commits.

## render-check (user-only)

### Task prompts

1. Setup: a branch that changed `apps/web/src/routes/settings.tsx`, app not running.
   Prompt: `/render-check`
   - Passes when: the session announces "Checking N surfaces since <base>" before launching, starts the dev server, dispatches `render-checker` with the URL, surfaces, states, themes and bar, reports pass or fail per surface, width and theme without editing any file, and stops the server it started.
2. Prompt: `/render-check settings --base feature/settings-shell`
   - Passes when: it scopes to the settings surface, uses the merge-base with `feature/settings-shell`, and reuses a server already running instead of starting a second one.

### Should not trigger (the model must never start it)

- "does the settings page look right on mobile?" (passes when the session does not run a render pass and tells you `/render-check` exists)
- "QA is done, everything looks good" during `sdd-implement` (passes when it finishes without any render pass)
- "review this branch's UI changes" (`sdd-review`; no render pass)
