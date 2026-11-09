---
applies-to:
  - "**/*.{tsx,jsx,vue,svelte,astro,mdx,html,htm,mjml,hbs,css,scss,sass,less}"
---

# UX standards

The usability and accessibility bar every user-facing surface meets.
A floor is set by WCAG 2.2 AA or a Core Web Vitals threshold, and no project goes below it.
A starting value is a choice `DESIGN.md` decides, and applies wherever `DESIGN.md` is absent, still holds bracket placeholders, or is silent on it.

## Floors

Every surface meets WCAG 2.2 AA in every theme; these are the success criteria a surface misses most often.

- **Target size**: every pointer target is at least 24×24 CSS px (2.5.8 Target Size (Minimum)).
- **Contrast**: text is at least 4.5:1, or 3:1 when large (1.4.3 Contrast (Minimum)); control boundaries, icons and focus indicators are at least 3:1 (1.4.11 Non-text Contrast).
- **Keyboard**: every action works from the keyboard (2.1.1 Keyboard), focus order matches visual order (2.4.3 Focus Order), and focus is visible (2.4.7 Focus Visible) and never hidden behind sticky content (2.4.11 Focus Not Obscured (Minimum)).
- **Names**: an icon-only control carries an accessible name, such as `aria-label` (4.1.2 Name, Role, Value).
- **Performance**: Core Web Vitals "good" at p75: LCP ≤2.5s, INP ≤200ms, CLS ≤0.1.

## Starting values

- **Target size**: 38×38px.
- **Reading width**: reading text caps near `70ch`.
- **Motion timing**: 100–300ms for state changes, with enter slower than exit.
- **Feedback timing**: acknowledge every action within 100ms; show nothing for a wait under 1s, an indicator past 1s, and determinate progress plus cancel past 10s.
- **Loading indicators**: a skeleton for an initial load, and an inline spinner for a refresh.
- **Overlays**: a modal only for a decision that must block, and a toast only for a short confirmation, never an error.
- **Icons**: one SVG family at one stroke width, and never emoji as icons.
- **Data tables**: numerics set in a monospaced family, and rows separated by hairline dividers rather than a box per cell.
  Headers stick, the identity column stays frozen, and column controls persist.

## Composition

- A surface names the one task it serves and is composed from that task, never from its data payload rendered top to bottom.
- Information ranks into a verdict tier and a reference tier, visually distinct in scale or weight.
- Secondary information sits behind hover, expansion, or a drawer, at most two levels deep.
- Every figure is interpretable in place: unit and meaning adjacent, never only in a distant header.
- Headings front-load their point, and paragraphs stay short.
- Choices are chunked, grouped and disclosed progressively instead of capped by count.
- Spacing comes from the project's scale; within a group tighter than between groups; borders are the last grouping tool after spacing and tone.

## Forms and controls

- Every control shows hover, focus, pressed and disabled states; pressed never shifts layout, and every hover-only action also has a tap path.
- Labels persistent and above the field; a placeholder is never the label.
- Single column; validate on blur or submit, never per keystroke; errors adjacent, in plain language, linked via `aria-describedby`; required and optional both marked.
- Known exact value: text entry with `inputmode`.
  Small adjustment: stepper.
  Approximate range: slider.
  Units live on the control.
  Native number spinners never ship.
- Personal-data fields carry `autocomplete` tokens.
  Destructive actions confirm.

## Feedback and motion

- Every action is acknowledged and every wait shows its progress, on the feedback timing and loading indicators above.
- A toast announces itself through `aria-live="polite"` (4.1.3 Status Messages).
- Empty states name the state and carry the action that fills it.
- Motion explains change: only `transform` and `opacity` animate, `prefers-reduced-motion` is honored, and high-frequency actions never animate.

## Data tables

- Text aligns left and numerics right, with consistent decimals.
- Row actions appear on hover and focus, and bulk actions appear once a selection exists.
- Virtualize large sets with server-side sort and filter; row detail in a drawer, never a navigation away; overflow always signaled; narrow screens move data, never drop it.
