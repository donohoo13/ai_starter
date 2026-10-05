---
applies-to:
  - "**/*.{tsx,jsx,vue,svelte,astro,mdx,html,htm,mjml,hbs,css,scss,sass,less}"
---

# UX standards

The usability and accessibility floors every user-facing surface meets.

## Floors

- **Touch targets** at least 44×44px.
- **Contrast** WCAG AA: 4.5:1 body text, 3:1 large text, per theme.
- **Accessibility** WCAG 2.1 AA: keyboard-navigable, focus order matches visual order, visible focus, `aria-label` on icon-only controls.
- **Interaction states**: visible hover, focus, pressed, and disabled; pressed never shifts layout; every hover-only action also has a tap path.
- **Performance**: Core Web Vitals "good" at p75 (LCP ≤2.5s, INP ≤200ms, CLS ≤0.1).
- **Icons**: one SVG family, one stroke width; emoji never serve as icons.
- **Choices**: chunk, group, and disclose progressively instead of capping option counts.
- **Scanning**: front-loaded headings, short paragraphs; reading text caps near `70ch`.

## Composition

- A surface names the one task it serves and is composed from that task, never from its data payload rendered top to bottom.
- Information ranks into a verdict tier and a reference tier, visually distinct in scale or weight.
- Secondary information sits behind hover, expansion, or a drawer, at most two levels deep.
- Every figure is interpretable in place: unit and meaning adjacent, never only in a distant header.
- Spacing comes from the project's scale; within a group tighter than between groups; borders are the last grouping tool after spacing and tone.

## Forms and controls

- Labels persistent and above the field; a placeholder is never the label.
- Single column; validate on blur or submit, never per keystroke; errors adjacent, in plain language, linked via `aria-describedby`; required and optional both marked.
- Known exact value: text entry with `inputmode`. Small adjustment: stepper. Approximate range: slider. Units live on the control. Native number spinners never ship.
- Personal-data fields carry `autocomplete` tokens. Destructive actions confirm.

## Feedback and motion

- Acknowledge every action within ~100ms; over 1s shows an indicator, over 10s determinate progress plus cancel. Skeletons for initial loads, inline spinners for refreshes, nothing for sub-second waits.
- Modals only for decisions that must block; toasts carry short confirmations via `aria-live="polite"`, never errors.
- Empty states name the state and carry the action that fills it.
- Motion explains change: 100–300ms for state changes, enter slower than exit, only `transform` and `opacity` animated, `prefers-reduced-motion` honored, high-frequency actions never animated.

## Data tables

- Text left, numerics right in a monospaced family with consistent decimals; hairline row dividers, never a box per cell.
- Sticky headers, frozen identity column, persisted column controls; row actions on hover and focus; bulk actions appear once a selection exists.
- Virtualize large sets with server-side sort and filter; row detail in a drawer, never a navigation away; overflow always signaled; narrow screens move data, never drop it.
