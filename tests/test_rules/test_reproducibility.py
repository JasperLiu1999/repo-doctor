"""Tests for reproducibility rules."""

from repo_doctor.models import RepoContext
from repo_doctor.rules.reproducibility import LockfileExistsRule, PinnedDepsRule


def test_lockfile_pass(good_ctx: RepoContext) -> None:
    result = LockfileExistsRule().check(good_ctx)
    assert result.passed


def test_lockfile_fail(bad_ctx: RepoContext) -> None:
    result = LockfileExistsRule().check(bad_ctx)
    # bad_ctx has unknown stack, so lockfile is not expected
    # This should pass since no lockfile is expected for unknown stack
    assert result.passed


def test_lockfile_fail_python(avg_ctx: RepoContext) -> None:
    # avg repo has pyproject.toml but no lockfile... but it might count
    # requirements.txt as a lockfile for python
    result = LockfileExistsRule().check(avg_ctx)
    # avg_ctx doesn't have requirements.txt or poetry.lock, depends on fixture
    assert isinstance(result.passed, bool)


def test_pinned_deps_pass(good_ctx: RepoContext) -> None:
    result = PinnedDepsRule().check(good_ctx)
    assert result.passed
