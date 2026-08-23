"""Integration tests — the complete cross-package discovery path.

This is where ``ehp_sn`` and ``ehp_research`` meet (root-level integration
scope). It proves the production composition path end to end:

    real ehp_research registration
        ↓  (entry-point provider, group ``ehp_sn.providers``)
    real generic ehp_sn registry (effective_registry)
        ↓
    FrameworkDataService
        ↓
    ``data list`` / ``data show``

Expected metadata is **derived from the registered authoritative definitions**,
not from a second hard-coded catalogue, so the framework, research, adapter, and
integration tests do not each re-state what Dagflow or Maze-ND mean (test a
semantic fact strongly at its owner; downstream tests derive from it).
"""

from __future__ import annotations

import pytest
from ehp_research.substrates.dagflow import DAGFLOW_DEFINITION
from ehp_research.substrates.maze_nd import MAZE_ND_DEFINITION
from ehp_sn.cli import app
from ehp_sn.cli._data_service import UnknownSubstrateError
from ehp_sn.cli.data_adapter import FrameworkDataService
from ehp_sn.discovery import effective_registry
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture()
def service() -> FrameworkDataService:
    """The production composition: effective registry over FrameworkDataService."""
    return FrameworkDataService(effective_registry())


# ---------------------------------------------------------------------------
# list exposes the installed research definitions
# ---------------------------------------------------------------------------


def test_data_list_exposes_dagflow(service: FrameworkDataService) -> None:
    listed = {row.ref: row for row in service.list()}
    row = listed["substrate:dagflow/v1"]

    # Derived from the authoritative definition, not a hard-coded copy.
    assert row.ref == DAGFLOW_DEFINITION.ref.canonical
    assert row.family == DAGFLOW_DEFINITION.ref.name
    assert row.output == DAGFLOW_DEFINITION.output_contract


def test_data_list_exposes_maze_nd(service: FrameworkDataService) -> None:
    listed = {row.ref: row for row in service.list()}
    row = listed["substrate:maze-nd/v1"]

    assert row.ref == MAZE_ND_DEFINITION.ref.canonical
    assert row.family == MAZE_ND_DEFINITION.ref.name
    assert row.output == MAZE_ND_DEFINITION.output_contract


def test_list_uses_provider_metadata(service: FrameworkDataService) -> None:
    listed = {row.ref: row for row in service.list()}

    assert listed["substrate:dagflow/v1"].output == DAGFLOW_DEFINITION.output_contract
    assert listed["substrate:maze-nd/v1"].output == MAZE_ND_DEFINITION.output_contract


# ---------------------------------------------------------------------------
# show resolves the authoritative definitions
# ---------------------------------------------------------------------------


def test_show_dagflow_succeeds(service: FrameworkDataService) -> None:
    result = service.show("substrate:dagflow/v1")

    assert result.ref == DAGFLOW_DEFINITION.ref.canonical
    assert result.description == DAGFLOW_DEFINITION.description


def test_show_maze_nd_succeeds(service: FrameworkDataService) -> None:
    result = service.show("substrate:maze-nd/v1")

    assert result.ref == MAZE_ND_DEFINITION.ref.canonical
    assert result.description == MAZE_ND_DEFINITION.description


def test_show_unknown_substrate_receives_controlled_error(service: FrameworkDataService) -> None:
    with pytest.raises(UnknownSubstrateError):
        service.show("substrate:not-registered/v1")


def test_show_wrong_kind_receives_controlled_error(service: FrameworkDataService) -> None:
    # The research provider registers only substrates; a task-shaped reference
    # must be rejected by ``show`` (which requires a substrate target).
    with pytest.raises(UnknownSubstrateError):
        service.show("task:not-present/v1")


# ---------------------------------------------------------------------------
# Real CLI invocation over the real composition path
# ---------------------------------------------------------------------------


def test_cli_data_list_output_and_status() -> None:
    """A real ``ehp-sn data list`` call lists the installed definitions with status 0.

    This checks meaningful output and exit status, not exact whitespace (output
    formatting is not itself an authoritative contract).
    """
    result = runner.invoke(app, ["data", "list"])

    assert result.exit_code == 0
    assert "substrate:dagflow/v1" in result.stdout
    assert "substrate:maze-nd/v1" in result.stdout


def test_cli_data_show_dagflow_succeeds() -> None:
    result = runner.invoke(app, ["data", "show", "substrate:dagflow/v1"])

    assert result.exit_code == 0
    assert "Target: substrate:dagflow/v1" in result.stdout
    assert DAGFLOW_DEFINITION.description in result.stdout


def test_cli_data_show_unknown_substrate_is_controlled() -> None:
    result = runner.invoke(app, ["data", "show", "substrate:not-registered/v1"])

    assert result.exit_code == 4
    assert "unknown substrate" in result.stderr
    assert "Traceback" not in result.stderr
