#!/usr/bin/env node
// Runs the shipped .husky/pre-commit and .husky/pre-push against a throwaway repo, so default-branch detection and branch state are real git rather than mocks.

import { execFileSync, spawnSync } from "node:child_process";
import { chmodSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { delimiter, join } from "node:path";

let failures = 0;

function check(name, condition, detail) {
  if (condition) {
    console.log(`ok   ${name}`);
    return;
  }
  console.log(`FAIL ${name}${detail ? ` — ${detail}` : ""}`);
  failures += 1;
}

function readHook(name) {
  try {
    return readFileSync(join(process.cwd(), ".husky", name), "utf8");
  } catch {
    return null;
  }
}

const scratch = mkdtempSync(join(tmpdir(), "husky-guard-"));
const sandbox = join(scratch, "repo");
const stubBin = join(scratch, "bin");
mkdirSync(sandbox);
mkdirSync(stubBin);

// The project's formatting step after the guard (prettier, lint-staged) runs through pnpm; a no-op pnpm keeps this battery on the guard alone.
writeFileSync(join(stubBin, "pnpm"), "#!/bin/sh\nexit 0\n");
chmodSync(join(stubBin, "pnpm"), 0o755);
const hookEnv = { ...process.env, PATH: `${stubBin}${delimiter}${process.env.PATH}` };

function git(...args) {
  return execFileSync("git", args, { cwd: sandbox, encoding: "utf8" });
}

function runHook(name, input = "") {
  const script = readHook(name);
  if (script === null) return { status: null, stderr: `.husky/${name} is missing` };
  const path = join(scratch, `${name}.sh`);
  writeFileSync(path, script);
  const result = spawnSync("sh", [path], { cwd: sandbox, input, encoding: "utf8", env: hookEnv });
  return { status: result.status, stderr: result.stderr };
}

function expectBlocked(name, hook, input) {
  const result = runHook(hook, input);
  check(
    name,
    result.status !== 0 && result.status !== null,
    result.stderr || `exit ${result.status}`,
  );
}

function expectAllowed(name, hook, input) {
  const result = runHook(hook, input);
  check(name, result.status === 0, result.stderr || `exit ${result.status}`);
}

function pushLine(remoteRef) {
  const sha = "1111111111111111111111111111111111111111";
  return `refs/heads/feature/x ${sha} ${remoteRef} ${sha}\n`;
}

try {
  git("init", "-q", "-b", "main");
  git("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "root");

  expectBlocked("pre-commit refuses a commit on main with no remote", "pre-commit");

  git("switch", "-q", "-c", "feature/x");
  expectAllowed("pre-commit allows a commit on a feature branch", "pre-commit");

  git("switch", "-q", "--detach");
  expectAllowed("pre-commit allows a commit on a detached HEAD", "pre-commit");

  git("update-ref", "refs/remotes/origin/trunk", "HEAD");
  git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/trunk");
  git("switch", "-q", "-c", "trunk");
  expectBlocked("pre-commit reads the default branch from origin/HEAD", "pre-commit");
  git("switch", "-q", "main");
  expectAllowed("pre-commit allows main when origin/HEAD names another default", "pre-commit");

  expectBlocked(
    "pre-push refuses a push to the default branch",
    "pre-push",
    pushLine("refs/heads/trunk"),
  );
  expectAllowed(
    "pre-push allows a push to a feature branch",
    "pre-push",
    pushLine("refs/heads/feature/x"),
  );
  expectAllowed(
    "pre-push allows publishing a tag",
    "pre-push",
    "refs/tags/v1.0.0 1111111111111111111111111111111111111111 refs/tags/v1.0.0 0000000000000000000000000000000000000000\n",
  );
  expectBlocked(
    "pre-push refuses a batch that includes the default branch",
    "pre-push",
    pushLine("refs/heads/feature/x") + pushLine("refs/heads/trunk"),
  );
} finally {
  rmSync(scratch, { recursive: true, force: true });
}

console.log("");
if (failures > 0) {
  console.log(
    `${failures} failed; run from the repo root: pnpm exec node scripts/test/husky-guard.battery.mjs`,
  );
  process.exit(1);
}
console.log("all husky-guard checks passed");
