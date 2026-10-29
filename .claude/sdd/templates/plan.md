---
title: <Feature name> plan
slug: <slug>
status: draft
updated: YYYY-MM-DD
based_on:
approved_hash:
---

# <Feature name> plan

## Approach

<A short summary of the technical approach.>

## Technical context

- Stack and versions:
- Dependencies:
- Platform limits:

## Principles check

| Principle | Pass/Fail | Notes |
| --------- | --------- | ----- |

### Deviations

- <principle>: <why the deviation is needed, and the simpler option rejected>

## Architecture

<Components, what each is responsible for, and the boundaries between them.>

## Data model

<Entities, fields, relationships, migrations.>

## Interfaces and contracts

<APIs, events, schemas, error formats, handoff contracts.>

## Affected code

- Change: <path>, <what changes>
- Create: <path>, <purpose>
- Pattern to follow: <path to an existing example>

## Seams and test strategy

### P1: <slice title>

- Seam: <boundary the tests run at, and why it's the repo's established seam for this code>
- Test types: <the repo's test types used here>
- Acceptance criteria to tests: <criterion → test>

## Alternatives considered

- <option>: <why rejected>

## Trade-offs and risks

- <what the team takes on>: <mitigation>

## Rollout

1. <step that ships on its own>. Rollback: <how>

## Traceability

| Requirement | Components | Seam | Tests |
| ----------- | ---------- | ---- | ----- |

## Research notes

- <verified fact>: <source>
