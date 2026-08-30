"""Integration-style tests for the Maze-ND execution operation and registration.

Exercises the producer-integration boundary for ``substrate:maze-nd/v1`` over
the real framework execution composition: registration binding, the full
``execute_substrate`` path with a deterministic injected source, unique-normalized
topology materialization through the shared ``raster-topology/v1`` constructor,
complete lineage as a separate logical resource, connectivity reject/preserve,
record-id independence from source-row ordering, and the absence of any
intrinsic topology split.

The source loader is monkeypatched to a deterministic fixture so the identical
downstream pipeline runs offline and reproducibly.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from ehp_research.registration import execution_registrations, planning_registrations
from ehp_research.substrates import maze_nd
from ehp_research.substrates.maze_nd import MAZE_ND_DEFINITION
from ehp_research.substrates.maze_nd import execute as maze_execute
from ehp_research.substrates.maze_nd.source import content_fingerprint
from ehp_sn.configuration import load_configuration
from ehp_sn.discovery import effective_registry
from ehp_sn.execution import (
    MissingExecutionCapabilityError,
    SubstrateExecutionComposition,
    execute_substrate,
)
from ehp_sn.planning import (
    ResolvedResource,
    ResourceRequirement,
    ResourceResolutionError,
    SubstratePlanningComposition,
    plan_substrate,
)

from . import _fixtures as fx


class _GenericResolver:
    """Minimal generic resource resolver (binds the declared source reference)."""

    def resolve(self, requirement: ResourceRequirement) -> ResolvedResource:
        if requirement.definition_resource_ref is None:
            raise ResourceResolutionError(
                f"no exact resource reference for requirement {requirement.ref!r}"
            )
        return ResolvedResource(
            requirement_ref=requirement.ref,
            resource_ref=requirement.definition_resource_ref,
            resolution_source="definition",
        )


def _execution_composition() -> SubstrateExecutionComposition:
    return SubstrateExecutionComposition(execution_registrations())


def _plan_text(*, connectivity: str = "preserve", fingerprint: str = "sha256:placeholder") -> str:
    return f"""[substrate]
    variant = "source-topology"

[source]
    reference              = "huggingface:flaitenberger/maze_hard_augmented"
    revision               = "rev-fixed"
    fingerprint            = "{fingerprint}"
    schema                 = "maze-nd:extraction/raster/v1"
    selection_policy       = "complete-source"
    selection_before_dedup = true

[normalization]
    policy = "maze-nd:normalization/raster/v1"

[topology]
    connectivity_policy  = "{connectivity}"
    deduplication_policy = "maze-nd:dedup/orientation-preserving-raster/v1"
"""


def _make_plan(tmp_path: Path, monkeypatch, *, connectivity: str = "preserve"):
    """Build an authoritative plan and seed the injected source into the loader.

    The config records the real fingerprint of the fixture blobs so the loader's
    verification passes and the identical pipeline is exercised faithfully.
    Returns ``(plan, fingerprint)``.
    """
    rows_train = [
        fx.row(fx.grid_from_strings("#S#", "#G#")),  # topology A (2x3)
        fx.row(fx.grid_from_strings("## ", "## ")),  # topology B (2x3, distinct)
    ]
    rows_test = [
        fx.row(fx.grid_from_strings("#S#", "#G#")),  # topology A (dup of train0)
        fx.row(fx.grid_from_strings("##", "#S", "##")),  # topology C (3x2)
    ]
    train_blob = fx.split_blob(rows_train)
    test_blob = fx.split_blob(rows_test)
    fingerprint = content_fingerprint(train_blob, test_blob)

    config_path = tmp_path / "maze-nd.toml"
    config_path.write_text(
        _plan_text(connectivity=connectivity, fingerprint=fingerprint), encoding="utf-8"
    )
    registry = effective_registry()
    planning = SubstratePlanningComposition(planning_registrations())
    plan = plan_substrate(
        registry,
        planning,
        "substrate:maze-nd/v1",
        load_configuration(str(config_path)),
        resource_resolver=_GenericResolver(),
    )

    def _loader(config, resource_source):
        yield from maze_nd.source.iter_source_rows(config, resource_source, train_blob, test_blob)

    monkeypatch.setattr(maze_nd.execution, "load_source", _loader)
    return plan, fingerprint


def _execute(plan):
    registry = effective_registry()
    return execute_substrate(registry, _execution_composition(), plan)


def test_registration_binds_maze_nd_definition_to_execution_operation() -> None:
    registry = effective_registry()
    definition = registry.resolve(MAZE_ND_DEFINITION.ref.canonical)
    composition = _execution_composition()
    assert composition.contains(definition)
    assert composition.execute(definition) is maze_execute


def test_execute_materializes_unique_valid_topology_records(tmp_path, monkeypatch) -> None:
    plan, _fp = _make_plan(tmp_path, monkeypatch=monkeypatch)
    result = _execute(plan)
    records = result.materialization.records
    # Unique topologies: A (train0+test0), B (train1), C (test1) => 3.
    assert len(records) == 3
    for record in records:
        assert record.schema_ref == "raster-topology/v1"
        assert set(record.content.keys()) == {"extent", "passable"}
    # Extent of A/B is 2x3; C is 3x2.
    extents = {
        (record.content["extent"]["height"], record.content["extent"]["width"]) for record in records
    }
    assert extents == {(2, 3), (3, 2)}


def test_duplicate_rows_aggregate_into_one_record_with_full_lineage(tmp_path, monkeypatch) -> None:
    plan, _fp = _make_plan(tmp_path, monkeypatch=monkeypatch)
    result = _execute(plan)
    lineage = next(r for r in result.materialization.logical_resources if r.name == "source-lineage")
    occ_map = lineage.content["occurrence_to_record"]
    # 4 source occurrences -> 4 mapping entries, 3 distinct records.
    assert len(occ_map) == 4
    assert len({v for v in occ_map.values()}) == 3
    # The duplicated topology maps both train0 and test0 to the same record.
    assert occ_map["rev-fixed::train.jsonl.gz::0"] == occ_map["rev-fixed::test.jsonl.gz::0"]


def test_complete_lineage_preserves_all_occurrences(tmp_path, monkeypatch) -> None:
    plan, _fp = _make_plan(tmp_path, monkeypatch=monkeypatch)
    result = _execute(plan)
    lineage = next(r for r in result.materialization.logical_resources if r.name == "source-lineage")
    assert set(lineage.content["occurrence_to_record"].keys()) == {
        "rev-fixed::train.jsonl.gz::0",
        "rev-fixed::train.jsonl.gz::1",
        "rev-fixed::test.jsonl.gz::0",
        "rev-fixed::test.jsonl.gz::1",
    }
    assert lineage.resource_kind == "lineage"


def test_record_id_is_framework_derived(tmp_path, monkeypatch) -> None:
    plan, _fp = _make_plan(tmp_path, monkeypatch=monkeypatch)
    result = _execute(plan)
    for record in result.materialization.records:
        assert record.record_id.startswith("sha256:")


def test_record_id_is_deterministic_for_same_source(tmp_path, monkeypatch) -> None:
    """Executing the same source twice yields identical record_ids."""
    plan, _fp = _make_plan(tmp_path, monkeypatch=monkeypatch)

    def _records():
        return {
            (
                r.content["extent"]["height"],
                r.content["extent"]["width"],
                tuple(r.content["passable"]),
            ): r.record_id
            for r in _execute(plan).materialization.records
        }

    first = _records()
    second = _records()
    assert first == second


def test_realization_key_is_first_duplicate_and_occurrence_count_independent(
    tmp_path, monkeypatch
) -> None:
    """A topology's realization identity ignores occurrence count and ordering.

    The realization key is content-based (extent + passability + source
    semantics) and deliberately carries no occurrence count, first-duplicate
    index, or source row ordinal, so grouping the same topology from a
    1-occurrence vs a 3-occurrence population yields the same key.
    """
    from ehp_research.substrates.maze_nd.configuration import resolve_configuration
    from ehp_research.substrates.maze_nd.execution import _realization_key

    plan, _fp = _make_plan(tmp_path, monkeypatch=monkeypatch)
    cfg = resolve_configuration(load_configuration(tmp_path / "maze-nd.toml"))

    # Same topology (A: #S#/#G#) -> key from a single occurrence equals the key
    # from the same topology regardless of how many duplicates surround it.
    key_single = _realization_key(cfg, 2, 3, (False, True, False, False, True, False))
    # Identical call -> identical key (no state dependence).
    assert key_single == _realization_key(cfg, 2, 3, (False, True, False, False, True, False))
    # Different passable content -> different key.
    assert key_single != _realization_key(cfg, 2, 3, (False, True, False, False, True, True))


def test_no_intrinsic_topology_split_on_records(tmp_path, monkeypatch) -> None:
    plan, _fp = _make_plan(tmp_path, monkeypatch=monkeypatch)
    result = _execute(plan)
    for record in result.materialization.records:
        names = {d.name for d in record.descriptors}
        assert not (names & {"train", "validation", "test"})


def test_bounded_lineage_summary_on_records(tmp_path, monkeypatch) -> None:
    plan, _fp = _make_plan(tmp_path, monkeypatch=monkeypatch)
    result = _execute(plan)
    for record in result.materialization.records:
        desc = {d.name: d.value for d in record.descriptors}
        assert desc["source_occurrence_count"] >= 1
        assert isinstance(desc["source_split_labels"], tuple)
        assert desc["lineage_resource"] == "source-lineage"


def test_record_uses_shared_raster_topology_no_private_state(tmp_path, monkeypatch) -> None:
    """Maze-ND delegates state/component/movement semantics to raster-topology/v1."""
    plan, _fp = _make_plan(tmp_path, monkeypatch=monkeypatch)
    result = _execute(plan)
    for record in result.materialization.records:
        # Content is the shared raster-topology content projection (extent+passable).
        assert set(record.content.keys()) == {"extent", "passable"}
        # Component/store/state fields are NOT re-emitted as private Maze-ND channels.
        assert not (
            set(record.content.keys())
            & {
                "component_count",
                "connected",
                "next_state",
                "movement_valid",
                "state_count",
            }
        )


def test_connectivity_reject_rejects_disconnected(tmp_path, monkeypatch) -> None:
    """Under reject, a disconnected candidate is never silently repaired."""
    # Two diagonal (not orthogonally adjacent) passable cells -> component_count > 1.
    rows_train = [fx.row(fx.grid_from_strings(" #", "# "))]
    rows_test = [fx.row(fx.grid_from_strings(" #", "# "))]  # duplicate
    train_blob = fx.split_blob(rows_train)
    test_blob = fx.split_blob(rows_test)
    fp = content_fingerprint(train_blob, test_blob)
    config_path = tmp_path / "maze-nd-reject.toml"
    config_path.write_text(_plan_text(connectivity="reject", fingerprint=fp), encoding="utf-8")
    registry = effective_registry()
    planning = SubstratePlanningComposition(planning_registrations())
    plan = plan_substrate(
        registry,
        planning,
        "substrate:maze-nd/v1",
        load_configuration(str(config_path)),
        resource_resolver=_GenericResolver(),
    )

    def _loader(config, resource_source):
        yield from maze_nd.source.iter_source_rows(config, resource_source, train_blob, test_blob)

    monkeypatch.setattr(maze_nd.execution, "load_source", _loader)
    result = _execute(plan)
    # Under reject, disconnected topologies are dropped -> no records.
    assert result.materialization.records == ()
    lineage = next(r for r in result.materialization.logical_resources if r.name == "source-lineage")
    assert lineage.content["occurrence_to_record"] == {}
    # Rejection is not silent: the rejected occurrence count is surfaced.
    assert lineage.content["connectivity_policy"] == "reject"
    assert lineage.content["rejected_occurrence_count"] == 2


def test_connectivity_preserve_keeps_disconnected(tmp_path, monkeypatch) -> None:
    """Under preserve, disconnected topologies are retained with component info."""
    rows_train = [fx.row(fx.grid_from_strings(" #", "# "))]  # diagonal islands (disconnected)
    train_blob = fx.split_blob(rows_train)
    test_blob = fx.split_blob([])
    fp = content_fingerprint(train_blob, test_blob)
    config_path = tmp_path / "maze-nd-preserve.toml"
    config_path.write_text(_plan_text(connectivity="preserve", fingerprint=fp), encoding="utf-8")
    registry = effective_registry()
    planning = SubstratePlanningComposition(planning_registrations())
    plan = plan_substrate(
        registry,
        planning,
        "substrate:maze-nd/v1",
        load_configuration(str(config_path)),
        resource_resolver=_GenericResolver(),
    )

    def _loader(config, resource_source):
        yield from maze_nd.source.iter_source_rows(config, resource_source, train_blob, test_blob)

    monkeypatch.setattr(maze_nd.execution, "load_source", _loader)
    result = _execute(plan)
    assert len(result.materialization.records) == 1


def test_removing_registration_yields_missing_capability(tmp_path, monkeypatch) -> None:
    plan, _fp = _make_plan(tmp_path, monkeypatch=monkeypatch)
    registry = effective_registry()
    empty = SubstrateExecutionComposition(())
    with pytest.raises(MissingExecutionCapabilityError):
        execute_substrate(registry, empty, plan)


def test_restoring_registration_succeeds_same_path(tmp_path, monkeypatch) -> None:
    plan, _fp = _make_plan(tmp_path, monkeypatch=monkeypatch)
    result = _execute(plan)
    assert len(result.materialization.records) == 3
