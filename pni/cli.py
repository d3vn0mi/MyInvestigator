"""PNI CLI — Phone Number Investigator command-line interface."""

from __future__ import annotations

import asyncio
import json
import os
import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

from pni import __version__
from pni.core.models import Query, QueryType
from pni.core.investigator import Investigator
from pni.core.cache import Cache
from pni.formatters import format_table, format_json, format_csv, get_formatter
from pni.reports.html_report import save_html_report

console = Console()


def _print_banner():
    t = Text()
    t.append("  PNI ", style="bold red")
    t.append(f"v{__version__}", style="dim")
    t.append("  |  Phone Number Investigator", style="white")
    t.append("  |  by d3vn0mi", style="dim")
    console.print(Panel(t, border_style="red", box=box.DOUBLE_EDGE))


def _get_sources(query_type: QueryType) -> list:
    sources = []

    if query_type == QueryType.PHONE:
        from pni.modules.phone import PhoneLocalSource, PhoneDorkSource, PhoneReputationSource
        sources.append(PhoneLocalSource())
        sources.append(PhoneDorkSource())
        sources.append(PhoneReputationSource())

    elif query_type == QueryType.EMAIL:
        from pni.modules.email import EmailLocalSource, EmailBreachSource, EmailSocialSource
        sources.append(EmailLocalSource())
        sources.append(EmailBreachSource())
        sources.append(EmailSocialSource())

    elif query_type == QueryType.NAME:
        from pni.modules.name import NameLocalSource, NameSearchSource, NameSocialSource
        sources.append(NameLocalSource())
        sources.append(NameSearchSource())
        sources.append(NameSocialSource())

    from pni.sources.wayback import WaybackSource
    sources.append(WaybackSource())

    return sources


async def _run_investigation(query: Query, output_dir: str | None, fmt: str, verbose: bool):
    cache = Cache()
    await cache.open()

    try:
        sources = _get_sources(query.query_type)
        investigator = Investigator(sources=sources, cache=cache)

        if verbose:
            console.print(f"[dim]Registered {len(sources)} sources for {query.query_type.value}[/dim]")
            for s in sources:
                console.print(f"[dim]  - {s.name} ({s.category})[/dim]")
            console.print()

        result = await investigator.investigate(query)

        if fmt == "json":
            click.echo(format_json(result))
        elif fmt == "csv":
            click.echo(format_csv(result))
        else:
            format_table(result, console)

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

            json_path = os.path.join(output_dir, f"pni_{query.query_type.value}_{_safe_filename(query.value)}.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False, default=str)
            console.print(f"[green]JSON report:[/green] {json_path}")

            html_path = save_html_report(result, output_dir)
            console.print(f"[green]HTML report:[/green] {html_path}")

    finally:
        await cache.close()


def _safe_filename(value: str) -> str:
    return "".join(c if c.isalnum() or c in ".-_" else "_" for c in value)[:50]


@click.group()
@click.version_option(__version__, prog_name="pni")
def cli():
    """PNI — Phone Number Investigator: OSINT toolkit for phone, email, and name reconnaissance."""
    pass


@cli.command()
@click.argument("number")
@click.option("--format", "fmt", type=click.Choice(["table", "json", "csv"]), default="table", help="Output format")
@click.option("--output", "-o", default=None, help="Output directory for reports")
@click.option("--verbose", "-v", is_flag=True, help="Show debug info")
def phone(number: str, fmt: str, output: str | None, verbose: bool):
    """Investigate a phone number."""
    _print_banner()
    console.print(f"[cyan]Investigating phone:[/cyan] [bold]{number}[/bold]\n")
    query = Query(query_type=QueryType.PHONE, value=number)
    asyncio.run(_run_investigation(query, output, fmt, verbose))


@cli.command()
@click.argument("email")
@click.option("--format", "fmt", type=click.Choice(["table", "json", "csv"]), default="table", help="Output format")
@click.option("--output", "-o", default=None, help="Output directory for reports")
@click.option("--verbose", "-v", is_flag=True, help="Show debug info")
def email(email: str, fmt: str, output: str | None, verbose: bool):
    """Investigate an email address."""
    _print_banner()
    console.print(f"[cyan]Investigating email:[/cyan] [bold]{email}[/bold]\n")
    query = Query(query_type=QueryType.EMAIL, value=email)
    asyncio.run(_run_investigation(query, output, fmt, verbose))


@cli.command()
@click.argument("name")
@click.option("--format", "fmt", type=click.Choice(["table", "json", "csv"]), default="table", help="Output format")
@click.option("--output", "-o", default=None, help="Output directory for reports")
@click.option("--verbose", "-v", is_flag=True, help="Show debug info")
def name(name: str, fmt: str, output: str | None, verbose: bool):
    """Search and investigate a person by name."""
    _print_banner()
    console.print(f"[cyan]Investigating name:[/cyan] [bold]{name}[/bold]\n")
    query = Query(query_type=QueryType.NAME, value=name)
    asyncio.run(_run_investigation(query, output, fmt, verbose))


@cli.command()
@click.option("--phone", "phone_num", default=None, help="Phone number to investigate")
@click.option("--email", "email_addr", default=None, help="Email to investigate")
@click.option("--name", "name_str", default=None, help="Name to investigate")
@click.option("--format", "fmt", type=click.Choice(["table", "json", "csv"]), default="table")
@click.option("--output", "-o", default=None, help="Output directory for reports")
@click.option("--verbose", "-v", is_flag=True, help="Show debug info")
def investigate(phone_num: str | None, email_addr: str | None, name_str: str | None,
                fmt: str, output: str | None, verbose: bool):
    """Full investigation across all provided identifiers."""
    _print_banner()

    if not any([phone_num, email_addr, name_str]):
        console.print("[red]Provide at least one: --phone, --email, or --name[/red]")
        sys.exit(1)

    async def _run_all():
        cache = Cache()
        await cache.open()
        try:
            if phone_num:
                console.print(f"\n[bold yellow]--- Phone Investigation ---[/bold yellow]")
                query = Query(query_type=QueryType.PHONE, value=phone_num)
                await _run_investigation(query, output, fmt, verbose)

            if email_addr:
                console.print(f"\n[bold yellow]--- Email Investigation ---[/bold yellow]")
                query = Query(query_type=QueryType.EMAIL, value=email_addr)
                await _run_investigation(query, output, fmt, verbose)

            if name_str:
                console.print(f"\n[bold yellow]--- Name Investigation ---[/bold yellow]")
                query = Query(query_type=QueryType.NAME, value=name_str)
                await _run_investigation(query, output, fmt, verbose)
        finally:
            await cache.close()

    asyncio.run(_run_all())
