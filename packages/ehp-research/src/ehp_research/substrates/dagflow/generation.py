"""Dagflow ``constructive-forward/v1`` scientific graph generation.

This module owns the *producer scientific algorithm* for the registered
``substrate:dagflow/v1`` definition. It implements the concrete generation
protocol whose remaining algorithmic choices are completely determined here and
by the resolved configuration, so no scientific choice is left implicit inside
Python code.

The selected executable protocol is ``constructive-forward/v1`` with the
**fixed** node-count policy (``graph.node_count``), matching the reusable
profiles under ``config/data/dagflow/``. Bounded node-count distributions are
not implemented here because the current Phase 5.1 execution profile does not
need them (see the phase plan).

For each realization the protocol performs the conceptual stages:

1. resolve the fixed node count ``N`` and the record's deterministic seed;
2. create a private acyclic construction order ``0..N-1`` (strictly increasing
   indices make every private edge a forward edge, so acyclicity is by
   construction);
3. designate construction node ``N-1`` as the structural terminal;
4. for every non-terminal construction node choose at least one required
   outgoing edge to a later node, so that every node reaches the terminal;
5. consider every remaining admissible forward pair in canonical lexicographic
   order and add it with the declared ``additional_edge_probability``;
6. apply a deterministic permutation from private construction identities to
   public node IDs;
7. canonicalize the public edge relation lexicographically through the shared
   ``simple-digraph/v1`` constructor and return the immutable conforming graph.

Required successors, additional-edge sampling, and the public-ID permutation
each derive independent deterministic random state from the record's semantic
realization identity (base seed + split + realization index + config identity),
so record content is reproducible and independent of worker scheduling,
completion order, and enumeration.

### Artifact-wide exact labelled-graph uniqueness

The producing family requires that no two records in an artifact share identical
canonical labelled graph content across all splits, while earlier realization
indexes must remain unchanged when requested counts increase. This is resolved
by processing records in a canonical deterministic order (split order, then
ascending realization index) and, for each record, advancing a bounded attempt
sequence until a candidate whose canonical labelled content has not yet been
accepted. Because each record's candidates depend only on its own semantic
identity and attempt number — never on the total requested count or on
completion order — this preserves worker independence, split-count prefix
stability, and deterministic exhaustion.
"""

from __future__ import annotations

import hashlib
import random
from collections.abc import Iterator

from ehp_sn.contracts.relations.simple_digraph import SimpleDigraph, simple_digraph

from .configuration import DagflowConfiguration, DagflowConfigurationError

#: Canonical intrinsic split order for one Dagflow artifact. Record content and
#: acceptance decisions are processed in this order so the collection is
#: deterministic and worker-independent.
SPLIT_ORDER: tuple[str, ...] = ("train", "validation", "test")

#: Maximum deterministic attempts per realization used to obtain artifact-wide
#: exact labelled-graph uniqueness. The candidate space is large, but the budget
#: is finite so exhaustion is deterministic.
MAX_UNIQUENESS_ATTEMPTS: int = 1000


class DagflowExhaustionError(DagflowConfigurationError):
    """A realization could not obtain unique labelled-graph content within budget.

    Raised when, after the bounded attempt sequence, no candidate's canonical
    labelled content is distinct from already-accepted records in the artifact.
    This is deterministic given the resolved configuration.
    """


def _seed_int(*parts: object) -> int:
    """Derive a stable non-negative integer seed from canonical string parts.

    Uses ``sha256`` (stable across processes, workers, and Python hash seeds —
    never the per-process salted ``hash()``) so record identity is reproducible
    and independent of scheduling.
    """
    digest = hashlib.sha256()
    for part in parts:
        digest.update(repr(part).encode("utf-8"))
    digest.update(b"\x00")
    return int.from_bytes(digest.digest()[:8], "big")


def _role_seed(record_seed: int, role: str) -> int:
    """Derive the deterministic seed for one randomness role of one record."""
    return _seed_int(record_seed, "role", role)


def _record_seed(
    config: DagflowConfiguration,
    split: str,
    realization_index: int,
    attempt: int,
) -> int:
    """Derive the deterministic seed for one record candidate.

    Depends only on the resolved semantic identity (base seed, split, realization
    index, node count, and edge policy) and the attempt number — never on worker
    scheduling, total counts, or completion order.
    """
    return _seed_int(
        "dagflow",
        config.variant,
        config.generation_protocol,
        config.seed,
        config.node_count,
        config.additional_edge_probability,
        split,
        realization_index,
        "attempt",
        attempt,
    )


def _required_successor_edges(node_count: int, rng: random.Random) -> list[tuple[int, int]]:
    """Choose one required forward edge for every non-terminal construction node.

    Node ``i`` (``0 <= i < N-1``) chooses a successor ``j`` in ``[i+1, N-1]``.
    Because construction edges are strictly forward, the graph is acyclic by
    construction, and because every non-terminal node has an outgoing path of
    strictly increasing indexes that must terminate at the sole sink ``N-1``,
    every node reaches the terminal (single-terminal by construction).
    """
    edges: list[tuple[int, int]] = []
    for node in range(node_count - 1):
        target = rng.randint(node + 1, node_count - 1)
        edges.append((node, target))
    return edges


def _additional_edges(
    node_count: int,
    required: set[tuple[int, int]],
    probability: float,
    rng: random.Random,
) -> list[tuple[int, int]]:
    """Sample admissible additional forward edges in canonical pair order.

    Every forward pair ``(i, j)`` with ``i < j`` that is not already a required
    edge is admissible (it preserves acyclicity and simple-digraph semantics).
    Candidates are considered in canonical lexicographic ``(source, target)``
    order and added independently with ``probability``.
    """
    edges: list[tuple[int, int]] = []
    for source in range(node_count):
        for target in range(source + 1, node_count):
            pair = (source, target)
            if pair in required:
                continue
            if rng.random() < probability:
                edges.append(pair)
    return edges


def _permutation(node_count: int, rng: random.Random) -> list[int]:
    """Return a deterministic permutation over public node IDs.

    Relabels private construction identities onto public node IDs so that public
    IDs carry no generation-order structural meaning (per ``simple-digraph/v1``).
    """
    permutation = list(range(node_count))
    rng.shuffle(permutation)
    return permutation


def _generate_candidate(
    config: DagflowConfiguration,
    split: str,
    realization_index: int,
    attempt: int,
) -> SimpleDigraph:
    """Generate one deterministic candidate graph for the given record/attempt.

    Accepts only contract-owned and producer-owned authoritative inputs; the
    generation is fully determined by the resolved configuration and the record
    identity. The returned graph already conforms to ``simple-digraph/v1`` and
    is single-terminal by construction; callers still verify that requirement.
    """
    node_count = config.node_count
    if node_count is None:
        raise DagflowConfigurationError(
            "constructive-forward/v1 execution requires the fixed node_count policy"
        )

    record_seed = _record_seed(config, split, realization_index, attempt)

    required = _required_successor_edges(
        node_count, random.Random(_role_seed(record_seed, "required_successor"))
    )
    required_set = set(required)

    additional = _additional_edges(
        node_count,
        required_set,
        config.additional_edge_probability,
        random.Random(_role_seed(record_seed, "additional_edge")),
    )

    private_edges = required + additional

    permutation = _permutation(node_count, random.Random(_role_seed(record_seed, "permutation")))
    public_edges = [(permutation[source], permutation[target]) for source, target in private_edges]

    return simple_digraph(node_count, public_edges)


def _verify_single_terminal(graph: SimpleDigraph) -> None:
    """Raise when the candidate is not a ``single-terminal`` Dagflow graph.

    Verifies the Dagflow record-level invariants ``DF-REC-005`` (acyclic),
    ``DF-REC-006`` (unique terminal), and ``DF-REC-007`` (terminal reachability).
    These are Dagflow `single-terminal` constraints enforced by the producer, not
    by ``simple-digraph/v1``. They should hold by construction; this is a guard.
    """
    if not graph.acyclic:
        raise DagflowConfigurationError(
            "Dagflow generation produced a cyclic graph (violates DF-REC-005)"
        )
    if graph.terminal_count != 1:
        raise DagflowConfigurationError(
            f"Dagflow generation produced terminal_count={graph.terminal_count}, "
            "expected 1 (violates DF-REC-006)"
        )
    if not graph.all_nodes_reach_a_terminal:
        raise DagflowConfigurationError(
            "Dagflow generation produced a node that does not reach the terminal (violates DF-REC-007)"
        )


def _canonical_content_key(graph: SimpleDigraph) -> tuple[int, tuple[tuple[int, int], ...]]:
    """Return a hashable canonical labelled-content key for uniqueness tracking.

    Exact labelled-graph content is ``node_count`` plus the canonical edge
    relation (``simple-digraph/v1`` labelled-graph equality). The graph edge
    tuple is already canonical lexicographic order, so this key is stable and
    hashable for the artifact-wide deduplication set.
    """
    return (graph.node_count, tuple(graph.edges))


def _generate_unique_for(
    config: DagflowConfiguration,
    split: str,
    realization_index: int,
    accepted: set[tuple[int, tuple[tuple[int, int], ...]]],
) -> SimpleDigraph:
    """Generate a unique candidate for one record, with a bounded attempt sequence.

    For ``attempt`` in ``0 .. MAX_UNIQUENESS_ATTEMPTS - 1`` a deterministic
    candidate is produced; the first whose canonical labelled content is not in
    ``accepted`` is accepted and returned. Raises :class:`DagflowExhaustionError`
    when the budget is exhausted (deterministic).
    """
    for attempt in range(MAX_UNIQUENESS_ATTEMPTS):
        candidate = _generate_candidate(config, split, realization_index, attempt)
        _verify_single_terminal(candidate)
        key = _canonical_content_key(candidate)
        if key not in accepted:
            accepted.add(key)
            return candidate
    raise DagflowExhaustionError(
        f"Dagflow could not obtain unique labelled-graph content for "
        f"split={split!r} realization_index={realization_index} within "
        f"{MAX_UNIQUENESS_ATTEMPTS} attempts"
    )


def _split_count(config: DagflowConfiguration, split: str) -> int:
    """Return the configured record count for one canonical split."""
    if split == "train":
        return config.splits_train_count
    if split == "validation":
        return config.splits_validation_count
    if split == "test":
        return config.splits_test_count
    raise DagflowConfigurationError(f"unknown split {split!r}")


def generate_artifact_records(config: DagflowConfiguration) -> Iterator[tuple[str, int, SimpleDigraph]]:
    """Generate the complete Dagflow artifact record collection.

    Yields ``(split, realization_index, graph)`` in canonical order (split order,
    then ascending realization index), enforcing artifact-wide exact labelled-graph
    uniqueness (``DF-SPLIT-003``) and configured per-split counts (``DF-SPLIT-004``).
    The collection is deterministic and worker-independent.
    """
    accepted: set[tuple[int, tuple[tuple[int, int], ...]]] = set()
    for split in SPLIT_ORDER:
        count = _split_count(config, split)
        for index in range(count):
            graph = _generate_unique_for(config, split, index, accepted)
            yield split, index, graph


__all__ = [
    "DagflowExhaustionError",
    "MAX_UNIQUENESS_ATTEMPTS",
    "SPLIT_ORDER",
    "generate_artifact_records",
]
