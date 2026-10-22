---
status: ready
---

# <Imperative title: the ask in one line>

<The task at hand in a sentence or two.>

## Product Requirements

<When no product question applies: one line saying why, and nothing below.>

### Problem

<Who has the problem, what they do today, why it matters now.>

### User Stories

- As a <persona>, I <verb> so that <outcome>.

## Design Requirements

<When the change touches no user-facing surface: one line saying so, and nothing below. Otherwise open with the one job the surface serves.>

### Controls

- <Element to create or change from the user's perspective, and the control that carries it.>

### Layout and Hierarchy

- <What ranks first, what is reference, what sits behind disclosure; typography and display surfaces (dialogs, sheets, chips, tooltips) named.>

## Engineering Requirements

<Constraints, assumptions, and edge cases, one bullet each.>

### Slices

- [ ] <Slice: the end-to-end behavior it delivers.> Done when: <the observable check>.

### Architecture

- <Interfaces and contracts, schema and API shapes, chosen patterns and frameworks, and the trade-off behind each.>
- Blast radius: <the shared code touched and every caller affected, or "none shared">.
- Existing implementation: <kept | extended | stripped first, naming what dies>.

## Evidence

- <The research or measured fact behind a decision, and the decision it settles.>

### Sources

- <URL or document>: <what it establishes>

## Touch Map

- `<path>`: <role in the change, current shape, risk>.

## Out of Scope

- <Non-goal, named so the task does not expand silently.>

## Rejections

- <Option considered>: rejected because <reason>.
