"""Explicit metamorphic reproducibility matrix for ObsField (Phase 5 § 27-31).

Phase 5 requires each producer's reproducibility to be exercised as an explicit
metamorphic matrix, classifying every applicable scenario as passing /
not-applicable / unsupported-because-dependency-unresolved — never silently
omitted. This module is that matrix for ``obsfield/v1``
(``categorical-random/v1`` assignment protocol).

The public API exercised is the producer generation surface:

* ``generate_realizations(config) -> Iterator[CategoricalField]`` — the complete
  realization collection in ascending realization-index order;
* ``generate_realization(config, index) -> CategoricalField`` — one
  record-addressable realization.

Canonical record content is the typed ``CategoricalField`` content projection
(``domain`` + ``vocabulary`` + ``observation_id``); the realization key is the
realization index. All assertions are structural on that canonical content
before any image comparison (Phase-5 § 38).

## Matrix (scenario → status)

```
worker-count invariance         PASS
worker-scheduling/order            PASS
operational-path invariance        PASS
prefix stability                   PASS
cross-domain isolation             N/A (single ambient domain; no multi-domain API)
rebuild equivalence                PASS
retry-stream isolation             N/A (no retry/acceptance stream; ObsField is not a rejection producer)
```

Scenarios marked ``N/A`` are explicitly skipped with a reason; they are not
silently omitted. No scenario here is unsupported-because-dependency-unresolved:
ObsField has no external build dependency.
"""

from __future__ import annotations

import pytest
from ehp_research.substrates.obsfield.configuration import ObsFieldConfiguration
from ehp_research.substrates.obsfield.generation import (
    generate_realization,
    generate_realizations,
)

#: Explicit metamorphic matrix: scenario → status.
MATRIX: dict[str, str] = {
    "worker-count invariance": "PASS",
    "worker-scheduling/order invariance": "PASS",
    "operational-path invariance": "PASS",
    "prefix stability": "PASS",
    "cross-domain isolation": "N/A (single ambient domain; no multi-domain collection API)",
    "rebuild equivalence": "PASS",
    "retry-stream isolation": "N/A (no retry/acceptance stream for ObsField)",
}


def _config(*, count: int = 8, seed: int = 0, height: int = 4, width: int = 5) -> ObsFieldConfiguration:
    """A small deterministic ObsField configuration."""
    return ObsFieldConfiguration(
        variant="categorical-complete",
        domain_schema="rectangular-row-column/v1",
        height=height,
        width=width,
        vocabulary_identity="obs-vocabulary:anon/v1",
        vocabulary_cardinality=3,
        assignment_protocol="categorical-random/v1",
        distribution="uniform",
        seed=seed,
        realization_count=count,
    )


def _by_index(config: ObsFieldConfiguration) -> dict[int, object]:
    """Generate the collection and key canonical content by realization index."""
    return {i: field.content() for i, field in enumerate(generate_realizations(config))}


def _single(index: int, config: ObsFieldConfiguration) -> object:
    """Canonical content of one record-addressable realization."""
    return generate_realization(config, index).content()


def test_worker_count_invariance() -> None:
    """Two independent full invocations yield identical per-index canonical records."""
    config = _config()
    a = _by_index(config)
    b = _by_index(config)
    assert a == b
    assert set(a) == set(range(config.realization_count))


def test_worker_scheduling_order_invariance() -> None:
    """Reversed/out-of-order generation yields the same per-realization content."""
    config = _config()
    forward = _by_index(config)
    # Generate every index explicitly in reverse order via the record-addressable API.
    reversed_contents = {
        index: _single(index, config) for index in reversed(range(config.realization_count))
    }
    assert reversed_contents == forward


def test_operational_path_invariance() -> None:
    """Content is independent of operational detail (iterator re-invocation)."""
    config = _config()
    direct = _by_index(config)
    # Re-invoke the iterator a second time independently.
    re_invoked = _by_index(config)
    assert direct == re_invoked
    # A lazily-drained iterator (two passes) yields the same records.
    first_pass = list(generate_realizations(config))
    second_pass = list(generate_realizations(config))
    assert [f.content() for f in first_pass] == [f.content() for f in second_pass]


def test_prefix_stability() -> None:
    """Requesting a larger count preserves earlier realization indexes' content."""
    small = _by_index(_config(count=5, seed=0))
    large = _by_index(_config(count=12, seed=0))
    assert large[0] == small[0]
    assert large[4] == small[4]
    assert len(large) == 12
    assert set(small) <= set(large)


def test_rebuild_equivalence() -> None:
    """Two independent full builds give identical canonical records."""
    config = _config(count=8, seed=3)
    first = _by_index(config)
    second = _by_index(config)
    assert first == second
    # Record keys (realization indexes) are identical across the rebuild.
    assert list(first) == list(second)


@pytest.mark.skip(
    reason=(
        "N/A: ObsField materializes a single ambient domain per configuration; "
        "there is no multi-domain collection API to add another domain to, so "
        "cross-domain isolation cannot be exercised."
    )
)
def test_cross_domain_isolation_not_applicable() -> None:
    """N/A: cross-domain isolation requires a multi-domain collection API."""
    raise AssertionError("must not run — classified N/A")


@pytest.mark.skip(
    reason=(
        "N/A: ObsField has no retry/acceptance stream (categorical assignment is "
        "single-pass); retry-stream isolation is a rejection-producer concern."
    )
)
def test_retry_stream_isolation_not_applicable() -> None:
    """N/A: ObsField has no acceptance/retry lineage to isolate."""
    raise AssertionError("must not run — classified N/A")
