---
name: sdd
description: Spec-driven development interview. Grills the user one question at a time about a change to this codebase through three lenses at once, engineering (60%), product (25%), and design (15%), grounding facts in the code and sourced research, and always ends by writing an implementable spec to docs/specs/. Use whenever the user wants to plan, scope, spec, grill, or stress-test a feature, bug, chore, or refactor before building it, or says "spec this", "sdd", "let's plan", "grill me".
argument-hint: '[the ask to spec, or a docs/specs file to resume]'
---

# SDD

One session, one output: a spec in `docs/specs/` that a fresh session can build without re-deciding anything. The interview runs three lenses in parallel rather than as separate processes. Engineering carries about 60% of the attention and always runs; product carries 25% and runs only where the answer changes what gets built; design carries 15% and runs only when the change touches a user-facing surface.

## Open

Restate the ask in one paragraph with every assumption and every undefined point, then say "Speccing <subject>, until <objective>." When the argument is a `docs/specs/` file, grill the gap between what it claims and what the code shows, resolving each `TBD`.

## Interview

- One question per turn, the largest load-bearing decision first, with your recommendation and reasoning attached. A stack of questions is bewildering, and small answers get invalidated by later big ones.
- Facts are looked up, never asked. Orient on the stack first (`package.json`, runtime configs), read the code the change touches, and pull version-specific docs through Context7 (falling back to web search, then primary documentation) whenever a decision leans on library behavior. Verify the user's claims about the code and correct them with the file cited.
- Decisions are the user's. Put each one to them and wait. When the code or the research supports your recommendation, hold it under pushback and restate the case; drop it only for a new fact or an explicit move-on. Folding to an assertion the evidence contradicts is a failed session.
- Product lens: who has the problem, what they do today, what done looks like to them, what is deliberately out.
- Design lens, surfaces only: the one job the surface serves, what ranks first, which control carries each value, what sits behind disclosure. Hold the floors in `.claude/rules/ux-standards.md`, read by path since no source file opens here.
- Engineering lens: reference implementations already in the tree, touch points and their current signatures, shared types and their consumers (LSP find-references), the test seams, and what happens to the existing implementation.
- A claim that needs sourcing (a pattern, a competitor, a study, a pricing structure) dispatches the `research-analyst` agent in the background, announced in one line; keep grilling and weave the evidence in when it lands. Block only when the next question depends on it.

## Exit

Stop when the objective is met, not before or after, then write the spec from `assets/spec-template.md`; read `references/example-spec.md` first for altitude and shape. Name it `docs/specs/NNN-<slug>.md`, NNN being one past the highest number already there, and set `status: ready`.

- Every section that does not apply is omitted, never left as a header over nothing; a small ask yields a short spec.
- Slices are vertical: each a thin, demoable cut through every layer it touches, in build order, each ending in the observable check that proves it. Every requirement maps to a slice; an unmapped requirement is a dropped requirement.
- Architecture describes interfaces and contracts, not file paths or snippets, which go stale. References is the one place paths live.
- Anything still unknown stays `TBD` rather than invented content. Rejections and Out of Scope carry the session's residue so the next session does not re-litigate it.
