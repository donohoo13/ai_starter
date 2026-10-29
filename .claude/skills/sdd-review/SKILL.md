---
name: sdd-review
description: Review the current branch before a PR. With a spec it runs the full Validate phase: evidence, spec conformance in a fresh subagent, the code-review skill for correctness and the standards-reviewer agent for legibility and usability, then one review.md report and a PR description draft. Without a spec it runs only the correctness and standards reviews and reports in the conversation. Use when the user says "review", "review this branch", "final review", "run the reviews", "sdd review", or wants a branch checked before opening or marking a PR. Phase 5 of spec-driven development, section 12 of .claude/sdd/spec-driven-development.md.
argument-hint: "[slug] [effort low|medium|high|xhigh|max] [--max-findings n] [base]"
allowed-tools: Bash(.claude/sdd/bin/sdd *)
---

# SDD Review (phase 5)

Two reviewers, two purposes, one report, plus the spec's own evidence when there is a spec.
Correctness belongs to the `code-review` skill; legibility and usability belong to the `standards-reviewer` agent.
Neither is skipped, and no finding is dropped quietly.
The rules live in section 12 (Validate) of `.claude/sdd/spec-driven-development.md`; this file is only the procedure.
Where the two differ, the document wins.

Arguments: `$ARGUMENTS`.

## Mode

Parse the arguments: a token is the slug only when `docs/sdd/<token>/` exists; one of `low`, `medium`, `high`, `xhigh`, `max` is the effort; `--max-findings n` is the findings cap; the remaining token, if any, is the base.

- **Spec mode** when a slug was given, or when `.claude/sdd/bin/sdd find` resolves one and `.claude/sdd/bin/sdd status <slug> --json` reports `phase` `5. Validate`.
  Runs the full Validate phase inside the start and finish protocols of section 4 (The workflow).
  When `find` resolves a spec that is not at `5. Validate`, say so, name the phase and skill `status` reports, and ask before reviewing without it.
- **Review-only mode** otherwise: a pre-PR review of any branch, for example after a `tdd` one-shot.
  It skips the protocols and every step marked _(spec only)_, writes no file, and reports in the conversation.

State which mode you are in, and why, as your first line.

## Preconditions (section 12 (Validate), Gate)

- Spec mode: `status` reports `5. Validate`, so every task is done.
  Anything else: stop, tell the user the phase and the skill `status` names, and do no other phase's work.
- A feature branch with a clean tree: `git status --porcelain` prints nothing.
  Otherwise list the paths and stop; uncommitted work would be reviewed as if it ships.
- Base: the argument; else the repo's default branch from `git symbolic-ref --short refs/remotes/origin/HEAD` without the `origin/` prefix; else a local `main` or `master`.
- Effort and cap: the arguments.
  Absent, ask once with the AskUserQuestion tool, suggesting `high` or `xhigh` and a cap of 3 to 5 scaled to `git diff --stat <base>...HEAD`.

## Start _(spec only)_ (section 4 (The workflow), start protocol)

1. Read sections 1–5 of the document once per session, then section 12 (Validate).
2. Load the spec, the plan's Traceability table and seams, and the tasks.
   Load the repo's test-running skill when it has one.

## Run (section 12 (Validate), Run), in parallel where possible

1. **Evidence** _(spec only)_: run the full suite once on the clean tree with the repo's test tiers, from the commands `CLAUDE.md` names, or the ones the `tdd` discovery in `.claude/skills/tdd/references/discover.md` finds for this repo.
   Map each acceptance criterion to the test that proves it, by file and test name.
   Measure each non-functional requirement instead of assuming it.
2. **Spec conformance** _(spec only)_: dispatch a general-purpose subagent through the Agent tool with the prompt in [references/conformance-review.md](references/conformance-review.md), its five placeholders filled in: the spec, plan and tasks paths, the repository root, and the base.
   It gets the files and the diff, never your reasoning.
3. **Correctness**: invoke the `code-review` skill through the Skill tool with the effort level, `--max-findings <n>`, and this branch against the base as its target, in the form `<effort> --max-findings <n> <base>...HEAD`. Keep its findings verbatim.
4. **Standards**: dispatch the `standards-reviewer` agent through the Agent tool with two inputs: the base ref and the commit range `<base>..HEAD`. It judges legibility, tests as documentation, usability floors and customer-facing text against `CLAUDE.md` and the `docs/standards/` files whose globs match the changed paths.

## Triage (section 12 (Validate), Triage)

Every finding is input, not a verdict.
Judge each one yourself.
Reject a finding you judge false, with evidence, and still show it to the user.
Drop findings the linter already owns.
Do not pad the report with style preferences.

## Report, then wait (section 12 (Validate), Report, then wait)

- Spec mode: write `docs/sdd/<slug>/review.md` from `.claude/sdd/templates/review.md`, with `base`, `range`, `effort`, `max_findings` and `updated` filled in and every section populated from the runs above, with no template placeholder left in them.
  Leave the PR description draft section as the template wrote it: its placeholders stay until acceptance, and `lint` reports them until then.
  Show the report.
- Review-only mode: present the same sections in the conversation, without Spec conformance.

Then stop and wait for the user.

## Fixes (section 12 (Validate), Fixes)

The user picks which findings to fix.
Build each one through the `tdd` skill via the Skill tool, with the finding as the behavior and "Unit of work: this fix." as its unit of work.
Validate with the repo's test tiers, stage by explicit path, propose a commit message, and commit only on the user's word.
Never push.
Record each fix under Fixes in the report.
Offer to rerun the review when the fixes are substantial.

## Confirm intent and close (section 12 (Validate), Confirm intent and close)

1. Restate in plain language what was built and ask the user to confirm it is what they meant.
   Passing tests prove the code matches the spec, not that the spec matched the intent.
2. On the user's acceptance, draft the PR description: a summary paragraph following the rules in section 7 (Outline), what changed, how it was verified with evidence, and the decisions made and follow-ups.
   Spec mode: write the draft into `review.md` first, run `.claude/sdd/bin/sdd lint <slug>` as the exit check until `review.md` reports 0 errors, then `.claude/sdd/bin/sdd set-status <slug> review accepted`, which refuses while review lint reports an error.
   Review-only mode: put the draft in the conversation.
3. In spec mode, stage `docs/sdd/<slug>/review.md` by explicit path and propose its commit message; the folder stays as the record of the change.
   Never push or open the PR unless the user asks.

## Outputs

- Spec mode: `docs/sdd/<slug>/review.md` at `accepted` with the PR description draft, and the fixes the user picked, committed on their word.
- Review-only mode: the report and the PR description draft in the conversation, and the fixes the user picked.

## Next

None.
The chain ends here.
