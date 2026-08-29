"""Integration tests — the complete cross-package discovery path.

This is where ``ehp_sn`` and ``ehp_research`` meet (root-level integration
scope). It proves the production composition path end to end:

    real ehp_research registration
        ↓  (entry-point provider, group ``ehp_sn.providers``)
    real generic ehp_sn registry (effective_registry)
        ↓
    FrameworkDataAdapter
        ↓
    ``data list`` / ``data show``

Expected metadata is **derived from the registered authoritative definitions**,
not from a second hard-coded catalogue, so the framework, research, adapter, and
integration tests do not each re-state what Dagflow or Maze-ND mean (test a
semantic fact strongly at its owner; downstream tests derive from it).
"""

from __future__ import annotations

from pathlib import Path

import pytest
from ehp_research.substrates.dagflow import DAGFLOW_DEFINITION
from ehp_research.substrates.maze_nd import MAZE_ND_DEFINITION
from ehp_sn.cli import app
from ehp_sn.cli.data_adapter import FrameworkDataAdapter, UnknownSubstrateError
from ehp_sn.discovery import effective_registry
from ehp_sn.execution import effective_execution_composition
from ehp_sn.planning import effective_planning_composition
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture()
def service() -> FrameworkDataAdapter:
    """The production adapter: effective registry + composed planning/execution."""
    return FrameworkDataAdapter(
        effective_registry(),
        planning_composition=effective_planning_composition(),
        execution_composition=effective_execution_composition(),
    )


# ---------------------------------------------------------------------------
# list exposes the installed research definitions
# ---------------------------------------------------------------------------


def test_data_list_exposes_dagflow(service: FrameworkDataAdapter) -> None:
    listed = {row.ref: row for row in service.list()}
    row = listed["substrate:dagflow/v1"]

    # Derived from the authoritative definition, not a hard-coded copy.
    assert row.ref == DAGFLOW_DEFINITION.ref.canonical
    assert row.family == DAGFLOW_DEFINITION.ref.name
    assert row.output == DAGFLOW_DEFINITION.output_contract


def test_data_list_exposes_maze_nd(service: FrameworkDataAdapter) -> None:
    listed = {row.ref: row for row in service.list()}
    row = listed["substrate:maze-nd/v1"]

    assert row.ref == MAZE_ND_DEFINITION.ref.canonical
    assert row.family == MAZE_ND_DEFINITION.ref.name
    assert row.output == MAZE_ND_DEFINITION.output_contract


def test_list_uses_provider_metadata(service: FrameworkDataAdapter) -> None:
    listed = {row.ref: row for row in service.list()}

    assert listed["substrate:dagflow/v1"].output == DAGFLOW_DEFINITION.output_contract
    assert listed["substrate:maze-nd/v1"].output == MAZE_ND_DEFINITION.output_contract


# ---------------------------------------------------------------------------
# show resolves the authoritative definitions
# ---------------------------------------------------------------------------


def test_show_dagflow_succeeds(service: FrameworkDataAdapter) -> None:
    result = service.show("substrate:dagflow/v1")

    assert result.ref == DAGFLOW_DEFINITION.ref.canonical
    assert result.description == DAGFLOW_DEFINITION.description


def test_show_maze_nd_succeeds(service: FrameworkDataAdapter) -> None:
    result = service.show("substrate:maze-nd/v1")

    assert result.ref == MAZE_ND_DEFINITION.ref.canonical
    assert result.description == MAZE_ND_DEFINITION.description


def test_show_unknown_substrate_receives_controlled_error(
    service: FrameworkDataAdapter,
) -> None:
    with pytest.raises(UnknownSubstrateError):
        service.show("substrate:not-registered/v1")


def test_show_wrong_kind_receives_controlled_error(service: FrameworkDataAdapter) -> None:
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


# ---------------------------------------------------------------------------
# Real CLI exact-record data inspect over a committed artifact (P0R-3)
# ---------------------------------------------------------------------------


def _build_committed_dagflow(tmp_path: Path) -> tuple[Path, str]:
    """Commit a small deterministic Dagflow artifact and return ``(release, record_id)``.

    Uses the real installed research producer and the generic build lifecycle
    rooted at ``tmp_path`` — no fixture replaces the provider's execution path.
    """
    import tomli_w
    from ehp_sn.artifacts import build_substrate
    from ehp_sn.planning import ResolvedResource, ResourceResolutionError

    class _Resolver:
        def resolve(self, requirement):
            if requirement.definition_resource_ref is None:
                raise ResourceResolutionError(f"no exact reference for {requirement.ref!r}")
            return ResolvedResource(
                requirement_ref=requirement.ref,
                resource_ref=requirement.definition_resource_ref,
                resolution_source="definition",
            )

    profile = {
        "substrate": {"variant": "single-terminal"},
        "generation": {"protocol": "constructive-forward/v1", "seed": 7},
        "graph": {"node_count": 6, "additional_edge_probability": 0.20},
        "splits": {"train": {"count": 2}, "validation": {"count": 1}, "test": {"count": 1}},
        "release": 1,
    }
    config_path = tmp_path / "dagflow.toml"
    config_path.write_text(tomli_w.dumps(profile), encoding="utf-8")

    outcome = build_substrate(
        registry=effective_registry(),
        planning_composition=effective_planning_composition(),
        execution_composition=effective_execution_composition(),
        target="substrate:dagflow/v1",
        config=str(config_path),
        resource_resolver=_Resolver(),
        root=tmp_path / "interim",
        release=1,
    )
    artifact = outcome.artifact
    return artifact.location, artifact.records[0].record_id


def test_cli_data_inspect_committed_artifact_exact_record(tmp_path) -> None:
    """A real ``ehp-sn data inspect`` returns the exact record of a committed artifact.

    Exercises the full required path: installed provider entry points →
    effective registry → committed substrate artifact → generic exact-record
    ``data inspect ARTIFACT --record RECORD_ID`` → exact logical record — with
    no figure framework import required anywhere in the path.
    """
    release_dir, record_id = _build_committed_dagflow(tmp_path)

    result = runner.invoke(
        app, ["data", "inspect", str(release_dir), "--record", record_id, "--format", "json"]
    )

    assert result.exit_code == 0, result.stderr
    assert "Traceback" not in result.stderr
    import json

    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["action"] == "inspect"
    assert payload["result"]["record_id"] == record_id
    assert payload["result"]["schema_ref"] == "simple-digraph/v1"
    assert {"node_count", "edges"} == set(payload["result"]["content"].keys())
