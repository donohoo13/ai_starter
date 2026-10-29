# Agent Skills Overview

Twelve skills, six agents, a document and a helper carrying a unit of work from idea to an accepted pre-PR review.
Each skill is self-contained: nothing starts another, and the user decides when to call each one.
The five SDD skills end by naming the next phase as the handoff, and still never start it.

The keystone: ceremony scales with size, engineering discipline never does.
A one-line chore still gets a failing test first and a real validation run; what collapses for small work is artifacts, never rigor.

Headless runs (`claude -p`) of the skills that dispatch agents (`sdd-outline`, `sdd-plan`, `sdd-review`, `refine`) set `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`, or the session exits after 600s of waiting while a worker is still running.

## Spec-driven development

`.claude/sdd/spec-driven-development.md` is the source of truth for the five phases.
The `sdd-*` skills point into it by section and never restate its rules, and `.claude/sdd/bin/sdd` keeps the state (approvals with content hashes, staleness down the chain, structural lint, templates generated from the appendices) so no skill tracks it by hand.
Working files live in `docs/sdd/<slug>/` and are committed on the feature branch at each gate, so the pull request carries the spec, plan, tasks and review beside the code.
[`.claude/sdd/README.md`](../sdd/README.md) explains the helper and how to change the document.

- **sdd-outline** (`/sdd-outline [slug] [brief]`): phase 1, an idea to an approved `spec.md`.
  Sizes the change first and sends trivial or small work to `tdd` instead, grounds in the code read-only, interviews in batches of coupled questions with a recommendation each, drafts numbered requirements with acceptance criteria, runs an adversarial review in a fresh subagent, and gates on the user's approval.
- **sdd-plan** (`/sdd-plan [slug]`): phase 2, an approved spec to an approved `plan.md`.
  Researches with sources (`research-analyst` for a question that would stall the conversation), presents each significant decision as options with a recommendation, names the seam each slice's tests run at in the vocabulary `tdd` discovers for the repo, checks the plan against `CLAUDE.md` and `docs/standards/`, and fills the traceability table.
- **sdd-task** (`/sdd-task [slug]`): phase 3, an approved plan to an approved `tasks.md`.
  One observable behavior per task with its requirements, seam, files and done-when check, grouped into slices that each end in a close-out; a requirement the user verifies another way is recorded under Verified elsewhere, inside the content hash.
- **sdd-implement** (`/sdd-implement [slug]`): phase 4, the tasks built one at a time, each through `tdd` in the session.
  Closes every slice with the full suite, staging by explicit path with the progress log included and a proposed commit, keeps `tasks.md` current so a fresh session resumes at the right item, and offers the worktree helpers when the main checkout should stay on the default branch.
- **sdd-review** (`/sdd-review [slug] [effort] [--max-findings n] [base]`): phase 5, and the pre-PR review of any branch.
  With a spec: evidence from the suite, spec conformance in a fresh subagent, Claude Code's `/code-review` for correctness beside `standards-reviewer` for legibility and usability, one `review.md` report, fixes on the user's pick, and a PR description draft once the user confirms the intent; without a spec, the two reviews and the same report in the conversation.
  Never pushes or opens the PR.
- **tdd**: red before green at public seams chosen for the critical paths, discovering the repo's commands and test shapes from its own files first, mocks only at true external boundaries, appearance never a test target, and every bug fix opening with a failing repro at the lowest seam that shows it.
  Run by `sdd-implement` per task and by `sdd-review` per fix, preloaded into `refiner`, and used directly whenever a test can lock something down.

## Other skills

- **refine** (`/refine [spec or intent] [--base <ref>]`): makes a working branch right, with or without a spec, and never stops at a gate.
  Discovers the change from the merge-base with the default branch, or with the `--base` ref a stacked branch names, and its intent without asking, commits any uncommitted work as a baseline, and dispatches a fresh `refiner`; verifies the suite and that the refiner's test table matches its commits, and runs a `render-checker` pass with the UX floors when a surface changed.
  Hands over one QA script with the app running, and never pushes or opens a PR; it fits between `sdd-implement` and `sdd-review` when a built branch should be brought up to the standards first.
- **stage-for-commit**: for small changes that needed no spec. Stages exactly this session's files by explicit path, proves the staged set, and hands back a commit message. Never commits, branches, or pushes.
- **curate-context**: the gate on the prescriptive context files (every `CLAUDE.md` and `CLAUDE.local.md`, `README.md`, `DESIGN.md`, `.claude/rules/`, `docs/standards/`), loaded on any edit to one by its description and the `CLAUDE.md` rule, with no hook behind it. Attributes friction-born candidates, holds an admission bar, routes to the narrowest file, and lands nothing model-invented without approval; zero net growth is the benchmark.
- **design-init** (`/design-init`): one and done. Interviews a new project's brand from the bracketed `DESIGN.md` scaffold to a governing doc, opening on a mood-board gate over `docs/design/moodboard/`, and offers to delete itself once the doc is filled and `pnpm exec designmd lint DESIGN.md` is clean. Later brand changes are edits to `DESIGN.md`, which every brand or surface decision reads first.

## Agents

- **refiner** (`.claude/agents/`): brings a working change up to the `docs/standards/` files its paths match, with `tdd` preloaded; `refine` dispatches it and resumes it with render findings and QA issues.
  It audits one standard at a time, pins required behavior at consumption seams, refactors code and tests one concern per commit without weakening a test, and proves every test it touched by deliberately breaking the behavior; a trunk change the spec did not decide goes through `skeptic` and `code-reviewer` and commits alone.
- **render-checker** (`.claude/agents/`): drives the running app to each state of each touched surface, screenshots it at mobile and desktop widths in every shipped theme, measures floors on the rendered page, and returns pass or fail with evidence.
  It inherits the browser tools with every edit tool and `Agent` disallowed, and never touches the server the orchestrator owns.
- **code-reviewer** (`.claude/agents/`): the defect lens on a staged trunk change the spec did not decide; `refiner` dispatches it beside `skeptic` and sends it one re-review of the fixes.
  It carries no edit tool and keeps `Bash` for `git` and test runs so read-only holds by instruction, and reports with `file:line` evidence, never fixes.
- **standards-reviewer** (`.claude/agents/`): the legibility and usability reviewer `sdd-review` dispatches beside `/code-review`.
  It judges a branch diff only against `CLAUDE.md` and the `docs/standards/` files its paths match, leaves correctness to the other reviewer, and reports findings that quote the standards line each fails, plus what the change does well; read-only by the same instruction.
- **skeptic** (`.claude/agents/`): argues whether a staged trunk change the spec did not decide should exist at all, returning `keep`, `revise`, or `drop` with the strongest case against it and a costed alternative.
  `refiner` dispatches it beside `code-reviewer`, which owns the defect lens; read-only by the same instruction.
- **research-analyst** (`.claude/agents/`): a background evidence fetcher `sdd-plan` dispatches to answer one scoped question with sourced, tiered claims while the conversation continues, using Context7 IDs the brief pins. Read-only; returns evidence, never advice.

## Standards

`docs/standards/` holds the conventions a change is brought up to, read by path by the agents that judge code (`refiner`, `code-reviewer`, `standards-reviewer`, and `render-checker` for the UX floors) and never loaded on their own.
Each file's `applies-to:` globs name the paths it governs, and a file without the key applies to every change:

- `ux-standards.md`: the usability and accessibility floors every surface meets.
- `frontend-styling.md`: how this project writes styles.
- `html-tables.md`: the markup and CSS floor for a plain `<table>`.
- `transactional-email.md`: email templates, winning over the styling and tables files on email paths.
- `javascript-typescript.md`: tooling, types, and language conventions.
- `agent-facing-output.md`: the output floors for scripts, hooks, and CLIs an agent runs.
- `code-legibility.md`: names, function size, control flow, and tests that read as specifications, whatever the language; it carries no key.
- `design-principles.md`: KISS, DRY, YAGNI, deep modules behind small interfaces, and SOLID where a class hierarchy calls for it; it carries no key.

A rule every implementer must hold from the first line, because getting it wrong first costs more than a refactor, lives in `CLAUDE.md` instead.
`.claude/rules/skill-authoring.md` stays a path-scoped rule, loading when a session reads a skill file: the 500-line body ceiling, the description as trigger, and gut-check prompts for a fresh session.

## SDD lifecycle

`docs/sdd/<slug>/` holds `spec.md`, `plan.md` and `tasks.md`, each `draft` until the user approves it (`approved`, with its content hash recorded), `tasks.md` moving to `in-progress` and `done` under `sdd-implement`, and `review.md` moving from `open` to `accepted` under `sdd-review`.
An approved artifact edited afterwards counts as changed and everything downstream as stale, and `.claude/sdd/bin/sdd status` names the phase and the skill to run.
The folder is the tracker: no GitHub issues, one commit per slice as the audit trail, and each artifact committed beside the code at the gate that approved it.
