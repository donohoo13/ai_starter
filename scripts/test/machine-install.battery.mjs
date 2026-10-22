#!/usr/bin/env node
// Runs scripts/setup/machine/install.sh against sandbox HOMEs with fake brew, mise, defaults, and uname.
// Run: pnpm exec node scripts/test/machine-install.battery.mjs
import { spawnSync } from "node:child_process";
import {
  chmodSync,
  cpSync,
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
const sandbox = mkdtempSync(join(tmpdir(), "machine-install-"));
const kit = join(sandbox, "repo", "scripts", "setup", "machine");
const installer = join(kit, "install.sh");
const installLog = join(sandbox, "repo", ".logs", "machine-install.log");
const SOURCE_LINE = 'source "$HOME/.config/zsh/ai-starter.zsh"';
const IDENTITY_HINT = "no identity yet";
const KIT_OWNED = [
  ["config/zsh/ai-starter.zsh", ".config/zsh/ai-starter.zsh"],
  ["config/git/ai-starter.gitconfig", ".config/git/ai-starter.gitconfig"],
  ["config/mise/conf.d/ai-starter.toml", ".config/mise/conf.d/ai-starter.toml"],
  ["claude/rules/ai-starter.md", ".claude/rules/ai-starter.md"],
];

let failures = 0;

/**
 * Prints one result line and counts a failure.
 * @param {string} name
 * @param {boolean} passed
 * @param {string} [detail]
 */
function check(name, passed, detail) {
  if (passed) {
    console.log(`ok   ${name}`);
    return;
  }
  failures += 1;
  console.log(`FAIL ${name}${detail ? ` — ${detail}` : ""}`);
}

/**
 * Reads a file, or returns an empty string when it does not exist.
 * @param {string} path
 * @returns {string}
 */
function read(path) {
  return existsSync(path) ? readFileSync(path, "utf8") : "";
}

/**
 * Counts the lines of a text that equal a line exactly.
 * @param {string} text
 * @param {string} line
 * @returns {number}
 */
function countLines(text, line) {
  return text.split("\n").filter(function isLine(candidate) {
    return candidate === line;
  }).length;
}

/**
 * Writes an executable fake command that records its arguments to $CALLS.
 * @param {string} bin
 * @param {string} name
 * @param {string} body
 */
function writeFake(bin, name, body) {
  const path = join(bin, name);
  writeFileSync(path, `#!/bin/sh\necho "${name} $*" >>"$CALLS"\n${body}\n`);
  chmodSync(path, 0o755);
}

/**
 * Builds an empty HOME and a fake-command directory for one scenario.
 * @param {string} name
 * @param {{ os?: string, brew?: boolean, brewExit?: number }} [options]
 * @returns {{ home: string, calls: string, env: NodeJS.ProcessEnv }}
 */
function scenario(name, { os = "Darwin", brew = true, brewExit = 0 } = {}) {
  const root = join(sandbox, name);
  const home = join(root, "home");
  const bin = join(root, "bin");
  const calls = join(root, "calls.log");
  mkdirSync(home, { recursive: true });
  mkdirSync(bin);
  writeFileSync(calls, "");
  writeFake(bin, "uname", `echo ${os}`);
  writeFake(bin, "mise", "exit 0");
  writeFake(bin, "defaults", "exit 0");
  if (brew) writeFake(bin, "brew", `echo "fake brew output"\nexit ${brewExit}`);
  const env = { HOME: home, PATH: `${bin}:/usr/bin:/bin`, CALLS: calls, GIT_CONFIG_NOSYSTEM: "1" };
  return { home, calls, env };
}

/**
 * Runs the installer under the stock /bin/bash.
 * @param {NodeJS.ProcessEnv} env
 * @returns {import("node:child_process").SpawnSyncReturns<string>}
 */
function install(env) {
  return spawnSync("/bin/bash", [installer], { env, encoding: "utf8" });
}

/**
 * Reads a git setting the way a session would see it from the scenario's HOME.
 * @param {NodeJS.ProcessEnv} env
 * @param {string[]} args
 * @returns {string}
 */
function gitConfig(env, args) {
  return spawnSync("git", ["config", ...args], { env, encoding: "utf8" }).stdout.trim();
}

try {
  cpSync(join(here, "..", "setup", "machine"), kit, { recursive: true });
  chmodSync(join(kit, "chrome-policies.sh"), 0o755);

  {
    const { home, calls, env } = scenario("fresh");
    const xdgGitConfig = join(home, ".config", "git", "config");
    const first = install(env);
    check("fresh install exits 0", first.status === 0, first.stderr);
    check(
      "fresh install ends in a change count",
      /^machine kit installed: \d+ file\(s\) changed/m.test(first.stdout),
      first.stdout,
    );
    for (const [source, target] of KIT_OWNED) {
      check(`installs ~/${target}`, read(join(home, target)) === read(join(kit, source)));
    }
    check(
      "wires the zsh fragment into ~/.zshrc",
      countLines(read(join(home, ".zshrc")), SOURCE_LINE) === 1,
    );
    check(
      "kit git settings resolve through the include",
      gitConfig(env, ["--includes", "--global", "pull.rebase"]) === "true",
    );
    check(
      "merges the global git ignore lines",
      [".DS_Store", ".zed/"].every(function isIgnored(line) {
        return countLines(read(join(home, ".config", "git", "ignore")), line) === 1;
      }),
    );
    check(
      "seeds Zed settings and keymap",
      read(join(home, ".config", "zed", "settings.json")) ===
        read(join(kit, "config", "zed", "settings.json")) &&
        read(join(home, ".config", "zed", "keymap.json")) ===
          read(join(kit, "config", "zed", "keymap.json")),
    );
    check(
      "runs brew bundle on the kit Brewfile",
      read(calls).includes(`brew bundle install --file=${join(kit, "Brewfile")}`),
    );
    check("runs mise install", read(calls).includes("mise install"));
    check("applies the Chrome policies", read(calls).includes("defaults write com.google.Chrome"));
    check("hints at a missing git identity", first.stdout.includes(IDENTITY_HINT), first.stdout);

    const second = install(env);
    check("re-run exits 0", second.status === 0, second.stderr);
    check(
      "re-run reports nothing changed",
      second.stdout.trim().endsWith("machine kit up to date: 0 files changed"),
      second.stdout,
    );
    check(
      "re-run keeps one source line",
      countLines(read(join(home, ".zshrc")), SOURCE_LINE) === 1,
    );
    check(
      "re-run keeps one git include",
      gitConfig(env, ["--file", xdgGitConfig, "--get-all", "include.path"]) ===
        "ai-starter.gitconfig",
    );
    check(
      "re-run adds no ignore duplicates",
      countLines(read(join(home, ".config", "git", "ignore")), ".DS_Store") === 1,
    );

    writeFileSync(join(home, ".config", "zsh", "ai-starter.zsh"), "stale\n");
    const third = install(env);
    check(
      "refreshes a stale kit-owned file",
      read(join(home, ".config", "zsh", "ai-starter.zsh")) ===
        read(join(kit, "config", "zsh", "ai-starter.zsh")) &&
        third.stdout.includes("updated ~/.config/zsh/ai-starter.zsh"),
      third.stdout,
    );
  }

  {
    const { home, env } = scenario("existing");
    const gitconfig = "[user]\n\temail = me@example.com\n[pull]\n\trebase = false\n";
    const miseConfig = '[tools]\nruby = "3"\n';
    mkdirSync(join(home, ".config", "zed"), { recursive: true });
    mkdirSync(join(home, ".config", "mise"), { recursive: true });
    writeFileSync(join(home, ".zshrc"), "export WORK=1");
    writeFileSync(join(home, ".gitconfig"), gitconfig);
    writeFileSync(join(home, ".config", "zed", "settings.json"), "{}\n");
    writeFileSync(join(home, ".config", "mise", "config.toml"), miseConfig);
    const result = install(env);
    check("install over machine files exits 0", result.status === 0, result.stderr);
    check(
      "~/.zshrc keeps its content and gains the line on its own line",
      read(join(home, ".zshrc")) === `export WORK=1\n${SOURCE_LINE}\n`,
      JSON.stringify(read(join(home, ".zshrc"))),
    );
    check("~/.gitconfig is untouched", read(join(home, ".gitconfig")) === gitconfig);
    check(
      "a machine git setting wins over the kit",
      gitConfig(env, ["--includes", "--global", "pull.rebase"]) === "false",
    );
    check(
      "existing Zed settings are kept",
      read(join(home, ".config", "zed", "settings.json")) === "{}\n",
    );
    check(
      "the machine mise config is untouched",
      read(join(home, ".config", "mise", "config.toml")) === miseConfig,
    );
    check(
      "no identity hint once an identity exists",
      !result.stdout.includes(IDENTITY_HINT),
      result.stdout,
    );
  }

  {
    const { home, env } = scenario("no-brew", { brew: false });
    const result = install(env);
    check("missing Homebrew exits 1", result.status === 1, result.stdout);
    check(
      "missing Homebrew names the fix",
      result.stderr.includes("https://brew.sh"),
      result.stderr,
    );
    check(
      "missing Homebrew writes nothing",
      !existsSync(join(home, ".config")) && !existsSync(join(home, ".zshrc")),
    );
  }

  {
    const { home, env } = scenario("linux", { os: "Linux" });
    const result = install(env);
    check("a non-macOS host exits 1", result.status === 1, result.stdout);
    check("a non-macOS host says why", result.stderr.includes("macOS-only"), result.stderr);
    check("a non-macOS host writes nothing", !existsSync(join(home, ".config")));
  }

  {
    const { home, env } = scenario("brew-fails", { brewExit: 1 });
    const result = install(env);
    check("a failed brew bundle exits 1", result.status === 1, result.stdout);
    check(
      "a failed brew bundle points at the log",
      result.stderr.includes(".logs/machine-install.log"),
      result.stderr,
    );
    check("the log carries the brew output", read(installLog).includes("fake brew output"));
    check("a failed brew bundle stops before any file", !existsSync(join(home, ".config")));
  }
} finally {
  rmSync(sandbox, { recursive: true, force: true });
}

console.log("");
if (failures > 0) {
  console.log(
    `${failures} failed; fix scripts/setup/machine/install.sh and rerun: pnpm exec node scripts/test/machine-install.battery.mjs`,
  );
  process.exit(1);
}
console.log("all machine-install checks passed");
