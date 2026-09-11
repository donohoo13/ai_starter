---
name: tdd
description: Test-driven development discipline, the red then green loop, seam selection, and the anti-patterns that make tests worth keeping. Use when implementing any feature or bug fix a test can lock down, even when nobody says test-first, and whenever the user asks to build test-first, mentions "red-green-refactor", or wants integration tests.
---

# Test-Driven Development

TDD is the red then green loop. This skill is what makes the loop produce tests worth keeping.

## What a good test is

Tests verify behavior through public interfaces, never implementation details. A good test reads like a specification ("user can checkout with valid cart") and survives refactors because it does not care about internal structure. Examples live in `tests.md` and mocking guidance in `mocking.md`, siblings of this file, read as reference.

## Seams

A seam is the public boundary you test at. Tests live at seams, never against internals. Before writing any test, write down the seams under test and confirm them with the user; agreeing them up front puts testing effort on the critical paths instead of every edge case.

Choose the seam by what the code depends on:

- **In-process** (pure computation, in-memory state): test through the module's interface. No adapter, no mock.
- **Local-substitutable** (Postgres via PGLite, an in-memory filesystem): run the stand-in in the suite and test through the interface.
- **Remote but owned** (your own services over a network): a port at the seam, a real transport adapter in production, an in-memory one in tests.
- **True external** (Stripe, Twilio): inject a port and mock only here, at the outermost edge. Never mock internal collaborators.

UI seams split. Layout, appearance, and composition are never test targets, because jsdom computes no layout, so such a test can neither see nor protect how a surface looks. View logic (state, view-model math, derived values) tests through its module interface; behavioral contracts test at the component seam the way a user exercises them: clicking save submits the right payload, the error message renders, the hidden section stays hidden until toggled. When the loop touches an existing test file, appearance-shaped assertions there (inline styles, look-classes, snapshots, geometry) are removed in the same change, re-expressed at the behavior seam when they smuggle a real guarantee; roles, accessible names, and `aria-*` assertions stay. Report every removal.

## Anti-patterns

- **Implementation-coupled**: mocks internal collaborators, tests private methods, or verifies through a side channel such as querying the database. The tell: the test breaks on a refactor that changed no behavior.
- **Tautological**: the assertion recomputes the expected value the way the code does, so it passes by construction. Expected values come from an independent source: a known-good literal, a worked example, the spec.
- **Horizontal slicing**: all tests first, then all implementation. Bulk tests verify imagined behavior. Work in vertical slices instead: one test, one implementation, repeat.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Never anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Run a bounded neighborhood.** Each cycle runs the tests covering the seam plus its direct consumers and lints only the touched files; the full suite runs once at the end of the unit of work, catching interactions single-file runs cannot see. A full suite per cycle is slow enough that the loop stops being run.
- **Refactoring is not part of the loop.** Land it as a separate tidy step after green with tests unchanged, proving the behavior held, never between red and green.
