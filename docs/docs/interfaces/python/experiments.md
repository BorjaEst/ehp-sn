---
title: Experiments
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Experiments

An `ExperimentDefinition` is the semantically immutable scientific composition consumed by training and evaluation.

This page defines public construction, identity, equality, canonicalization, and reuse behavior.
Internal class layout belongs to implementation and generated API reference.

## Canonical construction: reference resolution

The public construction path resolves a canonical experiment reference through the framework:

```python
ref = ExperimentRef.parse("experiment:arena-tem/v1")
experiment = resolve_experiment(ref)
```

The experiment itself is owned by the repository-level `experiments/<experiment>/vN/` specification and its concrete composition.
The generic Python interface takes a canonical reference and resolves it; it does not import a concrete package-owned factory such as `ehp_research.experiments.arena_tem`.
There is no `ehp_research.experiments` or `ehp_research.bindings` (`ARCH-005`/`ARCH-006`).

> `resolve_experiment()` is a documented target.
> The experiment discovery and resolution contract is not yet specified; until it exists this interface must not be implemented against an invented storage representation (`ARCH-014`).

## Identity model

```text
ExperimentRef
    canonical identity of the experiment specification (owned at experiments/<experiment>/vN/)

ResolvedExperiment
    complete effective scientific definition after specialization

ResolvedExperimentDigest
    canonical digest of that effective scientific definition
```

For example, both definitions retain `experiment:arena-tem/v1` (obtained by reference resolution
with different specialization):

```python
baseline = resolve_experiment(ExperimentRef.parse("experiment:arena-tem/v1"))
long_run = resolve_experiment(ExperimentRef.parse("experiment:arena-tem/v1"),
                              training=TrainingProtocol(max_steps=100_000))
```

They have different resolved digests because their effective scientific definitions differ.

A canonical experiment version changes when the public scientific meaning or contract changes.
Supported parameter specialization does not require a new canonical version, but it changes the resolved digest and is recorded in provenance.

## Semantic immutability

Once constructed and validated, an experiment cannot change in a way that affects semantics or identity.

This requirement applies recursively:

- nested specifications and collections are immutable or canonicalized into immutable forms;
- mutable dictionaries and lists are not retained as identity-bearing state;
- live model instances, modules, file handles, backend clients, and other mutable runtime objects are not embedded;
- arbitrary Python objects are accepted only when the owning specification defines deterministic canonicalization and identity behavior;
- supported specialization creates a new experiment value rather than modifying an existing value.

A frozen outer object with mutable nested state does not satisfy this contract.

## Equality, hashing, and canonicalization

Two separately constructed experiment definitions compare equal when their canonical effective scientific records are equal.

The public contract is:

- equality is semantic, not object-identity based;
- equal experiments have equal resolved digests;
- unequal resolved digests imply unequal effective scientific definitions;
- hashability is required when the implementation exposes experiments as mapping or cache keys;
- canonicalization occurs during construction before digest computation;
- ordering of semantically unordered fields does not alter equality or digest;
- runtime-only values never participate in experiment equality or digest.

The canonical record includes all identity-affecting scientific fields, including component references, protocols, objective configuration, metric and trace declarations, data requirements, and supported scientific specialization.

## Experiment ownership

An experiment owns:

- canonical experiment, task, model, and binding references;
- substrate or task-corpus requirements where applicable;
- training protocol;
- named evaluation regimes;
- objective selection and weighting;
- metric and trace declarations;
- scientific defaults and invariants.

An experiment does not own:

- device, precision, accelerator, or process topology;
- invocation seeds;
- tracking backend;
- physical output destination;
- selected checkpoint;
- resume or initialization state;
- diagnostic case bounds.

Those values belong to requests and execution provenance.

## Task-corpus requirements

An experiment declares a corpus requirement rather than silently selecting a local dataset.

Request resolution converts that requirement into one exact committed `ArtifactRef` using deterministic precedence:

1. explicit request corpus, when replacement is permitted;
2. exact corpus reference declared by the resolved experiment;
3. configured workspace binding for the declared requirement;
4. otherwise fail.

The resolver never selects automatically among arbitrary compatible local artifacts.

The resolved request records the corpus reference, artifact fingerprint, resolution source, schema compatibility, and any permitted override.
Execution never searches for a different corpus implicitly.

## Construction behavior

Construction must:

1. resolve the experiment's components through the framework discovery/resolution mechanism;
2. assemble the resolved scientific components into a definition;
3. apply supported specialization;
4. canonicalize nested scientific values;
5. validate definition-level compatibility;
6. compute the resolved digest;
7. return an immutable definition.

Construction must not load complete corpus payloads, instantiate mutable runtime model state, initialize devices, create run directories, or begin execution.

## Identity use

| Purpose                                | Identity used                                                  |
| -------------------------------------- | -------------------------------------------------------------- |
| Scientific definition comparison       | `ExperimentRef` plus resolved digest                           |
| Request construction                   | Resolved experiment record and digest                          |
| Resume compatibility                   | Resolved digest plus operation-specific lineage fields         |
| Provenance                             | Canonical reference, resolved record, and digest               |
| Cache lookup for definition-level work | Resolved digest                                                |
| Artifact identity                      | Experiment identity plus the operation's other identity inputs |

Equal experiments do not imply equal results because seeds, data, checkpoints, runtime behavior, and execution provenance remain separate.

## Related interfaces

- [Python interface overview](index.md)
- [Training](training.md)
- [Evaluation](evaluation.md)
- [Shared conventions](conventions.md)
- [Framework semantics](../../framework/index.md)
