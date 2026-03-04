"""Tests for the reporter module."""

import json
from pathlib import Path

from repo_doctor.models import ChangePlan, Grade, RuleResult, ScanReport, Severity
from repo_doctor.reporter import (
    generate_changes_md,
    generate_report_json,
    generate_report_md,
    write_reports,
)


def _sample_report() -> ScanReport:
    return ScanReport(
        score=75,
        grade=Grade.B,
        results=[
            RuleResult(
                rule_id="readme_exists",
                name="README present",
                category="basics",
                severity=Severity.ERROR,
                passed=True,
                weight=15,
                rationale="README present: OK",
            ),
            RuleResult(
                rule_id="license_exists",
                name="LICENSE present",
                category="basics",
                severity=Severity.ERROR,
                passed=False,
                weight=12,
                rationale="No LICENSE file found.",
                suggested_fix="Add a LICENSE file.",
                auto_fixable=True,
            ),
        ],
        repo_path="/tmp/test",
        stack="python",
        total_rules=2,
        passed_rules=1,
        failed_rules=1,
    )


def test_generate_report_md() -> None:
    md = generate_report_md(_sample_report())
    assert "# Repo Doctor Report" in md
    assert "75/100" in md
    assert "README present" in md
    assert "LICENSE present" in md
    assert "FAIL" in md
    assert "PASS" in md


def test_generate_report_json() -> None:
    raw = generate_report_json(_sample_report())
    data = json.loads(raw)
    assert data["score"] == 75
    assert data["grade"] == "B"
    assert len(data["results"]) == 2


def test_write_reports_both(tmp_path: Path) -> None:
    report = _sample_report()
    written = write_reports(report, tmp_path, fmt="both")
    assert len(written) == 2
    assert any("report.md" in str(p) for p in written)
    assert any("report.json" in str(p) for p in written)


def test_write_reports_md_only(tmp_path: Path) -> None:
    written = write_reports(_sample_report(), tmp_path, fmt="md")
    assert len(written) == 1
    assert "report.md" in str(written[0])


def test_generate_changes_md() -> None:
    plan = ChangePlan(changes=[], summary="No changes")
    md = generate_changes_md(plan)
    assert "No changes" in md
