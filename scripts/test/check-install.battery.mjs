// Verification battery for scripts/setup/check-install.mjs.
//
// The repo has no test runner (empty workspace), and check-install.mjs is a
// dependency-free preinstall guard whose interface is: the pnpm user agent
// (env), the pin files two directories up (.nvmrc, package.json, and optionally
// pnpm-workspace.yaml / .npmrc), and the running Node, producing an exit code
// and a diagnostic. This battery exercises that exact interface: for each case
// it builds a throwaway fixture tree, copies the real guard into it so its
// `../../` resolves to the fixture, runs it with a crafted `npm_config_user_agent`,
// and asserts the exit code (and a message fragment where the branch matters).
//
// Covers the acceptance matrix: pnpm major (<=10 / >=11) x engineStrict (on via
// both spellings / off) x devEngines (present / absent) x pin (exact / range
// drift / site drift / wrong node). The pnpm-11 + engineStrict case is the one
// this slice changes; every other case pins existing behavior so the change
// cannot regress it. Run: node scripts/test/check-install.battery.mjs
import { mkdtempSync, writeFileSync, mkdirSync, copyFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const here = dirname(fileURLToPath(import.meta.url));
const guardSrc = join(here, "..", "setup", "check-install.mjs");

// Pin fixtures to the running Node's own major so the wrong-Node check (which
// runs against the real process, not a fixture) passes for the cases that must
// reach past it; the wrong-node case below deliberately pins a different major.
const runningMajor = Number(process.versions.node.split(".")[0]);
const REQ = `${runningMajor}.0.0`;
const RANGE = `>=${REQ} <${runningMajor + 1}`;
// A major guaranteed distinct from the runner's own, for the wrong-major case
// below — hardcoding one collides when the runner's own Node is that major.
const wrongMajor = runningMajor - 1;
const nodeTok = `node/v${process.versions.node}`;

function run({ files, agent }) {
  const dir = mkdtempSync(join(tmpdir(), "ci-battery-"));
  let code = 0;
  let stderr = "";
  try {
    mkdirSync(join(dir, "scripts", "setup"), { recursive: true });
    copyFileSync(guardSrc, join(dir, "scripts", "setup", "check-install.mjs"));
    for (const [name, content] of Object.entries(files)) {
      writeFileSync(join(dir, name), content);
    }
    try {
      execFileSync(process.execPath, [join(dir, "scripts", "setup", "check-install.mjs")], {
        env: { ...process.env, npm_config_user_agent: agent },
        stdio: ["ignore", "ignore", "pipe"],
      });
    } catch (error) {
      code = typeof error.status === "number" ? error.status : 1;
      stderr = (error.stderr || "").toString();
    }
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
  return { code, stderr };
}

const pkg = (extra) =>
  JSON.stringify({
    name: "fix",
    version: "1.0.0",
    engines: { node: RANGE },
    devEngines: { runtime: { name: "node", version: REQ, onFail: "download" } },
    ...extra,
  });
const pkgNoDevEngines = JSON.stringify({ name: "fix", version: "1.0.0", engines: { node: RANGE } });
const pkgRangeRuntime = JSON.stringify({
  name: "fix",
  version: "1.0.0",
  engines: { node: RANGE },
  devEngines: { runtime: { name: "node", version: RANGE, onFail: "download" } },
});
const pkgWrongMajor = JSON.stringify({
  name: "fix",
  version: "1.0.0",
  engines: { node: `>=${wrongMajor}.0.0 <${wrongMajor + 1}` },
  devEngines: { runtime: { name: "node", version: `${wrongMajor}.0.0`, onFail: "download" } },
});

const AGENT11 = `pnpm/11.7.0 npm/? ${nodeTok} darwin arm64`;
const AGENT10 = `pnpm/10.32.1 npm/? ${nodeTok} darwin arm64`;
const AGENT9 = `pnpm/9.15.0 npm/? ${nodeTok} darwin arm64`;

const cases = [
  {
    name: "non-pnpm agent blocks",
    agent: `npm/10.0.0 ${nodeTok}`,
    files: { ".nvmrc": REQ, "package.json": pkg() },
    expect: 1,
    match: /pnpm only/,
  },
  {
    name: "pnpm11 happy path (no engineStrict)",
    agent: AGENT11,
    files: { ".nvmrc": REQ, "package.json": pkg() },
    expect: 0,
  },
  {
    name: "pnpm11 + engineStrict(.npmrc) + devEngines -> coexist, passes",
    agent: AGENT11,
    files: { ".nvmrc": REQ, "package.json": pkg(), ".npmrc": "engine-strict=true\n" },
    expect: 0,
  },
  {
    name: "pnpm11 + engineStrict(pnpm-workspace) + devEngines -> coexist, passes",
    agent: AGENT11,
    files: { ".nvmrc": REQ, "package.json": pkg(), "pnpm-workspace.yaml": "engineStrict: true\n" },
    expect: 0,
  },
  {
    name: "pnpm10 + engineStrict(pnpm-workspace) + devEngines -> deadlock, blocks",
    agent: AGENT10,
    files: { ".nvmrc": REQ, "package.json": pkg(), "pnpm-workspace.yaml": "engineStrict: true\n" },
    expect: 1,
    match: /engineStrict/,
  },
  {
    name: "pnpm9 + engineStrict(.npmrc) + devEngines -> deadlock, blocks",
    agent: AGENT9,
    files: { ".nvmrc": REQ, "package.json": pkg(), ".npmrc": "engine-strict=true\n" },
    expect: 1,
    match: /engineStrict/,
  },
  {
    name: "opt-out posture: no devEngines + engineStrict -> pairing check skipped, passes",
    agent: AGENT10,
    files: { ".nvmrc": REQ, "package.json": pkgNoDevEngines, ".npmrc": "engine-strict=true\n" },
    expect: 0,
  },
  {
    name: "drift: engines.node disagrees with .nvmrc, blocks",
    agent: AGENT11,
    files: { ".nvmrc": REQ, "package.json": pkg({ engines: { node: ">=99.0.0 <100" } }) },
    expect: 1,
    match: /disagrees/,
  },
  {
    name: "drift: devEngines range instead of exact, blocks (exact-not-range)",
    agent: AGENT11,
    files: { ".nvmrc": REQ, "package.json": pkgRangeRuntime },
    expect: 1,
    match: /disagrees/,
  },
  {
    name: "wrong node major, blocks",
    agent: AGENT11,
    files: { ".nvmrc": `${wrongMajor}.0.0`, "package.json": pkgWrongMajor },
    expect: 1,
    match: /Wrong Node/,
  },
];

let passed = 0;
let failed = 0;
for (const c of cases) {
  let result;
  try {
    result = run(c);
  } catch (error) {
    failed += 1;
    console.log(`  FAIL ${c.name}: harness error — ${error.message}`);
    continue;
  }
  const { code, stderr } = result;
  const okCode = code === c.expect;
  const okMatch = !c.match || c.match.test(stderr);
  if (okCode && okMatch) {
    passed += 1;
    console.log(`  ok   ${c.name}`);
  } else {
    failed += 1;
    const firstLine = stderr.split("\n").find(Boolean) || "(no stderr)";
    console.log(
      `  FAIL ${c.name}: expected exit ${c.expect}${c.match ? ` matching ${c.match}` : ""}, got ${code} — ${firstLine.trim()}`,
    );
  }
}
console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
