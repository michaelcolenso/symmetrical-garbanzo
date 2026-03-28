from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from kpf.config.loader import load_settings
from kpf.core.runner import RunInitializer
from kpf.core.runs import RunManager

console = Console()


def run_kpf(objective: str, config_path: Path | None) -> None:
    settings = load_settings(config_path)
    initializer = RunInitializer(settings)
    paths = initializer.initialize(objective)

    console.print("[green]KPF run initialized[/green]")
    console.print(f"run_id: [bold]{paths.root.name}[/bold]")
    console.print(f"workspace: {paths.root}")


def inspect_run(run_id: str, config_path: Path | None = None) -> None:
    settings = load_settings(config_path)
    manager = RunManager(settings)
    try:
        state = manager.read_state(run_id)
        events = manager.read_events(run_id)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    console.print(f"[bold]Run:[/bold] {run_id}")
    console.print(f"[bold]Objective:[/bold] {state.get('objective', '(unknown)')}")
    console.print(f"[bold]Stage:[/bold] {state.get('stage', 'UNKNOWN')}")
    console.print(f"[bold]Status:[/bold] {state.get('status', 'unknown')}")
    console.print(f"[bold]Events:[/bold] {len(events)}")


def validate_run(run_id: str, config_path: Path | None = None) -> None:
    settings = load_settings(config_path)
    manager = RunManager(settings)

    try:
        paths = manager.paths_for(run_id)
        state = manager.read_state(run_id)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    checks = {
        "workspace": paths.root.exists(),
        "config": paths.config_file.exists(),
        "run log": paths.run_log_file.exists(),
        "run state": paths.run_state_file.exists(),
        "objective": bool(state.get("objective")),
        "stage": bool(state.get("stage")),
        "status": bool(state.get("status")),
    }

    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        console.print("[red]Validation failed[/red]")
        for name in failed:
            console.print(f"- missing/invalid: {name}")
        raise typer.Exit(code=1)

    console.print("[green]Validation passed[/green]")


def resume_run(run_id: str, config_path: Path | None = None) -> None:
    settings = load_settings(config_path)
    manager = RunManager(settings)
    try:
        state = manager.resume(run_id)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    console.print("[green]Run resumed[/green]")
    console.print(f"run_id: [bold]{run_id}[/bold]")
    console.print(f"status: {state.get('status', 'unknown')}")


def export_run(run_id: str, format: str, config_path: Path | None = None) -> None:
    if format != "markdown":
        console.print(f"[red]Unsupported export format: {format}[/red]")
        raise typer.Exit(code=1)

    settings = load_settings(config_path)
    manager = RunManager(settings)

    try:
        export_path = manager.export_markdown(run_id)
    except FileNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    console.print("[green]Export complete[/green]")
    console.print(f"file: {export_path}")
