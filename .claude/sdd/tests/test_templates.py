import shutil
import unittest
from pathlib import Path

from helpers import TEMPLATES, SddCase, fixture_doc

REAL_DOC = Path(__file__).resolve().parents[1] / "spec-driven-development.md"


class TemplatesSyncTests(SddCase):
    def test_sync_writes_the_four_templates_from_the_appendices(self):
        shutil.rmtree(self.home / "templates")
        code, out, err = self.run_sdd("templates", "sync")
        self.assertEqual(code, 0, err)
        for name, text in TEMPLATES.items():
            self.assertEqual((self.home / "templates" / (name + ".md")).read_text(), text)
            self.assertIn(name + ".md", out)

    def test_check_passes_when_in_sync_and_fails_on_drift(self):
        code, out, err = self.run_sdd("templates", "sync", "--check")
        self.assertEqual(code, 0, out + err)
        self.assertIn("in sync", out)
        drifted = self.home / "templates" / "plan.md"
        drifted.write_text(drifted.read_text().replace("## Rollout", "## Release"))
        code, out, err = self.run_sdd("templates", "sync", "--check")
        self.assertEqual(code, 1)
        self.assertIn("plan.md", out + err)
        self.assertIn("drift", (out + err).lower())
        self.assertIn("## Release", drifted.read_text())

    def test_missing_appendix_is_a_refusal(self):
        doc = self.home / "spec-driven-development.md"
        doc.write_text(doc.read_text().replace("## Appendix C: Tasks template", "## Appendix C: Something else"))
        code, out, err = self.run_sdd("templates", "sync")
        self.assertEqual(code, 1)
        self.assertIn("Appendix C", err)

    def test_sync_against_the_real_document(self):
        if not REAL_DOC.is_file():
            self.skipTest("real document not installed yet")
        (self.home / "spec-driven-development.md").write_text(REAL_DOC.read_text())
        shutil.rmtree(self.home / "templates")
        code, out, err = self.run_sdd("templates", "sync")
        self.assertEqual(code, 0, err)
        for name in TEMPLATES:
            text = (self.home / "templates" / (name + ".md")).read_text()
            self.assertTrue(text.startswith("---\ntitle:"), name)
            self.assertTrue(text.endswith("\n"), name)


class CheckRefsTests(SddCase):
    def skill(self, name, text, filename="SKILL.md"):
        path = self.skills / name / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        return path

    def test_matching_references_pass(self):
        self.skill("sdd-outline", "Read section 7 (Outline) and section 4 (The workflow); the template is Appendix A (Spec template).\n")
        self.skill("sdd-plan", "See section 8 (Plan).\n", "references/notes.md")
        (self.home / "README.md").write_text("Start at section 1 (What spec-driven development is).\n")
        code, out, err = self.run_sdd("check-refs")
        self.assertEqual(code, 0, out + err)
        self.assertIn("5 references", out)

    def test_wrong_number_title_or_missing_section_fails_with_location(self):
        self.skill("sdd-task", "Follow section 9 (Plan).\nThen section 7 (Validate).\nAnd section 99 (Nothing).\nAppendix Z (Nope).\n")
        code, out, err = self.run_sdd("check-refs")
        self.assertEqual(code, 1)
        self.assertIn("sdd-task/SKILL.md:1", out)
        self.assertIn("section 9 (Plan)", out)
        self.assertIn("sdd-task/SKILL.md:2", out)
        self.assertIn("sdd-task/SKILL.md:3", out)
        self.assertIn("sdd-task/SKILL.md:4", out)

    def test_readme_is_checked_and_other_skills_are_not(self):
        self.skill("sdd-review", "section 12 (Validate)\n")
        self.skill("unrelated", "section 3 (Wrong title)\n")
        code, out, err = self.run_sdd("check-refs")
        self.assertEqual(code, 0, out + err)
        (self.home / "README.md").write_text("section 12 (Outline)\n")
        code, out, err = self.run_sdd("check-refs")
        self.assertEqual(code, 1)
        self.assertIn("README.md:1", out)


if __name__ == "__main__":
    unittest.main()
