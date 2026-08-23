"""CLI behavior tests for the ``ehp-sn data`` command group.

These tests focus on CLI behavior (CLI-001): command existence, argument and
option interfaces, help text, delegation through the production
:class:`~ehp_sn.cli.data_adapter.FrameworkDataAdapter`, output formatting,
failure formatting, and exit codes.

The implemented commands (``list``/``show``/``plan``) run against a real
``FrameworkDataAdapter`` built over **synthetic** generic dependencies (a
registry with neutral ``alpha``/``beta`` substrate definitions and a composed
planning resolver). No research package is imported; no test-local fake service
stands in for the adapter boundary.

The commands that are part of the established surface but intentionally
unsupported (``build``/``validate``/``inspect``) are asserted to produce the
documented controlled not-implemented response (exit 1), which the CLI owns
directly rather than delegating to a placeholder adapter method.
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
    UnknownSubstrateError,
)
from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.discovery import ComponentRegistry
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
def adapter() -> FrameworkDataAdapter:
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
    return FrameworkDataAdapter(registry, planning_composition=composition)


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


def test_build_is_controlled_not_implemented() -> None:
    result = runner.invoke(app, ["data", "build", "substrate:alpha/v1", "--config", "x.toml"])
    assert result.exit_code == 1
    assert "not yet implemented" in result.stderr
    assert "Traceback" not in result.stderr


def test_validate_is_controlled_not_implemented() -> None:
    result = runner.invoke(app, ["data", "validate", "example-substrate/v7"])
    assert result.exit_code == 1
    assert "not yet implemented" in result.stderr
    assert "Traceback" not in result.stderr


def test_inspect_is_controlled_not_implemented() -> None:
    result = runner.invoke(app, ["data", "inspect", "example-substrate/v7"])
    assert result.exit_code == 1
    assert "not yet implemented" in result.stderr
    assert "Traceback" not in result.stderr


def test_validate_invalid_level_exit_2() -> None:
    result = runner.invoke(app, ["data", "validate", "x", "--level", "deep"])
    assert result.exit_code == 2


def test_inspect_negative_samples_exit_2() -> None:
    result = runner.invoke(app, ["data", "inspect", "x", "--samples", "-1"])
    assert result.exit_code == 2


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
