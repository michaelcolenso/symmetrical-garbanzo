"""KPF CLI entrypoint.

Registered as the 'kpf' console script in pyproject.toml.
All commands are registered here. Non-M1 commands are stubs.
"""

from __future__ import annotations
import typer
from rich.console import Console

app = typer.Typer(
    name="kpf",
    help="Knowledge Product Factory — research, design, and package knowledge products.",
    add_completion=False,
    no_args_is_help=True,
)
_console = Console()


# --- M1 command: run ---
from kpf.cli.run import run_command  # noqa: E402
app.command(name="run")(run_command)


# --- Stub commands for M2+ (registered now so --help is complete) ---

@app.command(name="inspect")
def inspect_command(run_id: str = typer.Argument(..., help="Run ID to inspect.")) -> None:
    """Inspect the state and artifacts of a completed or in-progress run."""
    _console.print(f"[yellow]inspect[/yellow] not yet implemented (M7). run_id={run_id}")
    raise typer.Exit(code=0)


@app.command(name="validate")
def validate_command(run_id: str = typer.Argument(..., help="Run ID to validate.")) -> None:
    """Re-run validation gates on an existing run."""
    _console.print(f"[yellow]validate[/yellow] not yet implemented (M7). run_id={run_id}")
    raise typer.Exit(code=0)


@app.command(name="resume")
def resume_command(run_id: str = typer.Argument(..., help="Run ID to resume.")) -> None:
    """Resume a run from its last completed stage."""
    _console.print(f"[yellow]resume[/yellow] not yet implemented (M7). run_id={run_id}")
    raise typer.Exit(code=0)


@app.command(name="export")
def export_command(
    run_id: str = typer.Argument(..., help="Run ID to export."),
    format: str = typer.Option("markdown", "--format", "-f", help="Export format."),
) -> None:
    """Export run artifacts in the specified format."""
    _console.print(f"[yellow]export[/yellow] not yet implemented (M7). run_id={run_id}, format={format}")
    raise typer.Exit(code=0)


if __name__ == "__main__":
    app()
