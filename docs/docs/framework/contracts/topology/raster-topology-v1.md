---
title: Raster topology v1
authority: normative
document_status: draft
---

# Raster topology v1

## Normative summary

`raster-topology/v1` defines a producer-agnostic, consumer-agnostic logical record schema for a raster movement structure: which positions in an ambient spatial domain are traversable, and how movement between them is defined.

It is a framework-owned data contract, not a research-specific one and not itself a substrate family.
No builder produces `raster-topology/v1` directly.
Concrete substrate families (`dungeongen/v1`, `maze-nd/v1`, and any future family, from EHP research or elsewhere) each produce records that conform to it, declaring their own guaranteed capabilities.
Concrete tasks each declare the capabilities they require from a compatible record.
Neither side names the other.

```text
producers (dungeongen, maze-nd, ...)
    declare: "I produce raster-topology/v1 with capabilities {...}"
        ↕ compatibility via schema ID + declared capabilities
consumers (arena, mazehard, routebind, prospect, ...)
    declare: "I require raster-topology/v1 with capabilities {...}"
```

This document defines the object represented, its authoritative and derived representations, the capability vocabulary producers and consumers use to negotiate compatibility, and the schema-level invariants every conforming record satisfies.
It does not define which producer or task uses it, and it does not define any producer's generation process or any task's scientific semantics.

## Scope and boundary

### Owned semantics

This specification defines:

- the raster-topology object: an ambient spatial domain, a passability structure over it, and a movement relation;
- the authoritative representation (passability) versus canonical derived views (compact states, movement tables, connectivity);
- the capability vocabulary a producer declares and a consumer requires, including movement-related capabilities such as `movement_kind`;
- the logical record schema (fields and their meaning) independent of physical serialization;
- schema-level invariants that hold for every conforming record, regardless of producer;
- the compatibility mechanism between a producer's declared capabilities and a consumer's required capabilities.

### Excluded semantics

This specification does not define:

- which family produces it (that is `dungeongen/v1`, `maze-nd/v1`, or a future producer's own specification);
- any producer's generation, extraction, conversion, or acceptance process;
- which tasks require it, or their scientific semantics;
- position identity or coordinate structure, which are owned by [`ambient-domain/v1`](../domains/ambient-domain-v1.md) and only reused here;
- observation assignment, starts, goals, routes, solutions, rewards, or task-level `STAY`, which are task-owned;
- model-facing tensor encodings;
- generic artifact manifests, digests, fingerprints, lifecycle, reuse, or publication.

A producer or consumer referencing this schema does not thereby depend on any other named producer or consumer.

## Canonical identity and conformance

| Property              | Required value                                                                                                                                                                                                                                            |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Logical record schema | `raster-topology/v1`                                                                                                                                                                                                                                      |
| Ambient-domain schema | `rectangular-row-column/v1`, per [Ambient spatial domain v1](../domains/ambient-domain-v1.md); reused here, not redefined, so a topology record and a categorical-field record can be compared for ambient-domain compatibility against one shared schema |

A record conforms to `raster-topology/v1` when it satisfies every invariant in this document.
Conformance is declared by the producing family's own specification (for example, `dungeongen/v1` § "Canonical identity and conformance"), not by this document, since this document has no artifacts of its own.

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

movement (authoritative parameters; transition relation is derived)
    movement_kind        — for example grid4
    directed              — bool
    edge_cost_kind        — for example unit
    next_state / movement_valid   — derived transition relation over state_id

capabilities (declared by a producer, checked against a consumer's requirement)
    topology_kind
    coordinate_system
    movement_kind
    directed
    edge_cost_kind
    stay_included
    connected
    component_count
```

`movement_kind` and the other movement-related parameters belong to this topology contract, not to the ambient domain it reuses — see [Ambient spatial domain v1](../domains/ambient-domain-v1.md) § "Position identity is not movement".
This is what lets one ambient domain compose with more than one topology (for example, a `grid4` and a `grid8` topology over the same rectangular positions).

### Authoritative representation versus derived views

The normalized raster passability structure (`passable[position]` over the ambient domain) is the authoritative representation.
It is the sole basis for record identity and equality.

Compact state identity (`state_id`), the `state_to_position` / `position_to_state` mappings, and the movement tables (`next_state`, `movement_valid`) are canonical derived views: mechanically reconstructible from the authoritative passability structure plus the declared `movement_kind`, `directed`, and `edge_cost_kind` parameters.
Two records with identical passability and identical movement parameters have identical derived views.
Derived views do not define a second, independent notion of record equality.

Compact states are enumerated in canonical row-major order over passable positions, consistent with `rectangular-row-column/v1`'s dense position enumeration.

### Capabilities are declared metadata, not identity of the producer

A capability is a machine-readable property a consumer can inspect without knowing which family produced the record.
Capabilities describe what the record _guarantees_, not who built it.

| Capability          | Meaning                                                                                               | Example values                                                 |
| ------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `topology_kind`     | The structural family of the movement space                                                           | `raster`                                                       |
| `coordinate_system` | The ambient-domain coordinate convention                                                              | `row-column`                                                   |
| `movement_kind`     | The admissible movement geometry                                                                      | `grid4`                                                        |
| `directed`          | Whether the movement relation is directed                                                             | `true`, `false`                                                |
| `edge_cost_kind`    | The movement-cost model                                                                               | `unit`                                                         |
| `stay_included`     | Whether a self-transition (staying at the same state) is part of the topology-level movement relation | `true`, `false`                                                |
| `connected`         | Whether the passable structure is a single connected component                                        | `true`, `false`, `record-dependent`                            |
| `component_count`   | The number of connected components in the passable structure                                          | a non-negative integer, or `derived` when it varies per record |

A producer's specification declares which capability values it guarantees for every record it commits (uniformly, or per-record when a value is record-dependent).
A consumer's specification declares which capability values it requires.
Compatibility holds when the producer's declared values satisfy the consumer's required values for every capability the consumer names; a consumer that does not name a capability places no requirement on it.

This is the same schema-ID-plus-capability mechanism already defined generically by [Resource requirements](../../../interfaces/configuration/resource-requirements.md): accepted schema IDs plus, where schema equality alone is insufficient, a package-owned compatibility validator.
Binding a task's `topology` requirement to one exact producer's artifact is a configuration-time concern; this document defines only the schema and capability vocabulary that make that binding checkable.
See also [Contracts](../index.md) for `ehp_sn`'s planned generic producer–consumer compatibility mechanism.

`stay_included` describes whether the _topology_ contributes a self-transition.
A task may separately define its own task-level `STAY` action (see, for example, `arena.md` § 6.2, `routebind.md` § 6.2), which is unrelated to this capability and must not be inferred from it.

## Logical record schema

### Channel summary

| Field               | Requiredness | Domain                                                     | Meaning                                                                         |
| ------------------- | ------------ | ---------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `record_id`         | required     | scalar identifier                                          | Framework-managed stable identity of the topology realization                   |
| `extent`            | required     | `rectangular-row-column/v1` domain declaration             | Authoritative ambient-domain declaration (height, width, coordinate convention) |
| `passable`          | required     | boolean, one per ambient position, row-major order         | Authoritative passability structure                                             |
| `state_count`       | derived      | non-negative integer                                       | Number of passable positions                                                    |
| `state_to_position` | derived      | mapping, canonical row-major order over passable positions | Compact state identity to ambient position                                      |
| `position_to_state` | derived      | inverse mapping                                            | Ambient position to compact state identity, where passable                      |
| `next_state`        | derived      | mapping keyed by `(state_id, movement label)`              | Transition relation under the declared `movement_kind`                          |
| `movement_valid`    | derived      | boolean, keyed by `(state_id, movement label)`             | Whether the corresponding transition exists                                     |

A producer's own specification may declare additional optional extensions (for example, DungeonGen's `region_id`); such extensions are not part of `raster-topology/v1` itself, and a consumer may ignore them while still consuming the common topology.

### Movement relation

For `movement_kind: grid4`, movement labels are the four cardinal directions and the transition relation is derived from `passable` by connecting orthogonally adjacent passable positions.
`directed: false` means the relation is symmetric: if `(u, v)` is a valid transition, so is `(v, u)`.
`edge_cost_kind: unit` means every valid transition has cost one.

Other `movement_kind` and `edge_cost_kind` values may be introduced by a future specification version once at least one producer and one consumer demonstrate a concrete need; this version defines only the `grid4` / `unit` combination that current producers and consumers use.

## Invariants and validation

These invariants hold for every record conforming to `raster-topology/v1`, independent of producer.
A producer's own specification owns producer-specific invariants (for example, DungeonGen's component-selection or Maze-ND's orientation-preservation rules) and must not duplicate these.

### RT-REC-001 — Domain reconstruction

`extent` is a complete `rectangular-row-column/v1` domain declaration sufficient to reconstruct the full ambient position set and canonical enumeration without another artifact.

### RT-REC-002 — Passability coverage

`passable` has exactly one boolean value for every ambient position declared by `extent`, in canonical row-major order.

### RT-REC-003 — State enumeration consistency

`state_to_position` and `position_to_state` are mutual inverses over exactly the positions where `passable` is true, enumerated in canonical row-major order.

### RT-REC-004 — Movement relation consistency

`next_state` and `movement_valid` are exactly the transition relation derivable from `passable`, `movement_kind`, `directed`, and `edge_cost_kind`.
No transition exists between a passable and a non-passable position, or between two positions not related by the declared `movement_kind`.

### RT-REC-005 — Directedness conformance

When a record declares `directed: false`, the derived transition relation is symmetric.

### RT-REC-006 — No implicit self-loops

Unless a record explicitly declares `stay_included: true`, the derived transition relation contains no self-transition.
Absence of a topology self-loop does not by itself forbid a task from defining its own task-level `STAY` action.

### RT-REC-007 — Capability/content agreement

Every declared capability value (`connected`, `component_count`, and the others in "Capabilities are declared metadata") agrees with what is actually computable from the record's authoritative `passable` structure.

### RT-ART-001 — Record identity uniqueness

Within one producing artifact, every `record_id` is unique.

### Validation requirements

A producer's validation must check these invariants over its committed records in addition to its own producer-specific invariants.
Diagnostics should identify the record ID, the violated invariant, and the observed versus expected value.

## Compatibility and evolution

### New release under a producing family

A producing family's own specification governs what constitutes a compatible new release under its own version (for example, `dungeongen/v1`).
This document is not renegotiated by a producer's release changes.

### New specification version of this schema

A new `raster-topology` specification version is required for incompatible changes to:

- the meaning of the authoritative representation (`passable`) or its relationship to derived views;
- the capability vocabulary (adding a capability is compatible; changing the meaning of an existing capability is not);
- the ambient-domain schema this document reuses;
- the invariants in "Invariants and validation".

Adding a new `movement_kind` or `edge_cost_kind` value that existing records and consumers are unaffected by is compatible with `v1` as long as the values this version already defines (`grid4`, `unit`) keep their meaning.

### Downstream use

A task requires `raster-topology/v1` and a set of required capability values; it must not require a specific producing family by name as part of its normative scope.
A task or experiment may still select a specific producing family as a deliberate scientific/experimental choice (for example, to compare DungeonGen- versus Maze-ND-sourced topologies); that selection is a configuration/experiment concern, not a task-semantic dependency.

## Related specifications

- [`Contracts`](../index.md)
- [`Ambient spatial domain v1`](../domains/ambient-domain-v1.md) — shared `rectangular-row-column/v1` ambient-domain schema
- [`Substrates`](../../../research/substrates/index.md)
- [`DungeonGen v1`](../../../research/substrates/dungeongen-v1.md)
- [`Maze-ND v1`](../../../research/substrates/maze-nd-v1.md)
- [`Resource requirements`](../../../interfaces/configuration/resource-requirements.md) — schema ID and compatibility-validator mechanism used to bind a requirement to a concrete producer
- [`Data artifacts`](../../data-artifacts.md)
