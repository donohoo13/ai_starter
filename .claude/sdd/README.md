# Spec-driven development: the shared home

This folder holds the SDD document, the helper that keeps its state, the helper's tests, and the templates generated from the document.
The five `sdd-*` skills under `.claude/skills/` read from it by repository-relative path, so every command here runs from the repository root.

## What is here

- `spec-driven-development.md`: the SDD document, the single source of truth.
  The skills point into it by section number and title and never restate its rules.
  Section 4 (The workflow) defines the state machine and the start and finish protocols; section 5 (Working files) defines the files under `docs/sdd/`; sections 7 to 12 define each phase.
- `templates/`: `spec.md`, `plan.md`, `tasks.md` and `review.md`, generated from the document's appendices by `.claude/sdd/bin/sdd templates sync`.
  Never edit them by hand; edit the appendix and sync.
  Prettier skips the folder so the files stay byte-identical to the appendices.
- `bin/sdd`: the helper CLI, Python 3 standard library only, run directly as a script.
  It keeps state and runs mechanical checks so the skills do not track them by hand; it checks structure and state, not quality.
  It has no dependencies and no project environment, so `uv` has nothing to manage for it.
- `tests/`: the helper's `unittest` suite, run against throwaway git repos and a temp copy of this folder selected through the `SDD_HOME` environment variable.
  `scripts/test/sdd-helper.battery.mjs` runs it under `pnpm test:scripts`, with the template and reference checks below.

The skills live beside this folder:

| Skill           | Phase                      | Section | Produces                                                                |
| --------------- | -------------------------- | ------- | ----------------------------------------------------------------------- |
| `sdd-outline`   | 1. Outline                 | 7       | `spec.md`                                                               |
| `sdd-plan`      | 2. Plan                    | 8       | `plan.md`                                                               |
| `sdd-task`      | 3. Tasks                   | 9       | `tasks.md`                                                              |
| `sdd-implement` | 4. Implement               | 10      | code, tests, commits; `tasks.md` at `done`                              |
| `tdd`           | used by 4 and 5, and alone | 11      | tests and code, red then green                                          |
| `sdd-review`    | 5. Validate                | 12      | `review.md` and a PR description draft, or a chat report without a spec |

`tdd` knows nothing about SDD; `sdd-implement` and `sdd-review` hand it one behavior at a time.
The `standards-reviewer` and `research-analyst` agents in `.claude/agents/` are dispatched by `sdd-review` and `sdd-plan`.

## How to start

- A feature worth a spec: run `/sdd-outline <slug> <brief>`.
  Each phase ends by naming the next skill; you run it when you are ready, in a fresh session before `sdd-implement`.
- A small change: `/tdd <what to build>` as a one-shot, then `/sdd-review` before the PR.
- Where am I: `.claude/sdd/bin/sdd status` prints each artifact's state, the task progress, the phase and the skill to run.

Working files live in `docs/sdd/<slug>/` and are tracked by git.
Each skill stages the artifact it approved by explicit path and proposes a commit message; you commit, so the branch records when each gate passed.
The folder stays after the merge as the record of the change.

## The helper

```
sdd root                                   project root and its docs/sdd/ path
sdd init <slug> [--branch <name>]          create spec.md from the template
sdd find                                   the slug whose spec branch is the current branch
sdd status [slug] [--json]                 artifact states, task progress, phase, next skill
sdd hash <file>                            content hash of the body below the frontmatter
sdd lint <slug> [spec|plan|tasks|review]   structure, traceability and unfilled template placeholders; no artifact means every one present
sdd approve <slug> <spec|plan|tasks>       record the user's approval (only after they give it); refused on lint errors
sdd set-status <slug> <tasks|review> <status>  tasks to in-progress or done; review to accepted, refused while review lint has errors
sdd templates sync [--check]               regenerate templates from Appendix A (Spec template) to Appendix D (Review report template)
sdd check-refs                             every section reference in the skills and this README matches a heading
```

The content hash ignores frontmatter, checkbox ticks, `- Evidence:` sub-bullets, the `## Follow-ups` section and trailing whitespace, so progress notes never count as a change to an approved artifact.
The `## Verified elsewhere` section of `tasks.md`, where the user records an `NFR-` or `INV-` verified without a task, sits inside the hash, so that decision cannot change after approval unnoticed.
`based_on` is recorded at approval; while an artifact is a draft, lint accepts it empty.

Lint treats every `<...>` token that appears in an artifact's template as an unfilled placeholder, so a raw template never passes.
`sdd-review` therefore writes the PR description draft into `review.md` before it runs `set-status`, since acceptance is refused while the draft's placeholders remain.

## How to update

1. Edit `spec-driven-development.md`.
   It is the only place rules live.
2. Run `.claude/sdd/bin/sdd templates sync` when an appendix changed, then `templates sync --check`.
3. Run `.claude/sdd/bin/sdd check-refs` so every section reference in the six skills and this README still matches a heading.
4. Run the tests: `python3 -m unittest discover -s .claude/sdd/tests`, or `pnpm test:scripts` for the whole battery.
5. Adjust a skill only when its procedure changed, never to restate a rule.
   If a skill needs something the document does not say, change the document first.

Repo-specific test knowledge is not stored here: `tdd` discovers it from the repository's own files through `.claude/skills/tdd/references/discover.md`.
