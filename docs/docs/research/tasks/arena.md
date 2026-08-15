---
title: Arena v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Arena v1

## Normative summary

`arena/v1` defines sequential spatial replay for observation prediction and environment-specific memory acquisition in composed spatial environments.

One corpus record represents one complete replay episode over one compatible topology and observation-field composition.

Arena consumes one raster-topology record and one compatible ObsField record.
It generates an initial state and movement trajectory, resolves the observation encountered at every visited position, and materializes a self-contained replay episode containing the semantic information required for prediction and evaluation.

Arena owns episode generation, task-level action semantics, temporal alignment of observations and actions, revisit truth, public replay information, observation targets, and Arena-specific task metrics.
Model-specific prediction pathways and latent-state diagnostics belong to the applicable binding/model evaluation contract.
It does not own topology generation, observation-field generation, generic artifact or corpus mechanics, model architecture, model-native recurrent-state representation, or experiment policy.

A conforming Arena corpus also satisfies the generic `DataArtifact` and `TaskCorpus` contracts.

## 1. Purpose and scientific claim

### 1.1 Computational objective

Arena provides a temporally ordered sequence of environment observations and actions from which a model may acquire environment-specific state and produce observation predictions.

At acquisition/replay step $t$, the task supplies the experienced categorical observation

$$
o_t=\phi(g'_t),
$$

and the discrete action $a_t$ associated with that transition step.
For $t>0$, $a_t$ is the action that produced $g'_t$ from $g'_{t-1}$ under the declared movement semantics.
Step $t=0$ uses the declared initialization-action convention.

The task target at step $t$ is the experienced observation $o_t$.
Arena does not prescribe the internal computational pathway by which a model predicts or reconstructs that observation.

In the reference Arena–TEM evaluation, the same replay supports several model-specific prediction pathways with different access to the current sensory observation, including posterior, sensory-recall, and structural-prior/path-integration predictions.
Those pathway-specific information restrictions and metrics are properties of the Arena–TEM binding/model evaluation, not different Arena corpus records.

### 1.2 Scientific question

Arena tests whether a system can acquire and use structured environment-specific state from sequential action-observation experience, with revisit prediction providing the primary behavioral probe of environment-specific recall.

### 1.3 Intended comparisons

Arena supports comparisons including:

- first visits versus revisits within one episode;
- different topology families satisfying the same raster-topology capabilities;
- different ObsField realizations over compatible ambient domains;
- different acquisition or walk policies when represented by distinct corpus releases or experiment conditions.

### 1.4 Non-claims

Success on Arena does not by itself establish:

- shortest-path planning;
- semantic graph reasoning;
- prospective route construction;
- allocentric representation in any particular model-internal coordinate system;
- that a specific biological mechanism is implemented.

Those claims require model-specific analyses or other tasks.

## 2. Scope and ownership

### 2.1 Task-owned semantics

Arena defines:

- one replay episode as the logical record;
- composition of topology and observation-field parents;
- episode initialization;
- walk generation;
- Arena action semantics, including optional task-level `STAY`;
- temporal alignment of observations and actions;
- revisit classification;
- public replay channels and target channels;
- task-specific randomness roles;
- task-specific validation and metrics.

### 2.2 Excluded semantics

Arena does not define:

- raster-topology generation or normalization;
- ambient observation-field assignment;
- generic manifest, lineage, digest, release, or publication rules;
- model architecture or recurrent-state structure;
- tensor batching or model-native tokenization;
- optimizer, loss weighting, curriculum, or training schedule;
- repository-local scripts or CLI option spelling.

### 2.3 Authoritative dependencies

| Concern                             | Authoritative specification                     |
| ----------------------------------- | ----------------------------------------------- |
| Generic generated-data contract     | `data-artifacts`                                |
| Generic task-corpus contract        | `corpora`                                       |
| Traversability and movement         | `raster-topology/v1`                            |
| Persistent categorical observations | `categorical-field/v1`                          |
| Task semantics                      | this document                                   |
| Task-to-model encoding              | applicable `InputAdapter`/`OutputAdapter`, § 14 |

## 3. Conceptual model

### 3.1 Notation and composed environment

Arena defines its mathematical symbols locally.
Primed structural symbols denote decoded environment-level quantities; hats denote predictions; stars denote oracle/reference targets; and $p$ is reserved for the model-internal conjunctive representation rather than a physical position.

For one compatible topology record and ObsField record, let

$$
G' \quad \text{be the decoded ambient spatial domain},
$$

$$
G'_{\mathrm{free}} \subseteq G' \quad \text{be the traversable positions},
$$

$$
E'_{\mathrm{spatial}}
\subseteq
G'_{\mathrm{free}} \times G'_{\mathrm{free}}
\quad \text{be the valid physical-transition relation},
$$

and let $Obs$ be the categorical observation vocabulary.
The composed observation assignment is

$$
\phi : G'_{\mathrm{free}} \rightarrow Obs.
$$

The topology supplies $G'_{\mathrm{free}}$ and $E'_{\mathrm{spatial}}$.
The compatible ObsField supplies the ambient observation assignment from which $\phi$ is obtained by restriction to traversable positions.
This composition is task context, not a new substrate artifact.

### 3.2 Episode

An Arena episode of length $T$ consists of decoded positions, observations, and actions

$$
(g'_0,\ldots,g'_{T-1}),
\qquad
(o_0,\ldots,o_{T-1}),
\qquad
(a_0,\ldots,a_{T-1}),
$$

with

$$
g'_t \in G'_{\mathrm{free}},
\qquad
o_t = \phi(g'_t).
$$

For $t>0$, $a_t$ denotes the action whose application at $g'_{t-1}$ produces $g'_t$.
The initialization value $a_0$ is defined by the Arena action protocol and does not imply a topology self-loop.

### 3.3 Revisit

Step $t$ is a physical revisit exactly when its decoded position occurred previously in the same episode:

$$
\operatorname{revisit}(t)
\iff
\exists j<t:\; g'_j=g'_t.
$$

Observation equality alone does not imply a revisit because $\phi$ may assign the same observation identity to several positions.

## 4. Information regime

### 4.1 Public replay information

For each valid replay step `t`, Arena makes available semantically:

- current observation identity $o_t$;
- current transition action $a_t$ under the episode indexing convention;
- episode-boundary information sufficient to initialize/reset recurrent state;
- validity information required to distinguish real replay steps from storage padding.

Arena does not expose decoded coordinates, topology-state identifiers, wall maps, or movement-valid masks as ordinary task inputs.

### 4.2 Target information

The observation associated with the current replay step is also the task-level prediction/reconstruction target:

$$
y_t^* = o_t.
$$

The corpus channel `observation` materializes this target sequence.

The fact that $o_t$ is present in the replay does not imply that every model-specific prediction pathway may use it directly.
A binding/model evaluation may construct a restricted prediction pathway, such as the structural-prior/path-integration pathway, in which the current observation is deliberately withheld from that particular prediction.

`is_revisit[t]` is task evaluation truth used for metric stratification and is not a sensory observation input.

### 4.3 Privileged information

The corpus may retain corpus-local task context required for validation or declared analysis, including:

- decoded position trajectory $g'_t$ or an equivalent topology-state trajectory;
- environment reference within a corpus-local environment table;
- complete composed traversability and observation realization when required by declared analyses.

Privileged spatial context must not become an ordinary model input unless a different task version explicitly changes the information regime.

### 4.4 Withheld task information

Arena withholds from the ordinary replay interface:

- decoded physical coordinates or topology-state identity as model features;
- topology geometry and wall maps;
- movement-valid masks beyond the experienced action sequence;
- future observations and actions;
- revisit truth for use as a predictive cue.

### 4.5 Pathway-specific restrictions

Arena defines the replay sequence and task truth, not model-internal prediction pathways.
A task–model binding or evaluation regime may restrict which public replay quantities a particular prediction pathway may consume, provided that the restriction does not change the underlying episode, target observation, or revisit truth.

## 5. Unit of record and shared task context

### 5.1 Unit of record

One Arena record represents:

> one complete replay episode over one composed topology–ObsField environment.

Batching several episodes is a physical or binding concern and does not change the logical record unit.

### 5.2 Record discriminators

Task-semantic discriminators include:

- topology parent record;
- ObsField parent record;
- episode realization index;
- walk protocol;
- task-level action policy;
- episode-length policy;
- Arena randomness derivation.

### 5.3 Shared task context

A corpus may deduplicate repeated environment information through a corpus-local environment table referenced by multiple episode records.

One environment entry may contain the corpus-local representation required to resolve:

- topology-to-ambient-position mapping;
- traversability context needed by validation;
- restricted observation assignment;
- vocabulary identity.

Environment entries are not model-visible merely because they are corpus-local.

## 6. Parent roles and composition

### 6.1 Parent roles

| Role                | Required | Required contract      | Task use                                        |
| ------------------- | -------: | ---------------------- | ----------------------------------------------- |
| `topology`          |      yes | `raster-topology/v1`   | movement structure and physical state identity  |
| `observation_field` |      yes | `categorical-field/v1` | persistent observation at each ambient position |

Arena depends on topology capabilities rather than a concrete topology family.
DungeonGen and Maze-ND are both admissible when their records satisfy the required capabilities.

### 6.2 Required topology capabilities

Arena v1 requires:

```text
topology_kind: raster
coordinate_system: row-column
movement_kind: grid4
directed: false
edge_cost_kind: unit
```

Arena does not require topology-level self-loops.
`STAY`, when enabled by the episode protocol, is task-owned.

### 6.3 Parent exclusions

Arena must not assume that:

- the topology parent contains observations;
- the ObsField parent contains traversability;
- the topology parent contains task starts, goals, or trajectories;
- an observation ID identifies a physical position;
- topology-state IDs equal ambient-position IDs unless the shared contracts establish that mapping explicitly.

### 6.4 Compatibility relation

A topology record and ObsField record are compatible only when their complete ambient-domain semantics identify the same position space, including coordinate convention, natural extent, canonical position identity, enumeration, movement geometry, and boundary policy.

Every topology state must map to exactly one valid ambient position in the ObsField domain.

### 6.5 Composition procedure

For each selected pair:

1. validate topology and ObsField ambient-domain compatibility;
2. resolve each topology state to one ambient position;
3. restrict the ObsField assignment to traversable topology positions;
4. validate all resulting observation IDs against the declared vocabulary;
5. construct corpus-local environment context sufficient for episode generation and validation;
6. generate Arena episodes.

### 6.6 Rejection conditions

The pair is rejected if any required domain semantic differs, any topology state lacks a valid ambient position, the vocabulary declaration is invalid, or the composed environment violates an Arena requirement.

## 7. Task generation

### 7.1 Episode initialization

The episode protocol selects one valid decoded position $g'_0\in G'_{\mathrm{free}}$ using record-addressable deterministic randomness or another explicitly declared deterministic policy.

The initial observation is

$$
o_0=\phi(g'_0).
$$

### 7.2 Task action domain

Arena v1 uses the canonical grid4 movement actions supplied by the topology contract and may additionally define:

```text
STAY
```

`STAY` leaves the topology state unchanged and is an Arena action, not a topology edge.

The resolved episode protocol must state whether `STAY` may occur only at initialization or also during the generated walk.

### 7.3 Walk protocol

A walk protocol must define:

- action-selection semantics;
- treatment of invalid movement actions;
- whether `STAY` is selectable;
- episode-length rule;
- termination or truncation;
- deterministic randomness derivation.

Named policies such as angle-biased or uniform-valid walks are protocols or presets, not changes to Arena task semantics when they preserve the same information regime and record meaning.

### 7.4 Temporal canonicalization

For a generated trajectory $(g'_0,\ldots,g'_{T-1})$, the builder materializes the observation relation

$$
\texttt{observation}[t] = \phi(g'_t),
$$

and an action sequence aligned so that, for $t>0$, `action[t]` is the action producing $g'_t$ from $g'_{t-1}$.
`action[0]` is the declared initialization action or sentinel.

The action convention is part of Arena v1 task semantics.
A binding may shift or re-encode the sequence for a model-native recurrent API, but must preserve the same transition alignment.

### 7.5 Revisit truth

`is_revisit[t]` is computed from the complete prefix of physical states and is valid for all `t`.
It is independent of observation repetition.

### 7.6 Retry and exhaustion

If an episode protocol can reject candidate starts or trajectories, it must define deterministic attempt identity, attempt budget, and exhaustion behavior.
Exhaustion is explicit failure; it must not silently substitute a different logical episode identity.

## 8. Oracle and target semantics

Arena does not require a planning oracle.
For each valid replay step $t$, the authoritative task truth consists of

$$
g'_t \quad \text{(privileged decoded position)},
$$

$$
o_t = \phi(g'_t) \quad \text{(experienced observation and task target)},
$$

and

$$
\operatorname{revisit}(t)
\iff
\exists j<t:\;g'_j=g'_t.
$$

Observation prediction is evaluated against $o_t$.
The task does not prescribe the internal pathway used to produce a compatible prediction.
Pathway-specific outputs and diagnostics belong to the applicable binding/model evaluation contract.

## 9. Logical corpus contract

### 9.1 Episode record fields

One logical episode record contains or resolves at least:

| Field                 | Required | Scope / semantic shape      | Visibility                     | Role         | Meaning                                                    |
| --------------------- | -------: | --------------------------- | ------------------------------ | ------------ | ---------------------------------------------------------- |
| `record_id`           |      yes | scalar                      | metadata                       | identifier   | episode identity                                           |
| `environment_id`      |      yes | scalar                      | metadata                       | identifier   | corpus-local composed environment                          |
| `observation`         |      yes | `(T,)`                      | public/target by temporal role | sequence     | observation encountered at each visited state              |
| `action`              |      yes | `(T-1,)`                    | public                         | sequence     | action between consecutive visited states                  |
| `episode_start`       |      yes | scalar or derivable         | public control                 | boundary     | episode reset condition                                    |
| `is_revisit`          |      yes | `(T,)`                      | privileged                     | metric truth | physical-state revisit indicator                           |
| `trajectory_position` |      yes | `(T,)` logical position IDs | privileged                     | validation   | physical trajectory in canonical ambient-position identity |

A physical serialization may use padded fixed-width arrays, but padding is not part of the logical episode semantics.

### 9.2 Shared environment resource

A corpus-local environment resource must provide enough information to validate observations and trajectories without resolving parent artifacts.
It may deduplicate information shared by several episodes.

At minimum it resolves:

- environment identity;
- natural ambient-domain declaration;
- vocabulary identity and cardinality;
- traversable-position set or equivalent topology representation;
- observation assignment needed for traversable positions.

### 9.3 Sentinels and padding

If physical serialization pads variable-length episodes, the corpus schema must distinguish padding from valid values through an explicit valid-step mask or length field.
Sentinel values must never be interpreted as semantic observation, action, or position identities.

## 10. Split and sampling semantics

### 10.1 Parent split use

Arena follows the generic parent-to-corpus split rule where parents declare intrinsic splits.

ObsField and some topology substrates may define no intrinsic experimental splits.
For such parents, the Arena corpus specification or named corpus profile owns assignment of reusable records to task splits and must record that policy explicitly.

### 10.2 Multi-parent pairing

Pairing of topology and ObsField records must be deterministic and compatibility-aware.
The policy may deliberately hold one factor fixed while varying the other, but the policy is part of the corpus build semantics.

### 10.3 Leakage and novelty

Named Arena corpora must state whether train/validation/test novelty applies to:

- topology realization;
- ObsField realization;
- topology–ObsField combination;
- episode realization.

No universal novelty policy is imposed by Arena v1.

## 11. Determinism and task identity inputs

### 11.1 Randomness roles

Arena randomness roles may include:

- topology/ObsField pairing;
- initial-state selection;
- walk action selection;
- retry selection where applicable.

### 11.2 Deterministic derivation

Episode generation must be record-addressable and invariant to worker count, scheduling, sharding, and physical serialization order.

### 11.3 Task-semantic identity inputs

Arena-specific identity-affecting semantics include:

- parent selection and composition policy;
- walk protocol and semantic parameters;
- task-level `STAY` policy;
- episode-length policy;
- episode realization indexes;
- generation seed roles;
- split and novelty policy;
- logical channel contract.

Generic build-input identity and artifact fingerprints remain framework-owned.

## 12. Validation and invariants

### AR-COMP-001 — Parent-domain compatibility

Every episode environment derives from one topology and one ObsField record with compatible ambient-domain semantics.

### AR-COMP-002 — Complete observation resolution

Every traversable topology state used by an Arena episode resolves exactly one observation in the declared vocabulary.

### AR-REC-001 — Valid trajectory

Every consecutive physical state pair is related by the declared action according to topology movement semantics or by a permitted task-level `STAY`.

### AR-REC-002 — Temporal alignment

For every step $t>0$, $a_t$ corresponds exactly to the declared transition from $g'_{t-1}$ to $g'_t$, and $\texttt{observation}[t]=\phi(g'_t)$.

### AR-REC-003 — Revisit correctness

`is_revisit[t]` is true if and only if the same physical state occurred at an earlier episode step.

### AR-REC-004 — Spatial-privilege exclusion

Decoded physical identity, topology geometry, movement-valid structure, future replay content, and revisit truth are not ordinary public Arena inputs.
Current $o_t$ is part of the replay; any pathway-specific restriction on using it is binding/model-evaluation semantics.

### AR-REC-005 — Vocabulary validity

Every semantic observation value lies in the record's declared observation vocabulary.

### AR-CORPUS-001 — Local replay completeness

Every required episode and environment channel is resolvable from corpus-local resources without parent access.

### AR-SPLIT-001 — Declared split policy

Every episode and contributing parent record conforms to the corpus's declared split and novelty policy.

## 13. Metrics and evaluation semantics

### 13.1 Primary metric: revisit-conditioned observation accuracy

The primary Arena task metric is observation-prediction accuracy over replay steps whose decoded physical position is a revisit:

$$
A_{\mathrm{obs}}^{\mathrm{rev}}
=
\frac{N_{\mathrm{correct,rev}}}{N_{\mathrm{rev}}}.
$$

This corresponds to the revisit-conditioned observation-prediction quantity used by the formal research evaluation.
The metric is undefined for an evaluation set with zero revisit targets; an evaluator must report the empty denominator rather than silently substitute a value.

### 13.2 Secondary task metrics

Task-level supporting quantities include:

- observation accuracy over all evaluated replay steps;
- `correct_all`, `count_all`;
- `correct_revisit`, `count_revisit`;
- first-visit accuracy when useful diagnostically.

Model/binding-specific Arena–TEM evaluation may additionally report the pathway metrics `A_post`, `A_rec^rev`, and `A_PI^rev`.
These are not generic Arena task channels because they refer to particular TEM inference/retrieval pathways.

### 13.3 Aggregation

Count-based sufficient statistics are summed across batches or distributed workers before accuracy is derived.

### 13.4 Interpretation

Higher `A_obs^rev` supports the behavioral claim that the evaluated system can recover environment-specific sensory–spatial information at previously experienced locations.
It does not by itself identify which internal pathway or representation produced that recovery.

## 14. Binding boundary

Arena defines the replay sequence $(o_t,a_t)$, episode boundaries, decoded trajectory truth used for validation, observation targets, and revisit truth.

An `InputAdapter` (`docs/docs/framework/adapters/index.md`) may define:

- categorical/sensory encoding of $o_t$;
- model-native action encoding;
- batching, padding, and masks.

An `OutputAdapter` may define:

- one or more observation-prediction pathways;
- pathway-specific access restrictions and diagnostic outputs.

Recurrent unrolling and state reset belong to the experiment's training protocol, not to either adapter.

For the Arena–TEM binding, posterior and sensory-recall pathways may use the current encoded observation according to the TEM model contract, while the structural-prior/path-integration pathway must not use the current observation.
The resolved binding must not expose decoded topology or privileged spatial identity beyond the Arena task contract.

## 15. Open issues

- The shared `raster-topology/v1` contract must be finalized before Arena can become `specified`.
- The initial named Arena corpus must choose its walk protocol, episode-length policy, and `STAY` policy.
- The initial split/novelty policy for independent topology and ObsField pools must be declared by the concrete corpus profile.
- Any landmark or shiny-cue semantics require a separately defined reusable observation capability or later Arena version; they are not part of Arena v1.
