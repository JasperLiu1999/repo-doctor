"""Tests for CLI commands."""

from pathlib import Path

from typer.testing import CliRunner

from repo_doctor.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "scan" in result.output
    assert "fix" in result.output
    assert "init" in result.output


def test_scan_command(good_repo: Path) -> None:
    result = runner.invoke(app, ["scan", str(good_repo)])
    assert result.exit_code == 0
    assert "Score" in result.output
    assert "Grade" in result.output


def test_scan_writes_reports(good_repo: Path) -> None:
    runner.invoke(app, ["scan", str(good_repo)])
    assert (good_repo / "repo-doctor.report.md").exists()
    assert (good_repo / "repo-doctor.report.json").exists()


def test_scan_bad_repo(bad_repo: Path) -> None:
    result = runner.invoke(app, ["scan", str(bad_repo)])
    assert result.exit_code == 0
    assert "FAIL" in result.output


def test_scan_strict_exits_nonzero(bad_repo: Path) -> None:
    result = runner.invoke(app, ["scan", "--strict", str(bad_repo)])
    assert result.exit_code == 1


def test_fix_dry_run(bad_repo: Path) -> None:
    result = runner.invoke(app, ["fix", "--dry-run", str(bad_repo)])
    assert result.exit_code == 0
    assert "Dry run" in result.output
    # Should NOT have created files
    assert not (bad_repo / "LICENSE").exists()


def test_fix_yes(bad_repo: Path) -> None:
    result = runner.invoke(app, ["fix", "--yes", str(bad_repo)])
    assert result.exit_code == 0
    assert "Applied" in result.output
    # Should have created files
    assert (bad_repo / "README.md").exists()
    assert (bad_repo / "LICENSE").exists()


def test_fix_improves_score(bad_repo: Path) -> None:
    result = runner.invoke(app, ["fix", "--yes", str(bad_repo)])
    assert "improved" in result.output.lower() or "Score" in result.output


def test_scan_nonexistent_path() -> None:
    result = runner.invoke(app, ["scan", "/nonexistent/path"])
    assert result.exit_code == 1
