---
name: refine
description: Makes a working branch right, then runs the one human QA pass on the final code. Discovers the change and its intent without asking, dispatches a fresh refiner agent that audits it against docs/standards/, pins required behavior with proven tests, and refactors code and tests without weakening them, verifies the result, runs a render pass with the UX floors when a surface changed, and hands over a QA script with the app running; on confirmation flips a built spec to done. Works on any branch, with or without a spec, and never pushes or opens a PR. Use when a build is finished or ad-hoc AI work should be brought up to standard, when a spec sits at status built, or when the user says "refine", "make it right", "clean this up", "bring this up to our standards", or "tidy this branch before review".
argument-hint: "[optional: a docs/specs/ path or one line of intent, plus --base <ref> on a stacked branch; blank to discover]"
---

# Refine

Make it work, then make it right.
The work in front of this skill already runs; it brings that work up to the project's standards, strengthens its tests with proof, and puts the final code in front of the user once.
This session orchestrates and the `refiner` agent writes, in a fresh context that never saw the code being authored, so the judgment does not inherit the author's blind spots.
The session discovers the change, owns the branch and the app server, verifies the refiner's claims, and runs QA; it never edits source or tests.
Every worker it dispatches or resumes is waited on, because the next step acts on that worker's report.
Never take the next step until the report is in; when it has not arrived, end the turn and resume from the report when it does.

It never stops at a gate: whatever state the branch is in, it works out what it needs and proceeds.
The user hears the commit list, one validation line, one tests-proven line ("12 tests added or changed, all proven"), one render line, and the QA script.
Beyond that, only something major enough to halt reaches them during the run.

## Discover

- Resolve the default branch from `origin/HEAD`, else `git ls-remote --symref origin HEAD`, else a local `main` or `master`.
  The base is the merge-base of `HEAD` with the ref the argument names after `--base`, when it names one, else with `origin/<default>`, or with the local default when there is no remote.
  A branch stacked on another feature branch needs that branch as `--base`, since the merge-base with the default would pull the lower branch's work into scope; nothing detects a stack on its own.
  A `--base` ref that does not resolve is reported in one line and ends the run.
- The change is everything between the base and the working tree, committed or not.
  An empty change is reported in one line and ends the run.
- The intent is the rest of the argument, else a `docs/specs/` file the change touches, else inferred from the branch's commits and diff.
  Announce it in one line, "Refining X, from Y, since <base>", naming the base ref and the merge-base's short sha, and never ask.
  Emit that line as soon as discovery ends, before the baseline commit and the dispatch, so the user can interrupt a wrong read before any work starts.
- A spec at `status: built` sets spec mode; anything else, a spec at another status included, is ad-hoc.
- On the default branch, branch first per `CLAUDE.md`, naming the branch from the intent.
- Commit any uncommitted work untouched as a baseline, staging each path `git status` lists by explicit path, so the refiner's commits stay separable from the work it was handed and the test-table check stays exact.
  The baseline is `HEAD` after that commit, or `HEAD` as found when the tree was clean.

## Refine

1. Dispatch a fresh `refiner` with the base, the baseline commit, the intent (the spec path or the one line), and the mode, then wait for its report.
   Nothing else rides in the brief, because whatever the orchestrator adds is the bias the fresh context exists to keep out.
2. On `BLOCKED`, put the refiner's question to the user, then resume the same refiner with the answer through `SendMessage` so it keeps its full context.
3. Verify the report.
   Run the project's lint, typecheck, format check, and full suite at `HEAD`, discovered from `CLAUDE.md` and the manifest rather than assumed.
   Compare the test files changed across the refiner's commits (`git diff --name-only <baseline>..HEAD`, read by the project's test-file convention) with the report's test table; they match exactly.
   A failure or a mismatch goes back to the same refiner through `SendMessage` with what this session found.

## Render

- Run the render pass when the change touches a user-facing surface: a changed path matching the `applies-to:` globs in `docs/standards/ux-standards.md`, or a spec with Design Requirements.
- Launch the app (below), then dispatch `render-checker` with the URL, the touched surfaces and the states to reach, the themes the app ships, and the bar: the spec's Design Requirements and `BRANDING.md` when there is a spec, `BRANDING.md` otherwise, plus the `docs/standards/ux-standards.md` floors measured on the rendered page.
- Failures resume the refiner with the findings through `SendMessage`, the suite reruns, then one re-check; what still fails after that is reported, not looped on.
- A skipped pass is said in the render line with its reason.

## QA

- Hand over one QA script with the app already running when there is one: exact commands, URLs, and actions, each observation mapped to a done-when check in the spec (spec mode) or to the intent (ad-hoc).
  Then stop and wait.
  Green checks prove the code does what the tests say; only the user confirms it does what they meant.
- An issue the user finds resumes the refiner with it, a bug opening red-first.
  The suite reruns, the render re-check reruns when a surface changed, and QA returns.
- On confirmation, spec mode flips the spec to `status: done` and commits the flip alone.
  Then stop every process this session started, and stop.
  Never push or open a PR from here.

## App lifecycle

- Launch in this checkout: a recorded `run-*` project skill under `.claude/skills/` when one exists, otherwise `pnpm dev` as a background task.
- Read `.logs/dev-server.log` for readiness and the real URL.
  When `pnpm dev` reports a server already running with its pid, reuse that server.
- After QA, stop every process this session started: the server (`kill $(cat .logs/dev-server.pid)` for `pnpm dev`) and anything else it launched, such as a background command left from trying a QA step.
  Never stop a process it did not start, a reused server included.
  The session owns the server rather than an agent because the server must outlive several checker runs and the user's QA.
- Tell the user about a launch failure once, with its cause and `/run-skill-generator` as the one-time fix that records a launch recipe for later runs; that run's render pass is skipped and noted.

## Report

Before the QA script, report in this order and nothing more:

- The intent line again, and the commits, the baseline first and trunk commits marked.
- One validation line: each command and its result.
- One tests-proven line: how many test files were added, changed, or deleted, and that each carries its proof.
- One render line: pass, the failures left with their evidence, or skipped with the reason.
