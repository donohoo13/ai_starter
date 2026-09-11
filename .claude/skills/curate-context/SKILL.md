---
name: curate-context
description: Curation discipline for the prescriptive context files — every CLAUDE.md and CLAUDE.local.md at any depth (including the user-global ~/.claude/CLAUDE.md), README.md, BRANDING.md, and path-scoped rules under .claude/rules/. Use whenever a session is about to create or edit one of these files, whatever brought the edit — a convention to record, a doc correction, another skill's follow-through, or an edit arriving mid-task with nobody naming this skill. The trigger is the file itself: an Edit or Write whose path is one of those names loads this skill first, and nothing else enforces that. Also the distillation path: use when the user says "codify", "capture this convention", "add this to CLAUDE.md", "remember this convention", or "we should document this". Ceremony scales with the edit class; HITL means no model-invented content lands unseen. Descriptive docs (CONTEXT.md, CONTEXT-MAP.md, ARCHITECTURE.md, docs/adr/) belong to domain-modeling — hand off, never write them here.
argument-hint: '[optional: the edit or lesson to consider]'
---

# Curate Context

The curation discipline for the prescriptive context files — the docs that steer future behavior rather than describe the system: every `CLAUDE.md` and `CLAUDE.local.md` (root, nested per-package, and the user-global `~/.claude/CLAUDE.md`), every `README.md`, path-scoped rule files under `.claude/rules/`, and the brand foundation `BRANDING.md`. Every edit to one of these goes through this skill.

- AI context files (`CLAUDE.md`, `BRANDING.md`, the `.claude/rules/` files) state what is true TODAY in strict present tense. No aspirational language ("we'd like to", "try to") and no preferential language ("prefer", "prioritize", "when possible"): a soft verb leaves the exception to the model's discretion. Write rules as absolutes and document exceptions at point of use.
- Write rules for AI as positive instructions: state the action to take and the concrete check that grounds it, not the behavior to ban; scope each rule to the surfaces it governs; when a rule meets uncertainty, grant explicit permission to say "unknown" rather than guess.
- Nothing blocks a raw edit: the load rests on this skill's description triggering on the file names and on the `CLAUDE.md` rule that states the same thing, which is why both spell the paths out.
- Two stated carve-outs: `BRANDING.md`'s **steering sections** open to a loaded `grill-product` session, which legitimately writes them mid-interview under its own discipline, and everything under `.claude/skills/` (its README included) is `skill-creator`/`guard-skill-edit` territory — written only with that gate loaded, never under this skill alone.
- The carve-out names `grill-product` alone and reaches steering sections alone, and both bounds carry weight. `grill-design` is excluded because it refuses to write the brand doc at all — brand decisions taken as a side effect of one surface are the drift that doc exists to prevent, so naming it here would grant a permission it declines. Identity sections are excluded because the blast-radius gate in Step 5 is the whole point of treating them differently, and a lens writing them mid-interview reaches the file without passing it.
- `.claude/rules/ux-standards.md` is closed to growth and takes no mid-interview append from any lens, because a floors file a design session can extend is how one accretes a project's surfaces one at a time until the floors are buried in them.
- The descriptive docs — `CONTEXT.md`, `CONTEXT-MAP.md`, `ARCHITECTURE.md`, `docs/adr/` — are `domain-modeling`'s territory: hand off rather than write them, and that side of the seam holds the same way, through `domain-modeling`'s own description and the same `CLAUDE.md` rule.

The hard part is not writing bullets. It is deciding what deserves to exist. A rule is paid for by every future session that loads the file, so the cost is real and recurring. Default to writing nothing; when writing, hold the whole edit as close to zero net growth as the file allows. Forcing output is the primary failure mode of this skill.

## Entry paths

- **A governed edit is on the table.** This session is about to create or change one of the files above, for any reason — a convention surfaced during work, the user asked for a doc update, another skill's follow-through lands a bullet. This is the common path, and it fires whether or not anyone said "codify".
- **Distillation.** The user asks to distill the session ("codify", "capture this convention", "add this to CLAUDE.md", "we should document this") or accepts a suggestion to. Suggest at most once per session, and only when a genuine candidate surfaced — an undocumented convention got violated, a real gotcha came out of debugging. Never suggest it as a session-end ritual: an offer that fires regardless of whether anything happened trains the user to ignore it.

## Triage — ceremony scales, discipline doesn't

Classify the proposed edit first; the class decides how much of the process below runs. Three checks apply to every class and never collapse: verify each fact against the current code (never conversation memory alone), route to the correct file and scope (Step 3), and judge the edit's net size (Step 5).

- **New rule content** — a new bullet, a new constraint, a broadened rule → the full process: attribution when friction-born (Step 1), the admission bar (Step 2), routing (Step 3), drafting (Step 4), presentation and approval (Step 5).
- **Correction or factual update** — a renamed command, a moved path, a changed count, wording that changes nothing any session would do → verify the new fact, hold net growth at zero or below, apply.
- **Deletion** — cheap but never silent: state what dies and why before it goes; removing once-approved content is the user's call.

Who initiated the edit sets the approval ceremony, and the HITL invariant is precise: **no model-invented content lands unseen** — not "every edit needs a fresh yes".

- **Model-initiated** — anything this session proposed → each candidate lands only after the user approves it (Step 5).
- **User-directed** — "add X to CLAUDE.md" carries its own approval: apply without a second permission round, but run the same bar first and push back when X fails it ("the linter already enforces this — still want it in prose?"). The user can overrule; a skill that only polices model-initiated edits is a rubber stamp on user-directed bloat.

## Step 1: Attribute friction-born candidates

This step applies to candidates born from a friction moment in the session — a correction, a redo, a "no, not like that", a roadblock backed out of. (A user-directed rule has no friction moment to root-cause; it enters at Step 2.) The instinct is to convert each moment into a rule so it "never happens again". Resist that: attribute the root cause first, because only one cause justifies a durable rule.

- **(A) The prompt steered you wrong.** The request was ambiguous, under-specified, or a one-time preference. A generic future prompt would not reproduce the misstep; a rule here satisfies a sample size of one. **Do not codify — say so and say why.** If the ambiguity reflects a real recurring decision, document the _decision_ (often `domain-modeling` territory, Step 3), not the steering.
- **(B) A real convention was undocumented.** The code already follows a pattern you violated because nothing told you, or the user revealed a standing constraint. A future session lacking this context repeats the exact mistake. **The only real candidate.** It still faces Step 2.
- **(C) You simply erred.** Adequate context existed and you misread it. A rule that patches a one-off model error is noise every future session pays for. **Do not codify.** Own the mistake instead of memorializing it.

Be opinionated. If the user expects a rule from a moment you judge (A) or (C), say it does not belong and why — a short disagreement beats a defensively-added bullet. The user can always overrule.

## Step 2: The admission bar

A candidate rule must be something an AI **cannot reliably infer and would plausibly get wrong in this repo**: a convention established during implementation, a gotcha found while debugging, a non-obvious standard. Reject, even from cause (B):

- **Already enforced by configuration.** `settings.json` permissions and hooks, lint rules, formatter, the type system. Enforcement outranks prose; restating an enforced behavior as a bullet buys nothing and drifts when the config changes.
- **Already documented anywhere a future session can read.** Not just context files: project and plugin skills, and MCP tool descriptions count — a gotcha restated verbatim from a skill the session had read, or a fact sitting in a tool's own description, is duplication. The test is what a future session has access to, not what is literally a "context file".
- **Subsumed by a general rule** — existing, or proposed in the same edit. When following the general rule reveals the specific fact ("call `search` first" reveals what `search` returns), the specific rule is noise.
- **Generic best practice** or restated framework default.
- **Transcript-of-today.** Anything that reads as a record of this session rather than a rule for unrelated future ones; the test is reusability across sessions that share nothing with today's.

Verify each surviving candidate against the current code before writing it — read the file, grep the pattern — and resolve every pointer to a real `path` or `path:line` so it does not drift.

## Step 3: Route to the narrowest correct destination

Wrong placement is its own failure: an app-specific rule in a root file pollutes every other session, and a rule in the wrong _kind_ of file never gets read. Before routing, **discover the actual layout** — glob for every `CLAUDE.md`, `CLAUDE.local.md`, and `README.md`, plus `.claude/rules/`, the design docs, and the domain docs — rather than assuming; this skill ships with the starter template, and template and spawned projects lay these files out differently.

**What kind of content?**

- **Domain vocabulary, a hard-to-reverse decision, or an engineering-shape fact** → `domain-modeling`'s job (`CONTEXT.md`, `docs/adr/`, `ARCHITECTURE.md`). Hand off rather than write; no hook holds this seam, so both skills' descriptions and the `CLAUDE.md` context-edit rule are the whole mechanism from either side. If `domain-modeling` was active this session (the grill lenses run it), whatever it already captured counts as documented — route only the residue.
- **An imperative rule aimed at the AI** — it changes what the model does in a future session → the nearest enclosing `CLAUDE.md`. A rule about brand, visuals, styling, or usability routes by the UI bullet below whatever else it also is, because every one of those is an imperative rule aimed at the AI and this bullet would otherwise catch them all first — landing a UX floor in a file that loads at launch in every session, including the backend ones, which is a worse home than the file it was routed away from.
- **A procedure a human performs** — setup, onboarding, auth flows, running things → the `README.md` nearest the code it serves, next to its related steps. The test is who executes it: per-developer OAuth scope selection is README material even when the AI discovered it, because the model cannot perform it and the human must.
- **A brand, visual, or UX rule** — route by what the rule governs, because these destinations have opposite lifecycles and only some of them grow. Getting this split wrong is how a floors file fills with one project's surfaces.
  - **A choice this project makes that another could reasonably make differently** — palette, type, viewport posture, the spacing scale's base unit, density, motion character, voice → `BRANDING.md`.
  - **A styling convention the project's stack imposes** — units, the styling system's idioms → `.claude/rules/frontend-styling.md`.
  - **A universal usability or accessibility floor** → nowhere. `.claude/rules/ux-standards.md` ships complete, every rule in it carries a source, and it is closed to growth. A floor genuinely missing from it is a finding about the template rather than a line to append, and `/template-feedback` is its channel.
  - **One surface's hierarchy, layout, controls, or disclosure** → that surface's artifact in `docs/designs/`, authored by `grill-design`. A composition is never a context file: it governs one screen, and a context file is paid for by every session.
  - **A pattern that has now proven itself across three surfaces** → a component, and the channel is `/capture-task` for the extraction, offered once per the `CLAUDE.md` capture rule. Reuse is recorded in code, where the Rule of Three already governs it and the next surface inherits it by importing rather than by reading a description of it — but a destination with no channel is a lesson that exits the process unwritten, so this bullet names one like its siblings do.

**At what scope?** The nearest enclosing file to the code the rule governs — a rule about one package belongs in that package's `CLAUDE.md` or `README.md`, not the root. If only a broad file exists but the rule is package-specific, place it in the narrowest available file and note the better future home. When unsure, choose narrower, then pick the placement by how the rule has to load:

- **Read-triggered placements cost nothing until relevant and can silently never fire:** a nested `CLAUDE.md` and a `.claude/rules/` file with `paths:` frontmatter both load when Claude _reads_ a matching file.
- That covers every `Edit`, which requires a prior read of the file it edits, and misses two routes that reach a matching path without one — a `Write` creating a new file, and any Bash write (`sed -i`, a `cat >` heredoc, a formatter run in place).
- A nested file also stays unloaded after `/compact` until the next read there.
- **Guaranteed placements load at launch and cost context in every session:** a `.claude/rules/` file with no `paths:` frontmatter, which loads with the same priority as `.claude/CLAUDE.md`, or an `@path` import from the root file, which composes a file that outgrew one topic without reducing what it costs.
- A rule that must hold while work creates files at its paths, or edits them through Bash, takes a guaranteed placement — or keeps the read-triggered placement and names itself in a guaranteed file, so the uncovered routes have somewhere to read it from.
- In a repo shipping `project-init`, a new `.claude/rules/` file — or a `paths:` change to an existing one — updates `project-init/references/fork-points.md` in the same change — with `skill-creator` loaded first, since the manifest lives under `.claude/skills/` and the gate denies the edit otherwise — per that manifest's own contract: nothing else routes a rules file there (`skill-creator`'s landing checklist covers skill couplings only), which is how the last one shipped unmanifested and rode into a stack-mismatched destination.

**Which layer owns it?** A lesson about how the user collaborates or wants to be spoken to — register, persona, pushback style — is a property of the user, not the repo: offer it for `~/.claude/CLAUDE.md`. A personal, project-scoped preference that should not be committed belongs in `CLAUDE.local.md` beside the project file. A genuinely two-natured rule may live in both layers deliberately, wordings aligned, with an explicit precedence clause naming which wins when they could collide — two contradictory absolutes loaded together make the model silently pick one. Claude's auto memory is never a curation target: a durable convention lives in these files, where every session and teammate finds it, not in one machine's memory directory.

## Step 4: Draft

- **Imperative voice, present tense.** No "we decided", "going forward", "always remember".
- **Front-load the constraint**, then the _why_ only when non-obvious — the why is what lets a future model generalize instead of following blindly.
- **State the action, not the ban.** Name the concrete act that satisfies the rule — the command to run, the file to check, the replacement behavior — and when the rule governs uncertainty, grant explicit permission to say "unknown" rather than guess. A bare prohibition is the wording most likely to be ignored or over-applied.
- **Scope the surfaces.** When a rule could bleed (register, tone, formatting), say where it applies — conversation, code, docs, commits.
- **Point at a living example** with `path` or `path:line` rather than pasting a snippet; only cite a file that cleanly demonstrates the convention.
- **Match the target file's tone and density** (read it first). Write long prose as single continuous lines per the repo markdown convention.
- **Maintainer notes ride free in HTML comments.** Claude Code strips `<!-- -->` comments before injecting a CLAUDE.md, so editor-facing rationale can sit beside a rule at zero context cost. Only for notes to future editors — the why that lets the model generalize must stay in loaded text.
- Avoid `ALWAYS`/`NEVER` shouting; reaching for it usually means the why is missing.

## Step 5: Present, then apply

**Judge the edit whole before presenting it: net line growth.** Every bullet can be individually defensible and the edit still bad — twelve defensible bullets is how a context file dies. Prefer rewriting an existing line to carry the new constraint over appending a sibling; state the net count with the proposal. Zero net growth with the lesson landed is the benchmark, not the exception.

**An edit to `BRANDING.md`'s identity sections reports its blast radius before it asks.** Those sections — Brand Foundations, Themes, Color System, Typography, Logo, Shape — are the tier the doc's own preamble calls absolute, and a change to one of them is wrong on every surface in the product until someone notices, which no other context-file edit is. Read the roster from that preamble rather than from this line when the two disagree; the doc owns its own tiers, and Brand Foundations belongs on it precisely because it is the filter every later section passes through. So the ask arrives with the reach attached: grep the token across the theme CSS and the components, say how many call sites and which surfaces it touches, and name the `docs/designs/` artifacts that cite it. Then ask.

- Steering-section edits keep the ordinary ceremony. A gate that fires on every brand edit trains the reflexive yes, which is `ux-standards.md`'s own interruption-hierarchy rule turned on this process.
- The report is what makes the confirmation mean something. A bare "change the primary to X?" gets a yes; the same question carrying "47 call sites across 9 surfaces, and the compare artifact cites it by name" gets a decision.
- After the confirm, offer `/capture-task` once, with the dependency list as the task's requirements — the list is already written by then, and throwing it away means someone rebuilds it by hand when the retreatment work starts. Suggest once and drop it if the user does not bite, per the `CLAUDE.md` capture rule.
- Where the grep cannot run — no theme file yet, no components yet — say that plainly rather than reporting a clean radius. An unrun check and a genuinely empty one read identically in a one-line answer, and only one of them is safe.

Presentation scales with triage: a correction or deletion is one line — the diff and its why. New rules and distillation get the full deliberation, including what you rejected — that is where "picky" becomes visible:

- **Curate** → the exact bullet(s), target file and heading, net line count, and a one-line rationale kept out of the bullet itself.
- **Reject** → the candidate and its ground (A / C / enforced / documented / subsumed / generic / transcript), one line each.
- **Hand off** → candidates routed to `domain-modeling`, so the user can pick that up next.

Apply per the approval rules in Triage, appending by default: insert approved text under the right heading and leave surrounding content as it stands, because the user approved exact text, not a rewrite. This apply step is the documented point-of-use exception to the prose restatement rule in CLAUDE.md Standards, and during an apply this routing wins over that rule's same-change restatement. Three cases are not appends, named here so the default does not read as absolute:

- A candidate already implied by an existing bullet strengthens that bullet instead of adding a near-duplicate.
- A candidate that contradicts an existing bullet halts — surface both statements, let the user pick the survivor, then land the winner.
- A target file whose decay the apply exposes (stacked near-duplicates, contradictions, run-on accretion) gets flagged as a restatement candidate for its own visible pass instead of receiving another bullet on the pile.

One whole-file exception is sanctioned at point of use: `project-init`'s approved tailoring plan lands its merged `CLAUDE.md` rewrite under this skill loaded, with the itemized plan standing in as the per-candidate approval.

## Quality checks

- A project-specific convention aimed at a global file (`~/.claude/CLAUDE.md`) is a routing mismatch — flag it and route to the project file.
- Internal docs (`CLAUDE.md`, `BRANDING.md`, the `.claude/rules/` files) are exempt from the em-dash ban, but match each file's existing punctuation style.
- Before finishing, reread the edit as a future session with no memory of today. A line that does not change what that session would do gets cut.

$ARGUMENTS
