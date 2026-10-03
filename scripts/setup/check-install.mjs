// Preinstall guard: hard-fail an install not run through pnpm, and any install
// running on the wrong Node version. Dependency-free on purpose — this runs
// before node_modules exists, so built-ins only. Every failure path prints an
// actionable message and exits 1; a raw stack trace from here is a bug in here.
//
// pnpm-only, because the workspace protocol, the runtime pin, and the lockfile
// all assume pnpm; a stray `npm install` half-installs and corrupts the lockfile
// story. Read from the installer's own user agent, so it needs no dependencies.
//
// ── The Node pin: four sites, one version ───────────────────────────────────
//   .nvmrc                      exact version. The source of truth, and what mise and nvm read.
//   engines.node                ">=<version> <<major+1>". The range this file enforces.
//   devEngines.runtime.version  exact version. What pnpm downloads and runs scripts under.
//   pnpm-lock.yaml              regenerate and commit; stale fails --frozen-lockfile, CI's default.
// This file cross-checks the first three on every install BEFORE it checks the
// machine, because a partial retarget is otherwise indistinguishable from a
// broken environment and sends the reader hunting through their Node installs
// for a repo bug.
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
// engineStrict OFF wherever devEngines is present — on pnpm <=10.
//   pnpm's own settings docs recommend pairing engineStrict with nodeVersion,
//   so a project that followed them carries it. On pnpm <=10, alongside
//   devEngines the pair deadlocks: the engines check runs against the AMBIENT
//   Node before pnpm switches to the pinned runtime, so every pnpm command
//   fails on any other Node — including the install that would have downloaded
//   it. pnpm 11+ provisions the runtime BEFORE that check, so the pairing
//   installs cleanly and the two coexist (measured). The guard below hard-fails
//   the pairing only on pnpm <=10; read it for the measurement and the fix.
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
//
// This guard is not decorative: devEngines engages only when the pnpm running
// the install honors it. pnpm 9 (which also defaults manage-package-manager-
// versions to false, so it ignores the packageManager pin), a non-pnpm
// installer, or a sandbox with no network all land here on the ambient Node.
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

// pnpm major from the same user agent (the pnpm-only gate above guarantees the
// `pnpm/` prefix). Used to scope the engineStrict/devEngines check below, which
// is a pnpm <=10 deadlock only.
const pnpmMajor = Number((agent.match(/^pnpm\/(\d+)/) || [])[1]);

const here = dirname(fileURLToPath(import.meta.url));
const nvmrcPath = join(here, "..", "..", ".nvmrc");

let raw;
try {
  raw = readFileSync(nvmrcPath, "utf8");
} catch {
  fail([
    `  ✖ .nvmrc not found at ${nvmrcPath}.`,
    "",
    "    This repo pins its Node major in .nvmrc. Fix it:",
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

// Drift check, before the machine check: when the three pin sites disagree, pnpm
// supplies one version while this guard enforces another, and the wrong-Node
// message below would blame the machine for a repo bug. Name the drifted field
// instead — this is the cheapest place to catch it, since the guard already runs
// on every install and has .nvmrc in hand.
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

// engineStrict × devEngines deadlock ON pnpm <=10, before the machine check and
// for the same reason: it is a repo bug that presents as a broken machine.
//
// pnpm's settings docs recommend pairing engineStrict with nodeVersion to stop
// contributors adding dependencies that declare an incompatible engine, so a
// project that followed them carries engineStrict: true. With nodeVersion also
// set the engines check runs against the version pnpm PRETENDS, so it passes;
// delete nodeVersion for the devEngines pin — which is exactly what this repo's
// changelog instructs — and on pnpm <=10 the check falls through to the AMBIENT
// Node and runs BEFORE pnpm switches to the devEngines runtime, so the guard
// blocks the very install that would have provisioned the pinned Node. pnpm 11+
// switches to the runtime first, so the pairing installs cleanly and the two
// coexist; the guard therefore hard-fails only when the pnpm major is <=10 or
// cannot be parsed. Evidence for both behaviors is in the CHANGELOG.
//
// Two limits, both on pnpm <=10: this check cannot fire in the fully bricked
// state, because pnpm refuses at command startup and preinstall never runs —
// that developer gets pnpm's own message blaming their Node. It fires on the
// machine of whoever introduces the pairing while already on the pinned Node,
// the one place it is silently latent. Separately, on pnpm 11 the wrong-Node
// check below is advisory: preinstall runs under the provisioned runtime, so
// process.versions.node equals the pin regardless of ambient, and the check is
// load-bearing only on pnpm <=10 and the no-devEngines opt-out posture.
function readIfPresent(path) {
  try {
    return readFileSync(path, "utf8");
  } catch {
    return null;
  }
}

function engineStrictSite() {
  const workspace = readIfPresent(join(here, "..", "..", "pnpm-workspace.yaml"));
  if (
    workspace !== null &&
    /^engineStrict[ \t]*:[ \t]*(true|'true'|"true")[ \t]*(#.*)?$/m.test(workspace)
  ) {
    return { file: "pnpm-workspace.yaml", found: "engineStrict: true", fix: "engineStrict: false" };
  }
  // The .npmrc spelling predates pnpm's move of settings into pnpm-workspace.yaml
  // and is still honored, so a project carrying it deadlocks identically.
  const npmrc = readIfPresent(join(here, "..", "..", ".npmrc"));
  if (npmrc !== null && /^[ \t]*engine-strict[ \t]*=[ \t]*true[ \t]*$/m.test(npmrc)) {
    return { file: ".npmrc", found: "engine-strict=true", fix: "engine-strict=false" };
  }
  return null;
}

// Absent devEngines is a deliberate opt-out posture, where engineStrict is the
// only Node enforcement the project has and must stay on. Only the pairing fails.
const engineStrict = pkg.devEngines?.runtime === undefined ? null : engineStrictSite();

// The deadlock is a pnpm <=10 behavior. On pnpm 11+ the runtime is provisioned
// before the engines check, so the pairing installs cleanly (measured) and the
// guard leaves it alone. An unparseable major stays conservative and blocks,
// since it might be a pnpm <=10.
const pairingDeadlocks = Number.isNaN(pnpmMajor) || pnpmMajor <= 10;

if (engineStrict && pairingDeadlocks) {
  const majorLabel = Number.isNaN(pnpmMajor) ? "<=10" : String(pnpmMajor);
  fail([
    `  ✖ On pnpm ${majorLabel}, engineStrict and devEngines deadlock. As configured,`,
    `    this repo is uninstallable by anyone whose ambient Node is not already ${required}.`,
    `    Found ${engineStrict.found} in ${engineStrict.file}, alongside`,
    "    devEngines.runtime in package.json.",
    "",
    "    On pnpm <=10 the engines check runs against the ambient Node BEFORE the",
    "    switch to the devEngines runtime, so it blocks the very install that would",
    `    have downloaded Node ${required}. Every pnpm command fails that way, not`,
    "    just install. You are reading this instead of ERR_PNPM_UNSUPPORTED_ENGINE",
    `    only because your own Node (v${process.versions.node}) satisfies the range.`,
    "",
    "    Fix it — pick one:",
    "      • Upgrade to pnpm 11+, which provisions the runtime BEFORE the engines",
    "        check, so the pairing installs cleanly and this guard stops blocking it.",
    `      • Keep this pnpm: set ${engineStrict.fix} in ${engineStrict.file}, so the`,
    "        runtime download works and contributors need no Node of their own.",
    "      • Keep engineStrict: delete the devEngines block from package.json and",
    `        require every contributor to install Node ${required} themselves.`,
    "",
    "    What engineStrict off gives up on pnpm <=10: pnpm no longer hard-blocks a",
    "    DEPENDENCY that declares an incompatible engine. On pnpm 11+ you keep both,",
    "    so upgrading is the clean fix.",
  ]);
}

const actual = process.versions.node;
const [actMajor, actMinor, actPatch] = actual.split(".").map(Number);

// Pin to the .nvmrc major and require at least the .nvmrc patch within it.
const okMajor = actMajor === reqMajor;
const okFloor = actMinor > reqMinor || (actMinor === reqMinor && actPatch >= reqPatch);

if (!okMajor || !okFloor) {
  // Two different problems reach this branch, and they take different fixes:
  // the required major is missing entirely, or it is present but too old.
  // Diagnosing the second as the first sends the reader hunting for a Node
  // they demonstrably have.
  const wrongMajorHelp = [
    `    Node ${reqMajor} is very likely not installed anywhere on this machine.`,
    "    Verify that before anything else — both checks below fail in ways that",
    "    make an absent Node look present:",
    "",
    `      • Homebrew's versioned aliases can all point at ONE build, so the`,
    `        existence of /opt/homebrew/opt/node@${reqMajor} proves nothing:`,
    `            readlink /opt/homebrew/opt/node@${reqMajor}`,
    "            ls /opt/homebrew/Cellar | grep node",
    `        If that symlink resolves to a Cellar build that is not ${reqMajor}.x,`,
    `        you do not have Node ${reqMajor}.`,
    "",
    "      • nvm can be installed but never sourced, which hides every version it",
    '        manages behind "nvm: command not found":',
    "            command -v nvm || ls ~/.nvm/nvm.sh",
    "        If the file exists but the command does not, source it first:",
    "            . ~/.nvm/nvm.sh",
    "",
    "    Then install it:",
    "      • mise:  mise install               (reads .nvmrc through mise.toml)",
    "      • nvm:  nvm install && nvm use      (reads .nvmrc; needs nvm sourced)",
    `      • pnpm 11+:  pnpm runtime set node ${reqMajor} -g`,
    `        pnpm 10 spelling: pnpm env use --global ${reqMajor}`,
    "        Both error with ERR_PNPM_NO_GLOBAL_BIN_DIR when the global bin dir is",
    "        unset or off PATH. Run `pnpm setup` first if you hit that.",
    `      • or install Node ${required} through whatever version manager you use.`,
  ];

  const oldPatchHelp = [
    `    You have Node ${reqMajor}, but ${actual} is older than the ${required} floor.`,
    `    Upgrade within the major — there is nothing wrong with your Node install:`,
    "      • mise:  mise install               (reads .nvmrc through mise.toml)",
    "      • nvm:  nvm install && nvm use      (reads .nvmrc)",
    `      • pnpm 11+:  pnpm runtime set node ${required} -g`,
    `      • brew:  brew upgrade node@${reqMajor}`,
  ];

  fail([
    `  ✖ Wrong Node.js version: this repo requires Node ${reqMajor}.x (>= ${required}).`,
    `    You are running v${actual}.`,
    "",
    ...(okMajor ? oldPatchHelp : wrongMajorHelp),
    "",
    "    Why pnpm did not supply it: package.json pins the runtime in",
    "    devEngines.runtime, which pnpm downloads and runs lifecycle scripts under.",
    "    That engages only when the pnpm running this install honors devEngines and",
    "    could reach the network. Check which pnpm actually ran:",
    "        pnpm -v      # compare against the packageManager pin in package.json",
    "    If it is below that pin, the fix is to get onto it (`corepack enable`, or",
    "    upgrade pnpm) — pnpm 9 and older ignore devEngines entirely and do not",
    "    self-switch to the pin. Upgrading pnpm is safe here: the pin no longer",
    "    rides pnpm-workspace.yaml's useNodeVersion, which pnpm 11 removed.",
  ]);
}
