"""The ``ehp-sn tasks`` command group.

Build, validate, and inspect immutable processed task corpora
(``docs/docs/interfaces/cli/tasks.md``).

This module is a thin orchestration shell (CLI-001): each command owns only
argument parsing, delegation to a generic task adapter, and presentation. It
defines no scientific task semantics and never imports a concrete research
package (ARCH-001). The implemented catalogue surface (``list``/``show``/``plan``)
is producer- and task-neutral: it enumerates registered task definitions and
resolves their declared source roles generically, so an arbitrary task and
source reference works without any task-family or producer-family branching.
"""

from __future__ import annotations

import json
from typing import Annotated

import typer

from ehp_sn.discovery import effective_registry
from ehp_sn.tasks import TaskCompositionError

from .tasks_adapter import (
    TaskCompositionCliError,
    TaskPlanResult,
    TasksAdapter,
    TasksCliError,
    TaskShowResult,
)

app = typer.Typer(
    help="Build, validate, and inspect processed task corpora.",
    no_args_is_help=True,
    rich_markup_mode=None,
)

_JSON = False


def _fail(error: Exception) -> None:
    if isinstance(error, typer.Exit):
        raise error
    if isinstance(error, TasksCliError):
        if _JSON:
            typer.echo(json.dumps({"error": error.category, "message": error.message}))
        else:
            typer.echo(f"Error: {error.message}", err=True)
        raise typer.Exit(code=error.exit_code)
    if isinstance(error, TaskCompositionError):
        mapped = TaskCompositionCliError(str(error))
        if _JSON:
            typer.echo(json.dumps({"error": mapped.category, "message": mapped.message}))
        else:
            typer.echo(f"Error: {mapped.message}", err=True)
        raise typer.Exit(code=mapped.exit_code)
    raise error


@app.callback()
def _main(
    format: Annotated[str, typer.Option("--format", help="Output format: text|json")] = "text",
) -> None:
    global _JSON
    _JSON = format == "json"


def _adapter() -> TasksAdapter:
    return TasksAdapter(effective_registry())


@app.command("list")
def list_tasks_cmd(
    format: Annotated[str, typer.Option("--format", help="Output format: text|json")] = "text",
) -> None:
    """List available task families."""
    try:
        rows = _adapter().list()
    except Exception as exc:  # noqa: BLE001 - controlled mapping
        _fail(exc)
        return
    if format == "json":
        typer.echo(
            json.dumps(
                [
                    {
                        "ref": r.ref,
                        "purpose": r.purpose,
                        "source_roles": list(r.source_roles),
                        "contracts": list(r.contracts),
                    }
                    for r in rows
                ]
            )
        )
    else:
        for r in rows:
            typer.echo(f"{r.ref}\t{r.purpose}")


@app.command()
def show(
    task: Annotated[str, typer.Argument(help="Task family reference, e.g. task:maze-hard/v1")],
    format: Annotated[str, typer.Option("--format", help="Output format: text|json")] = "text",
) -> None:
    """Describe one task-generation contract."""
    try:
        result = _adapter().show(task)
    except Exception as exc:  # noqa: BLE001 - controlled mapping
        _fail(exc)
        return
    _emit_show(result, format)


def _emit_show(result: TaskShowResult, format: str) -> None:
    if format == "json":
        typer.echo(
            json.dumps(
                {
                    "ref": result.ref,
                    "purpose": result.purpose,
                    "source_roles": [{"role": r, "contract": c} for r, c in result.source_roles],
                    "required_contracts": list(result.required_contracts),
                }
            )
        )
    else:
        typer.echo(f"Task: {result.ref}")
        typer.echo(f"Purpose: {result.purpose}")
        for role, contract in result.source_roles:
            typer.echo(f"Source role: {role} -> {contract}")


@app.command()
def plan(
    task: Annotated[str, typer.Argument(help="Task family reference, e.g. task:maze-hard/v1")],
    source: Annotated[
        list[str] | None,
        typer.Option("--source", help="Source binding role=artifact-ref (repeatable)"),
    ] = None,
    release: Annotated[int, typer.Option("--release", help="Corpus release number")] = 1,
    seed: Annotated[int, typer.Option("--seed", help="Deterministic generation seed")] = 0,
    format: Annotated[str, typer.Option("--format", help="Output format: text|json")] = "text",
) -> None:
    """Resolve a task build without writing files."""
    try:
        bindings: list[tuple[str, str]] = []
        for item in source or []:
            role, _, literal = item.partition("=")
            bindings.append((role, literal))
        result = _adapter().plan(task, tuple(bindings), release=release, seed=seed)
    except Exception as exc:  # noqa: BLE001 - controlled mapping
        _fail(exc)
        return
    _emit_plan(result, format)


def _emit_plan(result: TaskPlanResult, format: str) -> None:
    if format == "json":
        typer.echo(
            json.dumps(
                {
                    "task": result.task_ref,
                    "release": result.release,
                    "seed": result.seed,
                    "sources": [
                        {"role": r, "ref": ref, "fingerprint": fp}
                        for r, ref, fp in result.resolved_sources
                    ],
                }
            )
        )
    else:
        typer.echo(f"Task: {result.task_ref}  release={result.release}  seed={result.seed}")
        for role, ref, fingerprint in result.resolved_sources:
            typer.echo(f"  {role}: {ref}  ({fingerprint})")
