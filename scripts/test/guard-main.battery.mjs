// Verification battery for the guard-main PreToolUse hook.
//
// Runs every case through the command string registered in
// .claude/settings.json (prefilter included) against a throwaway clone whose
// origin/HEAD names main, so default-branch detection, local branches, and tags
// are real git state rather than mocks. Cases run from two checkouts of the
// same clone: the main checkout (on main) and a worktree on a feature branch.
// Run: pnpm exec node scripts/test/guard-main.battery.mjs
import { execFileSync, spawnSync } from "node:child_process";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = join(here, "..", "..");

const settings = JSON.parse(readFileSync(join(repoRoot, ".claude", "settings.json"), "utf8"));
const registered = settings.hooks.PreToolUse.find((entry) => entry.matcher === "Bash")
  .hooks.map((hook) => hook.command)
  .find((cmd) => cmd.includes("guard-main"));
if (!registered) {
  console.error("FAIL guard-main is not registered under the Bash matcher in settings.json");
  process.exit(1);
}

const BLOCK = 2;
const ALLOW = 0;

const sandbox = mkdtempSync(join(tmpdir(), "guard-main-"));
const gitEnv = {
  ...process.env,
  GIT_CONFIG_NOSYSTEM: "1",
  GIT_CONFIG_GLOBAL: join(sandbox, "gitconfig"),
  GIT_AUTHOR_NAME: "t",
  GIT_AUTHOR_EMAIL: "t@t",
  GIT_COMMITTER_NAME: "t",
  GIT_COMMITTER_EMAIL: "t@t",
};
const git = (cwd, ...args) => execFileSync("git", args, { cwd, env: gitEnv, stdio: "pipe" });

const origin = join(sandbox, "origin.git");
const clone = join(sandbox, "clone");
const worktree = join(sandbox, "feature-wt");
writeFileSync(gitEnv.GIT_CONFIG_GLOBAL, "");
git(sandbox, "init", "-q", "--bare", "-b", "main", origin);
git(sandbox, "clone", "-q", origin, clone);
writeFileSync(join(clone, "file.txt"), "a\n");
git(clone, "add", "file.txt");
git(clone, "commit", "-q", "-m", "init");
git(clone, "push", "-q", "origin", "main");
git(clone, "remote", "set-head", "origin", "main");
git(clone, "tag", "v1.0.0");
git(clone, "branch", "feature/existing");
git(clone, "worktree", "add", "-q", worktree, "feature/existing");

const onMain = [
  // Reads and pulls never block
  { name: "pull named main", command: "git pull origin main", expect: ALLOW },
  { name: "checkout main then pull", command: "git checkout main && git pull", expect: ALLOW },
  { name: "log against main", command: "git log main..HEAD", expect: ALLOW },
  // Commits on main block in every spelling
  { name: "commit on main", command: 'git commit -m "x"', expect: BLOCK },
  { name: "commit with -C", command: "git -C . commit -m x", expect: BLOCK },
  { name: "subshell commit", command: "(git commit -m x)", expect: BLOCK },
  { name: "multiline commit", command: "git status\ngit commit -m x", expect: BLOCK },
  // Branching earlier in the same command moves the commit off main
  {
    name: "checkout -b then commit",
    command: "git checkout -b feature/x && git add . && git commit -m wip",
    expect: ALLOW,
  },
  {
    name: "switch -c then commit and push",
    command: "git switch -c feature/x && git commit -m x && git push -u origin feature/x",
    expect: ALLOW,
  },
  {
    name: "checkout existing branch then commit",
    command: "git checkout feature/existing && git commit -m x",
    expect: ALLOW,
  },
  {
    name: "branch away then back to main",
    command: "git checkout -b feature/x && git checkout main && git commit -m x",
    expect: BLOCK,
  },
  {
    name: "path checkout is not a branch switch",
    command: "git checkout -- file.txt && git commit -m x",
    expect: BLOCK,
  },
  {
    name: "checkout of a file name is not a branch switch",
    command: "git checkout file.txt && git commit -m x",
    expect: BLOCK,
  },
  // Pushes from main: only tag publishing is exempt
  { name: "bare push on main", command: "git push", expect: BLOCK },
  { name: "push main from main", command: "git push origin main", expect: BLOCK },
  { name: "push existing tag", command: "git push origin v1.0.0", expect: ALLOW },
  { name: "push tags flag", command: "git push origin --tags", expect: ALLOW },
  { name: "push tag piped", command: "git push origin v1.0.0 2>&1 | tail -3", expect: ALLOW },
  { name: "push unknown tag", command: "git push origin v9.9.9", expect: BLOCK },
  { name: "force push tag", command: "git push --force origin v1.0.0", expect: BLOCK },
  { name: "follow-tags push", command: "git push --follow-tags", expect: BLOCK },
  {
    name: "tag created then pushed in one command",
    command: 'git tag -a v9.9.9 -m "release" && git push origin v9.9.9',
    expect: ALLOW,
  },
  {
    name: "tag delete then push",
    command: "git tag -d v1.0.0 && git push origin v1.0.0",
    expect: BLOCK,
  },
];

const onFeature = [
  { name: "commit on feature", command: "git commit -m x", expect: ALLOW },
  {
    name: "push then PR against main",
    command:
      'git push -u origin feature/existing 2>&1 | tail -3 && gh pr create --base main --title "x"',
    expect: ALLOW,
  },
  {
    name: "rebase on main then force-with-lease",
    command: "git fetch origin main && git rebase origin/main && git push --force-with-lease",
    expect: ALLOW,
  },
  { name: "push local main by name", command: "git push origin main", expect: BLOCK },
  {
    name: "push refspec onto main",
    command: "git push origin feature/existing:main",
    expect: BLOCK,
  },
  {
    name: "push HEAD to refs/heads/main",
    command: "git push origin HEAD:refs/heads/main",
    expect: BLOCK,
  },
  { name: "force refspec main", command: "git push origin +main", expect: BLOCK },
  { name: "delete main by flag", command: "git push origin --delete main", expect: BLOCK },
  { name: "delete main by refspec", command: "git push origin :main", expect: BLOCK },
  {
    name: "switch to main then commit",
    command: "git switch main && git commit -m x",
    expect: BLOCK,
  },
];

function runPipeline(stdinText) {
  return spawnSync("bash", ["-c", registered], {
    input: stdinText,
    encoding: "utf8",
    timeout: 10_000,
    env: { ...gitEnv, CLAUDE_PROJECT_DIR: repoRoot },
  });
}

let failures = 0;

function report(name, passed, detail) {
  if (passed) {
    console.log(`ok   ${name}`);
    return;
  }
  failures++;
  console.error(`FAIL ${name}: ${detail}`);
}

function runCases(cases, cwd, label) {
  for (const testCase of cases) {
    const result = runPipeline(JSON.stringify({ tool_input: { command: testCase.command }, cwd }));
    const verdictOk = result.status === testCase.expect;
    const fragmentOk = testCase.expect === ALLOW || (result.stderr ?? "").includes("guard-main");
    report(
      `[${label}] ${testCase.name}`,
      verdictOk && fragmentOk,
      `expected exit ${testCase.expect}, got ${result.status}; stderr: ${(result.stderr ?? "").trim()}`,
    );
  }
}

try {
  runCases(onMain, clone, "main");
  runCases(onFeature, worktree, "feature");

  const malformed = runPipeline("this is not json but mentions git commit");
  report("malformed JSON fails open", malformed.status === ALLOW, `got exit ${malformed.status}`);
} finally {
  rmSync(sandbox, { recursive: true, force: true });
}

if (failures > 0) {
  console.error(`\n${failures} case(s) failed`);
  process.exit(1);
}
console.log(`\nall ${onMain.length + onFeature.length + 1} cases passed`);
