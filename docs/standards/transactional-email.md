---
applies-to:
  - "email/**/*.{tsx,jsx,html,mjml,hbs}"
  - "emails/**/*.{tsx,jsx,html,mjml,hbs}"
  - "mail/**/*.{tsx,jsx,html,mjml,hbs}"
  - "**/email/**/*.{tsx,jsx,html,mjml,hbs}"
  - "**/emails/**/*.{tsx,jsx,html,mjml,hbs}"
  - "**/mail/**/*.{tsx,jsx,html,mjml,hbs}"
  - "**/templates/{email,emails,mail}/**/*.{html,mjml,hbs}"
  - "**/*.email.{tsx,jsx,html,mjml,hbs}"
---

# Transactional email

Transactional emails (verification, password reset, email-change confirmation) are customer-facing brand surfaces rendered in the most hostile client environments products touch: Outlook desktop renders HTML through Word's engine (Microsoft's own rendering documentation), Gmail strips and clips markup, and dark-mode clients recolor without permission. These rules govern every email template.

`CLAUDE.md`'s no-em-dash rule applies to all email copy.
The accessibility floors in [`ux-standards.md`](./ux-standards.md) apply to the rendered message, since that file carries the contrast ratio and the touch-target number this one defers to and states nowhere else.

**On an email path, this file wins over [`frontend-styling.md`](./frontend-styling.md) and [`html-tables.md`](./html-tables.md).**
They contradict it by design: they say no `px` for layout, no inline styles, and tables for data only, while an email client needs nested layout tables, inline styles, and a `600px` column.
Email clients are the reason, so the email rules win here and only here.
A project that sends no templated mail deletes this file.

- **Tables carry layout, inline CSS carries style**: layout is nested tables with `role="presentation"`, never flex/grid — partial support in Gmail and Outlook at best (caniemail.com) — and every load-bearing style is inline. A `<style>` block is progressive enhancement only (media queries, dark mode): Gmail drops the entire block past 8,192 characters or on a single CSS parse error (caniemail.com).
- **One column, 600px**: content is a single column at `600px` max width, readable at mobile widths without media queries, which Gmail and Outlook support only partially (caniemail.com).
- **Padding, never margin**: spacing lives in table-cell `padding`; `margin` is unreliable across clients and negative margins silently break in both Gmail and Outlook (caniemail.com).
- **Bulletproof CTA**: the action button is a live-text link styled inline with a 44×44px minimum touch target (the `ux-standards.md` touch-target floor), wrapped in the MSO conditional/VML fallback so Outlook renders the fill and rounding (Campaign Monitor's bulletproof-button pattern); never an image button — `border-radius` or a background image without a VML + solid-color fallback renders as nothing in Outlook.
- **Dark mode is declared, then defended**: `color-scheme` and `supported-color-schemes` meta tags in the head, `prefers-color-scheme` overrides in the style block, a midtone palette instead of pure black/white, and logos and transparent images carry a subtle outline so they survive clients that force-invert — Gmail iOS, Outlook Windows (Litmus dark-mode guidance).
- **System-stack fallbacks always**: Gmail and Yahoo drop web fonts entirely (caniemail.com); every font declaration ends in a system stack, and the brand fonts are an enhancement for the clients that keep them, never assumed.
- **Text-first, never image-only**: the message survives with all images blocked, Outlook's default (Microsoft's client documentation); images are HTTPS-hosted with explicit dimensions, 2x exports for retina, and styled `alt` text.
- **Plain-text part always**: every email ships a `multipart/alternative` plain-text version, where auth links appear as literal URLs — phishing resistance for exactly the emails we send.
- **Authored preheader**: the preview line after the subject is deliberate copy, never whatever text happens to render first (Litmus preheader guidance).
- **Stay under the clip**: total HTML stays well below Gmail's ~102KB clipping threshold (Litmus), which truncates mid-markup and can break the layout it cuts.
- **Accessible like the app**: semantic headings, `lang` on the root element, `16px` body-copy floor, WCAG AA contrast per the `ux-standards.md` Standards.
- **Banned in email**: JavaScript, forms, video, CSS positioning, negative margins, and checkbox/hover interactivity hacks; every one is stripped or silently breaks somewhere in the client set (caniemail.com).
