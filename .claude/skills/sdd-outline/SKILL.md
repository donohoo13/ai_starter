---
name: sdd-outline
description: Turn an idea, brief, ticket or bug into an approved spec.md under docs/sdd/. Size the change, ground in the code, play the problem back for the user to confirm, interview in focused batches, run an adversarial review, then gate on the user's approval. Use when the user says "spec this out", "outline a feature", "write a spec", "start SDD", or brings a new feature idea. Phase 1 of spec-driven development, section 7 of .claude/sdd/spec-driven-development.md.
argument-hint: "[slug] [brief]"
allowed-tools: Bash(.claude/sdd/bin/sdd *)
---

# SDD Outline (phase 1)

Turn intent into an approved `spec.md`. The rules live in section 7 (Outline) of `.claude/sdd/spec-driven-development.md`; this file is only the procedure.
Where the two differ, the document wins.

Arguments: `$ARGUMENTS`.
The first token is the slug when it contains a hyphen or names an existing spec, one for which `.claude/sdd/bin/sdd status <token> --json` reports `artifacts.spec.exists` true or refuses because another worktree or branch holds it; otherwise the whole argument is the brief.

## Preconditions

- Section 3 (Sizing) sizes the change as medium or larger.
  Trivial: say so and recommend making the change directly, with `tdd` only if behavior changes.
  Small: recommend `tdd` as a one-shot, then `sdd-review` before the PR.
  Continue only if the user still wants the chain.
- If the spec already exists, this run revises or resumes it.
  Start over only when the user asks.

## Start (section 4 (The workflow), start protocol)

1. Read sections 1–5 of the document once per session, then section 7 (Outline).
2. Resolve the slug: the argument; else `.claude/sdd/bin/sdd find`; else, on a feature branch, the branch name in kebab-case (section 5 (Working files)); else list the folders `find` prints, with the specs it says other worktrees hold, and, when none fits, propose a short kebab-case slug and confirm it.
3. Run `.claude/sdd/bin/sdd status <slug> --json`.
   It reports `folder`, the spec folder's absolute path, and `mode`, `shared` or `private` (section 5 (Working files)).
   Read and write every spec file under `folder`, never at a path built by hand: in a private repository every worktree shares the main checkout's folder, so it can sit outside the current directory.
   When it refuses because the spec is in another worktree, or on a branch no worktree has checked out, the spec exists and this session started outside its worktree: make the worktree with the `.claude/sdd/bin/sdd worktree <branch>` the refusal names, when it names one, move into it as step 4 does, and run `status` again there.
   When a spec exists and `phase` is later than `1. Outline`, the spec is approved: ask whether the user wants to revise it (section 14 (Changing course)), warn that the design, plan and tasks built on it go stale, and continue only on yes.
4. Create the folder when it is missing, on the spec's own branch (section 5 (Working files), The branch and its worktree).
   On a feature branch of this work's own, run `.claude/sdd/bin/sdd init <slug>`, which records that branch.
   Anywhere else, on the base, on another shared branch that other work also merges into such as `main` or `staging`, or on a branch that belongs to other work, make the branch and its worktree before the spec, in a shared and a private repository alike: a shared repository commits the spec, which none of those branches can take, and in both the branch is how every later session finds the spec.
   1. Name the branch in the form the repository's context file states for branches, the `<type>/<kebab-slug>` convention in `CLAUDE.md`, or `feature/<slug>` where it states none.
   2. Run `.claude/sdd/bin/sdd worktree <branch>`, which prints the worktree's path and how the branch got there: cut from the base, tracking a branch the remote already had, on an existing local branch, or already checked out.
      Add `--base <name>` only when the user has said the work builds on another branch, and `--path <dir>` only when the context file says where worktrees live; without it the worktree lands under `.claude/worktrees/` in the main checkout.
      When it prints that git could not tell the base, ask the user and pass their answer as `--base <branch>`, here and to `init`.
   3. When the repository has `scripts/setup/gwt-add.sh`, run `scripts/setup/gwt-add.sh --no-open <branch>`, which adopts the worktree at that path, copies the local env and settings files into it and installs its dependencies.
      A failed install does not stop the outline, which needs no dependencies: tell the user what the script printed, since the build will need it fixed.
   4. Move the session into the worktree: with the `EnterWorktree` tool, pass the printed `path`; without that tool, as under Codex, run every later command with that directory as its working directory and read and write files by absolute path under it.
      Tell the user the branch and the path.
   5. Run `status` again there, since a branch that already existed may hold the spec, outlined in an earlier session or on another machine, and then this run resumes it.
      Otherwise run `.claude/sdd/bin/sdd init <slug>`.

   `init` also records the spec's base, the branch this work is cut from and merges back into, as the remote's default branch that git reports, so ask nothing about it; add `--base <name>` only when the user has said the work builds on another branch.
   When `init` prints that git could not tell, ask the user and record their answer: `.claude/sdd/bin/sdd set-base <slug> <branch>`.
   `init` prints the mode too, and in a private repository it makes git ignore the folder through the local exclude file before it writes the spec, so run nothing of your own to track or ignore it.
   Outside a git repository there is no branch to make, so run `init` where you are.

5. Load only what this phase needs: the project context (section 6 (Project principles and context)) and the existing spec, if any.

## Steps (section 7 (Outline), Steps)

1. **Ground yourself in the code.**
   Explore read-only.
   Delegate wide searches to Explore subagents and keep their conclusions.
   Before writing, name the files, interfaces and existing behavior involved.
   Establish why the problem happens, reading how each system involved behaves, its vendor's documentation included when it is third-party.
2. **Play back the problem** in the conversation as section 7 (Outline) Steps describes, then end your turn.
   Interview only after the user confirms or corrects the playback.
3. **Interview** when the brief is thin, with the AskUserQuestion tool, in batches of two to four related questions, the most load-bearing first, each with a recommended option listed first.
   Ask only what the code cannot tell you: edge cases, failure behavior, trade-offs, constraints, who the work is for, what success looks like.
   Keep options to behavior or hard constraints, and ask once per problem when the answer differs per problem.
   An assumption the user accepts goes under Assumptions with their name.
   Anything unresolved becomes `[NEEDS CLARIFICATION: <specific question>]`.
4. **Draft `spec.md`** in place, keeping the frontmatter `init` wrote.
   Follow section 7 (Outline) for the description, summary, requirements, scenarios, invariants and existing behavior.
   Delete every placeholder you do not fill, including the sample clarification line under Open questions, and drop the optional sections the sections table does not call for; lint reports every `<...>` placeholder left from the template as an error.
   List every screen, page, view, component or email template the change creates or edits under UI surfaces, as section 7 (Outline) describes, since the design offer at the finish and the later skills read that list; leave the section out when there is none.
   When revising an approved spec, add a dated entry under Changelog with the reason.
5. **Check it.**
   Run the spec readiness checklist from section 7 (Outline) and `.claude/sdd/bin/sdd lint <slug> spec`.
   Fix every error; answer every warning with a number or a rewrite.
6. **Adversarial review.**
   Dispatch a general-purpose subagent with the prompt in [references/adversarial-review.md](references/adversarial-review.md), its three placeholders filled in: the spec's absolute path under `folder`, the project context paths, and the repository root.
   Turn each finding into a fix or a clarification marker, then lint again.
7. **Interview again** for the markers the review raised, then clear them.

## Outputs

- `spec.md` in the spec folder, with status `approved` and `approved_hash` recorded by the helper.

## Finish (section 4 (The workflow), finish protocol)

1. Exit checks: `.claude/sdd/bin/sdd lint <slug> spec` reports 0 errors, no marker remains, the readiness checklist passes.
2. Present the spec, the decisions it records, the assumptions and any open question.
   Ask for approval.
3. Only after the user approves in the conversation, run `.claude/sdd/bin/sdd approve <slug> spec`.
   Never approve on their behalf.
   Then, when `mode` is `shared`, stage `<folder>/spec.md` by explicit path and propose a commit message in the repo's convention; the user commits.
   When this session moved into a worktree, give the commit as `git -C <worktree> commit -m "<message>"`, since the user's own shell may sit in another checkout.
   When it is `private`, stage nothing and propose no commit, and never force a spec file in with `git add -f`: git ignores the folder so that it stays out of the repository, and the file alone records the approval.
4. Name the next skill, and the worktree to run it in when the spec has one.
   When `design.md` exists, offer no skip and name the skill `sdd status` reports: `sdd-design` at `2. Design` for a requested or approved design, which it re-checks against the revised spec, or for a skip that misses a surface the spec now lists.
   When `design.md` is absent and the UI surfaces section lists a surface, name each listed surface and offer `sdd-design` for a Claude Design mockup before planning, with `sdd-plan` as the alternative.
   When the user skips the design, run `.claude/sdd/bin/sdd set-status <slug> design skipped`, which records their git `user.name`, the date and the surfaces the skip covers; write their reason under `design.md`'s Skip reason and "None" under every other section, then, only when `mode` is `shared`, stage `<folder>/design.md` by explicit path and propose a commit message.
   Record a skip only on the user's word, never by default.
   When the spec lists no UI surface, name `sdd-plan` only and write no `design.md`.
   Do not start the next skill unless the user said to run end to end.

## Next

`sdd-design` when `sdd status` reports `2. Design`, or the spec lists a UI surface and the user wants a design, otherwise `sdd-plan`, with the spec folder as the handoff.
