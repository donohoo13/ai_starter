---
name: curate-context
description: Curation discipline for the prescriptive context files, every CLAUDE.md and CLAUDE.local.md at any depth (the user-global ~/.claude/CLAUDE.md included), README.md, BRANDING.md, the rules under .claude/rules/, and the coding standards under docs/standards/. Use whenever a session is about to create or edit one of these files, whatever brought the edit, a convention to record, a doc correction, or an edit arriving mid-task with nobody naming this skill; the file path is the trigger. Also the distillation path, when the user says "codify", "capture this convention", "add this to CLAUDE.md", or "we should document this". No model-invented content lands unseen.
argument-hint: "[optional: the edit or lesson to consider]"
---

# Curate Context

The discipline for the files that steer future sessions: every `CLAUDE.md` and `CLAUDE.local.md` (root, nested, `~/.claude/CLAUDE.md`), every `README.md`, `.claude/rules/`, `docs/standards/`, and `BRANDING.md`.
Every edit to one loads this skill first; only this description and the `CLAUDE.md` rule enforce that.
`.claude/skills/` follows `.claude/rules/skill-authoring.md`.

A rule is paid for by every future session that loads the file.
Default to writing nothing; when writing, hold the edit near zero net growth.
Forcing output is this skill's primary failure mode.

Two entry paths.
The common one is a governed edit already on the table, for any reason, whether or not anyone said "codify".
The other is distillation: the user asks to capture a lesson, or accepts a suggestion to.
Suggest it at most once per session and only when a genuine candidate surfaced (an undocumented convention got violated, a real gotcha came out of debugging), never as a session-end ritual, because an offer that fires regardless trains the user to ignore it.

## Triage

Every edit verifies its facts against the current code, routes to the narrowest correct file, and states its net line count.
A **new rule** runs the full process below.
A **correction** (renamed command, moved path, changed count) verifies and applies at zero growth or below.
A **deletion** is cheap but never silent: say what dies and why.

A candidate this session proposed lands only after the user approves it.
A user-directed edit carries its own approval but runs the same bar, with pushback when it fails ("the linter already enforces this; still want it in prose?").

## Attribute

A candidate born from friction (a correction, a redo, a "not like that") is root-caused first.
**(A)** The prompt steered wrong, a one-time ambiguity: do not codify.
**(B)** A real convention was undocumented and a future session would repeat the mistake: the only candidate.
**(C)** You erred with adequate context: own it, do not memorialize it.
Say which and why; the user can overrule.

## Admission bar

A rule is something a session cannot infer and would plausibly get wrong here.
Reject: already enforced by config, lint, or types; already documented anywhere a session can read, skills included; subsumed by a general rule; generic best practice; a transcript of today.
Resolve every pointer to a real `path` or `path:line`.

## Route

Glob for the actual layout first.
The test is who executes the rule.
An imperative rule aimed at the AI goes to the nearest enclosing `CLAUDE.md`; a procedure a human performs (setup, auth flows, running things) to the nearest `README.md`, even when the AI discovered it, because the model cannot perform it.
A coding convention routes by when it must hold: a rule every implementer must hold, because getting it wrong first costs more than a refactor, goes to `CLAUDE.md` as one line, and a convention applied afterwards goes to the matching `docs/standards/` file, which is read when code is judged rather than while it is written.
A stack-imposed styling convention goes to `docs/standards/frontend-styling.md`, and a universal usability floor to `docs/standards/ux-standards.md`, with its source.
A choice another project could make differently (palette, type, density, voice) goes to `BRANDING.md`.
A nested `CLAUDE.md` or a `paths:` rules file loads only when a matching file is read, so a rule that must hold during `Write` and Bash writes takes a guaranteed placement or is named from one.
A collaboration preference is the user's, offered for `~/.claude/CLAUDE.md`; a personal uncommitted preference goes to `CLAUDE.local.md`.

## Draft

Imperative, present tense, absolutes with exceptions at point of use; no "prefer", "try to", "going forward".
State the action and its concrete check, not the ban; grant permission to say "unknown" where a rule meets uncertainty.
Front-load the constraint, the why only when non-obvious.
Scope surfaces a rule could bleed across.
Cite a living example by path rather than pasting code.
Match the target file's tone; one sentence per line.
Reaching for ALWAYS/NEVER usually means the why is missing.
Maintainer notes ride free in HTML comments, which Claude Code strips before injecting a `CLAUDE.md`; the why that lets the model generalize stays in loaded text.

## Present, then apply

State the exact text, target file and heading, and net line count; strengthen an existing line before appending a sibling; name rejected candidates with their ground.
An edit to `BRANDING.md`'s identity sections first reports its blast radius: the call sites and surfaces a grep of the token finds, or that the grep could not run.
Insert approved text under its heading; a near-duplicate strengthens the existing bullet, a contradiction halts for the user to pick the survivor, and a decayed target file is flagged for its own restatement pass.
Reread the edit as a session with no memory of today; a line that changes nothing it does gets cut.
