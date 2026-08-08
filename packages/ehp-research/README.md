# EHP Research

<div align="center">

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-specification--first-lightgrey)](#specification-status)
[![Docs](https://img.shields.io/badge/docs-readthedocs-green)](https://ehp-sn.readthedocs.io)

</div>

`ehp_research` contains the concrete scientific components and experiment families developed by the EHP research programme.

It implements research definitions against the reusable `ehp_sn` framework:

```text
ehp_research → ehp_sn
```

The package owns scientific/domain semantics. Generic artifact, configuration, resource, request, execution, identity, and lifecycle mechanics remain framework responsibilities.

This README provides package orientation and a catalogue overview. Exact scientific semantics and component status live in the corresponding research specifications.

## Contents

- [Research areas](#research-areas)
- [Data architecture](#data-architecture)
- [Component catalogue](#component-catalogue)
- [Models and bindings](#models-and-bindings)
- [Experiments](#experiments)
- [Registration and discovery](#registration-and-discovery)
- [Package structure](#package-structure)
- [Specification status](#specification-status)
- [Installation](#installation)
- [Testing](#testing)
- [Documentation](#documentation)
- [License](#license)

## Research areas

`ehp_research` contains:

- reusable spatial and relational substrates;
- navigation and structural-reasoning tasks;
- TEM, HRM, and integrated EHP model families;
- task–model bindings;
- objectives and research metrics;
- scientific analyses;
- reusable experiment definitions;
- research-specific study definitions.

Semantics are placed at the narrowest reusable scientific owner:

```text
substrate
    reusable task-neutral domain structure

task
    scientific problem and truth semantics

model
    model-native computation

binding
    task ↔ model representation and integration

experiment
    reusable scientific composition
```

## Data architecture

Research data separates task-neutral substrates from task-specific corpora.

```text
task-neutral substrates
        ↓
task-owned composition and case generation
        ↓
self-contained TaskCorpus
```

Substrates are committed under:

```text
data/interim/
```

Task corpora are committed under:

```text
data/processed/
```

Exact upstream artifacts and other reproducibility-relevant build choices are resolved through the framework configuration/resource-binding mechanism.

### Substrates

Current substrate specifications include:

| Reference       | Purpose                                                          |
| --------------- | ---------------------------------------------------------------- |
| `dungeongen/v1` | Procedurally generated raster topology                           |
| `maze-nd/v1`    | Normalized reusable raster topology from an external maze source |
| `obsfield/v1`   | Independent persistent categorical observation fields            |
| `dagflow/v1`    | Reusable directed graph structure                                |

Some producers may share a research-owned task-facing schema where several research components require the same domain representation.

For exact record schemas, invariants, lineage rules, and current status, see [`../../docs/docs/research/substrates/`](../../docs/docs/research/substrates/).

### Tasks

Current task specifications include:

| Reference      | Problem                                                                       |
| -------------- | ----------------------------------------------------------------------------- |
| `arena/v1`     | Sequential spatial experience, memory acquisition, and observation prediction |
| `maze-hard/v1` | Fully observed shortest-route reasoning                                       |
| `routebind/v1` | Spatial routing constrained by a semantic transition structure                |
| `prospect/v1`  | Memory-conditioned semantic-spatial prospective reasoning                     |

For exact parent roles, information regimes, oracle semantics, targets, metrics, and current status, see [`../../docs/docs/research/tasks/`](../../docs/docs/research/tasks/).

Catalogue status should be derived or mechanically validated from the authoritative specifications rather than maintained independently here.

## Models and bindings

Models define model-native architecture, state, memory, and inference semantics.

Bindings connect task families to model families and own integration-specific representation logic.

Typical research families include:

- TEM;
- HRM;
- integrated EHP models.

Bindings may cover combinations such as Arena–TEM or Routebind–EHP as those specifications are defined.

Exact model, binding, compatibility, and maturity information belongs in the corresponding research specifications rather than this README.

## Experiments

Reusable experiment families compose scientific definitions such as:

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

An experiment family defines reusable scientific composition.

Exact replaceable resources such as corpus artifacts are resolved through framework configuration rather than hidden in deployment-specific repository state.

Repository-local reproduction assets, when present, are separate from the installed package’s reusable experiment definitions.

## Registration and discovery

Installed research definitions are exposed through the framework-owned registration/discovery boundary.

Conceptually:

```text
ehp_sn
    owns catalogue / registry contracts

ehp_research
    provides concrete definitions
```

This preserves the dependency direction and allows the framework to remain independent of concrete research packages.

The exact automatic discovery mechanism belongs to the corresponding framework specification once finalized.

## Package structure

The intended research responsibilities can be organized conceptually as:

```text
ehp_research/
├── substrates/
├── tasks/
├── models/
├── bindings/
├── controllers/
├── objectives/
├── metrics/
├── analyses/
├── experiments/
├── studies/
└── configuration/
```

This is a responsibility map rather than a guarantee that every directory already exists or that the physical package layout is fixed.

## Specification status

EHP-SN is under specification-first development.

This README does not assign authoritative implementation or maturity status to individual research components.

For current status and exact semantics, use:

- [`../../docs/docs/research/substrates/`](../../docs/docs/research/substrates/);
- [`../../docs/docs/research/tasks/`](../../docs/docs/research/tasks/);
- the corresponding model, binding, experiment, metric, and analysis specifications as they are added.

The repository authority model is defined in [`../../docs/authority.md`](../../docs/authority.md).

## Installation

Requirements:

- Python 3.12 or later;
- `ehp_sn`.

For editable development installation from the repository root:

```bash
python -m pip install -e packages/ehp-sn
python -m pip install -e packages/ehp-research
```

## Testing

Run research-package and cross-package tests from the repository root:

```bash
python -m pytest packages/ehp-research/tests tests/architecture tests/integration
```

## Documentation

See:

- [repository README](../../README.md);
- [framework README](../ehp-sn/README.md);
- [research substrate specifications](../../docs/docs/research/substrates/);
- [research task specifications](../../docs/docs/research/tasks/);
- [documentation authority](../../docs/authority.md);
- [repository invariants](../../docs/invariants.md).

## License

`ehp_research` is distributed under the GNU General Public License v3.0. See [`LICENSE`](../../LICENSE).
