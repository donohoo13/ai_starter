# Changelog

Template releases, newest first.
Each entry carries three parts: **what** changed, **why**, and **adaptation notes** for projects whose setup diverges from the shipped defaults.
A release is a git tag (`vX.Y.Z`) on `main` matching the entry heading.
In a project created from the template, this file is template residue: delete it.

## v0.1.0 — unreleased

- **What**: the baseline.
  Versioning restarts here; every earlier tag is retired and earlier history lives only in git.
  The payload as of this entry:
  - **Skills** (`.claude/skills/`): `sdd` interviews and writes a spec to `docs/specs/`, `implement-spec` builds it slice by slice behind a human QA gate, `preflight` proves a finished branch through adversarial code and docs review and full validation before opening its PR, `tdd` holds the test-first discipline and needs nothing from the user, choosing its own seams and allowing tests to be restructured but never weakened in a refactor, `stage-for-commit` hands back a commit for small changes, `curate-context` governs context-file edits, and `brand-init` fills `BRANDING.md` once.
  - **Agents** (`.claude/agents/`): `code-reviewer` and `docs-reviewer` for `preflight`, and `research-analyst` for `sdd`.
  - **Rules** (`.claude/rules/`): skill authoring, a path-scoped rule that caps a skill body at 500 lines.
    Implementer-critical rules (pnpm only, the Node pin, email templates built to their standard from the first line) are condensed into `CLAUDE.md`.
  - **Standards** (`docs/standards/`): UX floors, frontend styling, HTML tables, transactional email, JavaScript and TypeScript, agent-facing script output, and design principles, each scoped by `applies-to:` globs and read by path rather than auto-loaded, so standards reach the code at judgment time instead of crowding every implementing session; `rules-frontmatter.battery.mjs` checks both scopes.
  - **Guards**: `guard-main` keeps AI commits and pushes off the default branch, `guard-secret-read` keeps secret files out of commands, and `.claude/settings.json` carries the permission and secrets registry.
  - **Toolchain**: pnpm and Turborepo, with Node and pnpm pinned in `.nvmrc` and `package.json` and read by mise through a version-free `mise.toml`; the `preinstall` guard enforces the pins.
  - **CI**: one `checks` job on every PR and push to `main` running `format:check`, `lint`, `typecheck`, `test`, and `test:scripts`.
  - **Context**: `CLAUDE.md`, a bracketed `BRANDING.md` scaffold, and a four-section PR template.
- **Why**: the template changed so much across its earlier versions that walking their entries no longer helps anyone adopt it, so it restarts at a pre-stable 0.x that says breaking changes may land in any minor release.
- **Adaptation notes**: a project created from any earlier version re-adopts from this baseline rather than applying old entries one by one.
