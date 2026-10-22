# Code legibility

What a person reading the code later pays for, whatever the language.
Language conventions live in their own files beside this one, and the comment rule lives in `CLAUDE.md`.

## Code

- Names say what a thing is or does, so a reader never needs the body to guess the purpose.
  Booleans read as predicates (`isStale`, `hasAccess`), collections are plural, and units ride in the name when they matter (`timeoutMs`, `amountCents`).
- A function fits one screen and does one thing; a second responsibility is a second function, named.
- Control flow reads top to bottom: guard clauses and early returns over nesting, and a lookup or `switch` over a chain of conditionals on one value.
- No clever one-liners: a reduce that needs a comment to follow is a loop.
- Types and signatures document the contract, and a function returns the same shape on every path.
- New code matches the conventions of the file it lives in, even when a better pattern exists elsewhere, because consistency inside a file is legibility.

## Tests as documentation

- A test name states the behavior in the caller's words ("rejects an order with no line items"), never the mechanism ("calls validate").
- One logical assertion per test.
- Setup is visible: builders and factories over hand-rolled fixtures, and nothing load-bearing hidden in a shared hook far from the test.
- A test waits on a condition it can observe, never on a duration.
