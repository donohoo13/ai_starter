---
applies-to:
  - "**/*.{ts,tsx,mts,cts,js,jsx,mjs,cjs}"
  - "**/package.json"
  - "**/tsconfig.json"
  - "**/pnpm-workspace.yaml"
  - "**/turbo.json"
  - ".nvmrc"
  - "mise.toml"
---

# JavaScript and TypeScript conventions

The pnpm and Node-pin rules every session must hold from the first command live in `CLAUDE.md`; these are the conventions a change is brought up to.

## Tooling

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
