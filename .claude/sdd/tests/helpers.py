"""Shared fixtures for the sdd helper tests.

Each test case gets a throwaway git repo on a feature branch, a temporary SDD
home (document plus templates) selected through SDD_HOME, and an in-process
runner for the CLI.
"""
import contextlib
import importlib.machinery
import importlib.util
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

BIN = Path(__file__).resolve().parents[1] / "bin" / "sdd"

SLUG = "invoice-thumbs"
BRANCH = "feature/invoice-thumbs"


def load_cli():
    loader = importlib.machinery.SourceFileLoader("sdd_cli", str(BIN))
    spec = importlib.util.spec_from_loader("sdd_cli", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


@contextlib.contextmanager
def chdir(path):
    previous = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, check=True, capture_output=True, text=True
    ).stdout


SPEC_TEMPLATE = """---
title: <Feature name>
slug: <slug>
branch: <feature branch>
status: draft
owner: <person>
created: YYYY-MM-DD
updated: YYYY-MM-DD
approved_hash:
description: <1–2 sentences; see section 7>
---

# <Feature name>

## Summary
<One paragraph, 5–7 sentences; see section 7.>

## Problem and context
<Current state, who is affected and how, and evidence (metrics, incidents, user reports) with sources.>

## Goals
- G1: <outcome, measurable where possible>

## Non-goals
- <out of scope, with the reason if it isn't obvious>

## User scenarios
### P1: <story title>
As a <user>, I want <capability> so that <outcome>.
Independent test: <how this slice is verified on its own>
- Given <context>, when <action>, then <result>.

### P2: <story title>
...

## Requirements
### Functional
- FR-001: When <trigger>, the system shall <behavior>.
  - Acceptance: Given <context>, when <action>, then <result>.

### Non-functional
- NFR-001: <metric, threshold and conditions>

## Invariants
- INV-001: The system shall never <behavior>.

## Edge cases and failure behavior
- <case>: <expected behavior>

## Existing behavior
<What exists today that this change builds on. These are not new requirements; do not re-implement them.>

## Assumptions
- A-001: <assumption>. Accepted by <person>.

## Open questions
- [NEEDS CLARIFICATION: <specific question>]

## Glossary
| Term | Meaning |
| --- | --- |

## Changelog
- YYYY-MM-DD: <change and reason>
"""

PLAN_TEMPLATE = """---
title: <Feature name> plan
slug: <slug>
status: draft
updated: YYYY-MM-DD
based_on:
approved_hash:
---

# <Feature name> plan

## Approach
<A short summary of the technical approach.>

## Technical context
- Stack and versions:
- Dependencies:
- Platform limits:

## Principles check
| Principle | Pass/Fail | Notes |
| --- | --- | --- |

### Deviations
- <principle>: <why the deviation is needed, and the simpler option rejected>

## Architecture
<Components, what each is responsible for, and the boundaries between them.>

## Data model
<Entities, fields, relationships, migrations.>

## Interfaces and contracts
<APIs, events, schemas, error formats, handoff contracts.>

## Affected code
- Change: <path>, <what changes>
- Create: <path>, <purpose>
- Pattern to follow: <path to an existing example>

## Seams and test strategy
### P1: <slice title>
- Seam: <boundary the tests run at, and why it's the repo's established seam for this code>
- Test types: <the repo's test types used here>
- Acceptance criteria to tests: <criterion → test>

## Alternatives considered
- <option>: <why rejected>

## Trade-offs and risks
- <what the team takes on>: <mitigation>

## Rollout
1. <step that ships on its own>. Rollback: <how>

## Traceability
| Requirement | Components | Seam | Tests |
| --- | --- | --- | --- |

## Research notes
- <verified fact>: <source>
"""

TASKS_TEMPLATE = """---
title: <Feature name> tasks
slug: <slug>
status: draft
updated: YYYY-MM-DD
based_on:
approved_hash:
---

# <Feature name> tasks

## P1: <slice title>
- [ ] T001 <one observable behavior>
  - Requirements: FR-001
  - Seam: <from the plan>
  - Files: <paths>
  - Done when: <command or check that passes or fails>
- [ ] T002 [P] <one observable behavior>
  - Requirements: FR-002
  - Seam: <from the plan>
  - Files: <paths>
  - Depends on: T001
  - Done when: <check>
- [ ] P1 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## P2: <slice title>
...

## Verified elsewhere
- <ID>: <how it is verified>. Decided by <person>.

## Follow-ups (out of scope)
- <discovery to handle later>
"""

REVIEW_TEMPLATE = """---
title: <Feature name> review
slug: <slug>
status: open
base: <base branch>
range: <base>..<head>
effort: <effort>
max_findings: <n>
updated: YYYY-MM-DD
---

# <Feature name> review

## Spec conformance
| Requirement | Met | Evidence |
| --- | --- | --- |

## Correctness findings
- [<severity>] <file:line>: <finding>

## Standards findings
- <file:line>: <finding>. Fails: "<standards line>"

## Reads well
- <note>

## Rejected findings
- <finding>: <why rejected, with evidence>

## Fixes
- <finding> → <fix, test, commit>

## PR description draft
### Summary
<One paragraph; see section 7.>
### What changed
- <change>
### How it was verified
- <command and result>
### Decisions and follow-ups
- <item>
"""

TEMPLATES = {
    "spec": SPEC_TEMPLATE,
    "plan": PLAN_TEMPLATE,
    "tasks": TASKS_TEMPLATE,
    "review": REVIEW_TEMPLATE,
}


def fixture_doc(templates=None):
    """A small stand-in for the SDD document: numbered headings plus the four appendices."""
    templates = templates or TEMPLATES
    headings = [
        "## 1. What spec-driven development is",
        "## 4. The workflow",
        "## 7. Phase 1: Outline (`sdd-outline`)",
        "## 8. Phase 2: Plan (`sdd-plan`)",
        "## 9. Phase 3: Tasks (`sdd-task`)",
        "## 10. Phase 4: Implement (`sdd-implement`)",
        "## 11. TDD discipline (`tdd`)",
        "## 12. Phase 5: Validate (`sdd-review`)",
    ]
    body = "# Spec-Driven Development\n\n" + "\n\nText.\n\n".join(headings) + "\n\nText.\n\n"
    appendices = [
        ("A", "Spec template", templates["spec"]),
        ("B", "Plan template", templates["plan"]),
        ("C", "Tasks template", templates["tasks"]),
        ("D", "Review report template", templates["review"]),
    ]
    for letter, title, text in appendices:
        body += "## Appendix %s: %s\n\n````markdown\n%s````\n\n" % (letter, title, text)
    return body


VALID_SPEC = """---
title: Invoice thumbnails
slug: %(slug)s
branch: %(branch)s
status: draft
owner: Test User
created: 2026-10-29
updated: 2026-10-29
approved_hash:
description: Adds thumbnail rendering to the invoice PDF so reviewers see every attachment without opening it. The result is faster reviews and fewer blank pages.
---

# Invoice thumbnails

## Summary
The invoice PDF lists attachments by filename only. Reviewers cannot see a attachment without opening it. An invoice with 300 attachments takes an hour to review. Finance approves invoices a day late as a result. The PDF generator will render a thumbnail for each attachment with pdf-lib. Thumbnails let reviewers judge a attachment from the list. The finished PDF shows every attachment inline.

## Problem and context
Reviewers open each attachment by hand. Source: support tickets from 2026-09.

## Goals
- G1: Reviews finish in under 10 minutes.

## Non-goals
- Editing attachments.

## Requirements
### Functional
- FR-001: When a reviewer opens the invoice PDF, the system shall render a thumbnail for each attachment.
  - Acceptance: Given an invoice with 300 attachments, when the PDF renders, then every thumbnail appears within 10 seconds.

### Non-functional
- NFR-001: p95 render time under 10 s for 300 attachments.

## Invariants
- INV-001: The system shall never show a raw exception to a user.

## Edge cases and failure behavior
- Missing attachment file: a placeholder renders and the invoice still opens.
"""

VALID_PLAN = """---
title: Invoice thumbnails plan
slug: %(slug)s
status: draft
updated: 2026-10-29
based_on: %(based_on)s
approved_hash:
---

# Invoice thumbnails plan

## Approach
Render thumbnails in the existing PDF generator.

## Technical context
- Stack and versions: Node 24
- Dependencies: pdf-lib 1.17
- Platform limits: 50 MB PDF

## Principles check
| Principle | Pass/Fail | Notes |
| --- | --- | --- |
| Test-first | Pass | |

### Deviations
- None

## Architecture
One service renders thumbnails.

## Data model
No changes.

## Interfaces and contracts
GET /invoices/:id.pdf unchanged.

## Affected code
- Change: src/invoices/pdf.ts, add thumbnails
- Pattern to follow: src/invoices/csv.ts

## Seams and test strategy
### P1: Thumbnails in the PDF
- Seam: request test on GET /invoices/:id.pdf
- Test types: supertest request test
- Acceptance criteria to tests: FR-001 acceptance, tests/invoices/pdf.test.ts

## Alternatives considered
- Client-side rendering: rejected, no browser in the PDF path

## Trade-offs and risks
- Render time grows with attachment count: cap thumbnail size

## Rollout
1. Ship without a flag. Rollback: revert

## Traceability
| Requirement | Components | Seam | Tests |
| --- | --- | --- | --- |
| FR-001 | InvoicePdf | request test on GET /invoices/:id.pdf | tests/invoices/pdf.test.ts |
| NFR-001 | InvoicePdf | request test on GET /invoices/:id.pdf | tests/invoices/pdf.test.ts |
| INV-001 | InvoicePdf | service test on InvoicePdf | tests/invoices/pdf-placeholder.test.ts |

## Research notes
- pdf-lib embeds images: https://pdf-lib.js.org
"""

VALID_TASKS = """---
title: Invoice thumbnails tasks
slug: %(slug)s
status: draft
updated: 2026-10-29
based_on: %(based_on)s
approved_hash:
---

# Invoice thumbnails tasks

## P1: Thumbnails in the PDF
- [ ] T001 Render a thumbnail for each attachment in the invoice PDF
  - Requirements: FR-001, NFR-001
  - Seam: request test on GET /invoices/:id.pdf
  - Files: src/invoices/pdf.ts, tests/invoices/pdf.test.ts
  - Done when: `pnpm test -- tests/invoices/pdf.test.ts` passes
- [ ] T002 [P] Render a placeholder when a attachment file is missing
  - Requirements: FR-001, INV-001
  - Seam: service test on InvoicePdf
  - Files: src/invoices/pdf-placeholder.ts, tests/invoices/pdf-placeholder.test.ts
  - Done when: `pnpm test -- tests/invoices/pdf-placeholder.test.ts` passes
- [ ] P1 close: full suite green, changes staged by explicit path, commit message proposed, user committed

## Verified elsewhere
- None

## Follow-ups (out of scope)
- None yet
"""

TASKS_VERIFIED_ELSEWHERE = VALID_TASKS.replace(
    "  - Requirements: FR-001, NFR-001", "  - Requirements: FR-001"
).replace(
    "## Verified elsewhere\n- None",
    "## Verified elsewhere\n- NFR-001: measured by the load test in CI. Decided by Test User.",
)

VALID_REVIEW = """---
title: Invoice thumbnails review
slug: %(slug)s
status: open
base: staging
range: staging..HEAD
effort: high
max_findings: 3
updated: 2026-10-29
---

# Invoice thumbnails review

## Spec conformance
| Requirement | Met | Evidence |
| --- | --- | --- |
| FR-001 | Yes | tests/invoices/pdf.test.ts renders every thumbnail |

## Correctness findings
- [low] src/invoices/pdf.ts:12: thumbnail size is not capped

## Standards findings
- None

## Reads well
- InvoicePdf reads top to bottom

## Rejected findings
- None

## Fixes
- None yet

## PR description draft
### Summary
Adds thumbnails to the invoice PDF so reviewers judge attachments from the list. The result is faster reviews.
### What changed
- InvoicePdf renders a thumbnail per attachment
### How it was verified
- `pnpm test` green, 412 tests
### Decisions and follow-ups
- None
"""


class SddCase(unittest.TestCase):
    """A temp SDD home, a temp git repo on a feature branch, and an in-process CLI runner."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        base = Path(self.tmp.name)
        self.home = base / "sdd"
        (self.home / "templates").mkdir(parents=True)
        (self.home / "spec-driven-development.md").write_text(fixture_doc())
        for name, text in TEMPLATES.items():
            (self.home / "templates" / (name + ".md")).write_text(text)
        self.skills = base / "skills"
        self.skills.mkdir()
        self.repo = base / "repo"
        self.repo.mkdir()
        self._saved_env = dict(os.environ)
        self.addCleanup(self._restore_env)
        os.environ["SDD_HOME"] = str(self.home)
        os.environ["GIT_CONFIG_GLOBAL"] = os.devnull
        os.environ["GIT_CONFIG_SYSTEM"] = os.devnull
        git(self.repo, "init", "-q", "-b", "main")
        git(self.repo, "config", "user.email", "test@example.com")
        git(self.repo, "config", "user.name", "Test User")
        (self.repo / "README.md").write_text("# repo\n")
        git(self.repo, "add", "README.md")
        git(self.repo, "commit", "-q", "-m", "init")
        git(self.repo, "switch", "-q", "-c", BRANCH)
        self.cli = load_cli()

    def _restore_env(self):
        os.environ.clear()
        os.environ.update(self._saved_env)

    def run_sdd(self, *argv, cwd=None):
        out, err = io.StringIO(), io.StringIO()
        with chdir(cwd or self.repo), contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = self.cli.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def folder(self, slug=SLUG):
        return self.repo / "docs" / "sdd" / slug

    def write_artifact(self, name, text, slug=SLUG):
        path = self.folder(slug) / (name + ".md")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def read_artifact(self, name, slug=SLUG):
        return (self.folder(slug) / (name + ".md")).read_text()

    def write_spec(self, text=None, slug=SLUG, branch=BRANCH):
        return self.write_artifact("spec", text or VALID_SPEC % {"slug": slug, "branch": branch}, slug)

    def write_plan(self, based_on="", slug=SLUG):
        return self.write_artifact("plan", VALID_PLAN % {"slug": slug, "based_on": based_on}, slug)

    def write_tasks(self, based_on="", slug=SLUG, text=None):
        return self.write_artifact("tasks", text or VALID_TASKS % {"slug": slug, "based_on": based_on}, slug)

    def write_review(self, text=None, slug=SLUG):
        return self.write_artifact("review", text or VALID_REVIEW % {"slug": slug}, slug)

    def approve_chain(self, upto="tasks"):
        """Write and approve spec, then plan, then tasks as far as `upto`."""
        self.write_spec()
        code, out, err = self.run_sdd("approve", SLUG, "spec")
        assert code == 0, err
        if upto == "spec":
            return
        self.write_plan()
        code, out, err = self.run_sdd("approve", SLUG, "plan")
        assert code == 0, err
        if upto == "plan":
            return
        self.write_tasks()
        code, out, err = self.run_sdd("approve", SLUG, "tasks")
        assert code == 0, err

    def frontmatter(self, name, slug=SLUG):
        return self.cli.parse_frontmatter(self.read_artifact(name, slug))[0]

    def mark_approved(self, name, based_on=None, slug=SLUG):
        """Set an artifact approved by hand, without going through `sdd approve`."""
        text = self.read_artifact(name, slug)
        updates = {"status": "approved", "approved_hash": self.cli.content_hash(text)}
        if based_on is not None:
            updates["based_on"] = based_on
        self.write_artifact(name, self.cli.set_frontmatter(text, updates), slug)
        return updates["approved_hash"]

    def set_fields(self, name, slug=SLUG, **updates):
        text = self.read_artifact(name, slug)
        self.write_artifact(name, self.cli.set_frontmatter(text, updates), slug)

    def status_json(self, slug=SLUG):
        code, out, err = self.run_sdd("status", slug, "--json")
        assert code == 0, err
        return json.loads(out)
