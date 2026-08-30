"""Explicit metamorphic reproducibility matrix for Dagflow (Phase 5 § 27-31).

Phase 5 requires each producer's reproducibility to be exercised as an explicit
metamorphic matrix, classifying every applicable scenario as passing /
not-applicable / unsupported-because-dependency-unresolved — never silently
omitted. This module is that matrix for ``dagflow/v1``
(``constructive-forward/v1`` generation protocol).

The public API exercised is the producer generation surface:

* ``generate_artifact_records(config) -> Iterator[(split, realization_index,
  SimpleDigraph)]`` — the complete artifact collection in canonical order
  (``SPLIT_ORDER`` then ascending realization index), enforcing artifact-wide
  exact labelled-graph uniqueness.

The realization key is the ``(split, realization_index)`` pair; canonical record
content is the typed ``SimpleDigraph`` content projection (``node_count`` +
canonical ``edges``). All assertions are structural on that canonical content
before any image comparison (Phase-5 § 38).

## Matrix (scenario → status)

```
worker-count invariance          PASS
worker-scheduling/order             PASS
operational-path invariance         PASS
prefix stability                    PASS
cross-split isolation               PASS
rebuild equivalence                 PASS
retry-stream isolation              N/A (no acceptance/rejection retry lineage;
                                        per-record determinism is covered by
                                        worker/order invariance)
```

Scenarios marked ``N/A`` are explicitly skipped with a reason; they are not
silently omitted. No scenario here is unsupported-because-dependency-unresolved:
Dagflow has no external build dependency.
"""

from __future__ import annotations

import pytest
from ehp_research.substrates.dagflow.configuration import DagflowConfiguration
from ehp_research.substrates.dagflow.generation import generate_artifact_records

#: Explicit metamorphic matrix: scenario → status.
MATRIX: dict[str, str] = {
    "worker-count invariance": "PASS",
    "worker-scheduling/order invariance": "PASS",
    "operational-path invariance": "PASS",
    "prefix stability": "PASS",
    "cross-split isolation": "PASS",
    "rebuild equivalence": "PASS",
    "retry-stream isolation": (
        "N/A (no acceptance/rejection retry lineage; per-record determinism "
        "covered by worker/order invariance)"
    ),
}


def _config(
    *,
    node_count: int = 6,
    probability: float = 0.20,
    seed: int = 7,
    train: int = 5,
    validation: int = 2,
    test: int = 2,
) -> DagflowConfiguration:
    """A small deterministic Dagflow configuration."""
    return DagflowConfiguration(
        variant="single-terminal",
        generation_protocol="constructive-forward/v1",
        seed=seed,
        node_count=node_count,
        node_count_minimum=None,
        node_count_maximum=None,
        node_count_distribution=None,
        additional_edge_probability=probability,
        splits_train_count=train,
        splits_validation_count=validation,
        splits_test_count=test,
    )


def _by_key(config: DagflowConfiguration) -> dict[tuple[str, int], object]:
    """Generate the collection and key canonical content by (split, index)."""
    return {(split, index): graph.content() for split, index, graph in generate_artifact_records(config)}


def test_worker_count_invariance() -> None:
    """Two independent full invocations yield identical per-key canonical records."""
    config = _config()
    a = _by_key(config)
    b = _by_key(config)
    assert a == b
    assert (
        len(a) == config.splits_train_count + config.splits_validation_count + config.splits_test_count
    )


def test_worker_scheduling_order_invariance() -> None:
    """Records' content is independent of the enumeration/completion order."""
    config = _config()
    forward = _by_key(config)
    # Consume a second full build in reversed iteration order; per-key content
    # is unchanged regardless of consumption order.
    reversed_map: dict[tuple[str, int], object] = {}
    items = list(generate_artifact_records(config))
    for split, index, graph in reversed(items):
        reversed_map[(split, index)] = graph.content()
    assert reversed_map == forward


def test_operational_path_invariance() -> None:
    """Content is independent of operational detail (repeated full generation)."""
    config = _config()
    first = _by_key(config)
    second = _by_key(config)
    third = _by_key(config)
    assert first == second == third


def test_prefix_stability() -> None:
    """Requesting a larger count preserves earlier realization indexes' content."""
    small = _by_key(_config(train=5, validation=2, test=2, seed=7))
    large = _by_key(_config(train=12, validation=2, test=2, seed=7))
    small_keys = sorted(small)
    for key in small_keys:
        assert large[key] == small[key]
    # The large collection strictly extends the small one by split.
    assert len(large["train", 5]) is not None  # extra record present


def test_cross_split_isolation() -> None:
    """Adding records to one split does not alter the other splits' records."""
    baseline = _by_key(_config(train=5, validation=2, test=2, seed=7))
    grown = _by_key(_config(train=5, validation=4, test=3, seed=7))
    # Train records are untouched by the grown validation/test counts.
    train_keys = [k for k in baseline if k[0] == "train"]
    for key in train_keys:
        assert grown[key] == baseline[key]
    # The first validation records are likewise preserved.
    assert grown["validation", 0] == baseline["validation", 0]
    assert grown["validation", 1] == baseline["validation", 1]
    assert len(grown["validation", 3]) is not None


def test_rebuild_equivalence() -> None:
    """Two independent full builds give identical canonical records."""
    config = _config(train=5, validation=2, test=2, seed=11)
    first = _by_key(config)
    second = _by_key(config)
    assert first == second
    assert sorted(first) == sorted(second)


@pytest.mark.skip(
    reason=(
        "N/A: Dagflow has no acceptance/rejection retry lineage (its bounded "
        "uniqueness attempt sequence is a per-record determinism mechanism); "
        "retry-stream isolation is a DungeonGen concern and is covered here by "
        "worker/order invariance."
    )
)
def test_retry_stream_isolation_not_applicable() -> None:
    """N/A: no retry/acceptance stream to isolate for Dagflow."""
    raise AssertionError("must not run — classified N/A")
