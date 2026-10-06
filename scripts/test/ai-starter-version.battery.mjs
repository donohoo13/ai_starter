#!/usr/bin/env node
// Asserts .ai-starter.yaml is well-formed, and in the template repo itself that
// its version matches package.json.
//
// Why this exists: template-sync uses the recorded version as the common
// ancestor for every three-way comparison, so a malformed or drifted value
// silently turns project edits into apparent template changes. In the template
// repo the file ships in the payload, so a release that bumps package.json but
// not this file stamps every new project with the wrong base.
//
// The template repo is recognised by its origin remote matching the file's
// `template` value; a project's package.json version is its own app version, so
// the match check runs only there.

import { execFileSync } from "node:child_process";
import { readFileSync } from "node:fs";

const SEMVER = /^\d+\.\d+\.\d+$/;
const OWNER_REPO = /^[\w.-]+\/[\w.-]+$/;
let failures = 0;

function check(name, condition, detail) {
  if (condition) {
    console.log(`ok   ${name}`);
    return;
  }
  console.log(`FAIL ${name}${detail ? ` — ${detail}` : ""}`);
  failures += 1;
}

function readTopLevelValues(text) {
  const values = {};
  for (const line of text.split("\n")) {
    const match = line.match(/^([a-z_]+):\s*(\S+)\s*$/);
    if (match) values[match[1]] = match[2];
  }
  return values;
}

function originOwnerRepo() {
  try {
    const url = execFileSync("git", ["remote", "get-url", "origin"], {
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
    const match = url.match(/[:/]([\w.-]+\/[\w.-]+?)(?:\.git)?$/);
    return match ? match[1] : null;
  } catch {
    return null;
  }
}

let text = null;
try {
  text = readFileSync(".ai-starter.yaml", "utf8");
} catch {
  // Reported by the check below.
}
check(".ai-starter.yaml exists at the repo root", text !== null);

if (text !== null) {
  const { template, version } = readTopLevelValues(text);
  check("template is owner/repo", OWNER_REPO.test(template ?? ""), `got "${template}"`);
  check("version is X.Y.Z", SEMVER.test(version ?? ""), `got "${version}"`);

  const origin = originOwnerRepo();
  if (origin && template && origin.toLowerCase() === template.toLowerCase()) {
    const pkgVersion = JSON.parse(readFileSync("package.json", "utf8")).version;
    check(
      "template repo: version matches package.json",
      version === pkgVersion,
      `.ai-starter.yaml says ${version}, package.json says ${pkgVersion}; bump both together`,
    );
  } else {
    console.log("skip version match: not the template repo (origin differs or is unset)");
  }
}

console.log("");
if (failures > 0) {
  console.log(
    `${failures} failed; run from the repo root: pnpm exec node scripts/test/ai-starter-version.battery.mjs`,
  );
  process.exit(1);
}
console.log("all .ai-starter.yaml checks passed");
