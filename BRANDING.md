# Brand Design Principles

Brand identity for this project. Filled sections are fixed constraints: any session making a brand or surface decision reads this file first and designs inside them.

- Bracketed placeholders mark axes not yet decided; the one-time `brand-init` skill fills them, and no other session derives brand decisions inline.
- This file stays thin and tightly curated: it carries binding constraints only, and a line earns its place by changing what a design session renders — an overgrown brand doc steers no better than an empty one, so additions strengthen an existing line before appending a sibling.
- The app's CSS is the source of truth for actual token values; read it before quoting any value in code.
- In monorepos, a per-app `BRANDING.md` (e.g. `apps/<app>/BRANDING.md`) overrides or extends this file.

Two tiers govern how sections bind:

- **Identity sections** — Brand Foundations, Themes, Color System, Typography, Logo, Shape — are absolute: exact values and fixed facts, never reinterpreted per surface, because freedom on identity axes is incoherence, not creativity.
- **Steering sections** — everything else — direct judgment without dictating outcomes, and every adjective in them is anchored: tied to a named shipped product ("density of Linear") or a "shows up as" consequence in the interface, because an unanchored adjective ("clean", "modern") steers nothing.
- In every section, balance grants against restraints: every restraint names its sanctioned alternative ("never X; reach for Y"), because an agent given only prohibitions ships the null design, and the null design of a data app is a spreadsheet.

## Brand Foundations

- **Audience**: [who this product speaks to and the problem they bring, one line]
- **Promise**: [the outcome or feeling every interaction delivers, one line]
- **Positioning**: [the category and the one way this product wins in it, one line]
- **Messaging pillars**: [2-4 repeatable themes that marketing and product copy return to]

[these four are the filter every later section passes through; narrative depth lives in `docs/company/company-overview.md`, which holds no rules]

## Aesthetic

[the one-paragraph visual thesis: what this product looks and feels like, and what it refuses to look like]

## Reference Anchors

[2-4 shipped products, each with what this brand takes from it and what it leaves — "take Linear's density, leave its monochrome". Anchors calibrate the steering sections as inspiration, never a target to copy; shipped products only, because polished unshipped concepts (Dribbble mockups) don't survive contact with real constraints]

## Brand Personality

[3-5 adjectives, each with one sentence on how it shows up in the interface]

## Themes

[light / dark / both; which is canonical; how a theme is selected]

## Color System

- **Primary**: []
- **Secondary**: []
- **Neutrals**: []
- **Semantic** (system states only, never brand): destructive/error, success, warning, info.

## Typography

[] (display/headings), [] (body), [] (code/data). Self-hosted with `font-display: swap`. Don't add a fourth family.

## Logo

[asset locations, clear space, minimum size, approved variants; the logo is never distorted, recolored outside the approved variants, or restyled per surface]

## Shape

[border-radius scale; sharp vs rounded]

## Hierarchy & Emphasis

[the ranked instrument list for making something rank first on a surface — e.g. type scale → weight → surface tone step → spacing → color, in a stated order, with borders grouping rather than ranking; this section is the grants column the restraints elsewhere point to, and a filled brand doc without it has exactly one failure mode: the uniform bordered grid. When defining the neutral scale, most steps belong to backgrounds and text, with borders drawing from a narrow low-contrast band (the Radix Colors allocation)]

## Layout

[grid system, max content widths, spacing rhythm; the viewport posture — mobile-first (design the narrow viewport first and let wide viewports reveal more, with primary mobile actions in the bottom-center reach zone per Hoober's grip research) or desktop-first, stated as a choice with the reason the product's job gives it; the spacing scale's base unit and half-step (8px with 4px half-steps is the common pick, and Material, Carbon, and Atlassian all constrain to base-unit multiples) and its tiering across the three distances — inside a group, between distinct elements, between sections (Atlassian's 0-8 / 12-24 / 32+ as the directional shape). `ux-standards.md` requires that a scale exist and be adhered to; this section is where its numbers are decided]

## Density

[compact vs airy; how tables and dense surfaces breathe; whether density is modal — comfortable as the default with a compact mode existing only for data-dense views (tables, resource lists) and never applying to focused-input components like date pickers and alerts (Cloudscape, Material) — or a single density throughout]

## Surfaces, Borders, Shadows, and Gradients

[line-led vs fill-led vs shadow-led emphasis and why; elevation policy — dark themes elevate by lightening surface tone, since shadows don't read on dark (Material); gradient policy]

## Motion

[duration range picked inside the perception bands `ux-standards.md` states; easing, where entrances conventionally decelerate (`ease-out`) and `ease-in` never opens an entrance; signature transitions, including the proportional scale a dialog and a button press animate from (~0.8 for dialogs rather than zero, ~0.95 for presses rather than anything dramatic, as the common pick); what never animates]

## Data Visualization

[chart palette derivation, mark style, axis and label rules]

## Imagery & Iconography

[imagery mode — photographic, illustrated, abstract, or product-first — with treatment rules (color grading, composition, subject matter); icon character above `ux-standards.md`'s one-family floor: stroke weight, filled vs outline, corner rounding]

## Voice and Copy

- **Traits**: [3-5 voice traits, each anchored — "confident: verbs first, no hedging qualifiers in CTAs"]
- **Register**: [how technical and how casual the language runs, and where the line flexes between UI and marketing surfaces]
- **Vocabulary**: [words this brand uses; words it never uses, each banned word paired with its sanctioned replacement]
- **Exemplars**: [one exemplar phrase each for a headline, an empty state, an error, and a CTA — exactly one per context, because exemplars steer copy harder than trait lists while more than one per context turns constraints into a staling copy library]

## Anti-Goals

[what this brand must never look or sound like — negative constraints are the doc's highest-leverage steering device; pair each with the section that grants the alternative]
