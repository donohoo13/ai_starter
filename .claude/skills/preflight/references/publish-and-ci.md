# Publish and CI

Read before the first push. The exact commands and edge cases behind the Publish and CI rules in `SKILL.md`.

## Publish

- `git push -u origin <branch>`, never with any force flag.
- When `gh pr view --json state` shows an `OPEN` PR, update it with `gh pr edit`.
  Otherwise `gh pr create` against the default branch, since `gh pr view` also finds merged and closed PRs, and one on a reused branch is not this change's PR.
- The title is imperative and under 72 characters.
- The body follows `.github/PULL_REQUEST_TEMPLATE.md`; with no template, use its headings anyway:
  - **Summary:** what changed and why, linking the spec when one drove it.
  - **Risk:** a level, then the evidence behind it, so the human reviewer knows where to look.
    The evidence is every trunk touch point from `code-reviewer`'s review of the full range with its consumer count, then every trunk commit on the branch (`git log --grep='^Trunk change:' <base>..HEAD`) with the skeptic's verdict and any alternative not taken, quoted from its body.
    The highest level any piece of evidence reaches is the PR's level:
    - **High:** a schema or migration, an auth or security path, or an interface with consumers outside the repository.
    - **Medium:** any other trunk touch point.
    - **Low:** the branch's own code only, said in one line.
  - **Validation:** each command run and its result.
  - **Review:** fixes made, docs corrected, findings deferred with their reasons, and a skipped `/code-review` named.
  - **QA:** what a human actually verified; "not yet human-verified" is an honest entry.
- No AI attribution anywhere in the title, body, or commits.

## CI

- `gh pr checks --watch`.
  A new PR's run takes a moment to register, so "no checks reported" gets a short wait and a few retries before it means the repo has no CI, which ends this section.
- On a failure, list every run for the pushed commit with `gh run list --commit <HEAD sha> --json databaseId,name,conclusion`, and read `gh run view <id> --log-failed` for each whose conclusion is not `success` or `skipped`.
  Filtering by commit keeps an earlier push's failure out, and checking every non-success conclusion catches `timed_out` and `cancelled` runs; without a terminal, `gh run view` needs the id.
- If the cause is local by the three fix tests in `SKILL.md`, fix it in its own commit, pass the failing command locally, and push once under the stop point's yes.
- The repair cap is one round.
  A second failure, or one caused outside the diff (secrets, runners, outages), goes to the user with the failing excerpt.
- Never merge, and never re-run a job to turn it green.
