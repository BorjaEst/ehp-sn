---
title: ObsField v1
authority: normative
document_status: draft
---

# ObsField v1

## Normative summary

`obsfield/v1` is a substrate family that procedurally generates persistent categorical observation fields conforming to [`categorical-field/v1`](../../framework/contracts/observations/categorical-field-v1.md) for downstream task-corpus construction.

One record represents one complete observation realization over exactly one self-contained ambient domain, conforming to the shared contract.
This document defines how such a realization is generated, its assignment protocols, and its family-specific configuration and identity.
The shared `categorical-field/v1` contract defines how tasks read and interpret the resulting field.

ObsField is independent of topology substrates.
It does not reference DungeonGen, Maze-ND, or any other topology artifact or record.
Topology and observation fields are peer substrate inputs selected and composed by a task builder.

ObsField owns assignment-protocol selection and generation.
It does not own traversability, walls, movement restrictions, agent experience, starts, goals, trajectories, queries, targets, rewards, task splits, or model-facing encodings.

## Scope and boundary

### Owned semantics

This specification defines:

- deterministic assignment protocols and realization identity;
- family-specific configuration and identity inputs;
- ObsField record and artifact invariants beyond the shared contract;
- family-specific validation;
- the information required for task-owned compatibility checks.

The ambient spatial domain, observation field, vocabulary, and logical record schema (`observation_id`) are owned by [`categorical-field/v1`](../../framework/contracts/observations/categorical-field-v1.md), not restated here.

### Excluded semantics

This specification does not define:

- walls, blocked positions, corridors, or irregular traversability;
- compact topology-state identifiers;
- topology edges or action-conditioned transitions;
- references to topology artifacts or topology records;
- task trajectories or experienced-observation sequences;
- starts, current states, goals, solutions, or terminal task conditions;
- task queries, rewards, supervision, or targets;
- hidden semantic structures or task-owned bindings;
- train, validation, or test composition;
- model tokens, tensors, masks, batches, or padding;
- generic artifact manifests, digests, lifecycle, publication, or reuse;
- CLI option spelling or configuration precedence;
- repository-local staging or cleanup paths.

Observation values assigned to positions that are blocked by a subsequently selected topology are valid ObsField content.
They are simply unused in that composition.

## Canonical identity and conformance

| Property                | Required value         |
| ----------------------- | ---------------------- |
| Artifact kind           | `substrate`            |
| Family                  | `obsfield`             |
| Specification reference | `obsfield/v1`          |
| Shared logical schema   | `categorical-field/v1` |

The canonical family identifier is `obsfield`.
`ObsField` is the display name.

A release conforms to this specification only when it satisfies the generic framework `SubstrateArtifact` contract, the complete `categorical-field/v1` contract, and every family-specific requirement and invariant defined here.

### Declared capabilities

ObsField v1's `categorical-complete` variant declares:

```text
coverage: total
value_kind: categorical
persistent: true
```

per [`categorical-field/v1`](../../framework/contracts/observations/categorical-field-v1.md) § "Capabilities".

### Variant model

ObsField v1 defines one initial variant:

```text
categorical-complete
```

Assignment profiles such as `unique`, `categorical-random`, `balanced`, and `landmark-background` are assignment protocols or presets, not variants.

A conforming release therefore uses:

```text
data/interim/obsfield/categorical-complete/v<N>/
```

The final `v<N>` is a framework release number, not the specification version.

## Conceptual model

### Assignment protocol

An assignment protocol defines how vocabulary entries are assigned to ambient positions.
It may constrain frequency, uniqueness, region structure, landmark placement, or another reusable observation-field property.
It must not define task trajectories, task queries, or experienced-observation sequences.

### Independent composition

See [`categorical-field/v1`](../../framework/contracts/observations/categorical-field-v1.md) § "Independent composition" for how a composed topology and observation-field record relate; ObsField does not redefine that relationship.

## Unit of record

One record represents one complete categorical observation realization over one canonical ambient spatial domain, per `categorical-field/v1`.
A record additionally contains, as ObsField-specific fields:

| Field                   | Meaning                               |
| ----------------------- | ------------------------------------- |
| `assignment_protocol`   | Protocol reference                    |
| `assignment_parameters` | Protocol-specific semantic parameters |
| `realization_index`     | Stable deterministic discriminator    |

### Record identifier

`record_id` is unique within one ObsField artifact and independent of physical storage location.
Its deterministic inputs include:

- specification reference;
- variant;
- canonical ambient-domain identity;
- vocabulary identity;
- assignment-protocol identity;
- assignment parameters;
- base seed;
- realization index.

The framework remains authoritative for the exact identifier and digest mechanisms.

## Assignment protocols

ObsField v1 permits registered deterministic assignment protocols.
At least one protocol must be implemented and normatively specified for a concrete release.

### `categorical-random/v1`

`categorical-random/v1` assigns one vocabulary entry independently to each canonical ambient position according to a declared categorical distribution.

Required parameters:

| Parameter           | Meaning                                                               |
| ------------------- | --------------------------------------------------------------------- |
| `distribution`      | Exact categorical probability vector or canonical uniform declaration |
| `base_seed`         | Base deterministic seed                                               |
| `realization_index` | Record-addressable realization discriminator                          |

For a uniform declaration, each vocabulary entry has probability `1 / K`.
Repeated observations are permitted.

The protocol must derive each record's random state independently from:

```text
base seed
canonical domain identity
vocabulary identity
assignment-protocol identity
assignment parameters
realization index
randomness role
```

### Other protocols

Protocols such as `unique`, `balanced`, or `landmark-background` may be added without creating new variants when they preserve the same record and channel semantics.
Each added protocol must define exact feasibility constraints, deterministic behavior, and failure conditions.

## Generation protocol

For each record, a conforming builder must semantically:

1. resolve one complete canonical ambient-domain declaration;
2. derive the canonical position set and position order;
3. resolve one immutable observation vocabulary;
4. resolve one registered assignment protocol and its parameters;
5. derive record-addressable deterministic random state;
6. assign exactly one observation to every ambient position;
7. canonicalize the assignment in `position_id` order;
8. derive the stable realization identity;
9. validate all family-specific invariants;
10. materialize the record through framework logical resources.

No stage resolves, reads, validates, or references a topology artifact.

## Determinism and randomness

For fixed semantic inputs, record content must not depend on:

- worker count;
- worker scheduling;
- generation order of other records;
- filesystem enumeration;
- temporary paths;
- logging or progress configuration.

Increasing the requested number of realizations for the same declared domain and protocol must not alter records with earlier realization indexes.
Adding records for another domain must not alter existing records.
A shared sequential release-global RNG stream is insufficient unless its use provably preserves these properties.

## Split semantics

ObsField v1 defines no intrinsic `train`, `validation`, or `test` membership.

Observation realizations form reusable pools.
Task specifications determine whether to:

- reuse one realization across task splits;
- prohibit realization overlap;
- vary topology while holding ObsField fixed;
- vary ObsField while holding topology fixed;
- test unseen topology-ObsField combinations.

Task-owned split composition must not be encoded as ObsField semantics.

## Configuration contract

### Semantic configuration

| Key                            | Type             | Requirement                    | Meaning                                                            | Family-specific build input |
| ------------------------------ | ---------------- | ------------------------------ | ------------------------------------------------------------------ | --------------------------: |
| `substrate.variant`            | string           | exactly `categorical-complete` | Coordinate variant                                                 |                         Yes |
| `domain.schema`                | string           | supported schema               | Canonical ambient-domain schema                                    |                         Yes |
| `domain.*`                     | schema-defined   | required                       | Complete domain parameters                                         |                         Yes |
| `vocabulary.identity`          | reference/string | required                       | Immutable vocabulary identity                                      |                         Yes |
| `vocabulary.cardinality`       | integer          | `>= 1`                         | Vocabulary size                                                    |                         Yes |
| `assignment.protocol`          | string           | registered protocol            | Assignment semantics                                               |                         Yes |
| `assignment.parameters`        | mapping          | protocol-defined               | Protocol parameters                                                |                         Yes |
| `generation.seed`              | integer          | required                       | Base deterministic seed                                            |                         Yes |
| `generation.realization_count` | integer          | `>= 1`                         | Number of realizations requested per declared domain/configuration |                         Yes |

When several ambient domains or vocabularies are generated in one artifact, the configuration must define their deterministic enumeration explicitly.

### Operational configuration

Worker count, cache location, staging location, logging, and progress reporting are operational.
They must not alter scientific content.

## Family-specific identity inputs

ObsField contributes the following semantic inputs to framework build identity:

- specification reference;
- variant;
- shared logical schema reference;
- complete canonical ambient-domain declarations;
- canonical domain-schema versions;
- vocabulary identities and cardinalities;
- assignment-protocol references;
- assignment parameters;
- canonical position-order policy;
- randomness derivation policy;
- base seed;
- realization counts and realization indexes.

ObsField contributes no parent topology identity, topology record ID, topology fingerprint, or topology schema.

## Framework contract instantiation

In addition to the generic `SubstrateArtifact` contract and the `categorical-field/v1` contract, a conforming ObsField release must declare:

| Framework property      | ObsField requirement             |
| ----------------------- | -------------------------------- |
| Specification reference | exactly `obsfield/v1`            |
| Family                  | exactly `obsfield`               |
| Variant                 | exactly `categorical-complete`   |
| Shared logical schema   | `categorical-field/v1`           |
| Assignment descriptors  | protocol and semantic parameters |
| Intrinsic splits        | none                             |

The framework remains authoritative for manifest serialization, resources, digests, fingerprints, staging, publication, reuse, and conflicts.

## Logical resources and enumeration

A conforming artifact must expose logical resources sufficient to:

- enumerate ObsField records deterministically;
- resolve each record's ambient-domain declaration;
- resolve its vocabulary declaration;
- resolve assignment-protocol metadata;
- load the complete `observation_id` field.

No fixed physical filename or serialization is required by this specification.
Each record index entry must contain or resolve:

- `record_id`;
- payload locator;
- record-schema reference;
- canonical domain identity;
- vocabulary identity;
- assignment-protocol identity;
- realization index.

No index entry contains a topology parent reference.

## Family-specific invariants and validation

Common ambient-domain, observation-field, and vocabulary invariants are owned by [`categorical-field/v1`](../../framework/contracts/observations/categorical-field-v1.md) and are not duplicated here.

### OF-REC-008 — Assignment-protocol conformance

The field satisfies every hard constraint of its declared assignment protocol.

### OF-REC-009 — Record identity consistency

The declared record identity agrees with the canonical family-specific record inputs and committed content under the framework identity contract.

### OF-ART-001 — Specification consistency

Every record conforms to `obsfield/v1` and `categorical-field/v1`.

### OF-ART-002 — Variant consistency

Every record satisfies `categorical-complete` semantics.

### OF-ART-003 — No intrinsic experimental splits

The artifact does not assign records to `train`, `validation`, or `test` as ObsField-owned semantics.

### OF-ART-005 — Descriptor consistency

Artifact-level declared domains, vocabularies, protocols, and counts agree with record content.

### Validation requirements

Full validation must invoke the shared `categorical-field/v1` checks in addition to the family-specific checks above.
Diagnostics should identify the artifact coordinate, record ID, invariant identifier, and observed versus expected value.

## Task-owned compatibility and composition

See [`categorical-field/v1`](../../framework/contracts/observations/categorical-field-v1.md) § "Task-owned compatibility and composition" for how a task builder checks compatibility with a topology record; ObsField does not redefine that relationship.

## Downstream-use boundary

Task builders may consume:

- record identity;
- canonical ambient-domain declaration;
- vocabulary identity;
- assignment-protocol identity;
- `observation_id` values.

Tasks own:

- selection of compatible topology and ObsField records;
- topology-to-ambient-position mappings;
- restriction of observations to traversable positions;
- starts, goals, and current-state conditions;
- trajectories and experienced observations;
- hidden-semantic bindings;
- queries, targets, rewards, and supervision;
- task splits;
- model-facing encodings.

No task may infer vocabulary compatibility solely from matching integer ranges or cardinalities.

## Compatibility and evolution

### New release under `obsfield/v1`

A new release may change:

- ambient-domain instances or parameters;
- vocabulary identities or sizes;
- assignment protocols or parameter values;
- seed;
- realization count;
- concrete assignments.

It remains `obsfield/v1` when one record still means one complete categorical field over one self-contained ambient domain conforming to `categorical-field/v1`, and no topology dependency is introduced.

### New specification version

A new specification version is required for incompatible changes such as changing assignment-protocol ownership, or any change that would also require a new `categorical-field/v1` version (see that contract's own "Compatibility and evolution").

## Open issues

ObsField v1 remains `draft` until the following are finalized:

1. `categorical-field/v1` and `ambient-domain/v1` themselves (currently `draft`);
2. the exact canonical hex coordinate, finite-shape, and enumeration contract;
3. the topology-to-ambient-position mapping contract used by topology substrates;
4. the immutable vocabulary-reference and vocabulary-identity contract.

## Related specifications

- [`Substrates`](index.md)
- [`Categorical field v1`](../../framework/contracts/observations/categorical-field-v1.md)
- [`Ambient spatial domain v1`](../../framework/contracts/domains/ambient-domain-v1.md)
- [`Data artifacts`](../../framework/data-artifacts.md)
- [`Manifests`](../../framework/manifests.md)
- [`Identity`](../../framework/identity.md)
- [`Digests`](../../framework/digests.md)
- [`Provenance`](../../framework/provenance.md)
- [`References`](../../framework/references.md)
- [`Data CLI`](../../interfaces/cli/data.md)
- [`Data layout`](../../development/data-layout.md)
