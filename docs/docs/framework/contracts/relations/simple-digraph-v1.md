---
title: Simple directed graph v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Simple directed graph v1

## Normative summary

`simple-digraph/v1` defines a producer-agnostic, consumer-agnostic logical record schema for a simple directed graph: a dense public node domain and a directed edge relation over it.

It is a framework-owned data contract, not a research-specific one and not itself a substrate family.
No builder produces `simple-digraph/v1` directly.
Concrete producers may produce records that conform to it and may expose compatibility properties derived from those records.
Concrete consumers may require compatibility properties defined by this contract.
Neither side names the other.

```text
producers (any conforming substrate family)
    declare: "I produce simple-digraph/v1 with compatibility properties {...}"
        ↕ compatibility via schema identity and framework compatibility rules
consumers (any conforming task)
    declare: "I require simple-digraph/v1 with compatibility properties {...}"
```

This schema defines a general simple directed graph.
Structural predicates beyond the simple-directed-graph baseline, such as acyclicity or terminal reachability, are derived compatibility properties rather than schema invariants.
A future weighted, multi-edge, or undirected graph contract would be a separate, differently named schema, not a variant of this one.

## Scope and boundary

### Owned semantics

This specification defines:

- the graph object: a dense public node domain and a simple directed edge relation;
- canonical edge ordering and labelled-graph equality;
- the derived compatibility properties exposed by the graph content;
- the logical record schema (fields and their meaning) independent of physical serialization;
- schema-level invariants that hold for every conforming record, regardless of producer.

### Excluded semantics

This specification does not define:

- which producer or task uses this schema;
- a producer's generation process;
- what an edge means beyond "progression is permitted" — physical movement, similarity, reward, causality, one task step, required traversal, and shortest-path membership are task-owned interpretations;
- producer-wide guarantee scope or consumer matching semantics for derived graph properties; those belong to the framework compatibility specification.

## Canonical identity and conformance

A conforming record declares this fixed identity value:

| Property              | Required value      |
| --------------------- | ------------------- |
| Logical record schema | `simple-digraph/v1` |

A record conforms to `simple-digraph/v1` when it satisfies every invariant in this document.
Conformance is asserted by a producing specification whose records satisfy every invariant in this document. This contract defines no artifact family of its own.

## Conceptual model

### Public node identifier

A record with `node_count = N` has the public node domain `{0, 1, ..., N - 1}`.
Public node identifiers are local to one graph record, unique within that record, dense non-negative integers, stable within the committed record, and categorical identities without numeric structural meaning.
For public IDs `u < v`, no topological, temporal, semantic, distance, priority, or generation-order relation is implied.

A public node identifier is not an observation identifier.
A consumer may compose this node domain with another categorical domain through an external binding; this schema does not define that binding.

### Directed edge

A directed edge `(u, v)` means the reusable graph structure permits progression from public node `u` to public node `v`.
Edges under this schema are directed, unweighted, unique, free of self-loops, and free of parallel-edge semantics.
An edge does not intrinsically mean physical movement, similarity, reward, causality, one task step, required traversal, or shortest-path membership — those are task-owned interpretations.

### Labelled-graph equality

Two records are content-identical when they have the same `node_count` and exactly the same directed edges over the same public node labels.
This is labelled-graph equality, not graph-isomorphism equality: structurally isomorphic graphs with different public labellings are distinct records unless their canonical labelled content is identical.

## Logical record schema

### Record fields

All fields below are public. `record_id` and `node_count` are record-scoped scalars; `edges` is the edge-relation channel, a variable-length sequence of pairs.

| Field        | Requiredness | Domain                           | Meaning                                                                  |
| ------------ | ------------ | -------------------------------- | ------------------------------------------------------------------------ |
| `record_id`  | required     | string identifier                | Identifier within the containing artifact (see [Contracts](../index.md)) |
| `node_count` | required     | integer `N >= 1`                 | Cardinality of the public node domain                                    |
| `edges`      | required     | ordered pairs of public node IDs | Canonical simple directed-edge relation                                  |

`edges` is a mathematical set; its canonical serialized ordering is lexicographic by `(source, target)`.
Insertion order and generator construction order are non-semantic.
No undeclared graph, node, or edge attributes are part of this schema.

The logical record schema is independent of JSONL, JSON, Parquet, or another physical encoding; a producer may store one canonical record per JSON Lines entry or another organization, but consumers resolve logical records through the framework resource surface rather than a fixed filename.

The following are not `simple-digraph/v1` channels: successor arrays, successor masks, node masks, padded adjacency tensors, transitive-closure matrices, reachability masks, topological layers, or construction ranks.
A downstream consumer may derive any such representation from `node_count` and `edges`.

## Properties and compatibility surface

### Derived compatibility properties

The following properties are deterministically computable from `node_count` and `edges`. Their mathematical value domains are part of this contract:

| Property                     | Meaning                                              | Value domain   |
| ---------------------------- | ---------------------------------------------------- | -------------- |
| `acyclic`                    | Whether the edge relation contains no directed cycle | boolean        |
| `terminal_count`             | Number of nodes with out-degree zero                 | integer `>= 0` |
| `all_nodes_reach_a_terminal` | Whether every node reaches at least one terminal     | boolean        |

`all_nodes_reach_a_terminal` is `false` when `terminal_count == 0`. When one or more terminals exist, it is `true` exactly when every node has a directed path to at least one terminal.

How a producer states that one of these properties is fixed artifact-wide, varies per record, or is not guaranteed is intentionally not represented in the property value domain. Producer guarantee scope, consumer requirement representation, and matching semantics are owned by [Contracts](../index.md) § "Compatibility mechanism".

## Invariants and validation

### Record invariants

These invariants hold for every record conforming to `simple-digraph/v1`, independent of producer-specific generation semantics.

#### SG-REC-001 — Node domain

`node_count` is an integer greater than or equal to one.
The public node domain is exactly `{0, ..., node_count - 1}`.

#### SG-REC-002 — Edge domain

Every edge source and target belongs to the record's public node domain.

#### SG-REC-003 — Simple directed relation

The edge relation contains no duplicate edge and no self-loop.
This schema has no parallel-edge semantics.

#### SG-REC-004 — Canonical edge ordering

The serialized logical edge sequence is ordered lexicographically by `(source, target)`.
This is an encoding invariant, not a mathematical graph property.

#### SG-REC-005 — Attribute restrictions

No undeclared graph, node, or edge attributes are present in the `simple-digraph/v1` scientific payload.

#### SG-REC-006 — Property/content agreement

`acyclic`, `terminal_count`, and `all_nodes_reach_a_terminal` agree exactly with the values computable from the record's `node_count` and `edges`.

### Validation requirements

A producer's validation must check these invariants over its committed records in addition to its own producer-specific invariants.
A validator may reconstruct a runtime graph object (for example, a NetworkX `DiGraph`) to check them, but is not required to use any particular library.
Diagnostics should identify the record ID, the violated invariant, and the observed versus expected value.

## Compatibility and composition boundary

### Compatibility requirements

A consumer of `simple-digraph/v1` may rely on the schema-fixed simple-directed-graph semantics defined here and may constrain the derived compatibility properties:

- `acyclic`;
- `terminal_count`;
- `all_nodes_reach_a_terminal`.

The framework compatibility specification owns how producer guarantees, per-record values, and consumer requirements are represented and matched.

This contract does not define graph-to-observation, graph-to-space, graph-to-reward, or other task-specific bindings. Such composition is external to the graph contract.

## Evolution

### Compatible changes

The following are compatible with `simple-digraph/v1` when existing conforming records retain identical semantics:

- non-normative clarifications and examples;
- additional canonical derived views reconstructible from `node_count` and `edges`;
- additional derived compatibility properties whose introduction does not alter existing graph semantics or invalidate existing records.

### Breaking changes

A new contract version is required for changes that alter:

- public node-identifier semantics;
- the meaning of the directed edge relation;
- support for self-loops or parallel edges;
- labelled-graph content equality;
- canonical edge ordering where it is part of the logical representation;
- the scientific meaning or value domain of an existing compatibility property;
- any existing invariant's scientific meaning.

Weighted edges, multi-edges, self-loops, or undirected semantics therefore require a future version or separately named contract.

## Related specifications

- [`Contracts`](../index.md)
- [`Raster topology v1`](../topology/raster-topology-v1.md)
- [`Resource requirements`](../../../interfaces/configuration/resource-requirements.md)
- [`Data artifacts`](../../data-artifacts.md)
