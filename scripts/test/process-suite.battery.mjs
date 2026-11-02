#!/usr/bin/env node
// Asserts the structural rules of the skill and agent suite that prose alone cannot hold, such as which agent a skill preloads and which skill may dispatch an agent.

import { execFileSync } from "node:child_process";
import { readdirSync, readFileSync } from "node:fs";
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
  check(
    `${path} pins a model`,
    Boolean(scalarValue(frontmatter, "model")),
    "set model: so every slice builds on the same model; which one is the project's choice",
  );
}

function checkRenderCheckIsUserOnly() {
  const path = ".claude/skills/render-check/SKILL.md";
  const frontmatter = frontmatterOf(readRepoFile(path));
  check(`${path} exists with frontmatter`, frontmatter !== null);
  if (frontmatter === null) return;
  check(
    `${path} is user-only`,
    scalarValue(frontmatter, "disable-model-invocation") === "true",
    "render checks are slow and token-heavy, so only the user starts one",
  );
}

function suiteFiles() {
  const skills = readdirSync(join(process.cwd(), ".claude/skills"), { withFileTypes: true })
    .filter(function isSkillDir(entry) {
      return entry.isDirectory();
    })
    .map(function skillFile(entry) {
      return `.claude/skills/${entry.name}/SKILL.md`;
    });
  const agents = readdirSync(join(process.cwd(), ".claude/agents"))
    .filter(function isMarkdown(name) {
      return name.endsWith(".md");
    })
    .map(function agentFile(name) {
      return `.claude/agents/${name}`;
    });
  return [...skills, ...agents].filter(function exists(path) {
    return readRepoFile(path) !== null;
  });
}

function namesWord(path, word) {
  return new RegExp(`(^|[^\\w-])${word}([^\\w-]|$)`).test(readRepoFile(path));
}

function checkRenderCheckerHasOneDispatcher() {
  const allowed = [".claude/skills/render-check/SKILL.md", ".claude/agents/render-checker.md"];
  const others = suiteFiles().filter(function namesRenderChecker(path) {
    return !allowed.includes(path) && namesWord(path, "render-checker");
  });
  check(
    "only render-check dispatches render-checker",
    others.length === 0,
    `also named in ${others.join(", ")}`,
  );
}

function checkNoOrphanAgents() {
  const files = suiteFiles();
  const skills = files.filter(function isSkill(path) {
    return path.startsWith(".claude/skills/");
  });
  const agents = files
    .filter(function isAgent(path) {
      return path.startsWith(".claude/agents/");
    })
    .map(function agentName(path) {
      return path.slice(".claude/agents/".length, -".md".length);
    });
  for (const agent of agents) {
    check(
      `agent ${agent} is named by a skill`,
      skills.some(function namesAgent(path) {
        return namesWord(path, agent);
      }),
      "an agent no skill dispatches is dead; delete it or name its dispatcher",
    );
  }
}

const REMOVED_NAMES = [
  "refiner",
  "code-reviewer",
  "template-sync",
  "template-feedback",
  "implement-spec",
  "run-skill-generator",
];
const REMOVED_ENGLISH_WORDS = ["refine", "builder"];

function removedNamePattern() {
  const notNameChar = "[^[:alnum:]_-]";
  const asWordAnywhere = `(^|${notNameChar})(${REMOVED_NAMES.join("|")})(${notNameChar}|$)`;
  const opensCodeSlashOrBold = "[`/*]";
  const closesCodeBoldLinkOrWord = "([`*\\] ]|$)";
  const asCodeCommandOrBold = `${opensCodeSlashOrBold}(${REMOVED_ENGLISH_WORDS.join("|")})${closesCodeBoldLinkOrWord}`;
  return `${asWordAnywhere}|${asCodeCommandOrBold}`;
}

function checkNoRemovedNames() {
  // Spec folders and the changelog record history, so naming a removed skill there is correct.
  const excluded = [":!docs/sdd", ":!CHANGELOG.md", ":!scripts/test/process-suite.battery.mjs"];
  let matches = "";
  try {
    matches = execFileSync("git", ["grep", "-nE", removedNamePattern(), "--", ".", ...excluded], {
      encoding: "utf8",
    });
  } catch (error) {
    if (error.status !== 1) throw error;
  }
  const lines = matches.split("\n").filter(Boolean);
  check(
    "no tracked file names a removed skill or agent",
    lines.length === 0,
    `${lines.length} found:\n  ${lines.join("\n  ")}`,
  );
}

checkImplementer();
checkRenderCheckIsUserOnly();
checkRenderCheckerHasOneDispatcher();
checkNoOrphanAgents();
checkNoRemovedNames();

console.log("");
if (failures > 0) {
  console.log(
    `${failures} failed; run from the repo root: pnpm exec node scripts/test/process-suite.battery.mjs`,
  );
  process.exit(1);
}
console.log("all process-suite checks passed");
