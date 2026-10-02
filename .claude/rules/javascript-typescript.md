---
paths:
  - "**/*.{ts,tsx,mts,cts,js,jsx,mjs,cjs}"
  - "**/package.json"
  - "**/tsconfig.json"
  - "**/pnpm-workspace.yaml"
  - "**/turbo.json"
  - ".nvmrc"
  - "mise.toml"
---

# JavaScript, TypeScript, and Node conventions

Loads when a session reads a file matching the globs above, which covers every `Edit` because that tool requires a prior read of the file. Two routes reach a matching path without triggering the load: a `Write` creating a new file, which carries no read precondition, and any Bash write (`sed -i`, a `cat >` heredoc, a formatter run in place), which the load mechanism does not observe. `CLAUDE.md` names this file directly so both routes have somewhere to read it from.

## Toolchain

- Use `pnpm` as the package manager; in monorepos its workspace support (`pnpm-workspace.yaml`) beats npm/yarn.
- Run local package bins through `pnpm exec` and one-off remote tools through `pnpm dlx`, never `npx`; installs are pnpm-only, enforced with the Node-major pin by the `preinstall` guard (`scripts/setup/check-install.mjs`). AI sessions are the stated exception: `Bash(pnpm dlx*)` and `Bash(npx*)` are deny-listed, so a session needing a one-off remote tool hands the user a ready-to-run `pnpm dlx` command for their own terminal.
- Retarget the Node pin as a set, never a file: `.nvmrc` (exact version, read by the guard, by mise through `mise.toml` locally and in CI, and by nvm/fnm, never by pnpm itself), `engines.node` (`>=X.Y.Z <X+1`), and `devEngines.runtime.version` (the same exact version, never a range) change together.
  - Then `pnpm install` and commit the regenerated `pnpm-lock.yaml`; `scripts/setup/check-install.mjs` fails the install on drift between the first three.
  - The script's header comment carries the mechanism and the causal reasoning behind each choice, so read that header before changing how the pin works rather than rediscovering why a range or `useNodeVersion` fails.
- Run one-off Node commands through `pnpm exec node`, never bare `node`, so they execute on the version pinned in `devEngines.runtime` instead of the shell's ambient Node; `pnpm run` scripts already run under the pinned runtime on pnpm 11, and bare `node` is reserved for when the ambient version is deliberately wanted.
- pnpm honors the `packageManager` pin itself (pnpm 11 self-switches to it), and Corepack, bundled through Node 24 and removed from Node 25+, is a second way to activate that pin; the README quickstart installs pnpm directly rather than depending on Corepack. Retargeting the Node major to 25 or newer is the trigger to migrate any Corepack-based activation in the same change: a contributor or CI step relying on `corepack enable` loses it there, so move to a direct pnpm install or pnpm's native package-manager management.
- Use ESLint for code quality and bug detection, Prettier for formatting. Configure them to work together without conflicts.
- In monorepos, use `Turborepo` for build orchestration (caching, task pipelines, parallel execution); `package.json` scripts route through the `turbo` CLI (`turbo build`, `turbo lint`).

## Types

- Enable TypeScript `strict: true` in `tsconfig.json`. Define explicit interfaces/types for all data structures, API payloads, and function parameters; type genuinely-unknown data as `unknown` and narrow it — `any` never ships.
- Validate function/API arguments upfront using a library like Zod. Fail fast instead of letting bad data propagate.

## Language

- Use `async/await` with `try/catch` for error handling. Never use callbacks for async operations.
- Always use `===` for equality checks. Never use `==` — it coerces types and causes unexpected results.
- Never nest ternary expressions; a ternary's branches must not themselves be ternaries. Use early-return guards, an `if`/`else if` chain, or a lookup map/`switch` when there are more than two outcomes. A single-level ternary for one binary choice is fine.
- Use `const` by default. Use `let` only when reassignment is needed (e.g., loops). Never use `var`.
- Import/require modules at the top of the file, outside of functions. This avoids blocking requests and catches errors early.
- Always throw `Error` objects (or classes extending `Error`), never strings. Add useful properties like `code` to custom errors.
- Register `process.on('unhandledRejection')` to catch unhandled promise rejections — errors that would otherwise be swallowed.
- Name all functions, including callbacks and closures. Anonymous functions make debugging and profiling harder.
