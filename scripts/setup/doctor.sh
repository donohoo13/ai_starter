#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/setup/doctor.sh
# Warn-only check that this machine has the toolchain prerequisites the project
# expects. Claude Code's LSP plugins (typescript-lsp, pyright-lsp) ship only
# server configuration; each language server binary is a separate per-machine
# install, and when it is missing LSP code intelligence silently degrades to
# text search. Wire this into package.json "prepare" so every `pnpm install`
# self-reports gaps. It informs, never blocks: always exits 0.

have() { command -v "$1" >/dev/null 2>&1; }
warn() {
  printf '! %s\n  fix: %s\n' "$1" "$2" >&2
}

# Node pin drift. npm enforces package.json devEngines against the running
# Node for any npx/npm invocation with this project as cwd and treats onFail
# "download" as an error, so a shell whose ambient Node differs from the pin
# loses every npx-launched tool here — including Claude Code plugin MCP
# servers, which fail with an opaque -32000. pnpm-routed commands are immune
# (pnpm downloads the pinned runtime); this warning exists to name the cause.
# The probe has two paths. Under a package-manager lifecycle (pnpm "prepare"
# sets npm_config_user_agent and puts the provisioned pinned runtime first on
# PATH) bare `node` can only ever see the pin, so the developer's shell is
# asked instead — interactive rc first, because version managers commonly
# init there, and the login shell only as fallback (measured here: the login
# PATH resolved a different, non-manager Node than interactive shells see).
# Both probes are non-fatal by design: a broken shim (asdf/mise with no
# version selected) degrades to no drift warning, never a dead script, so
# the LSP checks below always still run and the exit-0 contract holds.
if [[ -f .nvmrc ]]; then
  pinned=$(tr -d 'v[:space:]' <.nvmrc)
  ambient=""
  if [[ -n "${npm_config_user_agent:-}" && -n "${SHELL:-}" ]]; then
    ambient=$("$SHELL" -ic 'node --version' 2>/dev/null | grep '^v[0-9]' | tail -n 1 || true)
    if [[ -z "$ambient" ]]; then
      ambient=$("$SHELL" -lc 'node --version' 2>/dev/null | grep '^v[0-9]' | tail -n 1 || true)
    fi
  elif have node; then
    ambient=$(node --version 2>/dev/null || true)
  fi
  if [[ -n "$ambient" && "${ambient#v}" != "$pinned" ]]; then
    warn \
      "shell Node is $ambient but the project pins $pinned: npx run from this project fails the devEngines check (EBADDEVENGINES), which also kills npx-launched Claude Code plugin MCP servers" \
      "mise install (or nvm install $pinned && nvm use $pinned), then relaunch this shell (and Claude Code, if running) so PATH picks it up"
  fi
fi

# TypeScript / JavaScript
if [[ -f package.json || -f tsconfig.json ]]; then
  have typescript-language-server || warn \
    "typescript-language-server not found: LSP code intelligence for TS/JS is inactive" \
    "npm i -g typescript-language-server typescript"
fi

# Python
if [[ -f pyproject.toml || -f requirements.txt || -f uv.lock ]]; then
  have pyright-langserver || warn \
    "pyright-langserver not found: LSP code intelligence for Python is inactive" \
    "npm i -g pyright"
fi

# Adopting another language? Three steps: enable its plugin in
# .claude/settings.json enabledPlugins, install its binary, add a block above
# gated on its manifest. Official plugins -> binary (detect via manifest):
#   gopls-lsp -> gopls (go.mod)                    go install golang.org/x/tools/gopls@latest
#   rust-analyzer-lsp -> rust-analyzer (Cargo.toml)  rustup component add rust-analyzer
#   ruby-lsp -> ruby-lsp (Gemfile)                 gem install ruby-lsp
#   jdtls-lsp -> jdtls (pom.xml, build.gradle)
#   csharp-lsp -> csharp-ls (*.csproj)
#   clangd-lsp, kotlin-lsp, lua-lsp, php-lsp, swift-lsp also exist in the
#   claude-plugins-official marketplace.

exit 0
