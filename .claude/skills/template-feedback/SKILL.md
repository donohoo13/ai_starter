---
name: template-feedback
description: Reports a finding about the template this project was created from as a GitHub issue on the template's repository, such as a bug, a stale or wrong instruction in a shipped skill, rule, standard, script, or config, or a gap the template should cover. Reads `.ai-starter.yaml` for the template and the project's release, separates template defects from project edits, verifies the finding against the template's latest release so nothing already fixed gets filed, checks for duplicates, strips anything private to the project, and files only after the user approves the exact draft. Use in a project created from the template when the user says "report this to the template", "file template feedback", "this is a template bug", "send this upstream", or "open an issue on ai_starter", or when a session finds a defect in a file that came from the template.
argument-hint: "[the finding in one line, blank to draft from the session]"
---

# Template Feedback

A finding helps upstream only when it is true of the current template, reproducible from the template alone, and free of anything private to this project.
Each step below protects one of those three.

## Gate

- Read `.ai-starter.yaml` for `template` (owner/repo) and `version`.
  Missing, ask the user for the template repository and record the project's release as unknown in the issue.
- When `template` names this repository's own origin, stop: a finding about the template is fixed here, not filed.
- When `gh auth status` fails, draft as below and hand over the text for the user to file by hand.

## Shape

From the argument or the session, settle what is wrong, which template file it lives in (the path as the template ships it), how to see it, and what was expected.
Ask the user only for what the session cannot determine.

A defect that lives only in project code, or in a template file the project has since edited, is not a template finding.
Fetch the template at the project's release (`gh repo clone <template> <tmp> -- --depth 1 --branch v<version> --quiet`, into a temp directory outside the repository) and diff the project's copy of the file against it.
When the project's edit introduced the defect, say so and stop.

## Verify

- Clone the latest release the same way: the highest `vX.Y.Z` in `gh api repos/<template>/tags --paginate --jq '.[].name'`, or the default branch when there are no tags, said so in the issue.
- Check the finding against that copy.
  Already fixed, stop and name the release that fixed it from its `CHANGELOG.md` entry; updating the project to that release resolves it.
- Search for duplicates: `gh issue list -R <template> --state all --search "<key terms>" --limit 10`.
  On a match, show it and let the user choose to comment on it (`gh issue comment`), file anyway, or stop.

## Scrub

An issue tracker is outside the machine, and the template's may be public.
Remove secrets, keys, tokens, environment values, customer data, internal hostnames and URLs, and project code; quote only template files, and describe the project in one generic line.
A security vulnerability is never filed as an issue: stop and tell the user to report it privately to the template's maintainer, through a GitHub security advisory or direct contact.

## Draft and file

The title names the defect in under 72 characters, and the body runs:

```markdown
## Template version

Project on v<version>; verified against v<latest>.

## Finding

<what is wrong, in two or three sentences>

## Where

`<template path>:<line>` with a short excerpt from the template file.

## How to reproduce

<steps that work from the template alone>

## Expected

<what should happen instead>

## Suggested fix

<optional>
```

Show the exact title and body, then file with `gh issue create -R <template> --title "<title>" --body-file -` only on the user's yes, since a filed issue is visible to others the moment it exists.
No AI attribution.
Report the issue URL and delete the temp directories.
