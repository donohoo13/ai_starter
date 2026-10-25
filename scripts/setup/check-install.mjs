// Preinstall guard: hard-fail an install not run through pnpm, and any install
// whose Node pin disagrees with itself. Dependency-free on purpose — this runs
// before node_modules exists, so built-ins only. Every failure path prints an
// actionable message and exits 1; a raw stack trace from here is a bug in here.
//
// pnpm-only, because the workspace protocol, the runtime pin, and the lockfile
// all assume pnpm; a stray `npm install` half-installs and corrupts the lockfile
// story. Read from the installer's own user agent, so it needs no dependencies.
//
// ── The Node pin: four sites, one version ───────────────────────────────────
//   .nvmrc                      exact version. The source of truth, and what mise and nvm read.
//   engines.node                ">=<version> <<major+1>". The range installers check Node against.
//   devEngines.runtime.version  exact version. What pnpm downloads and runs scripts under.
//   pnpm-lock.yaml              regenerate and commit; stale fails --frozen-lockfile, CI's default.
// This file cross-checks the first three on every install, because a partial
// retarget is otherwise indistinguishable from a broken environment and sends
// the reader hunting through their Node installs for a repo bug.
//
// The running Node is not checked here. On pnpm 11 preinstall runs under the
// devEngines runtime, so it always equals the pin; a project that opts out of
// devEngines gets Node from mise, and doctor.sh warns when the shell's Node
// drifts. pnpm 9 ignores both devEngines and the packageManager pin, so it
// installs on the ambient Node unchecked; mise is the supported way onto the
// pinned pnpm.
//
// ── Why these defaults, so a project can diverge deliberately ───────────────
// Each choice below was measured, not assumed; the versions, probes, and
// observations live in the CHANGELOG. Change one only with equivalent evidence.
//
// devEngines.runtime, NOT pnpm-workspace.yaml's useNodeVersion.
//   useNodeVersion worked correctly through pnpm 10 and was REMOVED in pnpm 11,
//   which ignores the leftover key silently: no warning, and `pnpm config get
//   use-node-version` still echoes the value back. So a pnpm major bump used to
//   disarm the pin with no visible signal. The general claim "useNodeVersion
//   does not work" is false and misleads the next debugger — it is specifically
//   gone in 11. Never assume a runtime setting engaged because it reads back.
//
// engineStrict alongside devEngines needs pnpm 11+.
//   pnpm 11 provisions the runtime BEFORE the engines check, so the pairing
//   installs cleanly (measured). On pnpm <=10 the check runs against the AMBIENT
//   Node first and blocks the very install that would have downloaded the pin,
//   so a project that drops below pnpm 11 must turn engineStrict off.
//
// An exact version, NEVER a range.
//   On pnpm <=10 a range abandoned runtime resolution entirely and installed a
//   third-party `node` package from the registry (bin creation ENOENT, blocked
//   setup script, lifecycle scripts on the AMBIENT Node). On pnpm 11 the range
//   resolves a real runtime, but the node runtime's own build script trips the
//   build allowlist (ERR_PNPM_IGNORED_BUILDS), so `pnpm exec` then fails at
//   startup — measured. Either way a range breaks the pin, so it stays exact.
//   The exact spelling also earns the lockfile per-platform nodejs.org URLs with
//   integrity hashes; a range records none.
//
// Accepted cost: npm reads devEngines before preinstall and treats onFail
//   "download" as "error", so `npm install` on any other Node dies with
//   EBADDEVENGINES rather than reaching the pnpm-only message below. The install
//   still stops, which is this guard's actual job; only the diagnosis degrades.
//   The change that would fix it (a range) breaks the pin outright, per above.
//   The same npm check kills ANY `npx` spawned with this project as cwd on a
//   drifted ambient Node — including npx-launched Claude Code plugin MCP
//   servers, which die with an opaque -32000. That is why the shipped
//   .mcp.json spells local servers as `pnpm dlx` (pnpm downloads the pinned
//   runtime instead of erroring) and doctor.sh warns on ambient drift.
//
// musl (Alpine): pnpm's runtime resolution serves working musl variants,
//   hosted on unofficial-builds.nodejs.org and pinned by lockfile integrity,
//   so the pin provisions there like everywhere else (measured; see the
//   CHANGELOG). Projects that deleted the devEngines block under the earlier
//   no-musl-build limit can re-adopt the pin; the guard still treats an
//   absent block as a deliberate opt-out, not as drift.
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

function fail(lines) {
  console.error(["", ...lines, ""].join("\n"));
  process.exit(1);
}

const agent = process.env.npm_config_user_agent ?? "";
if (!agent.startsWith("pnpm/")) {
  fail([
    "  ✖ This repo installs with pnpm only.",
    `    Detected installer: ${agent || "(none — run via a package manager, not node directly)"}`,
    "",
    "    Fix it:",
    "      • mise install && pnpm install      (mise reads the packageManager pin)",
    "      • corepack enable && pnpm install   (packageManager pin in package.json)",
  ]);
}

const here = dirname(fileURLToPath(import.meta.url));
const nvmrcPath = join(here, "..", "..", ".nvmrc");

let raw;
try {
  raw = readFileSync(nvmrcPath, "utf8");
} catch {
  fail([
    `  ✖ .nvmrc not found at ${nvmrcPath}.`,
    "",
    "    This repo pins its Node version in .nvmrc. Fix it:",
    "      • restore .nvmrc (a concrete version, e.g. 26.5.0), or",
    '      • drop the guard deliberately: delete .nvmrc AND the "preinstall"',
    "        script in package.json together.",
  ]);
}

const required = raw.trim().replace(/^v/, "");
const [reqMajor, reqMinor = 0, reqPatch = 0] = required.split(".").map(Number);

if (
  !Number.isInteger(reqMajor) ||
  reqMajor <= 0 ||
  !Number.isInteger(reqMinor) ||
  !Number.isInteger(reqPatch)
) {
  fail([
    `  ✖ Malformed .nvmrc: expected a concrete version like 26.5.0, got "${required}".`,
    "",
    "    Aliases (lts/*, node, latest) are not supported by this guard — pin the",
    "    exact version, and mirror the range it implies in package.json",
    "    engines.node and devEngines.runtime.version.",
  ]);
}

const expectedRange = `>=${required} <${reqMajor + 1}`;
const pkgPath = join(here, "..", "..", "package.json");

let pkg;
try {
  pkg = JSON.parse(readFileSync(pkgPath, "utf8"));
} catch (error) {
  fail([
    `  ✖ Could not read package.json at ${pkgPath}: ${error.message}`,
    "",
    "    This guard cross-checks the Node pin against engines.node and",
    "    devEngines.runtime.version, so it needs a parseable package.json.",
  ]);
}

const enginesNode = pkg.engines?.node;
const devEnginesVersion = pkg.devEngines?.runtime?.version;
const drifted = [];

if (enginesNode !== expectedRange) {
  drifted.push(`engines.node is "${enginesNode ?? "(missing)"}", expected "${expectedRange}"`);
}
// devEngines is optional: a project may opt out of the runtime pin deliberately
// (e.g. the base image supplies Node). Present-but-wrong is drift; absent is a choice.
if (devEnginesVersion !== undefined && devEnginesVersion !== required) {
  drifted.push(`devEngines.runtime.version is "${devEnginesVersion}", expected "${required}"`);
}

if (drifted.length > 0) {
  fail([
    `  ✖ The Node pin disagrees with itself. .nvmrc says ${required}, so:`,
    ...drifted.map((line) => `      • ${line}`),
    "",
    "    This is a repo bug, not a problem with your machine — retargeting the",
    "    pin means changing every site together:",
    `      • .nvmrc                     → the exact version (currently ${required})`,
    `      • engines.node               → "${expectedRange}"`,
    `      • devEngines.runtime.version → "${required}" — exact, never a range; a`,
    "                                     range makes pnpm install a registry stub",
    "                                     and silently use the ambient Node.",
    "      • pnpm-lock.yaml             → run `pnpm install` and commit the result,",
    "                                     or CI fails on --frozen-lockfile",
  ]);
}
