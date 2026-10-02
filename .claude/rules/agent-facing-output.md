---
paths:
  - "scripts/**"
  - ".claude/hooks/**"
---

# Agent-facing output

Scripts, hooks, and CLIs here are read by an agent more often than a person, and every line they print costs context on every call.
These floors are distilled from [AXI, the Agent eXperience Interface](https://axi.md/); `scripts/dev/node-dev-server.mjs` and `.claude/hooks/guard-main.mjs` are living examples.

- Every run ends in a definitive outcome line, including the empty and no-op cases ("0 matches", "already running (pid 4121)"), because silence reads as either success or a hang.
- A failure or block states what happened, why, and the exact next command, so the agent's next turn is the fix rather than an investigation.
- Never prompt interactively; flags and environment decide, and exit codes carry the result (0 success, non-zero failure, 2 for a hook block).
- Default output is a summary that leads with counts and status; full detail goes behind a flag or into a log file under `.logs/`, and truncated text states its full size and how to get the rest.
- Mutations are idempotent: a re-run that finds the work done exits 0 and says so.
