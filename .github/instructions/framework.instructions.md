---
name: EHP-SN framework
description: Normative development rules for framework code, framework specifications, and framework tests
applyTo: "packages/ehp-sn/**,docs/framework/**,tests/framework/**"
---

# Framework development

Read, in order:

1. `README.md`;
2. `packages/ehp-sn/README.md`;
3. the owning document under `docs/framework/`;
4. directly affected adjacent framework specifications.

Read `docs/architecture/responsibilities.md` only when the change affects ownership, package boundaries, or cross-component placement.

Read only the framework documents relevant to the responsibility being changed.

## Documentation routing

Use the relevant normative document:

```text
substrates
    docs/framework/substrates.md

tasks
    docs/framework/tasks.md

models
    docs/framework/models.md

bindings
    docs/framework/bindings.md

experiments
    docs/framework/experiments.md

protocols or services
    docs/framework/protocols-and-services.md

validation
    docs/framework/validation.md

configuration
    docs/framework/configuration.md

artifact lifecycle
    docs/architecture/artifacts.md

execution lifecycle
    docs/architecture/execution-model.md
```

## Responsibility

`ehp_sn` owns:

- framework contracts and specifications;
- common scientific data structures;
- validation and conformance;
- protocols and execution services;
- training and evaluation runtime;
- configuration and explicit object loading;
- artifacts, provenance, analysis, reporting, and CLI infrastructure.

It does not own concrete research substrates, tasks, models, bindings, metrics, or analyses.

`ehp_sn` must not import `ehp_research`.

## Design direction

Derive framework behavior from consumer requirements:

```text
research use case
-> required public contract
-> validation rules
-> framework service
-> backend
```

Consult concrete research workflows only when needed to:

- derive or validate a framework requirement;
- assess the impact of a contract change;
- verify that an abstraction serves its intended consumers;
- run a vertical integration test.

Do not expose backend behavior as a scientific requirement.

## Contracts

- Keep contracts small, explicit, and semantically meaningful.
- Distinguish task definitions, immutable task instances, and runtime state.
- Preserve public, target, privileged, and provenance boundaries.
- Keep models independent of concrete tasks.
- Require explicit bindings for supported task-model combinations.
- Validate concrete specification versions; do not infer compatibility from shape alone.
- Make objective composition explicit in the experiment.
- Keep protocols declarative and services executable.
- Keep backend-specific objects behind framework interfaces.

## Framework-gap analysis

Before changing a public contract, record:

```text
Consumer requirement:
Current contract limitation:
Affected workflows:
Minimal contract change:
Alternatives considered:
Compatibility impact:
Verification criteria:
```

Change the framework when the responsibility is inherently framework-level or when stable commonality has been demonstrated.

Do not add a compatibility shim unless an actual compatibility requirement exists.

## Contract change procedure

Use this procedure when public semantics, compatibility, or artifact contracts change:

1. state the consumer requirement;
2. resolve terminology and assumptions;
3. identify affected contracts, services, validation, and artifacts;
4. inspect downstream research integrations;
5. implement the minimal contract change;
6. update framework tests and semantic microcases;
7. update the framework README or owning framework document.

For internal implementation changes, preserve the existing public contract and verify it through the relevant tests.

## Framework tests

Framework tests verify:

- contract conformance;
- validation behavior;
- protocol and service behavior;
- configuration and loading;
- artifact lifecycle;
- backend isolation and integration.

Each semantic or conformance test should identify the contract, invariant, or acceptance criterion it verifies.

Do not derive expected results from the implementation under test.
