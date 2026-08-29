"""CLI behavior tests for the ``ehp-sn data`` command group.

These tests focus on CLI behavior (CLI-001): command existence, argument and
option interfaces, help text, delegation through the production
:class:`~ehp_sn.cli.data_adapter.FrameworkDataAdapter`, output formatting,
failure formatting, and exit codes.

The implemented commands (``list``/``show``/``plan``/``build``/``inspect``) run
against a real ``FrameworkDataAdapter`` built over **synthetic** generic
dependencies (a registry with neutral ``alpha``/``beta`` substrate definitions
and a composed planning resolver). No research package is imported; no
test-local fake service stands in for the adapter boundary.

``data inspect ARTIFACT --record RECORD_ID`` is the deterministic generic
exact-record inspection path (Phase 0R): it provides a committed artifact (or a
stubbed adapter) and an explicit record identifier, and asserts the exact record
is projected. ``--samples`` representative sampling remains intentionally
unsupported until its selection semantics are specified, and is reported by the
CLI as a controlled not-yet-specified failure (exit 1) rather than invented.

The commands that are part of the established surface but intentionally
unsupported (``validate``) are asserted to produce the documented controlled
not-implemented response (exit 1), which the CLI owns directly rather than
delegating to a placeholder adapter method.
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import pytest
from ehp_sn.cli import app
from ehp_sn.cli import data as data_module
from ehp_sn.cli.data_adapter import (
    ConfigurationInvalidError,
    ConfigurationUnreadableError,
    DataCliError,
    DataNotImplementedError,
    FrameworkDataAdapter,
    InspectResult,
    RecordNotFoundError,
    UnknownArtifactError,
    UnknownSubstrateError,
)
from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.discovery import ComponentRegistry
from ehp_sn.execution import (
    SubstrateExecutionComposition,
    SubstrateExecutionRegistration,
)
from ehp_sn.experiments import ComponentRef
from ehp_sn.planning import (
    IdentityInput,
    PlanningDeclaration,
    SubstratePlanningComposition,
    SubstratePlanningRegistration,
)
from typer.testing import CliRunner

runner = CliRunner()


# ---------------------------------------------------------------------------
# Synthetic production adapter (no research import)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _Definition:
    """Minimal synthetic stand-in shaped like a registered substrate definition."""

    ref: ComponentRef
    description: str
    output_contract: str

    @property
    def kind(self) -> str:
        return self.ref.kind


def _plan(document: LoadedConfiguration) -> PlanningDeclaration:
    return PlanningDeclaration(
        configuration={"synthetic": True},
        resources=(),
        identity_inputs=(
            IdentityInput(name="variant", value="default"),
            IdentityInput(name="seed", value=42),
        ),
    )


@pytest.fixture()
def adapter(tmp_path) -> FrameworkDataAdapter:
    """A production adapter over synthetic generic dependencies."""
    registry = ComponentRegistry()
    alpha = _Definition(
        ref=ComponentRef.parse("substrate:alpha/v1"),
        description="A synthetic alpha substrate.",
        output_contract="alpha-contract/v1",
    )
    beta = _Definition(
        ref=ComponentRef.parse("substrate:beta/v1"),
        description="A synthetic beta substrate.",
        output_contract="beta-contract/v1",
    )
    registry.register(alpha)
    registry.register(beta)

    composition = SubstratePlanningComposition(
        (SubstratePlanningRegistration(definition=alpha, plan=_plan),)
    )
    execution = SubstrateExecutionComposition(
        (SubstrateExecutionRegistration(definition=alpha, execute=_execute),)
    )
    return FrameworkDataAdapter(
        registry,
        planning_composition=composition,
        execution_composition=execution,
        root=tmp_path,
    )


def _execute(session) -> None:
    """Synthetic producer execution: one generic record, no split."""
    from ehp_sn.execution import GeneratedRecordBody, RealizationKey
    from ehp_sn.planning import IdentityInput

    session.add_record(
        GeneratedRecordBody(
            content={"value": "alpha-record"},
            realization_key=RealizationKey(inputs=(IdentityInput("realization_index", 1),)),
        )
    )


@pytest.fixture()
def use_adapter(adapter: FrameworkDataAdapter) -> None:
    data_module._set_adapter(adapter)
    yield
    data_module._reset_adapter()


# ---------------------------------------------------------------------------
# Command existence and help surface
# ---------------------------------------------------------------------------


def test_data_group_exists() -> None:
    result = runner.invoke(app, ["data", "--help"])
    assert result.exit_code == 0
    for command in ("list", "show", "plan", "build", "validate", "inspect"):
        assert command in result.stdout


@pytest.mark.parametrize(
    "args",
    [
        ["list"],
        ["show", "x"],
        ["plan", "x", "--config", "f.toml"],
        ["build", "x", "--config", "f.toml"],
        ["validate", "x"],
        ["inspect", "x"],
    ],
)
def test_each_command_help(args: list[str]) -> None:
    result = runner.invoke(app, ["data", *args, "--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
    assert "Options" in result.stdout


# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------


def test_list_renders_rows(use_adapter: None) -> None:
    result = runner.invoke(app, ["data", "list"])
    assert result.exit_code == 0
    assert "substrate:alpha/v1" in result.stdout
    assert "substrate:beta/v1" in result.stdout


def test_list_json(use_adapter: None) -> None:
    result = runner.invoke(app, ["data", "list", "--format", "json"])
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["action"] == "list"
    assert len(payload["result"]) == 2


# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------


def test_show_renders(use_adapter: None) -> None:
    result = runner.invoke(app, ["data", "show", "substrate:alpha/v1"])
    assert result.exit_code == 0
    assert "Target: substrate:alpha/v1" in result.stdout
    assert "A synthetic alpha substrate." in result.stdout


def test_show_unknown_substrate_maps_to_exit_4(use_adapter: None) -> None:
    result = runner.invoke(app, ["data", "show", "substrate:missing/v1"])
    assert result.exit_code == 4
    assert "unknown substrate" in result.stderr


# ---------------------------------------------------------------------------
# plan
# ---------------------------------------------------------------------------


def test_plan_requires_config() -> None:
    result = runner.invoke(app, ["data", "plan", "substrate:alpha/v1"])
    assert result.exit_code == 2
    assert "--config" in result.stdout or "--config" in result.stderr


def test_plan_renders(use_adapter: None, tmp_path) -> None:
    """``plan`` delegates to the real adapter and renders the projected result."""
    cfg = tmp_path / "config.toml"
    cfg.write_text('[substrate]\nvariant = "default"\n', encoding="utf-8")
    result = runner.invoke(app, ["data", "plan", "substrate:alpha/v1", "--config", str(cfg)])
    assert result.exit_code == 0
    assert "target: substrate:alpha/v1" in result.stdout
    assert "output: alpha-contract/v1" in result.stdout
    assert "variant: default" in result.stdout
    assert "seed: 42" in result.stdout
    assert "Traceback" not in result.stderr


def test_plan_json_renders_semantic_fields(use_adapter: None, tmp_path) -> None:
    """JSON ``plan`` output is a deterministic projection of semantic fields."""
    cfg = tmp_path / "config.toml"
    cfg.write_text('[substrate]\nvariant = "default"\n', encoding="utf-8")
    result = runner.invoke(
        app, ["data", "plan", "substrate:alpha/v1", "--config", str(cfg), "--format", "json"]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["action"] == "plan"
    assert payload["result"]["target"] == "substrate:alpha/v1"
    assert payload["result"]["output_contract"] == "alpha-contract/v1"
    assert payload["result"]["resources"] == []
    assert payload["result"]["identity"] == [
        {"name": "variant", "value": "default"},
        {"name": "seed", "value": 42},
    ]


def test_plan_unreadable_config_maps_to_exit_4(use_adapter: None, tmp_path) -> None:
    result = runner.invoke(
        app, ["data", "plan", "substrate:alpha/v1", "--config", str(tmp_path / "missing.toml")]
    )
    assert result.exit_code == 4
    assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# Unsupported commands produce the documented controlled response
# ---------------------------------------------------------------------------


def test_build_delegates_to_real_backend(use_adapter: None, tmp_path) -> None:
    """``data build`` delegates to the generic lifecycle, not a placeholder.

    With a synthetic production adapter and a valid config file, build commits a
    logical artifact and reports the committed outcome; it never says
    "not implemented".
    """
    config = tmp_path / "alpha.toml"
    config.write_text("release = 1\n[generation]\nseed = 42\n")
    result = runner.invoke(app, ["data", "build", "substrate:alpha/v1", "--config", str(config)])
    assert result.exit_code == 0
    assert "action: committed" in result.stdout
    assert "artifact-fingerprint:" in result.stdout
    assert "artifact: artifact:alpha/default/v1" in result.stdout
    assert "not yet implemented" not in result.stdout


def test_build_json(use_adapter: None, tmp_path) -> None:
    config = tmp_path / "alpha.toml"
    config.write_text("release = 1\n[generation]\nseed = 42\n")
    result = runner.invoke(
        app, ["data", "build", "substrate:alpha/v1", "--config", str(config), "--format", "json"]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["action"] == "build"
    assert payload["result"]["action"] == "committed"
    assert payload["result"]["target"] == "substrate:alpha/v1"
    assert payload["result"]["artifact_ref"] == "artifact:alpha/default/v1"


def test_build_missing_config_is_controlled() -> None:
    """Building with an unreadable config maps to a controlled exit, no traceback."""
    result = runner.invoke(app, ["data", "build", "substrate:alpha/v1", "--config", "x.toml"])
    assert result.exit_code == 4
    assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# --release: invocation-layer publication coordinate (Target 9)
# ---------------------------------------------------------------------------


def test_build_missing_release_is_controlled(use_adapter: None, tmp_path) -> None:
    """A build with no config release and no --release is a controlled failure.

    Release selection is not auto-assigned: without an invocation-level
    ``--release`` (the canonical source; a config-declared value is only a
    legacy fallback) the build fails cleanly (exit 6) rather than inventing a
    coordinate, and the error points at the canonical source.
    """
    config = tmp_path / "alpha.toml"
    # Scientific config only — no release field, no --release.
    config.write_text('[substrate]\nvariant = "default"\n[generation]\nseed = 42\n')
    result = runner.invoke(app, ["data", "build", "substrate:alpha/v1", "--config", str(config)])
    assert result.exit_code == 6
    assert "requires --release" in result.stderr
    assert "Traceback" not in result.stderr


def test_build_unreadable_config_is_controlled_before_release() -> None:
    """An unreadable config maps to exit 4 before release-coordinate checks."""
    config = "dangling.toml"
    result = runner.invoke(app, ["data", "build", "substrate:alpha/v1", "--config", config])
    assert result.exit_code == 4
    assert "Traceback" not in result.stderr


def test_plan_accepts_release_option(use_adapter: None, tmp_path) -> None:
    """``plan --release 1`` is accepted and delegates to the real adapter."""
    config = tmp_path / "alpha.toml"
    # Scientific config only: no release field.
    config.write_text('[substrate]\nvariant = "default"\n[generation]\nseed = 42\n')
    result = runner.invoke(
        app,
        ["data", "plan", "substrate:alpha/v1", "--config", str(config), "--release", "1"],
    )
    assert result.exit_code == 0
    assert "target: substrate:alpha/v1" in result.stdout
    assert "Traceback" not in result.stderr


def test_build_release_option_selects_the_coordinate(use_adapter: None, tmp_path) -> None:
    """``build --release 1`` with a config containing no release commits to v1.

    Release is selected at the invocation layer, not required in the reusable
    scientific config.
    """
    config = tmp_path / "alpha.toml"
    config.write_text('[substrate]\nvariant = "default"\n[generation]\nseed = 42\n')
    result = runner.invoke(
        app,
        ["data", "build", "substrate:alpha/v1", "--config", str(config), "--release", "1"],
    )
    assert result.exit_code == 0
    assert "action: committed" in result.stdout
    assert "artifact: artifact:alpha/default/v1" in result.stdout
    assert "not yet implemented" not in result.stdout


def test_build_release_overrides_config_release(use_adapter: None, tmp_path) -> None:
    """``--release`` is the highest authority over a config-level release field."""
    config = tmp_path / "alpha.toml"
    config.write_text('release = 9\n[substrate]\nvariant = "default"\n[generation]\nseed = 42\n')
    result = runner.invoke(
        app,
        ["data", "build", "substrate:alpha/v1", "--config", str(config), "--release", "1"],
    )
    assert result.exit_code == 0
    assert "action: committed" in result.stdout
    # The invocation release wins, not the config-level fallback.
    assert "artifact: artifact:alpha/default/v1" in result.stdout
    assert "artifact: artifact:alpha/default/v9" not in result.stdout


@pytest.mark.parametrize("bad", ["0", "-1"])
def test_build_invalid_release_is_a_controlled_usage_error(
    use_adapter: None, tmp_path, bad: str
) -> None:
    """``--release 0`` / ``--release -1`` are controlled CLI errors (exit 2)."""
    config = tmp_path / "alpha.toml"
    config.write_text('[substrate]\nvariant = "default"\n[generation]\nseed = 42\n')
    result = runner.invoke(
        app,
        ["data", "build", "substrate:alpha/v1", "--config", str(config), "--release", bad],
    )
    assert result.exit_code == 2
    assert "--release must be a positive integer" in result.stderr
    assert "Traceback" not in result.stderr


def test_build_non_integer_release_is_a_controlled_usage_error(use_adapter: None, tmp_path) -> None:
    """A non-integer ``--release`` is rejected by typer as a controlled usage error."""
    config = tmp_path / "alpha.toml"
    config.write_text('[substrate]\nvariant = "default"\n[generation]\nseed = 42\n')
    result = runner.invoke(
        app,
        ["data", "build", "substrate:alpha/v1", "--config", str(config), "--release", "abc"],
    )
    assert result.exit_code == 2
    assert "Traceback" not in result.stderr


def test_plan_invalid_release_is_a_controlled_usage_error(use_adapter: None, tmp_path) -> None:
    """Invalid ``--release`` on ``plan`` is a controlled usage error (exit 2)."""
    config = tmp_path / "alpha.toml"
    config.write_text('[substrate]\nvariant = "default"\n')
    result = runner.invoke(
        app,
        ["data", "plan", "substrate:alpha/v1", "--config", str(config), "--release", "0"],
    )
    assert result.exit_code == 2
    assert "Traceback" not in result.stderr


def test_validate_is_controlled_not_implemented() -> None:
    result = runner.invoke(app, ["data", "validate", "example-substrate/v7"])
    assert result.exit_code == 1
    assert "not yet implemented" in result.stderr
    assert "Traceback" not in result.stderr


def test_validate_invalid_level_exit_2() -> None:
    result = runner.invoke(app, ["data", "validate", "x", "--level", "deep"])
    assert result.exit_code == 2


def test_inspect_negative_samples_exit_2() -> None:
    result = runner.invoke(app, ["data", "inspect", "x", "--samples", "-1"])
    assert result.exit_code == 2


def test_inspect_without_record_exit_2() -> None:
    result = runner.invoke(app, ["data", "inspect", "data/interim/x/v1"])
    assert result.exit_code == 2
    assert "requires --record" in result.stderr
    assert "Traceback" not in result.stderr


def test_inspect_positive_samples_is_not_yet_specified() -> None:
    result = runner.invoke(app, ["data", "inspect", "data/interim/x/v1", "--samples", "3"])
    assert result.exit_code == 1
    assert "not yet specified" in result.stderr
    assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# inspect: exact-record deterministic path
# ---------------------------------------------------------------------------


class _StubInspectAdapter(FrameworkDataAdapter):
    """Adapter whose ``inspect`` returns a fixed generic projection.

    Proves the CLI delegates to the adapter and renders the projection without
    any figure code; the exact-artifact/record mechanics are covered at the
    adapter layer.
    """

    def __init__(self, *, missing: bool = False) -> None:
        self._missing = missing

    def inspect(self, artifact: str, record_id: str) -> InspectResult:
        if self._missing:
            raise RecordNotFoundError(f"record {record_id!r} not found in committed artifact {artifact}")
        return InspectResult(
            artifact_ref="artifact:alpha/v1",
            record_id=record_id,
            schema_ref="alpha-contract/v1",
            content={"value": 7},
        )


@pytest.fixture()
def use_stub_inspect_adapter() -> None:
    data_module._set_adapter(_StubInspectAdapter())  # type: ignore[arg-type]
    yield
    data_module._reset_adapter()


def test_inspect_exact_record_text(use_stub_inspect_adapter: None) -> None:
    result = runner.invoke(app, ["data", "inspect", "artifact:alpha/v1", "--record", "abc123"])
    assert result.exit_code == 0
    assert "artifact: artifact:alpha/v1" in result.stdout
    assert "record_id: abc123" in result.stdout
    assert "schema_ref: alpha-contract/v1" in result.stdout


def test_inspect_exact_record_json(use_stub_inspect_adapter: None) -> None:
    result = runner.invoke(
        app, ["data", "inspect", "artifact:alpha/v1", "--record", "abc123", "--format", "json"]
    )
    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["action"] == "inspect"
    assert payload["result"]["record_id"] == "abc123"
    assert payload["result"]["artifact"] == "artifact:alpha/v1"
    assert payload["result"]["schema_ref"] == "alpha-contract/v1"


def test_inspect_delegates_exact_record_id(use_stub_inspect_adapter: None) -> None:
    """The exact record identifier is passed through unchanged (one lookup)."""
    result = runner.invoke(app, ["data", "inspect", "artifact:alpha/v1", "--record", "exact-record-9"])
    assert result.exit_code == 0
    assert "record_id: exact-record-9" in result.stdout


def test_inspect_unknown_record_maps_to_controlled_error() -> None:
    """A missing record surfaces as the controlled ``record_not_found`` (exit 4)."""
    data_module._set_adapter(_StubInspectAdapter(missing=True))  # type: ignore[arg-type]
    try:
        result = runner.invoke(app, ["data", "inspect", "artifact:alpha/v1", "--record", "missing"])
    finally:
        data_module._reset_adapter()
    assert result.exit_code == 4
    assert "not found" in result.stderr
    assert "Traceback" not in result.stderr


def test_default_backend_plan_is_real_not_not_implemented() -> None:
    # The real backend ``plan`` is not "not implemented": it is a real,
    # registry-backed projection. With the production (possibly empty) registry
    # and an absent config file, the operation surfaces as a controlled
    # referenced-input failure (exit 4: unreadable config or unknown target),
    # never a not-implemented message or a traceback.
    data_module._reset_adapter()
    result = runner.invoke(app, ["data", "plan", "substrate:alpha/v1", "--config", "x.toml"])
    assert result.exit_code == 4
    assert "not yet implemented" not in result.stderr
    assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# Controlled failure categories and exit codes
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("exc", "expected_code", "expected_text"),
    [
        (UnknownSubstrateError("no such substrate"), 4, "no such substrate"),
        (ConfigurationUnreadableError("cannot read config"), 4, "cannot read config"),
        (ConfigurationInvalidError("bad schema"), 3, "bad schema"),
        (UnknownArtifactError("no such artifact"), 4, "no such artifact"),
        (RecordNotFoundError("record missing"), 4, "record missing"),
        (DataNotImplementedError("not implemented"), 1, "not implemented"),
    ],
)
def test_error_categories_map_to_exit_codes(
    exc: DataCliError, expected_code: int, expected_text: str
) -> None:
    class RaisingAdapter(FrameworkDataAdapter):
        def __init__(self) -> None:
            pass

        def list(self):
            raise exc

    data_module._set_adapter(RaisingAdapter())  # type: ignore[arg-type]
    result = runner.invoke(app, ["data", "list"])
    data_module._reset_adapter()
    assert result.exit_code == expected_code
    assert expected_text in result.stderr
    assert "Traceback" not in result.stderr


# ---------------------------------------------------------------------------
# Producer neutrality
# ---------------------------------------------------------------------------


def test_cli_source_has_no_producer_conditionals() -> None:
    """The CLI module must not name producer families or branch on them."""
    import inspect as _inspect

    source = _inspect.getsource(data_module)
    for producer in ("dagflow", "maze-nd"):
        assert producer not in source.lower()


def test_cli_source_has_no_figure_branches_or_imports() -> None:
    """The ``data inspect`` CLI must be free of figure-specific branches and imports.

    ``data inspect ARTIFACT --record RECORD_ID`` (P0R-3) is generic: it must
    not require a figure framework import and must not branch on a figure
    concept. Figure rendering is a separate, later figure phase.
    """
    import inspect as _inspect

    source = _inspect.getsource(data_module)
    import_lines = [
        line for line in source.splitlines() if line.lstrip().startswith(("import ", "from "))
    ]
    assert not any(
        line.lstrip().startswith(("from ehp_sn.figures", "from matplotlib", "import matplotlib"))
        for line in import_lines
    )
    for token in ("FigureSpec", "FigureProjection", "matplotlib", "renderer"):
        assert token.lower() not in source.lower()
