# EHP-SN Framework

<div align="center">

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-specification--first-lightgrey)](#specification-status)
[![Docs](https://img.shields.io/badge/docs-readthedocs-green)](https://ehp-sn.readthedocs.io)

</div>

`ehp_sn` is the reusable framework package of EHP-SN.

It provides the contracts and services used to compose, configure, execute, validate, and inspect scientific workflows independently of the concrete `ehp_research` programme.

```text
ehp_research → ehp_sn
```

Concrete scientific substrates, tasks, and models belong to `ehp_research`.
Concrete experiment compositions and concrete task-model Bindings belong to repository-level `experiments/`, not to `ehp_research` or `ehp_sn` (`docs/invariants.md` ARCH-005/006).

This README provides the framework mental model and entry points.
Exact semantics live in the framework and interface specifications under `docs/docs/`.

## Contents

- [Responsibilities](#responsibilities)
- [Conceptual model](#conceptual-model)
- [Configuration and resources](#configuration-and-resources)
- [Data artifacts](#data-artifacts)
- [Public interfaces](#public-interfaces)
- [Component discovery](#component-discovery)
- [Framework boundaries](#framework-boundaries)
- [Specification status](#specification-status)
- [Installation](#installation)
- [Testing](#testing)
- [Documentation](#documentation)
- [License](#license)

## Responsibilities

The framework provides reusable semantics and services for:

- component references and compatibility;
- Task, Model, Adapter, and Binding contracts;
- experiment and protocol composition;
- execution requests and immutable plans;
- resource requirements and configuration resolution;
- training, evaluation, analysis, and reporting orchestration;
- reproducibility and seed ownership;
- generated-data and task-corpus contracts;
- artifact references, identity, provenance, validation, and inspection;
- public Python and CLI interfaces;
- component registration/discovery contracts.

Research-specific meaning remains downstream in `ehp_research`.

## Conceptual model

```text
scientific definitions
        ↓
resolved experiment / operation definition
        ↓
request
        ↓
immutable execution or build plan
        ↓
validation
        ↓
execution
        ↓
committed artifacts
```

### Task

A Task provides the generic contract for a scientific problem.

Concrete task specifications define the actual information regime, oracle semantics, targets, validity, and task-level scoring.

### Model

A Model provides model-native computation:

- architecture;
- native inputs and outputs;
- state and memory;
- inference behavior;
- intrinsic model observables.

Concrete model semantics belong to research model specifications.

### Adapter

An Adapter transforms between a task's interfaces and a model's interfaces:

- an `InputAdapter` transforms a task's task-data interface into a model's model-input interface;
- an `OutputAdapter` transforms a model's model-output interface into a task's prediction interface.

An adapter must be expressible entirely in terms of its declared source interface, target interface, and resolved configuration — it must not branch on concrete task or model identity.
This is what makes `ehp_sn` the right owner for a generic adapter implementation, distinct from any one task or model.

### Binding

A Binding is the resolved, validated connection of one task and one model, formed by one configured `InputAdapter` and one configured `OutputAdapter`.

A Binding is not an independently implemented component; it is assembled by an experiment from the task, the model, and their configured adapters.

Bindings do not redefine task truth or model architecture.
Adapters composing a binding do not perform oracle repair or task scoring, and do not introduce privileged information.

### Experiment

An experiment is an immutable scientific composition of resolved definitions.

Conceptually, it can combine:

```text
task
+ model
+ binding
+ training protocol
+ evaluation protocol
+ objectives
+ metrics
+ traces
+ resource requirements
```

Invocation-specific runtime, output, checkpoint, replicate seed, and replaceable resource selections belong to request/configuration layers rather than mutable experiment state.

### Request and plan

Requests add invocation-specific values to a scientific definition.

Resolution produces an immutable plan that records the effective values and exact resource bindings needed for validation and execution.

## Configuration and resources

Scientific definitions declare the resources they require.

Configuration resolves those requirements to exact permitted resources before execution.

```text
definition
    declares resource requirement
        ↓
configuration / workspace / explicit invocation
    selects resource
        ↓
resolved plan
        ↓
validation
        ↓
execution
```

This keeps scientific definitions independent of deployment-specific artifact coordinates while preserving reproducibility.

The public configuration model is EHP-SN-owned.
Hydra or another library may be used as an implementation backend without becoming the public semantic authority.

See [`../../docs/docs/interfaces/configuration/`](../../docs/docs/interfaces/configuration/) for the configuration specification.

## Data artifacts

The framework distinguishes two generic generated-data roles:

```text
DataArtifact
├── SubstrateArtifact
└── TaskCorpus
```

A `SubstrateArtifact` stores reusable task-neutral generated or normalized data.

A `TaskCorpus` stores task-specific cases, episodes, or queries together with the resources required by its declared normal consumers.

Concrete payload schemas and scientific generation semantics belong to `ehp_research`.

See:

- [`../../docs/docs/framework/data-artifacts.md`](../../docs/docs/framework/data-artifacts.md);
- [`../../docs/docs/framework/corpora.md`](../../docs/docs/framework/corpora.md).

## Public interfaces

### CLI

The public lifecycle is:

```text
data → tasks → train → evaluate → analyze → report
```

The general command form is:

```text
ehp-sn COMMAND OPERATION [TARGET] [OPTIONS]
```

Shared operation vocabulary includes:

```text
list
show
plan
validate
build
run
inspect
```

The CLI orchestrates framework and installed research definitions; it is not a separate scientific semantic layer.

See [`../../docs/docs/interfaces/cli/`](../../docs/docs/interfaces/cli/).

### Python

The direct Python interface exposes the same underlying framework semantics as the configured CLI path.

Conceptually:

```text
Python ─┐
        ├─→ resolution → validation → execution
CLI ────┘
```

See [`../../docs/docs/interfaces/python/`](../../docs/docs/interfaces/python/).

## Component discovery

The framework provides the registration/discovery boundary through which installed packages expose components to framework catalogues.

Concrete research packages remain downstream of that contract; the framework does not rely on concrete research modules as part of its reusable semantic core.

The exact discovery mechanism and duplicate-registration behavior belong to the corresponding framework specification once finalized.

## Framework boundaries

Infrastructure libraries sit below EHP-SN semantics.

Typical integrations include:

| Integration      | Framework role                              |
| ---------------- | ------------------------------------------- |
| PyTorch          | Tensor and model foundation                 |
| Lightning Fabric | Runtime execution backend                   |
| Hydra            | Internal configuration/composition backend  |
| Pydantic         | External and serialized-boundary validation |
| Typer            | CLI frontend                                |
| MLflow           | Optional tracking/persistence integration   |
| TorchMetrics     | Optional metric integration                 |
| Optuna           | Optional study backend                      |

Using an infrastructure library does not transfer semantic ownership to that library.

## Specification status

EHP-SN is under specification-first development.

This README summarizes the intended framework architecture.
It is not the normative home for exact framework contracts.

`Specified` means that semantics and responsibilities are documented; implementation and validation status are separate concerns.

Use:

- [`../../docs/authority.md`](../../docs/authority.md) for semantic ownership;
- [`../../docs/invariants.md`](../../docs/invariants.md) for cross-cutting repository invariants;
- [`../../docs/docs/framework/`](../../docs/docs/framework/) for framework specifications;
- [`../../docs/docs/interfaces/`](../../docs/docs/interfaces/) for public interfaces.

## Installation

From the repository root:

```bash
python -m pip install -e packages/ehp-sn
```

## Testing

Run framework and cross-package tests from the repository root:

```bash
python -m pytest packages/ehp-sn/tests tests/architecture tests/integration
```

## Documentation

See:

- [repository README](../../README.md);
- [framework specifications](../../docs/docs/framework/);
- [CLI specification](../../docs/docs/interfaces/cli/);
- [configuration specification](../../docs/docs/interfaces/configuration/);
- [Python interface specification](../../docs/docs/interfaces/python/);
- [research package](../ehp-research/README.md).

## License

`ehp_sn` is distributed under the GNU General Public License v3.0.
See [`LICENSE`](../../LICENSE).
