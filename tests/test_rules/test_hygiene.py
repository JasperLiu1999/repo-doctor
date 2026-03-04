"""Tests for hygiene rules."""

import subprocess
from pathlib import Path

from repo_doctor.context import build_context
from repo_doctor.models import RepoContext
from repo_doctor.rules.hygiene import (
    GitignoreCoverageRule,
    GitignoreExistsRule,
    NoVenvCommittedRule,
    RepoSizeRule,
)


def test_gitignore_pass(good_ctx: RepoContext) -> None:
    result = GitignoreExistsRule().check(good_ctx)
    assert result.passed


def test_gitignore_fail(bad_ctx: RepoContext) -> None:
    result = GitignoreExistsRule().check(bad_ctx)
    assert not result.passed


def test_gitignore_coverage_pass(good_ctx: RepoContext) -> None:
    result = GitignoreCoverageRule().check(good_ctx)
    assert result.passed


def test_no_venv_pass(good_ctx: RepoContext) -> None:
    result = NoVenvCommittedRule().check(good_ctx)
    assert result.passed


def test_no_venv_fail(tmp_path: Path) -> None:
    """Repo with venv committed should fail."""
    (tmp_path / "venv" / "lib").mkdir(parents=True)
    (tmp_path / "venv" / "lib" / "something.py").write_text("x = 1")
    (tmp_path / "main.py").write_text("pass")
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)

    ctx = build_context(tmp_path)
    result = NoVenvCommittedRule().check(ctx)
    assert not result.passed


def test_repo_size_pass(good_ctx: RepoContext) -> None:
    result = RepoSizeRule().check(good_ctx)
    assert result.passed
