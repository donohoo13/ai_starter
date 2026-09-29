# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Company/Project Overview

[one-line summary of what this product is and for whom]

The full company perspective lives in [docs/company/company-overview.md](./docs/company/company-overview.md): read it when work needs product, customer, or company context. It is narrative only; no rules live there.

- Commands can be found in root package.json

## Standards

- Commit messages: 50-char subject in imperative mood, explain WHY in body.
- Never attempt to estimate or project the concept of time.
- During conversations sacrifice grammar and story-telling for concision while maintaining clear and coherent thoughts and opinions.
- Expressing and communicating ideas should always be expressed with simple and clear grammar.
- Quality of prose should be prioritized when adding to text based content by rewriting whole points, paragraphs, or documents when append only additions would degrade the underlying readability of the information.
- Memory from previous conversations is a hint, not ground truth: verify any remembered file, command, or convention against the current code or with the user before acting on it.
- Use LSP tools for code navigation, symbol searches, and diagnostics; fall back to terminal commands when a real LSP call reports the file type unsupported, not before.
- Read [BRANDING.md](BRANDING.md) before any brand or surface decision, then follow it. It is not imported, so it is not in context until a session opens it; the one-time `brand-init` skill fills it on a new project. The UI/UX floors live in the `.claude/rules/` files named under Frontend and UI below and load on their own when a session reads a matching file; a session that opens no source file reads `ux-standards.md` by path before deciding anything about a surface.
- Confirm with the user to address root causes, not symptoms.
- Evidence before completion claims: do not state something passes, builds, is fixed, or was checked and found clean without running the command that proves it or directing the user to run guided QA steps to confirm the fix.
- No em-dashes (U+2014) in customer-facing text (UI, emails, marketing, AI prompts). Use commas, periods, or rephrasing instead. Hyphens (U+002D) and en-dashes (U+2013) are fine. Internal dev artifacts (code comments, CLAUDE.md, PRs) exempt.

### Development

- Never leave stubs, TODO comments, or placeholder logic in delivered code unless explicitly asked to scaffold. Finish the implementation.
- Write a comment only when it prevents a dangerous action, or caches a fact that costs multiple discovery jumps through files or symbols to reconstruct — or that no file in the repo can answer at all — stated in one line.
- Do not leave dead or orphaned code in the codebase.
- Start dev servers only through `pnpm dev` run as a background task, never a framework binary directly: it exits early with the running pid when a server is already up and mirrors output to `.logs/dev-server.log`, the file to read for server logs.

#### Python

- Always run Python through `uv` (`uv run …`, `uv add …`) — never a bare `python3`, `pip`, or an activated venv — so the env syncs from `uv.lock` first.
- Use `ruff` for lint/format.

#### Javascript/Typescript/Node.js

- [`.claude/rules/javascript-typescript.md`](.claude/rules/javascript-typescript.md)

#### Frontend and UI

- [`.claude/rules/ux-standards.md`](.claude/rules/ux-standards.md)
- [`.claude/rules/frontend-styling.md`](.claude/rules/frontend-styling.md)
- [`.claude/rules/html-tables.md`](.claude/rules/html-tables.md)
- [`.claude/rules/transactional-email.md`](.claude/rules/transactional-email.md)

### Git Control

- Use CLI tools (like `gh` for GitHub) for PR, issue, and remote repository management; fall back to raw git only when no CLI covers the operation.
- Commit only from a non-main branch: check `git branch --show-current` before every commit and branch first when on `main`.
- Branches are named `<type>/<kebab-slug>` (`type`: `feature` | `bug` | `chore`).
- `implement-spec` builds run in a dedicated git worktree — `scripts/setup/gwt-add.sh --no-open <branch>` creates it, the native `EnterWorktree` tool relocates the session into it — so the main checkout stays on `main`; declining the skill's one confirm falls back to a plain feature branch. Post-merge cleanup is `scripts/setup/gwt-remove.sh <branch>` from the main checkout.

### Markdown

- Keep bullet points and long descriptions as single continuous lines (no line breaks within a bullet); one bullet per line keeps cuts, moves, and diffs atomic.
- Escape literal pipes in table cells as `\|`, including inside backticks: `|` separates columns regardless of code spans, so `` `a || b` `` silently adds phantom columns.
- Use a list rather than a table when cells run past about one line; long-form content reads better and cannot break the table grammar.

## Skills

- Six skills, each self-contained and user-invoked: `sdd` interviews and writes a spec to `docs/specs/`, `implement-spec` builds one, `tdd` is the test-first discipline under any build, `stage-for-commit` hands back a commit for small changes that needed no spec, `curate-context` governs context-file edits, and `brand-init` fills `BRANDING.md` once on a new project. Nothing chains into anything else; the user decides when to call each one. The map is [the skills README](.claude/skills/README.md).
- Any create, edit, rename, or delete under `.claude/skills/` follows [`.claude/rules/skill-authoring.md`](.claude/rules/skill-authoring.md), which holds every body to 5000 characters excluding frontmatter; it loads on its own when a skill file is read, so a session creating a skill or deleting one through Bash reads it by path first.
- Any edit to a `CLAUDE.md`, `CLAUDE.local.md`, `README.md`, `BRANDING.md`, or `.claude/rules/` file loads `curate-context` first; no hook enforces this, so this rule and the skill's description are the whole mechanism.

## Data handling

- Logs never carry secrets, credentials, or customer PII; payloads and debug detail are fine once scrubbed of those. Security-relevant events (auth, CRUD on org-scoped objects, security settings changes) log: user id, IP, timestamp, action, object.
- Production or customer data never enters fixtures or test environments without anonymization.
- Restricted material (keys, secrets, vulnerability and pentest reports) never leaves the machine: not into external services, artifacts, or issue trackers.

## Deployment

[deployment targets, environments, and release process]
