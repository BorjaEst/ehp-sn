---
title: Ambient spatial domain v1
authority: normative
document_status: draft
---

# Ambient spatial domain v1

## Normative summary

`ambient-domain/v1` defines a producer-agnostic, consumer-agnostic canonical position space: a finite set of positions, a coordinate convention, and a canonical dense enumeration over them.
It is the shared identity substrate that both [`categorical-field/v1`](../observations/categorical-field-v1.md) and [`raster-topology/v1`](../topology/raster-topology-v1.md) declare their positions against, so that a topology record and a categorical-field record can be checked for compatibility without either naming the other's producer.

It is a framework-owned data contract, not a research-specific one and not itself a substrate family.
No builder produces `ambient-domain/v1` directly; it is a domain declaration embedded by other contracts and their producers.

An ambient domain owns position identity and coordinate structure only.
It does not own movement or admissible transitions — see "Position identity is not movement" below.

## Scope and boundary

### Owned semantics

This specification defines:

- what constitutes one ambient spatial domain;
- the required domain-declaration properties;
- the registered domain schemas (`rectangular-row-column/v1`, with `hex` pending);
- domain identity and equality.

### Excluded semantics

This specification does not define:

- movement, admissible transitions, or any other topology structure over the domain — see "Position identity is not movement";
- walls, blocked cells, corridors, an irregular traversability subset, or admissible movement — owned by a contract that reuses this domain declaration (for example `raster-topology/v1`);
- any observation assignment over the domain — owned by a contract that reuses this domain declaration (for example `categorical-field/v1`).

## Canonical identity and conformance

| Property                  | Required value                                  |
| ------------------------- | ----------------------------------------------- |
| Domain-declaration schema | `ambient-domain/v1`                             |
| Registered domain schemas | `rectangular-row-column/v1` (hexagonal pending) |

The domain-declaration schema is embedded by the contract that reuses it, not a standalone artifact schema — see "Registered domain schemas" below for the hexagonal-domain status.

A domain declaration conforms to `ambient-domain/v1` when it satisfies every invariant in "Invariants and validation", in particular AD-REC-001–AD-REC-003.
Conformance is asserted by the embedding logical record or its owning specification. `ambient-domain/v1` defines no standalone artifact of its own.

## Conceptual model

### Ambient spatial domain

An ambient spatial domain is a finite canonical position space.
A domain declaration defines:

- a domain-schema reference;
- a coordinate convention;
- shape parameters;
- the complete canonical position set;
- a canonical dense position enumeration;
- a coordinate-structure descriptor sufficient to classify domains as compatible or incompatible for reuse.

A domain declaration does not itself define walls, blocked cells, corridors, an irregular traversability subset, admissible movement, or any observation assignment — those belong to the contracts that reuse this domain declaration.

### Position identity is not movement

A domain answers "what positions exist, and how are they identified?" It does not answer "which transitions between positions are admissible?" — that is a topology contract's question.

Keeping these separate lets one ambient domain compose with more than one topology.
For example, the same rectangular position space could underlie a `grid4` topology, a `grid8` topology, or a directed topology with custom adjacency, without becoming three different domains.
A field defined over the domain (for example, a `categorical-field/v1` record) then composes with whichever topology a task selects, rather than being tied to one movement model.

### Position identity

A position identifies one location in the complete ambient domain.

Position identity is semantic.
Array position is authoritative only when the applicable domain schema defines that array index as the canonical position identifier.

Every supported domain schema must define both:

- a coordinate representation;
- a canonical dense `position_id` domain.

### Domain identity

Domain identity is derived from the complete canonical domain declaration, not from position count alone.

Equal position counts do not imply equal domains.

The following differences imply different domain identities:

- coordinate-system difference;
- shape difference;
- dimension difference;
- position-enumeration difference;
- rectangular-lattice versus hexagonal-lattice (or another registered `coordinate_structure`) difference.

A difference in a topology's declared `movement_kind` does not by itself imply a different domain identity: two topologies with different movement models may share the same domain.

## Logical record schema

A domain declaration is a logical structure independent of physical serialization, sufficient to reconstruct the complete position set and canonical position order without another artifact.
It is embedded inline within the contract that reuses it (for example as a `raster-topology/v1` record's `extent` field, or a `categorical-field/v1` record's `domain` field), not serialized as a standalone artifact of its own.

### Domain declaration fields

Every registered domain schema must define semantics for the following properties. The concrete declaration fields used to instantiate those semantics may be schema-specific; for example, `rectangular-row-column/v1` uses `height` and `width` directly rather than a generic nested `shape_parameters` field.

| Property               | Requirement                                                                             |
| ---------------------- | --------------------------------------------------------------------------------------- |
| `schema`               | Supported canonical domain-schema reference                                             |
| `coordinate_system`    | Exact coordinate convention                                                             |
| `shape`                | Finite-shape classification                                                             |
| `shape_parameters`     | Complete schema-specific parameters determining the position set                        |
| `position_count`       | Number of canonical positions                                                           |
| `position_enumeration` | Canonical dense enumeration contract                                                    |
| `coordinate_structure` | Geometric coordinate structure (for example `rectangular-lattice`, `hexagonal-lattice`) |

A concrete domain declaration must contain the fields required by its registered schema and must be sufficient to reconstruct the complete position set and canonical position order without another artifact.

For `rectangular-row-column/v1`, membership in the domain is fully determined by `height` and `width`; no separate boundary field is needed. A domain schema with different membership semantics (for example, coordinate wrapping) is a separately named schema, not a variant setting of an existing one.

`coordinate_structure` describes how coordinates are laid out geometrically — enough to interpret them — not which neighbor transitions a topology may later declare admissible. A topology contract (for example `raster-topology/v1`) owns movement semantics separately; this schema does not require or assert one.

The declaration separates authoritative schema inputs from schema-determined and derived assertions:

```text
authoritative schema inputs
    schema
    schema-specific shape parameters

schema-determined assertions
    coordinate_system
    coordinate_structure
    shape
    position_enumeration

derived assertion
    position_count
```

`coordinate_system`, `coordinate_structure`, `shape`, and `position_enumeration` are therefore not independently chosen semantics. When materialized in a declaration they must exactly match the values mandated by `schema`; `position_count` must exactly match the value derived from the schema parameters.

### Registered domain schemas

#### Rectangular row-column domain

For the required v1 rectangular raster domain:

```text
schema: rectangular-row-column/v1
coordinate_system: row-column
shape: rectangle
height: H
width: W
coordinate_structure: rectangular-lattice
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

#### Square domain

Squareness is a derived property (`height == width`) of a `rectangular-row-column/v1` declaration, not a separate authored `shape` value.
A square position space is declared as `shape: rectangle` with `height = width`; `shape: square` does not exist as a registered value and does not conform to `ambient-domain/v1`.

#### Hexagonal domain

Hexagonal domains are permitted only after a canonical hex ambient-domain schema defines:

- coordinate system;
- finite shape;
- shape parameters;
- canonical position set;
- canonical position enumeration;
- `coordinate_structure: hexagonal-lattice`.

Until that shared schema exists, a release containing hex domains does not conform to `ambient-domain/v1`.

## Properties and compatibility surface

`schema`, `coordinate_system`, and `coordinate_structure` are schema-fixed properties: determined entirely by the declared `schema` (see AD-REC-003), not independently authored or negotiated between a producer and a consumer.

`ambient-domain/v1` defines no derived compatibility-property vocabulary.
A contract that reuses an ambient domain (for example `raster-topology/v1`, `categorical-field/v1`) may define its own compatibility properties over its own structure, but that vocabulary is not part of this contract — see [Contracts](../index.md) § "Compatibility mechanism".

## Invariants and validation

### Record invariants

#### AD-REC-001 — Domain reconstruction

A domain declaration reconstructs exactly `position_count` canonical positions with unique dense IDs `{0, ..., position_count - 1}`, without another artifact.

#### AD-REC-002 — Schema conformance

Every domain declaration conforms to a registered domain schema in "Registered domain schemas".
An unregistered schema does not conform to `ambient-domain/v1`.

#### AD-REC-003 — Schema-determined field consistency

Every schema-determined assertion materialized in the declaration (`coordinate_system`, `coordinate_structure`, `shape`, and `position_enumeration`) equals exactly the value the declared `schema` mandates, and `position_count` equals the value derived from the schema-specific shape parameters.
A declaration containing a contradictory schema-determined or derived assertion does not conform to `ambient-domain/v1`.

### Validation requirements

A contract that embeds an ambient-domain declaration validates these invariants as part of its own record validation.
Diagnostics should identify the embedding record, the violated invariant, and the observed versus expected value.

## Compatibility and composition boundary

### Compatibility requirements

A contract reusing `ambient-domain/v1` may rely on the declaration's canonical domain identity, reconstruction semantics, and schema-conformance invariants.

Two embedded domain declarations are domain-identical only when their complete canonical declarations are identical under the registered domain schema. Equal position counts, equal array lengths, or equal geometric cardinality are insufficient.

A reusing contract must not infer movement, traversability, observation, or task semantics from ambient-domain compatibility.

## Evolution

### Compatible changes

The following are compatible with `ambient-domain/v1` when they do not alter the semantics of an existing registered domain schema:

- adding a newly registered domain schema with its own canonical coordinate, position, and enumeration semantics;
- adding non-normative examples or clarifications;
- adding derived descriptive material that does not change canonical domain identity.

### Breaking changes

A new contract version is required for changes that alter an existing registered schema's:

- canonical position set;
- position identity;
- coordinate interpretation;
- canonical enumeration;
- schema-determined assertions;
- required declaration semantics;
- domain-equality rules.

## Related specifications

- [`Contracts`](../index.md)
- [`Categorical observation field v1`](../observations/categorical-field-v1.md)
- [`Raster topology v1`](../topology/raster-topology-v1.md)
