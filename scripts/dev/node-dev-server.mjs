#!/usr/bin/env node
// `pnpm dev`: starts `turbo dev` once per checkout and mirrors its output into
// .logs/dev-server.log, so whoever did not start the server (the user or an AI
// session) can read the same output. A second start while one is running exits
// 0 with the running pid instead of competing for ports. Extra args pass through
// to turbo (`pnpm dev --filter web`).
import { spawn } from "node:child_process";
import { createWriteStream, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const LOG_DISPLAY_PATH = ".logs/dev-server.log";
const logPath = join(repoRoot, LOG_DISPLAY_PATH);
const pidPath = join(repoRoot, ".logs", "dev-server.pid");

function runningServerPid() {
  let pid;
  try {
    pid = Number.parseInt(readFileSync(pidPath, "utf8"), 10);
  } catch {
    return null;
  }
  if (!Number.isInteger(pid) || pid <= 0) return null;
  try {
    // Signal 0 delivers nothing; it only asks the OS whether the pid exists.
    process.kill(pid, 0);
    return pid;
  } catch (error) {
    return error.code === "EPERM" ? pid : null;
  }
}

const existing = runningServerPid();
if (existing) {
  console.log(`Dev server already running (pid ${existing}); logs: ${LOG_DISPLAY_PATH}`);
  process.exit(0);
}

mkdirSync(dirname(logPath), { recursive: true });
const log = createWriteStream(logPath);
const turboArgs = ["dev", ...process.argv.slice(2)];
log.write(`# turbo ${turboArgs.join(" ")} started ${new Date().toISOString()}\n`);

const server = spawn("turbo", turboArgs, { cwd: repoRoot, stdio: ["inherit", "pipe", "pipe"] });

function removePidFile() {
  try {
    if (readFileSync(pidPath, "utf8") === String(server.pid)) rmSync(pidPath);
  } catch {
    // already gone
  }
}

server.on("error", (error) => {
  console.error(`Could not start turbo (${error.message}); run this through \`pnpm dev\`.`);
  log.end(() => process.exit(1));
});

if (server.pid) {
  // The server's pid, not this wrapper's: an orphaned server must still read as running.
  writeFileSync(pidPath, String(server.pid));
  console.log(`Dev server starting (pid ${server.pid}); logs: ${LOG_DISPLAY_PATH}`);
}

server.stdout.on("data", (chunk) => {
  process.stdout.write(chunk);
  log.write(chunk);
});
server.stderr.on("data", (chunk) => {
  process.stderr.write(chunk);
  log.write(chunk);
});

for (const signal of ["SIGINT", "SIGTERM", "SIGHUP"]) {
  process.on(signal, () => server.kill(signal));
}

server.on("exit", (code) => {
  removePidFile();
  log.end(() => process.exit(code ?? 1));
});
