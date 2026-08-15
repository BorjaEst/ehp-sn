---
title: MazeHard v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# MazeHard v1

## Normative summary

`maze-hard/v1` defines a fully observed static shortest-route prediction task over finite raster maze topologies.

One corpus record represents one task-generated start–goal problem over one raster-topology realization.

MazeHard consumes one compatible raster-topology record, generates a reachable start and goal, computes canonical shortest-route truth, and materializes a self-contained task case containing the visible maze problem and route supervision.

MazeHard owns start/goal generation, shortest-route oracle semantics, ambiguity treatment, public problem representation, target semantics, and task-level metrics.
It does not own Maze-ND source extraction, topology generation, generic artifact mechanics, model architecture, or model-native tokenization.

A conforming MazeHard corpus also satisfies the generic `DataArtifact` and `TaskCorpus` contracts.

## 1. Purpose and scientific claim

### 1.1 Computational objective

Given an explicitly presented raster maze together with a start position and goal position, predict a path-labelled output grid representing one stored optimal route from start to goal.

The canonical reference Maze-Hard profile described by the research manuscript uses a `30 × 30` grid flattened to `900` positions for the HRM interface.
The task semantics remain the same under another explicitly named compatible corpus profile, but such a profile must not be confused with direct reproduction of the reference 30 × 30 benchmark.

### 1.2 Scientific question

MazeHard tests whether a model can perform global spatial reasoning over a fully observed static problem whose correct route may depend on long-range connectivity rather than local visual structure.

### 1.3 Intended comparisons

MazeHard supports comparisons across:

- topology difficulty;
- start–goal distance;
- maze size;
- model deliberation mechanisms;
- exact-route versus structural-route evaluation.

### 1.4 Non-claims

MazeHard does not test:

- online navigation under partial observation;
- acquisition or recall of an environment from sequential experience;
- semantic waypoint composition;
- memory-conditioned planning.

## 2. Scope and ownership

### 2.1 Task-owned semantics

MazeHard defines:

- one start–goal problem as the logical record;
- admissible topology capabilities;
- task generation of start and goal;
- reachable-query requirements;
- shortest-route oracle semantics;
- canonical ambiguity policy;
- public topology/start/goal information;
- route targets;
- task-specific metrics and invariants.

### 2.2 Excluded semantics

MazeHard does not define:

- Maze-ND source-row starts, goals, or source solutions as topology semantics;
- topology extraction or normalization;
- model-native token IDs, flattening, batch shapes, logits, or loss weights;
- optimizer or training policy;
- CLI commands or implementation helper names.

A faithful reproduction of source Maze-Hard problem rows is a separate corpus-import protocol and must not be represented as Maze-ND topology semantics.

### 2.3 Authoritative dependencies

| Concern                            | Authoritative specification                     |
| ---------------------------------- | ----------------------------------------------- |
| Generic generated-data contract    | `data-artifacts`                                |
| Generic task-corpus contract       | `corpora`                                       |
| Raster maze topology               | `raster-topology/v1`                            |
| Maze-ND source topology production | `maze-nd/v1` when used                          |
| Task semantics                     | this document                                   |
| Model encoding                     | applicable `InputAdapter`/`OutputAdapter`, § 14 |

## 3. Conceptual model

MazeHard defines one fully observed spatial shortest-route problem over a decoded raster environment.
Let

$$
G' \quad \text{be the decoded raster domain},
$$

$$
G'_{\mathrm{free}} \subseteq G' \quad \text{be the traversable maze positions},
$$

and

$$
E'_{\mathrm{spatial}}
\subseteq
G'_{\mathrm{free}}\times G'_{\mathrm{free}}
$$

be the valid unit-cost grid4 transition relation.

One query is

$$
q' = \left(g'_{\mathrm{start}},g'_{\mathrm{goal}}\right),
\qquad
 g'_{\mathrm{start}},g'_{\mathrm{goal}}\in G'_{\mathrm{free}}.
$$

A physical route is an ordered sequence

$$
R = \left(g'_0,\ldots,g'_L\right)
$$

such that $g'_0=g'_{\mathrm{start}}$, $g'_L=g'_{\mathrm{goal}}$, and $(g'_k,g'_{k+1})\in E'_{\mathrm{spatial}}$ for every $k<L$.
With unit physical edge cost,

$$
C(R)=L.
$$

The task target is a spatial labeling that identifies one deterministic reference optimal route $R^*$ while preserving the visible maze, start, and goal semantics.

## 4. Information regime

### 4.1 Public information

The model is given the complete task-visible maze problem:

- which ambient positions are traversable or blocked;
- the unique start position;
- the unique goal position;
- natural-domain or padding masks required to interpret the representation.

### 4.2 Target information

The task provides canonical shortest-route truth according to the ambiguity policy in Section 8.

### 4.3 Privileged information

Oracle-only or diagnostic information may include:

- shortest-distance map;
- predecessor/successor relation;
- complete optimal-route support;
- canonical-route construction evidence.

These are not public problem inputs unless explicitly promoted by another task version.

### 4.4 Withheld information

The model is not given:

- BFS or search frontier state;
- predecessor tables;
- oracle distances;
- solution path or optimal support as input.

### 4.5 Leakage constraints

Any physical encoding must keep route truth distinct from input topology/start/goal information.

## 5. Unit of record and shared task context

### 5.1 Unit of record

One MazeHard record represents:

> one generated start–goal route problem over one topology record.

One topology may support many MazeHard records.

### 5.2 Record discriminators

Task-semantic discriminators include:

- topology parent record;
- start position;
- goal position;
- query realization index or selection identity;
- ambiguity protocol;
- oracle protocol;
- target representation protocol.

### 5.3 Shared task context

A corpus may deduplicate topology payload through a corpus-local environment table referenced by several problem records.
Such deduplication is a corpus representation choice and does not alter the logical record unit.

## 6. Parent roles and composition

### 6.1 Parent roles

| Role       | Required | Required contract    | Task use                      |
| ---------- | -------: | -------------------- | ----------------------------- |
| `topology` |      yes | `raster-topology/v1` | maze passability and movement |

MazeHard is not semantically restricted to Maze-ND, although Maze-ND is the intended source-topology family for source-derived maze experiments.

### 6.2 Required capabilities

MazeHard v1 requires:

```text
topology_kind: raster
coordinate_system: row-column
movement_kind: grid4
directed: false
edge_cost_kind: unit
```

A selected start and goal must lie in the same connected component.

### 6.3 Parent exclusions

MazeHard must not require the topology parent to provide:

- starts;
- goals;
- paths;
- source solutions;
- task token labels.

Maze-ND explicitly treats those as source problem-instance information rather than topology channels.

### 6.4 Composition procedure

For each selected topology record:

1. resolve its traversable position domain and movement relation;
2. select or generate one admissible start–goal query;
3. validate reachability;
4. compute canonical shortest-route truth;
5. materialize public task input and target channels.

## 7. Task generation

### 7.1 Start–goal generation

A query-generation protocol must define deterministic selection of $g'_{\mathrm{start}}$ and $g'_{\mathrm{goal}}$ subject to:

- $g'_{\mathrm{start}}\neq g'_{\mathrm{goal}}$;
- $g'_{\mathrm{start}},g'_{\mathrm{goal}}\in G'_{\mathrm{free}}$;
- $g'_{\mathrm{goal}}$ is reachable from $g'_{\mathrm{start}}$ through $E'_{\mathrm{spatial}}$;
- any declared distance or difficulty constraints.

The reference Maze-Hard corpus additionally applies its documented benchmark admission/filtering rules, including the reference 30 × 30 spatial extent and hard-instance selection used for reproduction.

### 7.2 Query distribution

Distance bands, topology reuse, record counts, and difficulty balancing belong to named corpus profiles unless they are required to preserve MazeHard v1 semantics.

### 7.3 Retry and exhaustion

When a protocol uses rejection to satisfy query constraints, attempts must be deterministic and record-addressable.
An exhausted logical query fails explicitly.

### 7.4 Source-reproduction profile

A named source-reproduction corpus may reconstruct original source start/goal/solution problem rows through immutable Maze-ND source lineage or raw-source material.

Such a profile must state explicitly that its query and reference solution are source-instance data.
It must not redefine Maze-ND topology records to contain those fields.

## 8. Oracle and target semantics

### 8.1 Shortest-route truth

For decoded goal $g'_{\mathrm{goal}}$, define the shortest remaining physical cost

$$
d^*(g')
=
\min_{R:g'\leadsto g'_{\mathrm{goal}}} C(R)
$$

for every traversable position from which the goal is reachable.
A transition $(g',\tilde g')\in E'_{\mathrm{spatial}}$ is shortest-path optimal exactly when

$$
d^*(g') = 1 + d^*(\tilde g').
$$

The optimal query cost is

$$
C^*=d^*(g'_{\mathrm{start}}).
$$

### 8.2 Canonical reference route

MazeHard stores one reference optimal route per task record.
Multiple optimal routes may exist, so the stored reference is canonical benchmark truth rather than the only mathematically valid optimum.

For EHP-SN-generated cases, the generation protocol must define a deterministic tie-break over shortest routes.
The selected route is

$$
R^*
=
\left(g_0'^*,\ldots,g_{C^*}'^*\right),
$$

with $g_0'^*=g'_{\mathrm{start}}$, $g_{C^*}'^*=g'_{\mathrm{goal}}$, and every transition shortest-path optimal.
A source-reproduction corpus may instead preserve the source dataset's designated optimal reference route when its provenance is exact.

### 8.3 Canonical path-labelled target

Let

$$
y^*:G'\rightarrow
\{\text{wall},\text{free},\text{start},\text{goal},\text{path}\}
$$

denote the semantic reference labeling.
It preserves the visible maze classes and marks exactly the route cells selected by $R^*$ according to the declared endpoint-overlay convention.

Concrete token IDs, flattening order, ignore-label integers, and model-native tensor layout belong to an adapter (§ 14) or named reproduction profile.

### 8.4 Alternative optimal-route validity

A decoded prediction may describe an optimal route different from $R^*$.
It is an any-valid-optimal solution when it begins at $g'_{\mathrm{start}}$, ends at $g'_{\mathrm{goal}}$, follows only transitions in $E'_{\mathrm{spatial}}$, and has cost $C^*$.

Such a prediction is structurally optimal but fails exact reference-grid equality if its path cells differ from the stored target.
This distinction is intentional and must be reported rather than collapsed.

### 8.5 Oracle correctness

Validation must independently verify that $R^*$ is a valid route of cost $C^*$ and that the stored path-labelled target encodes exactly the declared reference route under the applicable semantic representation convention.

## 9. Logical corpus contract

### 9.1 Record fields

One record contains or resolves at least:

| Field              | Required | Scope / semantic shape                             | Visibility          | Role             | Meaning                               |
| ------------------ | -------: | -------------------------------------------------- | ------------------- | ---------------- | ------------------------------------- |
| `record_id`        |      yes | scalar                                             | metadata            | identifier       | task-case identity                    |
| `environment_id`   |      yes | scalar                                             | metadata            | identifier       | corpus-local topology context         |
| `start_flag`       |      yes | natural raster domain                              | public              | input            | unique $g'_{\mathrm{start}}$          |
| `goal_flag`        |      yes | natural raster domain                              | public              | input            | unique $g'_{\mathrm{goal}}$           |
| `reference_path`   |      yes | natural raster domain or equivalent route encoding | target              | oracle/reference | one deterministic optimal route $R^*$ |
| `reference_labels` |      yes | natural raster domain                              | target              | primary target   | path-labelled target $y^*$            |
| `optimal_cost`     |      yes | scalar                                             | privileged/metadata | oracle truth     | $C^*$                                 |

The public environment resource must resolve traversability over the same natural domain.

### 9.2 Storage representation and reference profile

MazeHard task semantics are expressed over the natural raster domain.
The canonical reference reproduction profile is a `30 × 30` maze represented as `900` flattened spatial positions, matching the benchmark interface described in the research manuscript.

A separately named corpus may use another raster extent only if it preserves the same task meaning and clearly declares that results are not direct Maze-Hard reference-reproduction results.
Flattening order, token IDs, embeddings, and model-native tensor layout remain adapter/profile concerns.

### 9.3 Padding

When heterogeneous natural extents are represented in a common storage canvas, padding must be distinct from blocked maze positions and excluded from task metrics.

## 10. Split and sampling semantics

### 10.1 Parent split use

When a topology parent has intrinsic splits, MazeHard preserves same-split derivation under the generic corpus contract.

Maze-ND v1 has no intrinsic topology train/validation/test split; source-row split labels are lineage, not topology splits.
A MazeHard corpus using Maze-ND must therefore define its own topology/query split policy.

### 10.2 Environment-level split grouping and novelty

For benchmark corpora that generate several queries from one maze environment, all records derived from the same environment must belong to the same split.
This matches the environment-level split architecture used by the research evaluation and prevents shared topology from crossing train/validation/test boundaries.

A named MazeHard corpus must additionally state whether novelty applies to:

- topology/environment;
- start–goal pair within an environment;
- original source problem row for source-reproduction corpora.

### 10.3 Sampling

Sampling policies must not silently bias the benchmark through topology duplication or start–goal multiplicity.
Any balancing over path length or difficulty must be explicit.

## 11. Determinism and task identity inputs

MazeHard-specific semantic identity inputs include:

- topology selection policy;
- start–goal generation or source-instance selection protocol;
- difficulty/admission constraints;
- ambiguity policy;
- oracle protocol;
- target representation;
- split/novelty policy;
- task randomness roles.

Generation must be stable under worker count and serialization order.

## 12. Validation and invariants

### MH-COMP-001 — Topology capability

Every selected topology satisfies the required raster, grid4, undirected, unit-cost movement capabilities.

### MH-REC-001 — Start and goal validity

Each record contains exactly one traversable start and one distinct traversable goal.

### MH-REC-002 — Reachability

The goal is reachable from the start.

### MH-ORACLE-001 — Optimal-cost correctness

`optimal_cost` equals the true shortest physical path length $C^*$ from $g'_{\mathrm{start}}$ to $g'_{\mathrm{goal}}$.

### MH-ORACLE-002 — Reference-route validity

The stored $R^*$ starts at $g'_{\mathrm{start}}$, ends at $g'_{\mathrm{goal}}$, uses only valid $E'_{\mathrm{spatial}}$ transitions, and has physical cost $C^*$.

### MH-ORACLE-003 — Deterministic reference selection

For generated cases with more than one optimal route, the declared canonical tie-break selects exactly one $R^*$ deterministically.
Source-reproduction corpora may preserve one exact source-designated optimal route instead.

### MH-ORACLE-004 — Target encoding correctness

The stored path-labelled target encodes exactly $R^*$ and the declared maze/start/goal classes under the task representation convention.

### MH-CORPUS-001 — Self-contained problem resolution

All public maze input and target truth required for normal training, evaluation, validation, and inspection are corpus-local.

### MH-SPLIT-001 — Environment-level split grouping

All records derived from the same maze environment belong to one and only one corpus split.

### MH-SPLIT-002 — Declared novelty policy

Every record satisfies the corpus's declared topology/query novelty and parent-use policy.

## 13. Metrics and evaluation semantics

### 13.1 Primary metric: exact solution accuracy

The primary MazeHard metric is exact reference-grid accuracy: a record is correct only when every supervised output position equals the stored reference target $y^*$.
This matches the benchmark result used for direct HRM/MazeHard comparison.

Conceptually:

$$
A_{\mathrm{exact}}
=
\frac{1}{N}
\sum_{i=1}^{N}
\mathbb{1}\!\left[\hat y_i = y_i^*\text{ at every supervised position}\right].
$$

### 13.2 Secondary metric: token accuracy

Token accuracy reports the fraction of supervised positions whose predicted label equals $y^*$.
It is diagnostic because high token accuracy does not imply a complete correct route.

### 13.3 Structural any-valid-optimal metric

When a route can be decoded from the prediction, `any_valid_optimal_path_rate` may additionally report whether the prediction forms any connected traversable route of cost $C^*$, including an optimal route different from $R^*$.

This metric answers a different question from exact reference-grid accuracy and must not silently replace the primary benchmark metric.

### 13.4 Aggregation

Exact accuracy is aggregated per record.
Token accuracy is accumulated from total correct and supervised token counts.
Structural route validity is aggregated per decoded record.

## 14. Binding boundary

MazeHard defines semantic topology visibility, start, goal, the stored optimal reference target, exact-reference scoring, and optional structural optimal-route validation.

An `InputAdapter` (`docs/docs/framework/adapters/index.md`) may author:

- token vocabulary and categorical encoding policy;
- padding alignment and ignore-label policy.

The flattening slot count is not independently authored: it is derived from the task's
domain-derived position count (`S = H * W`, `docs/docs/framework/contracts/domains/ambient-domain-v1.md`).
Any fixed sequence capacity, such as 900, is model-owned or derived from the model's declared
capacity, not adapter-authored (`docs/invariants.md` `ADAPT-003`).

An `OutputAdapter` may define:

- logits layout over the flattened sequence;
- legacy single-path canonicalization, where a source-reproduction profile requires it.

Model-specific loss weighting belongs to the experiment's training protocol, not to either adapter.

The resolved binding — the task, the model, and this configured `InputAdapter`/`OutputAdapter` pair — must not change which maze information is public or redefine a non-shortest route as correct.

## 15. Open issues

- The first reference-reproduction corpus must freeze the exact 30 × 30 source/admission profile and source-solution reconstruction needed for direct HRM/Maze-Hard comparison.

- The shared `raster-topology/v1` contract must be finalized.
- The first canonical MazeHard corpus must define topology/query split policy for Maze-ND, whose normalized topology records have no intrinsic experimental splits.
- A legacy HRM source-reproduction profile should be specified separately if exact upstream 30×30 token-label behavior is required.
