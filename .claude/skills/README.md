# Agent Skills Overview

Seven skills, six agents, and a spec file carrying a unit of work from interview to done. Each skill is self-contained: nothing chains into anything else, and the user decides when to call each one.

The keystone: ceremony scales with size, engineering discipline never does. A one-line chore still gets a failing test first and a real validation run; what collapses for small work is artifacts, never rigor.

## Skills

- **sdd** (`/sdd <ask>`): the spec-driven development interview. One question at a time, biggest decision first, recommendation attached, facts from the code and sourced research. Three lenses run in parallel, engineering 60%, product 25%, design 15%, and the session always ends by writing `docs/specs/NNN-<slug>.md` at `status: ready`. Pointed at an existing spec, it grills the gap between the file and the code.
- **implement-spec** (`/implement-spec <spec>`): builds a ready spec on a worktree or non-main branch by orchestrating one fresh `builder` agent per slice, verifying each slice's commit and tests and forwarding its notes to the next.
  Runs the full suite, launches the app for a `render-checker` pass when a surface changed, and flips the spec `ready` to `in-progress` to `built`: working and validated, with no QA script and no `done`.
  Never edits source itself, pushes, or opens a PR.
- **preflight** (`/preflight [spec or intent]`): proves a finished branch is production ready, then opens the PR.
  Syncs with the default branch without ever rewriting published history, runs the `code-reviewer` and `docs-reviewer` agents, fixes local and verifiable findings one commit each, surfaces trunk and intent issues, and validates lint, types, and the full suite.
  Pushes and opens the PR only on the user's yes, gives CI one repair round, and never merges or force-pushes.
- **tdd**: red before green at public seams chosen for the critical paths, needing nothing from the user, mocks only at true external boundaries, appearance never a test target, and every bug fix opening with a failing repro at the lowest seam that shows the bug. Preloaded into the `builder` agent, and used directly whenever a test can lock something down.
- **stage-for-commit**: for small changes that needed no spec. Stages exactly this session's files by explicit path, proves the staged set, and hands back a commit message. Never commits, branches, or pushes.
- **curate-context**: the gate on the prescriptive context files (every `CLAUDE.md` and `CLAUDE.local.md`, `README.md`, `BRANDING.md`, `.claude/rules/`, `docs/standards/`), loaded on any edit to one by its description and the `CLAUDE.md` rule, with no hook behind it. Attributes friction-born candidates, holds an admission bar, routes to the narrowest file, and lands nothing model-invented without approval; zero net growth is the benchmark.
- **brand-init** (`/brand-init`): one and done. Interviews a new project's brand from the bracketed `BRANDING.md` scaffold to a governing doc, opening on a mood-board gate over `docs/branding/moodboard/`, and offers to delete itself once the doc is filled. Later brand changes are edits to `BRANDING.md`, which every brand or surface decision reads first.

## Agents

- **builder** (`.claude/agents/`): builds one spec slice to a working, validated commit in a fresh context with `tdd` preloaded; `implement-spec` dispatches one per slice and one per repair.
  It carries every tool, makes its own judgment calls, and stops only for a major unforeseen issue or a destructive or outward-facing action; a trunk change the spec did not decide goes through `skeptic` and `code-reviewer` and commits alone.
- **render-checker** (`.claude/agents/`): drives the running app to each state of each touched surface, screenshots it at mobile and desktop widths in every shipped theme, measures floors on the rendered page, and returns pass or fail with evidence.
  It inherits the browser tools with every edit tool and `Agent` disallowed, and never touches the server the orchestrator owns.
- **code-reviewer** and **docs-reviewer** (`.claude/agents/`): the adversarial pair `preflight` dispatches in fresh contexts.
  The first reviews a diff or a staged change against its intent, scopes each finding `branch` or `trunk`, and lists the trunk touch points with their consumer counts; the second finds doc statements the diff made false.
  Neither carries an edit tool, both keep `Bash` for `git` and test runs so read-only holds by instruction, and both report with `file:line` evidence, never fixes.
- **skeptic** (`.claude/agents/`): argues whether a staged trunk change the spec did not decide should exist at all, returning `keep`, `revise`, or `drop` with the strongest case against it and a costed alternative.
  A worker making such a change dispatches it beside `code-reviewer`, which owns the defect lens; read-only by the same instruction.
- **research-analyst** (`.claude/agents/`): a background evidence fetcher `sdd` dispatches mid-interview to answer one scoped question with sourced, tiered claims while the conversation continues. Read-only; returns evidence, never advice.

## Standards

`docs/standards/` holds the conventions a change is brought up to, read by path and never loaded on their own.
Each file's `applies-to:` globs name the paths it governs, and a file without the key applies to every change:

- `ux-standards.md`: the usability and accessibility floors every surface meets.
- `frontend-styling.md`: how this project writes styles.
- `html-tables.md`: the markup and CSS floor for a plain `<table>`.
- `transactional-email.md`: email templates, winning over the styling and tables files on email paths.
- `javascript-typescript.md`: tooling, types, and language conventions.
- `agent-facing-output.md`: the output floors for scripts, hooks, and CLIs an agent runs.
- `design-principles.md`: KISS, DRY, YAGNI, deep modules behind small interfaces, and SOLID where a class hierarchy calls for it; it carries no key.

A rule every implementer must hold from the first line, because getting it wrong first costs more than a refactor, lives in `CLAUDE.md` instead.
`.claude/rules/skill-authoring.md` stays a path-scoped rule, loading when a session reads a skill file: the 500-line body ceiling, the description as trigger, and gut-check prompts for a fresh session.

## Spec lifecycle

`docs/specs/NNN-<slug>.md` carries `status: ready` (written by `sdd`), then `in-progress` and `built` (both flipped by `implement-spec`), then `done` once the user confirms QA on the final code.
`built` means working and validated, not yet made right; `implement-spec` resumes only `ready` and `in-progress` specs, so a finished build never reads as half done.
The spec is the tracker: no GitHub issues, one commit per slice as the audit trail. The template lives at `sdd/assets/spec-template.md` and a worked example at `sdd/references/example-spec.md`.
