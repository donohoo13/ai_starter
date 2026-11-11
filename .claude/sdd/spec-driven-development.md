---
title: Spec-Driven Development
description: Defines how agents turn a user's intent into a spec, plan, tasks and test-driven code, then validate the result before it ships. The result is fewer wrong guesses, small changes that are easy to review, and code whose tests carry the spec forward.
audience: AI agents
status: active
version: 4
---

# Spec-Driven Development

## How to use this document

You are an AI agent.
This document is the source of truth for spec-driven development (SDD).
Every SDD skill points into it.

- MUST, MUST NOT, SHOULD, SHOULD NOT and MAY carry their RFC 2119 meanings.
- **Precedence:** the repo's own rules (its `CLAUDE.md` and the standards under `docs/standards/`) come first, then this document, then a skill's own wording.
  If you can't tell which rule applies, ask.
- Read sections 1–5 once per session.
  After that, read the section for the phase you are in instead of keeping the whole document in context.
- The canonical copy lives at `.claude/sdd/spec-driven-development.md` in the repository, beside the helper, its tests and the generated templates.

### The skills

| Skill           | Phase                                  | Section | Job                                                                                          |
| --------------- | -------------------------------------- | ------- | -------------------------------------------------------------------------------------------- |
| `sdd-outline`   | 1. Outline                             | 7       | Turn an idea into an approved `spec.md`                                                      |
| `sdd-design`    | 2. Design                              | 8       | Request a UI design for an approved spec and record the one the user approves in `design.md` |
| `sdd-plan`      | 3. Plan                                | 9       | Turn an approved spec, and its approved design if any, into an approved `plan.md`            |
| `sdd-task`      | 4. Tasks                               | 10      | Turn an approved plan into an approved `tasks.md`                                            |
| `sdd-implement` | 5. Implement                           | 11      | Orchestrate the build: one `implementer` agent per slice                                     |
| `tdd`           | Used by phases 5 and 6, and on its own | 12      | Red-green discipline for any change a test can lock down                                     |
| `sdd-review`    | 6. Validate                            | 13      | Prove the branch meets the spec, review it, and prepare the PR                               |

The helper `.claude/sdd/bin/sdd`, run from the root of the checkout the session works in, keeps state and the mechanical checks out of the skills' hands: `init`, `worktree`, `find`, `status`, `hash`, `lint`, `approve`, `set-status`, `journal`, `uncommitted`, `templates sync` and `check-refs`.
It checks structure and state, not quality.
It also decides which folder holds a spec's files and whether git tracks them (section 5), so every skill takes a spec file's path from `sdd status` and none builds one by hand.
It makes each spec's branch and worktree too (section 5), so no skill spells out the git for that.

---

## 1. What spec-driven development is

Spec-driven development makes a written specification the source of truth for a piece of work and treats code as something derived from it.
The user's intent is captured as **what** and **why** before anyone decides **how**.
The spec drives a plan, the plan drives small tasks, each task is built test-first, and the finished branch is validated against the spec.

### Why this matters for agents

- You write plausible code quickly.
  When intent is vague, you fill the gaps with guesses, and a wrong guess looks like working code.
- A spec surfaces ambiguity at the cheapest moment to fix it: before any code exists.
- A spec gives you something to check your work against besides "it looks done."
- A spec is the contract that lets several agents, sessions or people work on the same change without drifting apart.

### Roles

| The user owns                                      | You own                                                     |
| -------------------------------------------------- | ----------------------------------------------------------- |
| Intent: the problem, the goals, what success means | Drafting the spec, plan and tasks from that intent          |
| Priorities and scope decisions                     | Finding ambiguity, gaps and contradictions and raising them |
| Answers to open questions                          | Researching facts the plan depends on                       |
| Approval at each gate                              | Building test-first, verifying and showing evidence         |
| QA at the end of Implement                         | Committing each verified slice during Implement             |
| Gate and review commits, pushes and PRs            | Staging by explicit path and proposing those commits        |
| Accepting the finished work                        | Reviewing the branch and reporting every finding            |

You MUST NOT make the user's decisions for them.
When a decision is theirs, present options with a recommendation and wait.

### Where the spec lives, and for how long

Specs are working documents that travel with the change.
They live in `docs/sdd/<slug>/` inside the project (section 5).
In a shared repository, one where git tracks that folder, they are committed on the feature branch, so the pull request carries them beside the code.
In a private repository git ignores the folder and no spec file is ever staged or committed, so the repository and its history stay as its collaborators know them.
Either way every spec here is **spec-first**: written before code to guide this change, then kept as the record of what was decided and why.

What carries the spec forward after the merge, beyond the folder itself:

- **Tests.**
  Each acceptance criterion becomes a test, so CI keeps enforcing the behavior whether or not anyone rereads the spec.
  This is why implementation is test-driven.
- **The PR description,** drafted from the spec's summary and the review evidence.
- **Commit messages.**
- **Repo docs or decision records,** only when the user asks for a lasting record, following the repo's convention.

You MUST NOT commit a gate artifact or a review fix on the user's behalf.
In a shared repository, stage an artifact by explicit path at the gates section 4 names, propose the message, and let the user commit; in a private one, stage nothing from the spec folder (section 5).
During Implement, the orchestrator commits each verified slice itself (section 11).

### What a spec is not

- **Not a long prompt.**
  A spec has structure, numbered requirements and acceptance criteria.
  A prompt has none of these.
- **Not project context.**
  Project context applies to every task: commands, conventions, architecture and boundaries (section 6).
  A spec applies to one change.
  Reference project context from a spec; don't copy it in.
- **Not pseudo-code.**
  A spec describes behavior a user or system can observe, not classes and functions.
- **Not a transcript.**
  A spec must stand on its own, without the conversation that produced it.

---

## 2. Core principles

1. **Intent before implementation.**
   Capture what and why, get approval, then decide how.
   Keep the functional spec (behavior) separate from the technical plan (implementation).
2. **The spec is authoritative while the work is in flight.**
   When code and spec disagree, you MUST NOT quietly pick one.
   Work out which is wrong.
   If the code is wrong, fix the code.
   If the spec is wrong, route back to `sdd-outline`, get the change approved, then change the code.
3. **Never guess.**
   Wherever intent is missing or ambiguous, write `[NEEDS CLARIFICATION: <specific question>]` instead of inventing a plausible answer.
   No phase after Outline begins while a marker is unresolved.
   The one exception is when the user explicitly accepts an assumption; record it under Assumptions.
4. **Right-size the rigor.**
   Write the smallest spec that removes ambiguity for this change.
   Too little spec pushes the cost into rework.
   Too much creates review overload.
   See section 3.
5. **Every requirement is verifiable.**
   If an outside reviewer could not decide pass or fail from the output alone, rewrite the requirement.
   Each acceptance criterion should become a test.
6. **Small, gated steps.**
   Each phase ends at a gate the user approves.
   Implementation proceeds one small task at a time.
7. **Tests are the lasting spec.**
   Write each test from an acceptance criterion, at the seam the plan names, before the code that makes it pass.
8. **Context is a budget.**
   Your performance degrades as your context fills.
   Load only what the current phase and task need, and start fresh sessions at natural breaks.
9. **Change flows through the spec.**
   New or changed behavior updates the spec first, then the plan and tasks, then the code.
10. **Commits follow approval.**
    The user commits gate artifacts and review fixes: you stage them by explicit path and propose the message.
    During Implement, the orchestrator commits each slice once it has verified it, because the user approved the spec, plan and tasks it builds and QAs the result at the end.
    In a private repository (section 5) no spec file is staged or committed, so a gate records its approval in the artifact alone and only code is committed.
    Nobody but the user pushes.

---

## 3. Sizing: how much process a change needs

Decide this before writing anything.
If you are torn between two rows, choose the lighter one and tell the user.

| Change                                                                                                             | Example                                    | What to write                                                                                                                                    | Skills                                               |
| ------------------------------------------------------------------------------------------------------------------ | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------- |
| **Trivial:** the diff fits in one sentence                                                                         | Typo, rename, log line, patch-version bump | Nothing. Make the change and verify it.                                                                                                          | None, or `tdd` if behavior changes                   |
| **Small and bounded**                                                                                              | Bug fix, a tweak to one endpoint           | Structured intent in the prompt: goal, non-goals, acceptance criteria, how to verify                                                             | `tdd` as a one-shot, then `sdd-review` before the PR |
| **Medium:** several files, unfamiliar code, or an uncertain approach                                               | A new feature inside one service           | `spec.md`, `plan.md` and `tasks.md`, each as short as the change allows                                                                          | The full chain                                       |
| **Large or long-lived:** cross-team interfaces, data migrations, core domain, regulated or security-sensitive work | Replacing a service, changing a public API | The full set, with a staged rollout in the plan                                                                                                  | The full chain                                       |
| **Exploratory:** the answer is unknown                                                                             | Spike, prototype, research                 | An exploration brief: the questions to answer, a time or scope limit, what is off limits, and what the output will be                            | None until findings exist; they feed `sdd-outline`   |
| **Multi-agent handoff**                                                                                            | One agent's output feeds another           | A handoff contract in the plan's Interfaces section: input and output schema, invariants, allowed ambiguity, validation checks, failure behavior | The full chain                                       |

- You MUST NOT inflate a small change into many stories and criteria.
- If a change outgrows its row while you work, stop and tell the user before switching to a heavier process.

---

## 4. The workflow

| Phase                | Skill                        | Starts when                                                                                                                           | Produces                                                      | Exit gate                                                                                                                                       | Next                                                                                            |
| -------------------- | ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------- |
| 1. Outline           | `sdd-outline`                | The user brings an idea, brief, ticket or bug big enough for the chain                                                                | `spec.md`                                                     | Readiness checklist passes, no clarification markers, **user approves**                                                                         | `sdd-design` when the spec lists a UI surface and the user wants a design, otherwise `sdd-plan` |
| 2. Design (optional) | `sdd-design`                 | The spec is approved, lists a UI surface, and the user asks for a design                                                              | `design.md` and the snapshot under `design/`                  | Every miss and gap answered, **user approves**; or the user skips                                                                               | `sdd-plan`                                                                                      |
| 3. Plan              | `sdd-plan`                   | The spec is approved and unchanged since approval, and any design is approved and current or skipped covering every listed UI surface | `plan.md`                                                     | Every requirement traces to the plan and a seam, **user approves**                                                                              | `sdd-task`                                                                                      |
| 4. Tasks             | `sdd-task`                   | The plan is approved and unchanged                                                                                                    | `tasks.md`                                                    | Every requirement has a task, every task has a seam and a check, **user approves**                                                              | `sdd-implement`                                                                                 |
| 5. Implement         | `sdd-implement`, using `tdd` | The tasks are approved and unchanged; on a feature branch                                                                             | Code, tests, one commit per verified slice                    | Every task is checked off, each slice's full suite is green apart from recorded pre-existing failures, the user confirmed QA, the tree is clean | `sdd-review`                                                                                    |
| 6. Validate          | `sdd-review`                 | All tasks are done, on a feature branch with a clean tree                                                                             | `review.md`, the fixes the user picks, a PR description draft | **User accepts**                                                                                                                                | Done                                                                                            |

### State

Each artifact records its state in its frontmatter.

| Artifact    | Statuses                                      | Recorded at approval                                                                                         |
| ----------- | --------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `spec.md`   | `draft` → `approved`                          | `approved_hash`                                                                                              |
| `design.md` | `requested` → `approved`, or `skipped`        | `approved_hash`, `based_on` (the spec's `approved_hash`, also recorded at a request or skip)                 |
| `plan.md`   | `draft` → `approved`                          | `approved_hash`, `based_on` (the design's `approved_hash` when the design is approved, otherwise the spec's) |
| `tasks.md`  | `draft` → `approved` → `in-progress` → `done` | `approved_hash`, `based_on` (the plan's `approved_hash`)                                                     |
| `review.md` | `open` → `accepted`, reopened to `open`       | `based_on` (the tasks' `approved_hash`), recorded at acceptance                                              |

The current phase follows from these states:

| State                                                                                                                  | Phase        | Skill to run    |
| ---------------------------------------------------------------------------------------------------------------------- | ------------ | --------------- |
| No `spec.md`, a draft spec, or open clarification markers                                                              | 1. Outline   | `sdd-outline`   |
| Design requested; an approved design changed or stale; or a skipped design that misses a UI surface the spec now lists | 2. Design    | `sdd-design`    |
| Spec approved, design absent, skipped covering every listed UI surface, or approved and current; plan missing or draft | 3. Plan      | `sdd-plan`      |
| Plan approved; tasks missing or draft                                                                                  | 4. Tasks     | `sdd-task`      |
| Tasks approved or in progress                                                                                          | 5. Implement | `sdd-implement` |
| Tasks done; review missing, open, or accepted but stale                                                                | 6. Validate  | `sdd-review`    |
| Review accepted and current                                                                                            | Done         | None            |

**Changed and stale artifacts.**
An approved artifact whose content no longer matches its `approved_hash` counts as changed, and it needs re-approval.
Every artifact downstream of it becomes **stale** because its `based_on` no longer matches, and the work routes back to the skill that produces the stale artifact.
The plan's upstream is the design while the design is approved and the spec otherwise, so a design approved after the plan, a re-approved design, or a spec change that stales the design all make the plan stale.
The approval hash covers the body below the frontmatter plus the artifact's `based_on`, so a re-approval against a changed upstream always records a new hash and stales what follows.
A design's hash also covers its recorded `version`, so re-recording a changed canvas needs a new approval.
An accepted review records the tasks' `approved_hash` as its `based_on`, so tasks re-approved after a late change make the review stale and the run returns to Validate.
A draft's `based_on` may stay empty until approval records it.
Once set, it must match: refreshing a stale artifact means revising it against its upstream and setting `based_on` to the new hash before re-approval.

**What counts as a change.**
The hash reads what the body says and never how it is laid out, so an approved artifact that a formatter rewrites, in a commit hook or in an editor, stays approved.
Every word, number and punctuation mark counts, in order, along with each heading's level, each list item, each table cell and the code inside a fence.
Line wrapping, indentation, blank lines, table padding and block quote markers do not count, and neither does the character that marks a bullet, emphasis, a rule or a fence, the number on an ordered item, or a backslash escape in prose.
Code inside a fence counts character for character apart from its whitespace, so a formatter that rewrites the code itself, as Prettier does in a language it knows, still makes the artifact changed.
Checking off tasks in `tasks.md`, the `- Evidence:` note under a task, and the Follow-ups section do not count either.

### Every SDD skill starts the same way

1. **Find the spec.**
   Use the slug from the argument.
   Otherwise use the spec whose `branch` matches the current git branch.
   Otherwise list the existing folders and ask.
2. **Read the state** with `sdd status <slug>`.
   It also reports the spec folder's path and the repository's mode, shared or private (section 5).
   Read and write every spec file through that path, since the folder is not always under the current directory, and follow the mode wherever a step stages or commits a spec file.
   A shared repository keeps a spec in its own worktree, so the helper refuses when the session started anywhere else, and names the worktree that holds the spec, or the branch that commits it when no worktree has that branch checked out.
   Move the session into that worktree, making it first with the `sdd worktree <branch>` the refusal names (section 5), then read the state again.
3. **Check this phase's preconditions.**
   If they aren't met, stop.
   Tell the user which phase the work is actually in and which skill to run.
   Don't do another phase's work.
4. **Load only what the phase needs:** this document's section for the phase, the project context, and the upstream artifacts.

### Every SDD skill finishes the same way

1. **Run the exit checks:** `sdd lint <slug>` plus the phase's checklist.
2. **Present** the artifact, a short summary of the decisions it contains, and any open questions.
   Ask for approval.
3. **Record approval only when the user gives it,** with `sdd approve <slug> <artifact>` for the spec, design, plan and tasks, and `sdd set-status <slug> review accepted` for the review.
   Then, in a shared repository, stage that artifact by explicit path (`git add <spec folder>/<artifact>.md`) and propose a commit message in the repo's convention; the user commits.
   The commit belongs on the spec's branch, so when the session works in a worktree, say where it runs (`git -C <worktree> commit`), since the user's own shell may sit in another checkout.
   In a private repository stage nothing and propose no commit: the file records the approval.
4. **Name the next skill,** and the worktree to run it in when the session works in one.
   Recommend a fresh session before `sdd-implement`.
   The files in the spec folder are the handoff.

### Gate rules

- You MUST NOT approve on the user's behalf or run `sdd approve` without explicit approval in the conversation.
- You MUST NOT start the next phase's skill on your own unless the user said to run end to end.
  Even then, stop at any clarification marker, failed check or stop-and-ask condition.
- Running a skill on an artifact that already exists revises or resumes it.
  Start over only if the user asks.

### Going back

- If a later phase finds a gap in an earlier artifact, stop, describe the gap, and route back to the skill that owns that artifact.
  Don't patch around the gap downstream.
- Editing an approved artifact makes it changed.
  Re-approve it, then refresh whatever went stale.
- A finished run goes back the same way, never by editing a status by hand (section 14).
  Re-approving `tasks.md` returns it from `done` to `approved` and the run to Implement, and an accepted review that goes stale returns the run to Validate.
  `sdd set-status <slug> review open` reopens an accepted review, when it went stale or when feedback arrives after acceptance (section 13).

---

## 5. Working files

```
docs/sdd/<slug>/
  spec.md     # Outline
  design.md   # Design: the prompt, the record, or the skip
  design/     # Design: the snapshot of the approved Design artifact
  plan.md     # Plan
  tasks.md    # Tasks; also the progress log during Implement
  journal.md  # Implement: agent reports, questions, answers and decisions
  review.md   # Validate report and PR description draft
```

- **Project root** is the git top-level directory, or the current directory outside git.
- **Spec folder.**
  A spec's working folder is always `docs/sdd/<slug>/` inside the project, but which checkout holds it follows the repository's mode, so it is not always under the current directory.
  `sdd status <slug>` reports its path as `folder` beside the `mode`, and `sdd root` prints the `docs/sdd/` folder that holds every spec.
  Take every spec file's path from there and never build one by hand.
- **Mode.**
  A repository is shared or private, and git decides which; nobody is asked.
  The mode belongs to the repository, never to one branch, because every worktree shares the one exclude file that keeps a private folder out of git.
  It changes only with what git tracks: the helper removes its exclude entry once a file under `docs/sdd/` is tracked and adds it again once none is, and specs written while the repository was private stay in the main checkout's folder.
  A directory outside git counts as private, with the folder under the current directory.
  - **Shared:** some checkout of the repository tracks at least one file under `docs/sdd/`, a spec or an empty `docs/sdd/.gitkeep`.
    The spec folder is the current checkout's own, since tracked files travel with the branch.
    It is committed on the feature branch, so the pull request carries the spec, plan, tasks and review beside the code, and the history shows when each gate passed.
    Stage an artifact by explicit path at the gates section 4 names and let the user commit; never `git add -A`.
  - **Private:** git tracks nothing under `docs/sdd/`.
    The helper makes git ignore the folder through the repository's local exclude file (`.git/info/exclude`), never through `.gitignore`, so nothing in the repository changes and collaborators see nothing.
    Every worktree shares one spec folder, the main checkout's, so a spec is reachable from any worktree and survives removing one.
    You MUST NOT stage or commit anything under it, and MUST NOT force it past the ignore rule with `git add -f`.
    Wherever a step stages or commits a spec file, leave that part out: a gate records its approval in the file alone, a commit that would hold only spec files is not made, and a commit of code is made without them.
- **Slug** is a short kebab-case name for the change.
  It defaults to the current feature branch name.
- **Branch** is the feature branch the change is built on, recorded in the spec's `branch` field, and `sdd find` matches a spec to the checkout whose branch it names.
  Outline makes it, in a worktree of its own, before it writes the spec (The branch and its worktree, below).
- **Base** is the branch the feature branch is cut from and merges back into.
  Git decides it and nobody is asked: `sdd init` records the remote's default branch in the spec's `base` field, read from the `origin/HEAD` this clone records and, when that is missing, from the remote itself.
  Only when both fail does the session ask the user, and `sdd set-base <slug> <branch>` records the answer; that command, or `sdd init --base <name>`, also names the base of work that does not build on the remote's default branch.
  Every skill reads the base from the helper, and none works out a default branch of its own: `sdd status` reports the recorded base, and `sdd base` prints it, detecting it the same way for a spec that records none and when no spec matches the current branch.
  `sdd set-base <slug>` records the detected base on a spec that has none, which `sdd lint` reports as an error.
  The field sits outside the content hash, so recording it never stales an approval.
- **Templates** live in `.claude/sdd/templates/` and are generated from this document's appendices by `sdd templates sync`.
  The appendices are canonical, and `sdd templates sync --check` reports drift.
  Every `<...>` placeholder in a template is filled or deleted before approval; `sdd lint` reports any that remain, in every artifact including `review.md`.
- **Lifetime.**
  The folder stays after the merge as the record of the change; delete it only when the user asks.

### The branch and its worktree

One spec is one feature branch and one worktree, from its first artifact to its merge.
Outline makes both before it writes the spec, every later phase works in that worktree, and Implement builds there.
A shared repository needs this: its spec files are committed, and written on the base they could only be committed there or left uncommitted on one machine, where a worktree made later would not hold them.
On the spec's own branch each gate's commit lands where the pull request carries it, can be pushed, and can be picked up from another clone.
A private repository commits no spec file and takes the same flow, so the skills hold one procedure: the worktree gives the spec a branch `sdd find` matches in every later session, leaves the main checkout on the base, and no later phase has to move.

- **When.**
  Outline that starts on a feature branch of this work's own, in the main checkout or in a worktree, uses that checkout as it is.
  Outline that starts anywhere else, on the base, on another shared branch that other work also merges into, or on a branch that belongs to other work, makes the branch and the worktree and moves into it before `sdd init`.
  In a shared repository `sdd init` refuses on the base.
  Outside git there is no branch, and `sdd init` writes the folder under the current directory.
- **Name.**
  The branch takes the form the repository's context file (`CLAUDE.md` or `AGENTS.md`) states for branches, and is `feature/<slug>` where it states none.
- **Making it.**
  `sdd worktree <branch>` checks the branch out in a worktree of its own and prints the worktree's path, so no skill spells out `git branch` or `git worktree add` for a new spec.
  It never forks a branch that exists: one some worktree already has checked out is reported and nothing is created, a local one gets a worktree, and one only the remote has is fetched and checked out tracking it.
  Otherwise it cuts the branch from the base, from the remote's copy when the remote has the base, since a local copy can lag or hold commits the remote lacks, and the new branch tracks nothing until the user pushes it.
  The base is the remote's default branch, the one `sdd init` then records, or the `--base <name>` both commands take.
- **Where.**
  A repository whose context file says where its worktrees live gets that directory, passed as `--path <dir>`.
  Otherwise the worktree is `.claude/worktrees/<branch>` in the main checkout, with the slashes of the branch name as dashes.
  That folder is inside the project, where an agent's session is already allowed to write, and it is where Claude Code keeps its own worktrees, the one place its `EnterWorktree` tool accepts from a session that is already inside a worktree.
  The helper keeps it out of the main checkout's `git status` through the local exclude file when no ignore rule covers it.
- **Setting it up.**
  A new worktree holds only tracked files.
  When the repository has a script that prepares one, run it once the worktree exists: `scripts/setup/gwt-add.sh --no-open <branch>` adopts the worktree at that path, copies the local env and settings files into it and installs its dependencies.
  Without such a script nothing more is needed until Implement, which installs dependencies before its first dispatch (section 11).
- **Moving in.**
  With Claude Code's `EnterWorktree` tool, pass the worktree's `path`.
  Without it, as under Codex, a session cannot change its own directory: run every later command with the worktree as its working directory, through the shell tool's working-directory setting or `cd <path> &&` at the head of the command, and read and write files by their absolute path under it.
  The helper and git both act on the checkout they run in, so nothing else changes for the session itself.
  An agent it dispatches starts where the session started, so its brief names the worktree as the directory to work in.
  Tell the user the branch and the path, since their own shell and editor stay where they were, and a later phase is simplest started in the worktree.
- **Later sessions** start in the worktree or are moved into it.
  In a shared repository no other checkout holds the spec, so `sdd status` and `sdd find` run anywhere else refuse and say where it is (section 4).
- **Another machine.**
  A spec whose commits were pushed is picked up in a clone that has fetched them: `sdd worktree <branch>` checks the branch out tracking the remote, and the next skill runs there.
- **Afterwards.**
  The worktree and the branch outlive the session, and nothing in the chain removes either.
  After the merge the user removes the worktree, with the repository's own script when it has one (`scripts/setup/gwt-remove.sh <branch>`), otherwise with `git worktree remove <path>` and `git branch -d <branch>`.
  An abandoned spec is cleared the same way (section 14).

### The journal

`journal.md` holds what a phase would otherwise keep only in its conversation: an agent's report, a question put to the user, the user's answer, and a decision later work must follow.
A session can end at any moment, and the next one resumes from files alone.
Implement is the phase that keeps one (section 11).

- **Written only through the helper.**
  `sdd journal <slug> add <kind> [--ref <ref>]` appends one entry, taking its text on stdin or in `--text` and recording the phase and the time itself; `sdd journal <slug> show [<kind>] [--ref <ref>]` prints entries.
  The ref says what an entry is about, such as a slice.
  No entry is edited or removed afterwards.
- **Kinds.**
  A `report` is an agent's report, recorded by the agent before it sends it.
  A `question` is one the session stops on for the user, an `answer` is what the user decided and why, and a `decision` is one the user gives with no question behind it.
  A `resolved` entry says the entries before it are settled.
- **Abridged.**
  An entry holds what a later session needs in order to act, a decision and its reason in a line or two, never a transcript of the conversation.
- **Pending.**
  The last entry is pending until a `resolved` entry follows it or the phase that wrote it ends.
  `sdd status` reports it with what it waits on, the user for a `question` and the session for the rest, so a fresh session reads where the work stopped.
- **Outside every approval.**
  It is a file of its own that no hash covers, so writing to it never makes an artifact changed.
- **Kept with `tasks.md`.**
  Wherever `tasks.md` is staged and committed, the journal goes with it.
- **No secrets.**
  An entry never quotes a secret, a credential or customer data; describe it instead.

---

## 6. Project principles and context

Project principles are the rules that apply to every change in a repo.
In this repository they live in `CLAUDE.md` and the standards under `docs/standards/`, and a project may add skills for its own tooling, such as how to run tests.
Every spec and plan MUST comply with them, and the plan checks against them explicitly.

### What belongs there

- **Commands:** build, test, lint, typecheck and run, written out in full with flags, including test tiers when the repo has them.
- **Stack:** languages, frameworks and their versions.
- **Structure:** where code, tests and docs live.
- **Conventions** that differ from language defaults.
  One real code example beats a paragraph of description.
- **Architectural decisions** and the reasons for them.
- **Boundaries,** in three tiers:
  - **Always:** for example, run the tests before proposing a commit; follow naming conventions.
  - **Ask first:** for example, schema changes, new dependencies, CI configuration changes, public API changes.
  - **Never:** for example, commit secrets; edit vendored or generated code; delete or skip a failing test without approval.
- **Engineering principles** that the plan is checked against, for example:
  - **Test-first.**
    Acceptance criteria become failing tests before implementation begins.
  - **Simplicity.**
    Use the fewest moving parts that meet the requirements, with no speculative features or future-proofing.
  - **No needless abstraction.**
    Use frameworks directly instead of wrapping them without a reason.
  - **Real integrations.**
    At system boundaries, prefer contract tests and real dependencies to mocks.

### What doesn't belong there

Anything you can learn by reading the code, standard language conventions, tutorials, frequently changing information, and file-by-file descriptions of the codebase.

### Rules

- Keep the principles short.
  Each line should prevent a real mistake.
  When rule files grow long, agents skip some rules and over-apply others.
- A rule that must hold every time belongs in an automated check (CI, a hook or a linter), not only in prose.
- When a plan has to deviate from a principle, record the deviation with the reason and the simpler alternative you rejected.
- Apply each rule as written, and don't stretch it to cases it doesn't cover.
  When unsure, ask.

---

## 7. Phase 1: Outline (`sdd-outline`)

**Purpose:** understand the code and the user's intent, then capture what and why in an approved spec.
**Starts when:** the user brings an idea, brief, ticket or bug that section 3 sizes as medium or larger.
**Produces:** `spec.md`, approved.

### Steps

1. **Size the change** (section 3).
   If it's trivial or small, say so and recommend `tdd` instead.
   Continue only if the user wants the chain.
2. **Make the branch, then the working folder.**
   On a feature branch of this work's own, stay; anywhere else, make the spec's branch and its worktree with `sdd worktree <branch>` and move the session into it (section 5).
   Then create the folder there with `sdd init <slug>` if it doesn't exist, which records the branch the checkout is on.
   `init` records the base from git (section 5); ask the user for it only when either command reports that git could not tell, and pass the answer to both as `--base <name>`.
   `init` also prints the repository's mode, and in a private repository makes git ignore the folder before it writes the spec.
3. **Ground yourself in the code.**
   Read the project context (section 6).
   Explore the relevant code without changing anything, and identify existing behavior, the patterns to follow and the interfaces to reuse.
   Establish what happens today and why, including how each system involved behaves, from its code, logs or documentation (the vendor's, for a third-party system).
   Research only what explains the problem; options for changing it are the plan's research (section 9).
   In a large codebase, delegate exploration to subagents and keep only their conclusions.
   Don't move on until you can name the files, interfaces and existing behavior involved.
4. **Play back the problem** in the conversation before asking anything, in plain words: the current state, who is affected, the evidence, and each distinct problem on its own line (for a bug, each cause).
   Mark each problem confirmed or hypothesis, and say where what you found contradicts the brief.
   When a problem's behavior decides which options exist, confirm it before any interview question, from code or documentation where they answer it and otherwise by asking in the playback, because every option built on a wrong cause is wrong.
   When problems differ in actor, fix or owner, say how many problems there are and ask which belong in this spec.
   Each one left out gets a line under Non-goals, the Goals cover only the ones kept, and what remains is sized again (section 3).
   End your turn after the playback, since a question dialog can hide text written earlier in the same turn, and interview only once the user confirms or corrects it.
   A hypothesis still open after that becomes a clarification marker, or an assumption the user accepts.
   Skip this step when resuming a spec whose problem the user already confirmed, or when revising one without changing its problem.
5. **Interview the user** when the brief is thin.
   Ask about the hard parts: edge cases, failure behavior, trade-offs, constraints, who the work is for and what success looks like.
   Don't ask anything the code can tell you.
   Ask in focused batches.
   Write each option as behavior or a hard constraint (see Where a detail belongs, below); anything else is a plan decision.
   When the right answer would differ per problem, ask once per problem and name the problem in the question.
6. **Draft `spec.md`** from the template (Appendix A), following the rules below.
7. **Check it.**
   Run the readiness checklist and `sdd lint <slug> spec`.
   For medium or larger changes, run an adversarial review in a fresh context.
   That review looks for contradictions, ambiguous terms, hidden dependencies, claims that can't be tested, missing failure modes, and criteria that could pass without meeting the intent.
   Turn what it finds into fixes or clarification markers.
8. **Gate.**
   No clarification markers remain, the checklist passes, and the user approves.
   Record the approval, then name the next step.
   When `design.md` exists, offer no skip and name the skill `sdd status` reports: `sdd-design` at `2. Design` for a requested or approved design, which it re-checks against the revised spec, or for a skip that misses a surface the spec now lists.
   When `design.md` is absent and the UI surfaces section lists a surface, name each surface and offer `sdd-design` (section 8), with `sdd-plan` as the alternative; a skip the user chooses is recorded in `design.md` with their name, the date and the surfaces it covers.
   Otherwise name `sdd-plan`, and write no `design.md`.

### Where a detail belongs

A spec describes behavior and outcomes.
It includes implementation detail only when that detail is a hard constraint, such as "must use the existing auth service" or "data must stay in region X." To decide, ask: would the user or a stakeholder care about this detail, or is it a hard constraint?
If so, it goes in the spec.
Otherwise it goes in the plan.

### Sections

| Section                         | When                                 | Contents                                                                                              |
| ------------------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------- |
| Frontmatter                     | Always                               | Title, slug, branch, status, owner, dates, approval hash, description                                 |
| Summary                         | Always                               | One paragraph; see the rules below                                                                    |
| Problem and context             | Always                               | Current state, who is affected, each distinct problem, evidence with sources                          |
| Goals                           | Always                               | Outcomes, measurable where possible                                                                   |
| Non-goals                       | Always                               | What is explicitly out of scope                                                                       |
| User scenarios                  | Medium and larger                    | Prioritized stories, each testable on its own                                                         |
| UI surfaces                     | When the change creates or edits one | Each screen, page, view, component or email template, once, with a permanent ID, marked new or edited |
| Requirements                    | Always                               | Numbered, one behavior each, with acceptance criteria                                                 |
| Non-functional requirements     | When relevant                        | Measurable performance, security, reliability, accessibility and cost targets                         |
| Invariants                      | When relevant                        | Rules that must never break                                                                           |
| Edge cases and failure behavior | Always                               | What happens at the boundaries and when things fail                                                   |
| Existing behavior               | Changes to existing code             | What exists today, clearly labeled as not new                                                         |
| Assumptions                     | When any exist                       | Each assumption and who accepted it                                                                   |
| Open questions                  | Until resolved                       | Clarification markers                                                                                 |
| Glossary                        | When domain terms appear             | Short definitions                                                                                     |
| Changelog                       | After first approval                 | Dated changes and the reason for each                                                                 |

### Frontmatter description

- 1–2 sentences, under about 45 words.
- Sentence 1 opens with a present-tense verb and no subject ("Replaces…", "Adds…", "Moves…").
  It says what changes, from what to what, and the one property of the new approach that matters most.
- Sentence 2 begins "The result is" and lists 2–4 outcomes, user-visible first and operational last.
- Name the system being replaced or changed, so searches for it find the spec.
  Use generic nouns for new parts ("a CDN", not a vendor product), unless the change is about choosing that vendor.
- Leave out the problem statement as its own sentence, numbers, steps, approvals, references to other documents, alternatives and open questions.
- Keep it plain enough for a non-engineer, and don't refer to "this spec" or "this document."

### Summary

- One paragraph, 5–7 sentences, about one sentence each:
  1. **Current state:** what the system does today, in concrete terms.
  2. **Limitation:** the specific constraint that causes the trouble.
  3. **Trigger:** the situation that pushes the system past that limit.
  4. **Impact:** what users or the business experience as a result.
  5. **Change:** what is being built, with technologies named.
  6. **Why it works:** how the change removes the limitation from sentence 2.
  7. **End state:** what the system looks like when the work is done.
- Cover the one core problem and the one core solution.
  Leave out secondary benefits unless they are the reason for the work.
- Leave out metrics, rollout steps, flags, approvals, references to other documents, alternatives, trade-offs, open questions, and any detail more than one level below the main components.
- Describe what and why, not how.
  Use short declarative sentences with one idea each.

### Requirements

- Write one behavior per requirement and number it: `FR-001` for functional, `NFR-001` for non-functional, `INV-001` for invariants.
  IDs are permanent: never renumber, and mark a removed requirement as removed instead of deleting it.
- Use **shall** for mandatory behavior and **should** for preferred behavior.
- Give every requirement acceptance criteria that an outside reviewer can judge.
  Write them so each one can become a test.
- Use concrete examples: input and output pairs, exact formats such as an error response body, and sample data.
- Use measurable terms.
  Write "p95 under 2 s at 100 concurrent requests," not "fast."
- Name every constraint, even ones a domain expert would consider obvious, such as data retention, privacy, permissions and opt-in.
  You will not reliably infer constraints from context.
- State domain relationships and rules explicitly.
- Keep the spec self-contained.
  Never write "as discussed" or "see above."
  Link to a document when you need one.

**EARS patterns** for writing requirements:

| Pattern           | Template                                                          |
| ----------------- | ----------------------------------------------------------------- |
| Ubiquitous        | The `<system>` shall `<response>`.                                |
| Event-driven      | When `<trigger>`, the `<system>` shall `<response>`.              |
| State-driven      | While `<state>`, the `<system>` shall `<response>`.               |
| Unwanted behavior | If `<condition>`, then the `<system>` shall `<response>`.         |
| Optional feature  | Where `<feature is included>`, the `<system>` shall `<response>`. |

**Given/When/Then** for acceptance scenarios:

```
Given a draw with 300 photos
When a reviewer opens the draw PDF
Then every thumbnail renders within 10 seconds
And no thumbnail is blank
```

### User scenarios

- Prioritize stories as P1, P2 and P3.
  Each story becomes a **slice** in the plan and tasks.
- Make each story something that can be built, tested and demonstrated alone.
  P1 by itself should be a viable first release.
- For each story, state how it is tested independently.

### UI surfaces

- List each screen, page, view, component or email template the change creates or edits, once, as `- UI-001: Settings screen (new)` or `- UI-002: Invoice header (edited)`.
  CLI output and API responses are not UI surfaces; leave the section out when the change touches none.
- IDs are permanent, like requirement IDs: never renumber, and a renamed surface keeps its ID.
  `sdd lint` reports a malformed or duplicate ID as an error.
- Later phases read the list from this section: a design is offered for it (section 8), a skip records the IDs it covers, and a re-approved spec with a new ID offers the design again.

### Invariants versus requirements

Invariants are absolute; requirements can be traded off.
A retry count is a requirement and can be loosened if circumstances change.
"Never show a raw exception to a user" is an invariant.
Keep invariants in their own section and write them in absolute language.

### Changes to existing code

- Describe today's behavior in an **Existing behavior** section and label it as existing.
  Agents have misread descriptions of existing code as new requirements and built duplicates.
- Name the existing modules and interfaces to reuse or extend.

### Spec readiness checklist

Run this before asking for approval.
It works like a unit test for the spec.

- [ ] The description and summary follow the rules above.
- [ ] Someone with no prior context could plan from it without asking the author anything.
- [ ] Each requirement is a single, testable behavior with an ID.
- [ ] Each requirement has acceptance criteria that an outside reviewer can judge from the output alone.
- [ ] Non-goals are explicit.
- [ ] Edge cases and failure behavior are covered.
- [ ] Non-functional requirements are measurable.
- [ ] Invariants are separate from requirements.
- [ ] Implementation details appear only where they are constraints.
- [ ] Existing behavior is labeled separately.
- [ ] Assumptions are stated, and no clarification markers remain.
- [ ] No vague word appears without a measure: _fast, simple, robust, scalable, intuitive, user-friendly, appropriate, reasonable_.
- [ ] Nothing refers to a conversation the reader can't see.
- [ ] The amount of spec matches the size of the change (section 3).

---

## 8. Phase 2: Design (`sdd-design`)

**Purpose:** get a UI design for the approved spec from Claude Design, check it against the spec, and record the version the user approves, before any plan commits to components, files and states.
**Starts when:** the spec is approved, its UI surfaces section lists a surface, and the user asks for a design, whether at the end of Outline, at the start of Plan, or by running `sdd-design`.
**Produces:** `design.md` (Appendix B) and a snapshot under `design/` in the spec folder, approved; or `design.md` recorded as `skipped`.

The phase is optional.
A spec whose UI surfaces section is absent or empty never enters it, and no `design.md` is written.
The design conversation runs outside the SDD session, in a Claude chat or a Claude Code `/design` session the user drives.
This phase writes the prompt for it and records its result; it never invokes `/design`, never publishes a Design artifact (the spec's mockup, not the Design System artifact `design-init` builds), and never steers the conversation.

### State

- **`requested`**: the prompt is out and the chain waits.
  `sdd status` reports `2. Design`, and Plan, Tasks, Implement and Validate refuse to start and name `sdd-design`.
  A design requested mid-build stops `sdd-implement` at its next start.
- **`skipped`**: the user declined a design or cancelled a requested one.
  `decided_by` (the git `user.name`), `surfaces` (the UI IDs the skip covers) and the date are recorded, and the reason goes under Skip reason.
  A re-approved spec that lists a UI ID the skip does not cover returns the chain to `2. Design`, so the user is offered a design for the new surfaces.
- **`approved`**: the plan builds on it.
  The plan records the design's `approved_hash` as its `based_on`, so re-approving the design, or a spec change that stales it, stales the plan and everything below it.

Every request, skip, cancel and approval happens only on the user's word in the conversation.
After each, in a shared repository, stage `design.md` (and `design/` at approval) by explicit path and propose a commit message; the user commits.
`design.md` is the handoff: any later session running `sdd-design` resumes from its state.

### Steps

`sdd-design` reads `design.md`'s state and does the one step it calls for.

1. **Request.**
   On the user's word, run `sdd set-status <slug> design requested`, which creates `design.md` from Appendix B when absent, records `based_on`, and on an existing `design.md` clears the recorded `link`, `version`, `read`, `design_system` and approval, and a skip's `decided_by` and `surfaces`, so the old design cannot be approved as the new one.
   Write the prompt (below) under Prompt, show the same text in the conversation as one copyable block, and tell the user to run it after `/design` in Claude Code or paste it into a Claude chat with Design selected, then bring the approved design's link back.
2. **Skip or cancel.**
   On the user's word, run `sdd set-status <slug> design skipped` and write the reason under Skip reason.
3. **Revise the prompt.**
   When the spec is re-approved while the design is `requested` and nothing is recorded yet, rewrite Prompt against the revised spec, run `set-status design requested` again to refresh `based_on`, and list what changed so the user can carry it into the running design conversation.
4. **Record.**
   When the user brings back the approved design's link, save the snapshot and fill the record (The snapshot, below).
5. **Check against the spec.**
   Put each miss and each gap to the user (Misses and gaps, below).
6. **Re-check.**
   When the spec is re-approved after a design was recorded, check the recorded design against the revised spec through misses and gaps, without writing a new prompt unless the user asks for one, then set `based_on` to the spec's new `approved_hash` before the gate.
7. **Gate.**
   Once every miss and gap is answered, `sdd lint <slug> design` passes and the user approves, record it with `sdd approve <slug> design` (Gate, below).

### The prompt

The prompt stands alone after `/design` or pasted into a Claude chat.
It contains no repository path, shell command or SDD tool name, and refers to nothing outside itself except the design system's link; requirement IDs are allowed.
It carries:

- The spec's goal and audience.
- Every surface in the spec's UI surfaces section with its UI ID, each state the spec names (the empty, loading and error states from its edge cases included), and the requirement IDs each serves.
- The devices or widths the spec requires.
- The spec's non-goals, restated in product terms as things not to design.
- The design system: the Claude design system link DESIGN.md records, restating none of its tokens; otherwise DESIGN.md's Overview, Key Characteristics and Do's and Don'ts text; otherwise, when DESIGN.md is absent or still holds bracket placeholders, a statement that the project has no design decisions yet.
- The WCAG 2.2 AA floors, the target size, reading width and motion timing DESIGN.md sets or the standards' starting values where it is absent, still holds bracket placeholders, or is silent on one, and that customer-facing copy contains no em-dash.
- The process: two or three directions on one named primary screen first, then the complete design in the direction the user picks, with one artboard per screen and state titled with both, such as `UI-001 Settings / empty`.
- A closing line asking the user to bring the approved design's link back.

The prompt never carries secrets, credentials, customer PII or restricted material, and contains no em-dash itself.

### The snapshot

Claude Design keeps no version history, so the link cannot pin what the user approved; the saved snapshot is the record.

- Read the Design artifact through its link with the Artifact tool: `project/canvas.json`, every `project/*.dc.html` artboard file, and the copied design system's `tokens.json` under `project/ds/` when the canvas used one.
  Save them under `design/` in the spec folder, deleting the artboard files of any earlier read first.
  Images the canvas holds stay links to the artifact.
- Record in `design.md` the `link`, the `read` date, the artifact `version` id read (so a later read can tell whether the canvas changed), and the `design_system` the canvas used or `none`.
- List each artboard under Artboards with its UI ID, screen, state and requirement IDs, and beside it any PNG the user placed in `design/` named after the artboard's file stem.
- When the link cannot be read (not found, no access, not a Design artifact), the session has no Artifact tool, the artifact belongs to someone else so the read returns a summary, or the artifact lacks `project/canvas.json` or any artboard file: report it, write no snapshot, and leave the design `requested`.
  For another owner's artifact, ask the user to copy the design into their own account and bring that link back.
- When the canvas used a different design system than DESIGN.md records, or none while one is recorded, report it from `canvas.json` and ask the user to accept it or revise the design.
- An edit made in Claude after approval counts only when the user brings the link back, which reruns the record, the check and the gate.

### Misses and gaps

- **Miss:** a listed surface or named state that no artboard shows.
  Ask the user to revise the design or accept the miss; an accepted miss goes under Accepted misses with its state and requirement IDs, and is built from the design system without a mockup.
- **Gap:** a screen, control or state the design shows that no requirement covers.
  Ask the user to add it to the spec or leave it out of this build.
  An addition routes to `sdd-outline` and leaves the design `requested` until the spec is re-approved; an exclusion goes under Not built, and nothing downstream builds it.

### Gate

Every miss and gap is answered, `sdd lint <slug> design` passes, and the user approves in the conversation.
Record it with `sdd approve <slug> design`, which refuses on a lint error or a missing `link`, `version` or `read`.
In a shared repository, stage `design.md` and `design/` by explicit path and propose a commit message.
Name `sdd-plan` as the next step.

---

## 9. Phase 3: Plan (`sdd-plan`)

**Purpose:** decide how the approved spec, and its approved design when there is one, will be built.
**Starts when:** `spec.md` is approved, unchanged since approval, and has no clarification markers, and `design.md` is absent, skipped covering every listed UI surface, or approved and current.
**Produces:** `plan.md`, approved.

### Steps

1. **Settle the design.**
   When the spec's UI surfaces section lists a surface and no `design.md` exists, ask the user whether to run `sdd-design` first or skip it.
   A run stops this phase and names `sdd-design`; a skip is recorded in `design.md` as at the end of Outline (section 7), and planning continues.
   When the design is approved, load `design.md` and its artboard list: the plan builds what it records and nothing it lists under Not built.
2. **Research** anything the plan depends on, such as library versions, API behavior, service limits and pricing.
   Record findings with sources.
   Don't rely on memory for version-specific facts.
3. **Draft `plan.md`** from the template (Appendix C).
4. **Offer options.**
   For each significant decision, present at least two options with trade-offs and a recommendation, and let the user choose.
5. **Name the seams.**
   For each slice, name the boundary its tests will run at, chosen by the seam rules in section 12. The repo's established seam for that kind of code wins over a purer choice.
6. **Check the principles.**
   Mark the plan pass or fail against each project principle, and justify every deviation.
7. **Route spec gaps back.**
   If planning exposes a gap in the spec, stop and route back to `sdd-outline`.
   Don't patch the gap in the plan.
8. **Gate.**
   Every requirement maps to plan elements and a seam, `sdd lint <slug> plan` passes, and the user approves.
   Name `sdd-task` as the next step.

### Sections

- **Approach:** a short summary of the technical approach.
- **Technical context:** stack, versions, dependencies and platform limits.
- **Principles check:** pass or fail against each project principle, with any deviations justified.
- **Architecture:** components, what each is responsible for, and the boundaries between them.
  Add a diagram only if it clarifies.
- **Data model:** entities, fields, relationships and migrations.
- **Interfaces and contracts:** APIs, events, schemas, error formats, and any multi-agent handoff contracts.
- **Affected code:** the files and modules to change or create, and an existing file to use as the pattern; with an approved design, the components that build each designed surface, by UI ID.
- **Seams and test strategy:** for each slice, the seam, the test types the repo uses for that kind of code, and how each acceptance criterion becomes a test.
- **Alternatives considered:** each option, and why it was rejected.
- **Trade-offs and risks:** what the team takes on, and how each risk is mitigated.
- **Rollout:** flags, migrations, backfills and rollback.
  Sequence the work as steps that each ship on their own.
- **Traceability:** a table mapping each requirement to its components, seam and tests; with an approved design, the components named for each designed surface's requirements.
- **Research notes:** facts you verified, with sources.

### Rules

- Every element of the plan traces to a requirement or a constraint.
  Remove anything that doesn't.
- Choose the simplest design that meets the requirements.
  Leave out speculative extension points.
- Reuse existing patterns, and point to a concrete example file.
- Each rollout step must leave the system working and ship on its own.

---

## 10. Phase 4: Tasks (`sdd-task`)

**Purpose:** break the approved plan into small tasks, each one behavior that a red-green loop can build.
**Starts when:** `plan.md` is approved and unchanged since approval.
**Produces:** `tasks.md`, approved.

### Task shape

```
- [ ] T012 Reject registration when the email format is invalid
  - Requirements: FR-003
  - Seam: request test on POST /registrations
  - Files: src/auth/registration.ts, tests/auth/registration.test.ts
  - Depends on: T010
  - Done when: `npm test -- registration` passes, including the invalid-email cases
```

### Rules

- **One behavior per task.**
  A task is one observable behavior that a test can lock down, built with one red-green loop or a short run of them.
  Its test is written inside the task, never in a separate "write the tests" task.
  Writing all the tests first and all the code afterward tests imagined behavior.
- **Size:** each task produces one focused diff that is easy to review.
  Write "Reject registration when the email format is invalid," not "Build authentication."
- **Slices:** group tasks by user story (P1, P2, P3) so each slice ships on its own.
  Within a slice, build foundations before the things that depend on them.
- **Slice close:** end every slice with a close-out item covering the full suite, staging and the orchestrator's commit (Appendix D).
- **Revising a built list:** leave each new task unchecked, and uncheck a task whose behavior changed, deleting its `- Evidence:` line.
  Uncheck the close-out of every slice that holds an unchecked task, because `sdd-implement` builds only the slices whose close-out is unchecked.
  `sdd lint` reports an unchecked task under a checked close-out as an error.
- **Seam:** every task names its seam, taken from the plan.
- **Coverage:** every functional requirement has at least one task, and every task traces to a requirement that is still in force.
  A non-functional requirement or invariant needs a task too, unless the user decides it is verified another way; record that decision under Verified elsewhere (Appendix D) with the ID, how it is verified and who decided.
  `sdd lint` reports an uncovered requirement as an error, and the section sits inside the content hash, so changing an entry after approval counts as a change.
  A task with no requirement means scope creep or a gap in the spec.
- **Done when:** make the check something that runs and returns pass or fail wherever possible.

### Gate

`sdd lint <slug> tasks` passes its traceability checks and the user approves.
Name `sdd-implement` as the next step, and recommend starting it in a fresh session.

---

## 11. Phase 5: Implement (`sdd-implement`)

**Purpose:** build the tasks slice by slice, each by a fresh `implementer` agent working through the `tdd` discipline, and commit each slice once it is verified.
**Starts when:** `tasks.md` is approved and unchanged since approval, on a feature branch.
**Produces:** code and tests, one commit per slice plus any trunk commits, and `tasks.md` checked off with status `done`.

The session running `sdd-implement` is the **orchestrator**.
It dispatches, verifies, commits and talks to the user, and writes nothing but `tasks.md`'s status, close-out boxes and `render_check` and `render_check_asked` frontmatter keys, the spec's `branch` and `base` fields, its journal entries, git commits and the processes it starts.
Every line of code, test and task evidence comes from an `implementer` in a fresh context, so the build follows the approved artifacts instead of the memory of the conversation that produced them.

The build keeps the journal (section 5), so that `tasks.md`, the journal and `git status` together say where an interrupted build stands.
Each `implementer` records its report there before sending it.
The orchestrator records each question it stops on for the user before asking it, the answer before acting on it, and any decision the user gives unasked.
It records `resolved` in the same command as each commit that settles a report or QA, with the journal staged in that commit when the repository is shared, so no session can end between a journal that calls work settled and the commit that settles it.

In a private repository (section 5) no commit of this phase holds `tasks.md`, `spec.md` or the journal.
Wherever a step below commits only those files, the file is written and no commit is made; wherever it commits them with code, the code is committed alone.

### Steps

1. **Check the branch.**
   The spec's `branch` field names the feature branch, and its `base` field the branch that one is cut from and merges back into (section 5).
   When the spec records no base, record the one git detects with `sdd set-base <slug>` first, and ask the user only when that fails.
   On the spec's branch, in the worktree Outline made, continue: this phase builds there and creates no branch of its own.
   A spec outlined before its branch existed is still on the base or another shared branch: propose making the branch and ask first; if the user picks another name, update the spec's `branch` field, which sits outside the hash.
   In a private repository `sdd worktree <branch> --base <base>` makes it with its worktree, as Outline would have, or names the worktree that already has it (section 5).
   In a shared repository the spec's files sit in the checkout they were outlined in, where no new worktree would hold them, so make the branch in that checkout with `git switch -c <branch>`, which carries uncommitted files along, then stage each spec file still uncommitted by explicit path and wait for the user to commit them.
   A worktree made without the repository's own worktree script has no dependencies installed: install them with the repo's install command before the first dispatch, and ask the user before copying an untracked local file, such as an env file, from the main checkout.
   Every commit of this phase lands on the feature branch, never on the base.
2. **Resume** at the first slice whose close-out item is unchecked, and set `tasks.md` to `in-progress`.
   Build only the slices whose close-out is unchecked, since a revised task list reopens the slices it touched and leaves the rest closed (section 10).
   If there are uncommitted changes that no report still awaiting its `resolved` entry names, list them and let the user choose between handing them to a fresh `implementer` to continue that slice and setting them aside by hand; never discard them.
   When `sdd status` reports a pending journal entry, continue from it before any new dispatch: act on a `report` as if it had just arrived, put a `question` to the user again, and act on an `answer` or `decision`, handing it to a fresh `implementer` when the agent it was meant for is gone.
3. **Render checks.**
   When the spec lists a UI ID that `tasks.md`'s `render_check_asked` frontmatter key does not, on the first start or any resume, since a spec re-approved mid-build can add a surface, list those surfaces and recommend each that is new, has an approved design, changes layout between the mobile and desktop widths, or uses a color pairing no existing surface uses, naming the criterion in one line.
   The user approves any, all or none.
   Write the approved UI IDs to `tasks.md`'s `render_check` frontmatter key, comma-separated, or `none` while no surface is approved, and every ID asked about to `render_check_asked`.
   Each key is written on the first answer and extended on later ones, since no template or helper writes them; an approved ID replaces a recorded `none`.
   In a shared repository, commit both before the next dispatch.
   Frontmatter sits outside the content hash, so the tasks stay approved, and no surface is asked about twice.
   With `none`, no render check runs.
4. **For each slice, one at a time:**
   1. **Dispatch** a fresh `implementer` with a brief of pointers only: the slug, the slice heading, the facts earlier slices reported as notes, the user's decisions for this slice, and any uncommitted paths the agent inherits from one that is gone.
      The agent loads its tasks, requirements, plan sections and seams itself, builds each task through `tdd` (section 12), checks off each task with one `- Evidence:` line, and checks its diff against the matching `docs/standards/` files before it reports.
      Inherited paths become the agent's own work, and its report lists them with the paths it changed.
   2. **Blocked.**
      The agent stops for the conditions under Stop and ask.
      Put its question to the user with options and a recommendation, dispatching the `skeptic` agent first when the question is a trunk change, then resume the same agent with the answer, or dispatch a fresh one with it when that agent is gone.
   3. **Trunk commit.**
      An approved trunk change is built first and reported on its own; run the full suite, commit it alone with a body that opens `Trunk change:` and records the skeptic's verdict and the user's decision, then resume the agent to finish the slice.
   4. **Verify** before committing, since a report is a claim: rerun each "Done when" check, run the full suite, confirm the reported files and test files match every changed path apart from `tasks.md` and the journal, confirm `tasks.md` changed only in this slice's boxes, Evidence lines and Follow-ups, and confirm with `sdd status` that it is unchanged since approval.
      A failing test in a file the slice added or changed belongs to the slice; any other failing test that also fails at `HEAD`, checked in a temporary worktree with dependencies installed rather than by stashing, is recorded as pre-existing.
      Any other failure goes back to the same agent once; a second failure stops the run with the evidence and no commit.
   5. **Commit** the verified slice: check its close-out item, stage by explicit path, including `tasks.md` and the journal in a shared repository so the progress log lands with the slice, and commit with the agent's judgment calls in the body.
      Never use `git add -A` or `git add .`, and never push.
5. **QA.**
   When every slice is checked off, run `sdd lint <slug>`, start the app when the change has a runnable surface, and hand the user one QA script whose every observation maps to a "Done when" check or an acceptance criterion.
   When `render_check` names surfaces, dispatch `render-checker` once for all of them before handing over the script, and put each failure into the script with its evidence and screenshot path; only the failures the user picks go to a fresh `implementer` as QA bugs.
   Each surface or state its report lists under Not reached goes into the script with its reason, as an item the user checks by hand.
   The script is a question the session stops on, so a session resuming at QA hands the recorded script over again without a second render pass.
   A bug the user finds goes to a fresh `implementer` as a red-first fix, which the orchestrator verifies and commits before QA resumes.
6. **Finish.**
   When the user confirms QA, set `tasks.md` to `done`, commit that change in a shared repository, stop the processes the session started, and report what was built, where the build stopped and how each stop was resolved, the judgment calls made, any pre-existing failures, and the follow-ups.
   Recommend `sdd-review` next in the same session, since its reviewers run in fresh contexts of their own; the user may still choose a fresh session.

### While working

The `implementer` holds these rules; the orchestrator checks the result against them.

- **Follow the plan.**
  A plan that turns out to be wrong against the code is a contradiction, reported under Stop and ask.
  Don't improvise a new architecture.
- **Stay in scope.**
  Record bugs, refactors and ideas as follow-ups instead of acting on them.
- **Follow existing patterns** in the codebase.
- **Never weaken a check to make it pass.**
  Skipping tests, loosening assertions and suppressing errors are not fixes; when nothing else makes a check pass, the same approach has failed twice, which is a reason to stop and ask.
- **Manage context.**
  Each slice runs in its agent's fresh context, so the orchestrator's own context holds only reports and verification.
  `tasks.md` and the journal are the memory a resumed session reads, so they stay current.

### Stop and ask when

The `implementer` reports `BLOCKED` and the orchestrator asks the user when:

- A gap would change observable behavior that a requirement or acceptance criterion describes, or would cross a non-goal or an invariant.
  A gap that changes only how the slice is built is the agent's to decide and report.
- The spec contradicts itself or the code.
  Raise it and don't choose a side.
- A task needs an "Ask first" action.
- The same approach has failed twice.
- The work needs a trunk change the spec did not decide.
  The agent applies a proof bar before building an approved one: every consumer is in the repository and updated with it, and it alters no published package API, external HTTP contract or schema holding live data.

---

## 12. TDD discipline (`tdd`)

The `tdd` skill owns this discipline and stands on its own.
Use it for any change a test can lock down, inside the SDD chain or as a one-shot for a small task.
It knows nothing about SDD: the `implementer` agent and `sdd-review` hand it one behavior at a time.
This section summarizes what SDD relies on; the skill and its references are the full version.

- **Discover the repo first.**
  Before the first test, `tdd` finds the repo's commands, frameworks, test locations, one living example of each test type and how collaborators are doubled, from the repo's own files, and never invents a command.
  It skips the discovery when `CLAUDE.md` or an earlier run in the session already holds those facts.
- **A good test** checks behavior through a public interface, never implementation detail.
  It reads like a specification ("rejects a draw with no line items"), survives a refactor that changes no behavior, and uses independent literal expected values, never values recomputed the way the code computes them.
- **Seams.**
  A seam is the boundary a test runs at.
  A caller that names the seam decides it.
  Otherwise choose it by what the code depends on and by what the repo already does for that kind of code, because the repo's established seam wins:
  - Pure computation: test through the module interface, with no doubles.
  - The database: use the real test database.
  - Collaborators the repo already doubles at that layer: double them the same way, through the same helper.
  - True externals such as payment providers and third-party APIs: mock at the client edge only, never deeper.
  - UI: test behavior (pressing this sends that payload; the error renders; the hidden section stays hidden until toggled), never appearance or layout.
- **Bug fixes** open with a failing test that reproduces the report at the lowest seam that shows it, and that fails for the reported reason.
- **The loop:**
  - Red before green: write the failing test first, then only enough code to pass it.
  - Each cycle covers one seam, one test and one minimal implementation.
  - Keep each cycle's checks bounded: run the touched test files and lint the touched files.
    Run the full suite once at the end of the unit of work.
    The caller names the unit: the `implementer` names the task and `sdd-implement` runs the full suite at slice close, `sdd-review` names the fix, and in a one-shot the unit is the whole request.
  - Refactoring is a separate tidy after green, with tests unchanged, and only inside code the task already touches.
- **Anti-patterns:**
  - **Implementation-coupled** tests break under a refactor that changes no behavior.
  - **Tautological** tests recompute the expected value the way the code does, so they pass by construction.
  - **Appearance-pinned** tests rely on snapshots, style classes or geometry.
  - **Horizontal** work writes all the tests first and all the code afterward.
  - **Duration waits** sleep for a fixed time instead of waiting on an observable condition.
    An `act(...)` warning counts as a failure.
- **Report back:** the tests written, the failing output that proved red, the passing output, the files touched, any appearance assertions removed, and any failures that existed before the change.

---

## 13. Phase 6: Validate (`sdd-review`)

**Purpose:** prove the branch does what the spec says, review it for correctness and standards, confirm with the user that it's what they meant, and prepare the PR.
**Starts when:** every task is done, on a feature branch with a clean tree.
**Produces:** `review.md`, the fixes the user picks, and a PR description draft.

`sdd-review` also runs without a spec, as a pre-PR review of any branch, for example after a `tdd` one-shot.
Use spec mode when a slug is given or the branch's spec has its tasks done.
When the branch's spec is not done yet, say so and ask before reviewing without it.
Without a spec the skill skips the start and finish protocols and the steps marked _(spec only)_, writes no `review.md`, and puts the report, the intent confirmation and the PR description draft in the conversation.

### Gate

- **Feature branch with a clean tree.**
  Uncommitted work would be reviewed as if it ships.
  If the tree isn't clean, list the paths and stop.
  The spec's own `review.md` is not such work: the review writes it and leaves it uncommitted until acceptance, so `sdd uncommitted <slug>` lists every uncommitted path except that file, and this gate and the fix check both read the tree through it.
  In a private repository git lists nothing under the spec folder, so the same command lists only the branch's own work.
  A review already in progress settles its uncommitted paths under Resume instead of stopping.
- **Base branch:** the argument if given, otherwise the base `sdd base` prints: the one the spec records, else the remote's default branch.
  The comparison reads it as `origin/<base>` when the remote has that branch, since a local copy can lag behind it.
  Ask the user only when it reports that git could not tell.
- **Effort and findings cap:** the argument if given.
  Otherwise ask once, suggesting `high` or `xhigh` with a cap of 3 to 5 scaled to the size of the diff.

### Run

The session running the review may be the one that ran the build.
Its independence comes from the reviewers: each runs in a fresh context on a brief of pointers only (the artifact paths, the repository root, the base and the range), never the session's reasoning.
`code-review` is a forked skill, a subagent that does not see the conversation; the conformance check and `standards-reviewer` are agents dispatched with those pointers.

Run these in parallel where possible:

1. **Evidence** _(spec only)_.
   Run the full suite once on the clean tree.
   Map each acceptance criterion to the test that proves it.
   Measure each non-functional requirement instead of assuming it.
2. **Spec conformance** _(spec only)_.
   A subagent in a fresh context gets the spec, the plan, the tasks and the diff, but not the implementer's reasoning.
   It checks that each requirement is implemented and tested, each listed edge case has a test, nothing outside the scope changed, and the invariants hold.
   It reports only gaps that affect correctness or the stated requirements.
3. **Correctness.**
   Run the `code-review` skill with the effort level, `--max-findings <n>`, and this branch against the base.
   Keep its findings verbatim.
4. **Standards.**
   Dispatch the `standards-reviewer` agent with two inputs: the base ref and the commit range.
   It judges legibility, tests as documentation, usability floors and customer-facing text against `CLAUDE.md` and the `docs/standards/` files whose globs match the changed paths.

### Triage

Every finding is input, not a verdict, so judge each one yourself.
Reject a finding you judge false, with evidence, and still show it to the user.
Drop findings the linter already owns.
Don't pad the report with style preferences; chasing every finding leads to over-engineering.

### Report, then wait

Write one report to `review.md` (Appendix E), or to the conversation without a spec, and show it:

- _(spec only)_ Spec conformance: each requirement met or not, with evidence, and each gap.
- Correctness findings, with severity and `file:line`.
- Standards findings, with the standards line each one fails.
- The standards reviewer's reads-well notes.
- Rejected findings, with the evidence.

`review.md` is also the record a later session resumes from, so it holds two things the conversation would otherwise carry.
`range` names the reviewed head by its commit hash, which lets a later session tell whether the branch has moved since.
Each conformance gap, correctness finding and standards finding is a top-level bullet in its section, the only kind of top-level bullet there, with one `- Disposition:` line under it:

- `open`: the user has not decided it.
  Every finding starts here.
- `picked`: the user chose to fix it, and the fix is not committed yet.
- `fixed`: its fix is committed and listed under Fixes.
- `declined`: the user chose not to fix it, followed by their reason.
- `deferred`: the user moved it to later work, followed by where that is recorded.

A section with no finding holds `- None`.
A disposition changes only on the user's decision or when a picked fix is committed.
`sdd lint <slug> review` reports a finding with no disposition, and one still `open` or `picked`.

Then stop and wait for the user.

### Fixes

The user picks which findings to fix.
Record each decision in `review.md` before acting on it: `picked` on a finding to fix, and `declined` or `deferred` on one the user turns down or postpones.
A rejected finding the user picks moves back to its findings section as `picked`.
A fresh `implementer` builds each fix red-first from the finding, its `file:line` and the requirement IDs it touches; the reviewing session never writes the fix itself.
Verify it with the repo's test tiers and by matching the files the agent reports against every uncommitted path, read with `sdd uncommitted <slug>` when there is a spec so the report itself is left out.
Stage it by explicit path and propose a commit message; commit only on the user's word, since a review fix answers a finding the user picked rather than an approved task.
Once it is committed, list the fix under Fixes with its test and commit, and set the finding to `fixed`.
If the fixes are substantial, offer to rerun the review (Resume).

### Resume

A `review.md` at `open` when the skill starts is a review in progress.
Continue it from that file alone: skip Run, Triage and writing the report, and run no reviewer again unless the user chooses a rerun.

- **Read the report.**
  Its frontmatter records the base, range, effort and cap the review ran with, each finding carries its disposition, and Fixes lists each fix with its commit.
- **Check that the branch is still the one reviewed.**
  `range` ends at the commit the reviewers read, and every commit after it should be a fix the report lists.
  When another commit follows it, or that commit is no longer on the branch, the report describes code that has since changed: show the user the commits and ask whether to rerun the review or continue on the report as written.
- **Settle uncommitted paths.**
  Any path `sdd uncommitted <slug>` lists is work an earlier session left unfinished, usually the fix for a `picked` finding.
  List the paths and let the user choose between handing them to a fresh `implementer` to finish that fix and setting them aside by hand; never discard them.
- **Continue from the dispositions.**
  Build the fix for each `picked` finding, put each `open` finding to the user, and go to Confirm intent and close once neither is left.
- **A rerun** runs the reviewers again on a clean tree and rewrites the report for the new range.
  Every finding the user has decided keeps its line and disposition, the Fixes entries stay, the new findings replace those still `open`, and a new finding that repeats a decided one is left out.

### Confirm intent and close

- Passing tests prove the code matches the spec, not that the spec matched the intent.
  Restate in plain language what was built and ask the user to confirm it's what they meant.
- On the user's acceptance, draft the PR description in `review.md`, or in the conversation without a spec, then set `review.md` to `accepted` with `sdd set-status <slug> review accepted`, which refuses while `sdd lint <slug> review` reports an error, such as a placeholder still in the report or a finding still `open` or `picked`.
  Acceptance decides no finding: put each one still `open` to the user first.
  The draft has four parts: a summary paragraph following the rules in section 7, what changed, how it was verified (with evidence), and any decisions made and follow-ups.
  Don't push or open the PR unless the user asks.
- _(spec only)_ In a shared repository, stage `review.md` by explicit path and propose its commit message.
  The folder stays as the record of the change.

Nothing is pushed from this phase.

### After acceptance

An accepted review covers the tasks it records as `based_on`.
A finished run comes back to this phase in two ways, and `sdd status` names the step for each:

- **The tasks were re-approved** after a late change (section 14), so the review is stale and the phase is `6. Validate` again.
  Reopen the review with `sdd set-status <slug> review open`, run every review again on the rebuilt branch, and replace the report with the new results.
- **Feedback arrives that changes no artifact,** such as a pull request comment or a bug found after acceptance.
  On the user's word, reopen the review the same way.
  Each item joins the report as a finding that names its source, and goes through Triage and Fixes like any other.
  Feedback that changes behavior a requirement describes is a spec change and goes to `sdd-outline` instead (section 14).

Either way the review is accepted again through Confirm intent and close, with the PR description draft brought up to date.

---

## 14. Changing course

- **Behavior changes mid-flight.**
  Update the spec through `sdd-outline` and re-approve it.
  Refresh the plan and tasks once they go stale, then change the code.
- **A bug found during Implement.**
  If the code violates the spec, fix it with `tdd`, starting from a failing test.
  If the spec was wrong or incomplete, route back to `sdd-outline`.
- **A change after the tasks are done or the review is accepted.**
  It takes the same route: the spec through `sdd-outline`, then the plan and tasks as they go stale.
  Re-approving the tasks returns the run to Implement, which builds only the slices the revision reopened (section 10), and makes an accepted review stale, so the run passes through Validate again (section 13).
- **Feedback after the review is accepted** that changes no artifact, such as a pull request comment, reopens the review (section 13).
- **An abandoned spec.**
  Nothing in the chain deletes work, so abandoning a spec is the user's word and the user's cleanup: remove the worktree (section 5), delete the branch with `git branch -d <branch>`, and delete the remote's copy if it was pushed.
  Git refuses rather than lose work: `git worktree remove` while the worktree holds uncommitted files, and `git branch -d` while the branch holds commits that are neither merged nor pushed, which in a shared repository includes its spec commits.
  Forcing either one discards that work, and is the user's call.
  A private repository's spec folder is no part of the branch, so it stays in the main checkout's `docs/sdd/` until the user deletes it.
- **Drift.**
  When you touch code the spec covers, check that the spec still describes it.
  If it doesn't, say so before going further.
- **Overlapping specs.**
  When two specs cover the same area, the newer approved spec wins, and it says what it replaces.

---

## 15. Anti-patterns

| Anti-pattern            | What it looks like                                                                    | Do instead                                                      |
| ----------------------- | ------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Vision document         | Lofty goals with no scope or criteria, so the agent makes the real decisions          | Goals, non-goals and acceptance criteria                        |
| Pseudo-code spec        | The spec dictates classes, functions and line-level logic                             | Describe observable behavior; move the how into the plan        |
| Conversation transcript | "As mentioned above," or reliance on context the reader never saw                     | Self-contained statements                                       |
| Sledgehammer            | The full chain for a one-line fix                                                     | Size the change first (section 3)                               |
| Spec bureaucracy        | Long, repetitive documents nobody reviews                                             | Shorter artifacts; cut any section that adds nothing            |
| Silent assumption       | The agent fills a gap with a plausible guess                                          | A clarification marker, then ask                                |
| Skipped gate            | A phase starts before the previous artifact is approved, or after it changed          | The start protocol and `sdd status`                             |
| Horizontal tasks        | A "write all the tests" task, then a "write all the code" task                        | One behavior per task, red then green                           |
| Rule overload           | So many rules that some are ignored and others over-applied                           | Short rule files; automate the rules that must always hold      |
| False confidence        | Tests pass, but the spec was wrong                                                    | Confirm intent with the user; review specs as carefully as code |
| Duplicate build         | Code described as existing gets rebuilt                                               | Label existing behavior; name the modules to reuse              |
| Overloaded context      | The whole spec set plus unrelated history loaded at once                              | Load only what the phase needs; fresh sessions at breaks        |
| Scope creep             | Refactors and extras appear in the diff                                               | Record them as follow-ups                                       |
| Spec on the base        | A shared repository's spec is written on the base, where no gate commit can land      | Make the branch and its worktree before `sdd init` (section 5)  |
| Unstaged artifacts      | A shared repository's approved artifact never reaches the branch, and the PR lacks it | Stage the spec folder's files by explicit path at every gate    |
| Leaked spec             | A private repository's spec file is staged, committed or added with `git add -f`      | Stage nothing under a private spec folder (section 5)           |
| Hand-built path         | A spec file is sought under the current directory, where a worktree may not hold it   | Take every spec file's path from `sdd status`                   |

---

## 16. Quick reference

**You MUST:**

1. Size the change before writing anything (section 3).
2. Start every SDD skill with the start protocol, and finish with the finish protocol (section 4).
3. Ground yourself in the project context and the relevant code before proposing anything.
4. Write what and why before how, in separate artifacts.
5. Mark every ambiguity with a clarification marker instead of guessing.
6. Stop for the user's approval after the spec, any design, the plan and the tasks.
7. Number every requirement, make each testable, and trace each through the plan, tasks and tests.
8. Build each slice through a fresh `implementer`, one task at a time through `tdd`, with evidence for every check.
9. Verify each slice yourself, then close it with the full suite, staging by explicit path, and the orchestrator's commit.
10. Validate with `sdd-review`: the evidence, spec conformance, correctness and standards reviews, then confirm intent with the user.

**You MUST NOT:**

1. Start a phase whose upstream artifact is unapproved, changed or stale.
2. Approve or push on the user's behalf.
3. Weaken, skip or delete a check to make it pass.
4. Treat a description of existing behavior as a new requirement.
5. Add abstraction or features that no requirement calls for.
6. Commit a gate artifact or a review fix on the user's behalf, or stage with `git add -A` instead of by explicit path.
7. Stage or commit a spec file in a private repository, or build a spec file's path by hand instead of taking it from `sdd status`.
8. Write, stage or commit a shared repository's spec file on the base or another shared branch.

---

## Appendix A: Spec template

```markdown
---
title: <Feature name>
slug: <slug>
branch: <feature branch>
base: <base branch>
status: draft
owner: <person>
created: YYYY-MM-DD
updated: YYYY-MM-DD
approved_hash:
description: <1–2 sentences; see section 7>
---

# <Feature name>

## Summary

<One paragraph, 5–7 sentences; see section 7.>

## Problem and context

<Current state, who is affected and how, each distinct problem on its own line (for a bug, each cause), and evidence (metrics, incidents, user reports) with sources.>

## Goals

- G1: <outcome, measurable where possible>

## Non-goals

- <out of scope, with the reason if it isn't obvious>

## User scenarios

### P1: <story title>

As a <user>, I want <capability> so that <outcome>.
Independent test: <how this slice is verified on its own>

- Given <context>, when <action>, then <result>.

### P2: <story title>

...

## UI surfaces

- UI-001: <screen, page, view, component or email template> (<new or edited>)

## Requirements

### Functional

- FR-001: When <trigger>, the system shall <behavior>.
  - Acceptance: Given <context>, when <action>, then <result>.

### Non-functional

- NFR-001: <metric, threshold and conditions>

## Invariants

- INV-001: The system shall never <behavior>.

## Edge cases and failure behavior

- <case>: <expected behavior>

## Existing behavior

<What exists today that this change builds on. These are not new requirements; do not re-implement them.>

## Assumptions

- A-001: <assumption>. Accepted by <person>.

## Open questions

- [NEEDS CLARIFICATION: <specific question>]

## Glossary

| Term | Meaning |
| ---- | ------- |

## Changelog

- YYYY-MM-DD: <change and reason>
```

## Appendix B: Design record template

```markdown
---
title: <Feature name> design
slug: <slug>
status: requested
updated: YYYY-MM-DD
based_on:
approved_hash:
decided_by:
surfaces:
link:
version:
read:
design_system:
---

# <Feature name> design

## Prompt

<The design prompt exactly as shown to the user, or "None" for a skip.>

## Artboards

- <file>: <UI ID> <screen> / <state>; <requirement IDs>; <PNG file, or no PNG>

## Accepted misses

- <UI ID> <state>: <requirement IDs>; built from the design system without a mockup

## Not built

- <screen, control or state the design shows>: <why it is left out of this build>

## Skip reason

<Why the design was skipped or cancelled, or "None".>
```

## Appendix C: Plan template

```markdown
---
title: <Feature name> plan
slug: <slug>
status: draft
updated: YYYY-MM-DD
based_on:
approved_hash:
---

# <Feature name> plan

## Approach

<A short summary of the technical approach.>

## Technical context

- Stack and versions:
- Dependencies:
- Platform limits:

## Principles check

| Principle | Pass/Fail | Notes |
| --------- | --------- | ----- |

### Deviations

- <principle>: <why the deviation is needed, and the simpler option rejected>

## Architecture

<Components, what each is responsible for, and the boundaries between them.>

## Data model

<Entities, fields, relationships, migrations.>

## Interfaces and contracts

<APIs, events, schemas, error formats, handoff contracts.>

## Affected code

- Change: <path>, <what changes>
- Create: <path>, <purpose>
- Pattern to follow: <path to an existing example>

## Seams and test strategy

### P1: <slice title>

- Seam: <boundary the tests run at, and why it's the repo's established seam for this code>
- Test types: <the repo's test types used here>
- Acceptance criteria to tests: <criterion → test>

## Alternatives considered

- <option>: <why rejected>

## Trade-offs and risks

- <what the team takes on>: <mitigation>

## Rollout

1. <step that ships on its own>. Rollback: <how>

## Traceability

| Requirement | Components | Seam | Tests |
| ----------- | ---------- | ---- | ----- |

## Research notes

- <verified fact>: <source>
```

## Appendix D: Tasks template

```markdown
---
title: <Feature name> tasks
slug: <slug>
status: draft
updated: YYYY-MM-DD
based_on:
approved_hash:
---

# <Feature name> tasks

## P1: <slice title>

- [ ] T001 <one observable behavior>
  - Requirements: FR-001
  - Seam: <from the plan>
  - Files: <paths>
  - Done when: <command or check that passes or fails>
- [ ] T002 <one observable behavior>
  - Requirements: FR-002
  - Seam: <from the plan>
  - Files: <paths>
  - Depends on: T001
  - Done when: <check>
- [ ] P1 close: full suite green, changes staged by explicit path, slice verified and committed

## P2: <slice title>

...

## Verified elsewhere

- <ID>: <how it is verified>. Decided by <person>.

## Follow-ups (out of scope)

- <discovery to handle later>
```

## Appendix E: Review report template

```markdown
---
title: <Feature name> review
slug: <slug>
status: open
base: <base branch>
range: <base>..<head>
effort: <effort>
max_findings: <n>
updated: YYYY-MM-DD
---

# <Feature name> review

## Spec conformance

| Requirement | Met | Evidence |
| ----------- | --- | -------- |

- <requirement ID>: <gap, with evidence>
  - Disposition: open

## Correctness findings

- [<severity>] <file:line>: <finding>
  - Disposition: open

## Standards findings

- <file:line>: <finding>. Fails: "<standards line>"
  - Disposition: open

## Reads well

- <note>

## Rejected findings

- <finding>: <why rejected, with evidence>

## Fixes

- <finding> → <fix, test, commit>

## PR description draft

### Summary

<One paragraph; see section 7.>

### What changed

- <change>

### How it was verified

- <command and result>

### Decisions and follow-ups

- <item>
```
