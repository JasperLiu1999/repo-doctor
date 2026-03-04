"""Tests for context building."""

from pathlib import Path

from repo_doctor.context import build_context
from repo_doctor.models import StackType


def test_detect_python_stack(avg_repo: Path) -> None:
    ctx = build_context(avg_repo)
    assert ctx.stack == StackType.PYTHON


def test_detect_node_stack(tmp_path: Path) -> None:
    import subprocess

    (tmp_path / "package.json").write_text('{"name": "test"}')
    (tmp_path / "index.js").write_text("console.log('hi')")
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "t@t.com"], cwd=tmp_path, capture_output=True
    )
    subprocess.run(
        ["git", "config", "user.name", "T"], cwd=tmp_path, capture_output=True
    )
    subprocess.run(
        ["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True
    )

    ctx = build_context(tmp_path)
    assert ctx.stack == StackType.NODE


def test_files_indexed(avg_repo: Path) -> None:
    ctx = build_context(avg_repo)
    assert "README.md" in ctx.files
    assert ".gitignore" in ctx.files


def test_project_name(avg_repo: Path) -> None:
    ctx = build_context(avg_repo)
    assert ctx.project_name == avg_repo.name
