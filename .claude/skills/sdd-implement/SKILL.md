---
name: sdd-implement
description: Orchestrate the build of an approved tasks.md, one slice at a time, each by a fresh implementer agent. Dispatch the slice with a pointer-only brief, bring the agent's blocking questions to the user, verify its work independently, and commit each verified slice, keeping tasks.md and the spec's journal current so a later session can resume where this one stopped. Use when the user says "implement the tasks", "build the spec", "sdd implement", "resume implementation", or tasks are approved and ready to build. Phase 5 of spec-driven development, section 11 of .claude/sdd/spec-driven-development.md.
argument-hint: "[slug]"
allowed-tools: Bash(.claude/sdd/bin/sdd *)
---

# SDD Implement (phase 5)

This session orchestrates and `implementer` agents build, each slice in a fresh context that never saw the planning conversation, so the build follows the approved artifacts rather than this session's memory of how they came about.
The rules live in section 11 (Implement) of `.claude/sdd/spec-driven-development.md`; this file is only the procedure.
Where the two differ, the document wins.

Arguments: `$ARGUMENTS`, an optional slug.

## What this session writes

Only these, so that every line of code and test comes from an agent whose work this session then checks:

- `tasks.md`'s `status` field and each slice's close-out box.
- `tasks.md`'s `render_check` and `render_check_asked` frontmatter keys, the user's render-check answer and the UI IDs it covers.
- The spec's `branch` and `base` fields.
- Its entries in the spec's journal (The journal, below).
- Git staging and commits.
- The processes it starts and stops.

An `implementer` writes every other file.
That includes code, tests, docs, the task boxes and Evidence lines in `tasks.md`, and its own report in the journal.
When something needs changing, dispatch or resume an agent for it.

Every agent this session dispatches or resumes is waited on, because the next step acts on its report.
When this session works in the spec's worktree without having moved into it, because it has no `EnterWorktree` tool, every brief also names the worktree's path as the directory the agent works in, since an agent starts where the session started.
Never take the next step until the report is in; when it has not arrived, end the turn and resume from the report when it does.

## The journal (section 5 (Working files))

A session can end at any point and the next one has only files to go on, so what this build would otherwise hold in conversation goes into the spec's journal as it happens.
Write to it only through the helper, with the text on stdin; a quoted heredoc keeps backticks and `$` literal:

```
.claude/sdd/bin/sdd journal <slug> add <kind> --ref <slice ID, or QA> <<'EOF'
<text>
EOF
```

Keep every entry abridged: write what a later session needs in order to act, never a transcript of the conversation.

- `question`: every question you stop on for the user in Blocked, Verify and QA, recorded before you ask it, with its options, your recommendation and any `skeptic` verdict.
  A question the files ask again on their own, about the branch, the render checks or uncommitted changes, takes no entry.
- `answer`: what the user decided and the reason they gave, in a line or two rather than their words, recorded before you act on it.
- `decision`: an instruction the user gives for a slice with no question behind it.
- `resolved`: one line naming what a commit settles, recorded in the same command that stages and makes that commit, so no session can end between a journal that calls work settled and the commit that settles it.
  The trunk, slice, QA-fix and finish commits each take one, and each stages the journal when the repository is shared (Spec files and git, below).

Each `implementer` records its own report before sending it.
`status` names the journal file as `journal.path` and reports the last entry as `journal.pending` until a `resolved` entry follows it.
An entry never quotes a secret or a credential; describe it instead.

## Spec files and git (section 5 (Working files))

`status` reports `folder`, the spec folder's absolute path, and `mode`.
`tasks.md`, `spec.md`, `design.md` and the journal are read and written under `folder`, never at a path built by hand: in a private repository every worktree shares the main checkout's folder, so it can sit outside this checkout.
In a shared repository the folder is the checkout's own, so run `status` again after moving into a worktree and take `folder` from that run.

When `mode` is `shared`, the spec files are tracked, and the steps below stage and commit them by explicit path.
When it is `private`, git ignores the spec folder so that it stays out of the repository: stage nothing under it, never force a file in with `git add -f`, and take each step that names a spec file this way:

- A commit that would hold only spec files is not made.
  Steps 2 and 3 and Finish still write the file, and stop there.
- A commit that holds code is made without the spec files.
  The trunk, slice and QA-fix commits stage the reported code paths alone, and still record `resolved` in the same command.
- `tasks.md` has no committed copy, so Verify compares it with a copy saved before the dispatch instead of with `HEAD`.

## Preconditions

- `.claude/sdd/bin/sdd status <slug> --json` reports `phase` `5. Implement`: tasks approved or in progress, unchanged since approval and not stale.
- Anything else: stop, tell the user the phase and the skill `status` names, and do no other phase's work.
  A design requested mid-build reports `2. Design`: stop and name `sdd-design`, since the plan and tasks go stale once that design is approved.

## Start (section 4 (The workflow), start protocol)

1. Read sections 1–5 of the document once per session, then section 11 (Implement).
2. Resolve the slug: the argument, else `.claude/sdd/bin/sdd find`, else list the folders it prints and ask.
3. Run `.claude/sdd/bin/sdd status <slug> --json` and check the preconditions.
   When it refuses because the spec is in another worktree, or on a branch no worktree has checked out, this session started outside the spec's worktree: move into it as Steps, step 1 does, making it first with the `.claude/sdd/bin/sdd worktree <branch>` the refusal names when it names one, and run `status` again there.
4. Load the project context (section 6 (Project principles and context)), the full-suite commands `CLAUDE.md` names or the `tdd` discovery in `.claude/skills/tdd/references/discover.md` finds, and `tasks.md`.
   Load no more of the spec and plan than a question in front of you needs; the agents load their own.
5. **Find the resume point.**
   The next slice is the first whose close-out box is unchecked, and only slices with an unchecked close-out are built, since a task list revised after a late change reopens the slices it touched and leaves the rest closed.
   When every close-out box is checked and `tasks.md` is still `in-progress`, the build is done and QA has not been confirmed: settle render checks (Steps, step 3) when no answer is recorded, then go to QA.
6. **Uncommitted changes** found now are listed for the user with two options: hand them to a fresh `implementer` to continue the resume slice, or set them aside by hand before you go on.
   Leave out of the list `tasks.md`, the journal, and the files named by a `report` entry that no `resolved` entry follows, since the journal already says whose work those are.
   Never stash, reset or discard them yourself, since they may hold work nobody else has.
7. **Continue from a pending entry.**
   When `status` reports `journal.pending`, an earlier session ended before that entry was settled.
   Read it with the entries around it, `.claude/sdd/bin/sdd journal <slug> show --ref <its ref>`, and once Steps 1 to 3 are done continue from it, before any new dispatch or QA pass:
   - A `report`: act on it as the step that dispatched its agent acts on a report that has just arrived, Steps, step 4.2 for a slice and QA bug for a QA fix.
     Its agent is gone, so wherever a step resumes the same agent, dispatch a fresh `implementer` instead, with what you would have sent listed as a decision for the slice (Steps, step 4.1); that dispatch counts as the resume, so it spends Verify's one retry.
   - A `question`: put it to the user again as recorded, without a second `skeptic` or `render-checker` dispatch; for a QA script, start the app first (QA, step 2).
   - An `answer` or `decision`: no step finished acting on it, so act on it now: one about a slice goes into the brief of that slice's next `implementer`, an answer together with the question it answers, a QA bug goes to QA bug, and a QA confirmation goes to Finish.

## Steps (section 11 (Implement), Steps)

1. **Check the branch.**
   The spec's `branch` field names the feature branch and its `base` field the branch that one is cut from and merges back into; `status` reports both.
   When it reports no base, record the one git detects before going on, `.claude/sdd/bin/sdd set-base <slug>`, and ask the user for the branch only when that refuses.
   On the spec's branch: continue.
   `sdd-outline` made that branch and its worktree before it wrote the spec (section 5 (Working files), The branch and its worktree), so the build runs where the spec was written and this step creates nothing.
   On the base or another shared branch, take the case that applies:
   - `mode` `private`, and `git worktree list` shows a worktree on the spec's branch: this session started outside it, so move into it and ask nothing.
   - `mode` `private`, and no worktree has the branch: the spec was outlined before its branch existed.
     Propose `.claude/sdd/bin/sdd worktree <branch> --base <base>`, ask, then run it; it checks out the local branch, else the remote's, tracking it, else cuts a new one from the base, and prints the worktree's path.
     When the repository has `scripts/setup/gwt-add.sh`, run `scripts/setup/gwt-add.sh --no-open <branch>` next, which adopts that worktree, copies the local env and settings files into it and installs its dependencies, then move into the worktree.
   - `mode` `shared`: `status` read the spec from this checkout, so its files are here, committed or not, and a worktree cut from the base would hold none of them.
     Propose making the branch in this checkout instead, ask, then run `git switch -c <branch>`, or `git switch <branch>` when it exists; both carry uncommitted files along.
     Then stage each spec file `git status` still lists by explicit path, propose its commit and wait for the user to make it, since gate artifacts are theirs to commit.
     When the base itself holds spec commits its remote lacks, say so: the new branch carries them, and moving the base back is the user's call.

   Moving into a worktree means the `EnterWorktree` tool with its `path` where the session has that tool, and otherwise running every later command with that directory as its working directory and reading and writing files by absolute path under it.
   If the user picks another branch name, set the spec's `branch` field to it (frontmatter sits outside the content hash, so the spec stays approved).
   On a different feature branch: ask whether to switch to the spec's branch or record the current one the same way.
   Before the first dispatch, make sure the checkout can build: a worktree made without the repository's worktree script has no dependencies, so install them with the repo's install command, and ask the user before copying an untracked local file, such as an env file, from the main checkout.

2. **Mark in progress**: `.claude/sdd/bin/sdd set-status <slug> tasks in-progress` (a no-op when already in progress).
   When this or step 1 changed `tasks.md` or `spec.md` in a shared repository, stage those files by explicit path and commit them before the first dispatch, so every later diff holds only an agent's work.
3. **Settle render checks** when the spec's `## UI surfaces` section lists a UI ID that `tasks.md`'s `render_check_asked` frontmatter key does not, whether this is the first start or a resume after slices were committed, since a spec re-approved mid-build can add a surface.
   A render pass costs minutes and many tokens, so the user picks the surfaces worth it.
   List only those surfaces and recommend each one that meets a criterion, with a one-line reason naming the criterion that applies: a new surface, a surface with an approved design in `design.md`, a layout that changes between the mobile and desktop widths, or a color pairing no existing surface uses.
   Ask the user to approve any, all or none, and wait for the answer.
   Record it in `tasks.md`'s frontmatter, writing each key on the first answer and extending it on later ones, since no template or helper writes them.
   `render_check` holds the approved IDs (`render_check: UI-001, UI-003`), or `render_check: none` while no surface is approved; an approved ID replaces a recorded `none`.
   `render_check_asked` holds every ID asked about.
   Frontmatter sits outside the content hash, so the tasks stay approved.
   In a shared repository, stage `<folder>/tasks.md` by explicit path and commit it before the next dispatch; either way the written keys are what a later session reads instead of asking again.
   With `none`, `render-checker` is never dispatched in this build.
4. **For each slice from the resume point**, in order, finish one before dispatching the next:
   1. **Dispatch** a fresh `implementer` through the Agent tool, with `effort: high` unless the user named another level for this run.
      In a private repository, first save a copy of `<folder>/tasks.md` outside the repository, such as in the session's temporary directory, for Verify to compare with.
      The brief carries only the slug, the slice heading, the notes earlier slices reported, any decisions the user made for this slice, and, when the tree holds uncommitted changes beyond `tasks.md` and the journal, their paths as inherited, since an agent that is gone left them; the agent loads its tasks, requirements, plan sections and seams itself, because anything more you add is this session's bias reaching a context built to be free of it.
      A session that did not see them reads the notes in the earlier slices' reports (`.claude/sdd/bin/sdd journal <slug> show report`) and the decisions in this slice's `answer` and `decision` entries (`show --ref <slice ID>`), giving each answer with the question it answers.
   2. **Act on the report's status**: `BLOCKED` goes to Blocked, `TRUNK_READY` to Trunk commit, and `DONE` or `DONE_WITH_CONCERNS` to Verify.
      Carry a `DONE_WITH_CONCERNS` doubt into the final report.
      When `status` does not show that report as `journal.pending`, the agent sent it without recording it, so record it yourself as a `report` before you act.

### Blocked

1. When the condition is an undecided trunk change, first dispatch `skeptic` with the intent (the spec's absolute path and the slice), the agent's description of the proposed change, and the consumers of each touched symbol, and wait for its verdict.
2. Record the question in the journal, then put it to the user with options and a recommendation, quoting the skeptic's verdict and its strongest case against the change when there is one, and wait for the answer.
3. Record the answer in the journal, then resume the same agent with it through `SendMessage`, so it keeps its full context.
   When that agent is no longer reachable, such as after a new session, dispatch a fresh `implementer` with the question and its answer listed as a decision for the slice.
   Act on its next report.

### Trunk commit

On `TRUNK_READY`:

1. Run the full suite, handling failures as in Verify.
2. Check `git branch --show-current` is not the spec's base, then in one command record `resolved` for the trunk change, stage by explicit path only the trunk paths the report names, with the journal in a shared repository, and commit them alone.
   The body opens with `Trunk change: <touch point> (<n> consumers)`, then records the skeptic's verdict and the user's decision, because the pull request's risk section quotes it from there.
3. Resume the same agent through `SendMessage` to finish the slice, telling it the trunk paths are committed so its next report lists only what it changes from here, and act on that report.

### Verify

Check the agent's work yourself before committing, since a report is a claim:

1. Rerun each Done-when check of the slice and compare with its Evidence line.
2. Run the full suite with the repo's test tiers.
3. Compare the report's files with every path `git status --porcelain --untracked-files=all` lists, `tasks.md` and the journal aside, and its test files with the test files among them; both match exactly, and "none" matches none.
   An unreported change would otherwise be left out of the commit.
4. Diff `tasks.md` against `HEAD`, or in a private repository against the copy saved before the dispatch: only this slice's task boxes went from unchecked to checked, each checked task gained exactly one `- Evidence:` line under it, Follow-ups gained only entries, and nothing else changed.
   The slice's own close-out box may already be checked, when an earlier session verified the slice and ended before its commit.
   When a private repository has no saved copy, because the session that dispatched the agent is gone, read the slice instead: every task in it is checked with exactly one `- Evidence:` line, and step 5 covers the rest of the file.
5. Run `.claude/sdd/bin/sdd status <slug> --json` and confirm `tasks.md` is unchanged since approval.

When a full-suite test fails, decide whether the failure is pre-existing:

- A test in a file this slice added or changed is never pre-existing, since the slice owns it.
- Any other failing test runs at `HEAD` in a temporary worktree (`git worktree add --detach <tmp> HEAD`, install dependencies there with the repo's install command, run the test, then `git worktree remove <tmp>`), never by stashing the working tree.
  It is pre-existing only when it fails there for the same reason; record it and let it pass verification.

Any other failure fails verification.

On a failure, resume the same agent once through `SendMessage` with what you found, then verify again.
A second failure stops the run: record the evidence in the journal as a `question`, report it to the user and commit nothing.
When every check passes, go to Slice commit.

### Slice commit

1. Check the slice's close-out box in `tasks.md` before the commit, so a crash can never leave a committed slice that looks unbuilt; in a shared repository the box lands in the slice's own commit.
2. Check `git branch --show-current` is not the spec's base, the `base` that `status` reported in Verify.
3. In one command, record `resolved` for the slice, stage by explicit path the report's files, which Verify matched against `git status`, with `<folder>/tasks.md` and the journal in a shared repository, and commit without asking; never `git add -A` or `git add .`.
   The subject names the slice's behavior in the repo's convention, and the body records the agent's judgment calls, any you made, and any pre-existing failures.
   Never push.
4. Carry the report's notes for later slices into the next brief.

## QA

Green checks prove the code does what the tests say; only the user confirms it does what they meant, so the one human pass comes after every slice is committed and before `tasks.md` reaches `done`.

1. Run `.claude/sdd/bin/sdd lint <slug>` as the exit check.
2. When the change has a runnable surface, something the app serves or the user exercises through it, start the app in this checkout: a `run-*` project skill under `.claude/skills/` when one exists, otherwise the repo's dev command as a background task.
   Read its log for readiness and the real URL, and reuse a server that is already running rather than starting a second one.
   When the app fails to start, tell the user once with the cause and carry on without it.
3. **Render check**, only when `tasks.md`'s `render_check` names surfaces; with `none` this step is skipped and the script carries no render results.
   Dispatch `render-checker` once, for every approved surface together, so the screenshots fill its context instead of this one.
   Its brief carries:
   - The running app's URL; when the app did not start, skip the dispatch and say in the script that the render check could not run, and why.
   - Each approved surface by UI ID and name, with its states from the spec's scenarios and acceptance criteria and, for a surface `design.md` records, from its Artboards lines.
   - The shipped themes, from `DESIGN.md` and the app's theme styles.
   - The bar: the WCAG 2.2 AA floors in `docs/standards/ux-standards.md`; `DESIGN.md`'s decisions, or the standards' starting values where `DESIGN.md` is absent, unfilled or silent; and for each designed surface the absolute path of its artboard files under `<folder>/design/` and `design.md`'s Not built list.
   - The instruction to return only its report, with screenshot paths and never images.

   Wait for the report, and keep the screenshots on disk rather than reading them into this session.

4. Hand over one QA script: exact commands, URLs and actions, each observation mapped to a Done-when check or an acceptance criterion it confirms.
   When there is no runnable surface or the app did not start, the script names the commands to run and the files to read instead.
   Each render failure goes into the script as its own numbered item with the requirement it breaks, its evidence and its screenshot path, and the script asks which failures to fix.
   Each surface or state the render report lists under Not reached goes into the script as its own numbered item with its reason, for the user to check by hand.
   Record the script in the journal as a `question` with ref `QA` before handing it over, so a session resuming here hands over the same script without a second render pass.
5. Stop and wait for the user.

### QA bug

Record the user's reply in the journal as an `answer` with ref `QA` before any dispatch.
A bug the user reports goes to a fresh `implementer` with the slug, the bug in the user's words with its reproduction steps, and the requirement IDs it touches, to fix red-first.
A render failure is a QA bug only when the user picks it: each picked failure goes to its own fresh `implementer` with the failure's evidence as the reproduction, and a failure the user does not pick stays in the report unfixed.
Verify its report with the full suite and the test-file check from Verify, then commit the fix alone, with the journal in a shared repository, recording `resolved` in the same command, refusing the spec's base and staging by explicit path, with a subject naming the bug and a body naming the red test and its passing run.
Then return to QA with the script's affected steps.

## Finish

When the user confirms QA:

1. Record the confirmation in the journal as an `answer` with ref `QA`.
   Then in one command record `resolved`, run `.claude/sdd/bin/sdd set-status <slug> tasks done` and, in a shared repository, stage `<folder>/tasks.md` and the journal by explicit path and commit the status change.
2. Stop every process this session started, the server included; leave a server it reused running.
3. Report, in this order: what was built, slice by slice; each stop with how it was resolved; the judgment calls of the agents and of this session, gathered from the journal and the commit bodies; any pre-existing failures; any render failures left unfixed; and the Follow-ups in `tasks.md`.

## Outputs

- Code and tests built by `implementer` agents; one commit per slice plus any trunk and QA-fix commits; `tasks.md` fully checked with status `done`; and the report.

## Exit gate (section 4 (The workflow))

Every task and close-out checked, each slice's full suite green apart from recorded pre-existing failures, QA confirmed by the user, the tree clean, `tasks.md` at `done`.

## Next

Recommend running `/sdd-review` next, in this same session.
Its reviewers each run in a fresh context on a brief of pointers, so this session's context never reaches them, and the user can still choose a fresh session instead.
Start it only when the user asked for an end-to-end run.
