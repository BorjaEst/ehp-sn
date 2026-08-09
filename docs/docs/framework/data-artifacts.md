---
title: Data artifacts
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Data artifacts

EHP-SN represents generated scientific data as immutable, manifest-governed artifacts.

This document defines the framework contract shared by generated data artifacts and the additional requirements of substrate artifacts. Task-corpus-specific requirements are defined in [Corpora](corpora.md).

The generic rules for manifests, identity, digests, provenance, and references remain authoritative in their dedicated framework documents. This page applies those rules to generated data; it does not redefine them.

## Scope

This document defines:

- the `DataArtifact` and `SubstrateArtifact` contracts;
- the conventional coordinates for committed substrate and corpus releases;
- release numbering and coordinate immutability;
- build-input identity and post-build content verification;
- required logical resources;
- lifecycle, validation, reuse, conflict handling, and publication;
- the ownership boundary between `ehp_sn` and `ehp_research`.

It does not define:

- the repository-wide purpose of `data/external/` or `data/raw/`;
- concrete substrate channels or payload schemas;
- task cases, episodes, inputs, targets, or supervision;
- canonical manifest serialization or digest algorithms;
- package-specific generation values.

The repository data layout is described in [Data layout](../development/data-layout.md).

## Data-artifact types

The framework distinguishes these semantic data-artifact types:

```text
DataArtifact
├── SubstrateArtifact
└── TaskCorpus
```

`DataArtifact` defines common manifest-governed access and integrity behavior.

`SubstrateArtifact` adds the requirements of a task-neutral world or structure.

`TaskCorpus` adds the requirements of task-specific cases, episodes, inputs, and targets. Its contract is defined in [Corpora](corpora.md).

A shared implementation may provide:

- manifest loading;
- release-coordinate parsing;
- index access;
- resource lookup;
- payload loading;
- digest verification;
- bounded inspection;
- physical-location resolution.

The common implementation must preserve the semantic distinction between substrate artifacts and task corpora.

## Substrate artifact

A substrate artifact is an immutable, versioned collection of task-neutral environments or structures.

Depending on its concrete `ehp_research` specification, a substrate may contain:

- topology or geometry;
- valid locations or connectivity;
- environment-level observations;
- regions or landmarks;
- source annotations;
- intrinsic split membership.

A substrate artifact must not define:

- task episodes;
- task-specific trajectories;
- task inputs or targets;
- rewards;
- model tokenization;
- training batches;
- evaluation metrics.

The same substrate artifact may be reused by multiple task-corpus builders.

## Conventional release coordinates

Committed substrate releases use:

```text
data/interim/<family>/<variant>/v<N>/
```

Committed task-corpus releases use:

```text
data/processed/<task>/<corpus>/v<N>/
```

These paths are human-facing release coordinates. They do not, by themselves, verify content identity.

The physical placement convention belongs to the monorepo workspace. A logical artifact reference may resolve to another physical location when a configured persistence backend is used.

## Release numbering

`v<N>` is a monotonically increasing release number.

The sequence is scoped independently to each:

```text
(family, variant)
```

or:

```text
(task, corpus)
```

For example, `arena/default/v3` has no ordering relationship with `arena/dungeons/v2`.

Any intentional change that produces different artifact content requires a new release number. This includes changes to:

- schema or protocol;
- channel definitions;
- dtypes or shape semantics;
- effective configuration;
- source or parent identity;
- split assignment;
- generation seed;
- builder semantics;
- generated payload content.

Accidental mutation or corruption of a committed release does not create a new valid release. It makes the existing release invalid. A corrected artifact must be rebuilt from an explicit configuration and published under a new release coordinate.

## Version source and overrides

The release number is declared in configuration and becomes part of the resolved effective configuration.

Precedence is:

```text
package default
< configuration file
< --set override
```

`--version` is a root-level CLI interface that reports the installed tool version; it is not a release-number override.
The release number is set through configuration or `--set`.

The framework must not auto-assign the next release number.

## Published-coordinate immutability

Once committed, a release coordinate is permanently bound to its committed manifest and content fingerprint.

A committed coordinate must never be:

- overwritten;
- renumbered;
- reused for different content;
- rebound to another manifest fingerprint.

A failed, unpublished staging build may be retried.

## Required logical resources

A committed data artifact must declare at least these logical resources:

- one authoritative manifest;
- one resolved-configuration resource;
- one provenance resource;
- one artifact index;
- all payload resources required by the concrete artifact specification.

The default local serialization is expected to use names such as:

```text
manifest.json
config.resolved.toml
provenance.json
index.jsonl
```

Those filenames are conventional, not semantic. The manifest identifies the authoritative resource roles and their relative locations.

A physical `splits/` directory is permitted and is the default local organization, but it is not required by the framework contract.
Split membership and split-owned payloads are declared by the manifest and index.

The artifact index provides access to logical records, but the generic per-record identity/envelope contract is not yet specified.
See [Contracts](contracts/index.md) § "Per-record identity and record envelope — deferred".

## Manifest, configuration, and provenance authority

The dedicated framework documents define generic manifest, identity, digest, and provenance semantics.

For data artifacts, the division of authority is:

- `manifest`: authoritative artifact descriptor and identity-bearing declarations;
- resolved configuration: complete effective builder configuration;
- provenance: integrity-protected audit and derivation evidence.

The manifest must record the resource digest of both the resolved configuration and provenance resources.

Validation must enforce:

- the recorded configuration digest matches the resolved-configuration bytes;
- the recorded provenance digest matches the provenance bytes;
- any identity-bearing assertion repeated across resources is consistent with the manifest.

Audit-only provenance fields, such as hostnames, timestamps, absolute paths, or runtime details, do not need to equal manifest fields and do not participate in artifact identity unless another normative specification explicitly says otherwise.

The provenance resource is integrity-protected but excluded from the artifact identity projection by default.

## Resource descriptors and digests

Every payload resource must have an individual resource digest.

A resource descriptor must identify at least:

- logical resource name;
- relative physical location or storage key;
- media or storage type;
- byte size;
- schema reference;
- resource digest;
- identity-bearing status;
- split association, where applicable.

Payload resources and the resolved configuration are identity-bearing by default.

Audit resources, including provenance, are integrity-protected but not identity-bearing by default.

The digest algorithm and canonical representation are defined by [Digests](digests.md).

## Build-input identity

Planning requires an identity that can be computed before payload generation.

The **build-input identity** is derived from the resolved identity-affecting inputs, including:

- artifact kind;
- substrate or task reference;
- family and variant, or task and corpus name;
- release version;
- resolved configuration digest;
- generation seed or seed roles;
- source fingerprints;
- parent artifact fingerprints;
- builder protocol identity;
- declared schema and channel contract.

The build-input identity does not include output resource digests because those do not exist before generation.

It is used to compare a planned build with an existing committed release.

## Artifact fingerprint

The **artifact fingerprint** verifies the committed artifact after payload generation.

It is derived from the canonical identity projection defined by the framework identity and digest contracts.
For data artifacts, that projection includes the build-input identity fields and all identity-bearing resource descriptors and digests.

It excludes:

- the fingerprint field itself;
- provenance-resource content and digest by default;
- timestamps;
- hostnames;
- absolute paths;
- physical storage locations;
- other audit-only fields.

The artifact fingerprint is not generally computable before generation.

## Planning states

Planning compares the resolved build-input identity with the destination, without writing output.

It classifies the destination as:

### Available

The release coordinate does not contain a committed valid artifact.

The build may generate and publish a new artifact.

### Reusable

The coordinate contains a committed valid artifact whose recorded build-input identity matches the planned build-input identity, whose required resources are available, and whose recorded digests validate.

The operation may return the existing artifact as a successful no-op.

Reuse trusts the committed artifact's validated resource digests; it does not recompute unknown future output digests.

### Conflict

The coordinate contains a committed artifact whose build-input identity differs from the planned build-input identity, or whose kind or release declaration is incompatible.

The build must fail. The user must select a new release number.

### Invalid existing state

The coordinate exists but is incomplete, uncommitted, unreadable, or fails required validation.

It is not reusable. Removal or replacement is permitted only under the explicit incomplete-state policy; a committed valid release must never be replaced.

## Lifecycle

A data artifact moves through:

```text
planned
→ staging
→ validated
→ committed
```

Only a committed artifact is available for normal framework consumption.

### Planned

Configuration, version, inputs, destination, and build-input identity are resolved. No output is written.

### Staging

Payloads are generated in an isolated temporary location. Staging output must not appear as committed data.

### Validated

The staged artifact has passed required structural, integrity, and concrete scientific validation.

### Committed

The validated artifact has been atomically published at its release coordinate or persistence destination.

## Validation

Validation is read-only.

Generic data-artifact validation must check, as applicable:

- supported manifest schema;
- artifact kind;
- completion state;
- release coordinate and manifest agreement;
- required logical resources;
- configuration and provenance resource digests;
- payload resource digests;
- index consistency;
- split declarations;
- channel declarations;
- source or parent references;
- concrete substrate- or corpus-specific invariants.

Validation failure must not repair or mutate an artifact implicitly.

## Publication

A build operation must:

1. load and validate the effective configuration;
2. resolve the explicit release version;
3. resolve source and parent artifacts;
4. compute the build-input identity;
5. classify the destination;
6. return an existing reusable artifact, or generate into isolated staging;
7. write payload resources and compute their digests;
8. write the resolved configuration and provenance;
9. construct the manifest and artifact fingerprint;
10. validate the staged artifact;
11. atomically publish it;
12. return the committed artifact reference.

A failed build must not leave a destination that appears committed.

## Framework ownership

`ehp_sn` owns:

- data-artifact kinds and typed contracts;
- common artifact loading and validation orchestration;
- build-input identity and artifact-fingerprint application;
- release semantics;
- planning states;
- staging and publication;
- logical reference resolution.

`ehp_research` owns:

- concrete substrate definitions;
- scientific channel schemas;
- generation parameters;
- substrate builders;
- concrete validation rules;
- package-owned default configurations.

## Related documents

- [Artifacts](artifacts.md)
- [Manifests](manifests.md)
- [Identity](identity.md)
- [Digests](digests.md)
- [Provenance](provenance.md)
- [References](references.md)
- [Corpora](corpora.md)
- [Data layout](../development/data-layout.md)
- [`ehp-sn data`](../interfaces/cli/data.md)
- [`ehp-sn tasks`](../interfaces/cli/tasks.md)
