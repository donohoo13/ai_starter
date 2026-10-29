import unittest

from helpers import BRANCH, SLUG, SddCase, git


class RootTests(SddCase):
    def test_prints_git_top_level_and_sdd_path(self):
        sub = self.repo / "app"
        sub.mkdir()
        code, out, err = self.run_sdd("root", cwd=sub)
        self.assertEqual(code, 0, err)
        self.assertIn("root: %s" % self.repo.resolve(), out)
        self.assertIn("sdd: %s" % (self.repo.resolve() / "docs" / "sdd"), out)

    def test_falls_back_to_cwd_outside_git(self):
        plain = self.repo.parent / "plain"
        plain.mkdir()
        code, out, err = self.run_sdd("root", cwd=plain)
        self.assertEqual(code, 0, err)
        self.assertIn("root: %s" % plain.resolve(), out)


class InitTests(SddCase):
    def test_creates_spec_from_template_with_slug_branch_and_dates(self):
        code, out, err = self.run_sdd("init", SLUG)
        self.assertEqual(code, 0, err)
        fields = self.frontmatter("spec")
        self.assertEqual(fields["slug"], SLUG)
        self.assertEqual(fields["branch"], BRANCH)
        self.assertEqual(fields["status"], "draft")
        self.assertEqual(fields["owner"], "Test User")
        self.assertRegex(fields["created"], r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(fields["created"], fields["updated"])
        self.assertEqual(fields["title"], "Invoice thumbs")
        self.assertIn("# Invoice thumbs\n", self.read_artifact("spec"))
        self.assertIn("## Summary", self.read_artifact("spec"))
        self.assertIn(str(self.folder() / "spec.md"), out)

    def test_branch_flag_overrides_the_current_branch(self):
        code, out, err = self.run_sdd("init", SLUG, "--branch", "feature/other")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.frontmatter("spec")["branch"], "feature/other")

    def test_refuses_when_spec_exists(self):
        self.write_spec()
        before = self.read_artifact("spec")
        code, out, err = self.run_sdd("init", SLUG)
        self.assertEqual(code, 1)
        self.assertIn("already exists", err)
        self.assertEqual(self.read_artifact("spec"), before)

    def test_leaves_the_new_spec_tracked_and_touches_no_ignore_file(self):
        code, out, err = self.run_sdd("init", SLUG)
        self.assertEqual(code, 0, err)
        self.assertIn("tracked by git", out)
        self.assertFalse((self.repo / ".gitignore").exists())
        exclude = self.repo / ".git" / "info" / "exclude"
        self.assertNotIn("sdd", exclude.read_text() if exclude.exists() else "")
        self.assertEqual(git(self.repo, "status", "--porcelain").strip(), "?? docs/")

    def test_works_outside_git(self):
        plain = self.repo.parent / "plain"
        plain.mkdir()
        code, out, err = self.run_sdd("init", SLUG, "--branch", "x", cwd=plain)
        self.assertEqual(code, 0, err)
        self.assertTrue((plain / "docs" / "sdd" / SLUG / "spec.md").exists())

    def test_refuses_without_templates(self):
        (self.home / "templates" / "spec.md").unlink()
        code, out, err = self.run_sdd("init", SLUG)
        self.assertEqual(code, 1)
        self.assertIn("templates sync", err)


class FindTests(SddCase):
    def test_prints_the_slug_whose_branch_matches(self):
        self.write_spec(slug="other", branch="feature/other")
        self.write_spec()
        code, out, err = self.run_sdd("find")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.strip(), SLUG)

    def test_lists_every_slug_and_fails_when_none_matches(self):
        self.write_spec(slug="other", branch="feature/other")
        self.write_spec(slug="another", branch="feature/another")
        code, out, err = self.run_sdd("find")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("another", err)
        self.assertIn("other", err)
        self.assertIn(BRANCH, err)

    def test_fails_when_no_specs_exist(self):
        code, out, err = self.run_sdd("find")
        self.assertEqual(code, 1)
        self.assertIn("no specs", err)


if __name__ == "__main__":
    unittest.main()


class ExecutableTests(SddCase):
    def test_runs_as_a_program(self):
        import subprocess

        from helpers import BIN

        result = subprocess.run([str(BIN), "root"], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("root: ", result.stdout)
        result = subprocess.run([str(BIN), "find"], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("sdd: no specs", result.stderr)
