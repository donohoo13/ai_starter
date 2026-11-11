# Changelog

Template releases, newest first.
Each entry carries three parts: **what** changed, **why**, and **adaptation notes** for projects whose setup diverges from the shipped defaults.
A release is a git tag (`vX.Y.Z`) on `main` matching the entry heading.
In a project created from the template, this file is template residue: delete it.

## v0.3.0 — unreleased

- **What**:
  - The spec suite is replaced by a five-phase spec-driven development chain: `sdd-outline`, `sdd-plan`, `sdd-task`, `sdd-implement` and `sdd-review` follow `.claude/sdd/spec-driven-development.md` by section, keep state with the `.claude/sdd/bin/sdd` helper (approvals with content hashes, staleness down the chain, structural lint, templates generated from the appendices), and commit their artifacts under `docs/sdd/<slug>/` as `spec.md`, `plan.md`, `tasks.md` and `review.md`.
    `sdd`, `implement-spec`, `review` and `preflight` are removed, with the `builder` and `docs-reviewer` agents only they dispatched.
  - `sdd-implement` orchestrates instead of building: a fresh `implementer` agent (new, `tdd` preloaded, `opus` pinned, dispatched at `effort: high` unless the user names another level) builds each slice from a pointer-only brief and self-checks against the matching `docs/standards/` files.
    The orchestrator brings each `BLOCKED` question to the user, dispatching `skeptic` first for a trunk change the spec did not decide, verifies every report with its own checks, commits each verified slice and any approved trunk change on its own, runs one QA pass before `tasks.md` reaches `done`, and recommends `sdd-review` next in the same session.
    `sdd-review` runs every reviewer in a fresh context on a pointer-only brief, so it needs no fresh session, and builds each fix the user picks through a fresh `implementer`.
    The SDD document's principle 10 follows: the orchestrator commits slice work during Implement, and the user still commits gate artifacts and review fixes.
  - `skeptic` argues a proposed trunk change from its brief instead of the index, since nothing is built until the user approves it.
  - `refine` and the `refiner` and `code-reviewer` agents are removed; `render-check`, a skill only the user can start, now runs `render-checker`.
  - The `[P]` task marker leaves `tasks.md`, its template, `sdd-task` and the helper's lint.
  - `scripts/test/process-suite.battery.mjs` fails CI when the implementer's frontmatter drifts, a skill other than `render-check` or `sdd-implement` names `render-checker`, an agent has no skill naming it, or a tracked file outside `docs/sdd/` and this changelog names a removed skill or agent.
  - `template-sync` and `template-feedback` are removed; a project takes a release by diffing against its `.ai-starter.yaml` base by hand.
  - The `guard-main` and `guard-secret-read` Claude Code hooks, their `settings.json` registrations and `guard-main.battery.mjs` are removed.
    `.husky/pre-commit` now refuses a commit on the default branch (read from `origin/HEAD`, else `main`) and a new `.husky/pre-push` refuses a push to it, letting tags through; `husky-guard.battery.mjs` runs both against a throwaway repo.
    The `Read(...)` deny rules in `settings.json` keep covering secret files.
  - `.claude/rules/skill-authoring.md` drops the 500-line skill body cap: a body is as long as its job needs, and gating or rationale that belongs in a reference file is cut at any length.
    `CLAUDE.md` and the READMEs list skills and agents by name without a count.
  - `tdd` is rebuilt around a discovery reference that finds a repo's test commands and test shapes from its own files, keeps the mocking and good-versus-bad-test references, and adds a report-back contract so the `implementer` records evidence per task.
  - `research-analyst` is dispatched by `sdd-plan` and takes pinned Context7 library IDs; `standards-reviewer` is dispatched by `sdd-review` with the base ref and the commit range.
  - `scripts/test/sdd-helper.battery.mjs` runs the helper's unittest suite, the template drift check and the section-reference check under `pnpm test:scripts`, so CI needs `python3`; `.claude/sdd/templates/` is prettier-ignored so the generated files stay byte-identical to the appendices.
  - `sdd-review` resumes a review an earlier session left open instead of running the reviewers again.
    `review.md` carries one `- Disposition:` line under each conformance gap, correctness finding and standards finding (`open`, `picked`, `fixed`, `declined` or `deferred`), written before any fix is dispatched, and names the reviewed head in `range` by its commit hash.
    A new session reads those records, asks whether to rerun when the branch holds a commit the report does not list, hands unfinished fix work to a fresh `implementer` on the user's word, and continues with the findings still `picked` or `open`; a rerun keeps every decision already made.
    The helper gains `sdd uncommitted [slug]`, which lists every uncommitted path except the spec's own `review.md`, and the review's clean-tree gate and fix check read the tree through it.
    `sdd lint <slug> review` reports a finding with no disposition and one still `open` or `picked`, so `set-status <slug> review accepted` refuses until every finding is decided.
  - `.claude/rules/skill-authoring.md` records the one SDD exception: naming the next phase as the handoff.
  - `BRANDING.md` is replaced by `DESIGN.md` in Google's [design.md](https://github.com/google-labs-code/design.md) format, which `design-init` writes at the root from a template it carries; the payload ships no root `DESIGN.md`.
    Token values move into YAML front matter: colors named by role, each with its `on-` pair, typography roles, radius and spacing scales, and component bindings for a base UI kit, all checked by `pnpm exec designmd lint DESIGN.md` and exportable to Tailwind or DTCG tokens.
    The prose keeps the spec's section order (Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts) and adds Hierarchy & Emphasis, Motion, Imagery & Iconography, Data Visualization, and Voice & Copy as extension sections; Anti-Goals merge into Do's and Don'ts, where every Don't names its Do.
  - `@google/design.md` is a root devDependency, pinned exactly because its spec and CLI are still alpha, so sessions run the linter through `pnpm exec designmd` instead of handing the user a `pnpm dlx` command.
    `curate-context` holds an edit to a filled `DESIGN.md` until that lint reports no errors, refuses a value below its WCAG 2.2 AA floor and names the success criterion, and once an approved edit lands on a `DESIGN.md` that records a Design System link, offers to re-sync that artifact after warning that edits made to it in Claude are replaced.
  - The design doc is now the source of truth for token values and the app's theme CSS mirrors it, the reverse of before; `frontend-styling.md` says so.
  - Positioning and messaging pillars leave the design doc for `docs/company/company-overview.md`; audience, primary job, and promise stay as the Overview's product context.
  - `brand-init` is renamed `design-init`, after the file it writes, and rewritten.
    Its only template lives at `.claude/skills/design-init/references/design-template.md`, with decision tables for target size, reading width, motion timing, units and table styling, and a Claude Design System section.
    It takes `docs/company/company-overview.md` as the authority on audience and voice, plus an optional reference `DESIGN.md` and an optional mood board, now read from `docs/design/moodboard/` instead of `docs/branding/moodboard/`.
    It opens with a brief of what it carries over and replaces, decides identity in five rounds of questions that each lead with a recommendation, asks before it touches a filled `DESIGN.md`, refuses any value below its WCAG 2.2 AA floor, and finishes only when `pnpm exec designmd lint DESIGN.md` is clean.
    It then offers to build or re-sync the project's Design System in Claude from `DESIGN.md`, following the artifact type's own instructions through a new mapping reference, and records the artifact's link in `DESIGN.md`.
  - `CLAUDE.md`, `README.md`, the skills, and the agents name `DESIGN.md` and `design-init` wherever they named `BRANDING.md` and `brand-init`.
  - `pnpm dev` clears `.logs/dev-server.log` before it records the new server's pid, so the log beside a fresh pid is always that run's.
    `node-dev-server.battery.mjs` delays the wrapper's async file I/O, so an ordering that only holds on a fast machine fails every run instead of some CI runs.
  - `check-install.mjs` keeps its pnpm-only gate and its pin-agreement check, and drops the wrong-Node check and the pnpm 10-and-older `engineStrict` deadlock check; its battery shrinks to match.
  - `code-review-settings.battery.mjs` is removed.
  - The `playwright-local` MCP server leaves `.mcp.json`, along with its `settings.json` allow rule and the `.playwright` lines in `.gitignore` and `.prettierignore`.
    The `chrome-devtools` server moves from `chrome-devtools-mcp@1.6.0` to `1.12.0`.
  - `sdd-outline` plays the problem back before its interview and ends the turn until the user confirms or corrects it.
    Section 7 of the SDD document holds the rules: grounding reads how each involved system behaves, the playback marks each distinct problem confirmed or hypothesis, a cause that decides the options is confirmed before any question, the user scopes several problems with the rest under Non-goals and the remainder sized again, and interview options stay at behavior and split per problem.
    Appendix A's Problem and context asks for each distinct problem, and the adversarial review flags a problem that no requirement addresses and no non-goal excludes.
  - A Design phase sits between Outline and Plan, run by the new `sdd-design` skill.
    The spec template gains a `## UI surfaces` section listing each screen, page, view, component or email template once under a permanent ID (`UI-001`), and `sdd-outline` and `sdd-plan` offer a design for a spec that lists one, recording a skip in `design.md`.
    `sdd-design` writes a standalone Claude Design prompt into `docs/sdd/<slug>/design.md`; when the user brings back the approved design's link, it saves the canvas and artboards under `docs/sdd/<slug>/design/`, asks about every listed state no artboard shows and every element no requirement covers, and records the approval.
    The helper tracks `design.md` as a fifth artifact: `set-status <slug> design requested|skipped` records a request or a skip, a repeat request clears the previously recorded design, and `approve <slug> design` records approval.
    `sdd status` reports `2. Design` and names `sdd-design` while a design is requested, approved but changed or stale, or skipped without covering every listed surface; `sdd-plan`, `sdd-task` and `sdd-implement` refuse to start meanwhile.
    The plan builds on the approved design, so a design approved or changed after the plan stales the plan and tasks, and the `implementer` builds a designed surface from the project's tokens and components with the artboards as reference, building nothing recorded as not built.
    The phases renumber to `1. Outline`, `2. Design`, `3. Plan`, `4. Tasks`, `5. Implement` and `6. Validate`, and the SDD document's sections and appendices renumber to match.
  - The approval hash of `design.md`, `plan.md` and `tasks.md` covers the body plus `based_on`, so re-approving one against a changed upstream always records a new hash and stales what builds on it; `spec.md` hashes its body alone as before.
    A design's hash also covers its recorded `version`, so re-recording a changed canvas needs a new approval and stales the plan.
    `set-status <slug> design` on an existing `design.md` no longer refuses when the spec lists no UI surface, so a requested design can still be cancelled after a re-approved spec drops its surfaces.
    A repeat request also clears a skip's `decided_by` and `surfaces`.
    `sdd lint` rejects any bullet under a spec's `## UI surfaces` that is not a `UI-` line with a colon after its ID.
  - `sdd-implement` asks, at the first start or at a resume that meets a new UI ID, which listed surfaces get a render check, recommending each by criterion: a new surface, an approved design, a layout that changes between mobile and desktop widths, or a color pairing no existing surface uses.
    It records the answer in `tasks.md`'s frontmatter as `render_check` (the approved IDs, or `none`) and `render_check_asked` (every ID asked about), outside the content hash, so the tasks stay approved.
    When every slice is committed and a surface was approved, it dispatches `render-checker` once before QA, puts each failure in the QA script with its evidence, and sends only the failures the user picks to a fresh `implementer`.
    `/render-check` still runs on its own, and `render-checker` accepts either dispatcher.
  - `ux-standards.md` splits into Floors, the WCAG 2.2 AA success criteria and Core Web Vitals thresholds no project goes below (a 24×24 CSS px target under 2.5.8), and Starting values that `DESIGN.md` decides: a 38×38px target in place of the fixed 44×44px, a `70ch` reading width, 100–300ms motion, feedback timing and data-table styling.
    `frontend-styling.md` and `html-tables.md` replace their unit bans with a principle to use units that scale with user settings and the viewport, keeping the `svh`-first full-height rule as a starting value; `html-tables.md` keeps its markup rules as requirements and labels its styling a starting value, and `frontend-styling.md` holds that a design snapshot or Claude Design markup is a reference, never shipped UI.
    The starting values apply wherever `DESIGN.md` is absent, still holds bracket placeholders, or is silent on a value, and brand decisions stay undecided until `design-init` runs.
    `implementer`, `standards-reviewer` and `render-checker` judge a surface against `DESIGN.md` on that rule, and against the floor wherever a `DESIGN.md` value falls below it.
    `transactional-email.md` keeps its 44×44px CTA target as an email starting value.
  - `.prettierignore` excludes `docs/sdd/*/design/`, so the pre-commit hook leaves a design snapshot byte for byte as it was read.
  - New `docs/standards/ruby.md` holds Ruby conventions for tooling, RBS types and language idioms, with Rails-only rules in their own section.
  - The opt-in macOS kit under `scripts/setup/machine/` is removed, with `machine-install.battery.mjs` and the README's "Setting Up a Mac" section.
- **Why**: the design restructure gets better results from design sessions.
  Role-named tokens and component bindings give a building session exact values to compose from instead of prose to interpret, and the linter catches broken references and contrast failures before a surface ships.
  `DESIGN.md` is the filename the format's spec and tooling use, and the skill that fills it now carries the same name.
  `pnpm dev` wrote its pidfile before the previous log was cleared, so a reader acting on the new pid could read the last server's output, and the dev-server battery failed intermittently on slow runners.
  The dropped install checks duplicated what mise and pnpm 11's `devEngines` runtime already guarantee, and the code-review settings battery guarded against settings no project adds.
  The spec chain replaces four skills that each held part of the lifecycle with one document and one state helper, so a phase cannot start on a stale or unapproved upstream and a fresh session resumes from the committed artifacts alone; `preflight` went with it because `sdd-review` covers the review, the fixes and the PR draft while the user keeps the push.
  A review wrote `review.md` and left it uncommitted until acceptance, so its own fix check met a path no agent reported and a new session's clean-tree gate stopped on that file, while the user's picks lived only in the conversation; an interrupted review could only start over.
  Building in the session that invoked `sdd-implement` carried the whole build in one context and checked each slice in the context that wrote it; a fresh agent per slice builds from the approved artifacts alone, and an orchestrator that did not write the code verifies it before committing.
  `refine` rewrote finished code to the standards `sdd-review` then judged again, so standards now hold inside each slice and the review is the single pass; render passes are slow and token-heavy, so one runs only when the user starts it or picks its surfaces at build start.
  The `[P]` marker had no consumer once slices build one at a time, and the battery keeps the suite's structural rules from drifting the way the skill counts did.
  A git hook guards every commit and push, from any author or tool, where the Claude Code hooks guarded only Claude's Bash calls and parsed shell text to do it.
  `chrome-devtools` covers what `playwright-local` did in a render or debug pass and adds performance traces, Lighthouse audits and network bodies, so a second Chromium driver only split sessions across overlapping tools and cost a ~100MB browser download on first launch.
  `chrome-devtools-mcp` 1.11.0 and later read a machine-level `~/.config/cd4a/config.json`, so one file can point every project's server at a chosen browser binary without a per-project flag.
  An outline session grounded in the code and went straight to solution-level questions without saying the problem had three distinct causes, so the user could not answer them with confidence.
  The grounding stayed in the session, the brief's framing went unchecked, and the options rested on an error source nobody had read up on.
  No phase requested or recorded a UI design, so implementers decided layout and flow mid-build, behavior a design implied bypassed the spec, and nobody saw a layout until QA; the Design phase puts an approved, committed design in front of the plan.
  A design, plan or tasks re-approved with an unchanged body against a changed upstream kept its old hash, so everything built on it still read current.
  The standards hard-coded values such as a 44×44px target and a px ban that each project's design system should own, so they overrode it; only the WCAG 2.2 AA floors stay fixed, and `DESIGN.md` is the one home for every other value.
  A scaffold at the root and a copy in `design-init` drifted apart, so one template in the skill and a lint-clean finish leave a project with either a complete `DESIGN.md` or none, and the Design System in Claude is built from that file so mockups use the project's own tokens.
  The skill body cap had no reliable measure and pushed skills to trim guidance that served quality.
  Ruby projects created from the template had no conventions for tooling, types or idioms.
  The machine kit leaves because one Mac's setup is personal, not project payload, and a dedicated dotfiles repository now carries it.
- **Adaptation notes**:
  - A `docs/specs/*.md` spec in flight finishes under the old skills before taking this release, or is outlined again with `sdd-outline` into `docs/sdd/<slug>/`; nothing migrates it.
  - A project that edited `sdd-implement` reapplies its edits to the orchestrator, or to `implementer` when they concerned how a task is built.
    One that used `refine` gets standards checks inside each slice, QA at the end of `sdd-implement`, and render passes through `/render-check`; `git grep -E 'refine|refiner|code-reviewer'` finds project files that still name the removed pieces.
  - A `tasks.md` in flight that marks tasks `[P]` still lints; the marker is now plain title text, so drop it.
  - A project that wants a different build model or effort edits `model:` in `.claude/agents/implementer.md`, or names the effort when it starts `sdd-implement`.
  - A project deletes `sdd`, `implement-spec`, `review` and `preflight`, first carrying any edits it made to them into the `sdd-*` skills.
  - A project deletes `.claude/hooks/` and the `hooks` block in `.claude/settings.json`, adds `.husky/pre-push`, and adds the default-branch check at the top of its own `.husky/pre-commit`; a project whose pre-commit runs lint-staged keeps that line below the check.
  - CI runners need `python3` for the new battery; a project without Python deletes `scripts/test/sdd-helper.battery.mjs` and runs `python3 -m unittest discover -s .claude/sdd/tests` by hand.
  - Project-owned files that name the removed skills (nested `CLAUDE.md` files, project rules) need the same rename; `git grep -E 'implement-spec|preflight|/review'` finds them.
  - A filled `BRANDING.md` has no `DESIGN.md` beside it when this release is diffed, since the payload ships only `design-init`'s template.
    Port its decisions into a root `DESIGN.md` started from `.claude/skills/design-init/references/design-template.md`, or run `design-init` with its decisions as context: values into the front matter, positioning and messaging pillars into `docs/company/company-overview.md`, anti-goals into Do's and Don'ts.
    Then run the lint and delete `BRANDING.md`.
  - A project replaces `brand-init` with `design-init`, carrying across any edits it made.
    A project that deleted `brand-init` after filling its brand doc sees `design-init` as a new skill: take it to run the interview against the new template, or skip it and port by hand.
  - The devDependency adds about 90 packages to the install; a project that ships no UI drops it with `pnpm remove @google/design.md`.
  - Move an existing `docs/branding/moodboard/` to `docs/design/moodboard/`, along with any `.gitignore` line for it.
  - Theme CSS whose token values differ from `DESIGN.md` is now the drift: reconcile it to the file, for instance by generating it with `pnpm exec designmd export --format css-tailwind DESIGN.md`.
  - Project-owned files that name `BRANDING.md` or `brand-init` (nested `CLAUDE.md` files, project rules, specs in progress) need the same rename; `git grep -E 'BRANDING|brand-init'` finds them.
  - A project that edited `scripts/dev/node-dev-server.mjs` merges on the three lines that open the log.
  - A project still on pnpm 10 or older loses the preinstall stop on an `engineStrict` and `devEngines` pairing: turn `engineStrict` off, or get onto the `packageManager` pin with `mise install`.
  - A project that deleted its `devEngines` block and skips mise no longer gets a hard stop on the wrong Node; `doctor.sh` still warns on drift during `prepare`.
  - A project that adds `Skill` denies, `disableBundledSkills`, or `skillOverrides` to `.claude/settings.json` has nothing left to flag a block on `/code-review`, which `review` and `preflight` run; confirm it still runs after such an edit.
  - A project whose own skills, agents or scripts drive `playwright-local` keeps its stanza, allow rule and `.playwright` ignore lines; `git grep -i playwright` finds what still names it.
    Otherwise delete the local `.playwright/` directory, which held that server's browser profile.
  - A project that passed flags to `chrome-devtools` carries them onto the new pin, or moves machine-specific ones such as `executablePath` into `~/.config/cd4a/config.json`.
  - A project that edited `sdd-outline` or section 7 of its SDD document merges the playback step and the interview rules by hand, then runs `.claude/sdd/bin/sdd templates sync` and `.claude/sdd/bin/sdd check-refs`.
    Specs already drafted still lint, since no heading changed.
  - A project with a filled `DESIGN.md` keeps it and skips the root scaffold's deletion, which only changes what a new project starts with; `design-init` now asks before it revises a filled file.
  - A project with specs in flight re-reads `sdd status`, since every phase from Plan on shifted by one (`2. Plan` is now `3. Plan`) and the SDD document's section numbers moved with them.
    A spec without `## UI surfaces` still lints and never meets the Design phase, and a build in flight whose spec lists a surface gets the render-check question at its next `sdd-implement` resume.
    A project that edited the SDD document or its skills merges the renumbering, then runs `.claude/sdd/bin/sdd templates sync` and `.claude/sdd/bin/sdd check-refs`.
  - A `plan.md` or `tasks.md` approved under an earlier helper keeps its body-only hash and still reads current, so nothing needs re-approving; its next approval records the new hash.
  - A `review.md` still `open` needs a `- Disposition:` line under each finding, and a `range` that ends at the reviewed commit, before `sdd-review` can resume or accept it; one already `accepted` needs nothing unless it is linted again.
    A project that edited `sdd-review` or section 13 of its SDD document merges the Resume step and the disposition rules by hand, then runs `.claude/sdd/bin/sdd templates sync` and `.claude/sdd/bin/sdd check-refs`.
  - A project that pinned or quoted `ux-standards.md` values in its own rules, such as the 44×44px target or the px ban, re-reads the split between Floors and Starting values: a value above its floor now belongs in `DESIGN.md`, and only the floor is fixed.
  - A project that extended the process battery's allowlist of skills naming `render-checker` adds `sdd-implement` to it.
  - A project that edited `.prettierignore` adds the `docs/sdd/*/design/` line.
  - `ruby.md`'s `applies-to:` globs match Ruby files and `mise.toml`, so a project without Ruby deletes it to keep it off `mise.toml` changes.
  - `scripts/setup/machine/` and `scripts/test/machine-install.battery.mjs` are gone: a project that used the kit keeps its own copy of both or deletes them, and files the kit already installed on a machine (`~/.config/zsh/ai-starter.zsh`, `~/.config/git/ai-starter.gitconfig`, `~/.config/mise/conf.d/ai-starter.toml`, `~/.claude/rules/ai-starter.md`) stay until removed by hand.

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
