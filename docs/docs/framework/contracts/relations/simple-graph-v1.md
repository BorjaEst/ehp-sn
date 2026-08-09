---
title: Simple graph v1
authority: normative
document_status: draft
---

# Simple graph v1

## Normative summary

`simple-graph/v1` defines a producer-agnostic, consumer-agnostic logical record schema for a simple directed graph: a dense public node domain and a directed edge relation over it.

It is a framework-owned data contract, not a research-specific one and not itself a substrate family. No builder produces `simple-graph/v1` directly. Concrete substrate families (currently `dagflow/v1`, and any future family, from EHP research or elsewhere) each produce records that conform to it, declaring their own guaranteed capabilities. Concrete tasks each declare the capabilities they require from a compatible record. Neither side names the other.

```text
producers (dagflow, ...)
    declare: "I produce simple-graph/v1 with capabilities {...}"
        ↕ compatibility via schema ID + declared capabilities
consumers (routebind, prospect, ...)
    declare: "I require simple-graph/v1 with capabilities {...}"
```

This schema defines a general simple directed graph. Structural guarantees beyond that — for example Dagflow's `single-terminal` acyclic-with-one-sink guarantee — are producer-declared capabilities, not part of this schema. A future weighted, multi-edge, or undirected graph contract would be a separate, differently named schema, not a variant of this one.

## Scope and boundary

### Owned semantics

This specification defines:

- the graph object: a dense public node domain and a simple directed edge relation;
- canonical edge ordering and labelled-graph equality;
- the capability vocabulary a producer declares and a consumer requires;
- the logical record schema (fields and their meaning) independent of physical serialization;
- schema-level invariants that hold for every conforming record, regardless of producer.

### Excluded semantics

This specification does not define:

- which family produces it (that is `dagflow/v1` or a future producer's own specification);
- any producer's generation protocol;
- structural guarantees beyond "simple directed graph" (acyclicity, terminal count, reachability, and similar are producer-declared capabilities, not schema requirements);
- weighted edges, multi-edges, typed relations, or undirected graphs, which would require a different, separately specified contract;
- graph-node-to-observation bindings, spatial or environmental context, task starts, queries, paths, targets, rewards, episodes, or model-facing encodings, which are task-owned;
- intrinsic split membership, which is producer-owned (see, for example, `dagflow/v1` § "Intrinsic split semantics").

A producer or consumer referencing this schema does not thereby depend on any other named producer or consumer.

## Canonical identity and conformance

| Property              | Required value    |
| --------------------- | ----------------- |
| Logical record schema | `simple-graph/v1` |

A record conforms to `simple-graph/v1` when it satisfies every invariant in this document. Conformance is declared by the producing family's own specification (for example, `dagflow/v1` § "Canonical identity and conformance"), not by this document, since this document has no artifacts of its own.

## Conceptual model

### Public node identifier

A record with `node_count = N` has the public node domain `{0, 1, ..., N - 1}`. Public node identifiers are local to one graph record, unique within that record, dense non-negative integers, stable within the committed record, and categorical identities without numeric structural meaning. For public IDs `u < v`, no topological, temporal, semantic, distance, priority, or generation-order relation is implied.

A public node identifier is not an observation identifier. A task may create a binding between those domains; this schema does not.

### Directed edge

A directed edge `(u, v)` means the reusable graph structure permits progression from public node `u` to public node `v`. Edges under this schema are directed, unweighted, unique, free of self-loops, and free of parallel-edge semantics. An edge does not intrinsically mean physical movement, similarity, reward, causality, one task step, required traversal, or shortest-path membership — those are task-owned interpretations.

### Labelled-graph equality

Two records are content-identical when they have the same `node_count` and exactly the same directed edges over the same public node labels. This is labelled-graph equality, not graph-isomorphism equality: structurally isomorphic graphs with different public labellings are distinct records unless their canonical labelled content is identical.

## Capabilities

| Capability                 | Meaning                                                              | Example values                                |
| -------------------------- | -------------------------------------------------------------------- | --------------------------------------------- |
| `acyclic`                  | Whether the edge relation contains no directed cycle                 | `true`, `false`                               |
| `terminal_count`           | The number of nodes with out-degree zero, when fixed by the producer | a non-negative integer, or `record-dependent` |
| `all_nodes_reach_terminal` | Whether every node reaches every declared terminal                   | `true`, `false`, `not-applicable`             |

A producer's specification declares which capability values it guarantees for every record it commits. A consumer's specification declares which capability values it requires. Compatibility holds when the producer's declared values satisfy every capability the consumer names, following the same schema-ID-plus-capability mechanism as [Raster topology v1](../topology/raster-topology-v1.md) § "Capabilities are declared metadata, not identity of the producer" and [Resource requirements](../../../interfaces/configuration/resource-requirements.md). See also [Contracts](../index.md) for `ehp_sn`'s planned generic producer–consumer compatibility mechanism.

Dagflow's `single-terminal` variant declares `acyclic: true`, `terminal_count: 1`, `all_nodes_reach_terminal: true`; see `dagflow/v1` § "Domain semantics" for that variant's own definition. A future producer could declare `acyclic: false` or `terminal_count: record-dependent` and still conform to this schema.

## Logical record schema

### Channel summary

| Field        | Scope         | Requiredness | Domain/dtype                     | Shape semantics                   | Visibility | Meaning                                  |
| ------------ | ------------- | ------------ | -------------------------------- | --------------------------------- | ---------- | ---------------------------------------- |
| `record_id`  | record        | required     | string identifier                | scalar                            | public     | Stable identity of the graph realization |
| `node_count` | record        | required     | integer `N >= 1`                 | scalar                            | public     | Cardinality of the public node domain    |
| `edges`      | edge relation | required     | ordered pairs of public node IDs | variable-length sequence of pairs | public     | Canonical simple directed-edge relation  |

`edges` is a mathematical set; its canonical serialized ordering is lexicographic by `(source, target)`. Insertion order and generator construction order are non-semantic. No undeclared graph, node, or edge attributes are part of this schema.

The logical record schema is independent of JSONL, JSON, Parquet, or another physical encoding; a producer may store one canonical record per JSON Lines entry or another organization, but consumers resolve logical records through the framework resource surface rather than a fixed filename.

The following are not `simple-graph/v1` channels: successor arrays, successor masks, node masks, padded adjacency tensors, transitive-closure matrices, reachability masks, topological layers, or construction ranks. A task-corpus builder may derive any such representation from `node_count` and `edges`.

## Invariants and validation

These invariants hold for every record conforming to `simple-graph/v1`, independent of producer. A producer's own specification owns producer-specific invariants (for example, Dagflow's acyclicity and unique-terminal guarantees, which are its own declared capabilities, not generic schema requirements) and must not duplicate these.

### SG-REC-001 — Node domain

`node_count` is an integer greater than or equal to one. The public node domain is exactly `{0, ..., node_count - 1}`.

### SG-REC-002 — Edge domain

Every edge source and target belongs to the record's public node domain.

### SG-REC-003 — Simple directed relation

The edge relation contains no duplicate edge and no self-loop. This schema has no parallel-edge semantics.

### SG-REC-004 — Canonical edge ordering

The serialized logical edge sequence is ordered lexicographically by `(source, target)`. This is an encoding invariant, not a mathematical graph property.

### SG-REC-005 — Attribute restrictions

No undeclared graph, node, or edge attributes are present in the `simple-graph/v1` scientific payload.

### SG-REC-006 — Record identity resolution

`record_id` resolves to exactly one logical graph record and is unique within the artifact.

### SG-REC-007 — Capability/content agreement

Every declared capability value (`acyclic`, `terminal_count`, `all_nodes_reach_terminal`) agrees with what is actually computable from the record's `node_count` and `edges`.

### Validation requirements

A producer's validation must check these invariants over its committed records in addition to its own producer-specific invariants. A validator may reconstruct a runtime graph object (for example, a NetworkX `DiGraph`) to check them, but is not required to use any particular library. Diagnostics should identify the record ID, the violated invariant, and the observed versus expected value.

## Compatibility and evolution

### New release under a producing family

A producing family's own specification governs what constitutes a compatible new release under its own version (for example, `dagflow/v1`). This document is not renegotiated by a producer's release changes.

### New specification version of this schema

A new `simple-graph` specification version is required for incompatible changes to:

- the meaning of `node_count` or `edges`, or public node-identifier semantics;
- support for parallel edges or self-loops;
- the capability vocabulary;
- canonical labelled-content equality;
- the invariants in "Invariants and validation".

### Downstream use

A task requires `simple-graph/v1` and a set of required capability values; it must not require a specific producing family by name as part of its normative scope.

## Related specifications

- [`Contracts`](../index.md)
- [`Raster topology v1`](../topology/raster-topology-v1.md)
- [`Substrates`](../../../research/substrates/index.md)
- [`Dagflow v1`](../../../research/substrates/dagflow-v1.md)
- [`Resource requirements`](../../../interfaces/configuration/resource-requirements.md)
- [`Data artifacts`](../../data-artifacts.md)
