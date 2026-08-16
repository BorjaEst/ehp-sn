# EHP Research

<div align="center">

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-specification--first-lightgrey)](#specification-status)
[![Docs](https://img.shields.io/badge/docs-readthedocs-green)](https://ehp-sn.readthedocs.io)

</div>

`ehp_research` provides reusable scientific building blocks developed by the EHP research programme: substrates, tasks, models, objectives, controllers, metrics, and analyses.

It implements research definitions against the reusable `ehp_sn` framework:

```text
ehp_research → ehp_sn
```

The package owns reusable scientific/domain semantics.
Generic artifact, configuration, resource, request, execution, identity, and lifecycle mechanics remain framework responsibilities.
Concrete experiments and concrete task-model Bindings do **not** belong to `ehp_research`; they belong to repository-level `experiments/` (`docs/invariants.md` ARCH-005/006).
Bindings are resolved compositions of generic `ehp_sn` adapters assembled by an experiment definition, not independent package artifacts.

This README provides package orientation and a catalogue overview.
Exact scientific semantics and component status live in the corresponding research specifications.

## Contents

- [Research areas](#research-areas)
- [Data architecture](#data-architecture)
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
- TEM, HRM, and related reusable model families;
- reusable objectives, controllers, and research metrics;
- reusable scientific analyses.

Semantics are placed at the narrowest reusable scientific owner:

```text
substrate
    reusable task-neutral domain structure

task
    scientific problem and truth semantics

model
    model-native computation

adapter
    task ↔ model representation transformation (ehp_sn, when generic)

binding
    resolved task+model+adapter composition (assembled by the experiment)

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

## Models

Models define model-native architecture, state, memory, and inference semantics.
Reusable model families belong to `ehp_research`.

Typical families include:

- TEM;
- HRM;
- related integrated EHP models.

A binding is the resolved, validated connection of one task and one model, formed by one configured `InputAdapter` and one configured `OutputAdapter`.
The generic adapter contracts live in `ehp_sn`; a concrete resolved binding is assembled by an experiment and belongs to that experiment under repository-level `experiments/` (`ARCH-006`).
`ehp_research` does not own a package-level `bindings/` directory.

Exact model, adapter, binding, compatibility, and maturity information belongs in the corresponding research and framework specifications rather than this README.

## Experiments

Concrete scientific experiments — composed of a task, a model, a binding, protocols, objectives, metrics, traces, and resource requirements — belong to repository-level `experiments/`, not to `ehp_research` (`ARCH-005`).
Each experiment's `plan.md` is the normative scientific authority for that composition.
`ehp_research` provides the reusable building blocks the experiment selects and connects; it does not package concrete experiment definitions.

## Registration and discovery

Installed research definitions are exposed through the framework-owned registration/discovery boundary.

Conceptually:

```text
ehp_sn
    owns catalogue / registry contracts

ehp_research
    provides concrete reusable definitions
```

Concrete workspace experiments under `experiments/` are discovered through workspace experiment discovery, not through `ehp_research.registration`.

This preserves the dependency direction and allows the framework to remain independent of concrete research packages.

The exact automatic discovery mechanism belongs to the corresponding framework specification once finalized.

## Package structure

The intended research responsibilities can be organized conceptually as:

```text
ehp_research/
├── substrates/
├── tasks/
├── models/
├── controllers/
├── objectives/
├── metrics/
├── analyses/
└── configuration/
```

There is deliberately no `experiments/` and no `bindings/` under `ehp_research` (`ARCH-005`/`ARCH-006`).

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

`ehp_research` is distributed under the GNU General Public License v3.0.
See [`LICENSE`](../../LICENSE).
