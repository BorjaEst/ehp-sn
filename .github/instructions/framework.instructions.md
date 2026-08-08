---
applyTo: "packages/ehp-sn/src/**/*.py,packages/ehp-sn/tests/**/*.py,docs/docs/framework/**/*.md,docs/docs/design/**/*.md,tests/architecture/**/*.py"
---

# Framework instructions

These paths participate in the reusable `ehp_sn` framework.

## Framework ownership

`ehp_sn` owns reusable contracts and services that are independent of the concrete EHP research programme.

Framework-owned concerns include:

- component references and generic compatibility mechanics;
- generic task/model/binding contracts;
- experiment, protocol, request, and execution-plan contracts;
- resource requirements and resource states;
- artifact references, identity, manifests, digests, and provenance;
- generic `DataArtifact`, `SubstrateArtifact`, and `TaskCorpus` contracts;
- generic loading, validation, staging, publication, and inspection mechanics;
- execution and runtime orchestration;
- public framework services.

## Dependency invariant

The dependency direction is:

```text
ehp_research → ehp_sn
```

Framework code must not import `ehp_research` or another concrete research package by name.

Framework discovery of research definitions must occur through a framework-owned registration/discovery contract.

## Generalization rule

Do not move a concept into the framework merely because multiple current research components share it.

A framework abstraction requires a demonstrated reusable requirement independent of those concrete research components.

Examples:

- `TaskCorpus` is framework-owned.
- `ResourceRequirement` is framework-owned.
- `raster-topology/v1` is research-owned.
- `observation-field/v1` is research-owned.
- DungeonGen, Maze-ND, ObsField, Dagflow, Arena, MazeHard, Routebind, and Prospect are research-owned.

Research examples may illustrate framework contracts without becoming framework requirements.

## Specification and implementation

Framework implementation must conform to the normative framework/interface specifications.

Do not silently change public semantics in code because another implementation would be easier.

When code reveals a specification gap, surface the gap and update the appropriate authority.

## Infrastructure boundary

PyTorch, Lightning Fabric, Hydra, Pydantic, MLflow, TorchMetrics, Optuna, Typer, and similar tools are implementation dependencies.

They must not become the semantic authority for EHP-SN public contracts.
