#!/usr/bin/env bash
set -euo pipefail

# Usage: scripts/setup/machine/install.sh
# Kit-owned files are overwritten on every run; a machine's own files only gain a missing line, so its local settings keep winning.

kit="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$kit/../../.." && pwd)"
log="$repo_root/.logs/machine-install.log"
config="$HOME/.config"
changes=0

fail() {
  printf '%s\n' "$1" >&2
  exit 1
}

report() {
  printf '%-6s %s\n' "$1" "$2"
}

home_relative() {
  printf '~%s' "${1#"$HOME"}"
}

run_logged() {
  local step="$1"
  shift
  "$@" >>"$log" 2>&1 || fail "$step failed running '$*'; full output in $log. Fix the cause, then re-run: $0"
}

install_owned() {
  local step="$1" source="$2" target="$3" verb="installed"
  if [[ -f "$target" ]] && cmp -s "$source" "$target"; then
    report "$step" "up to date $(home_relative "$target")"
    return
  fi
  [[ -f "$target" ]] && verb="updated"
  mkdir -p "$(dirname "$target")"
  cp "$source" "$target"
  changes=$((changes + 1))
  report "$step" "$verb $(home_relative "$target")"
}

seed_once() {
  local step="$1" source="$2" target="$3"
  if [[ -e "$target" ]]; then
    report "$step" "kept existing $(home_relative "$target")"
    return
  fi
  mkdir -p "$(dirname "$target")"
  cp "$source" "$target"
  changes=$((changes + 1))
  report "$step" "installed $(home_relative "$target")"
}

merge_lines() {
  local step="$1" target="$2" line added=0
  shift 2
  mkdir -p "$(dirname "$target")"
  touch "$target"
  for line in "$@"; do
    grep -qxF -- "$line" "$target" && continue
    [[ -s "$target" && -n "$(tail -c 1 "$target")" ]] && printf '\n' >>"$target"
    printf '%s\n' "$line" >>"$target"
    added=$((added + 1))
  done
  if [[ $added -eq 0 ]]; then
    report "$step" "up to date $(home_relative "$target")"
    return
  fi
  changes=$((changes + 1))
  report "$step" "added $added line(s) to $(home_relative "$target")"
}

install_brew() {
  run_logged brew brew bundle install --file="$kit/Brewfile"
  report brew "Brewfile satisfied"
}

install_mise() {
  install_owned mise "$kit/config/mise/conf.d/ai-starter.toml" "$config/mise/conf.d/ai-starter.toml"
  (cd "$HOME" && run_logged mise mise install)
  report mise "global tools installed"
}

install_git() {
  local ignore_lines=() line
  install_owned git "$kit/config/git/ai-starter.gitconfig" "$config/git/ai-starter.gitconfig"
  if git config --file "$config/git/config" --get-all include.path 2>/dev/null | grep -qxF ai-starter.gitconfig; then
    report git "up to date $(home_relative "$config/git/config")"
  else
    mkdir -p "$config/git"
    git config --file "$config/git/config" --add include.path ai-starter.gitconfig
    changes=$((changes + 1))
    report git "added include to $(home_relative "$config/git/config")"
  fi
  while IFS= read -r line; do
    ignore_lines+=("$line")
  done <"$kit/config/git/ignore"
  merge_lines git "$config/git/ignore" "${ignore_lines[@]}"
  if [[ -z "$(git config --global user.email || true)" ]]; then
    report git "no identity yet; set it: git config --global user.name \"Your Name\" && git config --global user.email you@example.com"
  fi
}

install_zsh() {
  install_owned zsh "$kit/config/zsh/ai-starter.zsh" "$config/zsh/ai-starter.zsh"
  merge_lines zsh "$HOME/.zshrc" 'source "$HOME/.config/zsh/ai-starter.zsh"'
}

install_zed() {
  seed_once zed "$kit/config/zed/settings.json" "$config/zed/settings.json"
  seed_once zed "$kit/config/zed/keymap.json" "$config/zed/keymap.json"
}

install_claude() {
  install_owned claude "$kit/claude/rules/ai-starter.md" "$HOME/.claude/rules/ai-starter.md"
}

install_chrome() {
  run_logged chrome "$kit/chrome-policies.sh"
  report chrome "policies applied; restart Chrome or reload chrome://policy"
}

[[ $# -eq 0 ]] || fail "usage: $0 (takes no arguments); nothing installed"
[[ "$(uname -s)" == "Darwin" ]] || fail "the machine kit is macOS-only and this is $(uname -s); nothing installed"
command -v brew >/dev/null 2>&1 || fail "Homebrew not found; nothing installed. Install it from https://brew.sh, open a new shell, then re-run: $0"

mkdir -p "$(dirname "$log")"
: >"$log"

install_brew
install_mise
install_git
install_zsh
install_zed
install_claude
install_chrome

if [[ $changes -eq 0 ]]; then
  echo "machine kit up to date: 0 files changed"
else
  echo "machine kit installed: $changes file(s) changed; open a new shell to load them"
fi
