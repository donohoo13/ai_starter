# Changelog

Template releases, newest first.
Each entry carries three parts: **what** changed, **why**, and **adaptation notes** for projects whose setup diverges from the shipped defaults.
A release is a git tag (`vX.Y.Z`) on `main` matching the entry heading.
In a project created from the template, this file is template residue: delete it.

## v0.3.0 — unreleased

- **What**:
  - `BRANDING.md` is replaced by `DESIGN.md`, a scaffold in Google's [design.md](https://github.com/google-labs-code/design.md) format.
    Token values move into YAML front matter: colors named by role, each with its `on-` pair, typography roles, radius and spacing scales, and component bindings for a base UI kit, all checked by `pnpm exec designmd lint DESIGN.md` and exportable to Tailwind or DTCG tokens.
    The prose keeps the spec's section order (Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts) and adds Hierarchy & Emphasis, Motion, Imagery & Iconography, Data Visualization, and Voice & Copy as extension sections; Anti-Goals merge into Do's and Don'ts, where every Don't names its Do.
  - `@google/design.md` is a root devDependency, pinned exactly because its spec and CLI are still alpha, so sessions run the linter through `pnpm exec designmd` instead of handing the user a `pnpm dlx` command.
    `curate-context` holds an edit to a filled `DESIGN.md` until that lint reports no errors.
  - The design doc is now the source of truth for token values and the app's theme CSS mirrors it, the reverse of before; `frontend-styling.md` says so.
  - Positioning and messaging pillars leave the design doc for `docs/company/company-overview.md`; audience, primary job, and promise stay as the Overview's product context.
  - `brand-init` is renamed `design-init`, after the file it fills.
    It walks the new structure, reads the mood board from `docs/design/moodboard/` instead of `docs/branding/moodboard/`, and runs the lint until it is clean before offering to delete itself.
  - `CLAUDE.md`, `README.md`, the skills, and the agents name `DESIGN.md` and `design-init` wherever they named `BRANDING.md` and `brand-init`.
  - `pnpm dev` clears `.logs/dev-server.log` before it records the new server's pid, so the log beside a fresh pid is always that run's.
    `node-dev-server.battery.mjs` delays the wrapper's async file I/O, so an ordering that only holds on a fast machine fails every run instead of some CI runs.
  - `check-install.mjs` keeps its pnpm-only gate and its pin-agreement check, and drops the wrong-Node check and the pnpm 10-and-older `engineStrict` deadlock check; its battery shrinks to match.
  - `code-review-settings.battery.mjs` is removed.
- **Why**: the design restructure gets better results from design sessions.
  Role-named tokens and component bindings give a building session exact values to compose from instead of prose to interpret, and the linter catches broken references and contrast failures before a surface ships.
  `DESIGN.md` is the filename the format's spec and tooling use, and the skill that fills it now carries the same name.
  `pnpm dev` wrote its pidfile before the previous log was cleared, so a reader acting on the new pid could read the last server's output, and the dev-server battery failed intermittently on slow runners.
  The dropped install checks duplicated what mise and pnpm 11's `devEngines` runtime already guarantee, and the code-review settings battery guarded against settings no project adds.
- **Adaptation notes**:
  - A filled `BRANDING.md` arrives in `template-sync` as a conflict beside a new `DESIGN.md`, since the contents differ too much to register as a rename.
    Port its decisions into the new sections: values into the front matter, positioning and messaging pillars into `docs/company/company-overview.md`, anti-goals into Do's and Don'ts.
    Then run the lint and delete `BRANDING.md`.
  - A project that still has an unedited `brand-init` ends up with `design-init` in its place; an edited one surfaces as a conflict.
    A project that deleted `brand-init` after filling its brand doc sees `design-init` as a new skill: take it to run the interview against the new scaffold, or skip it and port by hand.
  - The devDependency adds about 90 packages to the install; a project that ships no UI drops it with `pnpm remove @google/design.md`.
  - Move an existing `docs/branding/moodboard/` to `docs/design/moodboard/`, along with any `.gitignore` line for it.
  - Theme CSS whose token values differ from `DESIGN.md` is now the drift: reconcile it to the file, for instance by generating it with `pnpm exec designmd export --format css-tailwind DESIGN.md`.
  - Project-owned files that name `BRANDING.md` or `brand-init` (nested `CLAUDE.md` files, project rules, specs in progress) need the same rename; `git grep -E 'BRANDING|brand-init'` finds them.
  - A project that edited `scripts/dev/node-dev-server.mjs` merges on the three lines that open the log.
  - A project still on pnpm 10 or older loses the preinstall stop on an `engineStrict` and `devEngines` pairing: turn `engineStrict` off, or get onto the `packageManager` pin with `mise install`.
  - A project that deleted its `devEngines` block and skips mise no longer gets a hard stop on the wrong Node; `doctor.sh` still warns on drift during `prepare`.
  - A project that adds `Skill` denies, `disableBundledSkills`, or `skillOverrides` to `.claude/settings.json` has nothing left to flag a block on `/code-review`, which `review` and `preflight` run; confirm it still runs after such an edit.

## v0.2.0 — 2026-10-22

- **What**:
  - `sdd` opens with a read-only reconnaissance that presents a touch map before the first question, then interviews in rounds of three or four coupled questions instead of one per turn.
    Its lenses run in order, product, engineering, then design, in place of the weighted parallel lenses, and every lens is accounted for: Product and Design keep a one-line disposition when they do not apply.
    The spec template drops the `†` user-driven marker, adds a blast-radius line to Architecture, renames `References` to `Touch Map` with each path's role, current shape, and risk, and moves `Sources` under `Evidence`.
    `implement-spec` and `refine` run the render pass for a spec whose Design Requirements name a surface rather than a one-line disposition, and `builder` plans against the Touch Map.
  - New `review` skill and `standards-reviewer` agent: `/code-review` for correctness beside a legibility and usability review against `CLAUDE.md` and the matching `docs/standards/` files, reported once, with fixes made only on the user's pick and the commit left to the user.
    `preflight` stays, labeled beta, and drops its "review this before I open a PR" trigger so plain review requests route to `review`.
  - New `docs/standards/code-legibility.md`, a keyless standard for names, function size, control flow, and tests as documentation, read by every agent that judges code.
  - New opt-in macOS kit under `scripts/setup/machine/`: `install.sh` with a Brewfile and zsh, git, mise, Zed, and Chrome configs, plus a personal working agreement installed to `~/.claude/rules/`, covered by `machine-install.battery.mjs`.
  - `CLAUDE.md`'s Development section gains one rule: never hand-edit a file marked as generated; change its source and regenerate.
- **Why**: the interview changes, the review skill, the working agreement, and the generated-files rule come from running the suite daily on a second machine.
  A code-first reconnaissance and grouped questions grounded interviews in facts and cut the context switching between answers, and ordered lenses read better than weighted parallel ones.
  `review` and `preflight` ship side by side so the report-then-wait review and the autonomous one can be compared on real branches.
  The machine kit carries one Mac's setup to the next through the same release channel as the rest of the payload.
  A hand edit to a generated file is lost silently at the next regeneration, so that rule has to hold while code is written, not when it is reviewed.
- **Adaptation notes**:
  - Rename `## References` to `## Touch Map` in any `ready` or `in-progress` spec, since `builder` now plans against the Touch Map; `†` marks in older specs are plain text that nothing reads.
  - `code-legibility.md` carries no `applies-to:` key, so `refiner` and `code-reviewer` now hold every change to it as well; give it globs to narrow it, or delete it to opt out.
  - A project that edited `preflight`'s description merges on its first line; a project that removed `preflight` skips that file.
  - The machine kit never runs on its own, and `claude/rules/ai-starter.md` holds personal preferences: delete `scripts/setup/machine/` in a repository others share.

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
