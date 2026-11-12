# AGENTS.md

## Project

[one-line summary of what this product is and for whom]

The full company perspective lives in [docs/company/company-overview.md](./docs/company/company-overview.md): read it when work needs product, customer, or company context.
It is narrative only; no rules live there.

## Commands and stack

- Commands are the scripts in the root `package.json`.
- Start dev servers only through `pnpm dev` run as a background task, never a framework binary directly: it exits early with the running pid when a server is already up and mirrors output to `.logs/dev-server.log`, the file to read for server logs.
- Use pnpm only: local bins run through `pnpm exec` and one-off Node through `pnpm exec node`, so both run on the pinned runtime; `npx` and `pnpm dlx` are denied to AI sessions, so hand the user a ready-to-run `pnpm dlx` command for a one-off remote tool.
- Retarget the Node pin as a set (`.nvmrc` exact, `engines.node` as `>=X.Y.Z <X+1`, `devEngines.runtime.version` exact), then `pnpm install` and commit the lockfile; read `scripts/setup/check-install.mjs`'s header before changing how the pin works, and move pnpm activation off Corepack in the same change when the target is Node 25 or newer.
- Run Python through `uv` (`uv run …`, `uv add …`), never a bare `python3`, `pip` or an activated venv, so the env syncs from `uv.lock` first; lint and format with `ruff`.

## Design and standards

- Read `DESIGN.md` before any brand or surface decision, then follow it; it is not in context until a session opens it.
  While it is absent or still holds bracket placeholders, brand decisions are undecided until the `design-init` skill writes it.
- This project's own conventions (Tailwind, tooling, email client support) are in `docs/standards/stack.md`.
- Build an email template as nested tables with inline styles in a `600px` column from the first line: a template started in flex or grid is a rewrite, not a refactor.

## Git

- Commit only from a non-main branch: check `git branch --show-current` before every commit and branch first when on `main`.
  `.husky/pre-commit` and `.husky/pre-push` refuse commits on and pushes to the default branch.
- Branches are named `<type>/<kebab-slug>` (`type`: `feature` | `bug` | `chore`).
- `scripts/setup/gwt-add.sh --no-open <branch>` prepares a worktree by copying the local env files into it and installing its dependencies; `scripts/setup/gwt-remove.sh <branch>`, run from the main checkout, removes it after the merge.
- Specs are committed: `docs/sdd/` is tracked.

## Data handling

- Security-relevant events (auth, CRUD on org-scoped objects, security settings changes) log the user id, IP, timestamp, action and object.

## Deployment

[deployment targets, environments, and release process]
