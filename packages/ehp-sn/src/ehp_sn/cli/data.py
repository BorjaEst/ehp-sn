"""The ``ehp-sn data`` command group.

Generates, validates, and inspects immutable interim substrates
(``docs/docs/interfaces/cli/data.md``).

This module is a thin orchestration shell (CLI-001). Each command here owns only:

* argument parsing and option validation;
* delegating to a generic data-service seam (``_data_service.DataService``);
* rendering the returned result (text or JSON);
* mapping controlled failures to stable exit codes.

It does **not** own substrate generation, configuration semantics, registry,
build planning, artifact construction/persistence, contract validation,
inspection, resource resolution, or fingerprinting. Those live behind the
service seam.

The six commands are producer-neutral: this module contains no conditional
logic keyed to any specific substrate family, and an arbitrary substrate
reference works so long as the backend understands it.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated

import typer

from ehp_sn.cli._data_service import (
    BuildResult,
    DataNotImplementedError,
    DataService,
    DataServiceError,
    InspectResult,
    ListedSubstrate,
    PlanResult,
    ShowResult,
    ValidateResult,
)
from ehp_sn.cli.data_adapter import FrameworkDataService
from ehp_sn.discovery import effective_registry

app = typer.Typer(
    help="Generate, validate, and inspect substrate artifacts.",
    no_args_is_help=True,
    rich_markup_mode=None,
)

# ---------------------------------------------------------------------------
# Error mapping
# ---------------------------------------------------------------------------


def _fail(error: Exception) -> None:
    """Raise a controlled typer exit for a known failure.

    ``DataServiceError`` instances carry their own category and exit code.
    A bare ``NotImplementedError`` is translated to a controlled
    ``operation_not_implemented`` failure (exit 1) so normal users never see a
    traceback. Anything else is unexpected and re-raised for diagnostics.
    """
    if isinstance(error, typer.Exit):
        raise error
    if isinstance(error, DataServiceError):
        if _json_mode():
            typer.echo(_error_envelope(error))
        else:
            typer.echo(f"Error: {error.message}", err=True)
        raise typer.Exit(code=error.exit_code)
    if isinstance(error, NotImplementedError):
        wrapped = DataNotImplementedError(
            "the requested data operation is not yet implemented by the framework backend."
        )
        if _json_mode():
            typer.echo(_error_envelope(wrapped))
        else:
            typer.echo(f"Error: {wrapped.message}", err=True)
        raise typer.Exit(code=wrapped.exit_code)
    raise error


_json_requested = False
_current_action = "data"


def _json_mode() -> bool:
    return _json_requested


def _error_envelope(error: DataServiceError) -> str:
    import json

    envelope = {
        "schema_version": 1,
        "status": "error",
        "action": _current_action,
        "warnings": [],
        "code": error.category,
        "message": error.message,
    }
    return json.dumps(envelope)


# ---------------------------------------------------------------------------
# Output rendering
# ---------------------------------------------------------------------------


def _emit_list(rows: Sequence[ListedSubstrate], fmt: str) -> None:
    if fmt == "json":
        import json

        typer.echo(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "success",
                    "action": "list",
                    "warnings": [],
                    "result": [
                        {
                            "ref": r.ref,
                            "family": r.family,
                            "output": r.output,
                        }
                        for r in rows
                    ],
                }
            )
        )
        return
    if not rows:
        typer.echo("No substrate generators available.")
        return
    typer.echo(f"{'REF':<16} {'FAMILY':<14} OUTPUT")
    for row in rows:
        typer.echo(f"{row.ref:<16} {row.family:<14} {row.output}")


def _emit_show(result: ShowResult, fmt: str) -> None:
    if fmt == "json":
        import json

        typer.echo(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "success",
                    "action": "show",
                    "warnings": [],
                    "result": {
                        "ref": result.ref,
                        "description": result.description,
                    },
                }
            )
        )
        return
    typer.echo(f"Target: {result.ref}")
    typer.echo(f"Description: {result.description}")


def _emit_plan(result: PlanResult, fmt: str) -> None:
    if fmt == "json":
        import json

        typer.echo(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "success",
                    "action": "plan",
                    "warnings": [],
                    "result": {
                        "target": result.target,
                        "config": result.config,
                        "status": result.status,
                    },
                }
            )
        )
        return
    typer.echo(f"target: {result.target}")
    typer.echo(f"config: {result.config or '(default)'}")
    typer.echo(f"status: {result.status}")


def _emit_build(result: BuildResult, fmt: str) -> None:
    if fmt == "json":
        import json

        typer.echo(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "success",
                    "action": result.action,
                    "warnings": [],
                    "result": {
                        "ref": result.ref,
                        "action": result.action,
                        "location": result.location,
                    },
                }
            )
        )
        return
    if result.location:
        typer.echo(f"{result.action}: {result.ref} -> {result.location}")
    else:
        typer.echo(f"{result.action}: {result.ref}")


def _emit_validate(result: ValidateResult, fmt: str) -> None:
    if fmt == "json":
        import json

        typer.echo(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "success" if result.ok else "error",
                    "action": "validate",
                    "warnings": list(result.warnings),
                    "result": {
                        "artifact": result.artifact,
                        "ok": result.ok,
                        "errors": list(result.errors),
                    },
                }
            )
        )
        return
    if result.ok:
        typer.echo(f"OK: {result.artifact}")
    else:
        typer.echo(f"FAIL: {result.artifact}")
    for warning in result.warnings:
        typer.echo(f"warning: {warning}", err=True)
    for error in result.errors:
        typer.echo(f"error: {error}", err=True)


def _emit_inspect(result: InspectResult, fmt: str) -> None:
    if fmt == "json":
        import json

        typer.echo(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "success",
                    "action": "inspect",
                    "warnings": [],
                    "result": {
                        "artifact": result.artifact,
                        "summary": dict(result.summary),
                        "samples": list(result.samples),
                    },
                }
            )
        )
        return
    typer.echo(f"Artifact: {result.artifact}")
    for key, value in result.summary.items():
        typer.echo(f"{key}: {value}")
    if result.samples:
        typer.echo("samples:")
        for sample in result.samples:
            typer.echo(f"  {sample}")


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------


@app.command("list")
def list_command(
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """List available substrate generators."""
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "list"
    try:
        rows = _get_service().list()
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
    _emit_list(rows, fmt)


@app.command("show")
def show_command(
    target: Annotated[str, typer.Argument(help="Substrate generator reference.")],
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """Describe one substrate generator."""
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "show"
    try:
        result = _get_service().show(target)
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
    _emit_show(result, fmt)


@app.command("plan")
def plan_command(
    target: Annotated[str, typer.Argument(help="Substrate generator reference.")],
    config: Annotated[str, typer.Option("--config", help="Generation configuration file.")],
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """Resolve a build without writing data."""
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "plan"
    try:
        result = _get_service().plan(target, config)
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
    _emit_plan(result, fmt)


@app.command("build")
def build_command(
    target: Annotated[str, typer.Argument(help="Substrate generator reference.")],
    config: Annotated[str, typer.Option("--config", help="Generation configuration file.")],
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """Build one immutable substrate artifact."""
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "build"
    try:
        result = _get_service().build(target, config)
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
    _emit_build(result, fmt)


@app.command("validate")
def validate_command(
    artifact: Annotated[str, typer.Argument(help="Path or artifact reference.")],
    level: Annotated[str, typer.Option("--level", help="Validation depth (quick|full).")] = "full",
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """Validate an existing substrate artifact without modifying it."""
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "validate"
    if level not in ("quick", "full"):
        typer.echo("Error: --level must be 'quick' or 'full'.", err=True)
        raise typer.Exit(code=2)
    try:
        result = _get_service().validate(artifact, level)
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
    _emit_validate(result, fmt)
    if not result.ok:
        raise typer.Exit(code=5)


@app.command("inspect")
def inspect_command(
    artifact: Annotated[str, typer.Argument(help="Path or artifact reference.")],
    samples: Annotated[int, typer.Option("--samples", help="Number of representative records.")] = 0,
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """Display artifact metadata and bounded samples."""
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "inspect"
    if samples < 0:
        typer.echo("Error: --samples must be non-negative.", err=True)
        raise typer.Exit(code=2)
    try:
        result = _get_service().inspect(artifact, samples)
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
    _emit_inspect(result, fmt)
    _emit_inspect(result, fmt)
    _emit_inspect(result, fmt)
    _emit_inspect(result, fmt)
    _emit_inspect(result, fmt)
    _emit_inspect(result, fmt)
    _emit_inspect(result, fmt)
    _emit_inspect(result, fmt)
    _emit_inspect(result, fmt)
