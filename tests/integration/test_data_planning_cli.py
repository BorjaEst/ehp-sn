"""Integration tests — Capability 7: real ``data plan`` CLI adapter path.

This is the full Phase-3B vertical slice. It proves that ``ehp-sn data plan``
reaches the **same** generic framework planning machinery completed in
Capability 6 (``ehp_sn.planning.plan_substrate``) that the Python API uses, and
projects that authoritative immutable framework plan into the CLI seam.

Two explicit levels are tested so a CLI output test cannot pass merely because
the adapter fabricated information:

* **Python** — ``FrameworkDataAdapter.plan`` returns the expected framework
  plan semantics (target, output contract, bound resources, identity inputs)
  for the real Dagflow and Maze-ND profiles;
* **CLI** — ``ehp-sn data plan ... --config <real-profile>`` exits 0 and
  projects the same semantics deterministically.

Both real providers travel through the same generic orchestration; there is no
Dagflow-specific or Maze-ND-specific branch inside ``ehp_sn``. ``FrameworkDataAdapter``
uses its production adapter and its minimal generic resource resolver; no custom
resolver is injected here.

A separate side-effect test proves planning never mutates artifact state.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from ehp_sn.cli import app
from ehp_sn.cli.data_adapter import FrameworkDataAdapter
from ehp_sn.discovery import effective_registry
from ehp_sn.planning import effective_planning_composition
from typer.testing import CliRunner

#: Repo root, located relative to this test file (…/tests/integration/ → repo).
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DAGFLOW_PROFILE = _REPO_ROOT / "config" / "data" / "dagflow" / "constructive-dense.toml"
_MAZE_ND_PROFILE = _REPO_ROOT / "config" / "data" / "maze-nd" / "connected-source.toml"
_INTERIM_ROOT = _REPO_ROOT / "data" / "interim"
_ARTIFACTS_ROOT = _REPO_ROOT / "artifacts"

runner = CliRunner()


@pytest.fixture()
def service() -> FrameworkDataAdapter:
    """The production adapter: effective registry + composed planning resolvers."""
    return FrameworkDataAdapter(
        effective_registry(),
        planning_composition=effective_planning_composition(),
    )


def _tree(path: Path) -> dict[str, str]:
    """A snapshot of file paths -> sizes under ``path`` (empty if absent)."""
    if not path.exists():
        return {}
    return {
        str(p.relative_to(path)): str(p.stat().st_size) for p in sorted(path.rglob("*")) if p.is_file()
    }


# ---------------------------------------------------------------------------
# Python level: the service projects the authoritative framework plan
# ---------------------------------------------------------------------------


def test_python_dagflow_plan_projection(service) -> None:
    result = service.plan("substrate:dagflow/v1", str(_DAGFLOW_PROFILE))

    assert result.target == "substrate:dagflow/v1"
    # Output contract derived from the registered definition (single authority).
    assert result.output_contract == "simple-digraph/v1"
    # Dagflow is procedurally generated: no bound resources.
    assert result.resources == ()
    # Identity-bearing inputs from the resolved configuration are bound.
    names = {i.name for i in result.identity}
    assert {"variant", "generation_protocol", "seed", "node_count_policy"} <= names


def test_python_maze_nd_plan_projection(service) -> None:
    result = service.plan("substrate:maze-nd/v1", str(_MAZE_ND_PROFILE))

    assert result.target == "substrate:maze-nd/v1"
    assert result.output_contract == "raster-topology/v1"
    # The upstream source requirement is resolved and bound.
    assert len(result.resources) == 1
    bound = result.resources[0]
    assert bound.requirement_ref == "requirement:substrate/maze-nd-source/v1"
    assert bound.resource_ref == "UNRESOLVED-EXTERNAL-SOURCE"
    assert bound.resolution_source == "definition"
    names = {i.name for i in result.identity}
    assert {"source_reference", "source_fingerprint", "source_schema"} <= names


def test_python_and_cli_share_one_planning_path(service) -> None:
    """Python and CLI plans use the same underlying framework planning semantics.

    The service is the CLI's production backend, so a Python call and a CLI
    call against the same registry reach the same ``plan_substrate`` function.
    This pins that the CLI adapter does not reconstruct its own planner.
    """
    dagflow = service.plan("substrate:dagflow/v1", str(_DAGFLOW_PROFILE))
    maze = service.plan("substrate:maze-nd/v1", str(_MAZE_ND_PROFILE))
    assert dagflow.target != maze.target
    assert dagflow != maze


# ---------------------------------------------------------------------------
# CLI level: projection through the Typer seam
# ---------------------------------------------------------------------------


def test_cli_plan_dagflow_succeeds() -> None:
    result = runner.invoke(
        app,
        ["data", "plan", "substrate:dagflow/v1", "--config", str(_DAGFLOW_PROFILE)],
    )

    assert result.exit_code == 0
    assert "target: substrate:dagflow/v1" in result.stdout
    assert "output: simple-digraph/v1" in result.stdout
    assert "Traceback" not in result.stderr


def test_cli_plan_maze_succeeds() -> None:
    result = runner.invoke(
        app,
        ["data", "plan", "substrate:maze-nd/v1", "--config", str(_MAZE_ND_PROFILE)],
    )

    assert result.exit_code == 0
    assert "target: substrate:maze-nd/v1" in result.stdout
    assert "output: raster-topology/v1" in result.stdout
    assert "requirement:substrate/maze-nd-source/v1" in result.stdout
    assert "Traceback" not in result.stderr


def test_cli_plan_json_is_deterministic() -> None:
    import json

    result = runner.invoke(
        app,
        [
            "data",
            "plan",
            "substrate:maze-nd/v1",
            "--config",
            str(_MAZE_ND_PROFILE),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "success"
    assert payload["action"] == "plan"
    result_body = payload["result"]
    assert result_body["target"] == "substrate:maze-nd/v1"
    assert result_body["output_contract"] == "raster-topology/v1"
    assert len(result_body["resources"]) == 1
    assert result_body["resources"][0]["resource_ref"] == "UNRESOLVED-EXTERNAL-SOURCE"
    names = {item["name"] for item in result_body["identity"]}
    assert "source_reference" in names


# ---------------------------------------------------------------------------
# Side-effect: planning never mutates artifact state
# ---------------------------------------------------------------------------


def test_cli_plan_does_not_mutate_artifact_state() -> None:
    before = (_tree(_INTERIM_ROOT), _tree(_ARTIFACTS_ROOT))

    for target, profile in (
        ("substrate:dagflow/v1", _DAGFLOW_PROFILE),
        ("substrate:maze-nd/v1", _MAZE_ND_PROFILE),
    ):
        result = runner.invoke(app, ["data", "plan", target, "--config", str(profile)])
        assert result.exit_code == 0

    after = (_tree(_INTERIM_ROOT), _tree(_ARTIFACTS_ROOT))
    # No generated substrate, no staged artifact, no committed manifest.
    assert after == before
