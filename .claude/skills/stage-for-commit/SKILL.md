---
name: stage-for-commit
description: Stage the files changed during this session by explicit path and hand back a ready-to-paste commit message, without committing, branching, or pushing. Use at the end of a quick chore, small feature, or bug fix that needed no spec (a theme color, a new column, a copy change) when the user wants to commit it themselves. Trigger on "stage my changes", "stage what you did", "I'll commit this myself", "ready to commit", "write me a commit message". Invoke only on the user's word, after they have confirmed the change works.
argument-hint: "(no args needed)"
---

# Stage for Commit

One job: stage this session's work and produce a commit message the user can paste. The user is the committer, so hand them staged changes and a message, then stop.

## Hard boundaries

- **Never commit.** No `git commit`, no `--amend`.
- **Never branch.** No `checkout -b`, `switch`, or `branch`; staying on the current branch is intended.
- **Never push** or touch the remote.
- **Never stage work that is not from this session.** A quick-task tree often carries unrelated dirty files, and `git add -A` is how they get swept in. Stage by explicit path only.

## Tree at invocation

Working tree (`git status --short`):

```!
git status --short | head -50
```

Staged index (`git diff --cached --name-only`):

```!
git diff --cached --name-only | head -50
```

Empty output means a clean tree or an empty index. Both snapshots are invocation-time; re-run the commands after changing any file.

## Process

1. **Build the explicit file list.** From the conversation, list every file you created, edited, or deleted this session, then reconcile it against the working-tree snapshot to catch renames and deletions. Anything dirty that you did not touch stays out. Anything already staged that you did not touch is another session's work in flight: leave it staged and flag it, because `git commit` takes the whole index. A file you touched that also carries hunks you do not recognize is a collision: flag it and let the user decide, since `git add` stages the whole file.
2. **Stage exactly those paths** with `git add -- <path1> <path2> ...`, which covers modifications, additions, and deletions alike.
3. **Prove what is staged** with `git diff --cached --stat` and fix the set before moving on if a touched file is missing or an extra one appeared. Nothing to stage means say so and stop; there is no message to write.
4. **Write the message.** Match the repo's convention (see recent `git log`): imperative subject of 50 characters or fewer, a conventional prefix (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`) when it sharpens intent. Add a body only when the why is not obvious from the subject, wrapped near 72 characters, explaining reasoning rather than restating the diff. No `Co-Authored-By` or AI attribution: the user is the author of record.
5. **Hand it back.** One line above the block summarizing what got staged (a file count is enough), plus one line when another session's files were already staged. Then the message as raw text in a single fenced block, and nothing after it.

```
chore: tidy board switcher tab styling

Tabs and button groups now route through the shared components so the
look cannot drift between surfaces.
```
