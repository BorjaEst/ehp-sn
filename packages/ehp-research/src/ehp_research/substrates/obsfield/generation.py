"""ObsField ``categorical-random/v1`` scientific field generation.

This module owns the *producer scientific algorithm* for the registered
``substrate:obsfield/v1`` definition's ``categorical-random/v1`` assignment
protocol.

For each realization it:

1. resolves the canonical rectangular ambient domain from the configuration;
2. resolves the immutable anonymous vocabulary (identity + cardinality);
3. resolves the assignment distribution (uniform or explicit probability vector);
4. derives record-addressable deterministic random state from the base seed,
   domain identity, vocabulary identity, protocol identity, assignment
   parameters, and realization index;
5. assigns exactly one vocabulary entry to every canonical position;
6. builds the immutable shared ``categorical-field/v1`` record via the framework
   constructor.

ObsField is topology-independent throughout: no stage reads, resolves, or
references a topology artifact, passability, or any other substrate. Observation
realizations form a reusable pool with no intrinsic split.
"""

from __future__ import annotations

import hashlib
import random
from collections.abc import Iterator

from ehp_sn.contracts.domains import (
    RectangularRowColumnDomain,
    rectangular_row_column_domain,
)
from ehp_sn.contracts.observations import (
    AnonymousVocabulary,
    CategoricalField,
    categorical_field,
)

from .configuration import ObsFieldConfiguration


def _seed_int(*parts: object) -> int:
    """Derive a stable non-negative integer seed from canonical string parts.

    Uses ``sha256`` (stable across processes/workers — never the per-process
    salted ``hash()``) so record content is reproducible and scheduling-
    independent.
    """
    digest = hashlib.sha256()
    for part in parts:
        digest.update(repr(part).encode("utf-8"))
    digest.update(b"\x00")
    return int.from_bytes(digest.digest()[:8], "big")


def _record_seed(config: ObsFieldConfiguration, realization_index: int) -> int:
    """Derive the record-addressable seed for one realization.

    Depends only on the resolved semantic identity and the realization index —
    never on worker scheduling, total realization count, or completion order,
    preserving prefix stability when requested counts increase.
    """
    return _seed_int(
        "obsfield",
        config.variant,
        config.assignment_protocol,
        config.domain_schema,
        config.height,
        config.width,
        config.vocabulary_identity,
        config.vocabulary_cardinality,
        config.distribution,
        config.seed,
        realization_index,
    )


def _categorical_probabilities(config: ObsFieldConfiguration) -> tuple[float, ...]:
    """Return the categorical probability vector over the vocabulary.

    ``"uniform"`` yields ``(1/K, ..., 1/K)``; an explicit vector is used as-is.
    """
    if config.distribution == "uniform":
        return tuple(1.0 / config.vocabulary_cardinality for _ in range(config.vocabulary_cardinality))
    # Explicit probability vector (non-``uniform`` distribution).
    result = config.distribution
    assert isinstance(result, tuple)
    return result


def _domain(config: ObsFieldConfiguration) -> RectangularRowColumnDomain:
    """Resolve the canonical rectangular ambient domain."""
    return rectangular_row_column_domain(config.height, config.width)


def _vocabulary(config: ObsFieldConfiguration) -> AnonymousVocabulary:
    """Resolve the immutable anonymous vocabulary for the executable profile.

    The vocabulary identity is established directly from the declared immutable
    identity in configuration; no vocabulary registry is implied.
    """
    return AnonymousVocabulary(
        identity=config.vocabulary_identity,
        cardinality=config.vocabulary_cardinality,
    )


def generate_realization(
    config: ObsFieldConfiguration,
    realization_index: int,
) -> CategoricalField:
    """Generate one observation realization over the complete ambient domain.

    Assigns exactly one vocabulary entry to every canonical position under the
    declared categorical distribution, using record-addressable deterministic
    random state. Realizations with different indexes are independent.
    """
    domain = _domain(config)
    vocabulary = _vocabulary(config)
    probabilities = _categorical_probabilities(config)

    rng = random.Random(_record_seed(config, realization_index))
    cardinality = config.vocabulary_cardinality
    observation_ids = rng.choices(range(cardinality), weights=probabilities, k=domain.position_count)

    return categorical_field(domain, vocabulary, observation_ids)


def generate_realizations(
    config: ObsFieldConfiguration,
) -> Iterator[CategoricalField]:
    """Generate the complete ObsField realization collection.

    Yields one :class:`CategoricalField` per realization index in ascending
    order. There is no intrinsic split; fields form a reusable pool.
    """
    for index in range(config.realization_count):
        yield generate_realization(config, index)


__all__ = [
    "generate_realization",
    "generate_realizations",
]
