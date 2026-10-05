#!/usr/bin/env node
// Asserts the frontmatter of every .claude/rules/*.md and docs/standards/*.md
// file is well-formed.
//
// Why this exists: a rules file reaches a session through its `paths:` globs,
// and a standards file reaches the agents that judge code through its
// `applies-to:` globs; nothing else guards either. Malformed frontmatter loads
// the body with empty metadata, so the file never fires and the session looks
// exactly like one that had nothing to follow -- a failure shaped like success.
// Each scope also rejects the other's key: a rule scoped with `applies-to:`
// never loads, and a standard scoped with `paths:` reads as auto-loading.
//
// Scope, stated so nobody reads more into a green run than it earns: this
// checks that the block parses and that every glob is a plausible, quoted,
// brace-balanced pattern. It does NOT check match semantics, because the
// harness owns the glob engine and no glob library ships in this repo.
// Whether a given path actually matches is not covered here.

import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const SCOPES = [
  {
    dir: ".claude/rules",
    key: "paths",
    foreignKey: "applies-to",
    unscoped: "loads unconditionally",
  },
  {
    dir: "docs/standards",
    key: "applies-to",
    foreignKey: "paths",
    unscoped: "applies to every change",
  },
];
let failures = 0;

function check(name, condition, detail) {
  if (condition) {
    console.log(`ok   ${name}`);
    return;
  }
  console.log(`FAIL ${name}${detail ? ` — ${detail}` : ""}`);
  failures += 1;
}

function parseFrontmatter(source) {
  if (!source.startsWith("---\n")) return null;
  const end = source.indexOf("\n---\n", 4);
  if (end === -1) return { malformed: true };
  return { body: source.slice(4, end + 1) };
}

function keyLineIndex(lines, key) {
  return lines.findIndex(function isKeyLine(line) {
    return line.trim() === `${key}:`;
  });
}

function readGlobs(block, key) {
  const lines = block.split("\n");
  const start = keyLineIndex(lines, key);
  if (start === -1) return null;
  const globs = [];
  for (const line of lines.slice(start + 1)) {
    if (!line.startsWith(" ")) break;
    const match = line.match(/^\s+-\s+(.*)$/);
    if (!match) break;
    globs.push(match[1].trim());
  }
  return globs;
}

function checkGlob(label, glob) {
  const quoted = /^'.*'$/.test(glob) || /^".*"$/.test(glob);
  check(`${label}: ${glob} is quoted`, quoted, "an unquoted glob starting with * is invalid YAML");

  const inner = quoted ? glob.slice(1, -1) : glob;
  check(`${label}: ${glob} is non-empty`, inner.length > 0);

  const opens = (inner.match(/\{/g) || []).length;
  const closes = (inner.match(/\}/g) || []).length;
  check(
    `${label}: ${glob} has balanced braces`,
    opens === closes,
    `${opens} open, ${closes} close`,
  );

  const emptyBrace = /\{\s*\}/.test(inner) || /\{[^}]*,\s*,/.test(inner) || /\{\s*,/.test(inner);
  check(`${label}: ${glob} has no empty brace member`, !emptyBrace);
}

function checkFile(scope, file) {
  const label = `${scope.dir}/${file}`;
  const frontmatter = parseFrontmatter(readFileSync(join(process.cwd(), scope.dir, file), "utf8"));

  // No frontmatter is a legal, deliberate placement (template-dev.md and
  // design-principles.md use it), so absence is not a failure -- only a
  // frontmatter block that opens and never closes.
  if (frontmatter === null) {
    console.log(`ok   ${label}: no frontmatter, ${scope.unscoped}`);
    return;
  }

  if (frontmatter.malformed) {
    check(`${label}: frontmatter closes`, false, "opening --- with no closing ---");
    return;
  }

  check(
    `${label}: carries no ${scope.foreignKey} key`,
    keyLineIndex(frontmatter.body.split("\n"), scope.foreignKey) === -1,
    `files in ${scope.dir} scope with ${scope.key}:, so rename ${scope.foreignKey}: to ${scope.key}:`,
  );

  const globs = readGlobs(frontmatter.body, scope.key);
  if (globs === null) {
    console.log(`ok   ${label}: no ${scope.key} key, ${scope.unscoped}`);
    return;
  }

  check(`${label}: ${scope.key} block is non-empty`, globs.length > 0);
  for (const glob of globs) checkGlob(label, glob);
}

function checkScope(scope) {
  let files = [];
  try {
    files = readdirSync(join(process.cwd(), scope.dir)).filter(function isMarkdown(name) {
      return name.endsWith(".md");
    });
  } catch (error) {
    check(`${scope.dir} exists`, false, error.code);
    return;
  }
  check(`${scope.dir} holds at least one file`, files.length > 0, `found ${files.length}`);
  for (const file of files) checkFile(scope, file);
}

for (const scope of SCOPES) checkScope(scope);

console.log("");
if (failures > 0) {
  console.log(
    `${failures} failed; run from the repo root: pnpm exec node scripts/test/rules-frontmatter.battery.mjs`,
  );
  process.exit(1);
}
console.log("all frontmatter checks passed");
