---
title: Experiments
authority: normative
status: specified
api_stability: provisional
---

# Experiments

An `ExperimentDefinition` is the semantically immutable scientific composition consumed by training and evaluation.

This page defines public construction, identity, equality, canonicalization, and reuse behavior. Internal class layout belongs to implementation and generated API reference.

## Established use

```python
from ehp_research.experiments.arena_tem import arena_tem_v1

experiment = arena_tem_v1()
```

A package-owned factory supplies the standard task, model, binding, protocols, objectives, metrics, traces, and declared data requirements for the experiment family.

## Supported scientific specialization

```python
from ehp_sn.protocols import TrainingProtocol

experiment = arena_tem_v1(
    training=TrainingProtocol(max_steps=100_000),
)
```

A factory exposes only supported scientific specialization points. Arbitrary mutation of a constructed experiment is not public API.

## Nominal reference and construction

```python
ref = ExperimentRef.parse("experiment:arena-tem/v1")
experiment = resolve_experiment(ref)
```

| Capability                               | Canonical or candidate expression | Status                                                 |
| ---------------------------------------- | --------------------------------- | ------------------------------------------------------ |
| Parse a canonical experiment reference   | `ExperimentRef.parse(text)`       | Required capability; exact parser location provisional |
| Resolve a canonical experiment reference | `resolve_experiment(ref)`         | Proposed helper symbol                                 |
| Construct Arena–TEM                      | `arena_tem_v1(...)`               | Established target                                     |
| Access canonical identity                | `experiment.ref`                  | Stable public attribute                                |
| Access resolved scientific digest        | `experiment.digest`               | Stable public attribute                                |
| Convert portable metadata                | `experiment.to_record()`          | Stable public capability                               |

Direct factory construction and reference resolution use the same package-owned constructors and compatibility checks.

## Identity model

```text
ExperimentRef
    canonical identity of the package-owned experiment specification

ResolvedExperiment
    complete effective scientific definition after specialization

ResolvedExperimentDigest
    canonical digest of that effective scientific definition
```

For example, both definitions retain `experiment:arena-tem/v1`:

```python
baseline = arena_tem_v1()
long_run = arena_tem_v1(
    training=TrainingProtocol(max_steps=100_000),
)
```

They have different resolved digests because their effective scientific definitions differ.

A canonical experiment version changes when the public scientific meaning or contract changes. Supported parameter specialization does not require a new canonical version, but it changes the resolved digest and is recorded in provenance.

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

The resolved request records the corpus reference, content digest, resolution source, schema compatibility, and any permitted override. Execution never searches for a different corpus implicitly.

## Construction behavior

Construction must:

1. invoke package-owned constructors;
2. resolve referenced scientific components;
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

- [Python interface overview](_index.md)
- [Training](training.md)
- [Evaluation](evaluation.md)
- [Shared conventions](conventions.md)
- [Framework semantics](../../framework/_index.md)

## Non-goals

This page does not define runtime configuration, request serialization formats beyond portable records, operation execution, artifact schemas, or public extension inheritance.
