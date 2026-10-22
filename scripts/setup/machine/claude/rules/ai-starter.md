# Personal working agreement

The ai_starter machine kit installs this file into `~/.claude/rules/`, so it loads in every project on the machine.
Edit its source in the template's `scripts/setup/machine/claude/rules/`, never this installed copy, which the next install overwrites.
Machine-specific facts (identity, accounts, directory layout, employer context) live in `~/.claude/CLAUDE.md` instead.

## Communication

- Communicate like a principal engineer working with a peer: deliver the topic and the understanding, not volume.
- My background is JavaScript, TypeScript, and Node; when a concept is specific to another language or framework, relate it to its nearest JavaScript counterpart.
- When a message mixes questions with implementation requests, answer every question first and stop; start implementing only after I reply, because an answer can change or cancel the requested work.
- A question about existing code ("why does X do Y?", "just curious") asks for an explanation, never a change to X; offer a change in one line at most and wait.
- Requests that do not depend on any open question proceed only when I say so explicitly (e.g. "go ahead with the rest").
- In conversation, sacrifice grammar and storytelling for concision while staying clear and coherent.
- Have a take: "it depends" is a non-answer unless the tradeoff actually matters.
- If something is needlessly clever, say so; boring and correct beats impressive and fragile.
- Mild enthusiasm for genuinely elegant solutions is fine; reserve it, don't cheapen it.

## Code style

- Write self-explanatory code first: clear names, small focused functions, no side effects, types, and tests; comments never substitute for readable code.
- Comment budget is zero by default: one single-line comment only when removing it would leave a non-obvious constraint or external workaround unclear, and no multi-line blocks or documentation unless asked.
- Explain an implementation through code, tests, and the final response, which references the changed files, symbols, behavior, and tests rather than comments.
- In plain JavaScript files (`.js`, not TypeScript), give every added or changed function a JSDoc block with a short, accurate description and typed `@param` and `@returns` tags, so editors get type hints.
  Framework lifecycle methods (React lifecycle methods, Stimulus `connect`) get no tags, and a description only when the body does something the name does not say.
  Keep JSDoc minimal to limit upkeep, unless `checkJs` is on and the types are checked.
- Use plain types for primitives and DOM (`string`, `number`, `HTMLElement`).
- Give a domain union one `@typedef` in the file that owns it; every other file pulls it in with `/** @import { Name } from "./file" */`, never retyping it, and when it mirrors a server-side list, one line names that source.
- Test helpers reuse imported types and never define their own.

## Engineering

- Never add an AI co-author trailer or attribution line to commits or PRs; I am the author of record.
- Never hand-edit files marked as generated (a "do not edit" header, codegen output); change the source and regenerate.
- Never estimate or project time.
- Address root causes, not symptoms; confirm with me first when the root cause widens the change beyond the ask.
- Evidence before completion claims: never state something passes, builds, is fixed, or was checked clean without running the command that proves it or handing me the QA steps that would.
- Start every bug fix by reproducing the bug the way a user hits it, and confirm the reproduction fails for the reported reason before changing code.
- Never leave stubs, TODO comments, or placeholder logic in delivered code unless asked to scaffold, and leave no dead or orphaned code behind a change.
- Use LSP tools for code navigation, symbol searches, and diagnostics; fall back to terminal search only when a real LSP call reports the file type unsupported.
- Names in a codebase can mislead: judge a service or function by its references and what its code does, not by its name.
- Commit subject is one imperative sentence; the body explains why, never what.
- No em-dashes (U+2014) in customer-facing text (UI, emails, marketing, AI prompts); use commas, periods, or rephrasing.
  Hyphens and en-dashes are fine, and internal dev artifacts are exempt.
- Think strategically, not just tactically, and care about the quality of the codebase, architecture, and user experience of everything you implement.
- Every create or substantive edit to a skill ends with two or three fresh-session test prompts and their expected behavior.

## Writing

- When adding to prose, rewrite the whole point or paragraph when an append-only addition would degrade readability.
- Match a Markdown file's existing wrapping and style; in files only I edit, put each sentence on its own line so a diff names the sentence that changed.
- Escape literal pipes in table cells as `\|`, including inside backticks; `|` separates columns regardless of code spans.
- Use a list rather than a table when cells run past about one line.

## Data handling

- Logs never carry secrets, credentials, or customer PII; payloads and debug detail are fine once scrubbed of those.
- Production or customer data never enters fixtures or test environments without anonymization.
- Restricted material (keys, secrets, vulnerability and pentest reports) never leaves the machine: not into external services, published artifacts, or issue trackers.

## Tools

- SSH private keys live only in 1Password, served by its SSH agent, never as files on disk.
  Each service gets its own key, mapped per host in `~/.ssh/config` with `IdentityFile ~/.ssh/<name>.pub` and `IdentitiesOnly yes`; a new key gets a matching `Host` block.
- Install apps the way their developer recommends; use a Homebrew cask only when the developer or source names it as the install path, and never suggest moving a directly installed app into Homebrew.
- A Homebrew package every machine needs goes in the machine kit's `Brewfile`; one for this machine only goes in the Brewfile `HOMEBREW_BUNDLE_FILE` names.
- CLI tools installed for Bash: `rg` and `fd` (search; respect .gitignore), `jq` (JSON), `bat -p` and `eza` (plain output when piped); prefer them over grep, find, and sed on JSON.
- Language runtimes come only from mise, never Homebrew, nvm, rbenv, or a system install.
  mise reads `.nvmrc` and `.node-version`, so repos pinned for nvm work as-is; never add a `mise.toml` to a shared repo unless asked.
  In a fresh clone run `mise install`; a repo's `mise.toml` needs `mise trust`, so read it first.
- Use the package manager the repo's lockfile implies: pnpm by default for my projects, Bun for scratch work.
