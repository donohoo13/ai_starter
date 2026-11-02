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

| Skill           | Phase                                  | Section | Job                                                            |
| --------------- | -------------------------------------- | ------- | -------------------------------------------------------------- |
| `sdd-outline`   | 1. Outline                             | 7       | Turn an idea into an approved `spec.md`                        |
| `sdd-plan`      | 2. Plan                                | 8       | Turn an approved spec into an approved `plan.md`               |
| `sdd-task`      | 3. Tasks                               | 9       | Turn an approved plan into an approved `tasks.md`              |
| `sdd-implement` | 4. Implement                           | 10      | Build the tasks one at a time, each through `tdd`              |
| `tdd`           | Used by phases 4 and 5, and on its own | 11      | Red-green discipline for any change a test can lock down       |
| `sdd-review`    | 5. Validate                            | 12      | Prove the branch meets the spec, review it, and prepare the PR |

The helper `.claude/sdd/bin/sdd`, run from the repository root, keeps state and the mechanical checks out of the skills' hands: `init`, `find`, `status`, `hash`, `lint`, `approve`, `set-status`, `templates sync` and `check-refs`.
It checks structure and state, not quality.

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
| Commits, pushes and PRs                            | Staging by explicit path and proposing commit messages      |
| Accepting the finished work                        | Reviewing the branch and reporting every finding            |

You MUST NOT make the user's decisions for them.
When a decision is theirs, present options with a recommendation and wait.

### Where the spec lives, and for how long

Specs are working documents that travel with the change.
They live in `docs/sdd/<slug>/` inside the project (section 5) and are committed on the feature branch, so the pull request carries them beside the code.
Every spec here is therefore **spec-first**: written before code to guide this change, then kept as the record of what was decided and why.

What carries the spec forward after the merge, beyond the folder itself:

- **Tests.**
  Each acceptance criterion becomes a test, so CI keeps enforcing the behavior whether or not anyone rereads the spec.
  This is why implementation is test-driven.
- **The PR description,** drafted from the spec's summary and the review evidence.
- **Commit messages.**
- **Repo docs or decision records,** only when the user asks for a lasting record, following the repo's convention.

You MUST NOT commit on the user's behalf.
Stage an artifact under `docs/sdd/` by explicit path at the gates section 4 names, propose the message, and let the user commit.

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
10. **The user commits.**
    You stage by explicit path and propose a commit message.
    You commit only on the user's word, and you never push.

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

| Phase        | Skill                        | Starts when                                                            | Produces                                                      | Exit gate                                                                          | Next            |
| ------------ | ---------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------------------------- | --------------- |
| 1. Outline   | `sdd-outline`                | The user brings an idea, brief, ticket or bug big enough for the chain | `spec.md`                                                     | Readiness checklist passes, no clarification markers, **user approves**            | `sdd-plan`      |
| 2. Plan      | `sdd-plan`                   | The spec is approved and unchanged since approval                      | `plan.md`                                                     | Every requirement traces to the plan and a seam, **user approves**                 | `sdd-task`      |
| 3. Tasks     | `sdd-task`                   | The plan is approved and unchanged                                     | `tasks.md`                                                    | Every requirement has a task, every task has a seam and a check, **user approves** | `sdd-implement` |
| 4. Implement | `sdd-implement`, using `tdd` | The tasks are approved and unchanged; on a feature branch              | Code, tests, commits the user made                            | Every task is checked off, each slice's full suite is green, the tree is clean     | `sdd-review`    |
| 5. Validate  | `sdd-review`                 | All tasks are done, on a feature branch with a clean tree              | `review.md`, the fixes the user picks, a PR description draft | **User accepts**                                                                   | Done            |

### State

Each artifact records its state in its frontmatter.

| Artifact    | Statuses                                      | Recorded at approval                                     |
| ----------- | --------------------------------------------- | -------------------------------------------------------- |
| `spec.md`   | `draft` → `approved`                          | `approved_hash`                                          |
| `plan.md`   | `draft` → `approved`                          | `approved_hash`, `based_on` (the spec's `approved_hash`) |
| `tasks.md`  | `draft` → `approved` → `in-progress` → `done` | `approved_hash`, `based_on` (the plan's `approved_hash`) |
| `review.md` | `open` → `accepted`                           | None                                                     |

The current phase follows from these states:

| State                                                     | Phase        | Skill to run    |
| --------------------------------------------------------- | ------------ | --------------- |
| No `spec.md`, a draft spec, or open clarification markers | 1. Outline   | `sdd-outline`   |
| Spec approved; plan missing or draft                      | 2. Plan      | `sdd-plan`      |
| Plan approved; tasks missing or draft                     | 3. Tasks     | `sdd-task`      |
| Tasks approved or in progress                             | 4. Implement | `sdd-implement` |
| Tasks done; review missing or open                        | 5. Validate  | `sdd-review`    |
| Review accepted                                           | Done         | None            |

**Changed and stale artifacts.**
An approved artifact whose content no longer matches its `approved_hash` counts as changed, and it needs re-approval.
Every artifact downstream of it becomes **stale** because its `based_on` no longer matches, and the work routes back to the skill that produces the stale artifact.
The hash covers the body below the frontmatter, so checking off tasks in `tasks.md`, the single `- Evidence:` line under a task, and the Follow-ups section do not count as a change.
A draft's `based_on` may stay empty until approval records it.
Once set, it must match: refreshing a stale artifact means revising it against its upstream and setting `based_on` to the new hash before re-approval.

### Every SDD skill starts the same way

1. **Find the working folder** `docs/sdd/<slug>/`.
   Use the slug from the argument.
   Otherwise use the spec whose `branch` matches the current git branch.
   Otherwise list the existing folders and ask.
2. **Read the state** with `sdd status <slug>`.
3. **Check this phase's preconditions.**
   If they aren't met, stop.
   Tell the user which phase the work is actually in and which skill to run.
   Don't do another phase's work.
4. **Load only what the phase needs:** this document's section for the phase, the project context, and the upstream artifacts.

### Every SDD skill finishes the same way

1. **Run the exit checks:** `sdd lint <slug>` plus the phase's checklist.
2. **Present** the artifact, a short summary of the decisions it contains, and any open questions.
   Ask for approval.
3. **Record approval only when the user gives it,** with `sdd approve <slug> <artifact>` for the spec, plan and tasks, and `sdd set-status <slug> review accepted` for the review.
   Then stage that artifact by explicit path (`git add docs/sdd/<slug>/<artifact>.md`) and propose a commit message in the repo's convention; the user commits.
4. **Name the next skill.**
   Recommend a fresh session before `sdd-implement` and between slices of a long task list.
   The files in `docs/sdd/<slug>/` are the handoff.

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

---

## 5. Working files

```
<project root>/docs/sdd/<slug>/
  spec.md     # Outline
  plan.md     # Plan
  tasks.md    # Tasks; also the progress log during Implement
  review.md   # Validate report and PR description draft
```

- **Project root** is the git top-level directory, or the current directory outside git.
- **Slug** is a short kebab-case name for the change.
  It defaults to the current feature branch name.
  When Outline starts on a shared branch, record the intended feature branch with `sdd init <slug> --branch <name>`; `sdd-implement` creates it, and `sdd find` matches the spec to that branch from then on.
- **Tracked by git.**
  The folder is committed on the feature branch, so the pull request carries the spec, plan, tasks and review beside the code, and the history shows when each gate passed.
  Stage an artifact by explicit path at the gates section 4 names and let the user commit; never `git add -A`.
- **Templates** live in `.claude/sdd/templates/` and are generated from this document's appendices by `sdd templates sync`.
  The appendices are canonical, and `sdd templates sync --check` reports drift.
  Every `<...>` placeholder in a template is filled or deleted before approval; `sdd lint` reports any that remain, in every artifact including `review.md`.
- **Lifetime.**
  The folder stays after the merge as the record of the change; delete it only when the user asks.

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
2. **Create the working folder** with `sdd init <slug>` if it doesn't exist, adding `--branch <name>` when you are not on the feature branch yet (section 5).
3. **Ground yourself in the code.**
   Read the project context (section 6).
   Explore the relevant code without changing anything, and identify existing behavior, the patterns to follow and the interfaces to reuse.
   In a large codebase, delegate exploration to subagents and keep only their conclusions.
   Don't move on until you can name the files, interfaces and existing behavior involved.
4. **Interview the user** when the brief is thin.
   Ask about the hard parts: edge cases, failure behavior, trade-offs, constraints, who the work is for and what success looks like.
   Don't ask anything the code can tell you.
   Ask in focused batches.
5. **Draft `spec.md`** from the template (Appendix A), following the rules below.
6. **Check it.**
   Run the readiness checklist and `sdd lint <slug> spec`.
   For medium or larger changes, run an adversarial review in a fresh context.
   That review looks for contradictions, ambiguous terms, hidden dependencies, claims that can't be tested, missing failure modes, and criteria that could pass without meeting the intent.
   Turn what it finds into fixes or clarification markers.
7. **Gate.**
   No clarification markers remain, the checklist passes, and the user approves.
   Record the approval, then name `sdd-plan` as the next step.

### Where a detail belongs

A spec describes behavior and outcomes.
It includes implementation detail only when that detail is a hard constraint, such as "must use the existing auth service" or "data must stay in region X." To decide, ask: would the user or a stakeholder care about this detail, or is it a hard constraint?
If so, it goes in the spec.
Otherwise it goes in the plan.

### Sections

| Section                         | When                     | Contents                                                                      |
| ------------------------------- | ------------------------ | ----------------------------------------------------------------------------- |
| Frontmatter                     | Always                   | Title, slug, branch, status, owner, dates, approval hash, description         |
| Summary                         | Always                   | One paragraph; see the rules below                                            |
| Problem and context             | Always                   | Current state, who is affected and how, evidence with sources                 |
| Goals                           | Always                   | Outcomes, measurable where possible                                           |
| Non-goals                       | Always                   | What is explicitly out of scope                                               |
| User scenarios                  | Medium and larger        | Prioritized stories, each testable on its own                                 |
| Requirements                    | Always                   | Numbered, one behavior each, with acceptance criteria                         |
| Non-functional requirements     | When relevant            | Measurable performance, security, reliability, accessibility and cost targets |
| Invariants                      | When relevant            | Rules that must never break                                                   |
| Edge cases and failure behavior | Always                   | What happens at the boundaries and when things fail                           |
| Existing behavior               | Changes to existing code | What exists today, clearly labeled as not new                                 |
| Assumptions                     | When any exist           | Each assumption and who accepted it                                           |
| Open questions                  | Until resolved           | Clarification markers                                                         |
| Glossary                        | When domain terms appear | Short definitions                                                             |
| Changelog                       | After first approval     | Dated changes and the reason for each                                         |

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

## 8. Phase 2: Plan (`sdd-plan`)

**Purpose:** decide how the approved spec will be built.
**Starts when:** `spec.md` is approved, unchanged since approval, and has no clarification markers.
**Produces:** `plan.md`, approved.

### Steps

1. **Research** anything the plan depends on, such as library versions, API behavior, service limits and pricing.
   Record findings with sources.
   Don't rely on memory for version-specific facts.
2. **Draft `plan.md`** from the template (Appendix B).
3. **Offer options.**
   For each significant decision, present at least two options with trade-offs and a recommendation, and let the user choose.
4. **Name the seams.**
   For each slice, name the boundary its tests will run at, chosen by the seam rules in section 11. The repo's established seam for that kind of code wins over a purer choice.
5. **Check the principles.**
   Mark the plan pass or fail against each project principle, and justify every deviation.
6. **Route spec gaps back.**
   If planning exposes a gap in the spec, stop and route back to `sdd-outline`.
   Don't patch the gap in the plan.
7. **Gate.**
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
- **Affected code:** the files and modules to change or create, and an existing file to use as the pattern.
- **Seams and test strategy:** for each slice, the seam, the test types the repo uses for that kind of code, and how each acceptance criterion becomes a test.
- **Alternatives considered:** each option, and why it was rejected.
- **Trade-offs and risks:** what the team takes on, and how each risk is mitigated.
- **Rollout:** flags, migrations, backfills and rollback.
  Sequence the work as steps that each ship on their own.
- **Traceability:** a table mapping each requirement to its components, seam and tests.
- **Research notes:** facts you verified, with sources.

### Rules

- Every element of the plan traces to a requirement or a constraint.
  Remove anything that doesn't.
- Choose the simplest design that meets the requirements.
  Leave out speculative extension points.
- Reuse existing patterns, and point to a concrete example file.
- Each rollout step must leave the system working and ship on its own.

---

## 9. Phase 3: Tasks (`sdd-task`)

**Purpose:** break the approved plan into small tasks, each one behavior that a red-green loop can build.
**Starts when:** `plan.md` is approved and unchanged since approval.
**Produces:** `tasks.md`, approved.

### Task shape

```
- [ ] T012 [P] Reject registration when the email format is invalid
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
- **Slice close:** end every slice with a close-out item covering the full suite, staging and the user's commit (Appendix C).
- **Seam:** every task names its seam, taken from the plan.
- **Parallel work:** mark a task `[P]` only if it shares no files and no dependencies with the other parallel tasks.
  Never assign the same file to two agents at once.
- **Coverage:** every functional requirement has at least one task, and every task traces to a requirement that is still in force.
  A non-functional requirement or invariant needs a task too, unless the user decides it is verified another way; record that decision under Verified elsewhere (Appendix C) with the ID, how it is verified and who decided.
  `sdd lint` reports an uncovered requirement as an error, and the section sits inside the content hash, so changing an entry after approval counts as a change.
  A task with no requirement means scope creep or a gap in the spec.
- **Done when:** make the check something that runs and returns pass or fail wherever possible.

### Gate

`sdd lint <slug> tasks` passes its traceability checks and the user approves.
Name `sdd-implement` as the next step, and recommend starting it in a fresh session.

---

## 10. Phase 4: Implement (`sdd-implement`)

**Purpose:** build the tasks one at a time, each through the `tdd` discipline, and hand the user one commit per slice.
**Starts when:** `tasks.md` is approved and unchanged since approval, on a feature branch.
**Produces:** code and tests, the user's commits, and `tasks.md` checked off with status `done`.

### Steps

1. **Check the branch.**
   The spec's `branch` field names the feature branch.
   If you're on the default or a shared branch, propose creating it and ask first; if the user picks another name, update the spec's `branch` field, which sits outside the hash.
   If there are uncommitted changes that aren't part of this work, list them and ask what to do.
2. **Resume** at the first unchecked task, and set `tasks.md` to `in-progress`.
3. **For each task:**
   1. Load the task, its requirements, the plan sections it touches and its seam.
      Don't load the whole spec set when it is large.
   2. Build it with the `tdd` skill (section 11).
      The task is the behavior and the plan's seam is the seam.
      Write the failing test first and confirm it fails for the right reason.
      Write only enough code to pass, run the bounded checks, then tidy without changing tests.
   3. Run the task's "Done when" check and show the evidence: the command and its result.
   4. Self-check: list the task's requirements and mark each one met, with evidence, or not met.
   5. Check off the task and add one `- Evidence:` sub-bullet under it with the check and its result, including any appearance assertions removed.
      Record anything you found that's out of scope under Follow-ups.
      Only the checkbox, that single line and the Follow-ups section sit outside the content hash; any other edit changes the approved tasks.
4. **Close each slice:**
   1. Run the full suite once, using the repo's test tiers.
   2. If anything fails, check whether it failed before your changes.
      Stash, rerun and compare, then say which failures were already there.
   3. Stage by explicit path, including `docs/sdd/<slug>/tasks.md` so the progress log lands with the slice.
      Never use `git add -A` or `git add .`.
   4. Propose a commit message that follows the repo's convention.
      Commit only on the user's word.
      Never push.
   5. Check off the slice close-out.
5. **Finish.**
   When every task and slice is checked off, set `tasks.md` to `done` and name `sdd-review` as the next step.

### While working

- **Follow the plan.**
  If the plan turns out to be wrong, stop and propose a change.
  Don't improvise a new architecture.
- **Stay in scope.**
  Record bugs, refactors and ideas as follow-ups instead of acting on them.
- **Follow existing patterns** in the codebase.
- **Never weaken a check to make it pass.**
  Skipping tests, loosening assertions and suppressing errors all require the user's approval.
- **Manage context.**
  On a long task list, use a fresh session for each slice.
  `tasks.md` is your memory, so keep it current.

### Stop and ask when

- The spec doesn't cover the situation.
  Describe the gap, give options with a recommendation, and wait.
- The spec contradicts itself or the code.
  Raise it and don't choose a side.
- A task needs an "Ask first" action.
- The same approach has failed twice.
  Summarize what you learned and consider a fresh session with a better-defined task.

---

## 11. TDD discipline (`tdd`)

The `tdd` skill owns this discipline and stands on its own.
Use it for any change a test can lock down, inside the SDD chain or as a one-shot for a small task.
It knows nothing about SDD: `sdd-implement` and `sdd-review` hand it one behavior at a time.
This section summarizes what SDD relies on; the skill and its repo references are the full version.

- **Read the repo's test reference first,** selected by the repo's git remote.
  It names the commands, the helpers to reuse, and the shape each type of test takes in that repo.
  An unfamiliar repo gets a discovery pass that finds its commands and test shapes before the first test.
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
    The caller names the unit: `sdd-implement` names the task and runs the full suite itself at slice close, `sdd-review` names the fix, and in a one-shot the unit is the whole request.
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

## 12. Phase 5: Validate (`sdd-review`)

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
- **Base branch:** the argument if given, otherwise the repo's default branch.
- **Effort and findings cap:** the argument if given.
  Otherwise ask once, suggesting `high` or `xhigh` with a cap of 3 to 5 scaled to the size of the diff.

### Run

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

Write one report to `review.md` (Appendix D), or to the conversation without a spec, and show it:

- _(spec only)_ Spec conformance: each requirement met or not, with evidence.
- Correctness findings, with severity and `file:line`.
- Standards findings, with the standards line each one fails.
- The standards reviewer's reads-well notes.
- Rejected findings, with the evidence.

Then stop and wait for the user.

### Fixes

The user picks which findings to fix.
Build each fix with `tdd` and validate it with the repo's test tiers.
Stage it by explicit path and propose a commit message, exactly as for a slice; commit only on the user's word.
If the fixes are substantial, offer to rerun the review.

### Confirm intent and close

- Passing tests prove the code matches the spec, not that the spec matched the intent.
  Restate in plain language what was built and ask the user to confirm it's what they meant.
- On the user's acceptance, draft the PR description in `review.md`, or in the conversation without a spec, then set `review.md` to `accepted` with `sdd set-status <slug> review accepted`, which refuses while `sdd lint <slug> review` reports an error, such as a placeholder still in the report.
  The draft has four parts: a summary paragraph following the rules in section 7, what changed, how it was verified (with evidence), and any decisions made and follow-ups.
  Don't push or open the PR unless the user asks.
- _(spec only)_ Stage `docs/sdd/<slug>/review.md` by explicit path and propose its commit message.
  The folder stays as the record of the change.

Nothing is pushed from this phase.

---

## 13. Changing course

- **Behavior changes mid-flight.**
  Update the spec through `sdd-outline` and re-approve it.
  Refresh the plan and tasks once they go stale, then change the code.
- **A bug found during Implement.**
  If the code violates the spec, fix it with `tdd`, starting from a failing test.
  If the spec was wrong or incomplete, route back to `sdd-outline`.
- **Drift.**
  When you touch code the spec covers, check that the spec still describes it.
  If it doesn't, say so before going further.
- **Overlapping specs.**
  When two specs cover the same area, the newer approved spec wins, and it says what it replaces.

---

## 14. Anti-patterns

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
| Unstaged artifacts      | An approved artifact never reaches the branch, so the PR lacks the spec that drove it | Stage `docs/sdd/<slug>/` files by explicit path at every gate   |

---

## 15. Quick reference

**You MUST:**

1. Size the change before writing anything (section 3).
2. Start every SDD skill with the start protocol, and finish with the finish protocol (section 4).
3. Ground yourself in the project context and the relevant code before proposing anything.
4. Write what and why before how, in separate artifacts.
5. Mark every ambiguity with a clarification marker instead of guessing.
6. Stop for the user's approval after the spec, the plan and the tasks.
7. Number every requirement, make each testable, and trace each through the plan, tasks and tests.
8. Build one task at a time through `tdd`, and show evidence for every check.
9. Close each slice with the full suite, staging by explicit path, and a proposed commit message.
10. Validate with `sdd-review`: the evidence, spec conformance, correctness and standards reviews, then confirm intent with the user.

**You MUST NOT:**

1. Start a phase whose upstream artifact is unapproved, changed or stale.
2. Approve, commit or push on the user's behalf.
3. Weaken, skip or delete a check to make it pass.
4. Treat a description of existing behavior as a new requirement.
5. Add abstraction or features that no requirement calls for.
6. Commit on the user's behalf, or stage with `git add -A` instead of by explicit path.

---

## Appendix A: Spec template

```markdown
---
title: <Feature name>
slug: <slug>
branch: <feature branch>
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

<Current state, who is affected and how, and evidence (metrics, incidents, user reports) with sources.>

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

## Appendix B: Plan template

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

## Appendix C: Tasks template

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
- [ ] T002 [P] <one observable behavior>
  - Requirements: FR-002
  - Seam: <from the plan>
  - Files: <paths>
  - Depends on: T001
  - Done when: <check>
- [ ] P1 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## P2: <slice title>

...

## Verified elsewhere

- <ID>: <how it is verified>. Decided by <person>.

## Follow-ups (out of scope)

- <discovery to handle later>
```

## Appendix D: Review report template

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

## Correctness findings

- [<severity>] <file:line>: <finding>

## Standards findings

- <file:line>: <finding>. Fails: "<standards line>"

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
