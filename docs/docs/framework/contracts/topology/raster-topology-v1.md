---
title: Raster topology v1
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Raster topology v1

## Normative summary

`raster-topology/v1` defines a producer-agnostic, consumer-agnostic logical record schema for a raster movement structure: which positions in an ambient spatial domain are traversable, and how movement between them is defined.

It is a framework-owned data contract, not a research-specific one and not itself a substrate family.
No builder produces `raster-topology/v1` directly.
Concrete substrate families each produce records that conform to it, declaring any compatibility properties their specification guarantees.
Concrete tasks declare any compatibility properties they require from a compatible record.
Neither side names the other.

```text
producers (any conforming substrate family)
    declare: "I produce raster-topology/v1 with compatibility properties {...}"
        ↕ compatibility via schema identity and framework compatibility rules
consumers (any conforming task)
    declare: "I require raster-topology/v1 with compatibility properties {...}"
```

This document defines the object represented, its authoritative and derived representations, the compatibility properties available to the framework compatibility mechanism, and the schema-level invariants every conforming record satisfies.
It does not define which producer or task uses it, and it does not define any producer's generation process or any task's scientific semantics.

## Scope and boundary

### Owned semantics

This specification defines:

- the raster-topology object: an ambient spatial domain, a passability structure over it, and a movement relation;
- the authoritative representation (passability) versus canonical derived views (compact states, movement tables, connectivity);
- `v1`'s fixed movement parameters (`movement_kind`, `directed`, `edge_cost_kind`, `stay_included`) and the derived compatibility properties this schema exposes (`connected`, `component_count`);
- the logical record schema (fields and their meaning) independent of physical serialization;
- schema-level invariants that hold for every conforming record, regardless of producer;
- the scientific meaning and value domain of the compatibility properties exposed by this schema; generic declaration and matching mechanics are defined elsewhere.

### Excluded semantics

This specification does not define:

- which producer or task uses this schema;
- a producer's generation process;
- a task's scientific semantics.

## Canonical identity and conformance

A conforming record declares these fixed identity values:

| Property              | Required value                                                                                |
| --------------------- | --------------------------------------------------------------------------------------------- |
| Logical record schema | `raster-topology/v1`                                                                          |
| Ambient-domain schema | `rectangular-row-column/v1`, per [Ambient spatial domain v1](../domains/ambient-domain-v1.md) |

The ambient-domain schema is reused here rather than redefined, so a topology record and a categorical-field record can be compared for ambient-domain compatibility against one shared schema.

A record conforms to `raster-topology/v1` when it satisfies every invariant in this document.
Conformance is asserted by a producing specification whose records satisfy every invariant in this document. This contract defines no artifact family of its own.

## Conceptual model

### The raster-topology object

One record represents one complete raster movement structure over one self-contained ambient spatial domain:

```text
RasterTopology

domain
    coordinate_system: row-column
    extent: height, width
    (per rectangular-row-column/v1, see "Canonical identity and conformance")

structure (authoritative)
    passable[position]  — one boolean per ambient position

state representation (canonical derived views)
    state_count
    state_to_position[state_id]
    position_to_state[position]

movement (fixed v1 schema parameters; transition relation is derived from them and passable)
    movement_kind: grid4
    directed: false
    edge_cost_kind: unit
    stay_included: false
    next_state / movement_valid   — derived transition relation over state_id

fixed schema parameters (same for every conforming v1 record)
    topology_kind: raster
    coordinate_system: row-column
    movement_kind, directed, edge_cost_kind, stay_included — as above

derived compatibility properties
    connected
    component_count
```

`movement_kind` and the other movement-related parameters belong to this topology contract, not to the ambient domain it reuses — see [Ambient spatial domain v1](../domains/ambient-domain-v1.md) § "Position identity is not movement".
This is what lets one ambient domain compose with more than one topology (for example, a `grid4` and a `grid8` topology over the same rectangular positions).

### Authoritative representation versus derived views

The normalized raster passability structure (`passable[position]` over the ambient domain) is the authoritative representation.
Record identity and equality are based on the ambient domain (`extent`) and `passable`: every conforming `v1` record shares the same fixed movement parameters (see "Fixed schema parameters"), so those parameters cannot distinguish two records and are not part of identity.
A future version that lets movement parameters vary per record or per producer would need to fold them back into this identity definition (for example, a `grid4` and a `grid8` topology over the same passable positions would then need to be distinguishable, which `v1` does not need to express since it defines only `grid4`).

Compact state identity (`state_id`), the `state_to_position` / `position_to_state` mappings, and the movement tables (`next_state`, `movement_valid`) are canonical derived views: mechanically reconstructible from the authoritative passability structure under `v1`'s fixed movement parameters, and carrying no identity information beyond them.
Derived views do not define a second, independent notion of record equality.

Compact states are enumerated in canonical row-major order over passable positions, consistent with `rectangular-row-column/v1`'s dense position enumeration.

## Logical record schema

### Logical fields

| Field               | Requiredness | Domain                                                     | Meaning                                                                         |
| ------------------- | ------------ | ---------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `record_id`         | required     | scalar identifier                                          | Identifier within the containing artifact (see [Contracts](../index.md))        |
| `extent`            | required     | `rectangular-row-column/v1` domain declaration             | Authoritative ambient-domain declaration (height, width, coordinate convention) |
| `passable`          | required     | boolean, one per ambient position, row-major order         | Authoritative passability structure                                             |
| `state_count`       | derived      | positive integer                                           | Number of passable positions                                                    |
| `state_to_position` | derived      | mapping, canonical row-major order over passable positions | Compact state identity to ambient position                                      |
| `position_to_state` | derived      | inverse mapping                                            | Ambient position to compact state identity, where passable                      |
| `next_state`        | derived      | mapping keyed by `(state_id, movement label)`              | Transition relation under `v1`'s fixed grid4/undirected/unit/no-stay rule       |
| `movement_valid`    | derived      | boolean, keyed by `(state_id, movement label)`             | Whether the corresponding transition exists                                     |

A producing specification may declare additional optional extensions. Such extensions are not part of `raster-topology/v1` itself, and a consumer may ignore them while still consuming the common topology.

### Movement relation

Under `v1`'s fixed `movement_kind: grid4`, movement labels are the four cardinal directions and the transition relation is derived from `passable` by connecting orthogonally adjacent passable positions.
`directed: false` means the relation is symmetric: if `(u, v)` is a valid transition, so is `(v, u)`.
`edge_cost_kind: unit` means every valid transition has cost one.

Other movement geometries, edge-cost models, topology self-transitions, or a genuinely directed relation require a future specification version or a separately named contract. A directed raster contract would require authoritative information beyond `passable` to determine per-edge direction; `raster-topology/v1` intentionally does not define such a representation.

## Properties and compatibility surface

### Fixed schema parameters

These values are the same for every record conforming to `raster-topology/v1`; they are schema constants, not producer-declared or per-record data, and do not need to be checked for compatibility since they cannot differ between conforming records:

| Parameter           | Fixed `v1` value | Meaning                                                                                                              |
| ------------------- | ---------------- | -------------------------------------------------------------------------------------------------------------------- |
| `topology_kind`     | `raster`         | The structural family of the movement space                                                                          |
| `coordinate_system` | `row-column`     | The ambient-domain coordinate convention (implied by the required `rectangular-row-column/v1` ambient-domain schema) |
| `movement_kind`     | `grid4`          | The admissible movement geometry                                                                                     |
| `directed`          | `false`          | The movement relation is symmetric                                                                                   |
| `edge_cost_kind`    | `unit`           | Every valid transition has cost one                                                                                  |
| `stay_included`     | `false`          | The topology-level movement relation contains no self-transition                                                     |

A future specification version may broaden any of these to vary per producer once a concrete need is demonstrated (see "Evolution"); `v1` defines only this single combination.

`stay_included: false` describes the _topology_.
A task may separately define its own task-level `STAY` action. Such an action is external to this topology contract and must not be inferred from `stay_included`.

### Derived compatibility properties

These properties are deterministically computable from each conforming record's authoritative `extent` and `passable` content. Their mathematical value domains are part of this contract:

| Property          | Meaning                                                        | Value domain   |
| ----------------- | -------------------------------------------------------------- | -------------- |
| `connected`       | Whether the passable structure is a single connected component | boolean        |
| `component_count` | Number of connected components in the passable structure       | integer `>= 1` |

For every conforming record, `component_count` is the number of connected components induced by `grid4` adjacency over passable positions, and `connected` is exactly equivalent to `component_count == 1`.

How a producer states that one of these properties is fixed artifact-wide, varies per record, or is not guaranteed is intentionally not represented by values such as `record-dependent` or `derived`. Producer guarantee scope, consumer requirement representation, and matching semantics are owned by [Contracts](../index.md) § "Compatibility mechanism".

## Invariants and validation

### Record invariants

These invariants hold for every record conforming to `raster-topology/v1`, independent of producer-specific generation semantics.

#### RT-REC-001 — Domain reconstruction

`extent` is a complete `rectangular-row-column/v1` domain declaration sufficient to reconstruct the full ambient position set and canonical enumeration without another artifact.

#### RT-REC-002 — Passability coverage

`passable` has exactly one boolean value for every ambient position declared by `extent`, in canonical row-major order, and at least one position is passable. Therefore every conforming topology has `state_count >= 1`.

#### RT-REC-003 — State enumeration consistency

`state_to_position` and `position_to_state` are mutual inverses over exactly the positions where `passable` is true, enumerated in canonical row-major order.

#### RT-REC-004 — Movement relation consistency

`next_state` and `movement_valid` are exactly the transition relation derivable from `passable` under `v1`'s fixed `movement_kind`, `directed`, and `edge_cost_kind` (see "Fixed schema parameters").
No transition exists between a passable and a non-passable position, or between two positions not orthogonally adjacent under `grid4`.

#### RT-REC-005 — Directedness conformance

The derived transition relation is symmetric, consistent with `v1`'s fixed `directed: false`.

#### RT-REC-006 — No implicit self-loops

The derived transition relation contains no self-transition, consistent with `v1`'s fixed `stay_included: false`.
Absence of a topology self-loop does not by itself forbid a task from defining its own task-level `STAY` action.

#### RT-REC-007 — Property/content agreement

`connected` and `component_count` agree exactly with the values computed from the record's authoritative `passable` structure under `grid4` adjacency.

### Validation requirements

A producer's validation must check these invariants over its committed records in addition to its own producer-specific invariants.
Diagnostics should identify the record ID, the violated invariant, and the observed versus expected value.

## Compatibility and composition boundary

### Compatibility requirements

A consumer of `raster-topology/v1` may rely on the following schema-fixed semantics:

- ambient domain: `rectangular-row-column/v1`;
- topology kind: raster;
- movement kind: `grid4`;
- directedness: `false`;
- edge-cost kind: `unit`;
- topology self-transition: absent.

A consumer may additionally constrain the derived compatibility properties `connected` and `component_count`. The framework compatibility specification owns how producer guarantees, per-record values, and consumer requirements are represented and matched.

A topology record's ambient domain may compose with another domain-bearing record only when their complete ambient-domain declarations are domain-identical under `ambient-domain/v1`.

This contract does not select producers, tasks, or peer artifacts and does not define task-level movement actions.

## Evolution

### Compatible changes

The following are compatible with `raster-topology/v1` when existing conforming records retain identical semantics:

- non-normative clarifications and examples;
- additional canonical derived views reconstructible from existing authoritative content;
- additional derived compatibility properties whose introduction does not alter existing schema semantics or invalidate existing records.

### Breaking changes

A new contract version is required for changes that alter:

- the meaning of authoritative `passable` content;
- the required `rectangular-row-column/v1` ambient domain;
- fixed `grid4`, undirected, unit-cost, no-self-transition movement semantics;
- canonical compact-state enumeration;
- the derivation or meaning of existing movement views;
- the scientific meaning or value domain of an existing compatibility property;
- any existing invariant's scientific meaning.

Support for `grid8`, weighted movement, topology self-transitions, or genuinely directed raster movement is therefore breaking for `raster-topology/v1` and requires a future version or separately named contract.

## Related specifications

- [`Contracts`](../index.md)
- [`Ambient spatial domain v1`](../domains/ambient-domain-v1.md) — shared `rectangular-row-column/v1` ambient-domain schema
- [`Resource requirements`](../../../interfaces/configuration/resource-requirements.md) — schema ID and compatibility-validator mechanism used to bind a requirement to a concrete producer
- [`Data artifacts`](../../data-artifacts.md)
