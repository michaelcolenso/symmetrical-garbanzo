from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from kpf.cli.commands import export_run, inspect_run, resume_run, run_kpf, validate_run

app = typer.Typer(help="KPF (Knowledge Product Factory) CLI")
console = Console()


@app.callback()
def callback() -> None:
    """Knowledge Product Factory CLI runtime."""


@app.command("run")
def run_command(
    objective: str = typer.Argument(..., help="Niche or problem to investigate."),
    config: Path | None = typer.Option(None, "--config", help="Optional path to config YAML."),
) -> None:
    run_kpf(objective=objective, config_path=config)


@app.command("inspect")
def inspect_command(run_id: str) -> None:
    inspect_run(run_id)


@app.command("validate")
def validate_command(run_id: str) -> None:
    validate_run(run_id)


@app.command("resume")
def resume_command(run_id: str) -> None:
    resume_run(run_id)


@app.command("export")
def export_command(
    run_id: str,
    format: str = typer.Option("markdown", "--format", help="Export format."),
) -> None:
    export_run(run_id, format)


if __name__ == "__main__":
    app()
