# Changelog

Template releases, newest first.
Each entry carries three parts: **what** changed, **why**, and **adaptation notes** for projects whose setup diverges from the shipped defaults.
A release is a git tag (`vX.Y.Z`) on `main` matching the entry heading.
In a project created from the template, this file is template residue: delete it.

## v0.2.0 — unreleased

- **What**:
  - `sdd` opens with a read-only reconnaissance that presents a touch map before the first question, then interviews in rounds of three or four coupled questions instead of one per turn.
    Its lenses run in order, product, engineering, then design, in place of the weighted parallel lenses, and every lens is accounted for: Product and Design keep a one-line disposition when they do not apply.
    The spec template drops the `†` user-driven marker, adds a blast-radius line to Architecture, renames `References` to `Touch Map` with each path's role, current shape, and risk, and moves `Sources` under `Evidence`.
    `implement-spec` and `refine` run the render pass for a spec whose Design Requirements name a surface rather than a one-line disposition, and `builder` plans against the Touch Map.
  - New `review` skill and `standards-reviewer` agent: `/code-review` for correctness beside a legibility and usability review against `CLAUDE.md` and the matching `docs/standards/` files, reported once, with fixes made only on the user's pick and the commit left to the user.
    `preflight` stays, labeled beta, and drops its "review this before I open a PR" trigger so plain review requests route to `review`.
  - New `docs/standards/code-legibility.md`, a keyless standard for names, function size, control flow, and tests as documentation, read by every agent that judges code.
- **Why**: the interview changes and the review skill come from running the suite daily on a second machine.
  A code-first reconnaissance and grouped questions grounded interviews in facts and cut the context switching between answers, and ordered lenses read better than weighted parallel ones.
  `review` and `preflight` ship side by side so the report-then-wait review and the autonomous one can be compared on real branches.
- **Adaptation notes**:
  - Rename `## References` to `## Touch Map` in any `ready` or `in-progress` spec, since `builder` now plans against the Touch Map; `†` marks in older specs are plain text that nothing reads.
  - `code-legibility.md` carries no `applies-to:` key, so `refiner` and `code-reviewer` now hold every change to it as well; give it globs to narrow it, or delete it to opt out.
  - A project that edited `preflight`'s description merges on its first line; a project that removed `preflight` skips that file.

## v0.1.0 — 2026-10-06

- **What**: the baseline.
  Versioning restarts here; every earlier tag is retired and earlier history lives only in git.
  The payload as of this entry:
  - **Skills** (`.claude/skills/`): the pipeline is `sdd` → `implement-spec` → `refine` → `preflight`, each user-invoked.
    `sdd` interviews and writes a spec to `docs/specs/`.
    `implement-spec` builds it through one fresh agent per slice to a working, validated, render-checked `built` state.
    `refine` makes any branch right against `docs/standards/`, with or without a spec, and runs the one human QA pass on the final code before flipping a spec to `done`.
    `preflight` proves a finished branch through adversarial code and docs review, with Claude Code's `/code-review` beside `code-reviewer`, and full validation, then pushes and opens its PR without waiting for a yes once nothing is left for the user to decide; the PR's Risk section gives a level and the trunk evidence behind it.
    `tdd` holds the test-first discipline and needs nothing from the user, allowing tests to be restructured but never weakened in a refactor.
    `stage-for-commit` hands back a commit for small changes, `curate-context` governs context-file edits, and `brand-init` fills `BRANDING.md` once.
    `template-sync` pulls a newer template release into a project, using the release in `.ai-starter.yaml` as the common ancestor so untouched files stay untouched and project edits are three-way merged, with every conflict left to the user; `template-feedback` files a template defect as an issue on the template's repository after verifying it against the latest release, checking for duplicates, and scrubbing anything private.
  - **Agents** (`.claude/agents/`): skills that write or judge code orchestrate from the main session and dispatch that work to named agents briefed only from artifacts, so no author or reviewer shares a context.
    `builder` writes one spec slice and `refiner` brings a change up to standard, both with `tdd` preloaded; `render-checker` drives the running app for both orchestrators.
    A trunk change the spec did not decide is argued by `skeptic`, on whether it should exist, beside `code-reviewer`, which also reviews a staged change and lists trunk touch points with consumer counts.
    `code-reviewer` and `docs-reviewer` serve `preflight`, and `research-analyst` serves `sdd`.
  - **Rules** (`.claude/rules/`): skill authoring, a path-scoped rule that caps a skill body at 500 lines.
    Implementer-critical rules (pnpm only, the Node pin, email templates built to their standard from the first line) are condensed into `CLAUDE.md`.
  - **Standards** (`docs/standards/`): UX floors, frontend styling, HTML tables, transactional email, JavaScript and TypeScript, agent-facing script output, and design principles, each scoped by `applies-to:` globs and read by path rather than auto-loaded, so standards reach the code at judgment time instead of crowding every implementing session; `rules-frontmatter.battery.mjs` checks both scopes.
  - **Guards**: `guard-main` keeps AI commits and pushes off the default branch, `guard-secret-read` keeps secret files out of commands, and `.claude/settings.json` carries the permission and secrets registry; `code-review-settings.battery.mjs` fails when that file would block the bundled `/code-review` preflight runs.
  - **Lineage**: `.ai-starter.yaml` records the template repository and the release a project last synced to, shipped in the payload so every new project starts with the right base; `ai-starter-version.battery.mjs` checks its shape and, in the template repo, that it matches `package.json`.
  - **Toolchain**: pnpm and Turborepo, with Node and pnpm pinned in `.nvmrc` and `package.json` and read by mise through a version-free `mise.toml`; the `preinstall` guard enforces the pins.
  - **CI**: one `checks` job on every PR and push to `main` running `format:check`, `lint`, `typecheck`, `test`, and `test:scripts`.
  - **Context**: `CLAUDE.md`, a bracketed `BRANDING.md` scaffold, and a five-section PR template whose Risk section tells the human reviewer where to look.
- **Why**: the template changed so much across its earlier versions that walking their entries no longer helps anyone adopt it, so it restarts at a pre-stable 0.x that says breaking changes may land in any minor release.
- **Adaptation notes**: a project created from any earlier version re-adopts from this baseline rather than applying old entries one by one.
