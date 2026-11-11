"""The spec's branch and its worktree.

`sdd worktree <branch>` makes both before any artifact is written, so a shared
repository's approvals are committed on the feature branch and never on the base.
The origins and second clones here are real ones, made by `git init --bare` and `git clone`.
"""
import os
import shutil
import subprocess
import unittest

from helpers import BRANCH, SLUG, VALID_SPEC, SddCase, git

NEW_BRANCH = "feature/new-thing"
NEW_SLUG = "new-thing"
EXCLUDE_LINE = "/.claude/worktrees/"


def status_lines(checkout):
    return git(checkout, "status", "--porcelain", "--untracked-files=all").splitlines()


def commit_of(checkout, ref="HEAD"):
    return git(checkout, "rev-parse", ref).strip()


def branch_of(checkout):
    return git(checkout, "branch", "--show-current").strip()


def upstream_of(checkout):
    """The branch the checkout's branch tracks, or "" when it tracks none."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "@{upstream}"], cwd=checkout, capture_output=True, text=True
    )
    return result.stdout.strip() if result.returncode == 0 else ""


class WorktreeCase(SddCase):
    """The main checkout sits on `main`, the default branch of an origin it has pushed to."""

    def setUp(self):
        super().setUp()
        for key in ("GIT_AUTHOR_NAME", "GIT_COMMITTER_NAME"):
            os.environ[key] = "Test User"
        for key in ("GIT_AUTHOR_EMAIL", "GIT_COMMITTER_EMAIL"):
            os.environ[key] = "test@example.com"
        self.repo = self.repo.resolve()
        self.origin = self.repo.parent / "origin.git"
        git(self.repo, "init", "-q", "--bare", "-b", "main", str(self.origin))
        git(self.repo, "remote", "add", "origin", str(self.origin))
        git(self.repo, "push", "-q", "origin", "main")
        git(self.repo, "remote", "set-head", "origin", "main")
        git(self.repo, "switch", "-q", "main")

    def tree(self, branch=NEW_BRANCH):
        """Where a worktree lands when no path is named."""
        return self.repo / ".claude" / "worktrees" / branch.replace("/", "-")

    def worktree(self, *argv, cwd=None):
        code, out, err = self.run_sdd("worktree", *argv, cwd=cwd)
        self.assertEqual(code, 0, out + err)
        return out, err

    def another_clone(self):
        clone = self.repo.parent / "another-machine"
        git(self.repo, "clone", "-q", str(self.origin), str(clone))
        return clone

    def push_spec_from_another_clone(self, slug=NEW_SLUG, branch=NEW_BRANCH):
        """Another machine outlines a spec on its own branch and pushes it; returns the pushed commit."""
        clone = self.another_clone()
        git(clone, "switch", "-q", "-c", branch)
        spec = clone / "docs" / "sdd" / slug / "spec.md"
        spec.parent.mkdir(parents=True)
        spec.write_text(VALID_SPEC % {"slug": slug, "branch": branch})
        git(clone, "add", "docs/sdd/%s/spec.md" % slug)
        git(clone, "commit", "-q", "-m", "Approve the spec")
        git(clone, "push", "-q", "-u", "origin", branch)
        return commit_of(clone)

    def init_in(self, checkout, slug=NEW_SLUG):
        code, out, err = self.run_sdd("init", slug, cwd=checkout)
        self.assertEqual(code, 0, out + err)


class NewBranchTests(WorktreeCase):
    def test_cuts_the_branch_from_the_remote_base_into_a_worktree_inside_the_main_checkout(self):
        out, err = self.worktree(NEW_BRANCH)
        self.assertEqual(out.splitlines()[0], "worktree: %s" % self.tree())
        self.assertIn("branch: %s" % NEW_BRANCH, out)
        self.assertIn("cut from origin/main", out)
        self.assertEqual(branch_of(self.tree()), NEW_BRANCH)
        self.assertEqual(commit_of(self.tree()), commit_of(self.repo, "origin/main"))
        self.assertEqual(branch_of(self.repo), "main")

    def test_the_new_branch_tracks_nothing_so_a_push_cannot_reach_the_base(self):
        self.worktree(NEW_BRANCH)
        self.assertEqual(upstream_of(self.tree()), "")

    def test_a_base_that_moved_locally_does_not_reach_the_new_branch(self):
        (self.repo / "stray.txt").write_text("committed on the local base by mistake\n")
        git(self.repo, "add", "stray.txt")
        git(self.repo, "commit", "-q", "-m", "stray")
        self.worktree(NEW_BRANCH)
        self.assertEqual(commit_of(self.tree()), commit_of(self.repo, "origin/main"))
        self.assertFalse((self.tree() / "stray.txt").exists())

    def test_a_base_the_remote_moved_is_fetched_before_the_cut(self):
        clone = self.another_clone()
        (clone / "newer.txt").write_text("merged on the remote since this clone last fetched\n")
        git(clone, "add", "newer.txt")
        git(clone, "commit", "-q", "-m", "newer")
        git(clone, "push", "-q", "origin", "main")
        self.worktree(NEW_BRANCH)
        self.assertEqual(commit_of(self.tree()), commit_of(clone))

    def test_the_base_flag_names_another_base(self):
        git(self.repo, "switch", "-q", "-c", "release/2")
        (self.repo / "release.txt").write_text("only on the release branch\n")
        git(self.repo, "add", "release.txt")
        git(self.repo, "commit", "-q", "-m", "release")
        git(self.repo, "push", "-q", "origin", "release/2")
        git(self.repo, "switch", "-q", "main")
        out, err = self.worktree(NEW_BRANCH, "--base", "release/2")
        self.assertIn("cut from origin/release/2", out)
        self.assertTrue((self.tree() / "release.txt").is_file())

    def test_the_path_flag_places_the_worktree_and_leaves_the_exclude_file_alone(self):
        elsewhere = self.repo.parent / "trees" / "new-thing"
        out, err = self.worktree(NEW_BRANCH, "--path", str(elsewhere))
        self.assertEqual(out.splitlines()[0], "worktree: %s" % elsewhere)
        self.assertEqual(branch_of(elsewhere), NEW_BRANCH)
        self.assertFalse(self.tree().exists())
        self.assertNotIn(EXCLUDE_LINE, self.exclude_lines())

    def test_run_from_a_linked_worktree_it_still_lands_in_the_main_checkout(self):
        linked = self.add_worktree("feature/second-change")
        out, err = self.worktree(NEW_BRANCH, cwd=linked)
        self.assertEqual(out.splitlines()[0], "worktree: %s" % self.tree())
        self.assertEqual(branch_of(self.tree()), NEW_BRANCH)

    def test_refuses_a_path_that_is_taken_and_creates_no_branch(self):
        self.tree().mkdir(parents=True)
        (self.tree() / "notes.txt").write_text("someone's files\n")
        code, out, err = self.run_sdd("worktree", NEW_BRANCH)
        self.assertEqual(code, 1)
        self.assertIn("already exists", err)
        self.assertIn("--path", err)
        self.assertEqual(git(self.repo, "branch", "--list", NEW_BRANCH).strip(), "")

    def test_refuses_a_name_git_would_not_take(self):
        code, out, err = self.run_sdd("worktree", "not a branch")
        self.assertEqual(code, 1)
        self.assertIn("not a branch name", err)


class ExistingBranchTests(WorktreeCase):
    def test_a_branch_only_the_remote_has_is_checked_out_tracking_it(self):
        pushed = self.push_spec_from_another_clone()
        self.assertEqual(git(self.repo, "branch", "-r", "--list", "origin/" + NEW_BRANCH).strip(), "")
        out, err = self.worktree(NEW_BRANCH)
        self.assertIn("tracking origin/%s" % NEW_BRANCH, out)
        self.assertEqual(commit_of(self.tree()), pushed)
        self.assertEqual(upstream_of(self.tree()), "origin/" + NEW_BRANCH)
        self.assertTrue((self.tree() / "docs" / "sdd" / NEW_SLUG / "spec.md").is_file())

    def test_a_local_branch_with_no_worktree_gets_one_at_its_own_commit(self):
        out, err = self.worktree(BRANCH)
        self.assertIn("existing local branch", out)
        self.assertEqual(branch_of(self.tree(BRANCH)), BRANCH)
        self.assertEqual(commit_of(self.tree(BRANCH)), commit_of(self.repo, BRANCH))

    def test_a_branch_already_checked_out_is_reported_and_nothing_is_created(self):
        git(self.repo, "switch", "-q", BRANCH)
        out, err = self.worktree(BRANCH)
        self.assertEqual(out.splitlines()[0], "worktree: %s" % self.repo)
        self.assertIn("already checked out", out)
        self.assertEqual(len(git(self.repo, "worktree", "list").splitlines()), 1)
        self.assertFalse((self.repo / ".claude").exists())

    def test_a_second_run_names_the_worktree_the_first_made(self):
        first, err = self.worktree(NEW_BRANCH)
        second, err = self.worktree(NEW_BRANCH)
        self.assertEqual(first.splitlines()[0], second.splitlines()[0])
        self.assertIn("already checked out", second)

    def test_a_worktree_deleted_by_hand_is_refused_with_the_command_that_clears_it(self):
        self.worktree(NEW_BRANCH)
        shutil.rmtree(self.tree())
        code, out, err = self.run_sdd("worktree", NEW_BRANCH)
        self.assertEqual(code, 1)
        self.assertIn("git worktree prune", err)
        git(self.repo, "worktree", "prune")
        out, err = self.worktree(NEW_BRANCH)
        self.assertIn("existing local branch", out)


class IgnoredHomeTests(WorktreeCase):
    def test_the_main_checkout_stays_clean_through_the_local_exclude_file(self):
        out, err = self.worktree(NEW_BRANCH)
        self.assertIn(EXCLUDE_LINE, self.exclude_lines())
        self.assertIn("added %s to" % EXCLUDE_LINE, err)
        self.assertFalse((self.repo / ".gitignore").exists())
        self.assertEqual(status_lines(self.repo), [])

    def test_the_exclude_entry_is_written_once(self):
        self.worktree(NEW_BRANCH)
        out, err = self.worktree("feature/another")
        self.assertEqual(self.exclude_lines().count(EXCLUDE_LINE), 1)
        self.assertEqual(err, "")

    def test_a_home_the_repository_already_ignores_gets_no_entry(self):
        (self.repo / ".gitignore").write_text(".claude/worktrees/\n")
        git(self.repo, "add", ".gitignore")
        git(self.repo, "commit", "-q", "-m", "ignore the worktree home")
        git(self.repo, "push", "-q", "origin", "main")
        out, err = self.worktree(NEW_BRANCH)
        self.assertNotIn(EXCLUDE_LINE, self.exclude_lines())
        self.assertEqual(err, "")
        self.assertEqual(status_lines(self.repo), [])


class WithoutARemoteTests(SddCase):
    def test_the_named_base_is_cut_from_its_local_copy(self):
        code, out, err = self.run_sdd("worktree", NEW_BRANCH, "--base", "main")
        self.assertEqual(code, 0, err)
        self.assertIn("cut from main", out)
        tree = self.repo.resolve() / ".claude" / "worktrees" / "feature-new-thing"
        self.assertEqual(commit_of(tree), commit_of(self.repo, "main"))

    def test_refuses_and_says_to_ask_the_user_when_git_cannot_tell_the_base(self):
        code, out, err = self.run_sdd("worktree", NEW_BRANCH)
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("ask the user", err)
        self.assertIn("--base", err)
        self.assertEqual(git(self.repo, "branch", "--list", NEW_BRANCH).strip(), "")

    def test_refuses_a_base_no_branch_carries(self):
        code, out, err = self.run_sdd("worktree", NEW_BRANCH, "--base", "trunk")
        self.assertEqual(code, 1)
        self.assertIn("trunk", err)
        self.assertEqual(git(self.repo, "branch", "--list", NEW_BRANCH).strip(), "")

    def test_refuses_outside_git(self):
        plain = self.repo.parent / "plain"
        plain.mkdir()
        code, out, err = self.run_sdd("worktree", NEW_BRANCH, cwd=plain)
        self.assertEqual(code, 1)
        self.assertIn("not inside a git repository", err)


class SharedFlowTests(WorktreeCase):
    """Outline's order in a shared repository: the worktree, then the spec inside it."""

    def outline(self):
        self.worktree(NEW_BRANCH)
        self.init_in(self.tree())
        return self.tree() / "docs" / "sdd" / NEW_SLUG / "spec.md"

    def test_init_refuses_on_the_base_and_names_the_command_that_makes_the_branch(self):
        for argv in (("init", NEW_SLUG), ("init", NEW_SLUG, "--branch", NEW_BRANCH)):
            code, out, err = self.run_sdd(*argv)
            self.assertEqual(code, 1, out)
            self.assertIn("sdd worktree", err)
            self.assertIn("main", err)
        self.assertFalse((self.repo / "docs" / "sdd" / NEW_SLUG).exists())

    def test_the_spec_is_written_on_its_own_branch_and_the_main_checkout_stays_clean(self):
        spec = self.outline()
        self.assertTrue(spec.is_file())
        self.assertEqual(self.cli.parse_frontmatter(spec.read_text())[0]["branch"], NEW_BRANCH)
        self.assertEqual(self.cli.parse_frontmatter(spec.read_text())[0]["base"], "main")
        self.assertEqual(status_lines(self.tree()), ["?? docs/sdd/%s/spec.md" % NEW_SLUG])
        self.assertEqual(status_lines(self.repo), [])
        code, out, err = self.run_sdd("find", cwd=self.tree())
        self.assertEqual((code, out.strip()), (0, NEW_SLUG), err)

    def test_the_gate_commit_lands_on_the_feature_branch_and_the_base_does_not_move(self):
        self.outline()
        git(self.tree(), "add", "docs/sdd/%s/spec.md" % NEW_SLUG)
        git(self.tree(), "commit", "-q", "-m", "Approve the spec")
        self.assertEqual(commit_of(self.repo, "main"), commit_of(self.repo, "origin/main"))
        self.assertEqual(git(self.repo, "rev-list", "--count", "main..%s" % NEW_BRANCH).strip(), "1")

    def test_status_run_in_the_main_checkout_points_to_the_worktree_that_has_the_spec(self):
        self.outline()
        code, out, err = self.run_sdd("status", NEW_SLUG, "--json")
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn(str(self.tree()), err)
        self.assertIn(NEW_BRANCH, err)

    def test_find_run_in_the_main_checkout_lists_the_specs_other_worktrees_are_building(self):
        self.outline()
        code, out, err = self.run_sdd("find")
        self.assertEqual(code, 1)
        self.assertIn("no specs", err)
        self.assertIn(NEW_SLUG, err)
        self.assertIn(str(self.tree()), err)

    def test_status_names_the_branch_that_commits_a_spec_no_worktree_has_checked_out(self):
        self.outline()
        git(self.tree(), "add", "docs/sdd/%s/spec.md" % NEW_SLUG)
        git(self.tree(), "commit", "-q", "-m", "Approve the spec")
        git(self.repo, "worktree", "remove", str(self.tree()))
        code, out, err = self.run_sdd("status", NEW_SLUG)
        self.assertEqual(code, 1)
        self.assertIn("sdd worktree %s" % NEW_BRANCH, err)
        self.worktree(NEW_BRANCH)
        code, out, err = self.run_sdd("status", NEW_SLUG, cwd=self.tree())
        self.assertEqual(code, 0, err)
        self.assertIn("phase: 1. Outline", out)

    def test_a_spec_pushed_from_another_machine_is_picked_up_once_fetched(self):
        self.push_spec_from_another_clone()
        code, out, err = self.run_sdd("status", NEW_SLUG)
        self.assertEqual(code, 0, err)
        self.assertIn("missing", out)
        git(self.repo, "fetch", "-q", "origin")
        code, out, err = self.run_sdd("status", NEW_SLUG)
        self.assertEqual(code, 1)
        self.assertIn("sdd worktree %s" % NEW_BRANCH, err)
        self.worktree(NEW_BRANCH)
        code, out, err = self.run_sdd("find", cwd=self.tree())
        self.assertEqual((code, out.strip()), (0, NEW_SLUG), err)

    def test_a_merged_copy_of_a_spec_on_another_branch_is_not_taken_for_the_spec(self):
        git(self.repo, "switch", "-q", "-c", "feature/unrelated")
        self.write_spec()
        git(self.repo, "add", "docs/sdd/%s/spec.md" % SLUG)
        git(self.repo, "commit", "-q", "-m", "carry a spec that names another branch")
        git(self.repo, "switch", "-q", "main")
        code, out, err = self.run_sdd("status", SLUG)
        self.assertEqual(code, 0, err)
        self.assertIn("missing", out)

    def test_a_slug_nobody_has_outlined_still_reads_as_missing(self):
        data = self.status_json("never-outlined")
        self.assertFalse(data["artifacts"]["spec"]["exists"])
        self.assertEqual(data["phase"], "1. Outline")


class PrivateFlowTests(WorktreeCase):
    """A private repository takes the same order; its spec lands in the main checkout's folder."""

    SHARED = False

    def test_the_spec_lands_in_the_main_checkout_and_names_the_worktrees_branch(self):
        self.worktree(NEW_BRANCH)
        self.init_in(self.tree())
        spec = self.repo / "docs" / "sdd" / NEW_SLUG / "spec.md"
        self.assertTrue(spec.is_file())
        self.assertFalse((self.tree() / "docs").exists())
        self.assertEqual(self.cli.parse_frontmatter(spec.read_text())[0]["branch"], NEW_BRANCH)
        self.assertEqual(status_lines(self.repo), [])
        self.assertEqual(status_lines(self.tree()), [])
        code, out, err = self.run_sdd("find", cwd=self.tree())
        self.assertEqual((code, out.strip()), (0, NEW_SLUG), err)

    def test_status_reads_the_spec_from_the_main_checkout_too(self):
        self.worktree(NEW_BRANCH)
        self.init_in(self.tree())
        data = self.status_json(NEW_SLUG)
        self.assertEqual(data["mode"], "private")
        self.assertTrue(data["artifacts"]["spec"]["exists"])
        self.assertEqual(data["branch"], NEW_BRANCH)

    def test_init_on_the_base_is_allowed_since_nothing_is_staged_there(self):
        code, out, err = self.run_sdd("init", NEW_SLUG, "--branch", NEW_BRANCH)
        self.assertEqual(code, 0, err)
        self.assertEqual(status_lines(self.repo), [])


if __name__ == "__main__":
    unittest.main()
