---
title: <Feature name>
slug: <slug>
branch: <feature branch>
base: <base branch>
status: draft
owner: <person>
created: YYYY-MM-DD
updated: YYYY-MM-DD
approved_hash:
description: <1–2 sentences; see section 7>
---

# <Feature name>

## Summary

<One paragraph, 5–7 sentences; see section 7.>

## Problem and context

<Current state, who is affected and how, each distinct problem on its own line (for a bug, each cause), and evidence (metrics, incidents, user reports) with sources.>

## Goals

- G1: <outcome, measurable where possible>

## Non-goals

- <out of scope, with the reason if it isn't obvious>

## User scenarios

### P1: <story title>

As a <user>, I want <capability> so that <outcome>.
Independent test: <how this slice is verified on its own>

- Given <context>, when <action>, then <result>.

### P2: <story title>

...

## UI surfaces

- UI-001: <screen, page, view, component or email template> (<new or edited>)

## Requirements

### Functional

- FR-001: When <trigger>, the system shall <behavior>.
  - Acceptance: Given <context>, when <action>, then <result>.

### Non-functional

- NFR-001: <metric, threshold and conditions>

## Invariants

- INV-001: The system shall never <behavior>.

## Edge cases and failure behavior

- <case>: <expected behavior>

## Existing behavior

<What exists today that this change builds on. These are not new requirements; do not re-implement them.>

## Assumptions

- A-001: <assumption>. Accepted by <person>.

## Open questions

- [NEEDS CLARIFICATION: <specific question>]

## Glossary

| Term | Meaning |
| ---- | ------- |

## Changelog

- YYYY-MM-DD: <change and reason>
