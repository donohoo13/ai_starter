---
name: sdd-design
description: Get a Claude Design mockup for an approved spec that lists UI surfaces, and record the design the user approves before any plan exists. Reads design.md's state and does one step on the user's word, writing the design prompt, recording a skip or cancel, revising the prompt after a spec change, reading a returned Design artifact link into a committed snapshot, putting each miss and gap to the user, re-checking a recorded design against a revised spec, or approving it. Use when the user says "design this", "get mockups first", "write the design prompt", "sdd design", "here's the design link", "the design is approved", "skip the design", or when sdd status names sdd-design. Phase 2 of spec-driven development, section 8 of .claude/sdd/spec-driven-development.md.
argument-hint: "[slug] [Design artifact link]"
allowed-tools: Bash(.claude/sdd/bin/sdd *)
---

# SDD Design (phase 2)

Get a UI design for an approved spec from Claude Design and record the version the user approves, so the plan and the implementers build against a design someone signed off instead of guessing layout mid-build.
The rules live in section 8 (Design) of `.claude/sdd/spec-driven-development.md`; this file is only the procedure.
Where the two differ, the document wins.

The design conversation belongs to the user, in their own Claude chat or Claude Code `/design` session.
This session writes the prompt for it and records what comes back: it never invokes `/design`, never publishes or edits an artifact, and reads a Design artifact only through its link.

Arguments: `$ARGUMENTS`, an optional slug and, when the user is bringing a design back, its claude.ai artifact link.

## Preconditions

- The spec is approved and unchanged since approval, and its UI surfaces section lists at least one `UI-` ID.
  `.claude/sdd/bin/sdd status <slug> --json` then reports `2. Design`, or a later phase when no design is open.
- `1. Outline`: stop, and name `sdd-outline`, since a design for an unapproved spec designs a moving target.
- A spec with no UI surface: stop, say no design applies, and name the skill `status` reports; write no `design.md`.
- A phase after `3. Plan` with a request or a new link in hand: warn that a design approved now stales the plan and tasks, and continue only on yes.

## Start (section 4 (The workflow), start protocol)

1. Read sections 1–5 of the document once per session, then section 8 (Design).
2. Resolve the slug: the argument, else `.claude/sdd/bin/sdd find`, else list the folders it prints and ask.
3. Run `.claude/sdd/bin/sdd status <slug> --json` and check the preconditions.
   Note the spec's `approved_hash` and `artifacts.design`.
4. Load only what this phase needs: the project context (section 6 (Project principles and context)), the approved spec, `docs/sdd/<slug>/design.md` when it exists, and `DESIGN.md` when writing a prompt.

## Pick the step

`design.md`'s state and what the user brought decide the one step to run:

- **No `design.md`**: offer a design for the listed surfaces, or a skip; then Request or Skip on the user's answer.
- **`requested`, no `link` recorded, `based_on` matching the spec's `approved_hash`**: the prompt is out.
  With a link from the user, Record; with a request to stop, Cancel; otherwise show the Prompt section again and wait for the link.
- **`requested`, no `link` recorded, `based_on` behind the spec**: Revise the prompt.
- **`requested` with a `link` recorded**: finish Check, then Approve; when `based_on` is behind the spec, Re-check first.
- **`approved` and stale**, because the spec was re-approved: Re-check.
- **`approved` and current, with a new link**: the design was edited in Claude after approval; Record again.
- **`skipped`, with `status` at `2. Design`**: the spec now lists a surface the skip does not cover; offer a design for the uncovered surfaces, or a skip that covers them.

## Steps (section 8 (Design), Steps)

Each step that writes `design.md` runs only on the user's word in the conversation, because a request, skip, cancel or approval is their decision; then stage `docs/sdd/<slug>/design.md` by explicit path and propose a commit message in the repo's convention, and the user commits.

### Request

1. Run `.claude/sdd/bin/sdd set-status <slug> design requested`, which creates `design.md` from its template and records `based_on`; on an existing `design.md` it also clears the recorded `link`, `version`, `read`, `design_system` and approval, so the old design cannot be approved as the new one.
2. Write the prompt by the template in [references/design-prompt.md](references/design-prompt.md) under `## Prompt`, and write "None" under every other section.
3. Show the same text in the conversation as one fenced block the user can copy whole, so the committed prompt and the one they run never differ.
   Tell them to run it after `/design` in Claude Code or paste it into a Claude chat with Design selected, iterate there, and bring back the approved design's link, in this session or any later one.
4. Stage and propose the commit.
   A session without the Artifact tool, such as one authenticated by API key, Bedrock or Vertex, still writes the prompt; say that reading the link back needs a claude.ai-authenticated session.

### Skip or cancel

1. Run `.claude/sdd/bin/sdd set-status <slug> design skipped`, which records `decided_by`, the date, and the UI IDs the skip covers.
2. Write the user's reason under `## Skip reason`, and "None" under any other section still holding template text; a cancel keeps the prompt it already wrote.
3. Stage and propose the commit; `status` now reports `3. Plan`.

### Revise the prompt

The spec was re-approved while the prompt was out and nothing was recorded yet, so the running design conversation is working from an old spec.

1. Rewrite `## Prompt` against the revised spec.
2. List what changed in the conversation (surfaces, states, requirement IDs, non-goals), so the user can carry it into the running design conversation instead of starting over.
3. Run `.claude/sdd/bin/sdd set-status <slug> design requested` to refresh `based_on`, then stage and propose the commit.

### Record and check

Follow [references/record-design.md](references/record-design.md): read the link, save the snapshot, fill the record, and put each miss and each gap to the user.
A gap the user adds to the spec ends this run: name `sdd-outline`, and leave the design `requested` until the spec is re-approved.

### Re-check

The spec changed after a design was recorded.
Run the misses-and-gaps check of `references/record-design.md` against the revised spec and the committed snapshot, without reading the link again and without writing a new prompt; write a new prompt through Request only when the user asks for one.
Then set `based_on` in `design.md`'s frontmatter to the spec's new `approved_hash`, which sits outside the content hash, since Approve's lint fails on a `based_on` behind the spec before `approve` could record the new one, and go to Approve.

### Approve

1. While any miss or gap is unanswered, refuse approval and put the open items to the user.
2. Run `.claude/sdd/bin/sdd lint <slug> design` and fix every error.
3. Present the artboards, the accepted misses, the not-built list and the design system the canvas used, and ask for approval.
4. Only after the user approves in the conversation, run `.claude/sdd/bin/sdd approve <slug> design`, which refuses on a lint error or a missing `link`, `version` or `read`.
   Never approve on their behalf.
5. Stage `docs/sdd/<slug>/design.md` and `docs/sdd/<slug>/design/` by explicit path (the folder path also stages the artboard files a re-read deleted), and propose a commit message; the user commits.

## Outputs

- `docs/sdd/<slug>/design.md`: `requested` with its prompt, `skipped` with its reason, or `approved` with its record.
- `docs/sdd/<slug>/design/`: the snapshot of the approved Design artifact.

## Finish (section 4 (The workflow), finish protocol)

1. Exit checks: `.claude/sdd/bin/sdd lint <slug> design` reports 0 errors, and `status` reports `3. Plan` or later after a skip or an approval.
2. Name `sdd-plan` as the next skill after a skip or an approval, and the wait for the user's link after a request.
   Do not start `sdd-plan` unless the user said to run end to end.

## Next

`sdd-plan`, with `docs/sdd/<slug>/` as the handoff.
