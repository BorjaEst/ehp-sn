---
title: ObsField v1
authority: normative
status: draft
---

# ObsField v1

## Normative summary

`obsfield/v1` defines persistent categorical observation fields over canonical
ambient spatial domains for downstream task-corpus construction.

One record represents one complete observation realization over exactly one
self-contained ambient domain. The record assigns exactly one categorical
observation to every canonical position in that domain.

ObsField is independent of topology substrates. It does not reference
DungeonGen, Maze-ND, or any other topology artifact or record. Topology and
observation fields are peer substrate inputs selected and composed by a task
builder.

Given an ambient domain `D`, an ObsField record defines a total mapping:

```text
O : D -> V
```

where `V` is one immutable observation vocabulary. A compatible topology may
later define a traversable subset `V_T ⊆ D` and movement relation over that
subset. The task builder then uses the restricted field `O|V_T`.

ObsField owns persistent environment-level observation assignment. It does not
own traversability, walls, movement restrictions, agent experience, starts,
goals, trajectories, queries, targets, rewards, task splits, or model-facing
encodings.

## Scope and boundary

### Owned semantics

This specification defines:

- one self-contained ambient spatial domain per record;
- canonical position identity and enumeration within that domain;
- categorical observation vocabularies and vocabulary identity;
- one observation assignment for every ambient-domain position;
- deterministic assignment protocols and realization identity;
- family-specific configuration and identity inputs;
- ObsField record and artifact invariants;
- family-specific validation;
- the information required for task-owned compatibility checks.

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

Observation values assigned to positions that are blocked by a subsequently
selected topology are valid ObsField content. They are simply unused in that
composition.

## Canonical identity and conformance

| Property                | Required value         |
| ----------------------- | ---------------------- |
| Artifact kind           | `substrate`            |
| Family                  | `obsfield`             |
| Specification reference | `obsfield/v1`          |
| Logical record schema   | `observation-field/v1` |

The canonical family identifier is `obsfield`. `ObsField` is the display name.

A release conforms to this specification only when it satisfies the generic
framework `SubstrateArtifact` contract and every required domain, vocabulary,
assignment, schema, and invariant defined here.

### Variant model

ObsField v1 defines one initial variant:

```text
categorical-complete
```

The variant guarantees that:

- observations are categorical;
- every canonical ambient-domain position has exactly one observation;
- observation IDs resolve through exactly one declared vocabulary;
- no missing-observation sentinel exists;
- the field is persistent within the committed record.

Assignment profiles such as `unique`, `categorical-random`, `balanced`, and
`landmark-background` are assignment protocols or presets, not variants.

A conforming release therefore uses:

```text
data/interim/obsfield/categorical-complete/v<N>/
```

The final `v<N>` is a framework release number, not the specification version.

## Conceptual model

### Ambient spatial domain

An ambient spatial domain is a finite canonical position space over which an
observation field is total.

A domain declaration defines:

- a domain-schema reference;
- a coordinate convention;
- shape parameters;
- the complete canonical position set;
- a canonical dense position enumeration;
- movement geometry sufficient for compatibility classification;
- boundary semantics.

A domain declaration does not define walls, blocked cells, corridors, or an
irregular traversability subset.

### Position identity

A position identifies one location in the complete ambient domain.

Position identity is semantic. Array position is authoritative only when the
applicable domain schema defines that array index as the canonical position
identifier.

Every supported domain schema must define both:

- a coordinate representation;
- a canonical dense `position_id` domain.

### Observation field

For one ambient domain `D` and observation vocabulary `V`, an observation
field is a total function:

```text
O : D -> V
```

The field is persistent. Repeated access to the same committed record returns
the same vocabulary entry at every position.

### Observation vocabulary

An observation vocabulary is an immutable categorical domain.

Every vocabulary has:

- a stable vocabulary identity;
- a declared cardinality;
- a canonical observation-ID domain;
- optional reusable metadata.

ObsField v1 supports:

- anonymous categorical vocabularies generated from a declared vocabulary
  specification;
- immutable references to externally defined vocabularies.

Two vocabularies with equal cardinality and equal integer ranges are not
identical unless their vocabulary identities are equal.

### Observation identifier

For vocabulary cardinality `K`, the canonical v1 observation-ID domain is:

```text
{0, 1, ..., K - 1}
```

Observation identifiers are categorical labels. Numeric order carries no
priority, distance, similarity, spatial, or generation meaning.

Observation IDs may repeat across positions unless the assignment protocol
requires uniqueness.

### Assignment protocol

An assignment protocol defines how vocabulary entries are assigned to ambient
positions.

It may constrain frequency, uniqueness, region structure, landmark placement,
or another reusable observation-field property. It must not define task
trajectories, task queries, or experienced-observation sequences.

### Independent composition

Topology and ObsField records are peer substrate inputs.

For compatible records:

```text
ObsField:
    O : D -> V

Topology:
    traversable positions V_T ⊆ D
    movement relation E_T ⊆ V_T × V_T

Task composition:
    observation field O restricted to V_T
    movement relation E_T
```

The pair `(topology record, ObsField record)` is part of task-corpus build
identity. It is not part of either substrate's identity.

## Unit of record

One record represents:

> one complete categorical observation realization over one canonical ambient
> spatial domain.

A record contains logically:

| Field                   | Meaning                                            |
| ----------------------- | -------------------------------------------------- |
| `record_id`             | Stable identifier of this realization              |
| `spatial_domain`        | Complete canonical ambient-domain declaration      |
| `vocabulary`            | Vocabulary identity and cardinality                |
| `assignment_protocol`   | Protocol reference                                 |
| `assignment_parameters` | Protocol-specific semantic parameters              |
| `realization_index`     | Stable deterministic discriminator                 |
| `observation_id`        | Observation assignment in canonical position order |

The record contains no topology reference, parent artifact fingerprint,
parent record identifier, or topology-state mapping.

### Record identifier

`record_id` is unique within one ObsField artifact and independent of physical
storage location.

Its deterministic inputs include:

- specification reference;
- variant;
- canonical ambient-domain identity;
- vocabulary identity;
- assignment-protocol identity;
- assignment parameters;
- base seed;
- realization index.

The framework remains authoritative for the exact identifier and digest
mechanisms.

## Ambient-domain contract

### Required domain properties

Every `spatial_domain` declaration must define:

| Property               | Requirement                                      |
| ---------------------- | ------------------------------------------------ |
| `schema`               | Supported canonical domain-schema reference      |
| `coordinate_system`    | Exact coordinate convention                      |
| `shape`                | Finite-shape classification                      |
| `shape_parameters`     | Complete parameters determining the position set |
| `position_count`       | Number of canonical positions                    |
| `position_enumeration` | Canonical dense enumeration contract             |
| `movement_geometry`    | Compatibility-relevant neighbor geometry         |
| `boundary_policy`      | Exact finite-domain boundary convention          |

The domain declaration must be sufficient to reconstruct the complete position
set and canonical position order without another artifact.

### Rectangular row-column domain

For the required v1 rectangular raster domain:

```text
schema: rectangular-row-column/v1
coordinate_system: row-column
shape: rectangle
height: H
width: W
movement_geometry: grid4
boundary_policy: closed
```

with:

```text
H >= 1
W >= 1
D = {(r, c) | 0 <= r < H and 0 <= c < W}
position_count = H * W
position_id(r, c) = r * W + c
```

Canonical enumeration is row-major by increasing `position_id`.

`grid4` identifies the ambient cardinal-neighbor geometry used for
compatibility classification. It does not assert that every such neighbor pair
is traversable in a composed topology.

### Square domain

A square domain is a rectangular row-column domain with `height = width`.
`shape = square` may be used as a constrained declaration only if it resolves
to the same canonical position identity and enumeration as
`rectangular-row-column/v1`.

### Hexagonal domain

Hexagonal domains are permitted by ObsField v1 only after a canonical hex
ambient-domain schema defines:

- coordinate system;
- finite shape;
- shape parameters;
- canonical position set;
- canonical position enumeration;
- `hex6` movement geometry;
- boundary semantics.

Until that shared schema exists, a release containing hex domains does not
conform to ObsField v1.

### Domain identity

Domain identity is derived from the complete canonical domain declaration, not
from position count alone.

Equal position counts do not imply equal domains.

The following differences imply different domain identities:

- coordinate-system difference;
- shape difference;
- dimension difference;
- position-enumeration difference;
- square/grid4 versus hex/hex6 difference;
- boundary-policy difference.

## Logical record schema

The canonical logical schema is `observation-field/v1`.

### Channel summary

| Channel          | Scope    | Requiredness | Domain                 | Shape semantics                          | Visibility | Meaning                                    |
| ---------------- | -------- | ------------ | ---------------------- | ---------------------------------------- | ---------- | ------------------------------------------ |
| `observation_id` | position | required     | integer categorical ID | `(P,)`, canonical ambient-position order | public     | Vocabulary entry assigned to each position |

`P` is the `position_count` declared by `spatial_domain`.

### `observation_id`

For every canonical `position_id` in `{0, ..., P - 1}`:

```text
observation_id[position_id]
```

is the categorical vocabulary entry assigned to that ambient position.

Requirements:

- dtype semantics are non-negative integer categorical labels;
- every value belongs to `{0, ..., K - 1}` for vocabulary cardinality `K`;
- the array length is exactly `P`;
- no missing-value or invalid-position sentinel exists;
- every ambient position has exactly one value;
- repeated values are valid unless prohibited by the assignment protocol.

Physical serialization may use an array or another equivalent representation,
but the canonical semantic order is the domain's `position_id` order.

### No topology-state indexing

ObsField v1 does not index observations by compact topology-state IDs.

A topology substrate may separately define:

```text
topology state ID <-> ambient position ID
```

The task builder uses that mapping when restricting an ObsField realization to
traversable topology states.

## Vocabulary contract

### Anonymous vocabulary

An anonymous vocabulary declaration must define:

- vocabulary schema;
- cardinality `K >= 1`;
- immutable vocabulary identity;
- canonical ID domain `{0, ..., K - 1}`.

Its entries have no semantics beyond identity and equality unless reusable
metadata is explicitly declared.

### External vocabulary

An external vocabulary reference must resolve an immutable vocabulary identity
and a canonical local encoding compatible with `observation_id`.

The framework or vocabulary specification owns reference integrity. ObsField
owns only the requirement that every assigned ID resolve within the declared
vocabulary.

### Vocabulary compatibility

Compatibility must never be inferred from cardinality or integer range alone.
Tasks and hidden-semantics builders must compare vocabulary identities or use an
explicit binding resource.

## Assignment protocols

ObsField v1 permits registered deterministic assignment protocols.

At least one protocol must be implemented and normatively specified for a
concrete release.

### `categorical-random/v1`

`categorical-random/v1` assigns one vocabulary entry independently to each
canonical ambient position according to a declared categorical distribution.

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

Protocols such as `unique`, `balanced`, or `landmark-background` may be added
without creating new variants when they preserve the same record and channel
semantics.

Each added protocol must define exact feasibility constraints, deterministic
behavior, and failure conditions.

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

Increasing the requested number of realizations for the same declared domain
and protocol must not alter records with earlier realization indexes.

Adding records for another domain must not alter existing records.

A shared sequential release-global RNG stream is insufficient unless its use
provably preserves these properties.

## Split semantics

ObsField v1 defines no intrinsic `train`, `validation`, or `test` membership.

Observation realizations form reusable pools. Task specifications determine
whether to:

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

When several ambient domains or vocabularies are generated in one artifact,
the configuration must define their deterministic enumeration explicitly.

### Operational configuration

Worker count, cache location, staging location, logging, and progress reporting
are operational. They must not alter scientific content.

## Family-specific identity inputs

ObsField contributes the following semantic inputs to framework build identity:

- specification reference;
- variant;
- logical record schema;
- complete canonical ambient-domain declarations;
- canonical domain-schema versions;
- vocabulary identities and cardinalities;
- assignment-protocol references;
- assignment parameters;
- canonical position-order policy;
- randomness derivation policy;
- base seed;
- realization counts and realization indexes.

ObsField contributes no parent topology identity, topology record ID, topology
fingerprint, or topology schema.

## Framework contract instantiation

In addition to the generic `SubstrateArtifact` contract, a conforming ObsField
release must declare:

| Framework property      | ObsField requirement                           |
| ----------------------- | ---------------------------------------------- |
| Specification reference | exactly `obsfield/v1`                          |
| Family                  | exactly `obsfield`                             |
| Variant                 | exactly `categorical-complete`                 |
| Logical record schema   | `observation-field/v1`                         |
| Required public channel | `observation_id`                               |
| Domain descriptors      | complete canonical ambient-domain declarations |
| Vocabulary descriptors  | immutable identity and cardinality             |
| Assignment descriptors  | protocol and semantic parameters               |
| Parent references       | none                                           |
| Intrinsic splits        | none                                           |

The framework remains authoritative for manifest serialization, resources,
digests, fingerprints, staging, publication, reuse, and conflicts.

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

## Scientific invariants

### Record-level invariants

#### OF-REC-001 — Self-contained ambient domain

Each record contains exactly one complete supported `spatial_domain`
declaration and no topology reference.

#### OF-REC-002 — Canonical position domain

The domain declaration reconstructs exactly `position_count` canonical
positions with unique dense IDs:

```text
{0, ..., position_count - 1}
```

#### OF-REC-003 — Position-order consistency

The `observation_id` field is ordered by canonical `position_id` and has length
exactly `position_count`.

#### OF-REC-004 — Complete coverage

Every ambient-domain position has exactly one observation assignment.

#### OF-REC-005 — Vocabulary bounds

For vocabulary cardinality `K`, every assigned value belongs to:

```text
{0, ..., K - 1}
```

#### OF-REC-006 — No missing-observation sentinel

No value denotes missing, invalid, wall, blocked, or unassigned position.

#### OF-REC-007 — Vocabulary identity

The record declares exactly one immutable vocabulary identity. Vocabulary
compatibility is not inferred from cardinality.

#### OF-REC-008 — Assignment-protocol conformance

The field satisfies every hard constraint of its declared assignment protocol.

#### OF-REC-009 — Record identity consistency

The declared record identity agrees with the canonical family-specific record
inputs and committed content under the framework identity contract.

#### OF-REC-010 — No topology dependency

The record contains no parent topology artifact coordinate, fingerprint,
record ID, record digest, compact-state mapping, or topology schema reference.

### Artifact-level invariants

#### OF-ART-001 — Specification consistency

Every record conforms to `obsfield/v1` and `observation-field/v1`.

#### OF-ART-002 — Variant consistency

Every record satisfies `categorical-complete` semantics.

#### OF-ART-003 — No intrinsic experimental splits

The artifact does not assign records to `train`, `validation`, or `test` as
ObsField-owned semantics.

#### OF-ART-004 — Deterministic record enumeration

Record enumeration and realization indexes are deterministic and unique.

#### OF-ART-005 — Descriptor consistency

Artifact-level declared domains, vocabularies, protocols, and counts agree with
record content.

#### OF-ART-006 — Parent-free substrate

The artifact declares no parent topology resources or parent topology lineage
as a semantic dependency.

## Validation contract

Full framework validation must invoke at least the following checks:

| Check                 | Invariants             | Coverage                  | Failure condition                                           |
| --------------------- | ---------------------- | ------------------------- | ----------------------------------------------------------- |
| Domain reconstruction | OF-REC-001, OF-REC-002 | every record              | Domain is incomplete, unsupported, or non-canonical         |
| Position ordering     | OF-REC-003             | every record              | Assignment length/order disagrees with domain               |
| Coverage              | OF-REC-004, OF-REC-006 | every record              | Any position is missing or represented by a sentinel        |
| Vocabulary validation | OF-REC-005, OF-REC-007 | every record              | Value out of bounds or vocabulary identity missing          |
| Protocol validation   | OF-REC-008             | every record              | Protocol-specific hard constraint fails                     |
| Identity validation   | OF-REC-009             | every record              | Declared identity disagrees with canonical inputs/content   |
| Dependency exclusion  | OF-REC-010, OF-ART-006 | every record and artifact | Topology-parent dependency is present                       |
| Artifact consistency  | OF-ART-001–OF-ART-005  | complete artifact         | Schema, variant, enumeration, split, or descriptor mismatch |

Diagnostics should identify:

- artifact coordinate;
- record ID;
- invariant identifier;
- domain identity;
- position ID where applicable;
- vocabulary identity;
- observed value;
- expected condition.

## Task-owned compatibility and composition

ObsField itself does not validate compatibility with a topology record because
no topology is part of the ObsField artifact.

A task builder selecting an ObsField record and a topology record must compare
their complete ambient-domain contracts.

Compatibility requires equality of all semantics necessary to identify the same
position space, including at least:

- domain-schema reference;
- coordinate system;
- shape and dimensions;
- canonical position identity;
- canonical position enumeration;
- movement geometry classification;
- boundary convention.

Equal state counts or equal array shapes are insufficient.

The task builder must reject:

- height or width mismatch;
- coordinate-system mismatch;
- square/grid4 versus hex/hex6 mismatch;
- position-enumeration mismatch;
- boundary-policy mismatch;
- any topology state that does not map to a valid ambient position.

For a compatible topology, observations assigned to blocked ambient positions
remain valid ObsField data but are unused by the composed task environment.

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

No task may infer vocabulary compatibility solely from matching integer ranges
or cardinalities.

## Compatibility and evolution

### New release under `obsfield/v1`

A new release may change:

- ambient-domain instances or parameters;
- vocabulary identities or sizes;
- assignment protocols or parameter values;
- seed;
- realization count;
- concrete assignments.

It remains `obsfield/v1` when:

- one record still means one complete categorical field over one self-contained
  ambient domain;
- position identity retains the same declared domain-schema semantics;
- every position has exactly one categorical observation;
- vocabulary identity semantics remain unchanged;
- no topology dependency is introduced;
- task composition remains external.

### New specification version

A new specification version is required for incompatible changes such as:

- binding ObsField records to topology records;
- changing record meaning;
- indexing by topology-state identity instead of ambient position identity;
- permitting missing observations;
- permitting multiple or continuous observations per position;
- changing vocabulary identity semantics;
- changing canonical position semantics incompatibly;
- introducing intrinsic task splits;
- changing the public observation-field contract incompatibly.

Unknown optional metadata may be ignored only when the framework and schema
explicitly permit it. Unknown required channels, unsupported domain schemas, or
unsupported specification versions require explicit incompatibility.

## Open issues

ObsField v1 remains `draft` until the following shared contracts are finalized:

1. the canonical ambient-domain schema registry and identity rules;
2. the exact canonical hex coordinate, finite-shape, and enumeration contract;
3. the topology-to-ambient-position mapping contract used by topology
   substrates;
4. the task-level compatibility-check contract for composing peer substrates;
5. the immutable vocabulary-reference and vocabulary-identity contract.

The topology-record reference issue is intentionally closed: ObsField v1 has no
substrate parent and no topology-record references.

## Related specifications

Framework contracts:

- [`Data artifacts`](../../framework/data-artifacts.md);
- [`Manifests`](../../framework/manifests.md);
- [`Identity`](../../framework/identity.md);
- [`Digests`](../../framework/digests.md);
- [`Provenance`](../../framework/provenance.md);
- [`References`](../../framework/references.md).

Research contracts:

- [`Substrates`](./_index.md);
- canonical ambient-domain specification — pending;
- canonical raster-topology schema — pending;
- vocabulary identity specification — pending;
- task-level substrate composition contract — pending.

Interface and development contracts:

- [`Data CLI`](../../interfaces/cli/data.md);
- [`Data layout`](../../development/data-layout.md).
