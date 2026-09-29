// Verification battery for scripts/dev/node-dev-server.mjs, the `pnpm dev` entry point.
//
// Copies the script into a sandbox and puts a fake `turbo` first on PATH, so
// the real start, already-running, shutdown, and stale-pidfile paths run
// against a real child process without a workspace. The fake execs into
// `sleep`, so the pid it reports is the pid the wrapper records.
// Run: pnpm exec node scripts/test/node-dev-server.battery.mjs
import { spawn, spawnSync } from "node:child_process";
import {
  chmodSync,
  copyFileSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readFileSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "..", "dev", "node-dev-server.mjs");

const sandbox = mkdtempSync(join(tmpdir(), "dev-server-"));
const script = join(sandbox, "scripts", "dev", "node-dev-server.mjs");
const logPath = join(sandbox, ".logs", "dev-server.log");
const pidPath = join(sandbox, ".logs", "dev-server.pid");
mkdirSync(dirname(script), { recursive: true });
mkdirSync(join(sandbox, "bin"));
copyFileSync(source, script);
const fakeTurbo = join(sandbox, "bin", "turbo");
writeFileSync(
  fakeTurbo,
  '#!/usr/bin/env bash\necho "fake turbo $*"\necho "fake stderr" >&2\nexec sleep 30\n',
);
chmodSync(fakeTurbo, 0o755);
const env = { ...process.env, PATH: `${join(sandbox, "bin")}:${process.env.PATH}` };

let failures = 0;
function report(name, passed, detail) {
  if (passed) {
    console.log(`ok   ${name}`);
    return;
  }
  failures++;
  console.error(`FAIL ${name}: ${detail}`);
}

const readOr = (path, fallback) => (existsSync(path) ? readFileSync(path, "utf8") : fallback);
const isAlive = (pid) => {
  try {
    process.kill(pid, 0);
    return true;
  } catch {
    return false;
  }
};

async function waitFor(condition, timeoutMs = 5000) {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    if (condition()) return true;
    await new Promise((resolve) => setTimeout(resolve, 50));
  }
  return condition();
}

function startWrapper(args = []) {
  const child = spawn(process.execPath, [script, ...args], { cwd: sandbox, env });
  child.output = "";
  child.stdout.on("data", (chunk) => (child.output += chunk));
  child.stderr.on("data", (chunk) => (child.output += chunk));
  child.exited = new Promise((resolve) => child.on("exit", resolve));
  return child;
}

try {
  const first = startWrapper(["--filter", "web"]);
  const started = await waitFor(() => readOr(logPath, "").includes("fake stderr"));
  report(
    "start writes stdout and stderr to the log",
    started,
    `log: ${readOr(logPath, "<missing>")}`,
  );
  report(
    "start passes args through to turbo dev",
    readOr(logPath, "").includes("fake turbo dev --filter web"),
    `log: ${readOr(logPath, "<missing>")}`,
  );
  report(
    "start echoes output to the terminal",
    first.output.includes("fake turbo dev"),
    first.output,
  );
  const serverPid = Number(readOr(pidPath, "NaN"));
  report(
    "start records a live server pid",
    isAlive(serverPid),
    `pidfile: ${readOr(pidPath, "<missing>")}`,
  );

  const second = spawnSync(process.execPath, [script], {
    cwd: sandbox,
    env,
    encoding: "utf8",
    timeout: 5000,
  });
  report("second start exits 0", second.status === 0, `exit ${second.status}; ${second.stderr}`);
  report(
    "second start reports the running pid and log path",
    second.stdout.includes("already running") &&
      second.stdout.includes(String(serverPid)) &&
      second.stdout.includes(".logs/dev-server.log"),
    second.stdout,
  );
  report(
    "second start leaves the running log intact",
    readOr(logPath, "").includes("--filter web"),
    readOr(logPath, "<missing>"),
  );

  first.kill("SIGTERM");
  await first.exited;
  report(
    "shutdown stops the server",
    await waitFor(() => !isAlive(serverPid)),
    `pid ${serverPid} alive`,
  );
  report("shutdown removes the pidfile", !existsSync(pidPath), "pidfile still present");

  writeFileSync(pidPath, "999999");
  const afterStale = startWrapper();
  const restarted = await waitFor(
    () => readOr(pidPath, "999999") !== "999999" && readOr(logPath, "").includes("fake stderr"),
  );
  report("stale pidfile does not block a start", restarted, afterStale.output);
  report(
    "each start truncates the log",
    readOr(logPath, "").startsWith("# turbo dev started") &&
      !readOr(logPath, "").includes("--filter web"),
    readOr(logPath, "<missing>"),
  );

  const orphanPid = Number(readOr(pidPath, "NaN"));
  afterStale.kill("SIGKILL");
  await afterStale.exited;
  const orphanCheck = spawnSync(process.execPath, [script], {
    cwd: sandbox,
    env,
    encoding: "utf8",
    timeout: 5000,
  });
  report(
    "an orphaned server still counts as running",
    orphanCheck.stdout.includes("already running"),
    orphanCheck.stdout,
  );
  if (isAlive(orphanPid)) process.kill(orphanPid, "SIGTERM");
} finally {
  rmSync(sandbox, { recursive: true, force: true });
}

if (failures > 0) {
  console.error(`\n${failures} case(s) failed`);
  process.exit(1);
}
console.log("\nall dev-server cases passed");
