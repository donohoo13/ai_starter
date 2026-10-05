---
status: done
---

# Add a `refine` skill and run the build pipeline through fresh-context agents

Split "make it work" from "make it right".
`implement-spec` builds to a working, validated state through one fresh `builder` agent per slice, and a new `refine` skill brings any branch up to the project's standards through a fresh `refiner` agent, then runs the one human QA pass.
The coding standards move out of auto-loading `.claude/rules/` into `docs/standards/`, read explicitly by the agents that judge code.

† marks a decision the user drove, in the ask or under interview.

## Product Requirements

### Problem

The template's developer runs `sdd`, `implement-spec`, and `preflight`, often back to back in one session.
The implementing session carries everything at once: path-scoped rules load every standard into its context as it touches files, it judges its own surfaces in the render pass, and it prepares the human QA of code it wrote.
Run in one session, the interview, the build, and the review share one context, so each step inherits the bias of the step before it.
Ad-hoc AI work outside a spec gets no quality pass at all.
Trunk-level improvements are deferred and reported rather than made, while the PR gives the human reviewer no signal of where its risk sits.

### User Stories

- As the developer, I run `implement-spec` and get a working, validated build at `status: built`, written by agents that saw only the spec, the code, and the notes earlier slices left.
- As the developer, I run `refine` on any branch, with or without a spec, and get the change brought up to the project's standards, its tests strengthened with proof, and one QA pass of my own on the final code.
- As the developer, I hear nothing from a refine run beyond its commits, one validation line, and the QA script, unless something major or destructive needs me.
- As the developer, I learn about every trunk change on the PR, with a risk level, the touch points behind it, and the dissent each change survived.
- As the developer, I never start the app so an AI can check a surface.
- As a project created from the template, I customize standards by editing, adding, or deleting files in `docs/standards/`.

## Engineering Requirements

- The pipeline is `sdd` → `implement-spec` (working build under `tdd`, full suite green, AI render pass) → `refine` → human QA, once, on the final code → `preflight` → PR. †
- `refine` is user-invoked and runs on any branch, with or without a spec. †
- Coding standards leave `.claude/rules/` and become docs the judging agents read explicitly; only `skill-authoring.md` and `template-dev.md` stay as rules. †
- A rule every implementer must hold, because getting it wrong first costs more than a refactor, goes into `CLAUDE.md` as one condensed line. †
- `implement-spec` ends at working and validated; the human QA gate moves to after `refine`. †
- `refine` owns standards compliance, completeness, cleanup, and test quality: deep modules behind small interfaces, and no shallow or mock-heavy tests. †
- No two authors or reviewers share a context: each skill orchestrates from the main session, and every unit of code writing or code judging runs in a named agent briefed only from artifacts. †
- Workers stop and report only for a major unforeseen issue (the spec or intent is wrong against the code, or the work cannot finish without a decision nobody made) or a destructive, irreversible, or outward-facing action.
  Every other judgment call (seams, layout, naming, how to satisfy a standard) they make themselves and list in their report. †
- `tdd` requires nothing from the user. †
- Tests may be restructured, moved, or rewritten during a refactor; they are never weakened to make one pass. †
- `refine` discovers its own change and intent and never stops at a gate; it shares no gate logic with `preflight`. †
- Trunk changes are made when the proof bar holds and disclosed on the PR with a risk level for human review; the user hears about them at the end, not during the run. †
- Every trunk change the spec did not decide is argued by two agents with their own contexts before it lands, one on whether it should exist and one on what it breaks. †
- `preflight` adds Claude Code's built-in `/code-review`, and nothing in the shipped permissions may block it. †
- The render pass launches and drives the app itself; the user never starts it. †
- Every skill body stays at or under 500 lines excluding frontmatter, measured before landing, with no target under that ceiling: a body is as long as its job needs. †
  Each body this build creates or substantively edits is written or reflowed to one sentence per line first, so the count measures content rather than formatting. †
- Each slice amends the unreleased v0.1.0 entry in `CHANGELOG.md`; no new version opens. †
- No version references or cross-release provenance enter the steering docs, per `template-dev.md`.
- Nesting stays at most two layers below the main session (orchestrator → worker → reviewer), inside Claude Code's three-layer limit.
- The user's `~/.claude/CLAUDE.md` trunk line was rewritten during the interview, with the same text in `docs/notes/global-claude.md`, committed on this branch ahead of the first slice; the build touches neither again.
- Validation in this repo is `pnpm format:check` plus `pnpm test:scripts`.
  Every created or changed skill or agent closes with gut-check prompts for a fresh session, since new agent files and skill bodies can only be judged cold.

### Slices

- [x] Standards relocate to `docs/standards/`, with `CLAUDE.md`, `curate-context`, and every path reference updated.
      Done when: `.claude/rules/` holds only `skill-authoring.md` and `template-dev.md`; `docs/standards/` holds the seven files with the frontmatter in Architecture; a `git grep` for the six old rule paths and `DESIGN_PRINCIPLES` finds nothing outside `CHANGELOG.md` and `docs/specs/`; `CLAUDE.md` carries exactly the approved text; `curate-context` measures within the 500-line ceiling; the widened frontmatter battery passes, and fails when an `applies-to:` glob is deliberately unquoted; `pnpm format:check` and `pnpm test:scripts` pass.
- [x] `tdd` needs no user.
      Done when: the `tdd` body holds no instruction to confirm with or wait on the user; the Seams sentence, the Shallow anti-pattern, and the refactor rule read as approved in Architecture; the body measures within the 500-line ceiling; gut-check prompts are handed over.
- [x] Trunk-change review: the new `skeptic` agent and the widened `code-reviewer`.
      Done when: `skeptic.md` exists read-only with its brief schema in the description; `code-reviewer.md` names the staged-diff brief, the Trunk touch points output, and the standards lens; gut-check prompts are handed over that dispatch each agent on a staged trunk change in a scratch branch.
- [x] `implement-spec` orchestrates one `builder` per slice and ends at `built`, with `render-checker` and the app lifecycle.
      Done when: `builder.md` and `render-checker.md` exist with the tools, preloads, and briefs in Architecture; the `implement-spec` body dispatches and verifies per slice, forwards notes, launches the app for the render pass, never edits source, hands over no QA script, and flips to `built`; the three deleted lines are gone; `skill-authoring.md` carries the orchestration line; `.claude/skills/README.md` shows the `built` lifecycle; the body measures within the 500-line ceiling; gut-check prompts are handed over.
- [x] `refine` skill and `refiner` agent.
      Done when: `.claude/skills/refine/SKILL.md` and `refiner.md` exist and behave as Architecture states; `CLAUDE.md` lists eight skills, and `README.md` and `.claude/skills/README.md` list eight skills and the new agents; the body measures within the 500-line ceiling; gut-check prompts are handed over, including should-trigger prompts and near-miss should-not-trigger prompts against `preflight`, `stage-for-commit`, `/code-review`, and `/simplify`.
- [x] `preflight` runs `/code-review` beside `code-reviewer` and writes the PR's Risk section.
      Done when: the Review step runs `/code-review high <base>...HEAD` in parallel with `code-reviewer` and names a skip; `.github/PULL_REQUEST_TEMPLATE.md` carries `## Risk`; `references/publish-and-ci.md` states the Risk composition and levels; held corrections include `docs/standards/`; the body measures within the 500-line ceiling; the new settings battery passes on the shipped settings and fails when a `Skill(code-review)` deny rule is deliberately added; gut-check prompts are handed over.

### Architecture

#### Orchestration contract

- A skill body is an orchestrator in the main session.
  It runs gates, talks to the user, flips spec status, owns the app server, dispatches agents, and verifies their claims with `git` and test runs.
  It never edits source or tests; spec-status edits and git operations are its own.
- `context: fork` is not used, because subagents cannot call `AskUserQuestion` and every orchestrator here has user gates.
- Each worker's description states the brief it expects, the way `code-reviewer` does today.
  A brief carries pointers to artifacts (spec path, refs, intent, forwarded notes), never opinions, so the orchestrator's bias cannot ride in through it.
- A `BLOCKED` worker is resumed with `SendMessage` after the user answers, keeping its full context.
- Custom agents load `CLAUDE.md` and project rules at startup, so the condensed `CLAUDE.md` lines reach every worker; standards reach only the agents told to read them.
- `skill-authoring.md` gains: "A skill whose work writes or judges code dispatches it to a named agent in `.claude/agents/` and keeps its gates and every user interaction in the body, since a subagent cannot ask the user."

#### Agents

- `builder` (new): inherits every tool, `skills: [tdd]`.
  Brief: spec path, slice, and notes forwarded from earlier slices.
  It plans against Architecture and References, chooses its seams, builds red-first, validates with the project's typecheck, lint, format, and the slice's tests, commits the slice with its spec checkbox ticked, and audits multi-file consistency.
  It reports `DONE`, `DONE_WITH_CONCERNS`, or `BLOCKED`, plus the commit, the seams chosen, and notes for later slices (facts only: conventions found, gotchas).
- `refiner` (new): inherits every tool, `skills: [tdd]`.
  Brief: base (the merge-base), baseline commit, intent, and mode (spec or ad-hoc).
  Its method is under `refine` below.
  It reports the commit list and, for the orchestrator only, the test table: each test file added, changed, or deleted, with its proof.
- `skeptic` (new): read-only, `tools: Read, Grep, Glob, Bash, LSP`.
  Brief: the staged diff, the intent, and the consumers.
  It returns a verdict of `keep`, `revise`, or `drop`, the strongest case against the change, and an alternative with its cost when one exists.
  It hunts no defects; that lens belongs to `code-reviewer`.
- `render-checker` (new): inherits tools so the browser MCP tools come along, with `disallowedTools: Edit, Write, NotebookEdit, Agent`.
  Brief: the URL, the touched surfaces, the shipped themes, and the bar.
  It navigates and interacts to reach each state (hover, error, empty, open disclosure), screenshots at mobile and desktop widths in every shipped theme, measures floors on the rendered page (computed contrast, target bounding boxes), and returns pass or fail per surface, width, and theme with evidence.
- `code-reviewer` (widened): its description reads "dispatched by `preflight`, and by workers on a trunk change".
  Its brief accepts a staged diff (`git diff --cached`) in place of a commit range.
  Its output gains Trunk touch points: every pre-existing shared symbol, public interface, schema, or config the change touches, with its consumer count from LSP find-references.
  Its Consistency lens checks `CLAUDE.md`, `.claude/rules/`, and the `docs/standards/` files whose `applies-to:` matches the diff.
- Only `builder` and `refiner` carry `Agent`, and they dispatch only `skeptic` and `code-reviewer`; every other agent omits it.
- `docs-reviewer` gains the same no-execute, no-write wording as `code-reviewer`; `research-analyst` is unchanged.

#### Trunk-change protocol

Applies to any worker making a trunk change (shared utility, public interface, schema, config) the spec did not decide; one the spec decided was already argued during `sdd`.

- Proof bar: every consumer is in the repo and updated in the same commit, and proven tests show behavior held.
  Where that cannot be shown (a published package API, an external HTTP contract, a schema holding live data), the change is not made.
- Stage the change, then dispatch `skeptic` and `code-reviewer` in one message so they run concurrently.
- A defect the reviewer shows is fixed, followed by one re-review on the same instance through `SendMessage`.
  `drop` unstages the change; `revise` takes the alternative or records why not; `keep` records.
- Each trunk change commits alone, so it reverts alone.
  The body records the touch point, the consumer count, the reviewer's result, and the skeptic's verdict with any alternative not taken; `preflight` reads it from there, so nothing chains the skills together.

#### Spec lifecycle

- `ready` (written by `sdd`) → `in-progress` → `built` (both flipped by `implement-spec`) → `done` (flipped by `refine` once the user confirms QA).

#### `implement-spec`

- Gate and Workspace are unchanged.
- Per slice, in order: dispatch a fresh `builder`, verify the commit exists, the slice's tests pass, and the checkbox is ticked, then forward its notes into the next brief.
- Land: the orchestrator runs the full suite (a failure goes to a fresh `builder`), runs the render pass when any slice touched a surface, flips `in-progress` → `built`, commits the flip, reports, and stops.
  No QA script and no `done`.
- Render bar: the spec's Design Requirements and `BRANDING.md`.
  Failures go to a fresh `builder` briefed with the findings, then one re-check; a skipped pass is noted in the spec.
- Deleted: "A surface slice holds the floors in `.claude/rules/ux-standards.md`", the QA handover, and "Servers are user-run; give instructions, never start one", which contradicts `CLAUDE.md`'s `pnpm dev` rule.

#### `refine`

- Triggers: a finished build or ad-hoc AI work the user wants brought up to standard ("refine", "make it right", "clean this up", "bring this up to our standards").
  Argument: an optional spec path or one line of intent; blank means discover.
- Discovery: the change is everything between the merge-base with `origin/<default>` (the local default without a remote) and the working tree, committed or not.
  Intent is the argument, else a `docs/specs/` file in the change, else inferred from the branch's commits and diff, announced in one line ("Refining X, from Y") and never asked.
  A spec at `built` sets spec mode; anything else is ad-hoc.
- On the default branch, the orchestrator branches first per `CLAUDE.md`.
  Uncommitted work is committed untouched as a baseline before dispatch, so refine's own commits stay separable and its test-table check stays exact.
- Refiner method:
  1. Audit: match each `docs/standards/` file's `applies-to:` against the change's paths, read every match plus `design-principles.md` in full, walk the change against one standard at a time, and plan the refactor.
  2. Pin: add tests at consumption seams (where callers, users, or spec-named contracts observe the change) for behavior the intent requires.
     Each passes, and fails when that behavior is deliberately broken, after which the source is restored.
     A pin that fails against the current code has found a bug, fixed red-first in its own commit.
  3. Refactor: code and tests together, one commit per concern, the subject naming the standard or smell resolved, the full suite green at every commit.
     Weakening is forbidden: no changed expected value, loosened matcher, dropped assertion, or skip to make a refactor pass.
     A test that asserted structure rather than behavior is rewritten at a behavior seam.
  4. Prove: every test file added or changed passes the deliberate-break check, and every deleted test's behavior is shown pinned elsewhere.
- Scope: anything the refiner is confident improves the change, covering standards, design (deep modules, small interfaces, KISS, DRY, YAGNI), completeness (stubs, TODOs, placeholders, dead code, unhandled error, empty, and boundary paths, and a missing piece the intent leaves no doubt about), tests, bugs, and trunk under the protocol.
  It changes how, never what the spec decided.
  A slice-sized gap or an intent mismatch reaches the user only when it is major enough to halt.
- Orchestrator verification: the suite passes at the head, and the test files changed across refine's commits equal the report's test table.
- Render pass when the change touches a surface.
  Bar: the Design Requirements and `BRANDING.md`, plus the `ux-standards.md` floors measured on the rendered page.
  Failures resume the refiner, then one re-check.
- QA: one script mapped to the spec's done-when checks (spec mode) or the intent (ad-hoc), with the app already running.
  An issue resumes the refiner (a bug opens red-first), the suite reruns, the render re-check reruns when a surface changed, and QA returns.
  On confirmation, spec mode flips `built` → `done` and commits the flip.
- What the user sees: the commit list, one validation line, one tests-proven line ("12 tests added or changed, all proven"), one render line, and the QA script; beyond that, only halt-class items.

#### App lifecycle (both orchestrators)

- When the change touches a surface, the orchestrator launches the app in its checkout: a recorded `run-*` project skill when one exists, otherwise `pnpm dev` as a background task.
  It reads `.logs/dev-server.log` for readiness and the real URL, reuses a running server (`pnpm dev` reports its pid), and stops only a server it started, at the skill's end; for `refine` that is after QA.
- The orchestrator owns the server because it must outlive several checker runs, and nothing documents a background task started in a subagent outliving that subagent.
- A launch failure is told to the user once, with the cause and `/run-skill-generator` as the one-time fix; that run's render pass is skipped and noted.

#### `preflight`

- Review step 1 runs `/code-review high <base>...HEAD` in parallel with `code-reviewer`.
  The explicit level avoids the remembered effort setting, and the explicit range avoids the upstream-relative default scope.
  Never `ultra`, which is a billed cloud run only the user starts.
- When bundled skills are unavailable, it proceeds with `code-reviewer` alone and names the skip in the stop-point report and the PR's Review section.
- Fix commits are re-reviewed by `code-reviewer` only, through its existing re-review mode.
- Trunk findings stay surfaced at the stop point, as today, since the stop point is the end the user hears things at.
- Held context-file corrections add `docs/standards/`.
- The PR template gains `## Risk`: a level, the touch points from `code-reviewer`, and each trunk commit's skeptic verdict quoted from its body.
  High: a schema or migration, an auth or security path, or an interface with consumers outside the repo.
  Medium: any other trunk touch point.
  Low: the branch's own code only.
  `references/publish-and-ci.md` carries the composition and the levels, outside the skill body.

#### `docs/standards/`

- `ux-standards.md`, `frontend-styling.md`, `html-tables.md`, `transactional-email.md`, and `agent-facing-output.md` move from `.claude/rules/` with their filenames kept, so `BRANDING.md`'s bare `ux-standards.md` citations stay true.
- `javascript-typescript.md` holds the old rule's Types and Language sections, plus ESLint/Prettier and Turborepo script routing, whose mistakes are refactorable.
- `design-principles.md` moves from `docs/DESIGN_PRINCIPLES.md` and gains a "Deep modules, small interfaces" section. †
- Frontmatter: `applies-to:` carries each moved file's old `paths:` globs, quoted.
  No key means the standard applies to every change, which is how `design-principles.md` ships.
  The key is renamed from `paths:` so nobody mistakes it for auto-loading.
- The moved files lose their "Loads when a session reads a file matching the globs above…" paragraphs, and their relative links are repointed.
  `transactional-email.md`'s override is rewritten without the auto-load premise: on an email path it wins over `frontend-styling.md` and `html-tables.md`.
- `tdd` stays the single source of test quality, preloaded into `builder` and `refiner`.

#### `CLAUDE.md` (approved text)

- The BRANDING line loses its last sentence ("The UI/UX floors live in the `.claude/rules/` files … reads `ux-standards.md` by path before deciding anything about a surface.").
- The agent-facing-output line is deleted.
- The JS/TS section's rule link becomes:
  > - Use pnpm only: local bins run through `pnpm exec` and one-off Node through `pnpm exec node`, so both run on the pinned runtime; `npx` and `pnpm dlx` are denied to AI sessions, so hand the user a ready-to-run `pnpm dlx` command for a one-off remote tool.
  > - Retarget the Node pin as a set (`.nvmrc` exact, `engines.node` as `>=X.Y.Z <X+1`, `devEngines.runtime.version` exact), then `pnpm install` and commit the lockfile; read `scripts/setup/check-install.mjs`'s header before changing how the pin works, and move pnpm activation off Corepack in the same change when the target is Node 25 or newer.
- The Frontend and UI section's four links become:
  > - Build email templates to `docs/standards/transactional-email.md` from the first line: email clients force nested tables, inline styles, and a `600px` column, so a template started in flex or grid is a rewrite, not a refactor.
- The Skills line lists eight skills, with "`implement-spec` builds one to `built`" and "`refine` brings any branch up to the standards in `docs/standards/` and runs human QA".
- The `curate-context` line adds `docs/standards/` to the files that load it.

#### `curate-context`

- Description and scope add `docs/standards/`.
- Route gains the routing test: a rule every implementer must hold because getting it wrong first costs more than a refactor goes to `CLAUDE.md` as one line; a convention applied afterwards goes to the matching `docs/standards/` file.
  The styling and usability-floor routes point at their `docs/standards/` paths.

#### `tdd` (approved text)

- Seams: "Choose the seams before writing any test, aimed at the critical paths the spec or the intent names." replaces the sentence that confirms seams with the user.
- Anti-patterns gain **Shallow**: the test asserts existence, or that a call did not throw, instead of an outcome.
- The last rule keeps refactoring as a separate tidy step after green and replaces "with tests unchanged" with the refine rule: tests may be restructured, never weakened, with weakening defined as above.

#### Batteries

- `rules-frontmatter.battery.mjs` also checks `docs/standards/*.md` under the `applies-to:` key, with the same quoting and brace rules, and its header states both scopes.
- A new battery fails when `.claude/settings.json` denies `code-review` through a `Skill` rule, sets `disableBundledSkills`, or carries any `skillOverrides` entry for `code-review`.
  It follows `docs/standards/agent-facing-output.md` and the existing batteries' `ok` / `FAIL` shape.

#### Other ripple

- `sdd` and `brand-init` read `docs/standards/ux-standards.md` by path.
- `template-dev.md`: the design-surfaces clause points at `docs/standards/`, and the steering-docs list adds `docs/standards/` and `.claude/agents/`.
- `README.md`: What Ships (eight skills, seven agents, standards in `docs/standards/`) and the setup line ("swap the styling section of `docs/standards/frontend-styling.md` for your stack, or delete the frontend standards when you ship no UI").
  Its Node-pin note, which points at `CLAUDE.md`, becomes true.
- `.claude/skills/README.md`: the skills and agents lists, a Standards section replacing the Rules list, and the `built` lifecycle.
- `CHANGELOG.md` v0.1.0: the Skills, Agents, Rules, and Guards bullets, plus the PR template's Risk section.
- Existing implementation: `implement-spec`'s slice loop is stripped from its body and rebuilt as the `builder` agent, keeping its gate and workspace; the six standard-bearing rule files and `docs/DESIGN_PRINCIPLES.md` move; nothing else is removed.

## Evidence

- Subagents start with their own system prompt plus the delegation message and no conversation history, have `AskUserQuestion` stripped, start in the main session's working directory, load the `CLAUDE.md` hierarchy and project rules, preload skills through `skills:`, nest up to three layers, and resume with full history through `SendMessage`.
  This settles orchestrators in the main session, workers as named agents, `EnterWorktree` carrying workers into the worktree, and resume on `BLOCKED`.
- A skill with `context: fork` sees no conversation history and cannot pause for the user, which rules it out for skills with gates.
- `isolation: worktree` branches from the default branch rather than the session's `HEAD`, which rules it out for workers building on a spec branch.
- Local `/code-review` runs as a forked subagent with its own context, reviews commits ahead of upstream plus uncommitted work by default, accepts a ref range, reuses the last effort level typed when none is passed, takes no intent outside `ultra`, follows `CLAUDE.md`, and is model-invocable unless a `skillOverrides` entry or `disableBundledSkills` says otherwise.
  This settles adding it beside `code-reviewer` rather than replacing it, the explicit level and range, and the settings battery.
- `/simplify` is a cleanup-only review that applies its fixes directly, with no documented diff scope; the refiner covers its ground under the project's own standards.
- Invoking a skill or an agent needs no approval by default; only deny rules gate them.
  `.claude/settings.json`, `.claude/settings.local.json`, and `~/.claude/settings.json` carried no `Skill` deny, `skillOverrides`, or `disableBundledSkills` when checked.
- `/run-skill-generator` records a project's launch recipe once as `.claude/skills/run-<name>/`, which later agents follow, so a hard-to-launch project costs one setup rather than a user step per run.
- `scripts/dev/node-dev-server.mjs` runs one server per checkout, reports a running pid on a second start, and mirrors output to `.logs/dev-server.log`, so the orchestrator can launch, reuse, and read the URL without user help.
- Every standard plus `design-principles.md`, `tests.md`, and `mocking.md` totals about 33KB, roughly 9K tokens, so one refiner context holds every applicable standard and a per-standard fan-out buys nothing.
- Skill bodies at interview time run 32 to 71 lines, but with single lines up to 866 characters, so the raw count understates them.
  Reflowed to one sentence per line they hold roughly 40 to 60 sentences each before blank lines, far under the 500-line ceiling, so no slice is squeezed for room.

## References

- `.claude/skills/implement-spec/SKILL.md`: the slice loop that becomes the `builder` agent, and the gate and workspace that stay.
- `.claude/skills/preflight/SKILL.md` and `.claude/skills/preflight/references/publish-and-ci.md`: the Review step and PR body that gain `/code-review` and Risk.
- `.claude/skills/tdd/SKILL.md`, `tests.md`, `mocking.md`: the test-quality source both workers preload, and the three approved edits.
- `.claude/skills/curate-context/SKILL.md`: the scope and Route edits.
- `.claude/skills/sdd/SKILL.md` and `.claude/skills/brand-init/SKILL.md`: the `ux-standards.md` path reads to repoint.
- `.claude/agents/code-reviewer.md`: the pattern for brief-schema descriptions and read-only tool lists, and the agent being widened.
- `.claude/agents/docs-reviewer.md` and `.claude/agents/research-analyst.md`: further agent-file patterns.
- `.claude/rules/`: the six source files that move, plus `skill-authoring.md` (the orchestration line, the budget, gut-check prompts) and `template-dev.md` (the changelog and steering-doc rules).
- `docs/DESIGN_PRINCIPLES.md`: moves to `docs/standards/design-principles.md`.
- `docs/skill-quality.md`: frontmatter fields (`skills`, `disallowedTools`, `context`) and gut-check prompt craft.
- `CLAUDE.md`, `README.md`, `.claude/skills/README.md`, `CHANGELOG.md`: the ripple edits.
- `scripts/test/rules-frontmatter.battery.mjs`: the battery to widen and the shape for the new settings battery.
- `scripts/dev/node-dev-server.mjs`: the launch, reuse, and log contract the orchestrators rely on.
- `.github/PULL_REQUEST_TEMPLATE.md` and `.claude/settings.json`: the Risk section and the battery's input.
- `docs/notes/global-claude.md`: the trunk line already rewritten this session.

### Sources

- https://code.claude.com/docs/en/sub-agents: subagent startup context, `skills:` preload, nesting depth, `AskUserQuestion` removal, working directory and `isolation: worktree`, resume through `SendMessage`.
- https://code.claude.com/docs/en/skills: `context: fork` semantics, bundled `/run`, `/verify`, and `/run-skill-generator` recipes.
- https://code.claude.com/docs/en/code-review: local `/code-review` scope, targets, effort levels, model invocation, `skillOverrides`, and `/simplify`'s cleanup-only role.
- https://code.claude.com/docs/en/permissions: which tools need approval by default, and `Skill` and `Agent` rule syntax.

## Out of Scope

- The `template-sync` and `template-feedback` skills; a separate spec comes next. †
- Migrating any downstream project. †
- Tagging or releasing. †
- A commit-time adversary for branch-local changes; `preflight`'s reviewers cover them.
- Changing `preflight`'s trunk triage beyond adding the Risk section.
- Moving preflight's fixes into a named agent: preflight still writes fixes in its main session, which contradicts skill-authoring.md's orchestration line; it needs its own spec. †

## Rejections

- Freezing tests during refactors (no test edits in a refactor commit): rejected because good refactors improve tests alongside code; the real risk, weakening a test to pass, is guarded directly. †
- Mirroring `preflight`'s gate in `refine` (clean tree required, stops on spec status): rejected because it bleeds another skill's concerns into `refine`; the baseline commit covers the one need `refine` has. †
- Keeping refactors inside branch code and reporting trunk changes: rejected for confident trunk changes under the proof bar, two-agent review, and PR disclosure. †
- Making a worker its own adversarial reviewer through its proof bar: rejected because the author's tests cover only what it thought of. †
- Returning an unsettled seam as `BLOCKED`: rejected because seam choice is the builder's engineering call under a spec. †
- The user starting the app for render passes: rejected for orchestrator-owned launch. †
- A per-standard agent fan-out: rejected because context is not the constraint, restructuring needs one holistic judgment, and edits serialize anyway.
- `context: fork` skills: rejected because forked subagents cannot ask the user, and these skills have gates.
- A hook blocking main-session edits: rejected because it would also block legitimate main-session writes, such as `sdd` writing its spec.
- `/simplify` as a refine step: rejected because its scope is undocumented and it applies fixes outside the project's standards and commit discipline.
- Replacing `code-reviewer` and `docs-reviewer` with `/code-review`: rejected because it takes no intent, produces none of the contract outputs `preflight` and the PR need, cannot target a staged diff, and reviews no docs.
- Moving the defect lens out of `code-reviewer`: rejected because the trunk-change adversary needs it on a staged diff `/code-review` cannot target.
- A separate `adversary` agent file: rejected as a near-copy of `code-reviewer`.
- A numeric risk score: rejected as false precision; a level tied to named evidence says where to look.
- Recording skeptic outcomes in the spec or a separate file: rejected because ad-hoc runs have no spec and commit bodies reach `preflight` without chaining.
- `in-progress` as the post-build state: rejected because `implement-spec` resumes `in-progress` specs, so a finished build would read as half done.
- QA inside `preflight`: rejected because it would mix review with acceptance.
- `docs/standards/testing.md`: rejected because it would duplicate `tdd` and drift from it.
- A standards index file: rejected because it drifts; per-file `applies-to:` maintains itself.
- Keeping the `paths:` key in `docs/standards/`: rejected because it implies auto-loading that no longer happens.
- Before-and-after screenshot diffs in `refine`: rejected because the Design Requirements and `BRANDING.md` bar already fails a changed look, and QA follows immediately.
- `render-checker` owning the server: rejected because the server must outlive several checker runs.
- `isolation: worktree` for workers: rejected because it branches from the default branch, not the spec's branch.
