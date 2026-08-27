"""DungeonGen execution operation (producer integration).

This module owns the *producer execution operation* for the registered
``substrate:dungeongen/v1`` definition: the research-side callable bound to the
definition through the framework execution composition.

It consumes the authoritative, opaque producer-effective configuration from the
framework-owned :class:`~ehp_sn.execution.MaterializationSession`, verifies the
frozen external dependency is build-ready, and for each logical topology index
runs the deterministic pipeline:

```text
derive candidate seed
    → invoke exact dungeongen dependency
    → native Dungeon
    → convert to passability
    → largest-component policy
    → normalize extent
    → acceptance policy
    → retry / exhaustion
    → duplicate policy
    → accepted realization
    → raster-topology/v1 construction
    → GeneratedRecordBody → MaterializationSession
```

The only shared topology constructor is ``raster-topology/v1``: DungeonGen
delegates ``state_id``, state/position maps, ``next_state``, ``movement_valid``,
``component_count``, ``connected``, and grid4 ordering and never re-enumerates
them. The producer never creates ``record_id``, an ``ArtifactRef``, a release
coordinate, a manifest, or a final filesystem path.
"""

from __future__ import annotations

from ehp_sn.contracts.domains import RectangularRowColumnDomain
from ehp_sn.contracts.topology import raster_topology
from ehp_sn.execution import (
    GeneratedRecordBody,
    MaterializationSession,
    RealizationKey,
)
from ehp_sn.planning import IdentityInput

from ._dependency import RANDOMNESS_ROLE
from .acceptance import AcceptedTopology, RejectionReason, run_logical_topology
from .configuration import DungeonGenConfiguration
from .generation import GenerationError, generate_native, verify_dependency_build_ready
from .lineage import LINEAGE_RESOURCE_NAME, build_lineage_resource


class DungeonGenExecutionError(ValueError):
    """A controlled DungeonGen producer execution failure.

    Raised for an invalid session configuration, a dependency that is not
    build-ready, or an exhausted logical realization. Translated by the generic
    build boundary into a controlled build error; the CLI maps it at its own
    layer.
    """


def _realization_key(
    configuration: DungeonGenConfiguration,
    accepted: AcceptedTopology,
) -> RealizationKey:
    """Declare the producer-owned canonical realization identity for one record.

    The identity includes the resolved scientific semantics and the
    producer-owned per-record lineage (logical index and accepted attempt,
    plus the canonical topology content (extent + passability) so
    equal content + equal semantics yield equal records regardless of worker
    scheduling, enumeration order, or payload filenames.
    """
    inputs: list[IdentityInput] = [
        IdentityInput("specification_reference", "dungeongen/v1"),
        IdentityInput("variant", configuration.variant),
        IdentityInput("generator_dependency", configuration.generator_dependency),
        IdentityInput("generator_protocol", configuration.generator_protocol),
        IdentityInput("generator_profile", configuration.generator_profile),
        IdentityInput("conversion_policy", configuration.conversion_policy),
        IdentityInput("component_selection_policy", configuration.component_selection_policy),
        IdentityInput("acceptance_policy", configuration.acceptance_policy),
        IdentityInput("duplicate_policy", configuration.duplicate_policy),
        IdentityInput("randomness_role", RANDOMNESS_ROLE),
        IdentityInput("logical_index", accepted.logical_index),
        IdentityInput("accepted_attempt", accepted.attempt),
        IdentityInput("seed", configuration.seed),
        IdentityInput("extent", (accepted.height, accepted.width)),
        IdentityInput("passable", list(accepted.passable)),
    ]
    return RealizationKey(inputs=tuple(inputs))


def execute(session: MaterializationSession) -> None:
    """Execute the DungeonGen producer operation against the framework session.

    Reads the opaque :class:`DungeonGenConfiguration`, verifies the frozen
    dependency is build-ready, generates and accepts one realization per
    requested logical topology index, materializes each through the framework's
    ``GeneratedRecordBody`` boundary using the shared ``raster-topology/v1``
    constructor, and contributes the complete production-lineage resource.

    The producer never performs framework-owned lifecycle work; it supplies
    realization-identity inputs and bounded lineage descriptors and lets the
    framework derive ``record_id``.
    """
    configuration = session.configuration
    if not isinstance(configuration, DungeonGenConfiguration):
        raise DungeonGenExecutionError(
            f"expected DungeonGenConfiguration, got {type(configuration).__name__}"
        )

    try:
        verify_dependency_build_ready()
    except GenerationError as exc:
        raise DungeonGenExecutionError(str(exc)) from exc

    accepted: list[AcceptedTopology] = []
    seen: set[tuple[int, int, tuple[bool, ...]]] = set()
    first_seen: dict[tuple[int, int, tuple[bool, ...]], int] = {}
    duplicate_reports: list[tuple[int, int, int, int]] = []
    record_ids: dict[tuple[int, int, tuple[bool, ...]], str] = {}

    for logical_index in range(configuration.record_count):
        outcome = run_logical_topology(
            configuration, logical_index, seen=seen, generator=generate_native
        )
        if isinstance(outcome, RejectionReason):
            raise DungeonGenExecutionError(outcome.message)
        assert isinstance(outcome, AcceptedTopology)
        # Under `allow`, repetition of an earlier canonical topology is detected
        # and reported without collapsing the records.
        key = (outcome.height, outcome.width, outcome.passable)
        if outcome.duplicated:
            first_logical = first_seen[key]
            duplicate_reports.append(
                (first_logical, outcome.logical_index, outcome.height, outcome.width)
            )
        else:
            first_seen[key] = outcome.logical_index
        accepted.append(outcome)
        topology = raster_topology(
            RectangularRowColumnDomain(outcome.height, outcome.width), outcome.passable
        )
        descriptors = (
            IdentityInput("logical_index", outcome.logical_index),
            IdentityInput("accepted_attempt", outcome.attempt),
            IdentityInput("lineage_resource", LINEAGE_RESOURCE_NAME),
        )
        record = session.add_record(
            GeneratedRecordBody(
                content=topology.content(),
                realization_key=_realization_key(configuration, outcome),
                descriptors=descriptors,
            )
        )
        record_ids[key] = record.record_id

    # Complete production lineage in a separate logical resource.
    session.add_logical_resource(
        LINEAGE_RESOURCE_NAME,
        build_lineage_resource(
            tuple(accepted),
            record_ids,
            duplicate_policy=configuration.duplicate_policy,
            seed=configuration.seed,
            duplicate_reports=tuple(duplicate_reports),
        ),
        resource_kind="lineage",
    )


__all__ = ["DungeonGenExecutionError", "execute"]
