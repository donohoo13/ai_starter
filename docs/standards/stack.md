# Stack conventions

This project's own choices, on top of the user-level standards in `~/.config/standards/`.
Swap a section for what the project actually uses, and delete one for a stack it does not ship.

## Tooling

- **Default.** ESLint finds code problems and Prettier formats; configure them so neither fights the other.
- **Default.** Turborepo orchestrates builds: `package.json` scripts route through the `turbo` CLI (`turbo build`, `turbo lint`).
- **Default.** Validate function and API arguments up front with Zod, and fail fast instead of letting bad data travel.

## Tailwind

These apply when the project uses Tailwind v4.

- **Default.** Use Tailwind utility classes as the primary styling method while utilizing `@utility` & `@layer` components for multi-property patterns repeated across 3+ files.
- **Default.** Component files consume theme values by name and carry no raw palette value (`text-neutral-600`, `bg-primary-500`) and no `dark:` variant: every colour, alpha included, is a semantic colour token, and every non-colour value that differs between themes (opacity, mask, filter, transform) is a custom property declared in the app's CSS file alongside those tokens, with a value under each theme selector, read at the call site as `opacity-(--watermark-strength)`. Declaring one without its counterpart ships the light value into dark mode silently, which is the one failure a call-site override would at least have made visible.
- **Default.** If a colour class isn't mapped to a `--color-*` var in the app's CSS file, Tailwind v4 silently drops it; a custom property consumed with the `(--var)` form is read straight through instead, so an undefined one falls back to the property's initial value rather than disappearing. Verify both against the file.

## Email

- **Default.** This project supports classic Outlook for Windows: the call-to-action button is a live-text link wrapped in the MSO conditional and VML fallback, so Outlook renders its fill and rounding, and its tap target is at least 44×44px.
