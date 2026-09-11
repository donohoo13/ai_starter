#!/usr/bin/env node
// Asserts every .claude/rules/*.md file's frontmatter is well-formed.
//
// Why this exists: a rules file reaches a session through its `paths:` globs,
// and nothing else guards them. Malformed frontmatter loads the body with
// empty metadata, so the rules never fire and the session looks exactly like
// one that had no rules to follow -- a failure shaped like success.
//
// Scope, stated so nobody reads more into a green run than it earns: this
// checks that the block parses and that every glob is a plausible, quoted,
// brace-balanced pattern. It does NOT check match semantics, because the
// harness owns the glob engine and no glob library ships in this repo.
// Whether a given path actually matches is not covered here.

import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';

const RULES_DIR = join(process.cwd(), '.claude', 'rules');
let failures = 0;

function check(name, condition, detail) {
  if (condition) {
    console.log(`ok   ${name}`);
    return;
  }
  console.log(`FAIL ${name}${detail ? ` — ${detail}` : ''}`);
  failures += 1;
}

function parseFrontmatter(source) {
  if (!source.startsWith('---\n')) return null;
  const end = source.indexOf('\n---\n', 4);
  if (end === -1) return { malformed: true };
  return { body: source.slice(4, end + 1) };
}

function readGlobs(block) {
  const lines = block.split('\n');
  const start = lines.findIndex(function isPathsKey(line) {
    return line.trim() === 'paths:';
  });
  if (start === -1) return null;
  const globs = [];
  for (const line of lines.slice(start + 1)) {
    if (!line.startsWith(' ')) break;
    const match = line.match(/^\s+-\s+(.*)$/);
    if (!match) break;
    globs.push(match[1].trim());
  }
  return globs;
}

const files = readdirSync(RULES_DIR).filter(function isMarkdown(name) {
  return name.endsWith('.md');
});
check('rules directory holds at least one file', files.length > 0, `found ${files.length}`);

for (const file of files) {
  const source = readFileSync(join(RULES_DIR, file), 'utf8');
  const frontmatter = parseFrontmatter(source);

  // A rules file without frontmatter loads unconditionally. That is a legal,
  // deliberate placement (template-dev.md uses it), so absence is not a failure
  // -- only a frontmatter block that opens and never closes.
  if (frontmatter === null) {
    console.log(`ok   ${file}: no frontmatter, loads unconditionally`);
    continue;
  }

  if (frontmatter.malformed) {
    check(`${file}: frontmatter closes`, false, 'opening --- with no closing ---');
    continue;
  }

  const globs = readGlobs(frontmatter.body);
  if (globs === null) {
    console.log(`ok   ${file}: frontmatter carries no paths key`);
    continue;
  }

  check(`${file}: paths block is non-empty`, globs.length > 0);

  for (const glob of globs) {
    const quoted = /^'.*'$/.test(glob) || /^".*"$/.test(glob);
    check(`${file}: ${glob} is quoted`, quoted, 'an unquoted glob starting with * is invalid YAML');

    const inner = quoted ? glob.slice(1, -1) : glob;
    check(`${file}: ${glob} is non-empty`, inner.length > 0);

    const opens = (inner.match(/\{/g) || []).length;
    const closes = (inner.match(/\}/g) || []).length;
    check(
      `${file}: ${glob} has balanced braces`,
      opens === closes,
      `${opens} open, ${closes} close`,
    );

    const emptyBrace = /\{\s*\}/.test(inner) || /\{[^}]*,\s*,/.test(inner) || /\{\s*,/.test(inner);
    check(`${file}: ${glob} has no empty brace member`, !emptyBrace);
  }
}

console.log('');
if (failures > 0) {
  console.log(`${failures} failed`);
  process.exit(1);
}
console.log('all frontmatter checks passed');
