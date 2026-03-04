"""Tests for basics rules."""

from repo_doctor.models import RepoContext
from repo_doctor.rules.basics import LicenseExistsRule, ReadmeExistsRule, ReadmeSectionsRule


def test_readme_exists_pass(good_ctx: RepoContext) -> None:
    rule = ReadmeExistsRule()
    result = rule.check(good_ctx)
    assert result.passed


def test_readme_exists_fail(bad_ctx: RepoContext) -> None:
    rule = ReadmeExistsRule()
    result = rule.check(bad_ctx)
    assert not result.passed
    assert result.auto_fixable


def test_readme_fix_generates_content(bad_ctx: RepoContext) -> None:
    rule = ReadmeExistsRule()
    fix = rule.fix(bad_ctx)
    assert fix is not None
    assert fix.file_path == "README.md"
    assert len(fix.content) > 0


def test_readme_sections_pass(good_ctx: RepoContext) -> None:
    rule = ReadmeSectionsRule()
    result = rule.check(good_ctx)
    assert result.passed


def test_readme_sections_fail(bad_ctx: RepoContext) -> None:
    rule = ReadmeSectionsRule()
    result = rule.check(bad_ctx)
    assert not result.passed


def test_license_exists_pass(good_ctx: RepoContext) -> None:
    rule = LicenseExistsRule()
    result = rule.check(good_ctx)
    assert result.passed


def test_license_exists_fail(bad_ctx: RepoContext) -> None:
    rule = LicenseExistsRule()
    result = rule.check(bad_ctx)
    assert not result.passed
    assert result.auto_fixable


def test_license_fix_generates_mit(bad_ctx: RepoContext) -> None:
    rule = LicenseExistsRule()
    fix = rule.fix(bad_ctx)
    assert fix is not None
    assert "MIT License" in fix.content
