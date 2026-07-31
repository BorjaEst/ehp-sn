# EHP-SN Framework

<div align="center">

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Status](https://img.shields.io/badge/status-specified-lightgrey)](./README.md#capability-status)
[![Docs](https://img.shields.io/badge/docs-readthedocs-green)](https://ehp-sn.readthedocs.io)

</div>

`ehp_sn` is the reusable scientific framework of EHP-SN.

It defines the authoritative semantics for:

- component references and compatibility;
- tasks, models, and bindings;
- immutable experiment definitions;
- training and evaluation protocols;
- execution requests and runs;
- reproducibility and seed ownership;
- artifact manifests;
- configured and direct Python composition;
- post-hoc analysis execution.

Concrete scientific components belong to [`ehp_research`](../ehp-research/README.md).

The ownership boundaries and workflows described here are normative. Internal type shapes may evolve during implementation unless marked as stable public API.

---

## Contents

- [Quick Start](#quick-start)
- [Conceptual Model](#conceptual-model)
- [Identity & Compatibility](#identity-and-compatibility)
- [Configuration](#scientific-and-execution-configuration)
- [Composition & Execution](#composition-and-execution)
- [Artifacts & Analysis](#artifacts-and-analysis)
- [Framework Areas](#logical-framework-areas)
- [Extensions](#extensions-and-integrations)
- [Capability Status](#capability-status)
- [Installation](#installation)
- [Testing](#testing)
- [License](#license)

---

## Quick start

```python id="hm2tcc"
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

`arena_tem_v1` supplies the standard Arena–TEM task, model, binding, objective, evaluation regimes, metrics, and traces.

The quick start shows the planned API target. It becomes an executable contract after the Arena–TEM integration is implemented and validated.

## Conceptual model

```text id="fjl98i"
component references
    ↓
resolved ExperimentDefinition
    ↓
TrainingRequest or EvaluationRequest
    ↓
run
    ↓
committed ArtifactManifest
    ↓
inspection or AnalysisRequest
```

### Task

A task defines the scientific problem.

It owns:

- public inputs;
- targets;
- privileged or oracle-only information;
- interaction or phase semantics;
- validity rules;
- task-level scoring.

It specifies what the model must predict, what information is available, what constitutes a valid response, and how performance is scored.

### Model

A model defines the computational system under study.

It owns:

- model-native inputs and outputs;
- architecture;
- state and memory;
- inference behaviour;
- intrinsic regularisation;
- model-native traces.

Models remain independent of concrete tasks.

### Binding

A binding connects one task family to one model family.

It owns:

- task-to-model encoding;
- model-to-task decoding;
- integration-specific masks or padding;
- trainable integration modules;
- task–model compatibility declarations;
- genuinely joint objective or controller requirements.

Bindings must not redefine task or model semantics.

| Component | Primary ownership                                                     |
| --------- | --------------------------------------------------------------------- |
| Task      | Problem semantics, information boundaries, targets, validity, scoring |
| Model     | Native interfaces, architecture, state, memory, inference             |
| Binding   | Encoding, decoding, integration modules, joint compatibility          |

### Experiment

An `ExperimentDefinition` is an immutable, resolved scientific composition.

Conceptually, it contains:

```python id="ox2my3"
@dataclass(frozen=True)
class ExperimentDefinition:
    ref: ExperimentRef
    task: TaskSpecification
    model: ModelSpecification
    binding: BindingSpecification
    training: TrainingProtocol
    evaluation: EvaluationProtocol
    metrics: tuple[MetricSpecification, ...]
    traces: tuple[TraceSpecification, ...]
```

Real experiments may also include a substrate or data source, controller, and objective specifications.

The experiment contains resolved specifications and retains their canonical references.

Runtime objects, mutable state, infrastructure settings, replicate seeds, checkpoints, trackers, and output destinations belong to execution requests or runtime contexts rather than the experiment.

### Request and run

A `TrainingRequest` or `EvaluationRequest` combines an experiment with invocation-specific settings, including:

- runtime and hardware;
- precision and distribution;
- seeds;
- tracking;
- artifact destination;
- checkpoint or resumption state;
- selected evaluation regime.

A run is one execution of a validated request.

Its durable `RunRecord` links the resolved request to its source revision and committed artifacts.

### Artifact

An EHP-SN artifact contains the outputs and provenance of a framework operation.

Its manifest is the authoritative scientific record.

## Identity and compatibility

### Component references

First-party components use references such as:

```text id="2u9ddg"
task:goaltrace/v1
model:hrm/v2
binding:goaltrace-hrm/v1
experiment:goaltrace-hrm/v1
```

The `vN` suffix is the component specification version. It changes when the component’s scientific meaning or public contract changes.

Component specification versions are separate from:

- package releases;
- Git revisions;
- configuration digests;
- run identifiers;
- checkpoints;
- trained-model registry versions.

Within the first-party catalogue, names are unique within each component kind.

External namespace syntax will be defined before third-party publication is supported.

### Compatibility

Bindings declare exact supported task–model combinations.

```yaml id="lfjxfk"
task: task:goaltrace/v1
model: model:hrm/v2
support: supported
maturity: declared
```

Support is either:

| Support       | Meaning                                             |
| ------------- | --------------------------------------------------- |
| `supported`   | Accepted for framework use at the recorded maturity |
| `unsupported` | Explicitly considered and rejected                  |

No declaration means that the combination is unavailable for framework use. It does not imply scientific impossibility.

Compatibility maturity is:

| Maturity      | Meaning                                              |
| ------------- | ---------------------------------------------------- |
| `declared`    | Support is asserted by the binding specification     |
| `implemented` | Construction and basic execution exist               |
| `validated`   | Conformance and scientific validation evidence exist |
| `reference`   | Used in a reference reproduction                     |

A component's own maturity progresses through five stages:

```text id="j0v4u4"
Planned
→ Specified
→ Implemented
→ Validated
→ Reference
```

**Reference** maturity means the component has been validated in a reproducible published experiment.

## Scientific and execution configuration

### Protocols

Protocols describe scientifically meaningful procedures.

A training protocol may define:

- duration;
- validation cadence;
- checkpoint-selection policy;
- curriculum or phases;
- objective scheduling;
- memory policy.

An evaluation protocol defines named regimes.

Each evaluation regime may define:

- data source or split;
- sampling policy;
- selected metrics;
- primary outcomes;
- validity rules;
- trace requirements.

The evaluation request selects one declared regime:

```python id="rkwpvy"
evaluation = evaluate(
    experiment,
    checkpoint=checkpoint,
    regime="test",
)
```

It cannot redefine that regime’s scientific semantics.

The initial architecture assigns one training protocol to each experiment and allows several named evaluation regimes.

### Metrics and traces

The experiment declares the metric specifications available to its protocols.

Each evaluation regime selects which declared metrics it computes and which are primary outcomes.

A regime cannot reference a metric that the experiment has not declared.

Training telemetry is separate from scientific evaluation metrics.

Traces identify the model or task observations that execution must record. Post-hoc analyses can consume those traces without changing the original evaluation.

### Seeds and data identity

| Seed kind                                     | Owner                                       |
| --------------------------------------------- | ------------------------------------------- |
| Fixed dataset or benchmark generation         | Data, substrate, or benchmark specification |
| Model initialisation and replicate randomness | Training or evaluation request              |
| Online task or evaluation sampling            | Request and resulting artifact              |

Changing a fixed-data generation seed changes the identity of the generated data.

Run-level seeds may be derived from a master seed:

```python id="9dgftk"
SeedConfiguration.from_master(42)
```

Resolved role-specific seeds are recorded in the resulting artifact.

### Execution configuration

Execution configuration describes how a protocol is carried out.

It includes:

- device selection;
- precision;
- distributed strategy;
- process launch;
- tracking backend;
- artifact persistence.

Changing execution infrastructure does not change the scientific experiment, provided that it preserves the protocol’s semantics.

## Composition and execution

### Direct Python composition

Experiments may be built directly through package-owned factories or specification constructors.

```python id="7ib7w3"
experiment = arena_tem_v1(
    training=TrainingProtocol(max_steps=50_000),
)
```

### Configured composition

The same experiment may be composed through Hydra:

```bash id="8908xs"
ehp-sn train \
    experiment=arena-tem/v1 \
    protocol.training.max_steps=50000 \
    seeds.master=42 \
    runtime=cuda
```

Both paths use the same resolution chain:

```text id="f5wb2y"
component resolvers
→ package-owned constructors
→ compatibility checks
→ experiment validation
```

Hydra provides configuration, not an alternative semantics.

### Configuration ownership

Packages ship:

- typed configuration models;
- component resolvers;
- package-owned defaults;
- constructors;
- compatibility declarations.

Repository-level configuration supplies:

- workspace defaults;
- exact reproduction overrides;
- machine-specific runtime settings;
- study search spaces;
- local tracking and persistence settings.

An installed package must not require the monorepo root to construct its public components.

### Runtime boundary

EHP-SN controls the scientific training and evaluation lifecycle.

Lightning Fabric is the default runtime backend for:

- device placement;
- precision;
- distributed execution;
- process launch;
- gradient execution;
- runtime checkpoint operations.

Fabric does not define EHP-SN experiment, protocol, metric, or artifact semantics.

## Artifacts and analysis

The framework owns:

- artifact schemas;
- manifest construction;
- staging;
- validation;
- local commitment;
- logical artifact references;
- inspection.

Physical persistence may use the local filesystem or an external adapter.

MLflow may index runs or persist artifact content. It does not replace the EHP-SN manifest as the authoritative scientific record.

Scientific analyses operate over committed artifacts.

```python id="kg71d5"
analysis = analyze(
    artifacts=[evaluation.artifact],
    analyses=["memory-diagnostics"],
)
```

The framework defines artifact loading and analysis-execution contracts.

Research packages define the scientific analyses, figures, comparisons, and report content.

Adding a new post-hoc plot does not require a new experiment version unless different observables must be recorded.

## Logical framework areas

The framework is organized conceptually into four areas.

```text id="h1141d"
Core contracts
    identity, tasks, models, bindings, protocols, metrics

Composition and execution
    experiments, configuration, runtime, training, evaluation

Records and analysis
    reproducibility, artifacts, inspection, analysis requests

Optional integrations
    tracking, studies, metric adapters, persistence, registry
```

This is a logical responsibility map rather than a required physical package layout.

## Extensions and integrations

| Integration      | Role                                          |
| ---------------- | --------------------------------------------- |
| PyTorch          | Required tensor and model foundation          |
| Lightning Fabric | Default runtime backend                       |
| Hydra            | Default configuration frontend                |
| Pydantic         | External and serialized boundary validation   |
| MLflow Tracking  | Optional tracking and persistence adapter     |
| TorchMetrics     | Optional distributed metric adapter           |
| Optuna           | Initial backend for provisional study support |
| Typer            | Intended CLI frontend                         |

Generalized reporting, model registration, and broadly reusable study orchestration remain provisional.

MLflow Model Registry is a candidate persistence backend rather than part of the stable core contract.

## Capability status

| Capability                                        | Status                               |
| ------------------------------------------------- | ------------------------------------ |
| Core component contracts                          | Specified                            |
| Component identity and compatibility              | Specified                            |
| Experiment, protocol, request, and run boundaries | Specified                            |
| Metric, trace, and seed ownership                 | Specified                            |
| Direct and configured composition                 | Specified                            |
| Training and evaluation workflow                  | Specified                            |
| Local artifact manifests and inspection           | Specified                            |
| Analysis-execution contracts                      | Specified                            |
| Lightning Fabric and Hydra integrations           | Specified                            |
| MLflow Tracking and TorchMetrics adapters         | Optional, specified                  |
| Study orchestration                               | Provisional                          |
| Generalized reporting and model registry          | Planned                              |
| Typer–Hydra CLI integration                       | Specified; proof of concept required |

`Specified` means that semantics and responsibilities are documented. It does not imply implementation or validation.

## Installation

Requirements:

- Python 3.12 or later

Install the framework package in editable mode:

```bash id="23f3vo"
python -m pip install -e packages/ehp-sn
```

## Testing

Run the available framework tests from the repository root:

```bash id="7xg2tb"
python -m pytest packages/ehp-sn
```

Tests are added alongside implemented contracts and services.

Intended coverage includes:

- component identity and compatibility;
- experiment immutability;
- protocol and regime ownership;
- request resolution;
- metric and seed ownership;
- Python and configured composition equivalence;
- artifact authority;
- analysis execution.

## License

`ehp_sn` is distributed under the GNU General Public License v3.0. See the repository [`LICENSE`](../../LICENSE).

See the repository-level [README](../../README.md) for repository orientation.
