#!/usr/bin/env node
// Runs the SDD helper's own checks: its unittest suite, the templates generated
// from the document's appendices, and the section references the skills make
// into the document.
//
// Why this exists: the helper gates every SDD approval and nothing else in CI
// runs Python, so a helper that drifted from its document would keep approving
// artifacts against the wrong rules while looking healthy.

import { spawnSync } from "node:child_process";

const python = process.env.PYTHON ?? "python3";
const checks = [
  ["helper unit tests", [python, "-m", "unittest", "discover", "-s", ".claude/sdd/tests"]],
  [
    "templates match the appendices",
    [python, ".claude/sdd/bin/sdd", "templates", "sync", "--check"],
  ],
  ["section references resolve", [python, ".claude/sdd/bin/sdd", "check-refs"]],
];
let failures = 0;

function lastLine(text) {
  const lines = text.trim().split("\n");
  return lines[lines.length - 1] ?? "";
}

for (const [name, [command, ...args]] of checks) {
  const result = spawnSync(command, args, { cwd: process.cwd(), encoding: "utf8" });
  if (result.error) {
    console.log(
      `FAIL ${name} — ${result.error.message}; install python3 or set PYTHON to its path`,
    );
    failures += 1;
    continue;
  }
  if (result.status === 0) {
    console.log(`ok   ${name}: ${lastLine(result.stdout + result.stderr)}`);
    continue;
  }
  console.log(`FAIL ${name} (exit ${result.status})`);
  console.log((result.stdout + result.stderr).trim());
  console.log(`rerun: ${[command, ...args].join(" ")}`);
  failures += 1;
}

console.log("");
if (failures > 0) {
  console.log(
    `${failures} of ${checks.length} SDD helper checks failed; run from the repo root: pnpm exec node scripts/test/sdd-helper.battery.mjs`,
  );
  process.exit(1);
}
console.log(`all ${checks.length} SDD helper checks passed`);
