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
- Read [BRANDING.md](BRANDING.md) before any brand or surface decision, then follow it. It is not imported, so it is not in context until a session opens it; the one-time `brand-init` skill fills it on a new project.
- Confirm with the user to address root causes, not symptoms.
- Evidence before completion claims: do not state something passes, builds, is fixed, or was checked and found clean without running the command that proves it or directing the user to run guided QA steps to confirm the fix.
- No em-dashes (U+2014) in customer-facing text (UI, emails, marketing, AI prompts). Use commas, periods, or rephrasing instead. Hyphens (U+002D) and en-dashes (U+2013) are fine. Internal dev artifacts (code comments, CLAUDE.md, PRs) exempt.

### Development

- Never leave stubs, TODO comments, or placeholder logic in delivered code unless explicitly asked to scaffold. Finish the implementation.
- Start every bug fix by reproducing the bug the way a user hits it, and confirm the reproduction fails for the reported reason before changing code.
- Write a comment only when it prevents a dangerous action, or caches a fact that costs multiple discovery jumps through files or symbols to reconstruct — or that no file in the repo can answer at all — stated in one line.
- Do not leave dead or orphaned code in the codebase.
- Start dev servers only through `pnpm dev` run as a background task, never a framework binary directly: it exits early with the running pid when a server is already up and mirrors output to `.logs/dev-server.log`, the file to read for server logs.

#### Python

- Always run Python through `uv` (`uv run …`, `uv add …`) — never a bare `python3`, `pip`, or an activated venv — so the env syncs from `uv.lock` first.
- Use `ruff` for lint/format.

#### Javascript/Typescript/Node.js

- Use pnpm only: local bins run through `pnpm exec` and one-off Node through `pnpm exec node`, so both run on the pinned runtime; `npx` and `pnpm dlx` are denied to AI sessions, so hand the user a ready-to-run `pnpm dlx` command for a one-off remote tool.
- Retarget the Node pin as a set (`.nvmrc` exact, `engines.node` as `>=X.Y.Z <X+1`, `devEngines.runtime.version` exact), then `pnpm install` and commit the lockfile; read `scripts/setup/check-install.mjs`'s header before changing how the pin works, and move pnpm activation off Corepack in the same change when the target is Node 25 or newer.

#### Frontend and UI

- Build email templates to `docs/standards/transactional-email.md` from the first line: email clients force nested tables, inline styles, and a `600px` column, so a template started in flex or grid is a rewrite, not a refactor.

### Git Control

- Use CLI tools (like `gh` for GitHub) for PR, issue, and remote repository management; fall back to raw git only when no CLI covers the operation.
- Commit only from a non-main branch: check `git branch --show-current` before every commit and branch first when on `main`.
- Branches are named `<type>/<kebab-slug>` (`type`: `feature` | `bug` | `chore`).
- `implement-spec` builds run in a dedicated git worktree — `scripts/setup/gwt-add.sh --no-open <branch>` creates it, the native `EnterWorktree` tool relocates the session into it — so the main checkout stays on `main`; declining the skill's one confirm falls back to a plain feature branch. Post-merge cleanup is `scripts/setup/gwt-remove.sh <branch>` from the main checkout.

### Markdown

- Put each sentence on its own physical line when writing or substantially editing Markdown, so a diff names the exact sentence that changed.
  A bullet with several sentences continues on indented lines beneath its marker.
  Leave passages you are not editing in their existing format rather than reflowing them.
- Escape literal pipes in table cells as `\|`, including inside backticks: `|` separates columns regardless of code spans, so `` `a || b` `` silently adds phantom columns.
- Use a list rather than a table when cells run past about one line; long-form content reads better and cannot break the table grammar.

## Skills

- Ten skills, each self-contained and user-invoked: `sdd` interviews and writes a spec to `docs/specs/`, `implement-spec` builds one to `built`, `refine` brings any branch up to the standards in `docs/standards/` and runs human QA, `preflight` proves a finished branch through adversarial code and docs review and full validation before opening its PR, `tdd` is the test-first discipline under any build, `stage-for-commit` hands back a commit for small changes that needed no spec, `curate-context` governs context-file edits, `brand-init` fills `BRANDING.md` once on a new project, and `template-sync` and `template-feedback` pull newer template releases in through `.ai-starter.yaml` and report template defects back. Nothing chains into anything else; the user decides when to call each one. The map is [the skills README](.claude/skills/README.md).
- Any create, edit, rename, or delete under `.claude/skills/` follows [`.claude/rules/skill-authoring.md`](.claude/rules/skill-authoring.md), which caps every body at 500 lines excluding frontmatter; it loads on its own when a skill file is read, so a session creating a skill or deleting one through Bash reads it by path first.
- Any edit to a `CLAUDE.md`, `CLAUDE.local.md`, `README.md`, `BRANDING.md`, `.claude/rules/`, or `docs/standards/` file loads `curate-context` first; no hook enforces this, so this rule and the skill's description are the whole mechanism.

## Data handling

- Logs never carry secrets, credentials, or customer PII; payloads and debug detail are fine once scrubbed of those. Security-relevant events (auth, CRUD on org-scoped objects, security settings changes) log: user id, IP, timestamp, action, object.
- Production or customer data never enters fixtures or test environments without anonymization.
- Restricted material (keys, secrets, vulnerability and pentest reports) never leaves the machine: not into external services, artifacts, or issue trackers.

## Deployment

[deployment targets, environments, and release process]
