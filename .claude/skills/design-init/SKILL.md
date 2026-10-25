---
name: design-init
description: One-time brand and design-system initialization. Interviews the user from the bracketed DESIGN.md scaffold, written in Google's design.md format, to a governing document, product context, visual thesis, personality, and shipped-product anchors, identity tokens (colors by role, typography, radius, themes, logo) in lint-checked front matter, anchored steering sections, component rules, voice, and do's and don'ts, opening on a mood-board gate over docs/design/moodboard/. Use once, on a new project whose DESIGN.md is still placeholder-bracketed, when the user says "set up the brand", "set up the design system", "fill in DESIGN.md", "derive the brand", or "run design-init". Later brand changes are ordinary edits to the doc, not a re-run.
argument-hint: "[optional: the product or brand direction to derive from]"
---

# Design Init

The one-time brand and design-system derivation.
Brand decisions made as side effects of building one surface (a palette picked for a dashboard, a voice invented for one error message) are exactly the drift `DESIGN.md` prevents; settling the identity once means every later surface inherits it.
Read `references/brand-research.md` before the first question: it carries the evidence base and the rationale behind the doc's structure, so neither gets re-derived in session.

## The mood-board gate

Check `docs/design/moodboard/` for image files and state what was found; the path is the user's choice, never silent:

- **Images present**: run the interview with distillation as the aesthetic backbone.
- **Absent or empty**: one confirm.
  Stop and curate (recommended): hand over the guidance below and end, deriving in a fresh session once the board exists.
  Or continue without: ask for shipped products the user admires per axis (density, warmth, type character, motion) and what they take from each.

Curation guidance: a focused handful of images at mood, tone, and texture altitude, since a board of product screenshots pulls toward imitation; shipped products enter as names for Reference Anchors, never as screenshots; in a public repo, gitignore the moodboard directory.

## Frame

- **Persona**: a brand partner, strategy, visual identity, and voice in one seat.
  One question at a time, biggest first, recommendation and reasoning attached; decisions are the user's.
- **Fact sources**: `references/brand-research.md`; `docs/company/company-overview.md` for audience, positioning, and existing narrative; the app's CSS for values already shipped, which become front-matter tokens rather than a second source; `docs/standards/ux-standards.md`, read by path, for the floors identity choices must clear.
  Claims about competitors or market conventions dispatch the `research-analyst` agent in the background, announced in one line.

## Distillation

Per image or cluster, ask what draws the user to it, then extract attributes (mood, color temperature, density, type character, surface treatment), never a layout or palette wholesale.
An image the user cannot articulate a pull for is dropped.
The finished doc never references the board.

## The interview

Fill `DESIGN.md` in the order below; its binding note and authoring comment carry the fill grammar, so the doc governs its own filling.

1. **Overview**: product context (audience, primary job, promise) first, since it filters everything below.
   Then the two-paragraph thesis closing on its refusal, 3-5 personality traits each with a visible consequence, 2-4 shipped-product anchors with take and leave lines, and 5-7 key characteristics a reviewer could check from a screenshot.
2. **Identity**: Colors, Typography, Shapes, and Logo, decided together because contrast pairs cross them.
   Every role gets an exact front-matter value; the themes decision adds a `-dark` sibling per color role when both themes ship.
   AI-default attractors (warm cream with a serif and terracotta accent, near-black with one acid accent) are defaults rather than choices; spend free axes on the product's own world.
3. **Steering sections**: Layout with its spacing scale, Elevation & Depth, Hierarchy & Emphasis, Motion, imagery and icons, and Data Visualization, deleted when the product has no charts.
4. **Components**: anatomy and rules for each shipped component, the 1-3 signature components added to both the front matter and the prose, and the compositions the product will not build deleted.
5. **Voice & Copy**: anchored traits, register bounds, casing, use and never vocabulary, one exemplar per fixed context.
6. **Do's and Don'ts last**, harvested from every direction the user rejected above, each Don't paired with its Do and the section that grants it; negative constraints are the doc's highest-leverage device.

## Exit

Write the filled `DESIGN.md` in strict present tense with absolutes and no bracket left standing.
Run `pnpm exec designmd lint DESIGN.md` and resolve its findings until the authoring comment's done bar holds.
Then delete the authoring comment, as it directs, and offer to delete `.claude/skills/design-init/`: the doc is now the record, and later brand changes are edits to it.
