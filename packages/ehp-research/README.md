# EHP Research

<div align="center">

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-specified-lightgrey)](./README.md#current-status)
[![Docs](https://img.shields.io/badge/docs-readthedocs-green)](https://ehp-sn.readthedocs.io)

</div>

`ehp_research` contains the concrete scientific components and experiment families developed by the EHP research programme.

It includes:

- spatial and relational substrates;
- navigation and structural-reasoning tasks;
- TEM, HRM, and integrated EHP models;
- supported task–model bindings;
- domain objectives and metrics;
- scientific analyses;
- reusable experiment definitions;
- research-specific study definitions.

`ehp_sn` defines the authoritative semantics for component references, compatibility, experiments, protocols, requests, runs, seeds, metrics, and artifacts.

---

## Contents

- [Quick Start](#quick-start)
- [Relationship to ehp_sn](#relationship-to-ehp_sn)
- [Package Structure](#package-structure)
- [Component Catalogue](#component-catalogue)
- [Compatibility Matrix](#compatibility-matrix)
- [Controllers & Objectives](#controllers-and-objectives)
- [Experiment Families](#experiment-families)
- [Metrics & Analyses](#metrics-and-analyses)
- [Current Status](#current-status)
- [Installation](#installation)
- [Testing](#testing)
- [License](#license)

---

## Quick start

```python id="84s8qx"
from ehp_sn import evaluate, train
from ehp_sn.protocols import TrainingProtocol
from ehp_sn.reproducibility import SeedConfiguration
from ehp_research.experiments.arena_tem import arena_tem_v1

experiment = arena_tem_v1(
    training=TrainingProtocol(
        max_steps=50_000,
    ),
)

training = train(
    experiment,
    seeds=SeedConfiguration.from_master(42),
    runtime="cuda",
    tracking="local",
    output="runs/arena-tem-v1",
)

evaluation = evaluate(
    experiment,
    checkpoint=training.best_checkpoint,
    regime="test",
    seeds=SeedConfiguration.from_master(43),
)

print(evaluation.metrics)
```

The factory supplies the standard Arena–TEM components, evaluation regimes, metrics, traces, and observables.

The equivalent configured workflow:

```bash
ehp-sn train run experiment:arena-tem/v1 \
    --set protocol.training.max_steps=50000 \
    --seed 42 \
    --device cuda
```

See the [CLI reference](../../docs/docs/interfaces/cli/_index.md) for the full command grammar.

Both workflows resolve through the framework’s standard construction and validation path.

These examples become executable contracts when the Arena–TEM integration is implemented and validated.

## Relationship to `ehp_sn`

| `ehp_research` provides                  | `ehp_sn` provides                             |
| ---------------------------------------- | --------------------------------------------- |
| Substrates, tasks, models, bindings      | Their public contracts                        |
| Domain objectives, metrics, and analyses | Composition and execution infrastructure      |
| Experiment and study definitions         | Runtime, configuration, and artifact services |

The dependency direction is:

```text id="7q6lpw"
ehp_research → ehp_sn
```

Research implementations must not be added to the framework package.

## Package structure

```text id="j5xprn"
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

The structure is descriptive rather than a fixed implementation contract.

## Component catalogue

EHP-SN separates environments (substrates), problems (tasks), and solutions (models). Bindings connect compatible pairs. The catalogue below lists the components planned for the initial research programme.

### Substrates

| Reference       | Purpose                                                          | Status    |
| --------------- | ---------------------------------------------------------------- | --------- |
| `openfield/v1`  | Spatial environments with positions, movements, and observations | Specified |
| `dagflow/v1`    | Directed relational structures and observation mappings          | Specified |
| `dungeongen/v1` | Generated maze-like spatial environments                         | Planned   |
| `maze-nd/v1`    | Maze structures used by reasoning tasks                          | Planned   |

### Tasks

| Reference      | Purpose                                       | Status    |
| -------------- | --------------------------------------------- | --------- |
| `arena/v1`     | Spatial exploration, memory, and prediction   | Specified |
| `goaltrace/v1` | Structural reasoning over relational graphs   | Specified |
| `prospect/v1`  | Prospective prediction from acquired memory   | Specified |
| `routebind/v1` | Joint spatial and semantic route reasoning    | Specified |
| `maze-hard/v1` | Iterative reasoning over maze representations | Specified |

### Models

| Reference | Purpose                                             | Status    |
| --------- | --------------------------------------------------- | --------- |
| `tem/v1`  | Structural and episodic memory                      | Specified |
| `hrm/v1`  | Hierarchical iterative reasoning                    | Specified |
| `hrm/v2`  | Revised hierarchical reasoning system               | Specified |
| `ehp/v1`  | Integrated entorhinal–hippocampal–prefrontal system | Specified |

### Bindings

| Reference          | Purpose                | Status    |
| ------------------ | ---------------------- | --------- |
| `arena-tem/v1`     | Apply TEM to Arena     | Specified |
| `goaltrace-hrm/v1` | Apply HRM to Goaltrace | Specified |
| `prospect-tem/v1`  | Apply TEM to Prospect  | Specified |
| `routebind-hrm/v1` | Apply HRM to Routebind | Specified |
| `routebind-ehp/v1` | Apply EHP to Routebind | Specified |

Bindings contain only task–model integration logic. Task semantics remain with tasks, and model architecture remains with models.

## Compatibility matrix

Only explicitly supported task–model pairs are available for experiment composition. The matrix below lists the declared combinations.

| Binding            | Task           | Model    | Support   | Maturity |
| ------------------ | -------------- | -------- | --------- | -------- |
| `arena-tem/v1`     | `arena/v1`     | `tem/v1` | Supported | Declared |
| `goaltrace-hrm/v1` | `goaltrace/v1` | `hrm/v2` | Supported | Declared |
| `prospect-tem/v1`  | `prospect/v1`  | `tem/v1` | Supported | Declared |
| `routebind-hrm/v1` | `routebind/v1` | `hrm/v2` | Supported | Declared |
| `routebind-ehp/v1` | `routebind/v1` | `ehp/v1` | Supported | Declared |

The framework README defines the support and maturity vocabulary.

These combinations remain declared until implementation, conformance testing, and scientific validation justify higher maturity.

## Controllers and objectives

Controllers and objective terms follow the same ownership rule as other components — each belongs to its narrowest semantic owner:

- model-intrinsic behaviour → model;
- task-level semantics → task;
- joint task–model behaviour → binding;
- final selection and weighting → experiment.

## Experiment families

Reusable experiment factories belong under:

```text id="lslv4a"
ehp_research/experiments/
├── arena_tem/
├── goaltrace_hrm/
├── prospect_tem/
└── routebind_ehp/
```

Current specified experiment families include:

| Reference          | Composition                                | Status    |
| ------------------ | ------------------------------------------ | --------- |
| `arena-tem/v1`     | OpenField, Arena, TEM, and Arena–TEM       | Specified |
| `goaltrace-hrm/v1` | DagFlow, Goaltrace, HRM, and Goaltrace–HRM | Specified |
| `prospect-tem/v1`  | Prospect, TEM, and Prospect–TEM            | Specified |
| `routebind-ehp/v1` | Routebind, EHP, and Routebind–EHP          | Specified |

An experiment factory supplies the package-owned component specifications, protocols, metrics, traces, and observables for that experiment family.

Repository-level reproduction assets belong under [`../../experiments/`](../../experiments/).

## Metrics and analyses

Research metrics include:

- prediction error;
- task success;
- route and trajectory validity;
- anchor validity;
- pathway-specific performance;
- representation quality.

An experiment makes metric specifications available to its evaluation regimes. Each regime selects the metrics it computes and identifies its primary outcomes.

Scientific analyses include:

- memory diagnostics;
- latent-state dynamics;
- pathway comparisons;
- prediction visualisations;
- case-level inspection;
- experiment comparisons;
- domain-specific tables and figures.

Analyses consume committed artifacts and do not silently rerun inference.

## Study definitions

Research-specific study definitions live under:

```text id="vn9uwu"
ehp_research/studies/
├── arena_tem_search/
└── goaltrace_hrm_search/
```

Each trial resolves an ordinary experiment and executes an ordinary framework request.

Optuna is the initial backend.

Study abstractions remain provisional until validated by concrete research workflows.

## Reference integrations

The first intended vertical integration is:

```text id="198vf6"
openfield/v1
    ↓
arena/v1
    ↓
tem/v1
    ↓
arena-tem/v1
```

The second is:

```text id="tcq64m"
dagflow/v1
    ↓
goaltrace/v1
    ↓
hrm/v2
    ↓
goaltrace-hrm/v1
```

Their current component status is `Specified`.

Their current compatibility maturity is `Declared`.

A component or compatibility combination becomes `Reference` only after implementation, validation, and reproducible evidence exist.

## Configuration

`ehp_research` ships the defaults, resolvers, constructors, and compatibility declarations required to construct its public components.

Repository-level configuration supplies workspace-specific overrides, exact reproductions, study search spaces, and runtime settings.

An installed `ehp_research` package must not require the monorepo root to construct its public experiment definitions.

## Current status

| Area                                 | Status               |
| ------------------------------------ | -------------------- |
| OpenField and Arena specifications   | Specified            |
| TEM specification                    | Specified            |
| Arena–TEM binding and experiment     | Specified            |
| DagFlow and Goaltrace specifications | Specified            |
| HRM specifications                   | Specified            |
| Goaltrace–HRM binding and experiment | Specified            |
| Remaining catalogue components       | Specified or planned |
| Validated reference integrations     | Not yet available    |

## Scientific context

EHP-SN builds on research in:

- entorhinal–hippocampal cognitive maps;
- structural and relational representations;
- episodic and spatial memory;
- hierarchical and iterative reasoning;
- prospective prediction and planning.

Canonical references belong in the corresponding task, model, binding, and experiment documentation.

## Installation

Requirements:

- Python 3.12 or later
- `ehp_sn`

Install both local packages for development:

```bash id="vu6o2c"
python -m pip install -e packages/ehp-sn
python -m pip install -e packages/ehp-research
```

## Testing

Run the available research-package tests from the repository root:

```bash id="jha1fe"
python -m pytest packages/ehp-research
```

Tests are added alongside implemented scientific components and experiment workflows.

## License

`ehp_research` is distributed under the GNU General Public License v3.0. See the repository [`LICENSE`](../../LICENSE).

See the repository-level [README](../../README.md) for repository orientation and the [framework README](../ehp-sn/README.md) for authoritative framework semantics.
