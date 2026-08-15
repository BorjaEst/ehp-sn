---
title: Routebind v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Routebind v1

## Normative summary

`routebind/v1` defines a fully observed spatial–semantic prospective routing task in which physical topology and observation placement are public while a directed semantic transition law is hidden.

One corpus record represents one start–goal semantic routing query over one composed topology–ObsField environment under one corpus-level semantic graph and explicit graph-node-to-observation binding.

Routebind owns parent composition, semantic binding, query generation, semantic–spatial route oracle semantics, valid-route-set targets, public information, and route-specific metrics.
It does not own topology generation, observation-field generation, Dagflow graph generation, generic corpus mechanics, model architecture, or model-native encoding.

A conforming Routebind corpus also satisfies the generic `DataArtifact` and `TaskCorpus` contracts.

## 1. Purpose and scientific claim

### 1.1 Computational objective

Given visible spatial traversability, visible observation identity at traversable positions, one physical start, and a semantic goal cue, predict trajectory and waypoint fields that encode valid semantic–spatial routes, with lower-cost routes preferred according to the declared route-cost weighting.

### 1.2 Scientific question

Routebind tests whether a system can combine visible spatial structure with a corpus-stable but unobserved semantic transition law learned parametrically across task cases.

### 1.3 Intended comparisons

Routebind is intended as a visible-structure control for memory-conditioned tasks such as Prospect.
It also supports comparisons across physical route length, semantic transition depth, topology family, observation realization, and graph structure.

### 1.4 Non-claims

Routebind does not test recovery of spatial topology from memory because topology and observation placement are directly provided to the model.

## 2. Scope and ownership

### 2.1 Task-owned semantics

Routebind defines:

- topology–ObsField composition;
- explicit binding between Dagflow node identities and observation vocabulary entries;
- corpus-level hidden semantic law;
- task state $\xi=(g',o)$ over decoded physical position and accepted observation identity;
- physical and semantic transitions;
- start/goal query generation;
- valid accepting-route reference computation and optimal-cost calculation;
- valid-route-set target semantics;
- task-level information boundary and metrics.

### 2.2 Excluded semantics

Routebind does not define:

- topology or ObsField generation;
- Dagflow graph-generation distributions;
- model architecture or deliberation controller;
- binding-specific tensors, tokenization, or losses;
- generic manifests, fingerprints, or publication mechanics;
- CLI or repository implementation details.

### 2.3 Authoritative dependencies

| Concern                         | Authoritative specification                     |
| ------------------------------- | ----------------------------------------------- |
| Generic generated-data contract | `data-artifacts`                                |
| Generic task-corpus contract    | `corpora`                                       |
| Spatial topology                | `raster-topology/v1`                            |
| Observation field               | `categorical-field/v1`                          |
| Directed semantic graph         | `simple-digraph/v1`                             |
| Task semantics                  | this document                                   |
| Model encoding                  | applicable `InputAdapter`/`OutputAdapter`, § 14 |

## 3. Conceptual model

### 3.1 Symbols and spatial environment

| Symbol                  | Meaning                                                    |
| ----------------------- | ---------------------------------------------------------- |
| $G'$                    | decoded ambient spatial domain                             |
| $G'_{\mathrm{free}}$    | traversable positions                                      |
| $E'_{\mathrm{spatial}}$ | valid physical transitions                                 |
| $Obs$                   | categorical observation vocabulary                         |
| $\phi$                  | observation assignment $G'_{\mathrm{free}}\rightarrow Obs$ |
| $D_{\mathrm{sem}}$      | source semantic graph over Dagflow node IDs                |
| $\beta$                 | task-owned bijection from Dagflow nodes to observations    |
| $D_{\mathrm{obs}}$      | hidden semantic graph over $Obs$                           |
| $q'$                    | decoded start/semantic-goal query                          |
| $\xi=(g',o)$            | joint spatial–semantic route state                         |

For one compatible topology and ObsField composition,

$$
E'_{\mathrm{spatial}}
\subseteq
G'_{\mathrm{free}}\times G'_{\mathrm{free}},
\qquad
\phi:G'_{\mathrm{free}}\rightarrow Obs.
$$

Routebind exposes the composed spatial structure and observation placement to the model while keeping the semantic law hidden.

### 3.2 Semantic graph source and observation binding

Let the selected Dagflow source graph be

$$
D_{\mathrm{sem}}
=
\left(N_{\mathrm{sem}},E_{\mathrm{sem}}\right).
$$

Dagflow node identifiers are not observation identifiers.
Routebind therefore constructs an explicit task-owned bijection

$$
\beta:N_{\mathrm{sem}}\xrightarrow{\sim} Obs.
$$

The hidden observation-level semantic graph is

$$
D_{\mathrm{obs}}
=
\left(Obs,E_{\mathrm{obs}}\right),
$$

with

$$
E_{\mathrm{obs}}
=
\left\{
\left(\beta(n),\beta(\tilde n)\right)
\mid
(n,\tilde n)\in E_{\mathrm{sem}}
\right\}.
$$

### 3.3 Task query

A decoded query is

$$
q'
=
\left(g'_{\mathrm{start}},o_{\mathrm{goal}}\right),
\qquad
 g'_{\mathrm{start}}\in G'_{\mathrm{free}},
\quad
 o_{\mathrm{goal}}\in Obs.
$$

The corresponding physical goal-support set is

$$
C_{\mathrm{goal}}
=
\left\{
 g'\in G'_{\mathrm{free}}
 \mid
 \phi(g')=o_{\mathrm{goal}}
\right\}.
$$

Routebind exposes this support through its public goal representation.

### 3.4 Route state

The route state space is

$$
\mathcal S_{\mathrm{route}}
=
G'_{\mathrm{free}}\times Obs.
$$

A route state is

$$
\xi=(g',o),
$$

where $g'$ is the current physical position and $o$ is the last semantically accepted observation.
The initial semantic state is the observation at the start position:

$$
o_{\mathrm{start}}=\phi(g'_{\mathrm{start}}),
\qquad
\xi_0=\left(g'_{\mathrm{start}},o_{\mathrm{start}}\right).
$$

## 4. Information regime

### 4.1 Public information

The model receives semantic access to:

- natural-domain traversability or equivalent visible topology;
- observation identity at each traversable position;
- unique start position;
- all physical occurrences of the selected goal observation;
- spatial-domain mask when padding is used.

### 4.2 Target information

The task provides route-weighted trajectory and waypoint field truth derived from the semantic–spatial route oracle.

### 4.3 Privileged information

The following are available for generation, validation, or evaluation but not as model input:

- semantic graph edges;
- graph-node-to-observation binding;
- selected goal observation identity $o_{\mathrm{goal}}$ and candidate set $C_{\mathrm{goal}}$;
- complete retained valid-route set and per-route costs;
- exact optimal cost $C^*$;
- route-weight and target-construction diagnostics.

### 4.4 Withheld information

The hidden semantic graph and its binding are not exposed as model inputs.
The model must infer the reusable semantic law from route supervision across corpus cases.

### 4.5 Leakage constraints

The corpus or binding must not expose:

- semantic adjacency;
- canonical semantic waypoint sequence;
- retained oracle routes or route costs;
- target fields as input channels.

## 5. Unit of record and shared task context

### 5.1 Unit of record

One Routebind record represents:

> one start–semantic-goal query over one composed spatial environment under the corpus's semantic law.

### 5.2 Record discriminators

Task-semantic discriminators include:

- topology record;
- ObsField record;
- corpus-level semantic graph identity;
- corpus-level binding identity;
- start position;
- goal observation identity $o_{\mathrm{goal}}$;
- query realization or selection identity;
- oracle and target protocol parameters.

### 5.3 Shared task context

A Routebind corpus contains corpus-local shared task resources for:

- the hidden semantic graph;
- the graph-node-to-observation binding;
- reusable composed environment entries when several queries share one environment.

These resources are required for self-contained validation but remain privileged unless explicitly declared public.

## 6. Parent roles and composition

### 6.1 Parent roles

| Role                    |                   Required | Required contract      | Task use                                                    |
| ----------------------- | -------------------------: | ---------------------- | ----------------------------------------------------------- |
| `topology`              |                        yes | `raster-topology/v1`   | physical traversability and movement                        |
| `observation_field`     |                        yes | `categorical-field/v1` | visible observation placement                               |
| `semantic_graph_source` | yes for canonical v1 build | `simple-digraph/v1`    | source graph structure for corpus-level hidden semantic law |

### 6.2 Required topology capabilities

```text
topology_kind: raster
coordinate_system: row-column
movement_kind: grid4
directed: false
edge_cost_kind: unit
```

### 6.3 Parent exclusions

Routebind must not infer:

- observation assignments from topology;
- traversability from ObsField;
- graph-node/observation identity from matching integer values or cardinality;
- task goals or routes from parent artifacts.

### 6.4 Topology–ObsField compatibility

Compatibility requires equality of the complete ambient-domain semantics needed to identify the same position space.

Every traversable topology state must map to exactly one ObsField ambient position.

### 6.5 Graph–observation binding compatibility

The selected Dagflow graph must have exactly the same cardinality as the task observation vocabulary so that the declared binding protocol constructs a deterministic bijection

$$
\beta:N_{\mathrm{sem}}\xrightarrow{\sim} Obs.
$$

The binding protocol must be explicit and deterministic.
It may use a declared mapping, deterministic permutation, or another registered bijective protocol.
Matching integer values alone never establish identity.

### 6.6 Composition procedure

1. select compatible topology and ObsField records;
2. compose traversability with the restricted observation field;
3. select the corpus-level semantic graph source according to the corpus profile;
4. construct the explicit graph-node-to-observation binding;
5. validate start-eligible and goal-eligible observations in each environment;
6. generate task queries;
7. compute oracle truth and materialize records.

### 6.7 Semantic graph scope

Routebind v1 defines one semantic graph and one binding as corpus-level task state shared across all splits of a corpus.

Because Dagflow has intrinsic graph splits while the same hidden law is intentionally reused across Routebind splits, the selected Dagflow record is not treated as an example-level same-split parent.
Instead, the Routebind builder materializes the chosen graph and binding as corpus-level generated/derived task resources whose exact Dagflow source remains provenance.

This is a deliberate task-law construction, not cross-split derivation of individual task records from a parent example.

## 7. Task generation

### 7.1 Physical transition

Physical movement changes decoded position but not semantic state:

$$
\left((g',o),(\tilde g',o)\right)\in R_{\mathrm{phys}}
\iff
(g',\tilde g')\in E'_{\mathrm{spatial}}.
$$

Every physical transition has unit cost.

### 7.2 Semantic acceptance

Semantic acceptance changes semantic state without changing physical position:

$$
\left((g',o),(g',\tilde o)\right)\in R_{\mathrm{sem}}
\iff
\tilde o=\phi(g')
\land
(o,\tilde o)\in E_{\mathrm{obs}}.
$$

Semantic acceptance has zero physical cost and is optional whenever the condition holds.
Merely crossing a position carrying an admissible observation does not update semantic state unless the acceptance transition is taken.

The complete route relation is

$$
E_{\mathrm{route}}
=
R_{\mathrm{phys}}\cup R_{\mathrm{sem}}.
$$

### 7.3 Successful accepting route

A route is a finite sequence

$$
\Pi=(\xi_0,\xi_1,\ldots,\xi_L)
$$

whose consecutive states follow $E_{\mathrm{route}}$.
It is a successful accepting route when it begins at the query's initial state and terminates immediately after accepting $o_{\mathrm{goal}}$ at a position in $C_{\mathrm{goal}}$.

Routebind v1 uses simple product-state routes: no joint state $\xi$ may repeat within one valid route.

### 7.4 Query eligibility

A candidate query is eligible only when:

- the start is traversable and carries an observation;
- the goal observation occurs at least once in the environment;
- the goal differs from the already accepted start observation;
- at least one successful accepting route exists.

### 7.5 Query distribution and exhaustion

A corpus profile may stratify queries by physical cost, semantic depth, or other task-derived difficulty variables.
Such stratification must be explicit.
If generation cannot satisfy a required quota under the declared attempt policy, exhaustion is an explicit build failure unless the profile explicitly defines degraded completion semantics.

## 8. Oracle and target semantics

### 8.1 Mathematical route set and cost

Let $\mathcal V$ be the complete finite set of valid simple accepting routes for a query.
For a route $\Pi$, let $I_{\mathrm{move}}(\Pi)$ denote its physical-transition indexes.
Unit physical cost gives

$$
C(\Pi)=\left|I_{\mathrm{move}}(\Pi)\right|.
$$

The optimal physical cost and optimal subset are

$$
C^*=\min_{\Pi\in\mathcal V}C(\Pi),
\qquad
\mathcal V^*=\left\{\Pi\in\mathcal V\mid C(\Pi)=C^*\right\}.
$$

The oracle does not select one canonical route.

### 8.2 Physical and waypoint projections

For $\Pi=(\xi_0,\ldots,\xi_L)$ with $\xi_r=(g'_r,o_r)$, let $R(\Pi)$ be the ordered decoded positions visited by the route, and let $W(\Pi)$ be the decoded positions at which a semantic-acceptance transition occurs.

### 8.3 Route-cost weighting

Define excess physical cost

$$
\Delta(\Pi)=C(\Pi)-C^*.
$$

For $\lambda_{\mathrm{valid}}\in[0,1]$, define

$$
w_\lambda(\Pi)
=
\begin{cases}
1, & \Delta(\Pi)=0,\\
\lambda_{\mathrm{valid}}^{\Delta(\Pi)}, & \Delta(\Pi)>0.
\end{cases}
$$

Thus all optimal routes have unit route-level weight.
The special case $\lambda_{\mathrm{valid}}=0$ gives positive weight only to optimal routes; $\lambda_{\mathrm{valid}}=1$ weights every valid route equally.

### 8.4 Physical and semantic depth

For $g'\in R(\Pi)$, let $d_R(g',\Pi)$ be the number of physical transitions completed before the first occurrence of $g'$ in $\Pi$.
For $g'\in W(\Pi)$, let $d_W(g',\Pi)$ be the number of semantic acceptances completed up to and including the first acceptance at $g'$.

### 8.5 Canonical target fields

For $\gamma_{\mathrm{space}},\gamma_{\mathrm{semantic}}\in(0,1]$, define per-route contributions

$$
s_{\mathrm{traj}}(g',\Pi)
=
\gamma_{\mathrm{space}}^{d_R(g',\Pi)}w_\lambda(\Pi),
$$

$$
s_{\mathrm{wp}}(g',\Pi)
=
\gamma_{\mathrm{semantic}}^{d_W(g',\Pi)}w_\lambda(\Pi).
$$

The oracle/reference fields are

$$
f_{\mathrm{traj}}^*(g')
=
\max\!\left(
\{0\}\cup
\{s_{\mathrm{traj}}(g',\Pi)\mid \Pi\in\mathcal V,\ g'\in R(\Pi)\}
\right),
$$

$$
f_{\mathrm{wp}}^*(g')
=
\max\!\left(
\{0\}\cup
\{s_{\mathrm{wp}}(g',\Pi)\mid \Pi\in\mathcal V,\ g'\in W(\Pi)\}
\right).
$$

Both fields are defined over $G'$ and take values in $[0,1]$.
Non-traversable positions and positions unsupported by any contributing route receive zero.
Maximum aggregation prevents target amplitude from depending on route multiplicity.

The corpus channels `target_trajectory` and `target_waypoint` materialize $f_{\mathrm{traj}}^*$ and $f_{\mathrm{wp}}^*$ respectively.
Model predictions are denoted $\hat f_{\mathrm{traj}}$ and $\hat f_{\mathrm{wp}}$.

### 8.6 Finite enumeration protocol

The mathematical reference set is $\mathcal V$.
A concrete benchmark protocol may impose a deterministic finite enumeration limit.
If that limit truncates $\mathcal V$, the enumeration order, retained-subset rule, limit, and truncation status are part of target-generation semantics and corpus identity.
Target construction then uses the declared retained set exactly.

### 8.7 Privileged oracle information

The route set, per-route costs, $C^*$, hidden semantic graph, graph-observation binding, and target fields are privileged.
None is a model input.

### 8.8 Oracle correctness

Validation must establish that every retained route is a simple accepting route under $E_{\mathrm{route}}$, that every route cost is correct, and that the stored target fields equal the declared maximum aggregation over the retained route set.

## 9. Logical corpus contract

### 9.1 Record fields

| Field               |    Required | Scope / semantic shape | Visibility | Role              | Meaning                         |
| ------------------- | ----------: | ---------------------- | ---------- | ----------------- | ------------------------------- |
| `record_id`         |         yes | scalar                 | metadata   | identifier        | query identity                  |
| `environment_id`    |         yes | scalar                 | metadata   | identifier        | composed environment reference  |
| `start_flag`        |         yes | natural spatial domain | public     | input             | unique $g'_{\mathrm{start}}$    |
| `goal_flag`         |         yes | natural spatial domain | public     | input             | support $C_{\mathrm{goal}}$     |
| `target_trajectory` |         yes | natural spatial domain | target     | primary target    | $f_{\mathrm{traj}}^*$           |
| `target_waypoint`   |         yes | natural spatial domain | target     | structural target | $f_{\mathrm{wp}}^*$             |
| `optimal_cost`      |         yes | scalar                 | privileged | oracle metadata   | $C^*$                           |
| `valid_route_count` |         yes | scalar                 | privileged | diagnostic        | number of retained valid routes |
| `spatial_mask`      | when padded | storage domain         | technical  | mask              | natural-domain membership only  |

The referenced environment entry resolves the public traversability and observation identity needed by the task input.
Additional route-enumeration diagnostics may be stored as privileged channels but are not additional canonical outputs.

### 9.2 Shared semantic-law resource

The corpus-local privileged semantic-law resource resolves:

- semantic graph node domain and edges;
- graph-node-to-observation bijection;
- source Dagflow provenance;
- binding protocol identity.

### 9.3 Natural and storage domains

If heterogeneous natural extents are embedded in a common storage canvas, the corpus must distinguish natural-domain positions, blocked natural-domain positions, traversable natural-domain positions, and storage padding.
Padding is outside the natural environment: it is neither a wall nor a traversable state.

## 10. Split and sampling semantics

### 10.1 Environment-level split grouping

Routebind split boundaries are defined at the composed-environment level.
All queries generated from the same topology–ObsField environment belong to the same corpus split:

$$
\operatorname{environment}(q_i)=\operatorname{environment}(q_j)
\;\Longrightarrow\;
\operatorname{split}(q_i)=\operatorname{split}(q_j).
$$

This is normative for Routebind v1 and prevents leakage through shared topology or observation–position assignments.

When parent substrates have intrinsic splits, their use must additionally satisfy the generic corpus parent-split contract or another explicit framework-permitted transformation.

### 10.2 Corpus-level semantic law

The hidden $D_{\mathrm{obs}}$ and its $\beta$ binding are shared across the complete Routebind corpus, including train, validation, and test.
They are corpus-level task law rather than example-level split-specific target information.

### 10.3 Query sampling

Within each environment, start positions and goal observations are selected under the declared query protocol, subject to task validity ($\mathcal V\neq\varnothing$) and any named difficulty constraints.
The reference sampling regime may draw admissible start/goal pairs without replacement within an environment when the eligible set exceeds the corpus budget.

### 10.4 Additional novelty and balancing

A named corpus may impose stronger novelty constraints or balance by physical cost, semantic depth, topology family, or another declared task property.
Such policies must preserve environment-level split grouping and be identity-bearing when they change corpus content.

## 11. Determinism and task identity inputs

Routebind-specific semantic identity inputs include:

- parent selection and pairing policy;
- semantic graph source selection;
- graph-node-to-observation binding protocol;
- query-generation protocol;
- target protocol, $\lambda_{\mathrm{valid}}$, and spatial/semantic decay parameters;
- sampling/admission policy;
- storage-domain canonicalization when identity-bearing;
- task randomness roles.

Generation must be stable under worker count and physical serialization order.

## 12. Validation and invariants

### RB-COMP-001 — Spatial-domain compatibility

Every composed topology and ObsField record pair identifies the same ambient position space.

### RB-COMP-002 — Explicit semantic binding

Every semantic node used by Routebind resolves through one declared graph-node-to-observation binding.
Equality is never inferred from numeric IDs alone.

### RB-REC-001 — Valid start semantics

The unique start $g'_{\mathrm{start}}$ is traversable and $o_{\mathrm{start}}=\phi(g'_{\mathrm{start}})$ belongs to the bound observation-level semantic graph $D_{\mathrm{obs}}$.

### RB-REC-002 — Goal availability

The selected $o_{\mathrm{goal}}$ differs from $o_{\mathrm{start}}$ and $C_{\mathrm{goal}}$ is non-empty.

### RB-ORACLE-001 — Valid-route correctness

Every retained $\Pi\in\mathcal V$ begins at $\xi_0$, contains only transitions in $E_{\mathrm{route}}$, contains no repeated route state, and terminates after accepting $o_{\mathrm{goal}}$.

### RB-ORACLE-002 — Route-cost correctness

Every retained route cost equals its number of physical transitions, and $C^*$ equals the minimum cost over the retained complete valid-route set.

### RB-ORACLE-003 — Target aggregation correctness

For every decoded position $g'$, `target_trajectory` and `target_waypoint` equal the maximum route-weighted contributions prescribed by $f_{\mathrm{traj}}^*$ and $f_{\mathrm{wp}}^*$.

### RB-ORACLE-004 — Multiplicity semantics

No single route is privileged as the canonical Routebind solution.
When several valid routes contribute, maximum aggregation depends on their eligibility, costs, and depths rather than on route multiplicity.

### RB-ORACLE-005 — Enumeration declaration

If the implementation uses a finite route-enumeration limit, the limit, deterministic retention policy, and resulting target semantics are declared and validated.

### RB-CORPUS-001 — Local semantic-law resolution

The hidden semantic graph and binding required for validation are available as corpus-local privileged resources.

### RB-SPLIT-001 — Declared semantic-law scope

The corpus records whether its semantic graph and binding are shared across splits or split-specific.
Routebind v1 default semantics require one corpus-level shared law.

## 13. Metrics and evaluation semantics

### 13.1 Primary behavioral metric

The primary behavioral metric is `valid_semantic_spatial_route_rate`: the fraction of decoded routes that:

- begin at the declared start;
- use valid traversable grid4 moves;
- terminate at a goal-observation occurrence;
- admit a semantic acceptance subsequence consistent with the hidden graph and binding.

### 13.2 Optimality metric

For valid decoded routes:

$$
\rho_{\mathrm{cost}}
=
\frac{C(\hat R)}{C^*}.
$$

A ratio of 1 denotes physical optimality under the Routebind semantic constraints.

### 13.3 Representational metrics

For field-producing bindings, recommended metrics include support-balanced error, trajectory-field error, waypoint-field error, and multi-label first-action metrics.

These are representational diagnostics unless a concrete experiment identifies one as a primary outcome.

### 13.4 Structural validity precedes field similarity

A low field error does not by itself establish a valid semantic-spatial route.
Behavioral structural validity and optimality must remain separately reported.

## 14. Binding boundary

Routebind defines public spatial/observation information, hidden semantic-law semantics, targets, and validity.

An `InputAdapter` (`docs/docs/framework/adapters/index.md`) may define:

- dense or flattened layout representation;
- padding tensors;
- categorical observation encoding.

An `OutputAdapter` may define:

- field decoder layout.

Multi-label loss construction and model-native recurrent deliberation belong to the experiment's training protocol, not to either adapter.

The resolved binding must not expose the hidden graph/binding or change the product-state correctness relation.

## 15. Open issues

- The shared `raster-topology/v1` specification must be finalized.
- The first Routebind corpus must choose one explicit graph-node-to-observation binding protocol.
- The precise framework representation of a corpus-level semantic law sourced from an intrinsically split Dagflow artifact should be documented in the corpus/profile specification so it is not mistaken for example-level cross-split derivation.
- Named Routebind corpus profiles must define their actual cost/depth distributions; the task specification intentionally does not freeze the previous large preset table.
