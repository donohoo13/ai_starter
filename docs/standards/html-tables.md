---
applies-to:
  - "**/*.{tsx,jsx,vue,svelte,astro,mdx,html,htm,hbs,css,scss,sass,less}"
---

# HTML tables

How a plain `<table>` is marked up and styled, after [MDN: Styling tables](https://developer.mozilla.org/en-US/docs/Learn_web_development/Core/Styling_basics/Tables). The behaviour of a full data grid (sticky headers, virtualization, row actions, column controls) lives under "Data tables" in [`ux-standards.md`](./ux-standards.md); this file is the floor beneath it, and every rule here holds for a grid too. [`transactional-email.md`](./transactional-email.md) overrides this file on email paths, where tables carry layout instead of data.

## Markup

- A `<table>` holds tabular data only; page and component layout use grid or flex. Each table carries a `<caption>` naming what one row is, a `<thead>` and `<tbody>`, and a `<tfoot>` only when it holds totals.
- Every header cell is a `<th>` with `scope="col"` or `scope="row"`, never a styled `<td>`; assistive tech reads the header from the scope, not the styling. Column widths sit on the `<th>` so one declaration governs the column.
- Markup stays flat: no nested tables, no wrapper element per row, no presentational attributes (`border`, `cellpadding`, `align`, `bgcolor`), and no inline styles; the CSS below is the whole treatment.

## Styling

- The `table` sets `table-layout: fixed`, `border-collapse: collapse`, and `width: 100%`, so column widths resolve from the `<th>` declarations rather than the longest cell and borders meet as single lines.
- `th, td` share one `padding` from the spacing scale (`0.5em`-`0.75em`) and `vertical-align: top`, so a wrapped cell aligns with its neighbours instead of floating mid-row.
- Alignment follows the column's content: text left, numerics right, and a header aligns with its column. A centred column needs a stated reason, since centring breaks the scan line down a column.
- Rows separate by one device: a hairline `border-bottom` on `tbody tr` is the default, and zebra striping via `tbody tr:nth-child(odd)` on a semantic surface token replaces it when the table is wide enough that the eye loses the row across columns. Never both, never a box per cell. A `border-top` and `border-bottom` on the `table`, plus a `border-top` on `tfoot`, frame the whole.
- Header cells are distinguished by weight or a surface token, never by size, so header and body sit on the same type scale. Any `letter-spacing` is in `em` and applies to headers only; on data cells it breaks number scanning.
- `caption` styles as a label (`caption-side: top`, muted text token, body family), never as a page heading; it is read first by screen readers and belongs above the data it names.
- Column widths are `%` or `ch`, never `px`, and a table that can outgrow its container wraps in one element with `overflow-x: auto` so the page never scrolls horizontally.
