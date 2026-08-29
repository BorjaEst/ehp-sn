"""Integration regression — DungeonGen is discoverable, plannable, and executable.

Since Phase 5.3 the DungeonGen execution operation is registered in
``ehp_research`` against the generic execution composition. This proves:

* the generic ``ehp-sn data build substrate:dungeongen/v1 --release 1`` commits
  a durable release containing normalized raster-topology records, the complete
  production-lineage resource, and the standard manifest/config/provenance/
  index — with **zero** family-specific changes to generic ``ehp_sn`` planning,
  execution, materialization, publication, or CLI orchestration;
* a second identical build reuses the committed release without invoking the
  external generator again;
* removing the execution registration produces the controlled
  :class:`~ehp_sn.execution.MissingExecutionCapabilityError` (exit 6) through
  the same generic path.

The real upstream generator is deterministic and fast; tests seed the executor's
native generator with a bounded fixture so the generic build → execution →
materialization → publication lifecycle is exercised without depending on the
full ``--release 1`` population. The real committed release (the repository
profile ``config/data/dungeongen/independent-realizations.toml``) is the
documented manual acceptance command.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from ehp_research.substrates import dungeongen
from ehp_sn.cli import app
from ehp_sn.cli.data_adapter import DataOperationError, FrameworkDataAdapter
from ehp_sn.discovery import effective_registry
from ehp_sn.planning import effective_planning_composition
from typer.testing import CliRunner

#: Repo root, located relative to this test file (…/tests/integration/ → repo).
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DUNGEONGEN_PROFILE = _REPO_ROOT / "config" / "data" / "dungeongen" / "independent-realizations.toml"
_INTERIM_ROOT = _REPO_ROOT / "data" / "interim"

runner = CliRunner()


def _shared_room_cells() -> dict[tuple[int, int], int]:
    """A fixed valid 2x3 room (6 passable states) for deterministic builds."""
    return {(x, y): 1 for x in range(3) for y in range(2)}  # CellType.ROOM


def _seed_generator(monkeypatch) -> None:
    monkeypatch.setattr(
        dungeongen.execution,
        "generate_native",
        lambda config, seed: dungeongen.NativeCandidate(
            dungeon=None, cells=_shared_room_cells(), seed=seed
        ),
    )


def _adapter(tmp_path, *, execute=True):
    from ehp_research.registration import execution_registrations
    from ehp_sn.execution import SubstrateExecutionComposition

    composition = (
        SubstrateExecutionComposition(execution_registrations())
        if execute
        else SubstrateExecutionComposition(())
    )
    return FrameworkDataAdapter(
        effective_registry(),
        planning_composition=effective_planning_composition(),
        execution_composition=composition,
        root=tmp_path,
    )


def _fixture_profile(tmp_path) -> str:
    """Write a small DungeonGen fixture profile with real frozen identity.

    The repository profile (record_count 500) is too large for an offline test;
    this writes an equivalent ``general`` profile with the real frozen
    dependency/protocol/profile references and a small retry-tolerant budget.
    """
    profile = tmp_path / "dungeongen-fixture.toml"
    profile.write_text(
        """[substrate]
    variant = "general"

[generator]
    dependency = "git:benjcooley/dungeongen@2d228f5d3f82ccaa4666b087942100e7800fb069"
    protocol   = "dungeongen/generation/v1"
    profile    = "dungeongen/profile/general/v1"

    [generator.params]
        archetype = "classic"
        size = "medium"
        room_size_bias = 0.0
        round_room_chance = 0.15
        hall_chance = 0.1
        density = 0.5
        symmetry = "none"
        symmetry_break = 0.2
        linearity = 0.3
        loop_factor = 0.3
        passage_width = 1
        winding = 0.0
        extra_room_connections = 0.2
        extra_passage_junctions = 0.15
        levels = 1
        stair_frequency = 0.1
        water_enabled = false
        water_threshold = 0.15

[conversion]
    policy = "dungeongen:conversion/raster/v1"

[acceptance]
    policy = "dungeongen:acceptance/size-and-connected/v1"
    require_connected = true

[generation]
    attempt_budget = 10
    seed = 0
    record_count = 12
    role = "topology-candidate"

[topology]
    duplicate_policy = "allow"
    [topology.size_policy]
        minimum_height = 2
        maximum_height = 12
        minimum_width = 2
        maximum_width = 12
        minimum_states = 4
        maximum_states = 1000
""",
        encoding="utf-8",
    )
    return str(profile)


def test_dungeongen_is_registered_executable() -> None:
    """DungeonGen maps to a real execution operation by identity."""
    registry = effective_registry()
    definition = registry.resolve("substrate:dungeongen/v1")
    from ehp_research.registration import execution_registrations
    from ehp_sn.execution import SubstrateExecutionComposition

    composition = SubstrateExecutionComposition(execution_registrations())
    assert composition.contains(definition)
    assert composition.execute(definition) is dungeongen.execute


def test_python_dungeongen_build_commits_release(tmp_path, monkeypatch) -> None:
    """A ready plan with an execution capability commits a durable release."""
    from ehp_sn.artifacts import inspect_release, release_path
    from ehp_sn.planning import ReleaseCoordinate

    _seed_generator(monkeypatch)
    profile = _fixture_profile(tmp_path)
    service = _adapter(tmp_path)
    outcome = service.build("substrate:dungeongen/v1", profile, release=1)

    assert outcome.action == "committed"
    assert outcome.target == "substrate:dungeongen/v1"
    assert outcome.output_contract == "raster-topology/v1"

    coordinate = ReleaseCoordinate(family="dungeongen", variant="general", release=1)
    location = release_path(tmp_path, coordinate)
    assert inspect_release(tmp_path, coordinate).committed_exists is True

    manifest = json.loads((location / "manifest.json").read_text(encoding="utf-8"))
    names = {r["name"] for r in manifest["resources"]}
    assert "resolved-config" in names
    assert "provenance" in names
    assert "index" in names
    assert "payloads" in names
    assert "dungeongen-lineage" in names
    assert (location / "config.resolved.toml").exists()
    assert (location / "resources" / "dungeongen-lineage.data").exists()

    index_entries = [
        json.loads(line) for line in (location / "index.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    # record_count=12 logical topologies (all identical content under the fixture,
    # still 12 separate records under `allow`).
    assert len(index_entries) == 12


def test_second_identical_build_reuses(tmp_path, monkeypatch) -> None:
    """A second identical build reuses the committed release (no re-generation)."""
    _seed_generator(monkeypatch)
    profile = _fixture_profile(tmp_path)
    adapter = _adapter(tmp_path)
    first = adapter.build("substrate:dungeongen/v1", profile, release=1)
    assert first.action == "committed"
    second = adapter.build("substrate:dungeongen/v1", profile, release=1)
    assert second.action == "reused"


def test_removing_registration_yields_controlled_missing_capability(tmp_path, monkeypatch) -> None:
    """Without the execution registration the generic path fails controlled (exit 6)."""
    _seed_generator(monkeypatch)
    profile = _fixture_profile(tmp_path)
    adapter = _adapter(tmp_path, execute=False)
    with pytest.raises(DataOperationError) as exc:
        adapter.build("substrate:dungeongen/v1", profile, release=1)
    message = str(exc.value.message).lower()
    assert "execution" in message or "operation" in message


def test_cli_dungeongen_commit_isolated_root(tmp_path, monkeypatch) -> None:
    """The full accepted CLI command commits into the isolated root only."""
    from ehp_sn.cli import data as data_module

    _seed_generator(monkeypatch)
    profile = _fixture_profile(tmp_path)
    data_module._set_adapter(_adapter(tmp_path))
    try:
        result = runner.invoke(
            app,
            [
                "data",
                "build",
                "substrate:dungeongen/v1",
                "--config",
                profile,
                "--release",
                "1",
            ],
        )
    finally:
        data_module._reset_adapter()

    assert result.exit_code == 0
    assert "Traceback" not in result.stderr
    isolated_release = tmp_path / "dungeongen" / "general" / "v1"
    assert (isolated_release / "manifest.json").exists()
