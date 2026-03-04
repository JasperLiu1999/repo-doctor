"""Tests for community rules."""

from repo_doctor.models import RepoContext
from repo_doctor.rules.community import (
    CodeOfConductExistsRule,
    ContributingExistsRule,
    SecurityPolicyRule,
)


def test_contributing_pass(good_ctx: RepoContext) -> None:
    result = ContributingExistsRule().check(good_ctx)
    assert result.passed


def test_contributing_fail(bad_ctx: RepoContext) -> None:
    result = ContributingExistsRule().check(bad_ctx)
    assert not result.passed


def test_contributing_fix(bad_ctx: RepoContext) -> None:
    fix = ContributingExistsRule().fix(bad_ctx)
    assert fix is not None
    assert "Contributing" in fix.content


def test_coc_pass(good_ctx: RepoContext) -> None:
    result = CodeOfConductExistsRule().check(good_ctx)
    assert result.passed


def test_coc_fail(bad_ctx: RepoContext) -> None:
    result = CodeOfConductExistsRule().check(bad_ctx)
    assert not result.passed


def test_security_pass(good_ctx: RepoContext) -> None:
    result = SecurityPolicyRule().check(good_ctx)
    assert result.passed


def test_security_fail(bad_ctx: RepoContext) -> None:
    result = SecurityPolicyRule().check(bad_ctx)
    assert not result.passed
