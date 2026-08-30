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

The implemented commands (``list``/``show``/``plan``/``build``/``inspect``/
``validate``) are producer-neutral: this module contains no conditional logic
keyed to any specific substrate family, and an arbitrary substrate reference
works so long as the backend understands it. ``validate`` resolves a committed
artifact and delegates shared-contract conformance checking to the single
framework-owned shared validator.

A command-surface option that is intentionally unsupported until its ordering
or selection semantics are explicitly specified (for example ``inspect
--samples``) is reported by the CLI itself as a controlled "not implemented"
failure rather than invented here.
"""

from __future__ import annotations

import contextlib
from collections.abc import Sequence
from typing import Annotated

import typer

from ehp_sn.cli.data_adapter import (
    BuildResult,
    DataCliError,
    DataNotImplementedError,
    DataOperationError,
    FrameworkDataAdapter,
    InspectResult,
    ListedSubstrate,
    PlanResult,
    ShowResult,
    ValidateResult,
)
from ehp_sn.discovery import effective_registry
from ehp_sn.execution import effective_execution_composition
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
    from ehp_sn.figures.contracts import FigureInputCompatibilityError
    from ehp_sn.figures.service import FigureServiceError

    if isinstance(error, (FigureServiceError, FigureInputCompatibilityError)):
        _fail(_figure_service_cli_error(error))
        return
    raise error


class _UnknownFigureCliError(DataCliError):
    """The requested figure is not registered in the component catalogue."""

    exit_code = 4  # referenced input not found
    category = "unknown_figure"


class _FigureInputIncompatibleCliError(DataCliError):
    """The requested figure's semantic input requirement is not satisfied."""

    exit_code = 3  # invalid configuration or specification
    category = "figure_input_incompatible"


class _NoCompatibleFigureCliError(DataCliError):
    """``--figure auto`` resolved no compatible figure for the source record."""

    exit_code = 4  # referenced input not found
    category = "no_compatible_figure"


class _AmbiguousFigureCliError(DataCliError):
    """``--figure auto`` resolved more than one compatible figure."""

    exit_code = 3  # invalid configuration or specification
    category = "ambiguous_figure"


def _figure_service_cli_error(error: Exception) -> DataCliError:
    """Map a controlled figure-service failure to a stable CLI category.

    ``UnknownFigureError`` (unknown/malformed/invalid figure reference) maps to
    the controlled ``unknown_figure`` (exit 4); an input-compatibility mismatch
    maps to ``figure_input_incompatible`` (exit 3). ``NoCompatibleFigureError``
    and ``AmbiguousFigureError`` (``--figure auto`` outcomes) map to their own
    stable categories. Other figure-service failures
    (for example an unresolvable artifact or missing record) map to the generic
    ``operation_failed`` category.
    """
    from ehp_sn.figures.contracts import FigureInputCompatibilityError
    from ehp_sn.figures.service import (
        AmbiguousFigureError,
        NoCompatibleFigureError,
        UnknownFigureError,
    )

    if isinstance(error, UnknownFigureError):
        return _UnknownFigureCliError(str(error))
    if isinstance(error, FigureInputCompatibilityError):
        return _FigureInputIncompatibleCliError(str(error))
    if isinstance(error, NoCompatibleFigureError):
        return _NoCompatibleFigureCliError(str(error))
    if isinstance(error, AmbiguousFigureError):
        return _AmbiguousFigureCliError(str(error))
    return DataOperationError(str(error))


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


def _require_positive_release(release: int | None) -> None:
    """Reject an out-of-range invocation ``--release`` value as invalid usage.

    A release number selects a concrete publication coordinate and must be a
    positive integer. ``0`` and negative values are invalid option values and
    are rejected here as a controlled CLI usage error (exit 2), consistent with
    how other option-value violations (for example ``--samples -1``) are
    handled. A non-integer ``--release`` is rejected earlier by typer's integer
    option typing as the same control usage error.
    """
    if release is not None and release < 1:
        typer.echo("Error: --release must be a positive integer.", err=True)
        raise typer.Exit(code=2)


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
            execution_composition=effective_execution_composition(),
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


def _emit_build(result: BuildResult, fmt: str) -> None:
    if fmt == "json":
        import json

        typer.echo(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "success",
                    "action": "build",
                    "warnings": [],
                    "result": {
                        "action": result.action,
                        "target": result.target,
                        "output_contract": result.output_contract,
                        "build_input_identity": result.build_input_identity,
                        "artifact_fingerprint": result.artifact_fingerprint,
                        "artifact_ref": result.artifact_ref,
                        "location": result.location,
                    },
                }
            )
        )
        return
    typer.echo(f"action: {result.action}")
    typer.echo(f"target: {result.target}")
    typer.echo(f"output: {result.output_contract}")
    typer.echo(f"build-input-identity: {result.build_input_identity}")
    typer.echo(f"artifact-fingerprint: {result.artifact_fingerprint}")
    if result.artifact_ref:
        typer.echo(f"artifact: {result.artifact_ref}")
    if result.location:
        typer.echo(f"location: {result.location}")


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
                        "artifact": result.artifact_ref,
                        "record_id": result.record_id,
                        "schema_ref": result.schema_ref,
                        "content": result.content,
                    },
                }
            )
        )
        return
    typer.echo(f"artifact: {result.artifact_ref}")
    typer.echo(f"record_id: {result.record_id}")
    typer.echo(f"schema_ref: {result.schema_ref}")
    typer.echo(f"content: {result.content!r}")


def _emit_validate(result: ValidateResult, fmt: str) -> None:
    if fmt == "json":
        import json

        typer.echo(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "success",
                    "action": "validate",
                    "warnings": [],
                    "result": {
                        "artifact": result.artifact_ref,
                        "total_records": result.total_records,
                        "conforming_records": result.conforming_records,
                        "non_conforming": [
                            {
                                "record_id": r.record_id,
                                "schema_ref": r.schema_ref,
                                "invariant": r.invariant,
                                "message": r.message,
                            }
                            for r in result.non_conforming
                        ],
                    },
                }
            )
        )
        return
    typer.echo(f"artifact: {result.artifact_ref}")
    typer.echo(f"records: {result.conforming_records}/{result.total_records} conforming")
    if result.non_conforming:
        for r in result.non_conforming:
            typer.echo(f"  non-conforming {r.record_id} ({r.schema_ref} {r.invariant}): {r.message}")


def _run_figure_inspect(artifact: str, record_id: str, figure_ref: str, fmt: str) -> None:
    """Resolve, project, realize, and interactively display one requested figure.

    This is the Phase-1 ``data inspect --figure`` orchestration path. It
    delegates completely to the generic figure service
    (``ehp_sn.figures.inspect_figure``): the CLI owns only argument passing,
    invoking the framework figure service, presenting the result, and mapping
    controlled figure failures to stable exit codes. It carries no
    raster/producer semantics (Phase-1 § 17 · P1-T15, § 18).

    Interactive display is a CLI/runtime concern separate from figure
    realization: the figure service itself requires no graphical desktop
    (Phase-1 § 16 · P1-T14). Under a non-interactive backend the transient
    Figure is produced and reported without a GUI event loop.
    """
    from ehp_sn.figures import inspect_figure
    from ehp_sn.figures.contracts import FigureInputCompatibilityError
    from ehp_sn.figures.service import FigureServiceError

    try:
        result = inspect_figure(artifact, record_id, figure_ref)
    except (FigureServiceError, FigureInputCompatibilityError) as exc:
        _fail(exc)
        return
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
        return

    projection = result.projection
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
                        "artifact": projection.source.artifact_ref,
                        "record_id": projection.source.record_id,
                        "schema_ref": projection.source.logical_contract,
                        "figure": projection.figure_ref,
                        "projection_identity": str(projection.identity()),
                    },
                }
            )
        )
        return
    typer.echo(f"artifact: {projection.source.artifact_ref}")
    typer.echo(f"record_id: {projection.source.record_id}")
    typer.echo(f"figure: {projection.figure_ref}")
    typer.echo(f"projection_identity: {projection.identity()}")
    _display_figure(result.figure)


def _display_figure(figure: object) -> None:
    """Present a transient realized Matplotlib Figure (CLI/runtime concern).

    Uses Matplotlib's ordinary interactive display mechanism. Under a headless
    or non-interactive backend this is a no-op that does not require X11,
    Wayland, a Windows desktop, or a GUI event loop (Phase-1 § 16 · P1-T14).
    """
    import matplotlib.pyplot as plt

    # Under a non-interactive backend (Agg, headless CI) there is nothing to
    # show and show() warns; display is optional and must not fail the figure
    # result (Phase-1 § 16 · P1-T14). Only attempt interactive presentation on a
    # backend that can host a GUI event loop.
    if getattr(plt, "get_backend", lambda: "Agg")().lower().startswith(("agg", "template")):
        return
    # Interactive display failure must not fail the figure service result.
    with contextlib.suppress(Exception):  # noqa: BLE001
        plt.show(block=True)
    _ = figure  # the transient figure is owned by the interactive display path


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
    release: Annotated[
        int | None,
        typer.Option(
            "--release",
            help="Publication release number (where this concrete build is committed).",
        ),
    ] = None,
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """Resolve a build without writing data.

    ``--release`` selects the intended publication coordinate. It is the
    highest authority for where a concrete build is committed: it is not a
    scientific configuration field and does not participate in scientific build
    identity.
    """
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "plan"
    _require_positive_release(release)
    try:
        result = _get_adapter().plan(target, config, release)
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
    _emit_plan(result, fmt)


@app.command("build")
def build_command(
    target: Annotated[str, typer.Argument(help="Substrate generator reference.")],
    config: Annotated[str, typer.Option("--config", help="Generation configuration file.")],
    release: Annotated[
        int | None,
        typer.Option(
            "--release",
            help="Publication release number (where this concrete build is committed).",
        ),
    ] = None,
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """Build one immutable substrate artifact.

    Delegates to the generic framework build lifecycle and renders the projected
    framework build outcome (committed or reused) with the committed artifact's
    identity. ``--release`` is the invocation-layer publication coordinate and
    is not a scientific configuration field.

    Physical destination publication is a deferred concern; this command reports
    the logical, edition-bearing outcome.
    """
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "build"
    _require_positive_release(release)
    try:
        result = _get_adapter().build(target, config, release)
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
    _emit_build(result, fmt)


@app.command("validate")
def validate_command(
    artifact: Annotated[str, typer.Argument(help="Path or artifact reference.")],
    level: Annotated[str, typer.Option("--level", help="Validation depth (quick|full).")] = "full",
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """Validate an existing substrate artifact without modifying it.

    Resolves the committed artifact and validates every logical record against
    its declared shared logical schema through the single framework-owned
    shared-contract validation authority. No record is silently repaired; any
    non-conformance is reported as a controlled failure. The check is total and
    deterministic over the committed records.
    """
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "validate"
    if level not in ("quick", "full"):
        typer.echo("Error: --level must be 'quick' or 'full'.", err=True)
        raise typer.Exit(code=2)
    try:
        result = _get_adapter().validate(artifact)
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
    _emit_validate(result, fmt)


@app.command("inspect")
def inspect_command(
    artifact: Annotated[str, typer.Argument(help="Path or artifact reference.")],
    record: Annotated[
        str | None,
        typer.Option("--record", help="Exact record identifier to inspect."),
    ] = None,
    samples: Annotated[int, typer.Option("--samples", help="Number of representative records.")] = 0,
    figure: Annotated[
        str | None,
        typer.Option(
            "--figure",
            help="Request one figure over the exact record (or 'auto' to resolve.).",
        ),
    ] = None,
    list_figures: Annotated[
        bool,
        typer.Option("--list-figures", help="List figures compatible with the exact record."),
    ] = False,
    fmt: Annotated[str, typer.Option("--format", help="Output format.")] = "text",
) -> None:
    """Display metadata and one exact logical record of a committed artifact.

    The deterministic Phase-0R inspection path resolves a committed substrate
    artifact (by physical path or ``artifact:`` reference) and inspects exactly
    the logical record selected by ``--record RECORD_ID`` through the existing
    record-identity mechanism. This is a single deterministic lookup; no
    implicit ordering, RNG, or representative sampling is performed.

    ``--figure FIGURE_REF`` (Phase 1) additionally realizes one figure over the
    exact selected record through the ordinary figure catalogue and generic
    figure pipeline. It is figure-owner agnostic: the CLI carries no
    raster/producer semantics and delegates to the generic figure service.
    ``--figure auto`` (Phase 2) resolves to exactly one canonical figure before
    projection: zero compatible figures is a controlled ``no_compatible_figure``
    failure, more than one is ``ambiguous_figure``.

    ``--list-figures`` (Phase 2) lists the canonical references of every
    registered figure whose input requirement the exact record satisfies, in
    the catalogue's deterministic order. It performs no projection.

    ``--samples`` remains separate and intentionally unsupported until its
    ordering/selection semantics are explicitly specified: a positive value is
    reported as a controlled not-yet-specified failure rather than invented
    here.
    """
    global _json_requested  # noqa: PLW0603
    _json_requested = fmt == "json"
    global _current_action  # noqa: PLW0603
    _current_action = "inspect"
    if record is None:
        if samples > 0:
            _fail(
                DataNotImplementedError(
                    "data inspect --samples representative sampling is not yet specified; "
                    "use --record RECORD_ID to inspect an exact record."
                )
            )
        typer.echo("Error: data inspect requires --record RECORD_ID.", err=True)
        raise typer.Exit(code=2)
    if samples < 0:
        typer.echo("Error: --samples must be non-negative.", err=True)
        raise typer.Exit(code=2)
    if list_figures:
        _run_list_figures(artifact, record, fmt)
        return
    if figure is not None:
        _run_figure_inspect(artifact, record, figure, fmt)
        return
    try:
        result = _get_adapter().inspect(artifact, record)
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
    _emit_inspect(result, fmt)


def _run_list_figures(artifact: str, record_id: str, fmt: str) -> None:
    """List figures compatible with one exact record (Phase 2 · ``--list-figures``).

    Delegates entirely to the generic figure service
    (:func:`ehp_sn.figures.list_figures_for_record`), which iterates the ordinary
    component catalogue; the CLI hard-codes no producer→figure or contract→figure
    table (Phase-2 § 36). Controlled figure-service failures map to stable exit
    codes through the normal error mapping.
    """
    from ehp_sn.figures.service import FigureServiceError, list_figures_for_record

    try:
        refs = list_figures_for_record(artifact, record_id)
    except FigureServiceError as exc:
        _fail(exc)
        return
    except Exception as exc:  # noqa: BLE001
        _fail(exc)
        return
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
                        "artifact": artifact,
                        "record_id": record_id,
                        "figures": refs,
                    },
                }
            )
        )
        return
    if not refs:
        typer.echo("No compatible figures for this record.")
        return
    typer.echo(f"artifact: {artifact}")
    typer.echo(f"record_id: {record_id}")
    typer.echo("compatible-figures:")
    for ref in refs:
        typer.echo(f"  {ref}")
