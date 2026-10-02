---
name: preflight
description: Proves a finished feature branch is production ready before anyone reviews it, then opens the PR. Syncs with the default branch, runs independent adversarial code and docs reviews, fixes what is local and verifiable with proof, puts trunk and intent issues in front of the user, validates lint, types, and the full test suite, and on the user's word pushes, opens a clean PR, and gives CI one repair round; never merges or force-pushes. Use when work on a branch is done and the user says "preflight", "is this ready", "get this PR-ready", "review this before I open a PR", or "ship it", or wants a branch validated before review.
argument-hint: "[a docs/specs/ path or one line of intent; blank to use the spec the branch changed]"
---

# Preflight

The review is the product; the PR is what a passing review earns.
Every finding is either fixed here with proof or put in front of the user, and nothing is dropped quietly.

## Gate

- Resolve the default branch from `origin/HEAD`, or `gh repo view` when that is unset.
  On it, stop: preflight reviews a feature branch, so the user names or creates one.
- Require a clean tree (`git status --porcelain` empty).
  Otherwise list the paths and stop, since uncommitted work would either ride into the PR unreviewed or be reviewed as if it ships.
- Settle the intent: the argument, else the spec the branch changed under `docs/specs/`, else one line from the user.
  Never infer it from transcripts.

## Sync

- `git fetch origin`; the branch is published when `origin/<branch>` exists afterwards, whatever its upstream setting says.
  Take teammate commits from `origin/<branch>` first with `git merge --ff-only`, or a plain merge if it has diverged.
- An unpublished branch rebases onto `origin/<default>`; a published one merges `origin/<default>` in.
  Never rewrite published history or force-push: a lease protects the remote, not a teammate's local copy.
- Resolve mechanical conflicts (imports, lockfiles regenerated, both sides kept); a conflict where both sides change behavior goes to the user.

## Review

1. Dispatch the `code-reviewer` agent with the base, the range, and the intent.
2. Triage every finding yourself; the agent's scope is input, not a verdict.
   Fix it when all three hold: few dependents with nothing on the trunk (shared utilities, public interfaces, schemas, config), verifiable in this session, and the intent unchanged.
   A behavioral fix opens with a failing reproduction under `/tdd`.
   Commit each fix alone, its message naming the finding.
   Everything else is surfaced, and a finding that the approach itself is wrong stops preflight at once rather than waiting for the batch.
   A finding you judge false is rejected with evidence and still shown to the user.
3. Re-review once: dispatch `code-reviewer` on the fix commits with the findings they claim to resolve.
   Whatever stays open is surfaced; there is no second pass.
4. Dispatch the `docs-reviewer` agent on the final range.
   Correct false statements under `docs/**` and in code directly; a correction to `CLAUDE.md`, a `README.md`, `BRANDING.md`, or `.claude/rules/` goes through `/curate-context`.
   Gaps are surfaced as suggestions.

## Validate

- Run the project's lint, format check, typecheck, and full test suite, discovered from `CLAUDE.md` and the manifest rather than assumed.
- Fix failures that pass the same three tests, one commit each.
  A test that flips between runs is flaky: surface it, never rerun until green.
- After the last fix, run everything again; it all passes or the user defers what does not.

## Stop point

Present one report and wait:

- The intent and each fix commit with the finding it resolves.
- Each surfaced finding quoted with `file:line`, scope, and the choice of fix, defer, or skip.
- Rejected findings with the evidence, docs corrected, and every validation command with its result.

A fix decision goes back through Review and Validate.
Nothing leaves the machine without an explicit yes, because a push and a PR are seen by others.

## Publish

- `git push -u origin <branch>`, never with any force flag.
- When `gh pr view --json state` shows an `OPEN` PR, update it with `gh pr edit`; otherwise `gh pr create` against the default branch, since a merged or closed PR on a reused branch is not this change's PR.
  The title is imperative and under 72 characters.
  The body follows `.github/PULL_REQUEST_TEMPLATE.md`, filling Validation with each command and its result and Review with the fixes made, docs corrected, and findings deferred with their reasons; with no template, use those same headings.
  QA states what a human actually verified, and "not yet human-verified" is an honest entry.
  No AI attribution anywhere.
- With no remote or no `gh`, stop after the report and hand over the commands.

## CI

- `gh pr checks --watch`.
  A new PR's run takes a moment to register, so "no checks reported" gets a short wait and a few retries before it means the repo has no CI, which skips this section.
- On a failure, find the run with `gh run list --branch <branch> --limit 1 --json databaseId` and read `gh run view <id> --log-failed`, since without a terminal it needs the id.
  Fix and push once if the cause is local by the same three tests.
- The repair cap is one round.
  A second failure, or one caused outside the diff (secrets, runners, outages), goes to the user with the failing excerpt.
- Never merge, and never re-run a job to turn it green.

Report `READY` (PR link, checks green), `READY_WITH_DEFERRALS` (PR link, what was deferred), or `BLOCKED` (what stopped it, what would clear it).
