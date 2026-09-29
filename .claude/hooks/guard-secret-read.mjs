#!/usr/bin/env node
// PreToolUse guard: blocks Bash commands that reference secret-registered
// files. The paired Read(...) and Edit(...) globs in .claude/settings.json
// permissions.deny are the registry, and both spellings are load-bearing:
// Read(...) covers Read/Grep/Glob/@file and the recognized shell readers
// (cat, head, tail, sed) plus the Edit tool's own read-deny check, while
// Edit(...) is what covers the writing tools — Edit, Write, MultiEdit, and
// NotebookEdit — because a Read deny does not reach them and a Write(...)
// rule is accepted but never consulted. Registering a path under Read alone
// leaves it writable. This hook parses the Read(...) entries and extends
// that half of the registry to everything else Bash
// can do with a file: source, interpreter one-liners, base64, cp/mv
// relocation, git add. Every verb is blocked, not just readers, because
// relocation turns a denied read into an allowed one and staging a secret
// file is its own accident class. Matching is token-based — split the
// command on shell metacharacters, test the surviving tokens against the
// globs — so a quoted mention (a commit message naming .env) also denies:
// over-blocking is the safe failure for a guardrail against accidents; this
// is not an access control, same posture as the sibling guards. Fail-open:
// unreadable settings or bad input must not lock Bash shut. Exit 2 blocks
// the tool call and surfaces stderr to Claude; exit 0 allows.
import { readFileSync } from "node:fs";
import { join } from "node:path";

let input;
try {
  input = JSON.parse(readFileSync(0, "utf8"));
} catch {
  process.exit(0);
}

if (input.tool_name !== "Bash") process.exit(0);
const command = input.tool_input?.command ?? "";
if (!command) process.exit(0);

const projectDir = process.env.CLAUDE_PROJECT_DIR || input.cwd || process.cwd();

// {a,b} alternatives multiply out before glob conversion; the deny grammar
// nests no braces, so one level recursed suffices.
function expandBraces(pattern) {
  const m = pattern.match(/^(.*?)\{([^}]*)\}(.*)$/);
  if (!m) return [pattern];
  return m[2].split(",").flatMap((alt) => expandBraces(m[1] + alt + m[3]));
}

// Convert one deny glob to a whole-token RegExp. Anchors (`//` absolute,
// `~/`, `./`) are stripped rather than honored: tokens match on their path
// tail, so `//**/.ssh/**` catches ~/.ssh/id_rsa, /home/x/.ssh/config, and a
// relative .ssh/key alike — cross-anchor over-blocking is deliberate. `**/`
// matches any depth including none; `*` and `?` stay within one segment.
function globToRegExp(glob) {
  const g = glob.replace(/^\/\//, "").replace(/^~\//, "").replace(/^\.\//, "");
  let re = "";
  let i = 0;
  while (i < g.length) {
    if (g.startsWith("**/", i)) {
      re += "(?:.*/)?";
      i += 3;
    } else if (g.startsWith("**", i)) {
      re += ".*";
      i += 2;
    } else if (g[i] === "*") {
      re += "[^/]*";
      i += 1;
    } else if (g[i] === "?") {
      re += "[^/]";
      i += 1;
    } else {
      re += g[i].replace(/[.+^${}()|[\]\\]/g, "\\$&");
      i += 1;
    }
  }
  return new RegExp("^" + re + "$");
}

const rules = [];
for (const file of ["settings.json", "settings.local.json"]) {
  let deny;
  try {
    deny = JSON.parse(readFileSync(join(projectDir, ".claude", file), "utf8")).permissions?.deny;
  } catch {
    continue; // fail-open per file
  }
  for (const entry of deny ?? []) {
    const m = /^Read\((.+)\)$/.exec(entry);
    if (!m) continue;
    for (const glob of expandBraces(m[1])) {
      rules.push({ glob, re: globToRegExp(glob) });
    }
  }
}
if (rules.length === 0) process.exit(0);

// The metacharacter split covers quoting, substitution, redirection, and
// --flag=value spellings; each surviving token is tested whole so path
// structure is preserved.
const tokens = command.split(/[\s;|&<>()`"'=,]+/).filter(Boolean);
for (const token of tokens) {
  for (const rule of rules) {
    if (rule.re.test(token)) {
      console.error(
        `Blocked by guard-secret-read hook: "${token}" matches secret-registered pattern Read(${rule.glob}) in .claude/settings.json permissions.deny — secret-bearing files are gated against accidental access. Per CLAUDE.md: name the secret and its file, then hand the user a ready-to-run command that references it inline (e.g. FOO="$(grep '^FOO=' <file> | cut -d= -f2-)" <cmd>) for their own terminal; never print the value or ask them to paste it into chat. A false positive — a command that only names a registered file without touching it — is rephrased so no registered spelling appears as a token, or handed to the user; never worked around with a file that opens the path.`,
      );
      process.exit(2);
    }
  }
}
process.exit(0);
