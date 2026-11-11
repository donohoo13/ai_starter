"""The valid fixtures' bodies as the repository's pre-commit hook rewrote them: Prettier put a blank line after each heading and padded each table."""

FORMATTED_SPEC_BODY = """
# Invoice thumbnails

## Summary

The invoice PDF lists attachments by filename only. Reviewers cannot see a attachment without opening it. An invoice with 300 attachments takes an hour to review. Finance approves invoices a day late as a result. The PDF generator will render a thumbnail for each attachment with pdf-lib. Thumbnails let reviewers judge a attachment from the list. The finished PDF shows every attachment inline.

## Problem and context

Reviewers open each attachment by hand. Source: support tickets from 2026-09.

## Goals

- G1: Reviews finish in under 10 minutes.

## Non-goals

- Editing attachments.

## Requirements

### Functional

- FR-001: When a reviewer opens the invoice PDF, the system shall render a thumbnail for each attachment.
  - Acceptance: Given an invoice with 300 attachments, when the PDF renders, then every thumbnail appears within 10 seconds.

### Non-functional

- NFR-001: p95 render time under 10 s for 300 attachments.

## Invariants

- INV-001: The system shall never show a raw exception to a user.

## Edge cases and failure behavior

- Missing attachment file: a placeholder renders and the invoice still opens.
"""

FORMATTED_PLAN_BODY = """
# Invoice thumbnails plan

## Approach

Render thumbnails in the existing PDF generator.

## Technical context

- Stack and versions: Node 24
- Dependencies: pdf-lib 1.17
- Platform limits: 50 MB PDF

## Principles check

| Principle  | Pass/Fail | Notes |
| ---------- | --------- | ----- |
| Test-first | Pass      |       |

### Deviations

- None

## Architecture

One service renders thumbnails.

## Data model

No changes.

## Interfaces and contracts

GET /invoices/:id.pdf unchanged.

## Affected code

- Change: src/invoices/pdf.ts, add thumbnails
- Pattern to follow: src/invoices/csv.ts

## Seams and test strategy

### P1: Thumbnails in the PDF

- Seam: request test on GET /invoices/:id.pdf
- Test types: supertest request test
- Acceptance criteria to tests: FR-001 acceptance, tests/invoices/pdf.test.ts

## Alternatives considered

- Client-side rendering: rejected, no browser in the PDF path

## Trade-offs and risks

- Render time grows with attachment count: cap thumbnail size

## Rollout

1. Ship without a flag. Rollback: revert

## Traceability

| Requirement | Components | Seam                                  | Tests                                  |
| ----------- | ---------- | ------------------------------------- | -------------------------------------- |
| FR-001      | InvoicePdf | request test on GET /invoices/:id.pdf | tests/invoices/pdf.test.ts             |
| NFR-001     | InvoicePdf | request test on GET /invoices/:id.pdf | tests/invoices/pdf.test.ts             |
| INV-001     | InvoicePdf | service test on InvoicePdf            | tests/invoices/pdf-placeholder.test.ts |

## Research notes

- pdf-lib embeds images: https://pdf-lib.js.org
"""

FORMATTED_TASKS_BODY = """
# Invoice thumbnails tasks

## P1: Thumbnails in the PDF

- [ ] T001 Render a thumbnail for each attachment in the invoice PDF
  - Requirements: FR-001, NFR-001
  - Seam: request test on GET /invoices/:id.pdf
  - Files: src/invoices/pdf.ts, tests/invoices/pdf.test.ts
  - Done when: `pnpm test -- tests/invoices/pdf.test.ts` passes
- [ ] T002 Render a placeholder when a attachment file is missing
  - Requirements: FR-001, INV-001
  - Seam: service test on InvoicePdf
  - Files: src/invoices/pdf-placeholder.ts, tests/invoices/pdf-placeholder.test.ts
  - Done when: `pnpm test -- tests/invoices/pdf-placeholder.test.ts` passes
- [ ] P1 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## Verified elsewhere

- None

## Follow-ups (out of scope)

- None yet
"""
