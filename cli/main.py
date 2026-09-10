"""`r3po scan` command."""

from __future__ import annotations

import html
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from core.scanner import scan
from core.schema import ScanReport

app = typer.Typer(no_args_is_help=True)
console = Console()


def _html_report(report: ScanReport) -> str:
    rows = "".join("<tr>" + "".join(f"<td>{html.escape(str(value or ''))}</td>" for value in
        (f.tool, f.severity, f.file, f.line, f.title, f.description, f.remediation)) + "</tr>" for f in report.findings)
    return f"<!doctype html><html><body><h1>r3po report</h1><p>{html.escape(report.repo_url)}</p><table border='1'><tr><th>Tool</th><th>Severity</th><th>File</th><th>Line</th><th>Title</th><th>Description</th><th>Remediation</th></tr>{rows}</table></body></html>"


def _print_terminal(report: ScanReport) -> None:
    if report.error:
        console.print(f"[red]{report.error}[/red]")
    table = Table(title=f"r3po — {report.repo_url}")
    for column in ("Severity", "Tool", "File", "Line", "Title", "Description"):
        table.add_column(column)
    for finding in report.findings:
        table.add_row(finding.severity.upper(), finding.tool, finding.file, str(finding.line or ""), finding.title, finding.description)
    console.print(table)
    for error in report.tool_errors:
        console.print(f"[yellow]Tool warning: {error}[/yellow]")
    if report.scan_timed_out:
        console.print("[yellow]Scan timed out; results are partial.[/yellow]")


@app.command()
def scan_repo(repo_url: str, output: Annotated[str, typer.Option("--output")] = "terminal",
             out_file: Annotated[Path | None, typer.Option("--out-file")] = None) -> None:
    """Scan a public GitHub or GitLab repository."""
    if output not in {"terminal", "json", "html"}:
        raise typer.BadParameter("must be terminal, json, or html")
    report = scan(repo_url)
    rendered = report.model_dump_json(indent=2) if output == "json" else _html_report(report) if output == "html" else None
    if rendered is None:
        _print_terminal(report)
    elif out_file:
        out_file.write_text(rendered, encoding="utf-8")
        console.print(f"Wrote {output} report to {out_file}")
    else:
        console.print(rendered)
    if report.error:
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
