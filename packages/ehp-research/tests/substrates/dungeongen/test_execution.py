"""DungeonGen execution operation tests (Targets 13, 14, 15)."""

from __future__ import annotations

import pytest
from ehp_research.substrates import dungeongen
from ehp_research.substrates.dungeongen.execution import (
    DungeonGenExecutionError,
    execute,
)
from ehp_sn.execution import MaterializationSession

from ._fixtures import ROOM, fake_generator_factory, loaded_document


def _plan(session_values: dict) -> MaterializationSession:
    """Build a MaterializationSession from a raw config document."""
    cfg = dungeongen.resolve_configuration(loaded_document(**session_values))
    return MaterializationSession(
        component=dungeongen.DUNGEONGEN_DEFINITION.ref,
        schema_ref="raster-topology/v1",
        configuration=cfg,
        resources=(),
        identity_inputs=(),
    )


def _shared_room_cells() -> dict[tuple[int, int], int]:
    """A fixed valid 2x3 room (6 passable states) within fixture bounds."""
    return {(x, y): ROOM for x in range(3) for y in range(2)}


def test_execute_materializes_records_and_lineage(monkeypatch) -> None:
    """A conforming execution materializes records + lineage in the session."""
    monkeypatch.setattr(
        dungeongen.execution,
        "generate_native",
        fake_generator_factory(lambda seed: _shared_room_cells()),
    )
    session = _plan({"record_count": 4, "attempt_budget": 10})
    execute(session)

    assert len(session.records) == 4
    # Framework derives record_id; each distinct logical index gets a distinct id.
    ids = {r.record_id for r in session.records}
    assert len(ids) == 4
    # Every record conforms to raster-topology/v1 content: extent + passable.
    for record in session.records:
        content = record.content
        assert set(content) == {"extent", "passable"}
        assert record.schema_ref == "raster-topology/v1"
    # Lineage logical resource present.
    names = {res.name for res in session.logical_resources}
    assert "dungeongen-lineage" in names


def test_execute_same_realization_key_for_equal_content(monkeypatch) -> None:
    """Equal content + equal semantics → equal realization key.

    Under `allow`, distinct logical indexes with identical topology get distinct
    record_ids (they are separate intended realizations) but the content is
    identical. record_id independence from enumeration is guaranteed by the
    framework; here we only assert deterministic content.
    """
    monkeypatch.setattr(
        dungeongen.execution,
        "generate_native",
        fake_generator_factory(lambda seed: _shared_room_cells()),
    )
    session = _plan({"record_count": 3, "attempt_budget": 10})
    execute(session)
    contents = {tuple(record.content["passable"]) for record in session.records}
    assert len(contents) == 1  # all identical content
    assert len({r.record_id for r in session.records}) == 3  # still 3 records


def test_execute_exhaustion_is_controlled(monkeypatch) -> None:
    """Exhaustion fails execution with a controlled error."""
    monkeypatch.setattr(
        dungeongen.execution,
        "generate_native",
        fake_generator_factory(lambda seed: {(0, 0): ROOM}),
    )
    session = _plan({"record_count": 2, "attempt_budget": 3})
    with pytest.raises(DungeonGenExecutionError) as exc:
        execute(session)
    assert "exhaustion" in str(exc.value)


def test_execute_is_registered_by_identity() -> None:
    """The composition binds the definition to the real operation."""
    from ehp_research.registration import execution_registrations
    from ehp_sn.execution import SubstrateExecutionComposition

    composition = SubstrateExecutionComposition(execution_registrations())
    assert composition.contains(dungeongen.DUNGEONGEN_DEFINITION)
    assert composition.execute(dungeongen.DUNGEONGEN_DEFINITION) is execute


def test_execute_rejects_wrong_configuration_type() -> None:
    with pytest.raises(DungeonGenExecutionError):
        execute(
            MaterializationSession(
                component=dungeongen.DUNGEONGEN_DEFINITION.ref,
                schema_ref="raster-topology/v1",
                configuration=object(),
                resources=(),
                identity_inputs=(),
            )
        )
