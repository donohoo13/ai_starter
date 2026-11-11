import os
import shutil
import unittest
from pathlib import Path

from helpers import BRANCH, SLUG, VALID_SPEC, SddCase, git

SPEC = VALID_SPEC % {"slug": SLUG, "branch": BRANCH}
SPEC_WITHOUT_BASE = SPEC.replace("base: main\n", "")


class BaseCase(SddCase):
    """The fixture repo has no remote, so git cannot tell a default branch until a test gives it one."""

    def record_origin_head(self, name):
        git(self.repo, "update-ref", "refs/remotes/origin/%s" % name, "HEAD")
        git(self.repo, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/%s" % name)

    def add_origin_with_unrecorded_default(self, name):
        origin = Path(self.tmp.name) / "origin.git"
        git(self.repo, "init", "-q", "--bare", "-b", name, str(origin))
        git(self.repo, "remote", "add", "origin", str(origin))
        git(self.repo, "push", "-q", "origin", "main:%s" % name)

    def make_the_remote_answer_late(self):
        """Put a git on PATH whose ls-remote answers only after the helper's shortened patience has run out."""
        shim = Path(self.tmp.name) / "bin" / "git"
        shim.parent.mkdir()
        late_answer = "sleep 2; printf 'ref: refs/heads/staging\\tHEAD\\n'; exit 0"
        shim.write_text('#!/bin/sh\ncase "$1" in ls-remote) %s ;; esac\nexec "%s" "$@"\n' % (late_answer, shutil.which("git")))
        shim.chmod(0o755)
        os.environ["PATH"] = "%s%s%s" % (shim.parent, os.pathsep, os.environ["PATH"])
        self.cli.REMOTE_TIMEOUT_SECONDS = 0.2

    def write_spec_with_base(self, base):
        self.write_spec(SPEC.replace("base: main\n", "base: %s\n" % base))


class InitBaseTests(BaseCase):
    def test_records_the_remote_default_whichever_branch_outline_starts_on(self):
        self.record_origin_head("staging")
        code, out, err = self.run_sdd("init", "from-feature")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.frontmatter("spec", slug="from-feature")["base"], "staging")
        git(self.repo, "switch", "-q", "main")
        code, out, err = self.run_sdd("init", SLUG, "--branch", BRANCH)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.frontmatter("spec")["branch"], BRANCH)
        self.assertEqual(self.frontmatter("spec")["base"], "staging")
        self.assertIn("base: staging, from origin/HEAD", out)

    def test_asks_the_remote_when_its_default_is_not_recorded_locally(self):
        self.add_origin_with_unrecorded_default("staging")
        code, out, err = self.run_sdd("init", SLUG)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.frontmatter("spec")["base"], "staging")
        self.assertIn("base: staging, from the remote", out)

    def test_a_remote_that_answers_too_late_counts_as_git_not_telling(self):
        self.add_origin_with_unrecorded_default("staging")
        self.make_the_remote_answer_late()
        code, out, err = self.run_sdd("init", SLUG)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.frontmatter("spec")["base"], "")
        self.assertIn("ask the user", out)

    def test_the_base_flag_overrides_the_remote_default(self):
        self.record_origin_head("main")
        code, out, err = self.run_sdd("init", SLUG, "--base", "release/2")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.frontmatter("spec")["base"], "release/2")

    def test_records_no_base_and_says_to_ask_the_user_when_git_cannot_tell(self):
        code, out, err = self.run_sdd("init", SLUG)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.frontmatter("spec")["base"], "")
        self.assertNotIn("<base branch>", self.read_artifact("spec"))
        self.assertIn("ask the user", out)
        self.assertIn("sdd set-base %s <branch>" % SLUG, out)


class StatusBaseTests(BaseCase):
    def test_status_reports_the_recorded_base(self):
        self.write_spec_with_base("staging")
        self.assertEqual(self.status_json()["base"], "staging")
        code, out, err = self.run_sdd("status", SLUG)
        self.assertEqual(code, 0, err)
        self.assertIn("base: staging\n", out)

    def test_status_names_the_command_that_records_a_missing_base(self):
        self.write_spec(SPEC_WITHOUT_BASE)
        self.assertIsNone(self.status_json()["base"])
        code, out, err = self.run_sdd("status", SLUG)
        self.assertEqual(code, 0, err)
        self.assertIn("base: ?", out)
        self.assertIn("sdd set-base %s" % SLUG, out)


class BaseCommandTests(BaseCase):
    def test_prints_the_base_the_named_spec_records(self):
        self.write_spec_with_base("staging")
        code, out, err = self.run_sdd("base", SLUG)
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines()[0], "base: staging")
        self.assertIn("source: spec %s" % SLUG, out)

    def test_the_recorded_base_wins_over_a_remote_default_that_names_another_branch(self):
        self.record_origin_head("main")
        self.write_spec_with_base("release/2")
        code, out, err = self.run_sdd("base")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines()[0], "base: release/2")

    def test_detects_for_a_spec_that_records_no_base_and_names_the_command_that_records_it(self):
        self.record_origin_head("staging")
        self.write_spec(SPEC_WITHOUT_BASE)
        for argv in (("base", SLUG), ("base",)):
            code, out, err = self.run_sdd(*argv)
            self.assertEqual(code, 0, err)
            self.assertEqual(out.splitlines()[0], "base: staging")
            self.assertIn("detected from origin/HEAD", out)
            self.assertIn("sdd set-base %s" % SLUG, out)

    def test_detects_when_no_spec_matches_the_current_branch(self):
        self.record_origin_head("trunk")
        self.write_spec(slug="other", branch="feature/other")
        code, out, err = self.run_sdd("base")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines()[0], "base: trunk")
        self.assertIn("source: detected from origin/HEAD", out)

    def test_asks_the_remote_when_its_default_is_not_recorded_locally(self):
        self.add_origin_with_unrecorded_default("trunk")
        code, out, err = self.run_sdd("base")
        self.assertEqual(code, 0, err)
        self.assertEqual(out.splitlines()[0], "base: trunk")
        self.assertIn("source: detected from the remote", out)

    def test_refuses_and_says_to_ask_the_user_when_git_cannot_tell(self):
        code, out, err = self.run_sdd("base")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("ask the user", err)
        self.write_spec(SPEC_WITHOUT_BASE)
        code, out, err = self.run_sdd("base", SLUG)
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("ask the user", err)
        self.assertIn("sdd set-base %s <branch>" % SLUG, err)

    def test_refuses_a_slug_with_no_spec(self):
        code, out, err = self.run_sdd("base", "missing")
        self.assertEqual(code, 1)
        self.assertIn("spec.md is missing for missing", err)


class SetBaseTests(BaseCase):
    def test_records_a_named_base_on_an_approved_spec_without_staling_it(self):
        self.write_spec(SPEC_WITHOUT_BASE)
        self.mark_approved("spec")
        code, out, err = self.run_sdd("set-base", SLUG, "staging")
        self.assertEqual(code, 0, err)
        self.assertIn("staging", out)
        data = self.status_json()
        self.assertEqual(data["base"], "staging")
        self.assertFalse(data["artifacts"]["spec"]["changed"])
        self.assertEqual(data["phase"], "3. Plan")

    def test_replaces_a_recorded_base(self):
        self.write_spec()
        code, out, err = self.run_sdd("set-base", SLUG, "staging")
        self.assertEqual(code, 0, err)
        self.assertEqual(self.frontmatter("spec")["base"], "staging")
        self.assertEqual(self.read_artifact("spec").count("\nbase:"), 1)

    def test_without_a_branch_it_records_the_remote_default(self):
        self.record_origin_head("staging")
        self.write_spec(SPEC_WITHOUT_BASE)
        code, out, err = self.run_sdd("set-base", SLUG)
        self.assertEqual(code, 0, err)
        self.assertEqual(self.frontmatter("spec")["base"], "staging")
        self.assertIn("origin/HEAD", out)

    def test_without_a_branch_it_refuses_when_git_cannot_tell(self):
        self.write_spec(SPEC_WITHOUT_BASE)
        code, out, err = self.run_sdd("set-base", SLUG)
        self.assertEqual(code, 1)
        self.assertIn("ask the user", err)
        self.assertEqual(self.read_artifact("spec"), SPEC_WITHOUT_BASE)

    def test_refuses_a_missing_spec_and_an_empty_base(self):
        code, out, err = self.run_sdd("set-base", SLUG, "staging")
        self.assertEqual(code, 1)
        self.assertIn("spec.md is missing", err)
        self.write_spec()
        code, out, err = self.run_sdd("set-base", SLUG, " ")
        self.assertEqual(code, 1)
        self.assertEqual(self.frontmatter("spec")["base"], "main")


class LintBaseTests(BaseCase):
    def test_a_spec_with_no_base_fails_lint_and_cannot_be_approved(self):
        for text in (SPEC_WITHOUT_BASE, SPEC.replace("base: main\n", "base:\n")):
            self.write_spec(text)
            code, out, err = self.run_sdd("lint", SLUG, "spec")
            self.assertEqual(code, 1)
            self.assertIn("no base branch recorded", out)
            self.assertIn("sdd set-base %s" % SLUG, out)
            code, out, err = self.run_sdd("approve", SLUG, "spec")
            self.assertEqual(code, 1)
            self.assertEqual(self.frontmatter("spec")["status"], "draft")

    def test_a_spec_from_init_with_a_detected_base_passes_the_base_check(self):
        self.record_origin_head("main")
        code, out, err = self.run_sdd("init", SLUG)
        self.assertEqual(code, 0, err)
        code, out, err = self.run_sdd("lint", SLUG, "spec")
        self.assertNotIn("no base branch recorded", out)


if __name__ == "__main__":
    unittest.main()
