# Agent Skills Overview

Skills, agents, a document and a helper carrying a unit of work from idea to an accepted pre-PR review.
Each skill is self-contained, and the user decides when to call each one.
The six SDD skills end by naming the next phase as the handoff, and start it only when the user asked for an end-to-end run.

The keystone: ceremony scales with size, engineering discipline never does.
A one-line chore still gets a failing test first and a real validation run; what collapses for small work is artifacts, never rigor.

Headless runs (`claude -p`) of the skills that dispatch agents (`sdd-outline`, `sdd-plan`, `sdd-implement`, `sdd-review`, `render-check`, `design-init`) set `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`, or the session exits after 600s of waiting while a worker is still running.

## Spec-driven development

`.claude/sdd/spec-driven-development.md` is the source of truth for the six phases.
The `sdd-*` skills point into it by section and never restate its rules, and `.claude/sdd/bin/sdd` keeps the state (approvals with content hashes, staleness down the chain, structural lint, templates generated from the appendices) so no skill tracks it by hand.
Working files live in `docs/sdd/<slug>/`, and git decides whether the repository is shared or private.
Shared, because some checkout tracks a file under `docs/sdd/`: they are committed on the feature branch at each gate, so the pull request carries the spec, plan, tasks and review beside the code.
Private, because none does: the helper ignores the folder through `.git/info/exclude`, no spec file is ever staged or committed, and every worktree reads the main checkout's folder.
The skills and agents take the mode and each spec file's path from `sdd status`.
Each spec records its base, the branch its feature branch is cut from and merges back into, which the helper reads from git as the remote's default branch, and `sdd-implement`, `sdd-review` and `render-check` take it from the helper instead of working out a default branch.
[`.claude/sdd/README.md`](../sdd/README.md) explains the helper and how to change the document.

- **sdd-outline** (`/sdd-outline [slug] [brief]`): phase 1, an idea to an approved `spec.md`.
  Sizes the change first and sends trivial or small work to `tdd` instead, grounds in the code read-only, plays the problem back and waits for the user to confirm it, interviews in batches of coupled questions with a recommendation each, drafts numbered requirements with acceptance criteria and the UI surfaces the spec touches, runs an adversarial review in a fresh subagent, and gates on the user's approval; when a UI surface is listed, it offers `sdd-design` or records a skip on the user's word.
- **sdd-design** (`/sdd-design [slug] [Design artifact link]`): phase 2, optional, for a spec whose UI surfaces section lists a surface.
  Writes a standalone Claude Design prompt from the spec into `design.md` for the user to run in a separate design conversation, records a skip or cancel, reads the approved Design artifact's link into a saved snapshot under `design/`, puts each surface or state the design misses and each thing it adds to the user, and approves on the user's word, so the plan builds on the approved design.
  It never runs the design conversation itself.
- **sdd-plan** (`/sdd-plan [slug]`): phase 3, an approved spec, and its approved design when there is one, to an approved `plan.md`.
  Asks whether to run `sdd-design` or skip it when a UI spec has no `design.md`, then researches with sources (`research-analyst` for a question that would stall the conversation), presents each significant decision as options with a recommendation, names the seam each slice's tests run at in the vocabulary `tdd` discovers for the repo, checks the plan against `CLAUDE.md` and `docs/standards/`, and fills the traceability table.
- **sdd-task** (`/sdd-task [slug]`): phase 4, an approved plan to an approved `tasks.md`.
  One observable behavior per task with its requirements, seam, files and done-when check, grouped into slices that each end in a close-out, which a revision reopens when it adds or changes a task in a built slice; a requirement the user verifies another way is recorded under Verified elsewhere, inside the content hash.
- **sdd-implement** (`/sdd-implement [slug]`): phase 5, the session orchestrates and a fresh `implementer` builds each slice from a pointer-only brief.
  Asks at the start which UI surfaces get a render check, with a recommendation and reason each, and dispatches `render-checker` once before QA for the surfaces the user picked.
  Brings every `BLOCKED` question to the user (with `skeptic`'s case first for an undecided trunk change), verifies each report with its own checks, commits each verified slice, runs one QA pass before `tasks.md` reaches `done`, and recommends `/sdd-review` next in the same session, starting it only on an end-to-end request; offers the worktree helpers when the checkout should stay on the branch it is on, and never commits on the spec's base.
  Keeps the spec's journal through `sdd journal`, holding each agent report, each question it stops on with the user's answer, and a `resolved` entry with the commit that settles them, so a session that ended mid-build is resumed from `tasks.md`, the journal and `git status` alone.
- **sdd-review** (`/sdd-review [slug] [effort] [--max-findings n] [base]`): phase 6, and the pre-PR review of any branch.
  Every reviewer runs in a fresh context on a pointer-only brief, so it can run in the session that built the branch.
  With a spec: evidence from the suite, spec conformance in a fresh subagent, Claude Code's `/code-review` (a forked skill) for correctness beside `standards-reviewer` for legibility and usability, one `review.md` report, fixes on the user's pick built by a fresh `implementer`, and a PR description draft once the user confirms the intent; without a spec, the two reviews and the same report in the conversation.
  `review.md` records each finding's disposition, so a later session resumes an open review from the file instead of running the reviewers again.
  Reopens an accepted review when the tasks were re-approved after it, or on the user's word for pull request feedback, which goes through the same triage and fixes.
  Never pushes or opens the PR.
- **tdd**: red before green at public seams chosen for the critical paths, discovering the repo's commands and test shapes from its own files first, mocks only at true external boundaries, appearance never a test target, and every bug fix opening with a failing repro at the lowest seam that shows it.
  Preloaded into `implementer`, which runs it per task and per fix, and used directly whenever a test can lock something down.

## Other skills

- **render-check** (`/render-check [surfaces] [--base <ref>]`): user-only, since a pass is slow and token-heavy; `sdd-implement` runs its own pass before QA.
  Finds the touched surfaces since the merge-base with `--base` or the base the helper reports, or takes them from the argument, owns the app server, dispatches `render-checker` with the WCAG 2.2 AA floors, `DESIGN.md` or the standards' starting values, and any recorded design as the bar, and reports pass or fail per surface, width and theme without fixing anything.
- **stage-for-commit**: for small changes that needed no spec. Stages exactly this session's files by explicit path, proves the staged set, and hands back a commit message. Never commits, branches, or pushes, and never stages a file git ignores.
- **curate-context**: the gate on the prescriptive context files (every `CLAUDE.md` and `CLAUDE.local.md`, `README.md`, `DESIGN.md`, `.claude/rules/`, `docs/standards/`), loaded on any edit to one by its description and the `CLAUDE.md` rule, with no hook behind it. Attributes friction-born candidates, holds an admission bar, routes to the narrowest file, and lands nothing model-invented without approval; zero net growth is the benchmark.
  On `DESIGN.md` it refuses a value below its WCAG 2.2 AA floor, and after an approved edit offers a warned re-sync of the project's Design System in Claude.
- **design-init** (`/design-init`): writes `DESIGN.md` from the template it carries in `references/`, taking the company overview as the authority, plus the user's context, an optional reference `DESIGN.md` whose structure it carries over without its brand, and the optional mood board at `docs/design/moodboard/`.
  Briefs the structure first, decides identity in five rounds of recommended answers, finishes only when `pnpm exec designmd lint DESIGN.md` is clean and its own residue checks pass, and offers to build or re-sync the project's Design System in Claude.
  A filled `DESIGN.md` is revised only on the user's word; while it is absent or still holds bracket placeholders, the standards' starting values apply and brand decisions are undecided.

## Agents

- **implementer** (`.claude/agents/`): builds one slice of an approved `tasks.md`, or one QA bug or review fix, with `tdd` preloaded and a model pinned; `sdd-implement` dispatches it fresh per slice and `sdd-review` per picked finding, resuming it with the user's answers.
  It builds each task red-first, checks its diff against the matching `docs/standards/` files, stops with `BLOCKED` only for a behavior gap, a contradiction, an "Ask first" action, a repeated failure or an undecided trunk change, records its report in the spec's journal during a build, takes over uncommitted paths its brief hands it, and never commits.
- **render-checker** (`.claude/agents/`): drives the running app to each state of each surface it is given, screenshots it at mobile and desktop widths in every shipped theme, measures floors on the rendered page, and returns pass or fail with evidence.
  `render-check` dispatches it for a pass the user starts and `sdd-implement` once before QA; it inherits the browser tools with every edit tool and `Agent` disallowed, and never starts or stops the app server.
- **standards-reviewer** (`.claude/agents/`): the legibility and usability reviewer `sdd-review` dispatches beside `/code-review`.
  It judges a branch diff only against `CLAUDE.md` and the `docs/standards/` files its paths match, leaves correctness to the other reviewer, and reports findings that quote the standards line each fails, plus what the change does well; read-only by the same instruction.
- **skeptic** (`.claude/agents/`): argues whether a proposed trunk change the spec did not decide should exist at all, returning `keep`, `revise`, or `drop` with the strongest case against it and a costed alternative.
  `sdd-implement` dispatches it before putting the change to the user; read-only by the same instruction.
- **research-analyst** (`.claude/agents/`): a background evidence fetcher `sdd-plan` and `design-init` dispatch to answer one scoped question with sourced, tiered claims while the conversation continues, using Context7 IDs the brief pins. Read-only; returns evidence, never advice.

## Standards

`docs/standards/` holds the conventions a change is brought up to, read by path by the agents that judge code (`implementer` in its self-check, `standards-reviewer`, and `render-checker` for the UX floors) and never loaded on their own.
Each file's `applies-to:` globs name the paths it governs, and a file without the key applies to every change:

- `ux-standards.md`: the WCAG 2.2 AA floors every surface meets, and the starting values `DESIGN.md` may change.
- `frontend-styling.md`: how this project writes styles.
- `html-tables.md`: the markup and CSS floor for a plain `<table>`.
- `transactional-email.md`: email templates, winning over the styling and tables files on email paths.
- `javascript-typescript.md`: tooling, types, and language conventions.
- `ruby.md`: Ruby tooling, RBS types, and language conventions, plus Rails rules where the project uses Rails.
- `agent-facing-output.md`: the output floors for scripts, hooks, and CLIs an agent runs.
- `code-legibility.md`: names, function size, control flow, and tests that read as specifications, whatever the language; it carries no key.
- `design-principles.md`: KISS, DRY, YAGNI, deep modules behind small interfaces, and SOLID where a class hierarchy calls for it; it carries no key.

A rule every implementer must hold from the first line, because getting it wrong first costs more than a refactor, lives in `CLAUDE.md` instead.
`.claude/rules/skill-authoring.md` stays a path-scoped rule, loading when a session reads a skill file: bodies as long as their job needs, the description as trigger, and gut-check prompts for a fresh session.

## SDD lifecycle

`docs/sdd/<slug>/` holds `spec.md`, `plan.md` and `tasks.md`, each `draft` until the user approves it (`approved`, with its approval hash recorded), `tasks.md` moving to `in-progress` and `done` under `sdd-implement`, and `review.md` moving from `open` to `accepted` under `sdd-review`, and back to `open` when the tasks are re-approved or feedback arrives after acceptance.
A spec with UI surfaces adds `design.md`, `requested`, `approved` or `skipped` under `sdd-design`, with the approved design's snapshot under `design/`.
An approved artifact edited afterwards counts as changed and everything downstream as stale, and `.claude/sdd/bin/sdd status` names the phase and the skill to run.
The folder is the tracker: no GitHub issues, one commit per slice as the audit trail, and, in a shared repository, each artifact committed beside the code at the gate that approved it.
