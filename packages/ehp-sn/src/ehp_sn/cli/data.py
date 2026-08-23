"""The ``ehp-sn data`` command group.

Generates, validates, and inspects immutable interim substrates
(``docs/docs/interfaces/cli/data.md``).

This module is a thin orchestration shell (CLI-001). Each command here owns only:

* argument parsing and option validation;
* delegating to a generic CLI adapter (``data_adapter.FrameworkDataAdapter``);
* rendering the returned presentation DTO (text or JSON);
* mapping controlled failures to stable exit codes.

It does **not** own substrate generation, configuration semantics, registry,
build planning, artifact construction/persistence, contract validation,
inspection, resource resolution, or fingerprinting. Those live behind the
adapter boundary or in future framework capabilities.

The implemented commands (``list``/``show``/``plan``) are producer-neutral: this
module contains no conditional logic keyed to any specific substrate family, and
an arbitrary substrate reference works so long as the backend understands it.

The commands in the established command surface that are intentionally
unsupported until the corresponding framework capability lands
(``build``/``validate``/``inspect``) are reported here by the CLI itself as a
controlled "not implemented" failure; no fake backend lifecycle method pretends
they exist.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Annotated

import typer

from ehp_sn.cli.data_adapter import (
    DataCliError,
    DataNotImplementedError,
    FrameworkDataAdapter,
    ListedSubstrate,
    PlanResult,
    ShowResult,
)
from ehp_sn.discovery import effective_registry
from ehp_sn.planning import effective_planning_composition

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

    ``DataCliError`` instances carry their own category and exit code.
    ``DataNotImplementedError`` is the controlled translation the CLI uses for a
    command that is part of the established surface but intentionally
    unsupported. Anything else is unexpected and re-raised for diagnostics.
    """
    if isinstance(error, typer.Exit):
        raise error
    if isinstance(error, DataCliError):
        if _json_mode():
            typer.echo(_error_envelope(error))
        else:
            typer.echo(f"Error: {error.message}", err=True)
        raise typer.Exit(code=error.exit_code)
    raise error


_json_requested = False
_current_action = "data"


def _json_mode() -> bool:
    return _json_requested


def _error_envelope(error: DataCliError) -> str:
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
# Adapter wiring
#
# The default is a lazily-cached :class:`FrameworkDataAdapter` over the
# effective application registry (installed research providers compose it).
# Tests may inject a constructed adapter via ``_set_adapter``/``_reset_adapter``
# so command logic is exercised without a real backend.
# ---------------------------------------------------------------------------

_override_adapter: FrameworkDataAdapter | None = None
_default_adapter_cache: FrameworkDataAdapter | None = None


def _get_adapter() -> FrameworkDataAdapter:
    """Return the data adapter, preferring any test override."""
    global _default_adapter_cache  # noqa: PLW0603
    if _override_adapter is not None:
        return _override_adapter
    if _default_adapter_cache is None:
        _default_adapter_cache = FrameworkDataAdapter(
            effective_registry(),
            planning_composition=effective_planning_composition(),
        )
    return _default_adapter_cache


def _set_adapter(adapter: FrameworkDataAdapter) -> None:
    """Install an adapter override (for test injection)."""
    global _override_adapter  # noqa: PLW0603
    _override_adapter = adapter


def _reset_adapter() -> None:
    """Clear any override and the cached default adapter."""
    global _override_adapter, _default_adapter_cache  # noqa: PLW0603
    _override_adapter = None
    _default_adapter_cache = None


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
                        "output_contract": result.output_contract,
                        "resources": [
                            {
                                "requirement_ref": r.requirement_ref,
                                "resource_ref": r.resource_ref,
                                "resolution_source": r.resolution_source,
                            }
                            for r in result.resources
                        ],
                        "identity": [{"name": i.name, "value": i.value} for i in result.identity],
                    },
                }
            )
        )
        return
    typer.echo(f"target: {result.target}")
    typer.echo(f"output: {result.output_contract}")
    if result.resources:
        typer.echo("resources:")
        for r in result.resources:
            typer.echo(f"  {r.requirement_ref}: {r.resource_ref} ({r.resolution_source})")
    if result.identity:
        typer.echo("identity-inputs:")
        for i in result.identity:
            typer.echo(f"  {i.name}: {i.value}")


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
        rows = _get_adapter().list()
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
        result = _get_adapter().show(target)
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
        result = _get_adapter().plan(target, config)
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
    _emit_plan(result, fmt)


@app.command("build")
def build_command(
    target: Annotated[str, typer.Argument(help="Substrate generator reference.")],
    config: Annotated[str, typer.Option("--config", help="Generation configuration file.")],
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """Build one immutable substrate artifact.

    Currently unsupported: materializing artifacts is a future framework
    capability. The command is part of the established surface but is reported
    here as a controlled not-implemented failure.
    """
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "build"
    _fail(DataNotImplementedError("data build is not yet implemented."))


@app.command("validate")
def validate_command(
    artifact: Annotated[str, typer.Argument(help="Path or artifact reference.")],
    level: Annotated[str, typer.Option("--level", help="Validation depth (quick|full).")] = "full",
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """Validate an existing substrate artifact without modifying it.

    Currently unsupported: artifact validation is a future framework
    capability. The command is part of the established surface but is reported
    here as a controlled not-implemented failure.
    """
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "validate"
    if level not in ("quick", "full"):
        typer.echo("Error: --level must be 'quick' or 'full'.", err=True)
        raise typer.Exit(code=2)
    _fail(DataNotImplementedError("data validate is not yet implemented."))


@app.command("inspect")
def inspect_command(
    artifact: Annotated[str, typer.Argument(help="Path or artifact reference.")],
    samples: Annotated[int, typer.Option("--samples", help="Number of representative records.")] = 0,
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """Display artifact metadata and bounded samples.

    Currently unsupported: artifact inspection is a future framework
    capability. The command is part of the established surface but is reported
    here as a controlled not-implemented failure.
    """
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "inspect"
    if samples < 0:
        typer.echo("Error: --samples must be non-negative.", err=True)
        raise typer.Exit(code=2)
    _fail(DataNotImplementedError("data inspect is not yet implemented."))
