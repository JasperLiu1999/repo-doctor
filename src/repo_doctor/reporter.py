"""Report generation: Markdown and JSON."""

from __future__ import annotations

from pathlib import Path

from .models import ChangePlan, ScanReport, Severity


def _severity_icon(severity: Severity) -> str:
    return {"error": "X", "warn": "!", "info": "i"}[severity.value]


def generate_report_md(report: ScanReport) -> str:
    lines = [
        "# Repo Doctor Report",
        "",
        f"**Repository**: `{report.repo_path}`",
        f"**Stack**: {report.stack}",
        f"**Score**: {report.score}/100 (Grade {report.grade.value})",
        f"**Rules**: {report.passed_rules} passed, "
        f"{report.failed_rules} failed, {report.total_rules} total",
        f"**Scanned**: {report.timestamp}",
        "",
        "---",
        "",
    ]

    # Group by category
    categories: dict[str, list] = {}
    for r in report.results:
        categories.setdefault(r.category, []).append(r)

    for category, results in sorted(categories.items()):
        lines.append(f"## {category.title()}")
        lines.append("")
        for r in results:
            icon = _severity_icon(r.severity)
            status = "PASS" if r.passed else "FAIL"
            lines.append(f"- [{icon}] **{r.name}** [{status}] (weight: {r.weight})")
            if not r.passed:
                lines.append(f"  - {r.rationale}")
                if r.evidence:
                    for e in r.evidence[:5]:
                        lines.append(f"  - `{e}`")
                if r.suggested_fix:
                    lines.append(f"  - Fix: {r.suggested_fix}")
                if r.auto_fixable:
                    lines.append("  - *Auto-fixable with `repo-doctor fix`*")
        lines.append("")

    return "\n".join(lines)


def generate_report_json(report: ScanReport) -> str:
    return report.model_dump_json(indent=2)


def generate_changes_md(plan: ChangePlan, applied: list[str] | None = None) -> str:
    lines = [
        "# Repo Doctor Changes",
        "",
        f"**Summary**: {plan.summary}",
        "",
    ]

    if not plan.changes:
        lines.append("No changes were needed.")
        return "\n".join(lines)

    for change in plan.changes:
        status = "Applied" if applied and change.file_path in applied else "Planned"
        lines.append(f"## `{change.file_path}` [{status}]")
        lines.append("")
        lines.append(f"- **Operation**: {change.operation.value}")
        lines.append(f"- **Rule**: {change.rule_id}")
        lines.append(f"- **Description**: {change.description}")
        lines.append("")

    return "\n".join(lines)


def write_reports(
    report: ScanReport,
    output_dir: Path,
    fmt: str = "both",
) -> list[Path]:
    """Write report files. Returns list of written paths."""
    written: list[Path] = []
    output_dir.mkdir(parents=True, exist_ok=True)

    if fmt in ("md", "both"):
        md_path = output_dir / "repo-doctor.report.md"
        md_path.write_text(generate_report_md(report))
        written.append(md_path)

    if fmt in ("json", "both"):
        json_path = output_dir / "repo-doctor.report.json"
        json_path.write_text(generate_report_json(report))
        written.append(json_path)

    return written


def write_changes(
    plan: ChangePlan,
    output_dir: Path,
    applied: list[str] | None = None,
) -> Path:
    changes_path = output_dir / "repo-doctor.changes.md"
    changes_path.write_text(generate_changes_md(plan, applied))
    return changes_path
