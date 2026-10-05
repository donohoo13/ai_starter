---
applies-to:
  - "**/*.{tsx,jsx,vue,svelte,astro,mdx,html,htm,css,scss,sass,less}"
---

# Frontend styling conventions

How this project writes styles. The usability floors these styles must clear live in [`ux-standards.md`](./ux-standards.md); the palette, type scale, spacing rhythm, and motion character they express live in [`BRANDING.md`](../../BRANDING.md), and the app's theme CSS is the source of truth for token values.

**On an email path, [`transactional-email.md`](./transactional-email.md) wins over this file.**
An email client needs nested tables, inline styles, and a `600px` column, all of which these rules forbid, so follow that file there and treat this one as inert.

This is the file that tracks the project's stack: swap the styling-system section below for whatever the project actually uses, and delete the file when the project ships no UI.

## Units and scaling

- **CSS-First**: use modern native CSS capabilities over JS libraries for visual behavior (layout, animation, scroll effects); reach for JS only when CSS cannot express it.
- Use **rem** for font-sizes, padding, and margins to support browser zooming.
- Use **em** for component-level scaling (e.g., button internals).
- Use **%** or viewport units for layout dimensions; size any element to the full viewport height with `svh`, or with `dvh` when that element has no fixed or sticky descendant, never with `vh` — `vh` resolves against the viewport with the browser's retracting chrome hidden and so overflows while that chrome is visible, and `dvh` tracks the chrome as it moves, which re-anchors fixed and sticky children mid-scroll.
- **Do not use px** for layout or typography; use only for thin borders (1px) or where absolute precision is required.
- Use `clamp()` for fluid typography (e.g., `font-size: clamp(1rem, 2vw + 1rem, 2.5rem)`) instead of fixed `em` or `rem` values for headings and body text to ensure responsiveness.
- Assume a base font size of 16px (1rem = 16px). A project that steps the root away from that default documents the value where it sets it, since every rem-authored size in the app scales with it.

## Tailwind

These rules apply when the project uses Tailwind (v4); they are inert otherwise.

- Use Tailwind utility classes as the primary styling method while utilizing `@utility` & `@layer` components for multi-property patterns repeated across 3+ files.
- Component files consume theme values by name and carry no raw palette value (`text-neutral-600`, `bg-primary-500`) and no `dark:` variant: every colour, alpha included, is a semantic colour token, and every non-colour value that differs between themes (opacity, mask, filter, transform) is a custom property declared in the app's CSS file alongside those tokens, with a value under each theme selector, read at the call site as `opacity-(--watermark-strength)`. Declaring one without its counterpart ships the light value into dark mode silently, which is the one failure a call-site override would at least have made visible.
- If a colour class isn't mapped to a `--color-*` var in the app's CSS file, Tailwind v4 silently drops it; a custom property consumed with the `(--var)` form is read straight through instead, so an undefined one falls back to the property's initial value rather than disappearing. Verify both against the file.
