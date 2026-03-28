from __future__ import annotations

from pathlib import Path

import typer

from kpf.cli.commands import export_run, inspect_run, resume_run, run_kpf, validate_run

app = typer.Typer(help="KPF (Knowledge Product Factory) CLI")


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
def inspect_command(
    run_id: str,
    config: Path | None = typer.Option(None, "--config", help="Optional path to config YAML."),
) -> None:
    inspect_run(run_id, config)


@app.command("validate")
def validate_command(
    run_id: str,
    config: Path | None = typer.Option(None, "--config", help="Optional path to config YAML."),
) -> None:
    validate_run(run_id, config)


@app.command("resume")
def resume_command(
    run_id: str,
    config: Path | None = typer.Option(None, "--config", help="Optional path to config YAML."),
) -> None:
    resume_run(run_id, config)


@app.command("export")
def export_command(
    run_id: str,
    format: str = typer.Option("markdown", "--format", help="Export format."),
    config: Path | None = typer.Option(None, "--config", help="Optional path to config YAML."),
) -> None:
    export_run(run_id, format, config)


if __name__ == "__main__":
    app()
