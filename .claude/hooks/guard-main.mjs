#!/usr/bin/env node
// PreToolUse guard: blocks Claude from running `git commit` on the repo's default
// branch, from pushing while on it (publishing a tag excepted, so the release
// process stays reachable), and from pushing onto it from any branch. The hook
// runs before the command does, so git subcommands are walked in order and
// branch switches and tag creates or deletes earlier in the same command update
// the state later subcommands are judged against: `git checkout -b feat && git
// commit` commits on feat, not on main. Exit 2 blocks the tool call and surfaces
// stderr to Claude; exit 0 allows it. If the hook itself fails to launch (node
// missing, bad $CLAUDE_PROJECT_DIR), Claude Code treats the non-0/non-2 exit as
// a non-blocking error and the command proceeds: fail-open by design, because a
// launch failure that blocked every Bash call would cost more than the missed
// guard, and server-side branch protection covers pushes for every author.
import { readFileSync } from "node:fs";
import { execFileSync } from "node:child_process";

let input;
try {
  input = JSON.parse(readFileSync(0, "utf8"));
} catch {
  process.exit(0);
}

const command = input.tool_input?.command ?? "";
if (!command.includes("git")) process.exit(0);

// Blank quoted spans in one quote-aware pass: content inside quotes is data
// (commit messages, grep patterns) and may hide separators. An unterminated
// quote (a comment line with an apostrophe ahead of the git command) re-scans
// its tail as unquoted text, failing toward inspection. Escaped quotes are not
// modeled; this is a guardrail against honest mistakes, not a shell parser.
function blankQuotes(cmd) {
  let out = "";
  let quote = null;
  let openIndex = -1;
  for (let i = 0; i < cmd.length; i++) {
    const ch = cmd[i];
    if (quote) {
      if (ch === quote) quote = null;
      continue;
    }
    if (ch === "'" || ch === '"') {
      quote = ch;
      openIndex = i;
      continue;
    }
    out += ch;
  }
  if (quote !== null) out += blankQuotes(cmd.slice(openIndex + 1));
  return out;
}

// Newlines separate commands exactly like `;`, and one segment can invoke git
// more than once, so every token is scanned. Global flags with values are
// skipped so `git -C sub commit` is still caught; leading `(`/`{` are stripped
// so a subshell-wrapped git is too.
const FLAGS_WITH_VALUE = new Set(["-C", "-c", "--git-dir", "--work-tree", "--namespace"]);
const subcommands = [];
for (const segment of blankQuotes(command).split(/&&|\|\||[;|\n\r]/)) {
  const tokens = segment.trim().split(/\s+/);
  for (let i = 0; i < tokens.length; i++) {
    const bare = tokens[i].replace(/^[({]+/, "");
    if (bare !== "git" && !bare.endsWith("/git")) continue;
    for (let j = i + 1; j < tokens.length; j++) {
      const token = tokens[j];
      if (token.startsWith("-")) {
        if (FLAGS_WITH_VALUE.has(token)) j++;
        continue;
      }
      subcommands.push({ name: token, args: effectiveArgs(tokens.slice(j + 1)) });
      i = j;
      break;
    }
  }
}

// Git forbids `<` and `>` in ref names, so a redirection (`2>&1`) and anything
// after it can never be a ref; pipes and `&&` are already segment separators.
function effectiveArgs(args) {
  const redirect = args.findIndex((token) => /[<>]/.test(token) || token === "&");
  return (redirect === -1 ? args : args.slice(0, redirect)).map((token) =>
    token.replace(/[)}]+$/, ""),
  );
}

if (!subcommands.some((s) => s.name === "commit" || s.name === "push")) process.exit(0);

const cwd = input.cwd || process.cwd();
const git = (args) =>
  execFileSync("git", args, {
    cwd,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "ignore"],
    timeout: 2000, // a hung git (stalled mount) must not hang the whole agent turn
  }).trim();
const refExists = (ref) => {
  try {
    git(["rev-parse", "--verify", "--quiet", ref]);
    return true;
  } catch {
    return false;
  }
};

let current;
try {
  current = git(["branch", "--show-current"]);
} catch {
  process.exit(0); // not a git repo (or git unavailable), nothing to guard
}

let defaultBranch = null;
try {
  defaultBranch = git(["symbolic-ref", "refs/remotes/origin/HEAD"]).split("/").pop() || null;
} catch {
  // no origin/HEAD ref (fresh repo, no remote): fall through to name matching
}
const isDefault = (name) =>
  defaultBranch ? name === defaultBranch : name === "main" || name === "master";

const positionalsOf = (args) => args.filter((token) => !token.startsWith("-"));
const valueAfter = (args, flags) => {
  const index = args.findIndex((token) => flags.includes(token));
  return index === -1 ? undefined : args[index + 1];
};

// `checkout <name>` counts as a switch only when <name> is a branch, since the
// same spelling restores a file; anything unrecognized leaves the branch as is.
function branchAfterSwitch({ name, args }, branch) {
  if (args.includes("--detach")) return "";
  if (name === "switch") {
    return (
      valueAfter(args, ["-c", "-C", "--create", "--force-create"]) ??
      positionalsOf(args)[0] ??
      branch
    );
  }
  if (args.includes("--")) return branch;
  const created = valueAfter(args, ["-b", "-B"]);
  if (created) return created;
  const target = positionalsOf(args)[0];
  if (target && (refExists(`refs/heads/${target}`) || refExists(`refs/remotes/origin/${target}`))) {
    return target;
  }
  return branch;
}

const createdTags = new Set();
const deletedTags = new Set();
function trackTag({ args }) {
  if (args.includes("-l") || args.includes("--list")) return;
  const names = positionalsOf(args);
  if (args.includes("-d") || args.includes("--delete")) {
    for (const tag of names) {
      deletedTags.add(tag);
      createdTags.delete(tag);
    }
  } else if (names.length > 0) {
    createdTags.add(names[0]);
    deletedTags.delete(names[0]);
  }
}

// Returns the default-branch name a push would write to or delete, else null.
// The first positional is the remote; each later one is a refspec whose
// destination is the part after `:`, or the whole ref when there is no colon.
function pushDestinationOnDefault(args) {
  for (const ref of positionalsOf(args).slice(1)) {
    const spec = ref.replace(/^\+/, "");
    const destination = (spec.includes(":") ? spec.split(":").pop() : spec).replace(
      /^refs\/heads\//,
      "",
    );
    if (isDefault(destination)) return destination;
  }
  return null;
}

// Publishing a release tag is the one push that belongs on the default branch:
// a tag ref moves no commits onto it. The exemption is deliberately narrow: each
// ref must be a tag that exists (or was created earlier in this command) and
// must not also name a branch, so an ambiguous or invented name falls through to
// the block. Anything that could move a branch or rewrite a published tag stays
// blocked.
const PUSH_ESCALATIONS = new Set([
  "--force",
  "-f",
  "--force-with-lease",
  "--force-if-includes",
  "--mirror",
  "--all",
  "--follow-tags",
  "--delete",
  "-d",
  "--prune",
]);

function isTagOnlyPush(args) {
  if (args.some((token) => PUSH_ESCALATIONS.has(token))) return false;
  const refs = positionalsOf(args).slice(1);
  if (refs.some((ref) => ref.includes(":"))) return false;
  if (refs.length === 0) return args.includes("--tags");
  return refs.every((ref) => {
    const name = ref.replace(/^refs\/tags\//, "");
    const tagExists =
      createdTags.has(name) || (!deletedTags.has(name) && refExists(`refs/tags/${name}`));
    return tagExists && !refExists(`refs/heads/${name}`);
  });
}

function block(message) {
  console.error(`Blocked by guard-main hook: ${message}`);
  process.exit(2);
}

let branch = current;
for (const sub of subcommands) {
  if (sub.name === "checkout" || sub.name === "switch") {
    branch = branchAfterSwitch(sub, branch);
  } else if (sub.name === "tag") {
    trackTag(sub);
  } else if (sub.name === "commit" && isDefault(branch)) {
    block(
      `\`git commit\` on ${branch}. CLAUDE.md: never commit to the default branch; create or switch to a feature branch (earlier in the same command works), or hand the commit to the user via stage-for-commit.`,
    );
  } else if (sub.name === "push") {
    const destination = pushDestinationOnDefault(sub.args);
    if (destination) {
      block(
        `\`git push\` writes to ${destination}, the default branch. Push the feature branch and open a PR instead.`,
      );
    }
    if (isDefault(branch) && !isTagOnlyPush(sub.args)) {
      block(
        `\`git push\` on ${branch}. Only publishing a tag (\`git push <remote> <tag>\` or \`--tags\`) is exempt here; switch to a feature branch first.`,
      );
    }
  }
}
process.exit(0);
