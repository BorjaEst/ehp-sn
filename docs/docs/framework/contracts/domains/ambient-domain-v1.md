---
title: Ambient spatial domain v1
authority: normative
document_status: draft
---

# Ambient spatial domain v1

## Normative summary

`ambient-domain/v1` defines a producer-agnostic, consumer-agnostic canonical position space: a finite set of positions, a coordinate convention, and a canonical dense enumeration over them. It is the shared identity substrate that both [`categorical-field/v1`](../observations/categorical-field-v1.md) and [`raster-topology/v1`](../topology/raster-topology-v1.md) declare their positions against, so that a topology record and a categorical-field record can be checked for compatibility without either naming the other's producer.

It is a framework-owned data contract, not a research-specific one and not itself a substrate family. No builder produces `ambient-domain/v1` directly; it is a domain declaration embedded by other contracts and their producers.

An ambient domain owns position identity and coordinate structure only. It does not own movement or admissible transitions — see "Position identity is not movement" below.

## Scope and boundary

### Owned semantics

This specification defines:

- what constitutes one ambient spatial domain;
- the required domain-declaration properties;
- the registered domain schemas (`rectangular-row-column/v1`, with `hex` pending);
- domain identity and equality.

### Excluded semantics

This specification does not define:

- traversability, walls, admissible movement, or any passability structure over the domain (that is `raster-topology/v1`, or another future topology contract);
- observation assignment over the domain (that is `categorical-field/v1`);
- which family produces a domain declaration, or which task consumes one.

## Conceptual model

### Ambient spatial domain

An ambient spatial domain is a finite canonical position space. A domain declaration defines:

- a domain-schema reference;
- a coordinate convention;
- shape parameters;
- the complete canonical position set;
- a canonical dense position enumeration;
- a coordinate-structure descriptor sufficient to classify domains as compatible or incompatible for reuse;
- boundary semantics.

A domain declaration does not itself define walls, blocked cells, corridors, an irregular traversability subset, admissible movement, or any observation assignment — those belong to the contracts that reuse this domain declaration.

### Position identity is not movement

A domain answers "what positions exist, and how are they identified?" It does not answer "which transitions between positions are admissible?" — that is a topology contract's question.

Keeping these separate lets one ambient domain compose with more than one topology. For example, the same rectangular position space could underlie a `grid4` topology, a `grid8` topology, or a directed topology with custom adjacency, without becoming three different domains. A field defined over the domain (for example, a `categorical-field/v1` record) then composes with whichever topology a task selects, rather than being tied to one movement model.

### Position identity

A position identifies one location in the complete ambient domain.

Position identity is semantic. Array position is authoritative only when the applicable domain schema defines that array index as the canonical position identifier.

Every supported domain schema must define both:

- a coordinate representation;
- a canonical dense `position_id` domain.

## Required domain properties

Every domain declaration must define:

| Property               | Requirement                                                                                                                 |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| `schema`               | Supported canonical domain-schema reference                                                                                 |
| `coordinate_system`    | Exact coordinate convention                                                                                                 |
| `shape`                | Finite-shape classification                                                                                                 |
| `shape_parameters`     | Complete parameters determining the position set                                                                            |
| `position_count`       | Number of canonical positions                                                                                               |
| `position_enumeration` | Canonical dense enumeration contract                                                                                        |
| `coordinate_structure` | Geometric coordinate structure (for example `rectangular-lattice`, `hexagonal-lattice`), independent of admissible movement |
| `boundary_policy`      | Exact finite-domain boundary convention                                                                                     |

The domain declaration must be sufficient to reconstruct the complete position set and canonical position order without another artifact.

`coordinate_structure` describes how coordinates are laid out geometrically — enough to interpret them — not which neighbor transitions a topology may later declare admissible. A topology contract (for example `raster-topology/v1`) declares its own movement-related capabilities (such as `movement_kind: grid4`) separately; this schema does not require or assert one.

## Registered domain schemas

### Rectangular row-column domain

For the required v1 rectangular raster domain:

```text
schema: rectangular-row-column/v1
coordinate_system: row-column
shape: rectangle
height: H
width: W
coordinate_structure: rectangular-lattice
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

### Square domain

A square domain is a rectangular row-column domain with `height = width`. `shape = square` may be used as a constrained declaration only if it resolves to the same canonical position identity and enumeration as `rectangular-row-column/v1`.

### Hexagonal domain

Hexagonal domains are permitted only after a canonical hex ambient-domain schema defines:

- coordinate system;
- finite shape;
- shape parameters;
- canonical position set;
- canonical position enumeration;
- `coordinate_structure: hexagonal-lattice`;
- boundary semantics.

Until that shared schema exists, a release containing hex domains does not conform to `ambient-domain/v1`.

## Domain identity

Domain identity is derived from the complete canonical domain declaration, not from position count alone.

Equal position counts do not imply equal domains.

The following differences imply different domain identities:

- coordinate-system difference;
- shape difference;
- dimension difference;
- position-enumeration difference;
- rectangular-lattice versus hexagonal-lattice (or another registered `coordinate_structure`) difference;
- boundary-policy difference.

A difference in a topology's declared `movement_kind` does not by itself imply a different domain identity: two topologies with different movement models may share the same domain.

## Invariants and validation

### AD-REC-001 — Domain reconstruction

A domain declaration reconstructs exactly `position_count` canonical positions with unique dense IDs `{0, ..., position_count - 1}`, without another artifact.

### AD-REC-002 — Schema conformance

Every domain declaration conforms to a registered domain schema in "Registered domain schemas". An unregistered schema does not conform to `ambient-domain/v1`.

## Compatibility and evolution

A new registered domain schema (for example, a future hex schema) is a compatible addition to `ambient-domain/v1` as long as existing schemas' identity and enumeration semantics are unchanged. A new specification version is required for incompatible changes to an existing registered schema's position identity, enumeration, or required properties.

## Related specifications

- [`Contracts`](../index.md)
- [`Categorical field v1`](../observations/categorical-field-v1.md)
- [`Raster topology v1`](../topology/raster-topology-v1.md)
