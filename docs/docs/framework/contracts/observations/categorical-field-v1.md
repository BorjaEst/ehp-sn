---
title: Categorical observation field v1
authority: normative
document_status: draft
---

# Categorical observation field v1

## Normative summary

`categorical-field/v1` defines a producer-agnostic, consumer-agnostic logical record schema for a persistent categorical observation assignment over an ambient spatial domain: one categorical observation for every canonical position in the domain.

It is a framework-owned data contract, not a research-specific one and not itself a substrate family.
No builder produces `categorical-field/v1` directly.
Concrete substrate families (from EHP research or elsewhere) each produce records that conform to it, declaring any compatibility properties their specification guarantees.
Concrete tasks declare any compatibility properties they require from a compatible record.
Neither side names the other.

```text
producers (any conforming substrate family)
    declare: "I produce categorical-field/v1"
        ↕ compatibility via schema identity and framework compatibility rules
consumers (any conforming task)
    declare: "I require categorical-field/v1"
```

This schema is deliberately named for what it actually guarantees — a total, categorical, persistent field — not as a universal claim about "the" observation contract.
A continuous, multimodal, stochastic, or partially observed field would be a different, separately named contract.

Categorical-field records are independent of topology substrates: this schema does not reference `raster-topology/v1` or any topology record.
Topology and categorical-field records are peer inputs selected and composed by a task builder.

## Scope and boundary

### Owned semantics

This specification defines:

- the categorical-field object: an ambient spatial domain (reusing [`ambient-domain/v1`](../domains/ambient-domain-v1.md)) plus a total categorical observation assignment over it;
- observation vocabulary identity and the anonymous/external vocabulary contract;
- the logical record schema (fields and their meaning) independent of physical serialization;
- schema-level invariants that hold for every conforming record, regardless of producer.

### Excluded semantics

This specification does not define:

- any topology record or reference to `raster-topology/v1` — a categorical-field record is self-contained and independent of any topology substrate;
- which producer or task uses this schema;
- a producer's generation process or observation-assignment protocol;
- a task's scientific semantics.

## Canonical identity and conformance

| Property              | Required value                                                                        |
| --------------------- | ------------------------------------------------------------------------------------- |
| Logical record schema | `categorical-field/v1`                                                                |
| Ambient-domain schema | any schema registered in [Ambient spatial domain v1](../domains/ambient-domain-v1.md) |

A record conforms to `categorical-field/v1` when it satisfies every invariant in this document.
Conformance is asserted by a producing specification whose records satisfy every invariant in this document. This contract defines no artifact family of its own.

## Conceptual model

### Observation field

For an ambient domain `D` (per `ambient-domain/v1`) and observation vocabulary `V`, an observation field is a total function:

```text
O : D -> V
```

The field is persistent: repeated access to the same committed record returns the same vocabulary entry at every position.

A compatible topology may separately define a traversable subset `V_T ⊆ D`; a task builder then uses the restricted field `O|V_T`.
That restriction is task-owned composition, not part of this schema.

### Observation vocabulary

An observation vocabulary is an immutable categorical domain with:

- a stable vocabulary identity;
- a declared cardinality;
- a canonical observation-ID domain;
- optional reusable metadata.

For vocabulary cardinality `K`, the canonical observation-ID domain is `{0, 1, ..., K - 1}`.
Observation identifiers are categorical labels: numeric order carries no priority, distance, similarity, spatial, or generation meaning.

Two vocabularies with equal cardinality and equal integer ranges are not identical unless their vocabulary identities are equal.
Compatibility must never be inferred from cardinality or integer range alone.

### Vocabulary contract

A vocabulary declaration has exactly one of two logical forms:

```text
anonymous vocabulary
    kind: anonymous
    identity: <immutable vocabulary identity>
    cardinality: K

external vocabulary
    kind: external
    ref: <immutable external vocabulary reference>
    identity: <resolved immutable vocabulary identity>
    cardinality: K
```

For both forms, `K >= 1` and the canonical local observation-ID domain is `{0, ..., K - 1}`.

An **anonymous vocabulary** has no semantics beyond identity and equality unless reusable metadata is explicitly declared.

An **external vocabulary** delegates the referenced vocabulary's integrity and resolution semantics to the framework reference mechanism or the referenced vocabulary specification. This contract requires only that the resolved identity and cardinality are immutable for the committed record and that every assigned `observation_id` resolves within the declared local ID domain.

### Content equality

Two categorical-field records are content-identical when they have:

- identical ambient-domain declarations;
- identical vocabulary identities and canonical local vocabulary domains;
- identical `observation_id` values in canonical ambient-position order.

The provisional `record_id` does not define scientific content equality.

## Logical record schema

### Record fields

Whole-record-scoped declarations, distinct from the position-indexed channel below:

| Field        | Requiredness | Domain                                                                  | Meaning                                                                   |
| ------------ | ------------ | ----------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `record_id`  | required     | scalar identifier                                                       | Identifier within the containing artifact (see [Contracts](../index.md))  |
| `domain`     | required     | complete `ambient-domain/v1` declaration                                | The ambient spatial domain this field is defined over (per CF-REC-001)    |
| `vocabulary` | required     | anonymous or external vocabulary declaration, per "Vocabulary contract" | The immutable categorical domain from which this field's values are drawn |

### Channels

The following channel is position-scoped and public.

| Channel          | Requiredness | Domain                 | Meaning                                                                                    |
| ---------------- | ------------ | ---------------------- | ------------------------------------------------------------------------------------------ |
| `observation_id` | required     | integer categorical ID | Vocabulary entry assigned to each position; shape `(P,)`, canonical ambient-position order |

`P` is the `position_count` declared by the record's `domain` field.

For every canonical `position_id` in `{0, ..., P - 1}`, `observation_id[position_id]` is the categorical vocabulary entry assigned to that ambient position.
Requirements:

- dtype semantics are non-negative integer categorical labels;
- every value belongs to `{0, ..., K - 1}` for vocabulary cardinality `K`;
- the array length is exactly `P`;
- no missing-value or invalid-position sentinel exists;
- every ambient position has exactly one value;
- repeated values are valid unless a producer's own assignment protocol prohibits them.

Physical serialization may use an array or another equivalent representation, but the canonical semantic order is the domain's `position_id` order.

This schema does not index observations by compact topology-state IDs.
A topology substrate may separately define a `topology state ID <-> ambient position ID` mapping; a task builder uses that mapping when restricting a categorical-field realization to traversable topology states.

## Properties and compatibility surface

`value_kind: categorical`, `coverage: total`, and `persistent: true` are fixed by this schema's own definition (see "Normative summary"), not negotiated producer/consumer variation — a record guaranteeing anything else does not conform to `categorical-field/v1` and belongs to a different, separately specified contract.
This schema currently defines no derived compatibility properties or negotiated compatibility dimensions beyond that fixed baseline.

If a future version exposes a genuine compatibility property (for example, a vocabulary-level property distinct from schema-fixed semantics), this contract will define only that property's scientific meaning and value domain. Producer guarantee scope, consumer requirement representation, and matching semantics remain owned by [Contracts](../index.md) § "Compatibility mechanism".

## Invariants and validation

### Record invariants

These invariants hold for every record conforming to `categorical-field/v1`, independent of producer-specific generation semantics.

#### CF-REC-001 — Self-contained ambient domain

Each record contains exactly one complete ambient-domain declaration (per `ambient-domain/v1`) and no topology reference.

#### CF-REC-002 — Position-order consistency

`observation_id` is ordered by canonical `position_id` and has length exactly `position_count`.

#### CF-REC-003 — Coverage conformance

Every ambient-domain position has exactly one observation assignment; no value denotes missing, invalid, or unassigned position.

#### CF-REC-004 — Vocabulary bounds

For vocabulary cardinality `K`, every assigned value belongs to `{0, ..., K - 1}`.

#### CF-REC-005 — Vocabulary identity

The record declares exactly one immutable vocabulary identity.
Vocabulary compatibility is not inferred from cardinality alone.

#### CF-REC-006 — No topology dependency

The record contains no parent topology artifact coordinate, fingerprint, record ID, record digest, compact-state mapping, or topology schema reference.

### Validation requirements

A producer's validation must check these invariants over its committed records in addition to its own producer-specific invariants.
Diagnostics should identify the artifact coordinate, record ID, invariant identifier, domain identity, position ID where applicable, vocabulary identity, observed value, and expected condition.

## Compatibility and composition boundary

### Compatibility requirements

A consumer of `categorical-field/v1` may rely on the schema-fixed guarantees that the field is categorical, total over its ambient domain, and persistent.

When a categorical field is composed with another domain-bearing record, their ambient-domain declarations must be domain-identical under `ambient-domain/v1`. Equal position counts or equal array shapes are insufficient.

This contract defines no producer-guarantee scope or consumer matching algorithm beyond those scientific semantics; those mechanics remain owned by the framework compatibility specification.

### Composition rules

A categorical-field record is independent of topology. If a peer topology defines a traversable subset `V_T` of the same ambient domain `D`, composition uses the restricted field `O|V_T` together with the topology's movement relation.

Positions outside `V_T` remain valid categorical-field content; they are simply unused by that composition.

The choice of peer records and any resulting task-corpus build identity are external to this contract. This contract does not own starts, goals, trajectories, queries, targets, rewards, task splits, or model-facing encodings.

## Evolution

### Compatible changes

The following are compatible with `categorical-field/v1` when existing conforming records retain their meaning:

- non-normative clarifications and examples;
- additional optional vocabulary metadata whose absence remains valid;
- additional derived compatibility properties that do not change schema-fixed categorical, total, or persistent semantics.

### Breaking changes

A new contract version is required for changes that alter:

- the meaning of the total persistent function `O : D -> V`;
- canonical observation-ID semantics;
- vocabulary identity semantics;
- ambient-domain composition requirements;
- canonical position indexing of `observation_id`;
- the requirement that the field be total or persistent;
- any existing invariant's scientific meaning.

## Related specifications

- [`Contracts`](../index.md)
- [`Ambient spatial domain v1`](../domains/ambient-domain-v1.md)
- [`Raster topology v1`](../topology/raster-topology-v1.md)
- [`Resource requirements`](../../../interfaces/configuration/resource-requirements.md)
- [`Data artifacts`](../../data-artifacts.md)
