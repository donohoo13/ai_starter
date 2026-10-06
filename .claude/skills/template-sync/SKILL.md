---
name: template-sync
description: Pulls a newer release of the template this project was created from into the project, change by change. Reads `.ai-starter.yaml` for the template repository and the release the project last synced to, fetches that release and the target from the template's tags, classifies every file the template changed between them by comparing it with the project's copy, applies clean updates and three-way merges on the user's approval, hands every conflict and judgment call to the user, validates, commits, and records the new version; never pushes. Use in a project created from the template when the user says "sync the template", "pull template updates", "update from ai_starter", "what changed in the template", or "upgrade to the latest template", or when `.ai-starter.yaml` is behind the template's latest release.
argument-hint: "[target version, blank for the latest release]"
---

# Template Sync

A project shares no git history with its template, so sync rebuilds the history it needs.
The template at the release the project last synced to is the common ancestor, and the template at the target release is the change.
Every decision about a file comes from comparing those two with the project's copy, which is why no ownership list is needed: a file the template did not change is never touched, and a file the project changed is merged, never overwritten.

## Gate

- Read `.ai-starter.yaml` for `template` (owner/repo) and `version` (the last synced release).
  Missing, stop and say why: without a base release, sync cannot tell a project edit from a template change.
  Hand over the file with `template` filled and `version` set to the release the project started from, if the user knows it.
- When `template` names this repository's own origin, stop: the template never syncs into itself.
- Require a clean tree, since a sync mixed with unrelated work cannot be reviewed or reverted on its own.
  On the default branch, create `chore/template-sync-<target>` from it before any change.
- Resolve the target: the argument, else the highest `vX.Y.Z` in `gh api repos/<template>/tags --paginate --jq '.[].name'`.
  A target no newer than `version` ends here with "already on v<version>".

## Fetch

- Clone the target into a temp directory outside the repository and add the base tag:
  `gh repo clone <template> <tmp> -- --depth 1 --branch v<target> --quiet`, then `git -C <tmp> fetch --quiet --depth 1 origin tag v<version>`.
  `gh` carries the user's auth, so a private template works.
  A base tag that no longer exists stops sync: name the missing tag, since any other base would misread project edits, and let the user set `version` to a release they know the project matches.
- Read the target's `CHANGELOG.md` entries newer than `version`.
  They carry the intent and adaptation notes that every merge and conflict below is judged against.
- List what changed: `git -C <tmp> diff --name-status -M v<version> v<target>`.

## Classify

Leave out paths a project is meant to own or delete: `CHANGELOG.md`, `README.md`, `.claude/rules/template-dev.md`, `docs/specs/`, `docs/notes/`, and `pnpm-lock.yaml`, which is regenerated rather than copied.
`.ai-starter.yaml` is written last, by sync itself.

For every other changed path, compare the project's copy with the base (`git -C <tmp> show v<version>:<path>`):

- **Clean update**: modified by the template, and the project's copy equals the base. Take the target.
- **Merge**: modified by the template, and the project's copy differs from the base. Run `git merge-file -p <project> <base> <target>`; a result without conflict markers is a merge.
- **Conflict**: a merge that leaves markers, or a new template file at a path the project already uses.
- **New**: added by the template at a free path. Add it.
- **Removed**: deleted by the template. Delete it only when the project's copy equals the base; otherwise it is a conflict.
- **Renamed**: apply the move when the project's copy equals the base; otherwise it is a conflict.
- **Project-deleted**: modified by the template, but the project removed the file the base shipped. Skip it, since restoring what the project deleted is the user's call.

`CLAUDE.md`, `.claude/settings.json`, `BRANDING.md`, and `package.json` mix template and project content, so they always get a full diff and their own approval, even when the merge is clean.

## Plan

Present one plan and wait:

- From and to versions, and a short summary of the changelog intent.
- Clean updates and new files as one list under a single approval the user can trim.
- Each merge with its diff, and each shared file with its full diff.
- Each conflict with both sides, for the user to resolve or skip.
  Sync never picks a side itself, because the right resolution depends on what the project meant by its edit.
- Skipped paths and why: residue, project-deleted, or left out by rule.

The plan's approval covers edits to context files (`CLAUDE.md`, `.claude/rules/`, `docs/standards/`), since their exact text was shown.

## Apply

- Apply what was approved, and only that.
- Run `pnpm install` when `package.json` or `pnpm-workspace.yaml` changed, so the lockfile follows, then the project's format, lint, typecheck, and test commands from `CLAUDE.md` and the manifest.
  A failure is reported with its output, not fixed here; the cause is template content meeting project code, and fixing project code is separate work the user schedules.
- Write the target into `.ai-starter.yaml` when every change was applied or deliberately skipped.
  A skipped change stays skipped, because the next sync compares from the new base and only shows changes the template makes after it.
  A change the user defers ("not now") keeps the old version recorded, so the next run proposes it again.
- Commit on the branch, by explicit path: `chore: sync template to v<target>`, with a body listing what was applied, skipped, and deferred.
  No AI attribution.
  Delete the temp directory.

Report the from and to versions, counts per group, every skip and deferral with its reason, any conflict left unresolved, and the validation result.
Never push or open a PR.
