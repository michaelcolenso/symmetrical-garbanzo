"""Implementation of the 'kpf run' command.

Responsibility:
1. Load settings
2. Initialize logging (console only at first, then add file handler after workspace is created)
3. Create workspace
4. Write initial run.json state file
5. Log the run start event
6. Print a success summary to the console
"""

from __future__ import annotations
from pathlib import Path
import typer
import orjson
from rich.console import Console
from rich.panel import Panel

from kpf.config.loader import get_settings
from kpf.core.workspace import WorkspaceManager
from kpf.core.logging import configure_logging, get_logger
from kpf.core.clock import utc_now, format_iso


_console = Console()


def run_command(
    niche: str = typer.Argument(..., help='The niche or problem to research. E.g. "IEP/504 parent advocacy".'),
    workspace_base: str = typer.Option(None, "--workspace-base", "-w", help="Override workspace base directory."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Set up workspace but skip all agent work."),
) -> None:
    """Start a new KPF research and product design run."""

    settings = get_settings()

    # Allow CLI override of workspace base
    if workspace_base:
        settings = settings.model_copy(update={"workspace_base": Path(workspace_base)})

    # Step 1: Console-only logging during workspace setup
    configure_logging(log_level=settings.log_level)
    log = get_logger("cli.run")

    _console.print(Panel(
        f"[bold green]Starting KPF run[/bold green]\n"
        f"Niche: [cyan]{niche}[/cyan]",
        title="KPF",
        expand=False,
    ))

    # Step 2: Create workspace
    manager = WorkspaceManager(settings)
    try:
        paths = manager.create_run()
    except FileExistsError as exc:
        _console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1)

    log.info("Workspace created at %s", paths.root)

    # Step 3: Reconfigure logging now that we have a JSONL path
    configure_logging(log_level=settings.log_level, jsonl_path=paths.events_log_path)
    log = get_logger("cli.run")  # Re-fetch after reconfigure

    # Step 4: Write initial run.json state file
    now = utc_now()
    run_state = {
        "run_id": paths.run_id,
        "niche": niche,
        "stage": "INIT",
        "created_at": format_iso(now),
        "workspace_path": str(paths.root),
    }
    paths.run_state_path.write_bytes(orjson.dumps(run_state, option=orjson.OPT_INDENT_2))

    log.info("Run state written", extra={"run_id": paths.run_id, "stage": "INIT"})
    log.info("Run initialized: %s — niche: %s", paths.run_id, niche)

    # Step 5: Print success summary
    _console.print(Panel(
        f"[bold]Run ID:[/bold]      {paths.run_id}\n"
        f"[bold]Workspace:[/bold]   {paths.root}\n"
        f"[bold]State file:[/bold]  {paths.run_state_path}\n"
        f"[bold]Events log:[/bold]  {paths.events_log_path}\n"
        f"[bold]Stage:[/bold]       INIT\n\n"
        f"[dim]Next: implement M2 (persistence) to advance past INIT.[/dim]",
        title="[green]Run Created[/green]",
        expand=False,
    ))

    raise typer.Exit(code=0)
