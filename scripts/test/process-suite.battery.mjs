#!/usr/bin/env node
// Asserts the structural rules of the skill and agent suite that prose alone cannot hold, such as which agent a skill preloads and which skill may dispatch an agent.

import { readFileSync } from "node:fs";
import { join } from "node:path";

let failures = 0;

function check(name, condition, detail) {
  if (condition) {
    console.log(`ok   ${name}`);
    return;
  }
  console.log(`FAIL ${name}${detail ? ` — ${detail}` : ""}`);
  failures += 1;
}

function readRepoFile(path) {
  try {
    return readFileSync(join(process.cwd(), path), "utf8");
  } catch {
    return null;
  }
}

function frontmatterOf(source) {
  if (!source?.startsWith("---\n")) return null;
  const end = source.indexOf("\n---\n", 4);
  return end === -1 ? null : source.slice(4, end + 1);
}

function scalarValue(frontmatter, key) {
  const match = frontmatter.match(new RegExp(`^${key}:\\s*(.+)$`, "m"));
  return match ? match[1].trim() : null;
}

function listValues(frontmatter, key) {
  const lines = frontmatter.split("\n");
  const start = lines.findIndex(function isKeyLine(line) {
    return line.trim() === `${key}:`;
  });
  if (start === -1) return [];
  const values = [];
  for (const line of lines.slice(start + 1)) {
    const match = line.match(/^\s+-\s+(.*)$/);
    if (!match) break;
    values.push(match[1].trim());
  }
  return values;
}

function checkImplementer() {
  const path = ".claude/agents/implementer.md";
  const frontmatter = frontmatterOf(readRepoFile(path));
  check(`${path} exists with frontmatter`, frontmatter !== null);
  if (frontmatter === null) return;
  check(
    `${path} preloads tdd`,
    listValues(frontmatter, "skills").includes("tdd"),
    "add tdd under skills:",
  );
  check(`${path} pins model opus`, scalarValue(frontmatter, "model") === "opus");
}

checkImplementer();

console.log("");
if (failures > 0) {
  console.log(
    `${failures} failed; run from the repo root: pnpm exec node scripts/test/process-suite.battery.mjs`,
  );
  process.exit(1);
}
console.log("all process-suite checks passed");
