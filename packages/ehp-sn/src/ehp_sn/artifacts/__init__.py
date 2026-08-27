"""Generic framework data-artifact lifecycle (Phase 4B / 4B-D).

This package owns the generic, framework-level substrate-artifact lifecycle that
turns an uncommitted :class:`~ehp_sn.execution.MaterializationResult` into a
**durable committed** :class:`SubstrateArtifact`:

```text
ExecutionPlan + MaterializationResult
        ↓  assemble_artifact
AssembledArtifact          (assembled candidate; WHAT was materialized)
        ↓  publish_artifact
durable committed SubstrateArtifact
```

Distinct lifecycle states are not conflated:

```text
materialized   producer output exists but is uncommitted (MaterializationResult)
assembled      complete immutable artifact candidate      (AssembledArtifact)
committed      candidate durably published and resolvable (SubstrateArtifact)
```

It follows the same discipline as ``ehp_sn.planning`` and ``ehp_sn.execution``:
it consumes the authoritative plan and its plan-bound materialization exactly
once, never re-resolves configuration, never invokes the producer, and never
branches on a substrate family (``ARCH-001``).

This lifecycle owns release-coordinate semantics, physical publication staging,
publication integrity, atomic publication, deterministic reuse/conflict
semantics, and durable committed-artifact resolution. It does not auto-assign
release numbers, touch Git, or offer a remote/database persistence backend.
"""

from __future__ import annotations

from .artifact import SubstrateArtifact
from .assembly import AssembledArtifact, assemble_artifact
from .build import build_substrate
from .build_errors import (
    BuildError,
    ConflictBuildError,
    InvalidExistingStateBuildError,
    ReleaseNotConfiguredBuildError,
)
from .commit import (
    CommitConflictError,
    InvalidExistingStateError,
    ReleaseNotConfiguredError,
    find_reusable,
    publish_artifact,
)
from .descriptors import LogicalResourceDescriptor, ProducerDescriptor, RecordIndexEntry
from .identity import artifact_fingerprint, build_input_identity
from .outcome import BuildOutcome
from .provenance import build_semantic_provenance, provenance_resource_digest
from .resolve import load_release, resolve_release
from .store import (
    ExistingState,
    StoreError,
    artifact_ref,
    inspect_release,
    release_path,
)

__all__ = [
    "AssembledArtifact",
    "BuildError",
    "BuildOutcome",
    "CommitConflictError",
    "ConflictBuildError",
    "ExistingState",
    "InvalidExistingStateBuildError",
    "InvalidExistingStateError",
    "LogicalResourceDescriptor",
    "ProducerDescriptor",
    "RecordIndexEntry",
    "ReleaseNotConfiguredBuildError",
    "ReleaseNotConfiguredError",
    "StoreError",
    "SubstrateArtifact",
    "artifact_fingerprint",
    "artifact_ref",
    "assemble_artifact",
    "build_input_identity",
    "build_semantic_provenance",
    "build_substrate",
    "find_reusable",
    "inspect_release",
    "load_release",
    "provenance_resource_digest",
    "publish_artifact",
    "release_path",
    "resolve_release",
]
