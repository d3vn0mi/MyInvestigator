"""Output formatters for investigation results — table, JSON, CSV."""

from __future__ import annotations

import csv
import io
import json

from rich.console import Console
from rich.table import Table
from rich import box

from pni.core.models import InvestigationResult


def format_table(result: InvestigationResult, console: Console | None = None) -> str:
    """Render results as a rich table to terminal."""
    con = console or Console()

    con.print()
    summary = Table(title="Investigation Summary", box=box.ROUNDED, border_style="cyan")
    summary.add_column("Metric", style="bold cyan")
    summary.add_column("Value", style="white")
    summary.add_row("Target", result.query.value)
    summary.add_row("Type", result.query.query_type.value.upper())
    summary.add_row("Total checks", str(result.total_count))
    summary.add_row("Hits found", f"[green]{result.found_count}[/green]")
    summary.add_row("No result", f"[dim]{result.total_count - result.found_count}[/dim]")
    con.print(summary)
    con.print()

    categories: dict[str, list] = {}
    for r in result.results:
        categories.setdefault(r.category, []).append(r)

    for cat, items in categories.items():
        found_ct = sum(1 for i in items if i.status == "found")
        tbl = Table(
            title=f"{cat.upper()} ({found_ct}/{len(items)} hits)",
            box=box.SIMPLE, border_style="yellow",
        )
        tbl.add_column("Source", style="bold", width=25)
        tbl.add_column("Status", width=10)
        tbl.add_column("Title / Info", ratio=1)

        for item in items:
            status_style = {"found": "green", "not_found": "dim", "error": "red"}.get(item.status, "white")
            tbl.add_row(
                item.source_name,
                f"[{status_style}]{item.status}[/{status_style}]",
                item.title[:80] or item.snippet[:80] or "-",
            )
        con.print(tbl)
        con.print()

    return ""


def format_json(result: InvestigationResult) -> str:
    return json.dumps(result.to_dict(), indent=2, ensure_ascii=False, default=str)


def format_csv(result: InvestigationResult) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["source", "category", "status", "title", "snippet", "url", "confidence"])
    for r in result.results:
        writer.writerow([r.source_name, r.category, r.status, r.title, r.snippet, r.url, r.confidence])
    return output.getvalue()


def get_formatter(name: str):
    formatters = {
        "table": format_table,
        "json": format_json,
        "csv": format_csv,
    }
    return formatters.get(name, format_table)
