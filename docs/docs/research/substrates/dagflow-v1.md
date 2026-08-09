---
title: Dagflow v1
authority: normative
document_status: specified
---

# Dagflow v1

## Normative summary

`dagflow/v1` defines reusable procedurally generated directed-graph substrates
for downstream task-corpus construction.

One record represents one complete graph realization over dense public node
identifiers and a simple directed edge relation. Dagflow owns reusable graph
structure, record identity, and intrinsic graph split membership. It does not
own task queries, observation bindings, goals, paths, targets, episodes,
rewards, or model-facing graph encodings.

The initial `single-terminal` variant requires a finite, non-empty directed
acyclic graph with exactly one terminal node, where a terminal is a node with
out-degree zero. Every node must reach that terminal.

Dagflow uses NetworkX as the reference construction and validation dependency,
but committed artifacts contain stable EHP-SN graph records rather than
serialized NetworkX or Python objects.

## Scope and boundary

### Owned semantics

This specification defines:

- the public node-identifier domain;
- the simple directed-edge relation;
- the `single-terminal` graph class;
- the logical graph-record schema;
- graph-generation protocol requirements;
- canonical edge ordering and labelled-graph equality;
- intrinsic graph splits;
- family-specific semantic configuration;
- Dagflow scientific invariants and validation;
- the boundary between public graph structure and private generation state.

### Excluded semantics

This specification does not define:

- graph-node-to-observation bindings;
- spatial or environmental context;
- task starts, current states, or queries;
- task interpretation of the terminal as a goal;
- required or preferred paths;
- trajectory or waypoint targets;
- task-specific node or edge weights;
- rewards, episodes, or training examples;
- padded successor arrays, masks, reachability matrices, or other
  task-facing encodings;
- generic artifact manifests, digests, fingerprints, release conflict
  handling, staging, or publication;
- CLI option spelling or configuration precedence;
- repository-local physical placement beyond the framework coordinate model.

A downstream task may interpret or transform the graph relation, but that
interpretation does not become part of Dagflow.

## Canonical identity and conformance

| Property                | Required value      |
| ----------------------- | ------------------- |
| Artifact kind           | `substrate`         |
| Family                  | `dagflow`           |
| Specification reference | `dagflow/v1`        |
| Logical record schema   | `directed-graph/v1` |
| Initial variant         | `single-terminal`   |

The family identifier is exactly `dagflow`.

A conforming release satisfies the generic framework `SubstrateArtifact`
contract and every applicable requirement and invariant in this specification.
A concrete release uses the framework coordinate form:

```text
data/interim/dagflow/<variant>/v<release>/
```

The release number is independent of the `v1` specification version.

## Conceptual model

### Graph realization

A graph realization is one complete labelled directed graph committed as one
Dagflow record.

A realization consists logically of:

- a public node domain;
- a directed edge relation;
- a stable record identifier;
- exactly one intrinsic split membership.

A realization is not one node, edge, path, query, episode, or task case. One
Dagflow graph may be reused to derive multiple cases in one or more processed
task corpora.

### Public node identifier

A record with `node_count = N` has the public node domain:

```text
{0, 1, ..., N - 1}
```

Public node identifiers are:

- local to one graph record;
- unique within that record;
- dense non-negative integers;
- stable within the committed record;
- categorical identities without numeric structural meaning.

For public IDs `u < v`, no topological, temporal, semantic, distance, priority,
or generation-order relation is implied.

A public node identifier is not an observation identifier. A task may create a
binding between those domains, but Dagflow does not.

### Directed edge

A directed edge `(u, v)` means that the reusable graph structure permits
progression from public node `u` to public node `v`.

Dagflow v1 edges are:

- directed;
- unweighted;
- unique;
- free of self-loops;
- free of parallel-edge semantics;
- independent of task interpretation.

An edge does not intrinsically mean physical movement, similarity, reward,
causality, one task step, required traversal, or shortest-path membership.

### Terminal

A terminal is a node with out-degree zero.

`single-terminal` graphs contain exactly one terminal. The term `goal` is not
used because goal semantics belong to downstream tasks.

The terminal reaches itself through the zero-length path.

### Reachability

Node `v` is reachable from node `u` when a directed path from `u` to `v`
exists. Every node in a `single-terminal` graph must reach the unique terminal.

### Construction identity

A generator may use private construction identities or a private topological
order to guarantee acyclicity. These are not public graph identities and carry
no normative scientific meaning.

Private construction state must not be exposed as an ordinary public channel.
It may be retained only as integrity-protected provenance or bounded diagnostic
evidence when required by another framework contract.

### Labelled-graph equality

Two Dagflow records are content-identical when they have:

- the same `node_count`; and
- exactly the same directed edges over the same public node labels.

This is labelled-graph equality, not graph-isomorphism equality. Structurally
isomorphic graphs with different public labellings are distinct Dagflow v1
records unless their canonical labelled content is identical.

## Unit of record and variant model

### Unit of record

One record represents one complete directed graph realization.

Records are independently addressable and independently reconstructable from
the logical record fields. Record ordering within a resource or enumeration
has no scientific meaning.

Each record has one framework-managed stable `record_id`. The identifier is
unique within the artifact and does not depend on physical file placement or
serialization order. It is not the framework artifact fingerprint.

A task dataset generator may derive any number of processed task cases from one
record.

### Variant model

Dagflow v1 defines the following consumer-visible structural variant:

| Variant           | Required graph class                                                         |
| ----------------- | ---------------------------------------------------------------------------- |
| `single-terminal` | Finite non-empty simple DAG with exactly one terminal, reached by every node |

The variant defines the admissible graph class. It does not define the complete
probability distribution over that class.

Generation distributions are identified by generator protocol references, for
example:

```text
constructive-forward/v1
layered-terminal/v1
```

Named configuration presets may choose protocol and parameter values, but a
preset is not automatically a variant.

A stable graph class with materially different consumer-visible guarantees,
such as `multi-terminal`, requires a separate variant or specification version
after its semantics are defined.

## Channels and logical record schema

### Channel summary

Dagflow uses a minimal record schema rather than tensor-oriented graph
channels.

| Field        | Scope         | Requiredness | Domain/dtype                     | Shape semantics                   | Visibility | Meaning                                  |
| ------------ | ------------- | ------------ | -------------------------------- | --------------------------------- | ---------- | ---------------------------------------- |
| `record_id`  | record        | required     | string identifier                | scalar                            | public     | Stable identity of the graph realization |
| `node_count` | record        | required     | integer `N >= 1`                 | scalar                            | public     | Cardinality of the public node domain    |
| `edges`      | edge relation | required     | ordered pairs of public node IDs | variable-length sequence of pairs | public     | Canonical simple directed-edge relation  |

Intrinsic split membership is resolved through the framework artifact
enumeration or split contract. It is not duplicated inside the scientific
payload unless the framework resource schema requires that representation.

### `record_id`

`record_id` identifies one graph realization within the committed artifact.

It must:

- be unique across the artifact;
- resolve to exactly one logical record;
- remain stable within the committed release;
- remain independent of physical serialization position.

The generic framework owns the identifier mechanics. Dagflow defines only that
one identifier refers to one complete graph realization.

### `node_count`

`node_count` is the number of public nodes in the record.

For `node_count = N`, the public node domain is exactly:

```text
range(N)
```

Dagflow v1 does not require explicit node entries because v1 defines no public
node attributes and the complete node domain is recoverable from
`node_count`.

### `edges`

`edges` is the complete directed edge relation.

Each edge is represented logically as:

```text
[source, target]
```

where both endpoints belong to the record's public node domain.

The mathematical relation is a set. Its canonical serialized ordering is
lexicographic by `(source, target)`. Insertion order and generator construction
order are non-semantic.

Dagflow v1 permits no undeclared graph, node, or edge attributes.

### Logical record schema

| Field        | Requiredness | Constraint                                                  |
| ------------ | ------------ | ----------------------------------------------------------- |
| `record_id`  | required     | Unique within the artifact                                  |
| `node_count` | required     | Integer greater than or equal to one                        |
| `edges`      | required     | Canonically ordered sequence of unique valid directed pairs |

The logical record schema is independent of JSONL, JSON, Parquet, binary graph
collections, or another physical encoding.

A practical physical encoding may store one canonical record per JSON Lines
entry, but consumers must resolve logical records through the framework
resource surface rather than depending on a fixed filename.

### Representation exclusions

The following are not Dagflow v1 scientific channels:

- successor arrays;
- successor masks;
- node masks;
- padded adjacency tensors;
- transitive-closure matrices;
- reachability masks;
- topological layers;
- construction ranks;
- NetworkX object serialization.

A task corpus builder may derive any such representation from `node_count` and
`edges`.

## Domain semantics

### `single-terminal` graph semantics

A conforming graph is:

1. finite;
2. non-empty;
3. directed;
4. simple;
5. free of self-loops;
6. acyclic;
7. equipped with exactly one terminal;
8. such that every node reaches that terminal.

For a finite DAG, a unique sink implies that every node reaches it. The unique
terminal and terminal-reachability requirements remain separately normative
because they communicate the intended reusable structure and support distinct
validation diagnostics.

Dagflow v1 does not require:

- a Hamiltonian path;
- a mandatory chain backbone;
- pairwise reachability between every pair of nodes;
- a total order exposed to consumers;
- a unique topological ordering;
- a source node of in-degree zero that reaches every other node.

Incomparable nodes are permitted.

### Intrinsic split semantics

Each record belongs to exactly one canonical split:

```text
train
validation
test
```

Intrinsic graph splits belong to Dagflow because graph-structure
generalization is part of the reusable experimental boundary.

Task corpus builders must preserve parent split membership unless the concrete
task specification defines another framework-permitted policy.

Exact canonical labelled graph content must be unique across the entire
artifact, including across splits.

Dagflow v1 permits graph-isomorphic records with different public labellings.
Isomorphism-based deduplication is not a v1 conformance requirement.

## Source or generation contract

Dagflow is procedurally generated.

### Protocol

A conforming generator protocol must produce `single-terminal` graphs by
construction or through a fully declared deterministic rejection procedure.
The initial recommended protocol family is constructive generation.

For each realization, a constructive protocol performs the following
conceptual stages:

1. Resolve the specification reference, variant, generator protocol, size
   policy, edge policy, split, realization index, and base seed.
2. Resolve `N`, the record's node count, from the declared size policy.
3. Create a private acyclic construction order over `N` construction nodes.
4. Designate the final construction node as the structural terminal.
5. For every non-terminal construction node, add at least one outgoing edge to
   a later construction node so that the completed graph reaches the terminal.
6. Consider every remaining admissible forward pair under the declared
   additional-edge policy and add selected distinct edges.
7. Apply a deterministic permutation from private construction identities to
   public node IDs.
8. Construct the public labelled graph and discard private construction
   identities from the public scientific record.
9. Canonicalize the public edge relation lexicographically.
10. Validate all record-level invariants against the materialized logical
    record.
11. Assign the framework-managed stable record identity and intrinsic split
    membership.
12. Materialize the record through framework logical resources.

A protocol may use NetworkX `DiGraph` and NetworkX algorithms as its reference
runtime implementation. It must not persist Python objects or pickle files as
the normative graph representation.

### Required and additional edges

Required construction edges establish the `single-terminal` reachability
contract. Their exact distribution is owned by the declared generator
protocol.

Additional edges are optional admissible edges that preserve acyclicity and
simple-graph semantics.

The initial v1 edge policy is probability-based:

```text
graph.additional_edge_probability
```

The probability applies only to admissible non-required edges. It does not
replace the required construction needed to satisfy terminal reachability.

Dagflow v1 does not define an exact target-edge-count configuration. A future
protocol may support exact edge counts while remaining compatible with
`dagflow/v1` if it preserves the same logical record schema and variant
semantics and records the protocol change as an identity-bearing input.

### Node-count policy

Dagflow v1 permits heterogeneous node counts within one artifact.

Every release must declare one explicit node-count policy. Supported policy
shapes are:

```text
fixed:
    graph.node_count

bounded distribution:
    graph.node_count.minimum
    graph.node_count.maximum
    graph.node_count.distribution
```

A fixed policy assigns the same `node_count` to every record. A bounded policy
may assign different counts according to its declared deterministic
distribution.

The concrete distribution vocabulary and sampling semantics are owned by the
declared generator protocol and resolved configuration. The artifact-level
descriptor must agree with every materialized record.

### Rejection and exhaustion

Constructive protocols should avoid rejection for core graph validity.

When a protocol uses rejection for additional constraints, its resolved
configuration or protocol contract must define:

- the rejection condition;
- deterministic retry identity;
- maximum attempts per realization;
- behavior when the attempt budget is exhausted;
- whether rejected attempts affect any other realization.

A failed realization must fail generation explicitly. It must not silently
substitute a graph from another realization identity.

### Randomness and determinism

For fixed semantic inputs, graph generation is reproducible.

Record content depends on:

- specification reference;
- variant;
- generator protocol reference;
- resolved semantic configuration;
- base seed;
- split;
- realization index.

Record content must not depend on:

- worker count;
- worker scheduling;
- parallel completion order;
- filesystem enumeration order;
- dictionary iteration accidents;
- logging configuration;
- progress reporting;
- cache or temporary paths.

Logical randomness roles include:

- node-count selection when the size policy is heterogeneous;
- required successor selection;
- additional-edge selection;
- public node-ID permutation.

The builder derives independent deterministic random state for each record and
role from the semantic realization identity. Separate user-configurable seeds
for every role are not required.

Increasing a split's requested record count must not alter records with lower
realization indexes under otherwise identical semantic inputs. Record content
must also remain stable across worker counts.

## Configuration and family-specific identity inputs

### Semantic configuration

| Key                                 | Type                           | Requiredness/default              | Meaning                                       | Family-specific build input |
| ----------------------------------- | ------------------------------ | --------------------------------- | --------------------------------------------- | --------------------------: |
| `substrate.variant`                 | enum                           | required: `single-terminal`       | Consumer-visible graph class                  |                         Yes |
| `generation.protocol`               | specification reference        | required                          | Graph sampling protocol                       |                         Yes |
| `generation.seed`                   | integer                        | required                          | Base deterministic seed                       |                         Yes |
| `graph.node_count`                  | integer `>= 1`                 | required for fixed policy         | Fixed node count                              |                         Yes |
| `graph.node_count.minimum`          | integer `>= 1`                 | required for bounded policy       | Minimum node count                            |                         Yes |
| `graph.node_count.maximum`          | integer `>= minimum`           | required for bounded policy       | Maximum node count                            |                         Yes |
| `graph.node_count.distribution`     | protocol-supported enum/schema | required for bounded policy       | Deterministic node-count distribution         |                         Yes |
| `graph.additional_edge_probability` | real in `[0, 1]`               | required for the initial protocol | Probability for admissible non-required edges |                         Yes |
| `splits.train.count`                | non-negative integer           | required                          | Number of training graph records              |                         Yes |
| `splits.validation.count`           | non-negative integer           | required                          | Number of validation graph records            |                         Yes |
| `splits.test.count`                 | non-negative integer           | required                          | Number of test graph records                  |                         Yes |

Exactly one node-count policy is valid:

- `graph.node_count`; or
- the complete bounded-policy triple.

The fixed and bounded policy fields are mutually exclusive.

The initial protocol does not accept an exact target-edge-count field.

### Operational configuration

Operational settings such as worker count, logging level, progress display,
cache location, and temporary directories are not Dagflow scientific inputs.
They must not change generated graph content.

### Family-specific identity inputs

In addition to generic framework inputs, Dagflow contributes:

- `dagflow/v1`;
- the declared variant;
- `directed-graph/v1`;
- generator protocol reference;
- node-count policy;
- additional-edge policy;
- any declared degree or rejection constraints;
- split counts;
- deterministic randomness policy;
- base seed;
- canonical edge-ordering policy.

The framework remains authoritative for build-input identity and artifact
fingerprint construction.

## Framework contract instantiation

| Framework property         | Dagflow requirement                                                                          |
| -------------------------- | -------------------------------------------------------------------------------------------- |
| Specification reference    | Exactly `dagflow/v1`                                                                         |
| Artifact kind              | `substrate`                                                                                  |
| Family                     | Exactly `dagflow`                                                                            |
| Allowed variant            | `single-terminal`                                                                            |
| Logical record schema      | `directed-graph/v1`                                                                          |
| Required scientific fields | `record_id`, `node_count`, `edges`                                                           |
| Required logical resources | Deterministically enumerable graph records and framework-required split/resource descriptors |
| Family descriptors         | Generator protocol, node-count policy, additional-edge policy, canonicalization policy       |

Dagflow does not redefine the generic manifest, resource-descriptor, digest,
identity, lifecycle, reuse, validation-mode, or publication contracts.

### Record enumeration

Subject to the authoritative framework enumeration contract, one enumeration
entry corresponds to one complete graph record.

Dagflow-specific enumeration information must resolve:

- `record_id`;
- intrinsic split;
- graph payload locator;
- `directed-graph/v1` schema reference.

It may include bounded non-authoritative summaries such as `node_count` and
edge count. Summary fields must agree with the authoritative graph payload.

The physical enumeration format is not fixed by this specification.

## Invariants and validation

### Record-level invariants

#### DF-REC-001 — Node domain

`node_count` is an integer greater than or equal to one. The public node domain
is exactly `{0, ..., node_count - 1}`.

#### DF-REC-002 — Edge domain

Every edge source and target belongs to the record's public node domain.

#### DF-REC-003 — Simple directed relation

The edge relation contains no duplicate edge and no self-loop. Dagflow v1 has
no parallel-edge semantics.

#### DF-REC-004 — Canonical edge ordering

The serialized logical edge sequence is ordered lexicographically by
`(source, target)`.

This is an encoding invariant rather than a mathematical graph property.

#### DF-REC-005 — Acyclicity

The public directed edge relation is acyclic.

#### DF-REC-006 — Unique terminal

Exactly one public node has out-degree zero.

#### DF-REC-007 — Terminal reachability

Every public node reaches the unique terminal through zero or more directed
edges.

#### DF-REC-008 — Attribute restrictions

No undeclared graph, node, or edge attributes are present in the
`directed-graph/v1` scientific payload.

#### DF-REC-009 — Record identity resolution

`record_id` resolves to exactly one logical graph record and is unique within
the artifact.

### Split-level invariants

#### DF-SPLIT-001 — Exclusive membership

Every graph record belongs to exactly one of `train`, `validation`, or `test`.

#### DF-SPLIT-002 — Record-ID uniqueness

No `record_id` is reused across the artifact.

#### DF-SPLIT-003 — Exact labelled-graph uniqueness

No two records in the artifact have identical canonical labelled graph content
as defined by `node_count` and the complete directed edge relation.

Graph-isomorphic records with different public labellings are permitted.

#### DF-SPLIT-004 — Configured record counts

Each split contains exactly the number of records declared by the resolved
semantic configuration.

### Artifact-level invariants

#### DF-ART-001 — Specification consistency

Every graph record conforms to `dagflow/v1` and `directed-graph/v1`.

#### DF-ART-002 — Variant consistency

Every record in a `single-terminal` release satisfies the complete
`single-terminal` graph contract.

#### DF-ART-003 — Descriptor consistency

The declared generator protocol, size policy, edge policy, split counts, and
other family descriptors agree with the materialized records.

#### DF-ART-004 — Node-count policy consistency

For a fixed node-count policy, every record has the declared `node_count`.

For a bounded policy, every record falls within the declared bounds and the
protocol-defined distribution metadata is present and valid.

#### DF-ART-005 — Schema consistency

All graph payloads use the same logical graph schema. Heterogeneous node counts
do not imply heterogeneous schemas.

### Validation requirements

Validation must operate on materialized interim graph records rather than only
on generator-runtime objects.

| Invariant/check               | Scope           | Required failure context                                | Required coverage |
| ----------------------------- | --------------- | ------------------------------------------------------- | ----------------- |
| `DF-REC-001`–`DF-REC-009`     | record          | coordinate, split, `record_id`, offending field or edge | every record      |
| `DF-SPLIT-001`–`DF-SPLIT-004` | artifact splits | coordinate, involved record IDs and splits              | complete artifact |
| `DF-ART-001`–`DF-ART-005`     | artifact        | coordinate, declared descriptor, observed mismatch      | complete artifact |

NetworkX may be used to reconstruct a `DiGraph` and perform DAG, degree,
terminal, reachability, path, and summary checks. A non-NetworkX validator is
also conforming when it verifies the same normative conditions.

Validation diagnostics must identify the violated invariant and enough public
record context to reproduce the failure. Private construction identities must
not be required to validate the committed graph relation.

## Compatibility and downstream-use boundary

### Compatibility and evolution

A new concrete release may remain under `dagflow/v1` while changing:

- base seed;
- generated graph records;
- split counts;
- fixed node count;
- bounded node-count policy values;
- additional-edge probability;
- graph density and depth distributions;
- generator protocol, when the new protocol preserves the v1 semantic
  contract and is recorded as an identity-bearing input.

A new specification version is required for incompatible changes to:

- the meaning or scope of one graph record;
- public node-identifier semantics;
- directed-edge meaning;
- the `directed-graph/v1` logical schema;
- support for parallel edges;
- public graph, node, or edge attributes with new normative semantics;
- terminal meaning;
- intrinsic split semantics;
- channel visibility;
- canonical labelled-content equality;
- core conformance invariants.

A different stable consumer-visible graph class may be introduced as another
variant only when its guarantees are fully specified and remain compatible
with the same family-level record and edge semantics.

Consumers must reject unsupported specification versions, unknown required
fields, or incompatible logical schemas. Optional future fields may be ignored
only when their optionality and compatibility are explicitly declared by the
applicable specification.

### Downstream-use boundary

Downstream task corpus builders may consume:

- `record_id`;
- public node domain derived from `node_count`;
- canonical directed edge relation;
- intrinsic split membership;
- framework-declared source and identity references.

A task builder may reconstruct a runtime graph, for example:

```python
graph = nx.DiGraph()
graph.add_nodes_from(range(record.node_count))
graph.add_edges_from(record.edges)
```

This conversion is lossless, but task implementations are not required to use
NetworkX.

Downstream tasks own:

- selection of Dagflow records;
- combination with spatial or other substrates;
- graph-node-to-observation bindings;
- starts, current states, and queries;
- interpretation of the structural terminal as a task goal;
- hidden-information policies;
- path, trajectory, or waypoint construction;
- targets, rewards, episodes, and evaluation cases;
- tensor, sparse, padded, or model-facing graph encodings.

For Prospect specifically, Dagflow supplies the semantic node domain, directed
edge relation, unique structural terminal, record identity, and parent split.
Prospect supplies observation bindings, spatial context, queries, task-level
goal interpretation, and targets.

## Related specifications

- [`Substrates`](./index.md)
- [`Data artifacts`](../../framework/data-artifacts.md)
- [`Manifests`](../../framework/manifests.md)
- [`Identity`](../../framework/identity.md)
- [`Digests`](../../framework/digests.md)
- [`Provenance`](../../framework/provenance.md)
- [`References`](../../framework/references.md)
- [`Data CLI`](../../interfaces/cli/data.md)
- [`Data layout`](../../development/data-layout.md)
