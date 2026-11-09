---
applies-to:
  - "**/*.{tsx,jsx,vue,svelte,astro,mdx,html,htm,css,scss,sass,less}"
---

# Frontend styling conventions

How this project writes styles.
The usability floors these styles must clear live in [`ux-standards.md`](./ux-standards.md); the palette, type scale, spacing rhythm, and motion character they express live in `DESIGN.md`, whose front-matter tokens are the source of truth the app's theme CSS mirrors.
Where `DESIGN.md` is absent, still holds bracket placeholders, or is silent on a value, this file's starting values apply, and brand decisions such as palette, type and voice stay undecided until `design-init` runs.

**On an email path, [`transactional-email.md`](./transactional-email.md) wins over this file.**
An email client needs nested tables, inline styles, and a fixed `600px` column, which these rules steer away from, so follow that file there and treat this one as inert.

This is the file that tracks the project's stack: swap the styling-system section below for whatever the project actually uses, and delete the file when the project ships no UI.

## Designs are references

- A design snapshot under `docs/sdd/<slug>/design/`, or any Claude Design markup, is a reference for layout, flow and states; shipped UI is built from the project's tokens and components.
- Shipped code carries none of Claude Design's runtime markup: no `<x-dc>` or `<dc-import>` element, no `data-dc-script` attribute, and no `support.js` script.

## Units and scaling

- **CSS-First**: use modern native CSS capabilities over JS libraries for visual behavior (layout, animation, scroll effects); reach for JS only when CSS cannot express it.
- Use units that scale with the user's settings and the viewport: **rem** for font sizes, padding and margins so browser zoom and the user's font size carry through, **em** for component-level scaling (e.g., button internals), **%** for layout dimensions, `clamp()` for fluid type, and dynamic viewport units such as `svh` and `dvh` for viewport-relative sizes.
  A fixed unit such as `px` fits only a value that must not scale, such as a hairline border.
- Use `clamp()` for headings and body text (e.g., `font-size: clamp(1rem, 2vw + 1rem, 2.5rem)`) rather than one fixed `em` or `rem` value, so type stays responsive.
- **Starting value**: size an element to the full viewport height with `svh`, or with `dvh` only when that element has no fixed or sticky descendant.
  `vh` overflows while the browser's retracting chrome is visible, and `dvh` tracks that chrome as it moves, re-anchoring fixed and sticky children mid-scroll.
- Assume a base font size of 16px (1rem = 16px).
  A project that steps the root away from that default documents the value where it sets it, since every rem-authored size in the app scales with it.

## Tailwind

These rules apply when the project uses Tailwind (v4); they are inert otherwise.

- Use Tailwind utility classes as the primary styling method while utilizing `@utility` & `@layer` components for multi-property patterns repeated across 3+ files.
- Component files consume theme values by name and carry no raw palette value (`text-neutral-600`, `bg-primary-500`) and no `dark:` variant: every colour, alpha included, is a semantic colour token, and every non-colour value that differs between themes (opacity, mask, filter, transform) is a custom property declared in the app's CSS file alongside those tokens, with a value under each theme selector, read at the call site as `opacity-(--watermark-strength)`. Declaring one without its counterpart ships the light value into dark mode silently, which is the one failure a call-site override would at least have made visible.
- If a colour class isn't mapped to a `--color-*` var in the app's CSS file, Tailwind v4 silently drops it; a custom property consumed with the `(--var)` form is read straight through instead, so an undefined one falls back to the property's initial value rather than disappearing. Verify both against the file.
