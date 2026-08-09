---
title: Categorical field v1
authority: normative
document_status: draft
---

# Categorical field v1

## Normative summary

`categorical-field/v1` defines a producer-agnostic, consumer-agnostic logical record schema for a persistent categorical observation assignment over an ambient spatial domain: one categorical observation for every canonical position in the domain.

It is a framework-owned data contract, not a research-specific one and not itself a substrate family. No builder produces `categorical-field/v1` directly. Concrete substrate families (currently `obsfield/v1`, and any future family, from EHP research or elsewhere) each produce records that conform to it, declaring their own guaranteed capabilities. Concrete tasks each declare the capabilities they require from a compatible record. Neither side names the other.

```text
producers (obsfield, ...)
    declare: "I produce categorical-field/v1 with capabilities {...}"
        ↕ compatibility via schema ID + declared capabilities
consumers (arena, routebind, prospect, ...)
    declare: "I require categorical-field/v1 with capabilities {...}"
```

This schema is deliberately named for what it actually guarantees — a total, categorical, persistent field — not as a universal claim about "the" observation contract. A continuous, multimodal, stochastic, or partially observed field would be a different, separately named contract.

Categorical-field records are independent of topology substrates: this schema does not reference `raster-topology/v1` or any topology record. Topology and categorical-field records are peer inputs selected and composed by a task builder.

## Scope and boundary

### Owned semantics

This specification defines:

- the categorical-field object: an ambient spatial domain (reusing [`ambient-domain/v1`](../domains/ambient-domain-v1.md)) plus a total categorical observation assignment over it;
- observation vocabulary identity and the anonymous/external vocabulary contract;
- the capability vocabulary a producer declares and a consumer requires;
- the logical record schema (fields and their meaning) independent of physical serialization;
- schema-level invariants that hold for every conforming record, regardless of producer.

### Excluded semantics

This specification does not define:

- which family produces it (that is `obsfield/v1` or a future producer's own specification);
- any producer's assignment protocol or generation process;
- traversability, walls, or movement (that is `raster-topology/v1`);
- which tasks require it, or their scientific semantics;
- starts, goals, trajectories, queries, targets, rewards, or task splits, which are task-owned;
- model-facing tensor encodings;
- non-categorical, non-total, or non-persistent observation structures, which would require a different, separately specified contract.

A producer or consumer referencing this schema does not thereby depend on any other named producer or consumer.

## Canonical identity and conformance

| Property              | Required value                                                                     |
| ---------------------- | -------------------------------------------------------------------------------------- |
| Logical record schema | `categorical-field/v1`                                                              |
| Ambient-domain schema | `rectangular-row-column/v1`, per [Ambient spatial domain v1](../domains/ambient-domain-v1.md) |

A record conforms to `categorical-field/v1` when it satisfies every invariant in this document. Conformance is declared by the producing family's own specification (for example, `obsfield/v1` § "Canonical identity and conformance"), not by this document, since this document has no artifacts of its own.

## Conceptual model

### Observation field

For an ambient domain `D` (per `ambient-domain/v1`) and observation vocabulary `V`, an observation field is a total function:

```text
O : D -> V
```

The field is persistent: repeated access to the same committed record returns the same vocabulary entry at every position.

A compatible topology may separately define a traversable subset `V_T ⊆ D`; a task builder then uses the restricted field `O|V_T`. That restriction is task-owned composition, not part of this schema.

### Observation vocabulary

An observation vocabulary is an immutable categorical domain with:

- a stable vocabulary identity;
- a declared cardinality;
- a canonical observation-ID domain;
- optional reusable metadata.

For vocabulary cardinality `K`, the canonical observation-ID domain is `{0, 1, ..., K - 1}`. Observation identifiers are categorical labels: numeric order carries no priority, distance, similarity, spatial, or generation meaning.

Two vocabularies with equal cardinality and equal integer ranges are not identical unless their vocabulary identities are equal. Compatibility must never be inferred from cardinality or integer range alone.

### Vocabulary contract

An **anonymous vocabulary** declares a vocabulary schema, cardinality `K >= 1`, an immutable vocabulary identity, and the canonical ID domain `{0, ..., K - 1}`. Its entries have no semantics beyond identity and equality unless reusable metadata is explicitly declared.

An **external vocabulary** reference resolves an immutable vocabulary identity and a canonical local encoding compatible with `observation_id`. The framework or vocabulary specification owns reference integrity; this schema owns only the requirement that every assigned ID resolve within the declared vocabulary.

### Independent composition

Topology and categorical-field records are peer substrate inputs. For compatible records:

```text
categorical-field record:
    O : D -> V

topology record (raster-topology/v1):
    traversable positions V_T ⊆ D
    movement relation E_T ⊆ V_T × V_T

task composition:
    observation field O restricted to V_T
    movement relation E_T
```

The pair `(topology record, categorical-field record)` is part of task-corpus build identity. It is not part of either contract's identity.

## Capabilities

| Capability   | Meaning                                                                    | Example values     |
| ------------- | -------------------------------------------------------------------------- | -------------------- |
| `coverage`   | Whether every ambient position has an assigned observation                | `total`, `partial` |
| `value_kind` | The kind of value assigned per position                                    | `categorical`       |
| `persistent` | Whether the field is stable across repeated access to the committed record | `true`, `false`     |

A producer's specification declares which capability values it guarantees for every record it commits. A consumer's specification declares which capability values it requires. Compatibility holds when the producer's declared values satisfy every capability the consumer names, following the same schema-ID-plus-capability mechanism as [Raster topology v1](../topology/raster-topology-v1.md) § "Capabilities are declared metadata, not identity of the producer" and [Resource requirements](../../../interfaces/configuration/resource-requirements.md). See also [Contracts](../index.md) for `ehp_sn`'s planned generic producer–consumer compatibility mechanism.

## Logical record schema

### Channel summary

| Channel          | Scope    | Requiredness | Domain                 | Shape semantics                          | Visibility | Meaning                                    |
| ----------------- | -------- | ------------ | ----------------------- | ------------------------------------------- | ---------- | -------------------------------------------- |
| `observation_id` | position | required     | integer categorical ID | `(P,)`, canonical ambient-position order | public     | Vocabulary entry assigned to each position |

`P` is the `position_count` declared by the record's ambient-domain declaration.

For every canonical `position_id` in `{0, ..., P - 1}`, `observation_id[position_id]` is the categorical vocabulary entry assigned to that ambient position. Requirements:

- dtype semantics are non-negative integer categorical labels;
- every value belongs to `{0, ..., K - 1}` for vocabulary cardinality `K`;
- the array length is exactly `P`;
- no missing-value or invalid-position sentinel exists when `coverage: total` is declared;
- every ambient position has exactly one value;
- repeated values are valid unless a producer's own assignment protocol prohibits them.

Physical serialization may use an array or another equivalent representation, but the canonical semantic order is the domain's `position_id` order.

This schema does not index observations by compact topology-state IDs. A topology substrate may separately define a `topology state ID <-> ambient position ID` mapping; a task builder uses that mapping when restricting a categorical-field realization to traversable topology states.

## Invariants and validation

These invariants hold for every record conforming to `categorical-field/v1`, independent of producer. A producer's own specification owns producer-specific invariants (for example, an assignment protocol's own hard constraints) and must not duplicate these.

### CF-REC-001 — Self-contained ambient domain

Each record contains exactly one complete ambient-domain declaration (per `ambient-domain/v1`) and no topology reference.

### CF-REC-002 — Position-order consistency

`observation_id` is ordered by canonical `position_id` and has length exactly `position_count`.

### CF-REC-003 — Coverage conformance

When `coverage: total` is declared, every ambient-domain position has exactly one observation assignment and no value denotes missing, invalid, or unassigned position.

### CF-REC-004 — Vocabulary bounds

For vocabulary cardinality `K`, every assigned value belongs to `{0, ..., K - 1}`.

### CF-REC-005 — Vocabulary identity

The record declares exactly one immutable vocabulary identity. Vocabulary compatibility is not inferred from cardinality alone.

### CF-REC-006 — No topology dependency

The record contains no parent topology artifact coordinate, fingerprint, record ID, record digest, compact-state mapping, or topology schema reference.

### CF-ART-001 — Deterministic record enumeration

Record enumeration is deterministic and unique within the producing artifact.

### Validation requirements

A producer's validation must check these invariants over its committed records in addition to its own producer-specific invariants. Diagnostics should identify the artifact coordinate, record ID, invariant identifier, domain identity, position ID where applicable, vocabulary identity, observed value, and expected condition.

## Task-owned compatibility and composition

This schema does not validate compatibility with a topology record because no topology is part of a categorical-field artifact. A task builder selecting a categorical-field record and a topology record must compare their complete ambient-domain declarations per `ambient-domain/v1` — equal state counts or equal array shapes are insufficient. Observations assigned to positions a composed topology later marks non-traversable remain valid categorical-field content; they are simply unused in that composition.

## Compatibility and evolution

### New release under a producing family

A producing family's own specification governs what constitutes a compatible new release under its own version (for example, `obsfield/v1`). This document is not renegotiated by a producer's release changes.

### New specification version of this schema

A new `categorical-field` specification version is required for incompatible changes to:

- the meaning of the observation-field function `O : D -> V` or its persistence guarantee;
- the capability vocabulary;
- the ambient-domain schema this document reuses;
- binding categorical-field records to topology records (which would violate independence);
- indexing by topology-state identity instead of ambient-position identity;
- the invariants in "Invariants and validation".

### Downstream use

A task requires `categorical-field/v1` and a set of required capability values; it must not require a specific producing family by name as part of its normative scope. A task or experiment may still select a specific producing family as a deliberate scientific/experimental choice; that selection is a configuration/experiment concern, not a task-semantic dependency.

## Related specifications

- [`Contracts`](../index.md)
- [`Ambient spatial domain v1`](../domains/ambient-domain-v1.md)
- [`Raster topology v1`](../topology/raster-topology-v1.md)
- [`Substrates`](../../../research/substrates/index.md)
- [`ObsField v1`](../../../research/substrates/obsfield-v1.md)
- [`Resource requirements`](../../../interfaces/configuration/resource-requirements.md)
- [`Data artifacts`](../../data-artifacts.md)
