---
name: sdd-review
description: Review the current branch before a PR. With a spec it runs the full Validate phase: evidence, spec conformance in a fresh subagent, the code-review skill for correctness and the standards-reviewer agent for legibility and usability, then one review.md report that records each finding's disposition and a PR description draft; a review an earlier session left open resumes from that report instead of running again. Without a spec it runs only the correctness and standards reviews and reports in the conversation. Use when the user says "review", "review this branch", "final review", "run the reviews", "sdd review", "resume the review", or wants a branch checked before opening or marking a PR. Phase 6 of spec-driven development, section 13 of .claude/sdd/spec-driven-development.md.
argument-hint: "[slug] [effort low|medium|high|xhigh|max] [--max-findings n] [base]"
allowed-tools: Bash(.claude/sdd/bin/sdd *)
---

# SDD Review (phase 6)

Two reviewers, two purposes, one report, plus the spec's own evidence when there is a spec.
Correctness belongs to the `code-review` skill; legibility and usability belong to the `standards-reviewer` agent.
Neither is skipped, and no finding is dropped quietly.
This session orchestrates and may be the one that ran the build: every reviewer runs in a fresh context on a brief of pointers only, so its judgment never inherits this session's reasoning, and every fix is built by a fresh `implementer`.
The rules live in section 13 (Validate) of `.claude/sdd/spec-driven-development.md`; this file is only the procedure.
Where the two differ, the document wins.

Arguments: `$ARGUMENTS`.

## Mode

Parse the arguments: a token is the slug only when `docs/sdd/<token>/` exists; one of `low`, `medium`, `high`, `xhigh`, `max` is the effort; `--max-findings n` is the findings cap; the remaining token, if any, is the base.

- **Spec mode** when a slug was given, or when `.claude/sdd/bin/sdd find` resolves one and `.claude/sdd/bin/sdd status <slug> --json` reports `phase` `6. Validate`.
  Runs the full Validate phase inside the start and finish protocols of section 4 (The workflow).
  When `find` resolves a spec that is not at `6. Validate`, say so, name the phase and skill `status` reports, and ask before reviewing without it.
- **Review-only mode** otherwise: a pre-PR review of any branch, for example after a `tdd` one-shot.
  It skips the protocols and every step marked _(spec only)_, writes no file, and reports in the conversation.

State which mode you are in, and why, as your first line.

## Resume _(spec only)_ (section 13 (Validate), Resume)

When `status` reports `review.md` at `open`, an earlier session already wrote the report, and this run continues it from that file alone.
Do Start, then the steps below; the clean-tree and effort preconditions, Run, Triage and the writing of the report apply again only to a rerun.

1. Read the spec's `review.md` in full.
   Its frontmatter records the base, range, effort and cap this review runs with, so ask for none of them again.
2. Check that the branch is still the one reviewed.
   `range` ends at the commit the reviewers read, and every commit after it should be one a Fixes entry names: compare `git log --oneline <that commit>..HEAD` with them.
   When the log shows any other commit, fails because that commit is gone from the branch, or `range` names no commit hash, the report may describe code that has since changed: show the user what you found and ask whether to rerun the review or continue on the report as written.
3. Run `.claude/sdd/bin/sdd uncommitted <slug>`.
   Any path it lists is work the earlier session left unfinished, usually the fix for a `picked` finding.
   List the paths and ask whether to hand them to a fresh `implementer` to finish that fix or to wait while the user sets them aside by hand; never stash, reset or discard them yourself.
4. Tell the user where the review stands, counting the findings by disposition, then continue from them: each `picked` finding goes through Fixes, each `open` one is put to the user as in Report, then wait, and with neither left the review moves to Confirm intent and close.

A rerun, chosen here or offered after substantial fixes, starts from the clean tree of Preconditions and runs Run and Triage again.
It rewrites the report for the new range without losing a decision: every finding the user has decided keeps its line and disposition, the Fixes entries stay, the new findings replace those still `open`, and a new finding that repeats a decided one is left out.

## Preconditions (section 13 (Validate), Gate)

- Spec mode: `status` reports `6. Validate`, so every task is done.
  Anything else: stop, tell the user the phase and the skill `status` names, and do no other phase's work.
- A feature branch with a clean tree.
  Spec mode: `.claude/sdd/bin/sdd uncommitted <slug>` reports `0 uncommitted paths`; it lists what `git status --porcelain` lists except this spec's own `review.md`, which the review leaves uncommitted until acceptance.
  Review-only mode: `git status --porcelain` prints nothing.
  Otherwise list the paths and stop; uncommitted work would be reviewed as if it ships.
- Base: the argument; else what `.claude/sdd/bin/sdd base` prints, run with the slug in spec mode: the base the spec records, else the remote's default branch.
  Ask the user which branch the work merges into only when the helper refuses because git could not tell.
- Effort and cap: the arguments.
  Absent, ask once with the AskUserQuestion tool, suggesting `high` or `xhigh` and a cap of 3 to 5 scaled to `git diff --stat <base>...HEAD`.

## Start _(spec only)_ (section 4 (The workflow), start protocol)

1. Read sections 1–5 of the document once per session, then section 13 (Validate).
2. Load the spec, the plan's Traceability table and seams, and the tasks.
   Load the repo's test-running skill when it has one.

## Run (section 13 (Validate), Run), in parallel where possible

1. **Evidence** _(spec only)_: run the full suite once on the clean tree with the repo's test tiers, from the commands `CLAUDE.md` names, or the ones the `tdd` discovery in `.claude/skills/tdd/references/discover.md` finds for this repo.
   Map each acceptance criterion to the test that proves it, by file and test name.
   Measure each non-functional requirement instead of assuming it.
2. **Spec conformance** _(spec only)_: dispatch a general-purpose subagent through the Agent tool with the prompt in [references/conformance-review.md](references/conformance-review.md), its five placeholders filled in: the spec, plan and tasks paths, the repository root, and the base.
   It gets the files and the diff, never your reasoning.
3. **Correctness**: invoke the `code-review` skill through the Skill tool with the effort level, `--max-findings <n>`, and this branch against the base as its target, in the form `<effort> --max-findings <n> <base>...HEAD`.
   It runs as a forked skill, a subagent that does not see this conversation, so pass nothing but that target.
   Keep its findings verbatim.
4. **Standards**: dispatch the `standards-reviewer` agent through the Agent tool with two inputs: the base ref and the commit range `<base>..HEAD`. It judges legibility, tests as documentation, usability floors and customer-facing text against `CLAUDE.md` and the `docs/standards/` files whose globs match the changed paths.

## Triage (section 13 (Validate), Triage)

Every finding is input, not a verdict.
Judge each one yourself.
Reject a finding you judge false, with evidence, and still show it to the user.
Drop findings the linter already owns.
Do not pad the report with style preferences.

## Report, then wait (section 13 (Validate), Report, then wait)

- Spec mode: write `docs/sdd/<slug>/review.md` from `.claude/sdd/templates/review.md`, with `base`, `range`, `effort`, `max_findings` and `updated` filled in and every section populated from the runs above, with no template placeholder left in them.
  Leave the PR description draft section as the template wrote it: its placeholders stay until acceptance, and `lint` reports them until then.
  Name the head in `range` by its commit hash rather than `HEAD`, since a later session compares it with the branch.
  Write each conformance gap, correctness finding and standards finding as its own top-level bullet with `- Disposition: open` under it, as the template shows, and `- None` in a section with no finding; a later session resumes from those lines.
  Show the report.
- Review-only mode: present the same sections in the conversation, without Spec conformance.

Then stop and wait for the user.

## Fixes (section 13 (Validate), Fixes)

The user picks which findings to fix.
Spec mode: write each decision to the finding's `Disposition:` line in `review.md` before dispatching anything, since the file is the only record of it a later session has.
A finding to fix becomes `picked`, one the user turns down or postpones becomes `declined` or `deferred` with their reason, one they have not spoken to stays `open`, and a rejected finding they pick moves back to its findings section as `picked`.
For each picked finding, dispatch a fresh `implementer` through the Agent tool with the slug when there is one, the finding verbatim with its `file:line`, and the requirement IDs it touches, to fix it red-first; this session never writes the fix itself.
Verify its report with the full suite and by matching the files it names against every path `.claude/sdd/bin/sdd uncommitted <slug>` lists, or `git status --porcelain` in review-only mode; on a mismatch or a failure, resume the same agent once with what you found.
Stage by explicit path, propose a commit message, and commit only on the user's word.
Never push.
Once the fix is committed, record it under Fixes in the report with its test and commit, and set the finding to `fixed`.
Offer to rerun the review when the fixes are substantial; a rerun follows the last paragraph of Resume.

## Confirm intent and close (section 13 (Validate), Confirm intent and close)

1. Restate in plain language what was built and ask the user to confirm it is what they meant.
   Passing tests prove the code matches the spec, not that the spec matched the intent.
2. On the user's acceptance, draft the PR description: a summary paragraph following the rules in section 7 (Outline), what changed, how it was verified with evidence, and the decisions made and follow-ups.
   Spec mode: write the draft into `review.md` first, run `.claude/sdd/bin/sdd lint <slug>` as the exit check until `review.md` reports 0 errors, then `.claude/sdd/bin/sdd set-status <slug> review accepted`, which refuses while review lint reports an error.
   A lint error for a finding still `open` or `picked` clears only through the user's decision or the finished fix, never by editing the disposition to pass.
   Review-only mode: put the draft in the conversation.
3. In spec mode, stage `docs/sdd/<slug>/review.md` by explicit path and propose its commit message; the folder stays as the record of the change.
   Never push or open the PR unless the user asks.

## Outputs

- Spec mode: `docs/sdd/<slug>/review.md` at `accepted` with the PR description draft, and the fixes the user picked, committed on their word.
- Review-only mode: the report and the PR description draft in the conversation, and the fixes the user picked.

## Next

None.
The chain ends here.
