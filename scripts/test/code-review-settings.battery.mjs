#!/usr/bin/env node
// Asserts .claude/settings.json leaves Claude Code's bundled /code-review
// invocable by the model, since preflight runs it beside code-reviewer.
// Three settings block it: a deny rule matching the Skill tool for
// code-review, `disableBundledSkills`, and any `skillOverrides` entry for it.
// The self-cases run first so a green check on the shipped file means the
// detector would have caught each blocking form.
// Run: pnpm exec node scripts/test/code-review-settings.battery.mjs
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = join(dirname(fileURLToPath(import.meta.url)), "..", "..");
const SETTINGS_PATH = ".claude/settings.json";

let failures = 0;

function check(name, condition, detail) {
  if (condition) {
    console.log(`ok   ${name}`);
    return;
  }
  console.log(`FAIL ${name}${detail ? ` — ${detail}` : ""}`);
  failures += 1;
}

const SKILL_NAME = "code-review";
const INVOCATIONS = [SKILL_NAME, `${SKILL_NAME} high main...HEAD`];

function globToRegExp(glob) {
  const escaped = glob.replace(/[.+?^${}()|[\]\\]/g, "\\$&").replace(/\*/g, ".*");
  return new RegExp(`^${escaped}$`);
}

function denyRuleBlocks(rule) {
  const match = rule.match(/^([^(]+?)(?:\((.*)\))?$/);
  if (!match) return false;
  const [, toolPattern, specifier] = match;
  if (!globToRegExp(toolPattern.trim()).test("Skill")) return false;
  if (specifier === undefined) return true;

  const skillPattern = specifier.trim().replace(/^skill\s*:\s*/, "");
  const normalized = skillPattern.endsWith(":*") ? `${skillPattern.slice(0, -2)} *` : skillPattern;
  const pattern = globToRegExp(normalized);
  return INVOCATIONS.some(function matchesInvocation(invocation) {
    return pattern.test(invocation);
  });
}

function codeReviewBlockers(settings) {
  const deny = settings.permissions?.deny ?? [];
  const reasons = deny.filter(denyRuleBlocks).map(function describeRule(rule) {
    return `deny rule ${rule} blocks the Skill tool for ${SKILL_NAME}`;
  });
  if (settings.disableBundledSkills)
    reasons.push("disableBundledSkills turns off every bundled skill");
  if (settings.skillOverrides && Object.hasOwn(settings.skillOverrides, SKILL_NAME)) {
    reasons.push(
      `skillOverrides.${SKILL_NAME} is ${JSON.stringify(settings.skillOverrides[SKILL_NAME])}`,
    );
  }
  return reasons;
}

const BLOCKING = [
  { name: "bare Skill deny", settings: { permissions: { deny: ["Skill"] } } },
  { name: "Skill(*) deny", settings: { permissions: { deny: ["Skill(*)"] } } },
  { name: "every-tool glob deny", settings: { permissions: { deny: ["*"] } } },
  { name: "tool-name glob deny", settings: { permissions: { deny: ["Sk*"] } } },
  { name: "exact deny", settings: { permissions: { deny: ["Skill(code-review)"] } } },
  {
    name: "trailing-space wildcard deny",
    settings: { permissions: { deny: ["Skill(code-review *)"] } },
  },
  { name: "colon wildcard deny", settings: { permissions: { deny: ["Skill(code-review:*)"] } } },
  { name: "prefix glob deny", settings: { permissions: { deny: ["Skill(code*)"] } } },
  {
    name: "skill-parameter deny",
    settings: { permissions: { deny: ["Skill(skill:code-review)"] } },
  },
  { name: "disableBundledSkills", settings: { disableBundledSkills: true } },
  {
    name: "skillOverrides entry",
    settings: { skillOverrides: { "code-review": "user-invocable-only" } },
  },
];

const ALLOWING = [
  { name: "other skill denied", settings: { permissions: { deny: ["Skill(commit)"] } } },
  {
    name: "Bash and Read denies",
    settings: { permissions: { deny: ["Bash(npx*)", "Read(//**/.env)"] } },
  },
  { name: "MCP glob deny", settings: { permissions: { deny: ["mcp__*"] } } },
  { name: "code-review only asked", settings: { permissions: { ask: ["Skill(code-review)"] } } },
  { name: "other skill overridden", settings: { skillOverrides: { commit: "off" } } },
  { name: "disableBundledSkills false", settings: { disableBundledSkills: false } },
];

for (const blocking of BLOCKING) {
  check(`detects ${blocking.name}`, codeReviewBlockers(blocking.settings).length > 0);
}
for (const allowing of ALLOWING) {
  const reasons = codeReviewBlockers(allowing.settings);
  check(`ignores ${allowing.name}`, reasons.length === 0, reasons.join("; "));
}

const settings = JSON.parse(readFileSync(join(repoRoot, SETTINGS_PATH), "utf8"));
const shippedBlockers = codeReviewBlockers(settings);
check(
  `${SETTINGS_PATH} leaves /code-review invocable`,
  shippedBlockers.length === 0,
  shippedBlockers.join("; "),
);

console.log("");
if (failures > 0) {
  console.log(
    `${failures} failed; preflight runs /code-review, so remove what blocks it from ${SETTINGS_PATH} and rerun: pnpm exec node scripts/test/code-review-settings.battery.mjs`,
  );
  process.exit(1);
}
console.log("all code-review settings checks passed");
