---
version: alpha
name: "[Product name]"
description: "[2–3 sentences: what this product looks and feels like, its one signature visual move, and what it refuses to look like. Tools display this first and agents read it first.]"

# ─────────────────────────────────────────────────────────────────────────────
# Tokens are normative: prose references them by {path} and never restates a
# value. Colors are named by ROLE, never appearance ("canvas", not "periwinkle"),
# so themes swap values without renaming. One name per role, no aliases.
# Every color is used by at least one component, or lint flags it as orphaned.
# ─────────────────────────────────────────────────────────────────────────────

colors:
  # Brand — add a role only when it has a distinct job; each role gets an on-<role>.
  primary: "[hex]" # [its one job]
  on-primary: "[hex]"
  primary-hover: "[hex]"
  primary-active: "[hex]"
  secondary: "[hex]" # [its job, distinct from primary] — delete if single-hue
  on-secondary: "[hex]"
  # Surfaces — most of the neutral scale belongs to surfaces and text
  canvas: "[hex]" # page background
  surface: "[hex]" # cards, inputs, table body
  surface-raised: "[hex]" # menus, popovers, dialogs, toasts
  surface-sunken: "[hex]" # table headers, wells, hover fills, disabled fills
  # Text
  ink: "[hex]" # primary text
  ink-muted: "[hex]" # secondary text, placeholders — still ≥ 4.5:1 on every surface
  # Lines — a narrow, low-contrast band; borders group, they never rank
  border: "[hex]"
  # Interaction
  focus: "[hex]" # focus-visible ring, ≥ 3:1 against adjacent surfaces
  # Semantic — system states only. Separate tokens even if a value matches a brand hue.
  error: "[hex]"
  on-error: "[hex]"
  success: "[hex]"
  on-success: "[hex]"
  warning: "[hex]"
  on-warning: "[hex]"
  info: "[hex]"
  on-info: "[hex]"
  # Dark theme (only if Themes = both): add a `<role>-dark` sibling for every role
  # above, e.g. canvas-dark. Components don't reference these, so orphaned-token
  # warnings are expected for the -dark set only.

typography:
  # Three families at most: display, body, mono. Each fontFamily carries its fallback stack.
  display:
    fontFamily: "[Display family], [fallback stack]"
    fontSize: "[rem]"
    fontWeight: "[weight]"
    lineHeight: "[unitless]"
    letterSpacing: "[em]"
  heading-1:
    fontFamily: "[family, stack]"
    fontSize: "[rem]"
    fontWeight: "[weight]"
    lineHeight: "[unitless]"
    letterSpacing: "[em]"
  heading-2:
    fontFamily: "[family, stack]"
    fontSize: "[rem]"
    fontWeight: "[weight]"
    lineHeight: "[unitless]"
    letterSpacing: "[em]"
  heading-3:
    fontFamily: "[family, stack]"
    fontSize: "[rem]"
    fontWeight: "[weight]"
    lineHeight: "[unitless]"
    letterSpacing: "[em]"
  body:
    fontFamily: "[Body family], [fallback stack]"
    fontSize: "[rem]"
    fontWeight: "[weight]"
    lineHeight: "[unitless]"
    letterSpacing: "[em]"
  body-sm:
    fontFamily: "[family, stack]"
    fontSize: "[rem]"
    fontWeight: "[weight]"
    lineHeight: "[unitless]"
    letterSpacing: "[em]"
  label: # buttons, field labels, nav, table headers
    fontFamily: "[family, stack]"
    fontSize: "[rem]"
    fontWeight: "[weight]"
    lineHeight: "[unitless]"
    letterSpacing: "[em]"
  code: # code, IDs, tabular data
    fontFamily: "[Mono family], [fallback stack]"
    fontSize: "[rem]"
    fontWeight: "[weight]"
    lineHeight: "[unitless]"
    letterSpacing: "[em]"

rounded:
  none: 0px
  sm: "[px]"
  md: "[px]"
  lg: "[px]"
  full: 9999px

spacing:
  # 8px base with 4px half-steps (change only with a reason stated in Layout).
  # Tiers: inside a group xs–sm · between elements md–lg · between sections xl+
  xxs: 2px
  xs: 4px
  sm: 8px
  md: 12px
  lg: 16px
  xl: 24px
  xxl: 32px
  section: 48px

components:
  # Spec-valid properties only: backgroundColor, textColor, typography, rounded,
  # padding, size, height, width. Borders, shadows, icons and behavior go in the
  # Components prose. A state that changes a value is its own entry (<name>-hover).
  # On fixed-height controls, `height` is the vertical size and `padding` is inline.

  # ── Base ──
  page:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
  focus-ring:
    backgroundColor: "{colors.focus}"
    width: 2px

  # ── Actions ──
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "{spacing.lg}"
    height: 40px
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "{colors.on-primary}"
  button-primary-active:
    backgroundColor: "{colors.primary-active}"
    textColor: "{colors.on-primary}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "{spacing.lg}"
    height: 40px
  button-secondary-hover:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.ink}"
  button-ghost:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
    height: 40px
  button-ghost-hover:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.ink}"
  button-disabled:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.ink-muted}"
  link:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.primary}"
    typography: "{typography.body}"

  # ── Inputs ──
  field-label:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink}"
    typography: "{typography.label}"
  input:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.sm}"
    padding: "{spacing.md}"
    height: 40px
  input-disabled:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.ink-muted}"
  field-error:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.error}"
    typography: "{typography.body-sm}"

  # ── Containers ──
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
  dialog:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.ink}"
    rounded: "{rounded.lg}"
    padding: "{spacing.xl}"
  divider:
    backgroundColor: "{colors.border}"
    height: 1px

  # ── Navigation ──
  nav-item:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink-muted}"
    typography: "{typography.label}"
    rounded: "{rounded.sm}"
    padding: "{spacing.sm}"
  nav-item-active:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.ink}"

  # ── Feedback ──
  badge:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.on-secondary}"
    typography: "{typography.label}"
    rounded: "{rounded.full}"
    padding: "{spacing.xs}"
  alert-error:
    backgroundColor: "{colors.error}"
    textColor: "{colors.on-error}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  alert-success:
    backgroundColor: "{colors.success}"
    textColor: "{colors.on-success}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  alert-warning:
    backgroundColor: "{colors.warning}"
    textColor: "{colors.on-warning}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  alert-info:
    backgroundColor: "{colors.info}"
    textColor: "{colors.on-info}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"
  toast:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.md}"
    padding: "{spacing.md}"

  # ── Data ──
  table-header:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.ink-muted}"
    typography: "{typography.label}"
    padding: "{spacing.sm}"
  table-row:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    padding: "{spacing.sm}"
    height: 44px
  table-row-hover:
    backgroundColor: "{colors.surface-sunken}"
    textColor: "{colors.ink}"
  empty-state:
    backgroundColor: "{colors.canvas}"
    textColor: "{colors.ink-muted}"
    typography: "{typography.body}"
    padding: "{spacing.section}"

  # ── Signature ── 1–3 product-specific components that carry the brand.
  # [signature-name]:
  #   backgroundColor: "{colors.…}"
  #   textColor: "{colors.…}"
---

> **How this file binds.** Front-matter tokens are normative: use them by name, never re-type a value, and never invent one — compose from what exists, and flag a gap rather than filling it.
> Identity sections (Colors, Typography, Shapes, Logo) are absolute and never reinterpreted per surface.
> Steering sections direct judgment, and every adjective in them is anchored to a shipped product or a visible consequence.
> Every restriction names its sanctioned alternative.
> Code mirrors this file (`pnpm exec designmd export --format css-tailwind DESIGN.md`); where code and file disagree, the file wins and the drift is a bug.
> In monorepos, `apps/<app>/DESIGN.md` overrides this file section by section.

<!--
AUTHORING — delete this comment once the file is filled.
- Bracketed placeholders mark undecided axes; the one-time `brand-init` skill fills them.
- A line earns its place by changing what an agent renders.
  Narrative, positioning and messaging pillars live in docs/company/company-overview.md.
- Each value lives in exactly one place: front matter where the spec has a slot (colors, typography, rounded, spacing, components); otherwise the section's own table (breakpoints, elevation, motion).
  Prose references tokens, never values.
- Canonical sections keep spec order: Overview, Colors, Typography, Layout, Elevation & Depth, Shapes, Components, Do's and Don'ts.
  Extension sections (Hierarchy & Emphasis, Motion, Imagery & Iconography, Data Visualization, Voice & Copy) are preserved by the spec.
  To drop a canonical section on purpose, list it under `omitted:` in the front matter.
- Done = `pnpm exec designmd lint DESIGN.md` reports 0 errors, no contrast warnings, and orphaned-token warnings only for -dark colors.
  Before changing a shipped file, `pnpm exec designmd diff` the old and new versions.
- Target: front matter complete, prose ≤ ~400 lines.
-->

## Overview

<!-- Two short paragraphs.
1: the thesis — what the interface is "made of", e.g. "the web rendered as console hardware".
2: the voices — name each color/type role by its job (structural, authority, energy…) and the rule that keeps them apart.
Close on the refusal. -->

[Paragraph 1 — the thesis.]

[Paragraph 2 — the voices, and what this product refuses to look like.]

### Product Context

- **Audience** — [who this is for and the problem they bring]
- **Primary job** — [what most sessions are for; this decides density and emphasis]
- **Promise** — [the outcome or feeling every interaction delivers]

### Personality

<!-- 3–5 traits.
Each names a checkable consequence; "clean" or "modern" alone steers nothing. -->

- **[Trait]** — shows up as [a visible consequence, e.g. "numbers right-aligned in tabular figures"].

### Reference Anchors

<!-- 2–4 shipped products only.
Take one specific thing, leave one specific thing.
Calibration, never a target to copy. -->

- **[Shipped product]** — take [specific quality]; leave [specific quality].

### Key Characteristics

<!-- 5–7 rules a reviewer could verify from a screenshot.
Agents re-read this list before shipping a surface. -->

- [Rule]

## Colors

[One sentence on the palette's structure, e.g. "a warm neutral chassis with one saturated action hue".]

### Brand

- **[Display name]** (`{colors.primary}`) — [its one job].
  [Where it never appears.]
- **[Display name]** (`{colors.secondary}`) — [its job, distinct from primary].

### Surfaces, Text & Lines

- `{colors.canvas}` page · `{colors.surface}` [cards, inputs] · `{colors.surface-raised}` [menus, dialogs, toasts] · `{colors.surface-sunken}` [table headers, wells, hover and disabled fills].
- `{colors.ink}` for primary text, `{colors.ink-muted}` for secondary text and placeholders.
  There is no third text gray; reach for `{typography.body-sm}` or weight instead.
- `{colors.border}` comes from a narrow low-contrast band.
  Borders group; they never rank (→ Hierarchy & Emphasis).

### Semantic

- `{colors.error}`, `{colors.success}`, `{colors.warning}` and `{colors.info}` mark system states only — never decoration, brand emphasis, or chart series.
  [Note any value deliberately shared with a brand hue.]

### Themes

- [Light / Dark / Both]; canonical: [light].
  Selected by [`prefers-color-scheme`, overridable by a user toggle stored in …].
- [If both: dark values are the `-dark` sibling of each role — same names, swapped values, no component changes.
  Dark elevates by lightening surface tone, not by adding shadow.]

### Usage Rules

- [Proportion, e.g. "`{colors.primary}` covers under ~10% of a screen; one primary-filled control per view."]
- Text sits only on color pairs exercised by a component in the front matter.
  A new pairing gets a component entry first, so lint checks its contrast.

## Typography

### Families

- **Display** — [family], fallback [stack].
  **Body** — [family], fallback [stack].
  **Mono** — [family], fallback [stack].
- [Self-hosted with `font-display: swap` | system stack].
  Never add a fourth family; reach for size, weight or case within the three.

### Hierarchy

<!-- Roles only; sizes and weights live in the front matter. -->

| Token                    | Role                                            | Casing |
| ------------------------ | ----------------------------------------------- | ------ |
| `{typography.display}`   | [marketing headline only, never product chrome] | [ ]    |
| `{typography.heading-1}` | [page title, one per view]                      | [ ]    |
| `{typography.heading-2}` | [section title]                                 | [ ]    |
| `{typography.heading-3}` | [card or group title]                           | [ ]    |
| `{typography.body}`      | [default reading text]                          | [ ]    |
| `{typography.body-sm}`   | [captions, helper text, compact table cells]    | [ ]    |
| `{typography.label}`     | [buttons, field labels, nav, table headers]     | [ ]    |
| `{typography.code}`      | [code, IDs, tabular numbers]                    | [ ]    |

### Principles

- [The casing rule in one sentence an agent can apply everywhere, shaped like "uppercase + tracking is the chrome voice".]
- [Numbers: tabular figures in tables and metrics.]
- [Measure: body text capped at ~65ch.]
- [Signature treatment, if any, stated as "always X, never Y".]

## Layout

### Spacing

- Base unit [8px] with [4px] half-steps.
  Every gap, padding and margin is a `{spacing.*}` token; no off-scale values.
- Three distances: inside a group `{spacing.xs}`–`{spacing.sm}`; between distinct elements `{spacing.md}`–`{spacing.lg}`; between sections `{spacing.xl}` and up.

### Grid & Containers

- [Max content width; columns and gutters per breakpoint; app-shell structure — nav position, sidebar width, rails.]

### Viewport Posture

- [Mobile-first | Desktop-first], because [the product's primary job].
  [If mobile-first: primary actions sit in the bottom-center reach zone.]

### Breakpoints

<!-- The spec has no breakpoint slot, so the values live here, once. -->

| Name | Min width | What changes |
| ---- | --------- | ------------ |
| [sm] | [px]      | [ ]          |
| [md] | [px]      | [ ]          |
| [lg] | [px]      | [ ]          |

### Density

- [Single density | Modal: comfortable by default, compact only for data-dense views (tables, resource lists), never for focused-input components such as date pickers, alerts and dialogs.]
  Anchor: [e.g. "row height of Linear's issue list"].
- [Whitespace philosophy in one sentence, shaped like "engineered seam, not breathing room".]

### Accessibility Floors

- Touch hit areas ≥ 44×44px; a smaller visual control extends its hit area with padding.
- Text ≥ 4.5:1 on its surface (3:1 at ≥ 24px, or ≥ 18.66px bold); focus indicator ≥ 3:1.
  Remaining floors live in `docs/standards/ux-standards.md`; this file picks values inside them.

## Elevation & Depth

- **Lead**: [line-led | fill-led | shadow-led], because [reason].

<!-- Shadow values live in this table only; the spec has no slot for them. -->

| Level     | Surface                   | Edge / shadow            | Use                       |
| --------- | ------------------------- | ------------------------ | ------------------------- |
| 0 Base    | `{colors.canvas}`         | none                     | page                      |
| 1 Surface | `{colors.surface}`        | [1px `{colors.border}`]  | cards, inputs, table body |
| 2 Raised  | `{colors.surface-raised}` | [shadow value]           | menus, popovers, toasts   |
| 3 Overlay | `{colors.surface-raised}` | [shadow value] + [scrim] | dialogs, sheets           |

- Gradients: [never in product UI — reach for a surface tone step | allowed only for …].
- [Texture or decorative depth, if any.]

## Shapes

| Token            | Use                        |
| ---------------- | -------------------------- |
| `{rounded.none}` | [ ]                        |
| `{rounded.sm}`   | [inputs, nav items]        |
| `{rounded.md}`   | [buttons, alerts, toasts]  |
| `{rounded.lg}`   | [cards, dialogs]           |
| `{rounded.full}` | [badges, avatars, toggles] |

- [The signature in one sentence, e.g. "sharp chrome with rationed roundness", and where roundness is spent.]
- Nested corners: inner radius = outer radius − padding; never equal radii on nested shapes.

## Hierarchy & Emphasis

<!-- The grants column the restraints point to.
Without it, agents default to a uniform bordered grid. -->

To make one thing rank first on a surface, reach for these in order and stop at the first that works:

1. [Type scale step — e.g. `{typography.heading-2}` over `{typography.body}`]
2. [Weight]
3. [Surface tone step — `{colors.surface}` → `{colors.surface-raised}`]
4. [Isolation — a `{spacing.xl}` gap]
5. [Color — `{colors.primary}`, spent once per view]

- Borders group related things; they never signal importance.
- One `button-primary` per view, placed [where].
- [What "secondary" looks like here, so agents don't flatten everything to equal weight.]

## Motion

<!-- Durations and easings live in this table only.
Pick within the perception bands in docs/standards/ux-standards.md. -->

| Use                           | Duration | Easing     |
| ----------------------------- | -------- | ---------- |
| [Micro: hover, press, toggle] | [ms]     | [ease-out] |
| [Standard: expand, menu, tab] | [ms]     | [ease-out] |
| [Large: dialog, sheet, page]  | [ms]     | [curve]    |

- Entrances decelerate (`ease-out`); `ease-in` never opens an entrance.
  Exits run shorter than entrances.
- Signature transitions: [dialogs enter from scale ~[0.8–0.95] with a fade, never from 0; presses scale to ~[0.95–0.97]].
- Never animates: [table data, content the user is reading, scroll position].
- `prefers-reduced-motion`: transforms become opacity fades or are removed.

## Imagery & Iconography

### Logo

- Assets: [paths].
  Clear space: [ ].
  Minimum size: [ ].
  Approved variants: [full color, mono, reversed].
- Never distorted, recolored outside the approved variants, or restyled per surface.

### Imagery

- Mode: [photographic | illustrated | abstract | product-first].
  Treatment: [grading, composition, subject matter].
  [Where imagery never appears.]
- With no asset available: [e.g. a `{colors.surface-sunken}` block holding the final aspect ratio — never stock photography or a generated stand-in].

### Icons

- One family: [name].
  [Stroke weight], [outline] by default, [filled] only for active or selected.
  Sizes [16/20/24], matched to the adjacent line height.
  Icon-only buttons carry an accessible label.

## Data Visualization

<!-- Delete this section if the product has no charts. -->

- Series palette: [derivation].
  Semantic colors are never series colors.
- Marks: [line weight, bar radius, point size].
  Axes and labels: `{typography.body-sm}` in `{colors.ink-muted}`, [gridline rule].
  [Direct labels over legends at ≤ 4 series.]

## Components

<!-- Bindings live in the front matter.
This section holds what tokens can't: when to use it, anatomy (borders, icons, shadows), state behavior and rules.
Don't restate bound values. -->

### State Coverage

- Every interactive component has default, hover, active, focus-visible and disabled; inputs add error.
  A state that changes a color is its own front-matter entry.
- Focus is global: `focus-ring` — a [2px] `{colors.focus}` ring at [2px] offset on `:focus-visible`, on every interactive element, never removed.
- Disabled controls use `button-disabled` or `input-disabled` and keep their size; no ad-hoc opacity.

### Actions

**`button-primary`** — [the single highest-emphasis action in a view].

- Use for: [commit actions].
  Not for: navigation (→ `link`) or secondary actions (→ `button-secondary`).
- Anatomy: [label only | leading icon], [border], [min width].
- States: `button-primary-hover`, `button-primary-active` ([press scale]), `button-disabled`.

**`button-secondary`** — [role].
[Border: 1px `{colors.border}`.]

**`button-ghost`** — [toolbars and low-emphasis inline actions].

**`link`** — [inline navigation; underline rule].

### Inputs

**`input`** with **`field-label`** — [label position, 1px `{colors.border}` edge, helper text in `{colors.ink-muted}`].

- Error: [border becomes `{colors.error}`] and the message renders as `field-error` below.
  Never signal an error by color alone; pair it with text or an icon.

### Containers

**`card`** — [when to use a card vs. an unboxed group; edge treatment].

**`dialog`** — [width, scrim, close affordance, where actions sit].

**`divider`** — [when a divider is allowed vs. spacing alone].

### Navigation

**`nav-item`** / **`nav-item-active`** — [active indicator, e.g. `{colors.surface-sunken}` fill plus a 2px `{colors.primary}` leading bar].

### Feedback

**`badge`** — [use; max one per row].

**`alert-error`** · **`alert-success`** · **`alert-warning`** · **`alert-info`** — [inline vs. banner; icon; dismissal].

**`toast`** — [position, duration, stacking limit].

### Data

**`table-header`** / **`table-row`** / **`table-row-hover`** — [row height per density, numerals right-aligned, sticky header, zebra or not].

### Empty & Loading States

**`empty-state`** — [one-line headline, one sentence of help, one action].

- Loading: [skeletons in `{colors.surface-sunken}` matching the final layout | spinners only for actions under ~1s].

### Signature Components

<!-- The 1–3 product-specific components that carry the brand, e.g. a beveled plate or an outlined-wordmark hero.
Add each to the front matter too. -->

**`[signature-name]`** — [role, anatomy, rules].

### Compositions

<!-- Standard surfaces agents get asked to build, described as assemblies of the primitives above — not new tokens.
Delete any that don't apply. -->

- **App shell** — [nav placement, `nav-item`, content width].
- **Sign in / sign up** — [`card` on `{colors.canvas}`, centered, width].
- **Settings form** — [label position, section spacing].
- **Data table page** — [filter row, `table-*`, pagination].
- **Pricing** — [tier = `card`; featured tier treatment].
- **Confirm dialog** — [`dialog`; destructive confirm uses …].

## Voice & Copy

- **Traits** — [trait]: [anchored rule, e.g. "confident: verbs first, no hedging qualifiers in CTAs"]. (3–5)
- **Register** — [how technical and how casual; where UI and marketing differ].
- **Casing** — [Sentence case for UI text, headings and buttons | …].
- **Vocabulary**

  | Use    | Never         |
  | ------ | ------------- |
  | [word] | [banned word] |

- **Exemplars** — exactly one per context:
  - Headline: "[ ]"
  - Empty state: "[ ]"
  - Error: "[ ]"
  - CTA: "[ ]"

## Do's and Don'ts

<!-- Anti-goals and do's merged.
5–8 pairs, highest leverage first.
Every Don't names its replacement and the section that grants it, e.g. "Don't soften every corner. Do keep chrome sharp and spend roundness only on controls (→ Shapes)." -->

- **Don't** [what this must never look or sound like].
  **Do** [the sanctioned alternative] (→ [Section]).
