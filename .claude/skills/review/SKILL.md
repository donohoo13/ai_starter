---
name: review
description: Runs two independent reviews of the current branch before a PR, reports them once, and waits for the user to pick what gets fixed. Claude Code's bundled /code-review covers correctness at a chosen effort and findings cap; the standards-reviewer agent covers legibility and usability against the docs/standards/ files the diff's paths match. Never pushes or opens a PR. Use when a branch's work is built and the user says "review", "review this branch", "final review", "run the reviews", or wants a branch checked before opening or marking a PR.
argument-hint: "[effort low|medium|high|xhigh|max] [--max-findings n] [base ref, default: the default branch]"
---

# Review

Two reviewers, two purposes, one report.
Correctness belongs to Claude Code's bundled `/code-review`; legibility and usability belong to the `standards-reviewer` agent.
Neither is skipped, no finding is dropped quietly, and nothing is fixed until the user picks it, because the user decides what the branch ships.

## Gate

- Resolve the default branch from `origin/HEAD`, else `git ls-remote --symref origin HEAD`, else a local `main` or `master`.
  The base is the argument's ref when it names one, otherwise that branch.
  On the default branch itself, stop: a review reads a feature branch, so the user names or creates one.
- Require a clean tree (`git status --porcelain` empty).
  Otherwise list the paths and stop, since uncommitted work would be reviewed as if it ships.
- Settle the effort and the findings cap from the argument.
  Absent either, ask once, recommending `high` with a cap of three to five scaled to the size of the diff.
  Never `ultra`, which is a billed cloud run only the user starts.

## Run

1. Run both reviews concurrently, in one message: invoke `/code-review <effort> --max-findings <n> <base>...HEAD` through the Skill tool, and dispatch the `standards-reviewer` agent with the base ref and the commit range `<base>..HEAD`.
   The explicit level and cap keep a remembered setting out, and the explicit range replaces the command's upstream-relative default scope.
   When bundled skills are unavailable, proceed with `standards-reviewer` alone and name the skip in the report.
2. Wait for both before triage; when one has not arrived, end the turn and resume from it when it does.
3. Triage every finding yourself; a reviewer's severity is input, not a verdict.
   A finding you judge false is rejected with evidence and still shown to the user.
   A finding the linter or formatter already owns is dropped.

## Report, then wait

Present one report, then stop:

- Correctness findings with severity and `file:line`, kept verbatim from `/code-review`.
- Standards findings with the standards line each fails.
- The standards reviewer's reads-well notes.
- Rejected findings with their evidence, and the `/code-review` skip when there was one.

A fix the user picks is made in this session under `/tdd`, a behavioral fix opening with a failing reproduction.
Validate it with the project's lint, format check, typecheck, and the touched tests, discovered from `CLAUDE.md` and the manifest rather than assumed.
Stage it by explicit path and hand back a commit message, imperative subject and no AI attribution, for the user to commit.
Nothing is pushed from here.
