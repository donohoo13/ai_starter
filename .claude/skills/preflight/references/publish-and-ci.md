# Publish and CI

Read before the first push. The exact commands and edge cases behind the Publish and CI rules in `SKILL.md`.

## Publish

- `git push -u origin <branch>`, never with any force flag.
- When `gh pr view --json state` shows an `OPEN` PR, update it with `gh pr edit`.
  Otherwise `gh pr create` against the default branch, since `gh pr view` also finds merged and closed PRs, and one on a reused branch is not this change's PR.
- The title is imperative and under 72 characters.
- The body follows `.github/PULL_REQUEST_TEMPLATE.md`; with no template, use its headings anyway:
  - **Summary:** what changed and why, linking the spec when one drove it.
  - **Validation:** each command run and its result.
  - **Review:** fixes made, docs corrected, and findings deferred with their reasons.
  - **QA:** what a human actually verified; "not yet human-verified" is an honest entry.
- No AI attribution anywhere in the title, body, or commits.

## CI

- `gh pr checks --watch`.
  A new PR's run takes a moment to register, so "no checks reported" gets a short wait and a few retries before it means the repo has no CI, which ends this section.
- On a failure, find the run with `gh run list --branch <branch> --status failure --limit 1 --json databaseId` and read `gh run view <id> --log-failed`; without a terminal, `gh run view` needs the id.
- If the cause is local by the three fix tests in `SKILL.md`, fix it in its own commit, pass the failing command locally, and push once under the stop point's yes.
- The repair cap is one round.
  A second failure, or one caused outside the diff (secrets, runners, outages), goes to the user with the failing excerpt.
- Never merge, and never re-run a job to turn it green.
