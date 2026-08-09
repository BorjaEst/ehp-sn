---
title: Research tasks
authority: normative
document_status: draft
api_stability: provisional
---

# Research tasks

This section defines the scientific task specifications used by EHP-SN research experiments.

A task defines a scientific problem. It owns public information, targets, privileged or oracle-only truth, task-case or episode semantics, task-specific validity, and task-level scoring. It does not own model architecture, task-to-model encoding, generic data-artifact mechanics, or substrate generation.

The framework-level task/model/binding ownership boundary remains authoritative. Task corpora additionally conform to the generic generated-data and corpus contracts.

## Task-document contract

Every normative task specification should answer six questions unambiguously:

1. What does one logical task record represent?
2. What information is public to the model, privileged, targeted, or withheld?
3. Which substrate or upstream roles are required, and how are they composed?
4. How are valid cases or episodes generated?
5. What is the canonical truth against which predictions are judged?
6. What scientific claim can the resulting metrics support?

"One logical task record" is documentation vocabulary describing a task's primary independently enumerable case, episode, or query unit — for example, Arena's replay episode, MazeHard's start–goal problem, or Routebind's start–semantic-goal query. Every task specification must define that unit locally and unambiguously. The phrase does not impose a repository-wide cardinality constraint: it does not require that all task-owned information be stored in one physical record, and it does not forbid corpus-level shared context, auxiliary tables, or other independently addressed resources, which Routebind and Prospect both use for their corpus-level semantic-law and memory resources.

Task specifications should reference, not restate, generic framework mechanics for manifests, release numbering, digests, fingerprints, staging, publication, corpus indexing, and generic lineage semantics.

They should also avoid model-specific tensor layouts, concrete Python helper names, CLI spelling, repository-local script paths, optimizer settings, and experiment schedules unless those details are themselves part of the scientific task meaning.

## Common normative structure

Task documents use the following common structure:

1. Purpose and scientific claim
2. Scope and ownership
3. Conceptual model
4. Information regime
5. Unit of record and shared task context
6. Parent roles and composition
7. Case, query, or episode generation
8. Oracle and target semantics
9. Logical corpus contract
10. Split and sampling semantics
11. Determinism and task identity inputs
12. Validation and invariants
13. Metrics and evaluation semantics
14. Binding boundary
15. Open issues

A subsection that does not apply may be omitted or replaced by a precise non-applicability statement. The structure is intended to expose task semantics, not to force boilerplate.

Normative clauses use **must** and **must not** for requirements and **may** for permitted behavior. **Should** is reserved for explicitly non-mandatory recommendations and should be avoided where a requirement or permission can be stated precisely.

## Mathematical notation discipline

Each task specification is mathematically self-contained and defines every symbol it uses. Task documents do not depend on a separate shared mathematical-background page.

When choosing symbols and formal task semantics, task specifications follow the conventions established by the project formal research definition (`main.tex` in the research manuscript source). Each task nevertheless defines the variables it uses locally so that the task file remains independently readable:

- for paired EC–HPC representations, a primed symbol such as $g'$ or $x'$ denotes a decoded/environment-level representation, while the corresponding unprimed symbol such as $g$ or $x$ denotes a latent/model-internal representation;
- directly observed categorical identities such as $o$ and $o_{\mathrm{goal}}$ do not use the primed/unprimed distinction;
- hats denote model predictions, for example $\hat f$;
- stars denote oracle/reference targets, for example $f^*$;
- uppercase symbols denote domains, sets, collections, relations, and graphs;
- lowercase symbols denote individual states, observations, and vectors;
- $p$ is reserved for the conjunctive representation and must not denote a physical position.

A task may introduce additional local symbols when its problem requires them, but it must not redefine an established project symbol with an incompatible meaning.

## Common data architecture

The current research data architecture separates task-neutral substrates from processed task corpora:

```text
task-neutral substrate artifacts
    data/interim/<family>/<variant>/v<N>/

        topology substrates
        observation-field substrates
        graph substrates

                ↓ task-owned selection and composition

self-contained task corpora
    data/processed/<task>/<corpus>/v<N>/
```

A task builder may compose several independent substrates. The resulting composition is task-corpus build context and does not become a new substrate merely because several tasks use similar composition logic.

A committed task corpus must be self-contained for its declared normal consumers. Parent artifacts remain provenance and build inputs rather than runtime dependencies.

## Substrate roles

### Raster topology

DungeonGen and Maze-ND are producers of the shared [`raster-topology/v1`](../../framework/contracts/topology/raster-topology-v1.md) contract.

Tasks should depend on required topology capabilities rather than on concrete family identity unless a scientific experiment intentionally selects a family.

Topology owns traversability and movement. It does not own observation assignment, task starts, task goals, routes, solutions, or task-level `STAY`.

### Observation field

ObsField independently defines a total categorical observation assignment over one ambient spatial domain.

Topology and ObsField are peer substrate inputs. A task builder validates ambient-domain compatibility and restricts the observation field to traversable topology positions.

Observation vocabulary identity must not be inferred from cardinality or integer range alone.

### Directed semantic graph

Dagflow defines reusable directed graph structure over graph-local categorical node IDs.

Dagflow node IDs are not observation IDs. Any task that gives graph nodes observation semantics must create an explicit task-owned graph-node-to-observation binding.

## Current task catalogue

| Reference | Problem | Primary parent roles | Information regime | Component maturity |
| --- | --- | --- | --- | --- |
| [`arena/v1`](arena.md) | sequential spatial experience and observation-prediction supervision | raster topology + ObsField | replay exposes observations/actions; topology remains privileged | Planned |
| [`maze-hard/v1`](mazehard.md) | fully observed shortest-route reasoning | raster topology | full maze topology/start/goal visible | Planned |
| [`routebind/v1`](routebind.md) | visible spatial + hidden semantic route binding | raster topology + ObsField + Dagflow source | topology/observations visible; semantic law hidden | Planned |
| [`prospect/v1`](prospect.md) | memory-conditioned semantic-spatial routing | raster topology + ObsField + Dagflow source + acquired memory source | decoded topology, observation placement, and physical goal locations withheld | Planned |

`Component maturity` reflects the component as a whole (specification, implementation, and validation evidence together), following `planned → specified → implemented → validated → reference`. All four task specifications are currently `document_status: draft`, so their component maturity is `planned`.

## Scientific relationship among the four tasks

The four tasks are intentionally not interchangeable. They isolate different capabilities:

```text
Arena
    sequential experience
    -> acquire/use environment-specific state

MazeHard
    fully visible maze
    -> spatial reasoning without acquisition requirement

Routebind
    visible spatial structure + hidden reusable semantic law
    -> joint spatial-semantic reasoning

Prospect
    acquired memory instead of visible spatial structure
    + semantic goal observation cue
    + same hidden semantic law
    -> memory-conditioned joint reasoning and goal localization
```

Routebind and Prospect should use matched oracle semantics so that their principal difference is the source of environment-specific spatial information rather than a different definition of correctness.

## Task and binding boundary

A task defines semantic inputs and outputs. A binding maps those semantics to one model family.

Bindings may own:

- flattening and tokenization;
- model-native dtypes and batch dimensions;
- padding tensors;
- recurrent unrolling;
- memory-object decoding;
- decoder/logit layout;
- integration modules and binding-specific losses.

Bindings must not change:

- which information is public or withheld;
- target meaning;
- oracle truth;
- task validity;
- split semantics;
- metric meaning.

Consequently, particular token IDs, ignore-label integers, model-native memory layouts, and concrete loss weighting belong to bindings or named reproduction profiles unless a task specification explicitly makes them part of the scientific problem. A fixed spatial size may belong to a named benchmark reproduction profile even when the task family itself admits other compatible extents.

## Task and experiment boundary

Task specifications define admissible scientific task semantics. Concrete experiment or corpus profiles may choose:

- record counts;
- difficulty distributions;
- named sampling presets;
- acquisition thresholds;
- optimizer/training schedules;
- active auxiliary losses;
- ablations;
- checkpoint-selection rules.

A choice belongs in the task specification only when changing it changes what one task case means or what constitutes correct behavior.

## Status policy

A task should remain `draft` while any blocking issue remains unresolved in its semantic contract, parent compatibility, information regime, oracle truth, or self-contained corpus requirements.

`Specified` should mean that the task semantics and boundaries are sufficiently complete to implement independently and test for conformance. It does not imply that an implementation or scientific result already exists.

The four tasks in this section remain `draft` until their shared dependencies and named initial corpus profiles are finalized.

## Related specifications

- [`Data artifacts`](../../framework/data-artifacts.md)
- [`Corpora`](../../framework/corpora.md)
- [`DungeonGen v1`](../substrates/dungeongen-v1.md)
- [`Maze-ND v1`](../substrates/maze-nd-v1.md)
- [`ObsField v1`](../substrates/obsfield-v1.md)
- [`Dagflow v1`](../substrates/dagflow-v1.md)
- [`Contracts`](../../framework/contracts/index.md)
- framework task/model/binding contracts
