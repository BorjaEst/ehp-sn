---
title: Corpora
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Corpora

A task corpus is an immutable, self-contained collection of task-specific records derived from one or more exact parent data artifacts.

Task corpora are produced by `ehp-sn tasks` and consumed by training, evaluation, validation, inspection, and declared analyses.

This document defines the generic framework contract. Concrete task channels, record semantics, generation policies, and scientific invariants belong to the corresponding `ehp_research` task specifications.

## Scope

This document defines:

- the `TaskCorpus` contract;
- corpus completeness;
- mandatory corpus indexing;
- parent artifact provenance;
- copied, derived, and generated resource lineage;
- split inheritance;
- generic channel descriptors;
- corpus validation;
- consumer requirements.

It does not define:

- concrete task channels;
- task-specific target formulas;
- model inputs or tokenization;
- training batch construction;
- evaluation metrics;
- package-specific generation values.

Release identity, lifecycle, planning, validation orchestration, and publication are defined in [Data artifacts](data-artifacts.md).

## Task corpus

A task corpus contains task-specific records such as cases, episodes, trajectories, sequences, or environment projections.

Depending on the task specification, it may contain:

- public inputs;
- targets;
- privileged or oracle-only channels;
- masks and structural controls;
- identifiers and metadata;
- task-specific sequences;
- materialized substrate-derived context.

The task specification defines what one logical record means.

## Self-contained requirement

A task corpus is self-contained when every required channel declared by its manifest can be resolved entirely from corpus-local resources for every scope instance to which that channel applies.

The manifest channel schema is the completeness contract.

The corpus must not require access to parent artifacts during normal:

- training;
- evaluation;
- validation;
- inspection;
- transport;
- declared analysis execution.

Parent identities remain mandatory provenance, but they are not runtime dependencies.

If a consumer needs information that is not declared by the corpus channel schema, the corpus does not satisfy that consumer contract. Adding or changing the required information requires a new corpus release.

## Required logical resources

In addition to the common data-artifact resources, every task corpus must declare:

- one corpus index resource;
- one or more payload resources containing all required channels;
- parent artifact descriptors;
- resource-lineage descriptors.

The default index serialization is `index.jsonl`, but the framework contract requires an abstract corpus index, not a particular filename or storage encoding.

## Corpus index

The corpus index provides deterministic enumeration of logical corpus records.

Each index entry must contain at least:

- stable record identifier;
- corpus split;
- payload resource or storage key;
- record schema version.

When the record is derived from parent data, the entry must also contain:

- parent artifact fingerprint;
- parent record identifier;
- parent split.

A task specification may define additional fields.

The index may point to one record per payload, multiple records within a shard, or another declared storage organization.
The task specification defines the record unit; the index must make that unit addressable without scanning storage implicitly.

## Parent artifacts

A corpus manifest must record every parent artifact that contributed to the corpus.

Each parent descriptor must identify at least:

- parent role;
- logical reference;
- artifact kind;
- release coordinate;
- artifact fingerprint;
- relevant split declarations;
- lineage relations for affected corpus resources.

Deleting, moving, or making the parent unavailable after corpus publication must not prevent normal use of the committed corpus.

## Resource lineage

Every corpus payload resource must declare one lineage relation.

### Copied

A copied resource is byte-preserving materialization of a parent resource.

The lineage descriptor must identify:

- parent artifact fingerprint;
- parent resource name and digest;
- corpus resource name and digest.

For a valid copied relation, the parent and corpus resource digests must match.

### Derived

A derived resource is a deterministic transformation of one or more parent resources.

The lineage descriptor must identify:

- parent artifact fingerprints;
- parent resource names and digests;
- transformation or builder-protocol identity;
- effective configuration digest;
- resulting corpus resource and digest.

Derived resources are not required to match parent bytes.

### Generated

A generated resource is produced by task semantics, effective configuration, randomness, and optionally parent data.

The lineage descriptor must identify:

- task or generator reference;
- builder-protocol identity;
- effective configuration digest;
- generation seed or seed role;
- parent artifact fingerprints when applicable;
- resulting corpus resource and digest.

The framework does not require element-level lineage.

## Splits

A task specification declares the corpus split names and roles.

Common roles are:

```text
train
validation
test
```

The framework does not require these names for every task.

Each split descriptor must identify:

- split name;
- split role;
- record count;
- index coverage;
- payload resources or storage partitions;
- covered resource digests or split fingerprint.

Split semantics are declared in metadata. A physical `splits/` directory is a conventional serialization, not a framework requirement.

## Parent-to-corpus split inheritance

A corpus record in split `S` must derive only from parent records in split `S`.

Examples:

```text
corpus train record      → parent train record
corpus validation record → parent validation record
corpus test record       → parent test record
```

Cross-split derivation is a validation failure.

The corpus index must contain enough parent information to check this invariant.

A task requiring deliberate split transformation must define a separate explicit normative contract.
It must not weaken this rule implicitly.

## Channel schema

The manifest declares the corpus channel schema.

Each channel descriptor must identify:

- channel name;
- semantic role;
- required or optional status;
- scope;
- dtype;
- shape semantics;
- schema reference;
- resource mapping.

Generic roles include:

- input;
- target;
- privileged;
- metadata;
- mask;
- identifier;
- parent-derived context.

Typical scopes include:

- corpus-level;
- split-level;
- record-level;
- step-level.

A required channel is complete only when it is resolvable for every applicable scope instance declared by the index and manifest.

A change to channel presence, role, meaning, dtype, shape semantics, scope, required status, or mapping semantics requires a new release.

## Corpus identity application

A task corpus uses the build-input identity and artifact-fingerprint contracts defined in [Data artifacts](data-artifacts.md).

For corpora, the build-input identity includes at least:

- task reference;
- corpus name;
- release version;
- channel contract;
- split contract;
- parent artifact fingerprints;
- effective configuration digest;
- task-builder protocol identity;
- generation seed or seed roles.

The final artifact fingerprint additionally includes identity-bearing payload resource descriptors and digests.

Lineage descriptors participate in identity when they affect how corpus resources were produced.

## Manifest requirements

In addition to the common data-artifact fields, a task-corpus manifest must identify at least:

- artifact kind `task_corpus`;
- task reference;
- corpus name;
- release version;
- channel descriptors;
- split descriptors;
- corpus index resource;
- parent descriptors;
- lineage descriptors;
- record counts;
- effective configuration resource and digest;
- builder-protocol identity;
- generation seed or seed roles;
- build-input identity;
- artifact fingerprint;
- completion state.

The generic manifest schema remains authoritative in [Manifests](manifests.md).

## Validation

Corpus validation is read-only and must support at least:

### Manifest validation

Checks:

- supported manifest schema;
- artifact kind;
- completion state;
- required logical resources;
- channel, split, parent, and lineage descriptors;
- index declaration;
- configuration and provenance integrity.

### Sample validation

Checks a deterministic bounded sample of records against:

- index consistency;
- channel presence and schema;
- split inheritance;
- parent references;
- task-specific structural invariants.

### Full validation

Checks all records and all required payload digests, plus every task-specific semantic invariant.

Generic corpus validation must reject:

- missing required channels;
- missing or inconsistent index entries;
- undeclared payload resources;
- cross-split derivation;
- invalid copied-resource digests;
- unresolved parent descriptors;
- incompatible task or schema declarations;
- incomplete or uncommitted artifacts.

## Consumer requirements

Training, evaluation, inspection, and analysis consumers must:

1. resolve one exact corpus artifact;
2. verify its artifact kind and supported schema;
3. select records through the declared index and split metadata;
4. resolve channels through manifest mappings;
5. reject missing required channels;
6. record the exact corpus reference and artifact fingerprint in resulting run artifacts.

Consumers must not:

- silently search for a parent substrate;
- infer scientific semantics from filenames;
- mutate the corpus;
- reinterpret a declared split;
- silently derive undeclared required channels.

## Framework and research ownership

`ehp_sn` owns:

- the generic `TaskCorpus` contract;
- index mechanics;
- split inheritance rules;
- lineage relation mechanics;
- generic channel descriptors;
- corpus loading and validation orchestration.

`ehp_research` owns:

- concrete task definitions;
- record meaning;
- concrete channel schemas;
- task-generation policies;
- task builders;
- task-specific validation;
- package-owned default configurations.

## Related documents

- [Data artifacts](data-artifacts.md)
- [Artifacts](artifacts.md)
- [Manifests](manifests.md)
- [Identity](identity.md)
- [Digests](digests.md)
- [Provenance](provenance.md)
- [Arena v1](../research/tasks/arena.md)
- [`ehp-sn tasks`](../interfaces/cli/tasks.md)
