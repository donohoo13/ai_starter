# Brand research: the locked evidence base

Sourced findings behind `brand-init`'s method and `BRANDING.md`'s structure, gathered 2026-07-27 via a research-analyst pass during the interview that produced both. This file exists so no future session re-runs the research or re-litigates the structural decisions; edit it when better evidence lands, and carry the evidence grade with every claim.

Evidence grades: **studied** (a published study or primary vendor documentation), **practitioner** (agency/vendor writing, consensus but unmeasured), **thin** (single source, uncorroborated).

## Delivering brand guidance to AI

- LLMs cannot act on subjective brand language ("make it feel welcoming"); guidance converts to explicit rules, exact values, named vocabulary, banned phrases with replacements (Monigle), **practitioner**.
- OpenAI's own image-model prompting documentation recommends concrete material/texture/medium language and short labeled segments over adjective-heavy prose (OpenAI Cookbook), **studied** (primary vendor docs).
- Named style/brand anchors ("in the style of A24 posters") carry more specific meaning than generic adjectives and narrow model output better (Lummi), **thin**, but consistent with the above.
- Negative prompts describing undesired characteristics measurably improve generative output quality (arXiv 2403.07605, diffusion-model scope), **studied**, adjacent evidence: image models, not LLM text consumption. This is the empirical backing for the Anti-Goals section's weight.
- Free-text prompting alone produced generic, brand-nonspecific creative; structured inputs, separate branding, audience, and inspiration-board panels, improved brand alignment (arXiv 2504.14320, 6-participant formative study), **studied**, low-N. This is the backing for both the structured doc and the mood-board gate.
- Shipped past-work examples steer output harder than trait lists (Superside), **practitioner**; the basis for the one-exemplar-per-context rule in Voice and Copy.
- No NN/g, Baymard, or Material/Polaris/Carbon guidance exists on writing brand guidelines for LLM consumption; the field is agency/vendor-tier only, and no controlled study ranks adjectives vs anchors vs tokens vs negative constraints as steering devices. Every ranking claim above is graded accordingly, **literature gap, stated so it is not mistaken for settled science**.

## Mood boards in brand derivation

- NN/g warns that boards loaded with product screenshots collapse into competitive-reference boards and prematurely focus on concrete outcomes; boards stay at mood/tone/color/texture altitude (NN/g, "Mood Boards in UX"), **studied** (primary practitioner source). This is the anti-imitation rule in the curation guidance.
- The style-tile lineage (Samantha Warren, 2012; still the taught method) treats the mood board as deliberately vague scaffolding distilled into progressively concrete artifacts, **practitioner**, decade-plus adoption. This is the distill-and-set-aside method the gate implements.
- NN/g's competing framing treats mood boards as persistent references consulted throughout, **studied**; the literature never reconciles the two. `brand-init` follows the style-tile reading because its runtime consumer generates code and copy, which distilled text steers, not images; the board persists in `docs/branding/moodboard/` only as provenance, and the finished doc never references it.
- Shipped-product references (Mobbin, real apps) translate to working products; Dribbble's polished unshipped mockups are harder to translate, **thin**. Hence the split: Dribbble for mood, shipped products for Reference Anchors.
- Committed images of others' work are copyrighted; a private repo holding them for internal reference is common practice, a public repo is redistribution; public repos gitignore `docs/branding/moodboard/` so the board stays local at the path the gate checks.

## Structural decisions this produced

Recorded so future edits know what was deliberate; the session that settled these considered and rejected the alternatives named.

- **Two-tier fill grammar** (identity absolute, steering anchored): strictness on identity axes costs no design quality because they are picked once, not per surface; freedom there is incoherence. Steering sections stay free precisely where good per-surface design happens. Rejected: one uniform grammar (leaves "clean and modern" legal), full steerability (incoherent identity).
- **Anchored adjectives**: every steering adjective ties to a named shipped product or a "shows up as" consequence; unanchored adjectives are the under-constraint failure the evidence above names.
- **One exemplar per voice context**: exemplars steer hardest, but a copy library stales and turns constraints into content.
- **Brand strategy lives in BRANDING.md Foundations, not a separate doc**: the four-document framework common in brand-strategy writing was rejected because every design session reads this one file as its authority, and `docs/company/company-overview.md` is chartered narrative-only. Landing-page and per-surface specs were likewise rejected as doc content; they belong in the spec for that surface.
- **Images, not URLs, in the mood board**: companies and sites change or vanish under a saved link; committed images are stable, and the distillation interview supplies the articulation a written manifest would have carried.
- **Sole ownership**: no other session derives brand decisions inline; two owners of one outcome drift.
