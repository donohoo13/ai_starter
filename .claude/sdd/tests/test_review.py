import unittest

from helpers import SLUG, SddCase, VALID_REVIEW, git

REVIEW_PATH = "docs/sdd/%s/review.md" % SLUG
NO_PATHS = "0 uncommitted paths, not counting %s" % REVIEW_PATH
REVIEW = VALID_REVIEW % {"slug": SLUG}
FINDING = "- [low] src/invoices/pdf.ts:12: thumbnail size is not capped\n"
DISPOSITION = "  - Disposition: declined, the cap ships as a follow-up\n"


class UncommittedPathsTests(SddCase):
    """`sdd uncommitted` is the clean-tree check of a review whose own report stays uncommitted."""

    def setUp(self):
        super().setUp()
        self.write_spec()
        self.commit_everything()

    def commit_everything(self):
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-q", "-m", "work")

    def make_the_repository_private(self):
        git(self.repo, "rm", "-r", "-q", "--cached", "docs")
        git(self.repo, "commit", "-q", "-m", "untrack the spec files")
        return "git lists nothing under the private spec folder %s" % (self.repo.resolve() / "docs" / "sdd")

    def uncommitted(self, *argv, cwd=None):
        code, out, err = self.run_sdd("uncommitted", *argv, cwd=cwd)
        self.assertEqual(code, 0, out + err)
        return out.splitlines()

    def test_a_clean_tree_reports_zero_paths(self):
        self.assertEqual(self.uncommitted(SLUG), [NO_PATHS])

    def test_a_new_review_is_left_out(self):
        self.write_review()
        self.assertEqual(self.uncommitted(SLUG), [NO_PATHS])

    def test_a_staged_review_is_left_out(self):
        self.write_review()
        git(self.repo, "add", REVIEW_PATH)
        self.assertEqual(self.uncommitted(SLUG), [NO_PATHS])

    def test_a_committed_review_edited_again_is_left_out(self):
        self.write_review()
        self.commit_everything()
        self.write_review(REVIEW.replace("- None yet", "- Thumbnail cap: fixed in abc1234"))
        self.assertEqual(self.uncommitted(SLUG), [NO_PATHS])

    def test_every_other_path_is_listed_one_file_per_line(self):
        self.write_review()
        (self.repo / "README.md").write_text("# changed\n")
        (self.repo / "tests").mkdir()
        (self.repo / "tests" / "pdf.test.ts").write_text("test\n")
        self.assertEqual(
            self.uncommitted(SLUG),
            [" M README.md", "?? tests/pdf.test.ts", "2 uncommitted paths, not counting %s" % REVIEW_PATH],
        )

    def test_the_specs_other_artifacts_are_listed(self):
        self.write_plan()
        self.assertEqual(
            self.uncommitted(SLUG),
            ["?? docs/sdd/%s/plan.md" % SLUG, "1 uncommitted path, not counting %s" % REVIEW_PATH],
        )

    def test_another_specs_review_is_listed(self):
        self.write_review(slug="other-spec")
        self.assertIn("?? docs/sdd/other-spec/review.md", self.uncommitted(SLUG))

    def test_a_private_spec_folder_reports_zero_paths(self):
        nothing_listed = self.make_the_repository_private()
        self.write_review()
        self.write_plan()
        self.assertEqual(self.uncommitted(SLUG), ["0 uncommitted paths; %s" % nothing_listed])

    def test_a_private_spec_folder_is_left_out_of_the_other_paths(self):
        nothing_listed = self.make_the_repository_private()
        self.write_review()
        (self.repo / "README.md").write_text("# changed\n")
        self.assertEqual(self.uncommitted(SLUG), [" M README.md", "1 uncommitted path; %s" % nothing_listed])

    def test_the_slug_defaults_to_the_spec_of_the_current_branch(self):
        self.write_review()
        self.assertEqual(self.uncommitted(), [NO_PATHS])

    def test_the_whole_tree_is_read_from_a_subdirectory(self):
        self.write_review()
        (self.repo / "README.md").write_text("# changed\n")
        (self.repo / "src").mkdir()
        self.assertEqual(self.uncommitted(SLUG, cwd=self.repo / "src")[0], " M README.md")

    def test_a_slug_without_a_working_folder_is_refused(self):
        code, out, err = self.run_sdd("uncommitted", "no-such-spec")
        self.assertEqual(code, 1)
        self.assertIn("no working folder for no-such-spec", err)


class ReviewDispositionTests(SddCase):
    """Every finding in review.md carries a disposition, the record a later session resumes from."""

    def setUp(self):
        super().setUp()
        self.approve_chain("tasks")

    def lint_review(self, text):
        self.write_review(text)
        code, out, err = self.run_sdd("lint", SLUG, "review")
        return code, out

    def with_disposition(self, value):
        """The fixture review with its one finding's disposition line replaced, or removed when `value` is None."""
        self.assertIn(FINDING + DISPOSITION, REVIEW)
        return REVIEW.replace(DISPOSITION, "" if value is None else "  - Disposition: %s\n" % value)

    def test_a_finding_without_a_disposition_fails_lint_at_its_line(self):
        code, out = self.lint_review(self.with_disposition(None))
        self.assertEqual(code, 1)
        self.assertIn("review.md:20: finding has no `- Disposition:` line", out)

    def test_an_unknown_disposition_fails_lint(self):
        code, out = self.lint_review(self.with_disposition("wontfix"))
        self.assertEqual(code, 1)
        self.assertIn("review.md:20: disposition 'wontfix' is not one of open, picked, fixed, declined, deferred", out)

    def test_an_open_finding_fails_lint_as_undecided(self):
        code, out = self.lint_review(self.with_disposition("open"))
        self.assertEqual(code, 1)
        self.assertIn("review.md:20: finding is still open; the user has not decided it", out)

    def test_a_picked_finding_fails_lint_as_unfinished(self):
        code, out = self.lint_review(self.with_disposition("picked"))
        self.assertEqual(code, 1)
        self.assertIn("review.md:20: finding is still picked; its fix is not recorded as fixed", out)

    def test_fixed_declined_and_deferred_findings_pass_lint(self):
        for decided in ("fixed", "declined, the cap ships as a follow-up", "Deferred: tracked in the follow-ups"):
            with self.subTest(disposition=decided):
                code, out = self.lint_review(self.with_disposition(decided))
                self.assertEqual(code, 0, out)

    def test_a_disposition_may_follow_the_lines_that_continue_its_finding(self):
        code, out = self.lint_review(REVIEW.replace(FINDING, FINDING + "  A 40 MB attachment renders at full size.\n"))
        self.assertEqual(code, 0, out)

    def test_a_conformance_gap_and_a_standards_finding_need_dispositions_too(self):
        text = REVIEW.replace(
            "## Correctness findings\n",
            "- FR-001: no test covers a missing attachment file\n\n## Correctness findings\n",
        ).replace(
            "## Standards findings\n- None\n",
            '## Standards findings\n- src/invoices/pdf.ts:3: `x` names nothing. Fails: "Names say what a thing is or does"\n',
        )
        code, out = self.lint_review(text)
        self.assertEqual(code, 1)
        self.assertIn("review.md:19: finding has no `- Disposition:` line", out)
        self.assertIn("review.md:26: finding has no `- Disposition:` line", out)

    def test_only_a_bare_none_bullet_marks_a_section_without_findings(self):
        code, out = self.lint_review(REVIEW.replace("## Standards findings\n- None\n", "## Standards findings\n- None of the new tests names its behavior\n"))
        self.assertEqual(code, 1)
        self.assertIn("review.md:24: finding has no `- Disposition:` line", out)

    def test_bullets_outside_the_findings_sections_need_no_disposition(self):
        code, out = self.lint_review(REVIEW)
        self.assertEqual(code, 0, out)
        self.assertIn("review.md: 0 errors", out)

    def test_a_review_with_an_undecided_finding_cannot_be_accepted(self):
        self.write_review(self.with_disposition("open"))
        code, out, err = self.run_sdd("set-status", SLUG, "review", "accepted")
        self.assertEqual(code, 1)
        self.assertIn("finding is still open", out)
        self.assertEqual(self.frontmatter("review")["status"], "open")


if __name__ == "__main__":
    unittest.main()
