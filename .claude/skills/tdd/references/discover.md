# Discovering a repo's test shapes

Read before the first test in a repository whose commands and test shapes are not already in context.
It tells you how to build that knowledge from the repo's own files, and what to do when you cannot.

## Find the commands

Look, in this order, and stop at the first source that names a command outright:

1. `CLAUDE.md`, `AGENTS.md` or any principles document at the root, and the project's skills under `.claude/skills/` when one runs tests.
   A project skill for running tests wins over everything below; load it.
2. The README, under headings such as Testing, Development or Contributing.
3. The manifest: `package.json` scripts (`test`, `lint`, `typecheck`, `format`), a `Gemfile` plus `Rakefile` or `bin/rspec`, a `Makefile` target, `pyproject.toml` or `tox.ini`, `Cargo.toml`, `go.mod`.
4. `bin/` and `scripts/` for wrappers the team actually runs, such as a container entry point.
5. CI configuration (`.github/workflows`, `.gitlab-ci.yml`, `.circleci`) for the exact invocations the build runs, including tiers such as unit, integration and system.

Write down: the command for one test file, the command for the full suite, each lint or typecheck tier, and whether anything must be running first (a container, a database, a service).

## Find the frameworks and where tests live

- Frameworks from the manifest's dependencies and from configuration files: `jest.config.*`, `vitest.config.*`, `.rspec`, `spec/spec_helper.rb`, `pytest.ini`, `conftest.py`, `phpunit.xml`, and so on.
- Locations from the configuration's test match patterns and from a listing: `spec/`, `test/`, `tests/`, `__tests__/`, files ending in `.test.*`, `.spec.*`, `_test.*` or `_spec.rb`. Note any naming rule the runner enforces, such as an extension it silently skips.
- Fixtures and factories: `spec/factories`, `test/fixtures`, builder functions under a `testUtils` or `support` folder, global mocks under `__mocks__`.

## Find one living example of each test type

For each kind of code the change touches (pure function, model, service, HTTP handler, worker, UI component, CLI), open one existing test of that kind and note: its path, how it builds input (factory, builder, literal), how it drives the code (direct call, HTTP client, render and interact), what it asserts on, and which helpers it imports.
The newest test by git log is the best guide to current convention when files disagree.

## Find how collaborators are doubled

Search the tests for the repo's doubling tools: `instance_double`, `allow(...).to receive`, `jest.mock`, `vi.mock`, `sinon`, `unittest.mock`, `monkeypatch`, `WebMock`, `VCR`, `msw`, `nock`.
The pattern you find at a given layer is the seam for that layer.
Note what is never mocked (a real test database, an in-memory store) and what is always mocked (payment providers, third-party APIs, the network).

## Summarize before the first test

Write a short summary in the conversation before writing any test:

- Commands: one file, full suite, lint and typecheck tiers, prerequisites.
- Frameworks and test locations, with any naming rule the runner enforces.
- One example path per test type you will write.
- How collaborators are doubled at each layer, and what is never doubled.
- Anything you could not find.

Then write the first test following the example you named.

## Never invent a command

If no source names a test or lint command, or two sources disagree, ask the user which to use instead of guessing.
A command that does not exist proves nothing, and a wrong one can mutate state.
The same applies to a factory, helper or fixture you cannot find: ask, or build the input as a literal in the test.
