"""Shared test fixtures for repo fixtures."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from repo_doctor.context import build_context
from repo_doctor.models import RepoContext


def _git_init(path: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=path, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=path,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=path,
        capture_output=True,
    )
    subprocess.run(["git", "add", "."], cwd=path, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "init", "--allow-empty"],
        cwd=path,
        capture_output=True,
    )


@pytest.fixture
def bad_repo(tmp_path: Path) -> Path:
    """A repo missing everything."""
    (tmp_path / "main.py").write_text("print('hello')\n")
    _git_init(tmp_path)
    return tmp_path


@pytest.fixture
def avg_repo(tmp_path: Path) -> Path:
    """A repo with some basics but missing community files."""
    (tmp_path / "README.md").write_text(
        "# My Project\n\n## Installation\n\npip install it\n\n"
        "## Usage\n\nRun it\n"
    )
    (tmp_path / ".gitignore").write_text(
        "*.pyc\n__pycache__/\n.DS_Store\n*.log\nThumbs.db\n"
    )
    (tmp_path / "pyproject.toml").write_text('[project]\nname = "myproject"\n')
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text("def test_hello(): pass\n")
    _git_init(tmp_path)
    return tmp_path


@pytest.fixture
def good_repo(tmp_path: Path) -> Path:
    """A repo that should pass most checks."""
    (tmp_path / "README.md").write_text(
        "# Good Project\n\n## Installation\n\npip install good\n\n## Usage\n\nRun it\n"
    )
    (tmp_path / "LICENSE").write_text("MIT License\n")
    (tmp_path / "CONTRIBUTING.md").write_text("# Contributing\n")
    (tmp_path / "CODE_OF_CONDUCT.md").write_text("# Code of Conduct\n")
    (tmp_path / "SECURITY.md").write_text("# Security\n")
    (tmp_path / ".gitignore").write_text(
        "*.pyc\n__pycache__/\n.DS_Store\n*.log\nThumbs.db\nvenv/\n"
    )
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "good"\n\n[tool.ruff]\nline-length = 88\n'
    )
    (tmp_path / "uv.lock").write_text("# lockfile\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_main.py").write_text("def test_ok(): pass\n")
    ci_dir = tmp_path / ".github" / "workflows"
    ci_dir.mkdir(parents=True)
    (ci_dir / "ci.yml").write_text("name: CI\non: push\njobs: {}\n")
    _git_init(tmp_path)
    return tmp_path


@pytest.fixture
def bad_ctx(bad_repo: Path) -> RepoContext:
    return build_context(bad_repo)


@pytest.fixture
def avg_ctx(avg_repo: Path) -> RepoContext:
    return build_context(avg_repo)


@pytest.fixture
def good_ctx(good_repo: Path) -> RepoContext:
    return build_context(good_repo)
