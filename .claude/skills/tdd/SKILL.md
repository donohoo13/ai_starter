---
name: tdd
description: Test-driven development discipline for any repo. The red then green loop, choosing the seam the repo already tests at, and the anti-patterns that make tests worth keeping. Discovers a repo's test commands and test shapes from its own files before the first test. Works as a one-shot inside any prompt. Use when implementing any feature or bug fix a test can lock down, even when nobody says test-first, and whenever the user says "red-green", "test first", "tdd", or asks which kind of test to write for a change.
argument-hint: "[the behavior, bug or task to build test-first]"
---

# TDD

Red then green.
This skill is what makes the loop produce tests worth keeping.

## Before the first test

Read [references/discover.md](references/discover.md) once per repository and session.
It finds the commands, the frameworks, where tests live, one living example of each test type and how collaborators are doubled, and has you summarize them before the first test.
Skip it only when those facts are already in context, from `CLAUDE.md` or an earlier run in the same session.
Never invent a command: one that does not exist proves nothing, and a wrong one can mutate state.

## Unit of work

When the caller names the unit of work, follow it; for example, when the caller says it runs the full suite at the end, skip that run and report the bounded checks you did run.
Otherwise the whole request is the unit of work: the full suite runs once at its end.

## What a good test is

Behavior through a public interface, never implementation detail.
It reads like a specification ("rejects a checkout with an empty cart") and survives a refactor that changes no behavior.
Expected values are independent literals, never recomputed the way the code computes them.
[references/tests.md](references/tests.md) shows good and bad tests side by side; read it when a test under your hands starts to look like the bad column.

## Seams

A seam is the boundary you test at.
Name the seams a change will test at before the first test, so effort lands on the critical paths instead of every edge.
Choose by what the code depends on, and by what the repo already does for that kind of code, since the repo's established seam wins over the purist one:

- In-process (pure computation, in-memory state): through the module interface, no doubles.
- Local-substitutable (a database with a local stand-in, the file system): run the stand-in in the suite and test through the interface; a real test database or temp directory beats a mock.
- Remote but owned (your own services over a network): a port at the seam, a real transport adapter in production, an in-memory one in tests.
- True external (payments, email, third-party APIs): inject a port and mock only here, at the outermost edge, never deeper.
  [references/mocking.md](references/mocking.md) shows how to shape that edge so the mock stays simple.
- Collaborators the repo already doubles at a layer: double them the same way, through the same helper the discovery found.

UI seams split.
Appearance and layout are never test targets, because jsdom and native test renderers compute no layout.
Behavior is: pressing this calls that with this payload, the error renders, the hidden section stays hidden until toggled.
View logic (state, derived values) tests through its module interface; behavioral contracts test at the component seam the way a user exercises them.
Climb to a browser test only when the browser is the thing under test.

A caller that names the seam decides it: test there, and say so in the report when the repo's established seam for that code disagrees.

## Bug fixes

Open with a failing test that reproduces the report at the lowest seam that shows it, and confirm it fails for the reported reason, not an incidental one.
Climb to a browser test only when nothing lower can show the bug, since every layer added makes the repro slower and flakier.

## Anti-patterns

- **Implementation-coupled**: asserting call counts or order on internal collaborators, testing private methods, verifying through a side channel such as querying the database.
  The tell: a refactor with no behavior change breaks it.
- **Tautological**: the expected value is recomputed the way the code computes it, so it passes by construction.
- **Shallow**: the test asserts existence, or that a call did not throw, instead of an outcome.
  It passes against an implementation that returns the wrong thing.
- **Appearance-pinned**: snapshots, style classes, inline styles, geometry.
  Roles, labels, test IDs, and `aria-*` assertions stay.
  When the loop touches an existing test file, appearance assertions there are removed in the same change and re-expressed at the behavior seam when they carried a real guarantee; report every removal.
- **Horizontal**: all tests first, then all code.
  Bulk tests verify imagined behavior.
  One test, one implementation, repeat.
- **Duration waits**: wait on a condition the test can observe.
  An `act(...)` warning is a failure, fixed by awaiting the trigger inside `act`, never silenced.

## Rules of the loop

- Red before green: the failing test first, then only enough code to pass it, nothing speculative.
- One seam, one test, one minimal implementation per cycle.
- Bounded neighborhood: each cycle runs the touched test files and lints the touched files; the full suite runs once at the end of the unit of work, where single-file runs cannot see interactions.
- Refactoring is not part of the loop: a separate tidy after green, and only inside the code the task already touches, never the surrounding old code.
  Tests may move or be restructured with the code, but never weakened to make a refactor pass: no changed expected value, loosened matcher, dropped assertion, or skip.

## Report back

End with this report, so a caller can record the evidence:

- **Tests written**: each test by file and name, with the behavior it locks down.
- **Red**: the failing output that proved each test failed first, and that it failed for the right reason.
- **Green**: the passing output for the bounded checks, and for the full suite when this unit of work ran it.
- **Files touched**: every file created or changed.
- **Appearance assertions removed**: each one, and where its guarantee now lives, or "none".
- **Pre-existing failures**: any failure that existed before the change, shown by stash, rerun and compare, or "none".
