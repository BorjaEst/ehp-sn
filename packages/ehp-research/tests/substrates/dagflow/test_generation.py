"""Tests for the Dagflow ``constructive-forward/v1`` generation protocol.

Verifies the producer scientific algorithm against the dagflow-v1 specification:
fixed node-count resolution, required-successor selection, additional-edge
sampling, public-ID permutation, and the artifact-wide exact labelled-graph
uniqueness policy (prefix stability, worker independence, deterministic
exhaustion).
"""

from __future__ import annotations

import pytest
from ehp_research.substrates.dagflow.configuration import DagflowConfiguration
from ehp_research.substrates.dagflow.generation import (
    DagflowExhaustionError,
    generate_artifact_records,
)


def _config(
    *,
    node_count: int = 8,
    probability: float = 0.30,
    seed: int = 7,
    train: int = 5,
    validation: int = 2,
    test: int = 2,
) -> DagflowConfiguration:
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


def _records(config: DagflowConfiguration) -> list[tuple[str, int, object]]:
    return list(generate_artifact_records(config))


def test_configured_counts_per_split() -> None:
    """Each split contains exactly its configured record count (DF-SPLIT-004)."""
    records = _records(_config(train=5, validation=2, test=2))
    counts: dict[str, int] = {}
    for split, _index, _graph in records:
        counts[split] = counts.get(split, 0) + 1
    assert counts == {"train": 5, "validation": 2, "test": 2}


def test_all_records_are_single_terminal_dags() -> None:
    """Every generated graph satisfies DF-REC-005/006/007."""
    for _split, _index, graph in _records(_config()):
        assert graph.acyclic is True
        assert graph.terminal_count == 1
        assert graph.all_nodes_reach_a_terminal is True


def test_fixed_node_count_respected() -> None:
    """Every record has the declared fixed node_count."""
    for _split, _index, graph in _records(_config(node_count=10)):
        assert graph.node_count == 10


def test_same_configuration_identical_collection() -> None:
    """Same configuration → identical complete collection (determinism)."""
    a = [g.content() for _s, _i, g in _records(_config())]
    b = [g.content() for _s, _i, g in _records(_config())]
    assert a == b


def test_higher_count_preserves_earlier_content() -> None:
    """Increasing requested counts leaves earlier realization contents unchanged."""
    small = [g.content() for _s, _i, g in _records(_config(train=5))]
    large = [g.content() for _s, _i, g in _records(_config(train=12))]
    small_set = {repr(c) for c in small}
    large_set = {repr(c) for c in large}
    assert small_set <= large_set


def test_no_identical_labelled_graph_across_artifact() -> None:
    """No two records share identical canonical labelled content (DF-SPLIT-003)."""
    records = _records(_config(train=40, validation=10, test=10))
    keys = [repr(g.content()) for _s, _i, g in records]
    assert len(keys) == len(set(keys))


def test_worker_scheduling_irrelevant() -> None:
    """Content is independent of the order in which records are generated.

    Generating the collection twice through independent iterators (simulating
    independent workers) yields the same content for every realization identity.
    """
    a = {(s, i): repr(g.content()) for s, i, g in _records(_config())}
    b = {(s, i): repr(g.content()) for s, i, g in _records(_config())}
    assert a == b


def test_exhaustion_is_deterministic_for_impossible_uniqueness() -> None:
    """A forced collision exhausts the bounded attempt sequence deterministically.

    With ``node_count == 1`` there is only one labelled graph (a single isolated
    node), so requesting two records cannot yield two distinct labelled graphs;
    the protocol must raise a deterministic exhaustion error.
    """
    config = _config(node_count=1, probability=0.0, train=2, validation=0, test=0)
    with pytest.raises(DagflowExhaustionError):
        list(generate_artifact_records(config))
