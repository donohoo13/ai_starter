---
name: render-check
description: Checks how the surfaces a branch touched actually render, by dispatching the render-checker agent against the running app at mobile and desktop widths in every shipped theme, then reports pass or fail per surface with evidence. User-only, run as /render-check when the user decides a surface needs a look, because a pass is slow and token-heavy.
argument-hint: "[surfaces] [--base <ref>]"
disable-model-invocation: true
---

# Render check

A render pass drives a browser through every state of every touched surface, at two widths, in every theme, so it costs minutes and many tokens.
It runs only when the user asks for it, and never from another skill.
This session finds the scope, owns the app server, and reports; the `render-checker` agent drives the browser in its own context, so the screenshots never fill this one.
It reports and never fixes: a failure goes back to the user, who routes it to a build or a review.

Arguments: `$ARGUMENTS`, optional surfaces to check and an optional `--base <ref>`.

## Discover

1. **Base.**
   The merge-base of `HEAD` with the `--base` ref when the argument names one, otherwise with `origin/<default>`, the default from `origin/HEAD`, else `git ls-remote --symref origin HEAD`, else a local `main` or `master`.
   A branch stacked on another feature branch needs that branch as `--base`, since nothing detects a stack on its own.
   A `--base` that does not resolve is reported in one line and ends the run.
2. **Surfaces**, from the first source that yields any:
   - The surfaces the argument names.
   - The changed paths since the base, committed or not, that match the `applies-to:` globs of `docs/standards/ux-standards.md`, mapped to the screens that render them.
   - A `docs/sdd/<slug>/spec.md` the change touches whose user scenarios or requirements name a surface.

   No surface found: say so in one line and end.

3. **States** for each surface: the ones the spec's scenarios and acceptance criteria name when there is a spec, otherwise the ones the changed code renders, such as empty, loading, error and populated.
4. **Themes**: every theme the app ships, from `DESIGN.md` and the app's theme styles.
5. **Bar**: the spec's requirements when there is a spec, `DESIGN.md`, and the `docs/standards/ux-standards.md` floors measured on the rendered page.

Announce the scope in one line, "Checking N surfaces since <base>", naming the base ref and the merge-base's short sha, before launching anything, so the user can stop a wrong read.

## App

- Start the app in this checkout: a `run-*` project skill under `.claude/skills/` when one exists, otherwise the repo's dev command as a background task.
- Read its log for readiness and the real URL.
  When a server is already running, reuse it rather than starting a second one.
- When the app fails to start, report the cause once and end; there is nothing to check.

## Check

Dispatch `render-checker` through the Agent tool with the URL, the surfaces and the states to reach, the themes, and the bar, then wait for its report.
When the report has not arrived, end the turn and resume from it when it does.

## Report

- One line with the overall verdict.
- Pass or fail per surface, width and theme, and for each failure the requirement it breaks, its evidence and the element, as the checker returned them.
- Each surface or state the checker could not reach, and why.
- Where the screenshots were saved.

Then stop every process this session started, and leave a server it reused running.
