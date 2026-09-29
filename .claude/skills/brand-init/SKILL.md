---
name: brand-init
description: One-time brand initialization. Interviews the user from the bracketed BRANDING.md scaffold to a governing document, brand foundations (audience, promise, positioning), identity tokens (palette, typography, logo, shape, themes), anchored steering sections, four-part voice, and anti-goals, opening on a mood-board gate over docs/branding/moodboard/. Use once, on a new project whose BRANDING.md is still placeholder-bracketed, when the user says "set up the brand", "fill in BRANDING.md", "derive the brand", or "run brand-init". Later brand changes are ordinary edits to the doc, not a re-run.
argument-hint: "[optional: the product or brand direction to derive from]"
---

# Brand Init

The one-time brand derivation. Brand decisions made as side effects of building one surface (a palette picked for a dashboard, a voice invented for one error message) are exactly the drift `BRANDING.md` prevents; settling the identity once means every later surface inherits it. Read `references/brand-research.md` before the first question: it carries the evidence base and the rationale behind the doc's two-tier structure, so neither gets re-derived in session.

## The mood-board gate

Check `docs/branding/moodboard/` for image files and state what was found; the path is the user's choice, never silent:

- **Images present**: run the interview with distillation as the aesthetic backbone.
- **Absent or empty**: one confirm. Stop and curate (recommended): hand over the guidance below and end, deriving in a fresh session once the board exists. Or continue without: ask for shipped products the user admires per axis (density, warmth, type character, motion) and what they take from each.

Curation guidance: a focused handful of images at mood, tone, and texture altitude, since a board of product screenshots pulls toward imitation; shipped products enter as names for Reference Anchors, never as screenshots; in a public repo, gitignore the moodboard directory.

## Frame

- **Persona**: a brand partner, strategy, visual identity, and voice in one seat. One question at a time, biggest first, recommendation and reasoning attached; decisions are the user's.
- **Fact sources**: `references/brand-research.md`; `docs/company/company-overview.md` for existing narrative; the app's CSS for token values already real; `.claude/rules/ux-standards.md`, read by path, for the floors identity choices must clear. Claims about competitors or market conventions dispatch the `research-analyst` agent in the background, announced in one line.

## Distillation

Per image or cluster, ask what draws the user to it, then extract attributes (mood, color temperature, density, type character, surface treatment), never a layout or palette wholesale. An image the user cannot articulate a pull for is dropped. The finished doc never references the board.

## The interview

Walk `BRANDING.md` top-down; its preamble carries the fill grammar, so the doc governs its own filling.

1. **Foundations**: audience, promise, positioning, messaging pillars. These filter everything below.
2. **Aesthetic thesis, personality, anchors**: one paragraph of what it looks like and refuses; 3-5 adjectives each with how it shows up; 2-4 shipped-product anchors with take and leave lines.
3. **Identity tokens**: palette, type roles, logo rules, shape, themes, as exact values verified against the contrast floors. AI-default attractors (warm cream with a serif and terracotta accent, near-black with one acid accent) are defaults rather than choices; spend free axes on the product's own world.
4. **Steering sections**: hierarchy instruments, layout, density, surfaces, motion, data visualization, imagery and iconography.
5. **Voice**: anchored traits, register bounds, use and avoid vocabulary, one exemplar per fixed context.
6. **Anti-goals last**, harvested from every direction the user rejected above; negative constraints are the doc's highest-leverage device.

## Exit

Write the filled `BRANDING.md` in strict present tense with absolutes and no bracket left standing. Then offer to delete `.claude/skills/brand-init/`: the doc is now the record, and later brand changes are edits to it.
