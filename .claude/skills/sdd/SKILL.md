---
name: sdd
description: Spec-driven development interview. Reads the codebase first, read-only, and presents the files the change will touch and why, then interviews the user in rounds of grouped questions, product first, engineering second, design last, grounding facts in the code and sourced research, and always ends by writing an implementable spec to docs/specs/. Use whenever the user wants to plan, scope, spec, grill, or stress-test a feature, bug, chore, or refactor before building it, or says "spec this", "sdd", "let's plan", "grill me".
argument-hint: "[the ask to spec, or a docs/specs file to resume]"
---

# SDD

One session, one output: a spec in `docs/specs/` that a fresh session can build without re-deciding anything.
The interview opens on facts from a read-only reconnaissance, then runs product, engineering, and design in that order, so each lens builds on what the one before it settled.

## Open

Restate the ask in one paragraph with every assumption and every undefined point, then say "Speccing <subject>, until <objective>."
When the argument is a `docs/specs/` file, grill the gap between what it claims and what the code shows, resolving each `TBD`.

## Reconnaissance

Read-only, before the first question, so the interview opens on facts rather than guesses.

- Orient on the stack (`CLAUDE.md`, `package.json` and runtime configs, `.claude/skills/README.md`), sweep for touch points with Explore agents, then read the files that matter directly.
- Present a touch map: each file or symbol, why it is involved, its current shape, the consumers of anything shared (LSP find-references), the risk, and the reference implementation already in the tree to mirror.
- Never run anything with side effects.
  When seeding data, running a job, hitting an endpoint, or a console session would teach more, hand the user the exact command and what it would show.
- Facts are looked up, never asked.
  Verify the user's claims about the code and correct them with the file cited.
  Library behavior comes from version-specific docs through Context7, falling back to web search, then primary documentation.

## Interview

- Rounds, not single questions.
  A round groups three or four questions that stem from one topic or are tightly coupled, each with your recommendation and reasoning, so the user answers without switching context.
  The most load-bearing question opens the round because its answer prunes the most branches; later rounds branch on earlier answers, and a small decision waits until the big one that could invalidate it is settled.
- Lenses run in order, and all three are accounted for; a lens that does not apply still gets a one-line disposition in the spec.
  Product first: who has the problem, what they do today, what done looks like to them, what is deliberately out.
  Engineering second: contracts, test seams, blast radius, and what happens to the existing implementation.
  Design last and brief: the one job the surface serves, what ranks first, which control carries each value, what sits behind disclosure, held to the floors in `docs/standards/ux-standards.md` and the identity in `DESIGN.md`, both read by path.
- Decisions are the user's.
  Put each to them and wait.
  When the code or the research supports your recommendation, hold it under pushback and restate the case; drop it only for a new fact or an explicit move-on.
  Folding to an assertion the evidence contradicts is a failed session.
- When a design decision is visual (competing layouts, a flow, a density call), show it rather than describe it: render the options side by side as one HTML page and continue from the user's comments.
  Publish it with the harness's private page tool when one exists; otherwise write it to the gitignored `.review/` folder and hand the user the path to open.
  The page is a review surface and the spec stays the record, so every decision it settles lands in the spec.
  Mockups only, never secrets, customer data, or security findings, because a published page leaves the machine.
- A claim that needs sourcing (a pattern, a competitor, a study, a pricing structure) dispatches the `research-analyst` agent in the background, announced in one line; keep interviewing and weave the evidence in when it lands.
  Block only when the next question depends on it.

## Exit

Stop when the objective is met, not before or after, then write the spec from `assets/spec-template.md`; read `references/example-spec.md` first for altitude and shape.
Name it `docs/specs/NNN-<slug>.md`, NNN being one past the highest number already there, and set `status: ready`.

- A section that does not apply is omitted, never left as a header over nothing, except Product and Design, which keep their one-line disposition; a small ask yields a short spec.
- Slices are vertical: each a thin, demoable cut through every layer it touches, in build order, each ending in the observable check that proves it.
  Every requirement maps to a slice; an unmapped requirement is a dropped requirement.
- Architecture describes interfaces and contracts, not file paths or snippets, which go stale.
  Its blast-radius line names the shared code the change touches and every caller affected, or says none is shared.
- The Touch Map is the one place paths live, carried over from reconnaissance: each path with its role in the change, its current shape, and its risk.
- Anything still unknown stays `TBD` rather than invented content.
  Rejections and Out of Scope carry the session's residue so the next session does not re-litigate it.
