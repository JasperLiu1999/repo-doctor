"""CLI entry point for Repo Doctor."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import __version__
from .context import build_context
from .engine import RuleEngine
from .fixer import apply_changes, preview_changes
from .models import Severity
from .reporter import write_changes, write_reports

app = typer.Typer(
    name="repo-doctor",
    help="Turn any repository into an open-source-ready, professional repo.",
    no_args_is_help=True,
)
console = Console()


def _grade_color(grade: str) -> str:
    return {
        "A": "green", "B": "blue", "C": "yellow", "D": "red",
    }.get(grade, "white")


def _severity_style(severity: Severity) -> str:
    return {
        "error": "red", "warn": "yellow", "info": "dim",
    }.get(severity.value, "white")


def _print_scan_summary(report) -> None:  # noqa: ANN001
    color = _grade_color(report.grade.value)
    console.print()
    score_line = (
        f"[bold {color}]Score: {report.score}/100  "
        f"Grade: {report.grade.value}[/bold {color}]"
    )
    stats_line = (
        f"Stack: {report.stack}  |  "
        f"Passed: {report.passed_rules}  |  "
        f"Failed: {report.failed_rules}  |  "
        f"Total: {report.total_rules}"
    )
    console.print(
        Panel(
            f"{score_line}\n{stats_line}",
            title="[bold]Repo Doctor[/bold]",
            border_style=color,
        )
    )

    table = Table(show_lines=False, pad_edge=False, box=None)
    table.add_column("", width=3)
    table.add_column("Rule", min_width=30)
    table.add_column("Status", width=6)
    table.add_column("Details")

    for r in report.results:
        sev = _severity_style(r.severity)
        if r.passed:
            icon = "[green]OK[/green]"
        else:
            icon = f"[{sev}]FAIL[/{sev}]"
        severity_badge = (
            f"[{sev}]{r.severity.value.upper()}[/{sev}]"
        )
        detail = "" if r.passed else r.rationale
        if not r.passed and r.auto_fixable:
            detail += " [dim](auto-fixable)[/dim]"
        table.add_row(severity_badge, r.name, icon, detail)

    console.print(table)
    console.print()


@app.command()
def scan(
    path: Annotated[
        Path, typer.Argument(help="Path to the repository")
    ] = Path("."),
    format: Annotated[
        str, typer.Option("--format", "-f", help="Output format")
    ] = "both",
    strict: Annotated[
        bool, typer.Option("--strict", help="Treat warnings as errors")
    ] = False,
    only: Annotated[
        Optional[list[str]], typer.Option("--only", help="Only run these rules")
    ] = None,
    skip: Annotated[
        Optional[list[str]], typer.Option("--skip", help="Skip these rules")
    ] = None,
) -> None:
    """Scan a repository and produce a health report."""
    repo_path = path.resolve()
    if not repo_path.is_dir():
        console.print(f"[red]Error: {repo_path} is not a directory[/red]")
        raise typer.Exit(1)

    ctx = build_context(repo_path)
    engine = RuleEngine(only=only, skip=skip)
    report = engine.scan(ctx)

    _print_scan_summary(report)

    written = write_reports(report, repo_path, fmt=format)
    for p in written:
        console.print(f"[dim]Report written: {p}[/dim]")

    if strict:
        has_warnings = any(
            not r.passed and r.severity in (Severity.WARN, Severity.ERROR)
            for r in report.results
        )
        if has_warnings:
            raise typer.Exit(1)


@app.command()
def fix(
    path: Annotated[
        Path, typer.Argument(help="Path to the repository")
    ] = Path("."),
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Show changes without applying")
    ] = False,
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Apply without confirmation")
    ] = False,
    license: Annotated[
        str, typer.Option("--license", help="License: mit or apache-2.0")
    ] = "mit",
    ci: Annotated[
        str, typer.Option("--ci", help="CI platform: github-actions")
    ] = "github-actions",
    readme: Annotated[
        str, typer.Option("--readme", help="README style: minimal or standard")
    ] = "standard",
    format: Annotated[
        str, typer.Option("--format", "-f", help="Report format")
    ] = "both",
    only: Annotated[
        Optional[list[str]], typer.Option("--only", help="Only run these rules")
    ] = None,
    skip: Annotated[
        Optional[list[str]], typer.Option("--skip", help="Skip these rules")
    ] = None,
) -> None:
    """Fix repository issues by generating missing files."""
    repo_path = path.resolve()
    if not repo_path.is_dir():
        console.print(f"[red]Error: {repo_path} is not a directory[/red]")
        raise typer.Exit(1)

    # Initial scan
    ctx = build_context(repo_path)
    engine = RuleEngine(only=only, skip=skip)
    report = engine.scan(ctx)

    console.print("[bold]Initial scan:[/bold]")
    _print_scan_summary(report)

    # Build change plan
    plan = engine.build_change_plan(ctx, report)
    if not plan.changes:
        console.print("[green]Nothing to fix! Repository looks good.[/green]")
        return

    # Preview
    preview_changes(plan, console)

    if dry_run:
        console.print("[yellow]Dry run - no files were modified.[/yellow]")
        write_changes(plan, repo_path)
        return

    # Confirm
    if not yes:
        confirm = typer.confirm("Apply these changes?")
        if not confirm:
            console.print("[yellow]Aborted.[/yellow]")
            return

    # Apply
    applied = apply_changes(plan, repo_path)
    console.print(f"[green]Applied {len(applied)} change(s).[/green]")

    # Re-scan
    ctx_after = build_context(repo_path)
    report_after = engine.scan(ctx_after)

    console.print("\n[bold]After fix:[/bold]")
    _print_scan_summary(report_after)

    improvement = report_after.score - report.score
    if improvement > 0:
        console.print(
            f"[green]Score improved by {improvement} points![/green]"
        )

    # Write reports
    write_reports(report_after, repo_path, fmt=format)
    write_changes(plan, repo_path, applied=applied)


@app.command()
def init(
    path: Annotated[
        Path, typer.Argument(help="Path to the repository")
    ] = Path("."),
) -> None:
    """Initialize a .repo-doctor.yml config file."""
    repo_path = path.resolve()
    config_path = repo_path / ".repo-doctor.yml"

    if config_path.exists():
        console.print(
            f"[yellow]Config already exists: {config_path}[/yellow]"
        )
        overwrite = typer.confirm("Overwrite?")
        if not overwrite:
            return

    project_name = typer.prompt("Project name", default=repo_path.name)
    license_choice = typer.prompt("License (mit/apache-2.0)", default="mit")
    ci_choice = typer.prompt(
        "CI platform (github-actions)", default="github-actions"
    )
    readme_style = typer.prompt(
        "README style (minimal/standard)", default="standard"
    )

    config = f"""# Repo Doctor configuration
project_name: {project_name}
license: {license_choice}
ci: {ci_choice}
readme: {readme_style}

# Uncomment to skip specific rules:
# skip:
#   - lint_config
#   - pinned_deps
#   - repo_size
"""

    config_path.write_text(config)
    console.print(f"[green]Config written: {config_path}[/green]")
    console.print("\nNext steps:")
    console.print("  repo-doctor scan  # Check your repo")
    console.print("  repo-doctor fix   # Fix issues")


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"repo-doctor {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool,
        typer.Option(
            "--version", "-v", help="Show version",
            is_eager=True, callback=_version_callback,
        ),
    ] = False,
) -> None:
    pass


if __name__ == "__main__":
    app()
