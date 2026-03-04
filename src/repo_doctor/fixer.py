"""ChangePlan application: diff preview and file writes."""

from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from .models import ChangePlan, FileOp


def preview_changes(plan: ChangePlan, console: Console | None = None) -> str:
    """Show a rich diff preview of planned changes. Returns plain text summary."""
    console = console or Console()
    if not plan.changes:
        console.print("[green]No changes needed.[/green]")
        return "No changes needed."

    table = Table(title="Planned Changes", show_lines=True)
    table.add_column("File", style="cyan")
    table.add_column("Operation", style="yellow")
    table.add_column("Description")

    for change in plan.changes:
        op_label = "CREATE" if change.operation == FileOp.CREATE else "PATCH"
        table.add_row(change.file_path, op_label, change.description)

    console.print(table)
    console.print()

    for change in plan.changes:
        title = f"{'+ ' if change.operation == FileOp.CREATE else '~ '}{change.file_path}"
        # Detect language from extension
        ext = change.file_path.rsplit(".", 1)[-1] if "." in change.file_path else ""
        lang_map = {
            "md": "markdown",
            "yml": "yaml",
            "yaml": "yaml",
            "json": "json",
            "toml": "toml",
            "py": "python",
            "js": "javascript",
            "ts": "typescript",
        }
        lang = lang_map.get(ext, "text")

        # Truncate content for preview
        lines = change.content.splitlines()
        preview_content = "\n".join(lines[:40])
        if len(lines) > 40:
            preview_content += f"\n... ({len(lines) - 40} more lines)"

        syntax = Syntax(preview_content, lang, theme="monokai", line_numbers=True)
        console.print(Panel(syntax, title=title, border_style="green"))
        console.print()

    op = "created/modified" if plan.changes else "changed"
    summary = f"{len(plan.changes)} file(s) will be {op}"
    return summary


def apply_changes(plan: ChangePlan, repo_root: Path) -> list[str]:
    """Apply the change plan to disk. Returns list of modified file paths."""
    applied: list[str] = []
    for change in plan.changes:
        target = repo_root / change.file_path
        target.parent.mkdir(parents=True, exist_ok=True)

        if change.operation == FileOp.CREATE:
            target.write_text(change.content)
        elif change.operation == FileOp.PATCH:
            target.write_text(change.content)

        applied.append(change.file_path)

    return applied
