from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from kpf.config.loader import load_settings
from kpf.core.runner import RunInitializer

console = Console()


def run_kpf(objective: str, config_path: Path | None) -> None:
    settings = load_settings(config_path)
    initializer = RunInitializer(settings)
    paths = initializer.initialize(objective)

    console.print("[green]KPF run initialized[/green]")
    console.print(f"run_id: [bold]{paths.root.name}[/bold]")
    console.print(f"workspace: {paths.root}")


def inspect_run(run_id: str) -> None:
    raise typer.Exit(code=2)


def validate_run(run_id: str) -> None:
    raise typer.Exit(code=2)


def resume_run(run_id: str) -> None:
    raise typer.Exit(code=2)


def export_run(run_id: str, format: str) -> None:
    raise typer.Exit(code=2)
