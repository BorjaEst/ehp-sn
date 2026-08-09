---
title: Prospect v1
authority: normative
document_status: draft
api_stability: provisional
---

# Prospect v1

## Normative summary

`prospect/v1` defines a memory-conditioned spatial–semantic prospective routing task. The current query input withholds visible topology and complete observation placement and instead supplies a previously acquired environment-specific memory representation together with a start cue and semantic goal observation identity.

One corpus record represents one start–goal semantic routing query over one environment for which a compatible acquired-memory entry has already been produced.

Prospect uses the same physical/semantic oracle semantics as Routebind, but changes the information regime: spatial traversability and non-goal observation placement are not directly exposed to the model. Required acquired-memory content is materialized as corpus-local shared task context so the committed corpus remains self-contained.

Prospect owns the memory-conditioned task information boundary, memory/environment compatibility relation, query generation, shared Routebind-compatible oracle truth, leakage constraints, and Prospect metrics. It does not own memory-model architecture, acquisition-model internals, topology or ObsField generation, or model-native memory encoding.

A conforming Prospect corpus also satisfies the generic `DataArtifact` and `TaskCorpus` contracts.

## 1. Purpose and scientific claim

### 1.1 Computational objective

Given:

- one acquired environment-specific memory state;
- one physical start position;
- one semantic goal observation identity;
- a non-semantic output-slot validity mask when fixed-size padded output requires it;

predict trajectory and waypoint fields encoding valid semantic–spatial routes without receiving the current environment's wall map, traversability graph, observation-to-position assignment, or physical goal-location mask directly.

### 1.2 Scientific question

Prospect tests whether an acquired environment-specific memory representation can supply spatial structure required for novel prospective route reasoning when direct spatial topology and complete observation placement are withheld from the current task input.

### 1.3 Intended comparisons

The principal control comparison is Routebind under matched environment, semantic-law, query, and oracle semantics:

```text
Routebind:
    visible topology + visible observation placement + query

Prospect:
    acquired environment memory + query
```

Differences in performance can then be interpreted in relation to the information source for environment-specific spatial structure.

### 1.4 Non-claims

Prospect v1 does not establish:

- that memory acquisition and prospective reasoning are trained end-to-end;
- that the acquired memory has any particular biological implementation;
- that semantic graph knowledge is stored in the acquired spatial memory.

## 2. Scope and ownership

### 2.1 Task-owned semantics

Prospect defines:

- its current-query information regime;
- required acquired-memory role;
- compatibility between acquired memory and the exact composed environment;
- start and goal query semantics;
- task-level novelty/leakage constraints;
- the same product-state oracle truth as Routebind;
- Prospect-specific memory diagnostics and metrics.

### 2.2 Excluded semantics

Prospect does not define:

- TEM, EHP, or another model's internal memory structure;
- how memory is encoded into model-native tensors;
- topology or ObsField generation;
- semantic graph generation;
- optimizer or training policy;
- generic artifact publication or manifest mechanics;
- runtime resolution of required data from an external memory-bank artifact.

### 2.3 Authoritative dependencies

| Concern                         | Authoritative specification                     |
| ------------------------------- | ----------------------------------------------- |
| Generic generated-data contract | `data-artifacts`                                |
| Generic task-corpus contract    | `corpora`                                       |
| Spatial topology                | `raster-topology/v1`                            |
| Observation field               | `obsfield/v1`                                   |
| Semantic graph source           | `dagflow/v1`                                    |
| Shared route semantics          | `routebind/v1` oracle semantics                 |
| Task semantics                  | this document                                   |
| Memory-native encoding          | applicable Prospect binding/model specification |

## 3. Conceptual model

### 3.1 Symbols and task query

| Symbol                  | Meaning                                                    |
| ----------------------- | ---------------------------------------------------------- |
| $G'$                    | decoded spatial domain                                     |
| $G'_{\mathrm{free}}$    | traversable positions                                      |
| $E'_{\mathrm{spatial}}$ | valid physical transitions                                 |
| $Obs$                   | categorical observation vocabulary                         |
| $\phi$                  | observation assignment $G'_{\mathrm{free}}\rightarrow Obs$ |
| $D_{\mathrm{obs}}$      | hidden semantic graph over $Obs$                           |
| $q'$                    | decoded start/semantic-goal query                          |
| $C_{\mathrm{goal}}$     | privileged physical support of the semantic goal           |
| $M_e$                   | acquired environment-specific memory at the task level     |
| $\xi=(g',o)$            | joint spatial–semantic route state                         |

The decoded query is

$$
q'
=
\left(g'_{\mathrm{start}},o_{\mathrm{goal}}\right),
\qquad
 g'_{\mathrm{start}}\in G'_{\mathrm{free}},
\quad
 o_{\mathrm{goal}}\in Obs.
$$

The physical support of the semantic goal is

$$
C_{\mathrm{goal}}
=
\left\{
 g'\in G'_{\mathrm{free}}
 \mid
 \phi(g')=o_{\mathrm{goal}}
\right\},
$$

which is privileged environment truth and is not a Prospect model input.

A binding converts the benchmark-level query and memory role into model-facing representations. Prospect constrains the information available to that conversion but does not prescribe the model-native encodings.

### 3.2 Composed environment

A Prospect environment is produced by composing one compatible topology and ObsField. The composition defines $G'_{\mathrm{free}}$, $E'_{\mathrm{spatial}}$, and $\phi$ for generation, oracle computation, and validation. Most of this decoded structure is withheld from the model-facing query.

### 3.3 Acquired environment memory

An acquired-memory entry is an environment-specific state produced before Prospect query generation by a declared acquisition process. Prospect treats it abstractly as the semantic input role `acquired_environment_memory`; the task does not standardize the internal tensors, slots, latent variables, or recurrent objects constituting the memory.

### 3.4 Corpus-local memory table

Required acquired-memory entries are copied or deterministically materialized into a corpus-local shared memory table during Prospect corpus construction. Prospect records reference a local `memory_entry_id`. Normal corpus use must not require an external memory-bank lookup.

### 3.5 Semantic law

Prospect uses the same hidden observation-level semantic graph $D_{\mathrm{obs}}=(Obs,E_{\mathrm{obs}})$ and graph-node-to-observation binding semantics as Routebind. The semantic law is corpus-level privileged task context and is not assumed to be encoded in the acquired spatial memory.

## 4. Information regime

### 4.1 Public task information

At the benchmark/task level, Prospect provides:

- the acquired environment-memory entry associated with the explored environment;
- decoded start identity $g'_{\mathrm{start}}$ as the source of the model's start-state encoding;
- semantic goal observation identity $o_{\mathrm{goal}}$ as the source of the model's sensory goal cue;
- the technical output-slot validity mask required to interpret the fixed spatial output domain, when applicable.

The decoded task variables are not necessarily supplied directly to the model. A binding must derive the model-facing start and sensory goal representations without exposing additional privileged environment structure.

### 4.2 Target information

Prospect uses Routebind-compatible route-weighted trajectory and waypoint field truth.

### 4.3 Privileged information

Generation, validation, and evaluation may access:

- full topology;
- full observation assignment;
- hidden semantic graph;
- graph-node-to-observation binding;
- oracle product-state distances and valid-route set;
- acquisition provenance and qualification evidence.

### 4.4 Withheld information

The model is not directly given:

- wall/free map;
- physical adjacency;
- complete observation identity per position;
- physical goal-location mask $C_{\mathrm{goal}}$;
- hidden semantic graph or binding;
- oracle route or waypoint truth.

### 4.5 Goal-cue semantics

Prospect v1 exposes the semantic goal identity $o_{\mathrm{goal}}$, or a binding-defined sensory encoding derived from it. It does not expose $C_{\mathrm{goal}}$, `goal_flag`, or any equivalent physical goal-location support. The evaluated system must recover any goal-location binding required for routing from the permitted acquired-memory and query representations.

### 4.6 Leakage constraints

Acquired memory used by a Prospect record must have been produced before the record's route query and without access to:

- that query's oracle route;
- target support/depth fields;
- query-specific semantic waypoint sequence.

If a corpus claims query novelty relative to acquisition experience, that novelty must be operationally defined and validated.

## 5. Unit of record and shared task context

### 5.1 Unit of record

One Prospect record represents:

> one memory-conditioned start–semantic-goal query over one exact composed environment.

### 5.2 Record discriminators

Task-semantic discriminators include:

- composed environment identity;
- local acquired-memory entry;
- semantic graph and binding law;
- start position;
- goal observation identity;
- query realization identity;
- target/oracle protocol;
- declared acquisition-novelty relation.

### 5.3 Shared task context

A Prospect corpus contains corpus-local shared resources for:

- composed environment validation context;
- acquired-memory entries;
- hidden semantic graph;
- graph-node-to-observation binding;
- acquisition provenance/qualification summaries needed by validation.

Records refer to these through corpus-local identifiers.

## 6. Parent roles and composition

### 6.1 Build-time parent roles

| Role                     | Required | Required contract                                  | Task use                                                 |
| ------------------------ | -------: | -------------------------------------------------- | -------------------------------------------------------- |
| `topology`               |      yes | `raster-topology/v1`                               | oracle physical structure and memory compatibility       |
| `observation_field`      |      yes | `obsfield/v1`                                      | oracle observation placement and memory compatibility    |
| `semantic_graph_source`  |      yes | `dagflow/v1`                                       | source of hidden semantic law                            |
| `acquired_memory_source` |      yes | producer/binding-defined qualified memory resource | source bytes/state copied into corpus-local memory table |

### 6.2 Spatial compatibility

Topology and ObsField compatibility is identical to Routebind: their complete ambient-domain semantics must identify the same position space.

### 6.3 Semantic binding

Graph-node-to-observation identity is explicit and task-owned exactly as in Routebind. The selected semantic graph node domain is bound bijectively to the complete task observation vocabulary:

$$
\beta:N_{\mathrm{sem}}\xrightarrow{\sim} Obs,
\qquad
D_{\mathrm{obs}}=(Obs,E_{\mathrm{obs}}).
$$

Identity is never inferred from matching integer values or cardinality alone.

### 6.4 Memory/environment compatibility

Every Prospect record must resolve an acquired-memory entry compatible with the exact composed environment and declared acquisition semantics.

| Compatibility dimension | Requirement                                                             |
| ----------------------- | ----------------------------------------------------------------------- |
| Topology                | exact topology record/content identity used by the composed environment |
| Observation field       | exact ObsField realization identity                                     |
| Vocabulary              | exact observation-vocabulary identity                                   |
| Coordinates             | compatible ambient-domain and position convention                       |
| Acquisition             | exact acquisition protocol and qualifying experience identity           |
| Producer                | supported checkpoint/model producer identity where required             |
| Memory schema           | supported by the consuming Prospect binding                             |

A cardinality match, equal tensor shape, or common topology family is insufficient evidence of memory compatibility.

### 6.5 Composition procedure

1. select compatible topology and ObsField records;
2. construct the composed environment;
3. select and validate an acquired-memory entry produced for that exact environment;
4. copy/materialize the required memory content into the corpus-local memory table;
5. resolve the corpus-level semantic graph and graph-observation binding;
6. generate Prospect queries;
7. compute Routebind-compatible oracle truth from source environment and semantic law, never from acquired memory;
8. materialize query records and local shared resources.

### 6.6 Rejection conditions

Reject a candidate if:

- topology and ObsField are incompatible;
- memory does not match the exact composed environment;
- memory schema is unsupported by the declared producing/consuming binding contract;
- qualification evidence required by the corpus profile is absent;
- acquisition leakage constraints fail;
- no valid semantic-spatial query exists.

## 7. Task generation

### 7.1 Route state space

Prospect uses the same route state space as Routebind:

$$
\mathcal S_{\mathrm{route}}
=
G'_{\mathrm{free}}\times Obs,
\qquad
\xi=(g',o).
$$

The initial semantic state is

$$
o_{\mathrm{start}}=\phi(g'_{\mathrm{start}}),
\qquad
\xi_0=\left(g'_{\mathrm{start}},o_{\mathrm{start}}\right).
$$

### 7.2 Physical and semantic transitions

Physical movement satisfies

$$
\left((g',o),(\tilde g',o)\right)\in R_{\mathrm{phys}}
\iff
(g',\tilde g')\in E'_{\mathrm{spatial}},
$$

and has unit cost. Semantic acceptance satisfies

$$
\left((g',o),(g',\tilde o)\right)\in R_{\mathrm{sem}}
\iff
\tilde o=\phi(g')
\land
(o,\tilde o)\in E_{\mathrm{obs}},
$$

and has zero physical cost.

### 7.3 Valid accepting routes

A valid route is a simple finite sequence

$$
\Pi=(\xi_0,\ldots,\xi_L)
$$

whose consecutive states follow $R_{\mathrm{phys}}\cup R_{\mathrm{sem}}$ and which terminates immediately after accepting $o_{\mathrm{goal}}$ at a position in $C_{\mathrm{goal}}$.

### 7.4 Query novelty

A corpus profile must define any claimed novelty relative to acquisition experience, for example whether the exact start–goal pair or route was absent from acquisition. Novelty is not inferred from different record identifiers.

### 7.5 Acquisition diagnostics

Acquisition-coverage diagnostics may be retained as privileged metadata when required to validate a declared novelty policy or support post-hoc analysis.

## 8. Oracle and target semantics

Prospect repeats the route mathematics here so that the specification remains independently readable. Matched Routebind and Prospect cases must nevertheless use identical oracle semantics.

### 8.1 Canonical route set and cost

Let $\mathcal V$ be the complete finite set of valid simple accepting routes for query $q'$. With unit-cost physical transitions and zero-cost semantic acceptances,

$$
C(\Pi)=\left|I_{\mathrm{move}}(\Pi)\right|,
$$

$$
C^*=\min_{\Pi\in\mathcal V}C(\Pi),
\qquad
\mathcal V^*=\left\{\Pi\in\mathcal V\mid C(\Pi)=C^*\right\}.
$$

### 8.2 Route projections

For $\Pi=(\xi_0,\ldots,\xi_L)$ with $\xi_r=(g'_r,o_r)$, let $R(\Pi)$ be the ordered decoded positions visited by the route and $W(\Pi)$ the decoded positions at which semantic acceptance occurs.

### 8.3 Route-cost weighting

Define

$$
\Delta(\Pi)=C(\Pi)-C^*.
$$

For $\lambda_{\mathrm{valid}}\in[0,1]$,

$$
w_\lambda(\Pi)
=
\begin{cases}
1, & \Delta(\Pi)=0,\\
\lambda_{\mathrm{valid}}^{\Delta(\Pi)}, & \Delta(\Pi)>0.
\end{cases}
$$

### 8.4 Canonical trajectory and waypoint targets

For $g'\in R(\Pi)$, let $d_R(g',\Pi)$ count physical transitions completed before the first occurrence of $g'$. For $g'\in W(\Pi)$, let $d_W(g',\Pi)$ count semantic acceptances completed up to and including the first acceptance at $g'$.

For $\gamma_{\mathrm{space}},\gamma_{\mathrm{semantic}}\in(0,1]$,

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

The corpus channels `target_trajectory` and `target_waypoint` materialize these fields. Model predictions are denoted $\hat f_{\mathrm{traj}}$ and $\hat f_{\mathrm{wp}}$.

A deterministic enumeration limit may truncate $\mathcal V$ only under the same declared semantics used by the matched Routebind control. When truncation occurs, the enumeration order, retained-subset rule, limit, and truncation status are identity-bearing target-generation semantics.

### 8.5 Ground-truth independence from memory quality

Oracle routes and target fields are computed from decoded topology, $\phi$, $D_{\mathrm{obs}}$, and the decoded query $q'$, never from the acquired-memory payload. A degraded, ablated, or incorrect memory state must not alter ground truth.

### 8.6 Routebind equivalence

For matched cases with identical decoded environment, semantic law, decoded query, enumeration protocol, and target parameters, Routebind and Prospect must produce identical route truth and target fields. Their scientific difference is the model-visible source of environment-specific spatial information.

## 9. Logical corpus contract

### 9.1 Record fields

| Field                 |                         Required | Scope / semantic shape      | Visibility | Role              | Meaning                                                              |
| --------------------- | -------------------------------: | --------------------------- | ---------- | ----------------- | -------------------------------------------------------------------- |
| `record_id`           |                              yes | scalar                      | metadata   | identifier        | Prospect query identity                                              |
| `environment_id`      |                              yes | scalar                      | metadata   | identifier        | exact composed environment                                           |
| `memory_entry_id`     |                              yes | scalar                      | metadata   | input reference   | corpus-local acquired-memory entry                                   |
| `start_position`      |                              yes | decoded position identity   | public     | task query        | $g'_{\mathrm{start}}$; binding source for the model's start cue      |
| `goal_observation_id` |                              yes | scalar categorical identity | public     | task query        | $o_{\mathrm{goal}}$; binding source for the model's sensory goal cue |
| `target_trajectory`   |                              yes | decoded spatial domain      | target     | primary target    | $f_{\mathrm{traj}}^*$                                                |
| `target_waypoint`     |                              yes | decoded spatial domain      | target     | structural target | $f_{\mathrm{wp}}^*$                                                  |
| `optimal_cost`        |                              yes | scalar                      | privileged | oracle metadata   | $C^*$                                                                |
| `spatial_mask`        | when fixed padded output is used | storage/output domain       | technical  | mask              | valid output slots only                                              |

`memory_entry_id` is storage metadata; the semantic input is the resolved corpus-local acquired-memory content. The public query fields define $q'$ and must be encoded by a binding without exposing decoded topology or physical goal support.

### 9.2 Corpus-local memory resource

Each memory entry must resolve entirely within the committed Prospect corpus and identify:

- local memory entry ID;
- memory schema/reference required by the binding;
- source acquisition/provenance identity;
- exact compatible composed environment identity;
- integrity-protected serialized memory payload or equivalent local representation.

### 9.3 Environment validation resource

The corpus retains sufficient privileged environment context to validate route truth and memory compatibility without parent access. This context is not automatically model-visible.

### 9.4 Natural and storage domains

Padding is outside the natural environment and must not be conflated with walls or traversable states. A public technical mask may identify valid output slots only; it must not encode traversability, adjacency, observation identity, goal location, or route support.

## 10. Split and sampling semantics

### 10.1 Environment-level split grouping

Prospect split boundaries are defined at the composed-environment level. All Prospect queries generated from one topology–ObsField environment belong to the same split:

$$
\operatorname{environment}(q_i)=\operatorname{environment}(q_j)
\;\Longrightarrow\;
\operatorname{split}(q_i)=\operatorname{split}(q_j).
$$

This prevents leakage through shared topology, observation–position assignments, or environment-specific acquired memory.

### 10.2 Semantic-law scope

The hidden semantic graph $D_{\mathrm{obs}}$ and bijection $\beta$ are corpus-level task law shared across splits, exactly as in the matched Routebind control.

### 10.3 Memory split semantics

A Prospect record may use only a memory entry whose acquisition inputs and provenance correspond to the same environment and satisfy the split/novelty policy declared for that record. Because memory is environment-specific, an environment's memory entries cannot be reused to construct queries in another split.

The corpus must validate this relationship from explicit lineage or acquisition diagnostics rather than infer safety from a storage label.

### 10.4 Matched Routebind comparison

A Prospect corpus intended for controlled comparison with Routebind should use the same:

- composed environments;
- environment-level split assignment;
- semantic graph and binding;
- start/goal query identities;
- oracle enumeration protocol and limits;
- target protocol and target hyperparameters.

Only the model-visible source of environment-specific spatial information should differ.

## 11. Determinism and task identity inputs

Prospect-specific semantic identity inputs include:

- topology/ObsField selection and composition;
- local memory source selection and memory payload identity;
- acquisition protocol/checkpoint qualification requirements;
- semantic graph and observation-binding law;
- query-generation protocol;
- target/oracle protocol;
- novelty policy;
- task randomness roles.

Changing a memory source or payload changes Prospect corpus identity even when oracle targets remain unchanged.

## 12. Validation and invariants

### PR-COMP-001 — Spatial-domain compatibility

Every Prospect environment uses compatible topology and ObsField records.

### PR-COMP-002 — Complete bijective semantic binding

The declared $\beta$ is a bijection between the complete semantic graph node domain used by the corpus and the complete task observation vocabulary $Obs$.

### PR-MEM-001 — Local memory availability

Every record's `memory_entry_id` resolves to exactly one corpus-local memory entry. No external memory-bank lookup is required for normal corpus use.

### PR-MEM-002 — Exact environment compatibility

Every memory entry identifies and matches the exact topology, ObsField, vocabulary, coordinate, and acquisition semantics required by its Prospect environment.

### PR-MEM-003 — Acquisition precedence

The memory entry was produced before the Prospect query and without query oracle targets or query-specific route labels.

### PR-MEM-004 — Ground-truth independence

Oracle targets depend on authoritative environment and semantic-law truth, not on the acquired-memory payload.

### PR-REC-001 — Public information boundary

No model-facing Prospect input exposes decoded traversability, spatial adjacency, complete per-position observation identities, or physical goal-location support.

### PR-REC-002 — Goal-cue semantics

The public task query contains $o_{\mathrm{goal}}$; no `goal_flag`, $C_{\mathrm{goal}}$, or equivalent physical goal-location mask is a Prospect input.

### PR-REC-003 — Technical-mask non-leakage

Any public storage/output mask identifies only valid output slots. It must not encode traversability, adjacency, observation identity, goal location, or route support.

### PR-ORACLE-001 — Routebind equivalence

For a Prospect and Routebind case with identical environment, semantic law, start, goal, and oracle protocol, canonical oracle truth and targets are identical.

### PR-SPLIT-001 — Environment-level grouping

Every query and every compatible acquired-memory entry for one composed environment belong to one and only one corpus split.

### PR-SPLIT-002 — Acquisition/query policy

Every record satisfies the declared acquisition-novelty policy within that environment-level split.

### PR-CORPUS-001 — Self-contained validation

Memory, privileged environment truth, semantic law, binding, and required task channels are resolvable from corpus-local resources.

## 13. Metrics and evaluation semantics

### 13.1 Primary behavioral metric

Prospect uses `valid_semantic_spatial_route_rate` with the same structural definition as Routebind.

### 13.2 Optimality metric

For valid routes:

$$
\rho_{\mathrm{cost}}
=
\frac{C(\hat R)}{C^*}.
$$

### 13.3 Representational metrics

The primary field-level metrics include balanced trajectory-field error and balanced waypoint-field error against $f_{\mathrm{traj}}^*$ and $f_{\mathrm{wp}}^*$; ordinary unbalanced field errors may be reported as calibration diagnostics.

### 13.4 Informative memory-dependence diagnostics

Prospect-specific diagnostics may include controlled memory perturbations such as:

- replacing the correct memory with an environment-incompatible memory;
- zeroing or ablating the memory representation;
- comparing performance across acquisition coverage levels.

These diagnostics require experiment/binding support and do not alter task ground truth.

### 13.5 Interpretation

A performance advantage over an appropriate memory ablation, together with matched Routebind controls, supports causal reliance on acquired environment-specific memory. Performance alone does not establish which internal memory features carry the required topology or observation bindings.

## 14. Binding boundary

Prospect defines the abstract `acquired_environment_memory` input role and its compatibility semantics, not a universal memory tensor schema.

A Prospect binding may define:

- how a corpus-local memory entry is decoded;
- model-family-specific memory tensors or objects;
- memory retrieval operations;
- start/goal cue encoding;
- spatial output representation;
- recurrent deliberation.

A binding must not expose privileged topology/observation fields that Prospect v1 withholds.

## 15. Open issues

- A project-level reusable memory-artifact abstraction should be introduced only if acquired memory must be independently published and consumed by multiple workflows. Prospect v1 itself requires only corpus-local materialization of its needed memory entries.
- The initial acquisition profile must define memory qualification and query-novelty evidence precisely.
- The first matched Routebind/Prospect corpus pair must freeze one shared graph-node-to-observation binding protocol and one shared query/oracle protocol.
