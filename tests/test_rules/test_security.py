"""Tests for security rules."""

import subprocess
from pathlib import Path

from repo_doctor.context import build_context
from repo_doctor.rules.security import NoHighEntropyRule, NoSecretsRule


def test_no_secrets_pass(good_ctx) -> None:
    result = NoSecretsRule().check(good_ctx)
    assert result.passed


def test_no_secrets_fail(tmp_path: Path) -> None:
    (tmp_path / ".env").write_text("SECRET=abc123")
    (tmp_path / "main.py").write_text("pass")
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)

    ctx = build_context(tmp_path)
    result = NoSecretsRule().check(ctx)
    assert not result.passed


def test_env_example_ignored(tmp_path: Path) -> None:
    (tmp_path / ".env.example").write_text("SECRET=changeme")
    (tmp_path / "main.py").write_text("pass")
    subprocess.run(["git", "init", "-b", "main"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@t.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)

    ctx = build_context(tmp_path)
    result = NoSecretsRule().check(ctx)
    assert result.passed


def test_no_high_entropy_pass(good_ctx) -> None:
    result = NoHighEntropyRule().check(good_ctx)
    assert result.passed
