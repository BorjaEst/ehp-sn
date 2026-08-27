"""DungeonGen substrate family container.

Exposes the authoritative ``substrate:dungeongen/v1`` definition object
(``DUNGEONGEN_DEFINITION``) at the discovery level, and the producer-owned
configuration surface (``resolve_configuration``, ``DungeonGenConfiguration``,
``DungeonGenConfigurationError``), planning resolver (``plan``), and execution
operation (``execute``) with their scientific owner. It also re-exports the
DungeonGen dependency/protocol/seed-derivation, conversion/normalization/
component-selection, acceptance/retry, and lineage building blocks so tests and
callers address them at the family boundary. This package only re-exports and
contains these; it defines no framework lifecycle semantics itself.

The frozen external dependency identity (``dungeongen`` package `0.1.14` at Git
revision ``2d228f5…``) and the EHP-SN reference protocol/profile/policy
references live in :mod:`.dungeongen._dependency`; see
``docs/docs/research/substrates/dungeongen-v1.md`` § "First release dependency
and protocol decision".
"""

from __future__ import annotations

from ._dependency import (
    ACCEPTANCE_POLICY,
    COMPONENT_SELECTION_POLICY,
    CONVERSION_POLICY,
    DEPENDENCY_REFERENCE,
    LINEAGE_SCHEMA,
    PACKAGE_DEPENDENCY,
    PROFILE_REFERENCE,
    PROTOCOL_REFERENCE,
    RANDOMNESS_ROLE,
    UPSTREAM_REPOSITORY,
    UPSTREAM_REVISION,
)
from .acceptance import (
    AcceptedTopology,
    Rejection,
    RejectionReason,
    evaluate,
    run_logical_topology,
)
from .configuration import (
    DungeonGenConfiguration,
    DungeonGenConfigurationError,
    GeneratorProfile,
    SizePolicy,
    resolve_configuration,
)
from .conversion import (
    ConversionError,
    convert_to_passability,
    is_passable_native_cell,
    largest_component,
    normalize_extent,
)
from .definition import DUNGEONGEN_DEFINITION
from .execution import DungeonGenExecutionError, execute
from .generation import (
    GenerationError,
    NativeCandidate,
    candidate_seed,
    generate_native,
    to_upstream_params,
    verify_dependency_build_ready,
)
from .lineage import (
    LINEAGE_RESOURCE_NAME,
    build_lineage_resource,
    record_lineage,
)
from .planning import plan as plan

__all__ = [
    "ACCEPTANCE_POLICY",
    "AcceptedTopology",
    "COMPONENT_SELECTION_POLICY",
    "CONVERSION_POLICY",
    "ConversionError",
    "DEPENDENCY_REFERENCE",
    "DUNGEONGEN_DEFINITION",
    "DungeonGenConfiguration",
    "DungeonGenConfigurationError",
    "DungeonGenExecutionError",
    "GenerationError",
    "GeneratorProfile",
    "LINEAGE_RESOURCE_NAME",
    "LINEAGE_SCHEMA",
    "NativeCandidate",
    "PACKAGE_DEPENDENCY",
    "PROFILE_REFERENCE",
    "PROTOCOL_REFERENCE",
    "RANDOMNESS_ROLE",
    "Rejection",
    "RejectionReason",
    "SizePolicy",
    "UPSTREAM_REPOSITORY",
    "UPSTREAM_REVISION",
    "build_lineage_resource",
    "candidate_seed",
    "convert_to_passability",
    "evaluate",
    "execute",
    "generate_native",
    "is_passable_native_cell",
    "largest_component",
    "normalize_extent",
    "plan",
    "record_lineage",
    "resolve_configuration",
    "run_logical_topology",
    "to_upstream_params",
    "verify_dependency_build_ready",
]
