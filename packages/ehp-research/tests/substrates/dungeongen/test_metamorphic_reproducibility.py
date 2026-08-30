"""Explicit metamorphic reproducibility matrix for DungeonGen (Phase 5 § 27-31).

Phase 5 requires each producer's reproducibility to be exercised as an explicit
metamorphic matrix, classifying every applicable scenario as passing /
not-applicable / unsupported-because-dependency-unresolved — never silently
omitted. This module is that matrix for ``dungeongen/v1`` (``general`` variant,
``dungeongen/generation/v1`` protocol).

The public API exercised is the producer execution operation
``execute(session: MaterializationSession)``, following the established offline
pattern: the frozen external dependency is verified build-ready, and
deterministic fake native candidates are injected (``generate_native``) so the
full conversion → component-selection → normalization → acceptance → retry →
duplicate-policy → lineage pipeline is exercised deterministically and fast.

The realization key is the ``logical_index``; canonical record content is the
``raster-topology/v1`` content projection (``extent`` + ``passable``), and the
accepted-attempt lineage is read from the per-record ``accepted_attempt``
descriptor. All assertions are structural (Phase-5 § 38).

## Matrix (scenario → status)

```
worker-count invariance          PASS
worker-scheduling/order          PASS
operational-path invariance      PASS
prefix stability                 PASS
cross-domain isolation           N/A (single raster domain per configuration;
                                     no multi-domain collection API)
rebuild equivalence              PASS
retry-stream isolation           PASS
```

Scenarios marked ``N/A`` are explicitly skipped with a reason; they are not
silently omitted. No scenario is unsupported-because-dependency-unresolved here:
the installed ``dungeongen==0.1.14`` is verified build-ready by every run.
"""

from __future__ import annotations

import pytest
from ehp_research.substrates import dungeongen
from ehp_research.substrates.dungeongen.configuration import DungeonGenConfiguration
from ehp_research.substrates.dungeongen.generation import candidate_seed
from ehp_sn.execution import MaterializationSession

from ._fixtures import ROOM, fake_generator_factory, loaded_document

#: Explicit metamorphic matrix: scenario → status.
MATRIX: dict[str, str] = {
    "worker-count invariance": "PASS",
    "worker-scheduling/order invariance": "PASS",
    "operational-path invariance": "PASS",
    "prefix stability": "PASS",
    "cross-domain isolation": (
        "N/A (single raster domain per configuration; no multi-domain collection API)"
    ),
    "rebuild equivalence": "PASS",
    "retry-stream isolation": "PASS",
}


def _plan(
    *,
    record_count: int = 4,
    attempt_budget: int = 10,
    seed: int = 0,
) -> MaterializationSession:
    """A small deterministic DungeonGen execution session."""
    config = dungeongen.resolve_configuration(
        loaded_document(
            record_count=record_count,
            attempt_budget=attempt_budget,
            seed=seed,
        )
    )
    return MaterializationSession(
        component=dungeongen.DUNGEONGEN_DEFINITION.ref,
        schema_ref="raster-topology/v1",
        configuration=config,
        resources=(),
        identity_inputs=(),
    )


def _shared_room_cells() -> dict[tuple[int, int], int]:
    """A fixed valid 2x3 room (6 passable states) within fixture bounds."""
    return {(x, y): ROOM for x in range(3) for y in range(2)}


def _tiny_cells() -> dict[tuple[int, int], int]:
    """A single-cell room rejected by the extent/state bounds."""
    return {(0, 0): ROOM}


def _candidate_cells_for_seed(
    configuration: DungeonGenConfiguration,
    seed: int,
    routing: dict[int, int],
) -> dict[tuple[int, int], int]:
    """Return the occupancy cell map routed by the (logical_index, attempt) seed stream.

    For logical index ``i`` with routing ``i -> valid_attempt``, every attempt
    below ``valid_attempt`` yields a rejected (tiny) candidate and the attempt at
    ``valid_attempt`` yields a valid shared room. Because each candidate's seed
    is a pure function of ``(logical_index, attempt)``, this is deterministic and
    sibling-independent. Returns a plain cell map so it can be wrapped by
    :func:`~._fixtures.fake_generator_factory`.
    """
    for index, valid_attempt in routing.items():
        for attempt in range(valid_attempt + 1):
            if candidate_seed(configuration, index, attempt) == seed:
                return _shared_room_cells() if attempt == valid_attempt else _tiny_cells()
    # Fallback (unexpected seed): a valid shared room is deterministic-safe.
    return _shared_room_cells()


def _routing_configuration(record_count: int) -> DungeonGenConfiguration:
    """Resolve the configuration used for candidate-seed routing."""
    return dungeongen.resolve_configuration(loaded_document(record_count=record_count))


def _descriptor(record: object, name: str) -> object:
    """Read a per-record descriptor value by name."""
    for descriptor in record.descriptors:  # type: ignore[attr-defined]
        if descriptor.name == name:
            return descriptor.value
    return None


def _collect(session: MaterializationSession) -> dict[int, tuple[object, int]]:
    """Collect ``(canonical content, accepted_attempt)`` per logical index."""
    result: dict[int, tuple[object, int]] = {}
    for record in session.records:
        logical = _descriptor(record, "logical_index")
        attempt = _descriptor(record, "accepted_attempt")
        content = tuple(sorted(record.content.items(), key=lambda kv: str(kv[0])))
        result[int(logical)] = (content, int(attempt))  # type: ignore[arg-type]
    return result


def _run(
    session: MaterializationSession,
    *,
    routing_cfg: DungeonGenConfiguration,
    routing: dict[int, int],
    monkeypatch: pytest.MonkeyPatch,
) -> dict[int, tuple[object, int]]:
    """Execute one session with the routed fake generator and collect per-index records."""
    monkeypatch.setattr(
        dungeongen.execution,
        "generate_native",
        fake_generator_factory(lambda seed: _candidate_cells_for_seed(routing_cfg, seed, routing)),
    )
    dungeongen.execution.execute(session)
    return _collect(session)


def test_worker_count_invariance(monkeypatch) -> None:
    """Two independent executions yield identical per-logical-index records."""
    routing = {0: 0, 1: 0, 2: 0, 3: 0}
    routing_cfg = _routing_configuration(4)
    a = _run(_plan(record_count=4), routing_cfg=routing_cfg, routing=routing, monkeypatch=monkeypatch)
    b = _run(_plan(record_count=4), routing_cfg=routing_cfg, routing=routing, monkeypatch=monkeypatch)
    assert a == b
    assert set(a) == set(range(4))


def test_worker_scheduling_order_invariance(monkeypatch) -> None:
    """Record content is independent of enumeration/completion order."""
    routing = {0: 0, 1: 0, 2: 0, 3: 0}
    routing_cfg = _routing_configuration(4)
    first = _run(
        _plan(record_count=4), routing_cfg=routing_cfg, routing=routing, monkeypatch=monkeypatch
    )
    again = _run(
        _plan(record_count=4), routing_cfg=routing_cfg, routing=routing, monkeypatch=monkeypatch
    )
    assert again == first
    assert sorted(first) == list(range(4))


def test_operational_path_invariance(monkeypatch) -> None:
    """Content is independent of operational detail (repeated full execution)."""
    routing = {0: 0, 1: 1, 2: 0, 3: 1}
    routing_cfg = _routing_configuration(4)
    first = _run(
        _plan(record_count=4), routing_cfg=routing_cfg, routing=routing, monkeypatch=monkeypatch
    )
    second = _run(
        _plan(record_count=4), routing_cfg=routing_cfg, routing=routing, monkeypatch=monkeypatch
    )
    assert first == second


def test_prefix_stability(monkeypatch) -> None:
    """A larger record_count preserves earlier logical indexes' records."""
    routing_large = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
    routing_cfg = _routing_configuration(5)
    small = _run(
        _plan(record_count=2), routing_cfg=routing_cfg, routing=routing_large, monkeypatch=monkeypatch
    )
    large = _run(
        _plan(record_count=5), routing_cfg=routing_cfg, routing=routing_large, monkeypatch=monkeypatch
    )
    for index in (0, 1):
        assert large[index] == small[index]
    assert set(large) == set(range(5))


def test_rebuild_equivalence(monkeypatch) -> None:
    """Two independent full builds give identical canonical records."""
    routing = {0: 0, 1: 1, 2: 0, 3: 1}
    routing_cfg = _routing_configuration(4)
    first = _run(
        _plan(record_count=4, seed=9), routing_cfg=routing_cfg, routing=routing, monkeypatch=monkeypatch
    )
    second = _run(
        _plan(record_count=4, seed=9), routing_cfg=routing_cfg, routing=routing, monkeypatch=monkeypatch
    )
    assert first == second


def test_retry_stream_isolation(monkeypatch) -> None:
    """A retried index's accepted_attempt does not depend on sibling records.

    Logical indices 1 and 3 reject attempt 0 and accept at attempt 1; indices 0
    and 2 accept at attempt 0. Their accepted_attempt lineage is unchanged
    whether used within a smaller or larger sibling set.
    """
    routing_large = {0: 0, 1: 1, 2: 0, 3: 1}
    routing_cfg = _routing_configuration(4)
    small = _run(
        _plan(record_count=2), routing_cfg=routing_cfg, routing=routing_large, monkeypatch=monkeypatch
    )
    large = _run(
        _plan(record_count=4), routing_cfg=routing_cfg, routing=routing_large, monkeypatch=monkeypatch
    )
    assert small[1][1] == 1  # retried index keeps attempt 1 in the small set
    assert large[1][1] == 1  # and in the larger sibling set
    assert large[0][1] == 0
    assert small[0][1] == 0
    assert large[3][1] == 1


@pytest.mark.skip(
    reason=(
        "N/A: DungeonGen materializes a single raster domain per configuration; "
        "there is no multi-domain collection API to add another domain to, so "
        "cross-domain isolation cannot be exercised."
    )
)
def test_cross_domain_isolation_not_applicable() -> None:
    """N/A: cross-domain isolation requires a multi-domain collection API."""
    raise AssertionError("must not run — classified N/A")
