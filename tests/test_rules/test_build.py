"""Tests for build rules."""

from repo_doctor.models import RepoContext
from repo_doctor.rules.build import CIWorkflowRule, LintConfigRule, TestCommandRule


def test_ci_pass(good_ctx: RepoContext) -> None:
    result = CIWorkflowRule().check(good_ctx)
    assert result.passed


def test_ci_fail(bad_ctx: RepoContext) -> None:
    result = CIWorkflowRule().check(bad_ctx)
    assert not result.passed
    assert result.auto_fixable


def test_ci_fix(bad_ctx: RepoContext) -> None:
    fix = CIWorkflowRule().fix(bad_ctx)
    assert fix is not None
    assert fix.file_path == ".github/workflows/ci.yml"


def test_test_command_pass(good_ctx: RepoContext) -> None:
    result = TestCommandRule().check(good_ctx)
    assert result.passed


def test_test_command_fail(bad_ctx: RepoContext) -> None:
    result = TestCommandRule().check(bad_ctx)
    assert not result.passed


def test_lint_config_pass(good_ctx: RepoContext) -> None:
    result = LintConfigRule().check(good_ctx)
    assert result.passed


def test_lint_config_fail(bad_ctx: RepoContext) -> None:
    result = LintConfigRule().check(bad_ctx)
    assert not result.passed
