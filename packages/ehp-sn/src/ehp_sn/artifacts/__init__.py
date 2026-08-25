"""Generic framework data-artifact lifecycle (Phase 4B).

This package owns the generic, framework-level substrate-artifact lifecycle that
closes an uncommitted :class:`~ehp_sn.execution.MaterializationResult` into a
committed logical :class:`SubstrateArtifact`:

```text
ExecutionPlan + MaterializationResult
        ↓  assemble_artifact
AssembledArtifact          (framework metadata; WHAT was materialized)
        ↓  find_reusable / commit_artifact
committed SubstrateArtifact
```

It follows the same discipline as ``ehp_sn.planning`` and ``ehp_sn.execution``:
it consumes the authoritative plan and its plan-bound materialization exactly
once, never re-resolves configuration, never invokes the producer, and never
branches on a substrate family (``ARCH-001``). Artifact assembly is
deliberately not a ``SubstrateArtifact`` and not a store/repository facade.

This lifecycle is *edition-focused and logical*: it establishes correct artifact
identity (build-input identity, artifact fingerprint), resource descriptors and
digests, portable provenance, and deterministic reuse/conflict semantics. It
does not allocate release numbers, touch Git, or publish physical coordinates.
"""

from __future__ import annotations

from .artifact import SubstrateArtifact
from .assembly import AssembledArtifact, assemble_artifact
from .build import BuildError, build_substrate
from .commit import CommitConflictError, commit_artifact, find_reusable
from .descriptors import LogicalResourceDescriptor, ProducerDescriptor, RecordIndexEntry
from .identity import artifact_fingerprint, build_input_identity
from .outcome import BuildOutcome
from .provenance import build_semantic_provenance, provenance_resource_digest

__all__ = [
    "AssembledArtifact",
    "BuildError",
    "BuildOutcome",
    "CommitConflictError",
    "LogicalResourceDescriptor",
    "ProducerDescriptor",
    "RecordIndexEntry",
    "SubstrateArtifact",
    "artifact_fingerprint",
    "assemble_artifact",
    "build_input_identity",
    "build_semantic_provenance",
    "build_substrate",
    "commit_artifact",
    "find_reusable",
    "provenance_resource_digest",
]
