---
name: preflight
description: Proves a finished feature branch is production ready before anyone reviews it, then opens the PR. Syncs with the default branch, runs independent adversarial code and docs reviews, fixes what is local and verifiable with proof, puts trunk and intent issues in front of the user, validates lint, types, and the full test suite, and on the user's word pushes, opens a clean PR, and gives CI one repair round; never merges or force-pushes. Use when work on a branch is done and the user says "preflight", "is this ready", "get this PR-ready", "review this before I open a PR", or "ship it", or wants a branch validated before review.
argument-hint: "[a docs/specs/ path or one line of intent; blank to use the spec the branch changed]"
---

# Preflight

The review is the product; the PR is what a passing review earns.
Every finding is either fixed here with proof or put in front of the user, and nothing is dropped quietly.

## Gate

- Resolve the default branch from `origin/HEAD`, else `git ls-remote --symref origin HEAD`, else a local `main` or `master`.
  On it, stop: preflight reviews a feature branch, so the user names or creates one.
- Require a clean tree (`git status --porcelain` empty).
  Otherwise list the paths and stop, since uncommitted work would either ride into the PR unreviewed or be reviewed as if it ships.
- Settle the intent: the argument, else the spec the branch changed under `docs/specs/`, else one line from the user.
  Never infer it from transcripts.

## Sync

- With no remote, skip this section.
- The branch is published when `git ls-remote --exit-code origin refs/heads/<branch>` finds it, whatever its upstream or fetch refspec says.
  Fetch with explicit refspecs, `git fetch origin +refs/heads/<default>:refs/remotes/origin/<default>` plus the same for `<branch>` when published, since a single-branch clone's refspec skips them.
  When published, take teammate commits from `origin/<branch>` with `git merge --ff-only`, or a plain merge if it has diverged.
- An unpublished branch rebases onto `origin/<default>`; a published one merges `origin/<default>` in.
  Never rewrite published history or force-push: a lease protects the remote, not a teammate's local copy.
- Resolve mechanical conflicts (imports, lockfiles regenerated, both sides kept); a conflict where both sides change behavior goes to the user.

## Review

1. Run two reviews concurrently, in one message: dispatch the `code-reviewer` agent with the base, the range, and the intent, and run `/code-review high <base>...HEAD`.
   The explicit level keeps a remembered effort setting out, and the explicit range replaces the command's upstream-relative default scope.
   Never `ultra`, which is a billed cloud run only the user starts.
   When bundled skills are unavailable, proceed with `code-reviewer` alone and name the skip in the stop-point report and the PR's Review section.
2. Triage every finding from both reviews yourself; a reviewer's scope or severity is input, not a verdict.
   Fix it when all three hold: few dependents with nothing on the trunk (shared utilities, public interfaces, schemas, config), verifiable in this session, and the intent unchanged.
   A behavioral fix opens with a failing reproduction under `/tdd`.
   Commit each fix alone, its message naming the finding and carrying no AI attribution, which no later step can strip without rewriting history.
   Everything else is surfaced, and a finding that the approach itself is wrong stops preflight at once rather than waiting for the batch.
   A finding you judge false is rejected with evidence and still shown to the user.
3. Re-review once: dispatch `code-reviewer`, and only it, on the fix commits with the findings they claim to resolve.
   Whatever stays open is surfaced; there is no second pass.
4. Dispatch the `docs-reviewer` agent on the final range.
   Correct each false statement in its own commit: `docs/**`, code, agent files, and the changelog head directly, and skill files under `.claude/rules/skill-authoring.md`.
   A correction to `CLAUDE.md`, a `README.md`, `BRANDING.md`, `.claude/rules/`, or `docs/standards/` is drafted under `/curate-context` and held for the stop point, so the user approves it there rather than mid-run.
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
- Rejected findings with the evidence, docs corrected, held context-file corrections with their exact text, and every validation command with its result.
- A skipped `/code-review`, when bundled skills were unavailable.

A fix the user chooses is made, gets one scoped `code-reviewer` pass over its commits, runs Validate, and returns to this report.
An approved held correction is committed alone, then Validate runs before anything is pushed.
Nothing leaves the machine without an explicit yes, because a push and a PR are seen by others.

## Publish and CI

Read `references/publish-and-ci.md` before the first push; it holds the exact commands, the PR body, and the CI repair procedure.

- With no remote or no `gh`, stop here and hand over the push and PR commands instead of running them.
- Push without any force flag, and edit an existing PR only when it is `OPEN`.
- The PR body fills the template's Risk, Validation, and Review from the report and the branch's trunk commits, with no AI attribution.
- CI gets one repair round, passed locally first and pushed under the stop point's yes; a second failure or a cause outside the diff goes to the user.
- Never merge, and never re-run a job to turn it green.

Report `READY` (PR link, checks green), `READY_WITH_DEFERRALS` (PR link, what was deferred), or `BLOCKED` (what stopped it, what would clear it).
