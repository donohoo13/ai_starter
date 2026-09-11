# Agent Skills Overview

Five skills, one agent, and a spec file carrying a unit of work from interview to done. Each skill is self-contained: nothing chains into anything else, and the user decides when to call each one.

The keystone: ceremony scales with size, engineering discipline never does. A one-line chore still gets a failing test first and a real validation run; what collapses for small work is artifacts, never rigor.

## Skills

- **sdd** (`/sdd <ask>`): the spec-driven development interview. One question at a time, biggest decision first, recommendation attached, facts from the code and sourced research. Three lenses run in parallel, engineering 60%, product 25%, design 15%, and the session always ends by writing `docs/specs/NNN-<slug>.md` at `status: ready`. Pointed at an existing spec, it grills the gap between the file and the code.
- **implement-spec** (`/implement-spec <spec>`): builds a ready spec slice by slice on a worktree or non-main branch: plan, `/tdd`, validate, commit, per slice. Flips the spec `ready` to `in-progress` to `done`, and `done` waits on the human QA gate: the user sees it work before anything is marked finished. Never pushes or opens a PR.
- **tdd**: red before green at pre-agreed public seams, mocks only at true external boundaries, appearance never a test target. Runs under the hood of `implement-spec` and directly whenever a test can lock something down.
- **stage-for-commit**: for small changes that needed no spec. Stages exactly this session's files by explicit path, proves the staged set, and hands back a commit message. Never commits, branches, or pushes.
- **skill-creator**: the authoring discipline for any change under `.claude/skills/`. The `guard-skill-edit` hook denies `Edit` and `Write` there until it loads. Holds every body to 3500 characters, makes the description the trigger, and closes with gut-check prompts for a fresh session.

## Agent

- **research-analyst** (`.claude/agents/`): a background evidence fetcher `sdd` dispatches mid-interview to answer one scoped question with sourced, tiered claims while the conversation continues. Read-only; returns evidence, never advice.

## Rules

`.claude/rules/` holds path-scoped conventions that load on their own when a session reads a matching file: `ux-standards.md` (the usability and accessibility floors every surface meets), `frontend-styling.md` (how this project writes styles), `javascript-typescript.md`, and `transactional-email.md` (which overrides the styling file on email paths). A session that opens no source file, such as `sdd` on a surface-bearing ask, reads `ux-standards.md` by path.

## Spec lifecycle

`docs/specs/NNN-<slug>.md` carries `status: ready` (written by `sdd`), `in-progress`, then `done` (both flipped by `implement-spec`). The spec is the tracker: no GitHub issues, one commit per slice as the audit trail. The template lives at `sdd/assets/spec-template.md` and a worked example at `sdd/references/example-spec.md`.
