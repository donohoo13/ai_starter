// Verification battery for scripts/setup/check-install.mjs.
//
// The repo has no test runner (empty workspace), and check-install.mjs is a
// dependency-free preinstall guard whose interface is: the pnpm user agent
// (env) and the pin files two directories up (.nvmrc, package.json), producing
// an exit code and a diagnostic. This battery exercises that exact interface:
// for each case it builds a throwaway fixture tree, copies the real guard into
// it so its `../../` resolves to the fixture, runs it with a crafted
// `npm_config_user_agent`, and asserts the exit code (and a message fragment
// where the branch matters).
//
// Covers installer (pnpm / other) x pin (agreeing / engines drift / devEngines
// range / devEngines absent). Fixtures pin a Node unrelated to the running one,
// since the guard leaves the runtime to devEngines and mise.
// Run: pnpm exec node scripts/test/check-install.battery.mjs
import { mkdtempSync, writeFileSync, mkdirSync, copyFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execFileSync } from "node:child_process";

const here = dirname(fileURLToPath(import.meta.url));
const guardSrc = join(here, "..", "setup", "check-install.mjs");

const REQ = "26.5.0";
const RANGE = `>=${REQ} <27`;
const PNPM_AGENT = `pnpm/11.7.0 npm/? node/v${REQ} darwin arm64`;

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

const cases = [
  {
    name: "non-pnpm agent blocks",
    agent: `npm/10.0.0 node/v${REQ}`,
    files: { ".nvmrc": REQ, "package.json": pkg() },
    expect: 1,
    match: /pnpm only/,
  },
  {
    name: "pnpm with an agreeing pin passes",
    agent: PNPM_AGENT,
    files: { ".nvmrc": REQ, "package.json": pkg() },
    expect: 0,
  },
  {
    name: "opt-out posture: no devEngines passes",
    agent: PNPM_AGENT,
    files: { ".nvmrc": REQ, "package.json": pkgNoDevEngines },
    expect: 0,
  },
  {
    name: "drift: engines.node disagrees with .nvmrc, blocks",
    agent: PNPM_AGENT,
    files: { ".nvmrc": REQ, "package.json": pkg({ engines: { node: ">=99.0.0 <100" } }) },
    expect: 1,
    match: /disagrees/,
  },
  {
    name: "drift: devEngines range instead of exact, blocks (exact-not-range)",
    agent: PNPM_AGENT,
    files: { ".nvmrc": REQ, "package.json": pkgRangeRuntime },
    expect: 1,
    match: /disagrees/,
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
