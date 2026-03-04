"""Data models for Repo Doctor."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field


class Severity(str, Enum):
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


class Grade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class FileOp(str, Enum):
    CREATE = "create"
    PATCH = "patch"


class StackType(str, Enum):
    PYTHON = "python"
    NODE = "node"
    RUST = "rust"
    GO = "go"
    SWIFT = "swift"
    UNKNOWN = "unknown"


class RepoContext(BaseModel):
    """Collected metadata about a repository."""

    root: Path
    stack: StackType = StackType.UNKNOWN
    secondary_stacks: list[StackType] = Field(default_factory=list)
    files: list[str] = Field(default_factory=list)
    file_sizes: dict[str, int] = Field(default_factory=dict)
    git_clean: bool = True
    default_branch: str = "main"
    has_remote: bool = False
    remote_url: str = ""
    project_name: str = ""
    dependencies: dict[str, str] = Field(default_factory=dict)

    model_config = {"arbitrary_types_allowed": True}


class RuleResult(BaseModel):
    """Result of a single rule check."""

    rule_id: str
    name: str
    category: str
    severity: Severity
    passed: bool
    weight: int
    rationale: str
    evidence: list[str] = Field(default_factory=list)
    suggested_fix: str = ""
    auto_fixable: bool = False


class FixResult(BaseModel):
    """A single file operation proposed by a rule fix."""

    rule_id: str
    file_path: str
    operation: FileOp
    content: str
    description: str


class ChangePlan(BaseModel):
    """Collection of proposed file changes."""

    changes: list[FixResult] = Field(default_factory=list)
    summary: str = ""


class ScanReport(BaseModel):
    """Full scan report."""

    score: int
    grade: Grade
    results: list[RuleResult]
    repo_path: str
    stack: str
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    total_rules: int = 0
    passed_rules: int = 0
    failed_rules: int = 0


def compute_grade(score: int) -> Grade:
    if score >= 90:
        return Grade.A
    elif score >= 75:
        return Grade.B
    elif score >= 55:
        return Grade.C
    else:
        return Grade.D
