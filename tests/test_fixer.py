"""Tests for the fixer module."""

from pathlib import Path

from repo_doctor.fixer import apply_changes
from repo_doctor.models import ChangePlan, FileOp, FixResult


def test_apply_creates_files(tmp_path: Path) -> None:
    plan = ChangePlan(
        changes=[
            FixResult(
                rule_id="test",
                file_path="NEW_FILE.md",
                operation=FileOp.CREATE,
                content="# Hello\n",
                description="Create test file",
            )
        ],
        summary="1 file to create",
    )
    applied = apply_changes(plan, tmp_path)
    assert "NEW_FILE.md" in applied
    assert (tmp_path / "NEW_FILE.md").read_text() == "# Hello\n"


def test_apply_creates_nested_dirs(tmp_path: Path) -> None:
    plan = ChangePlan(
        changes=[
            FixResult(
                rule_id="test",
                file_path=".github/workflows/ci.yml",
                operation=FileOp.CREATE,
                content="name: CI\n",
                description="Create CI",
            )
        ],
    )
    apply_changes(plan, tmp_path)
    assert (tmp_path / ".github" / "workflows" / "ci.yml").exists()


def test_apply_patches_file(tmp_path: Path) -> None:
    (tmp_path / "existing.txt").write_text("original\n")
    plan = ChangePlan(
        changes=[
            FixResult(
                rule_id="test",
                file_path="existing.txt",
                operation=FileOp.PATCH,
                content="original\nappended\n",
                description="Patch file",
            )
        ],
    )
    apply_changes(plan, tmp_path)
    assert (tmp_path / "existing.txt").read_text() == "original\nappended\n"


def test_empty_plan_no_changes(tmp_path: Path) -> None:
    plan = ChangePlan(changes=[])
    applied = apply_changes(plan, tmp_path)
    assert applied == []
