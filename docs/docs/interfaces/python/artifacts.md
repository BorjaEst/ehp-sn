---
title: Artifact interface
authority: normative
status: specified
api_stability: provisional
---

# Artifact interface

EHP-SN artifacts are durable scientific outputs. Their manifests are the authoritative records of completed operations.

This page defines how Python callers use artifact identities and resources. Physical layouts, checksum algorithms, publication transactions, schema migration, and reference grammar belong to framework artifact specifications.

## Nominal reference types

```python
ArtifactRef
CheckpointRef
```

`ArtifactRef` identifies one committed artifact. `CheckpointRef` identifies one committed checkpoint resource owned by a committed training-run artifact.

Canonical strings may be parsed explicitly:

```python
artifact_ref = ArtifactRef.parse("artifact:...")
checkpoint_ref = CheckpointRef.parse("checkpoint:...")
```

The full canonical grammar is owned by the framework artifact specification. Public operations accept nominal references or canonical strings, not arbitrary strings, paths, and objects through one ambiguous parameter.

Filesystem locations use separate documented location parameters or constructors and are resolved into logical identities before planning.

## Core public types

### `ArtifactManifest`

The authoritative portable record of artifact identity, content digest, scientific inputs, resolved request and plan identities, execution provenance, declared resources, schema version, and commitment status.

### `Artifact`

An immutable loaded handle linked to one `ArtifactRef`. It exposes the manifest and lazy or bounded resource access without eagerly loading all payloads.

### `ResourceRef`

A nominal reference to one manifest-declared resource owned by an artifact. Its namespace and version grammar are defined outside this interface.

## Public capabilities

| Capability                         | Public contract                  | Status                                     |
| ---------------------------------- | -------------------------------- | ------------------------------------------ |
| Load a committed artifact          | `load_artifact(ref) -> Artifact` | Proposed helper symbol; behavior normative |
| Read manifest metadata             | `artifact.manifest`              | Stable public attribute                    |
| Query supported capabilities       | `artifact.capabilities`          | Stable public attribute                    |
| Open a declared resource           | `artifact.resources.open(ref)`   | Stable access capability                   |
| Obtain a bounded summary           | `artifact.inspect()`             | Stable public capability                   |
| Retrieve a recorded case           | `artifact.cases.get(case_id)`    | Stable when case capability is supported   |
| Serialize portable handle metadata | `artifact.to_record()`           | Stable public capability                   |

## Loading and process portability

```python
artifact = load_artifact(evaluation.artifact)
```

Loading resolves the nominal reference or explicit invocation location, verifies the manifest boundary and commitment state, and returns a typed handle. Large resources remain unloaded.

An `ArtifactRef`, `CheckpointRef`, manifest record, and `Artifact.to_record()` output are portable across processes. Open resource streams and backend handles are process-local and are recreated by loading the artifact again.

Pickle compatibility for loaded handles is not guaranteed.

## Manifest access

```python
manifest = artifact.manifest
print(manifest.identity)
print(manifest.content_digest)
print(manifest.kind)
print(manifest.status)
print(manifest.provenance)
```

The manifest interface exposes enough portable metadata to determine identity, commitment, schema compatibility, scientific inputs, executed plan, provenance, and declared resources.

## Resource access

```python
metrics = artifact.resources.open("<metrics-resource-ref>")
traces = artifact.resources.open("<trace-resource-ref>")
```

The placeholders deliberately do not define reference grammar. See [Framework semantics](../../framework/_index.md) for the owning specification area.

Required behavior:

- only manifest-declared resources can be opened;
- resource references remain linked to their owning artifact identity;
- large payloads use lazy, streaming, paged, or bounded access;
- opening a resource never mutates the artifact;
- schema and integrity checks occur before unsafe materialization;
- unsupported capabilities raise `CapabilityUnavailableError`;
- missing or corrupt declared resources raise `ResourceError` or `ArtifactIntegrityError`.

## Optional capabilities

`artifact.capabilities` permits callers to determine whether case, trace, prediction, table, figure, checkpoint, or other resource access is supported.

The policy is:

- unsupported capability: `CapabilityUnavailableError` on access;
- supported capability with zero records: empty immutable collection or bounded accessor reporting length zero;
- declared but missing resource: `ResourceError`;
- integrity mismatch: `ArtifactIntegrityError`;
- resource too large for direct materialization: a lazy handle is returned rather than silently loading it.

## Logical identity, content identity, and placement

| Concept                 | Public representation           | Meaning                                                                             |
| ----------------------- | ------------------------------- | ----------------------------------------------------------------------------------- |
| Artifact identity       | `ArtifactRef`                   | Durable identity used for selection and downstream inputs.                          |
| Artifact content digest | `manifest.content_digest`       | Integrity/content identity of the committed manifest and declared payload contract. |
| Resource identity       | `ResourceRef`                   | Identity of one artifact-owned resource.                                            |
| Physical placement      | explicit location/path metadata | One storage location; not portable identity.                                        |

Changing only placement does not change artifact identity unless the owning artifact specification explicitly says otherwise. Scientific equivalence does not imply byte-identical content digests.

## Checkpoint references

A `CheckpointRef` resolves:

- parent training-run `ArtifactRef`;
- checkpoint `ResourceRef`;
- checkpoint role and selection metadata where declared;
- experiment, model, corpus, lineage, and step metadata needed for resume or evaluation.

A checkpoint location is not a portable checkpoint identity. Only committed checkpoint resources are valid downstream references.

## Commitment and immutability

A successful operation result always points to a committed immutable artifact.

User-visible guarantees:

- committed artifacts are not overwritten in place;
- interrupted or failed operations do not masquerade as committed artifacts;
- external tracker entries and physical directory names do not override manifest authority;
- uncommitted staging information cannot be converted directly into an `ArtifactRef`;
- result return occurs only after commitment succeeds.

## Bounded inspection

```python
summary = artifact.inspect()

if "cases" in artifact.capabilities:
    case = artifact.cases.get("case-012")
```

Inspection is read-only and bounded by default. It reports selected manifest and resource metadata; it does not become a general scientific analysis or materialize entire datasets.

## Serialization expectations

`ArtifactRef`, `CheckpointRef`, `ResourceRef`, manifest metadata, and artifact handle records support JSON-compatible portable records.

Serialization records logical identities and metadata, not open resources or full payloads. Reloading in another process resolves the same logical artifact and verifies current availability and integrity.

## Exceptions

Artifact operations may raise:

- `ConfigurationError` for invalid canonical reference text;
- `ArtifactNotFoundError` when a logical artifact or resource cannot be resolved;
- `ArtifactIntegrityError` for manifest, schema, or digest violations;
- `CapabilityUnavailableError` for unsupported inspection or resource capabilities;
- `ResourceError` for unavailable declared payloads;
- `PublicationError` only from operations that create artifacts, not ordinary read-only loading.

## Reuse

Reuse policy is operation-specific. `ArtifactRef` and content digests provide the identities used by those policies; loading an artifact does not itself authorize scientific reuse.

## Related interfaces

- [Python interface overview](_index.md)
- [Training](training.md)
- [Evaluation](evaluation.md)
- [Analysis](analysis.md)
- [Shared conventions](conventions.md)
- [Framework semantics](../../framework/_index.md)

## Non-goals

This page does not define manifest JSON layout, directory trees, publication transactions, locking, checksum algorithms, storage adapters, content-addressable storage, or schema migration mechanics.
