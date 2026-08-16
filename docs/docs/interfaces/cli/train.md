---
title: "`ehp-sn train`"
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# `ehp-sn train`

Plan, validate, and execute model training from an experiment definition.

## Overview

Use `ehp-sn train` after the experiment's required task data exists. The command consumes an experiment definition, its declared training protocol, prepared task data, and optional checkpoint state. It produces a versioned run artifact containing resolved configuration, checkpoints, metrics, logs, and provenance.

Training uses the experiment as its scientific identity. It does not maintain a separate public training-recipe catalogue.

## Usage

```console
ehp-sn train COMMAND [OPTIONS]
```

The `train` command group provides these commands:

| Command               | Purpose                                          |
| --------------------- | ------------------------------------------------ |
| `list`                | List experiments that declare training protocols |
| `show EXPERIMENT`     | Show an experiment's training definition         |
| `plan EXPERIMENT`     | Resolve a training request without executing     |
| `validate EXPERIMENT` | Validate configuration and prerequisites         |
| `run EXPERIMENT`      | Execute one training run                         |

## `list`

List experiments available for training.

```console
ehp-sn train list [--format text|json]
```

### Outputs

The command reports each experiment reference, task, model, binding, training-protocol maturity, and short description.

### Example

```console
ehp-sn train list
```

The result includes `experiment:arena-tem/v1` when the Arena–TEM experiment definition is installed.

### Errors

- Experiment catalogue cannot be loaded.
- An experiment definition is present but invalid.

## `show EXPERIMENT`

Display the training-relevant part of one experiment definition.

```console
ehp-sn train show EXPERIMENT [--format text|json]
```

### Arguments

| Argument     | Required | Description                    |
| ------------ | -------- | ------------------------------ |
| `EXPERIMENT` | Yes      | Canonical experiment reference |

### Outputs

The command reports:

- resolved experiment, task, model, and binding references;
- training protocol and maturity;
- required task data;
- declared objectives and checkpoint-selection policy;
- configuration entry points;
- supported runtime requirements.

It does not resolve one concrete run or access training data.

### Example

```console
ehp-sn train show experiment:arena-tem/v1
```

The result describes the standard Arena–TEM training protocol and its required Arena corpus.

### Errors

- Experiment reference is unknown or ambiguous.
- Experiment does not declare a training protocol.
- Experiment definition is internally invalid.

## Public resume compatibility

A checkpoint declares one capability: `resumable`, `initialization-only`, or `inference-only`.

| Category                                                  | Resume rule                                                                  |
| --------------------------------------------------------- | ---------------------------------------------------------------------------- |
| Experiment, task data, and model structure                | Must match                                                                   |
| Optimizer and scheduler semantics                         | Must match unless protocol explicitly permits a compatible change            |
| Completed-step and phase history                          | Must match checkpoint record                                                 |
| Logging frequency, verbosity, and monitoring presentation | May change                                                                   |
| Output placement                                          | May change while remaining in the same lineage                               |
| Device topology and precision                             | Protocol-defined; resolved changes are reported and recorded                 |
| Source revision                                           | Must match unless an explicit compatibility policy is declared and validated |

`--resume` requires a `resumable` checkpoint with model, optimizer, scheduler, step, and protocol state. `--init-from` accepts only checkpoints that explicitly permit initialization. Incompatible capability or metadata is rejected before a run artifact is created. Successful resume reports `action = "resumed"`.

## `plan EXPERIMENT`

Resolve one concrete training request without constructing the full runtime or starting training.

```console
ehp-sn train plan EXPERIMENT [OPTIONS]
```

### Arguments

| Argument     | Required | Description                    |
| ------------ | -------- | ------------------------------ |
| `EXPERIMENT` | Yes      | Experiment definition to train |

### Options

| Option                    | Default                       | Description                                |
| ------------------------- | ----------------------------- | ------------------------------------------ |
| `--config PATH`           | Experiment defaults           | Additional training configuration          |
| `--set KEY=VALUE`         | None                          | Typed override; repeatable                 |
| `--output PATH`           | Configured run root           | Override the run artifact destination      |
| `--seed INT`              | Configured seed policy        | Override the master run seed               |
| `--device DEVICE`         | `auto`                        | Runtime device selection                   |
| `--precision POLICY`      | Experiment or runtime default | Runtime precision                          |
| `--hardware-profile NAME` | None                          | Named runtime preset                       |
| `--resume CHECKPOINT`     | None                          | Continue an existing training lineage      |
| `--init-from CHECKPOINT`  | None                          | Initialize a new run from model parameters |
| `--format text\|json`     | `text`                        | Terminal output format                     |

`--seed INT` sets the master run seed and overrides the corresponding configured master-seed field. Supplying both `--seed` and a `--set` override for that same field is rejected as ambiguous.

A hardware profile is a CLI-only convenience: it must expand into the same canonical runtime request fields (such as `device` and `precision`) that `--device` and `--precision` set directly, per [Interfaces](../index.md). Explicit options such as `--device` and `--precision` override corresponding profile values and do not modify the scientific experiment.

`--hardware-profile` is training-only in the initial CLI.
It may supply defaults only for canonical runtime fields already defined by EHP-SN (such as `device` and `precision`); it does not define distributed-launch, process-topology, launcher, or coordination semantics unless those semantics are first represented by canonical framework-owned configuration fields.
Evaluation and analysis use direct runtime options until a concrete workflow demonstrates the need for shared profiles.

### Behavior

The command resolves the experiment and component references, composes the training protocol and configuration, resolves the intended task-data and checkpoint identities, derives role-specific seeds, checks task–model–binding compatibility, determines the run destination, and reports reproducibility or conflict warnings. It does not require all referenced resources to be readable and does not instantiate the complete model and data runtime; resource availability belongs to `train validate --level resources`.

`--resume` and `--init-from` are mutually exclusive. Resume continues the same logical lineage. Only fields classified as resume-compatible by the training protocol may change. Scientific composition, task-data identity, model structure, optimizer family, and completed-step history must not be silently changed. Initialization starts a new lineage and loads only parameter groups permitted by the model contract.

### Inputs

- experiment definition;
- task corpus or data declared by the experiment;
- optional configuration overrides;
- optional checkpoint for resume or initialization;
- selected runtime profile.

### Outputs

- resolved training request;
- configuration provenance;
- seed allocation;
- expected run destination;
- input and checkpoint identities;
- warnings and intended actions.

### Example

```console
ehp-sn train plan experiment:arena-tem/v1 \
    --set protocol.training.max_steps=50000 \
    --seed 42 \
    --device cuda
```

The command prints the resolved Arena–TEM run, selected Arena corpus, derived seeds, runtime placement, and expected output path without training.

### Errors

- Experiment, task-corpus, or checkpoint reference is malformed, unknown, or ambiguous.
- Configuration or override is invalid.
- Task, model, and binding definitions are incompatible.
- Resume metadata is definitionally incompatible with the original run.
- `--resume` and `--init-from` are supplied together.

A resolved corpus or checkpoint whose payload is unavailable is reported as a warning. `train validate --level resources` performs the required readability checks.

## `validate EXPERIMENT`

Validate a training request at a selected depth.

```console
ehp-sn train validate EXPERIMENT [--level config|resources|build] [OPTIONS]
```

### Options

`validate` accepts the same resolution options as `plan`, plus:

| Option                             | Default     | Description      |
| ---------------------------------- | ----------- | ---------------- |
| `--level config\|resources\|build` | `resources` | Validation depth |

### Behavior

Each validation level performs these checks:

| Level       | Checks                                                                               |
| ----------- | ------------------------------------------------------------------------------------ |
| `config`    | Experiment composition, schemas, overrides, and compatibility                        |
| `resources` | All `config` checks plus data, checkpoints, device availability, and writable output |
| `build`     | All `resources` checks plus model/data construction and a minimal forward-path check |

Validation must complete before a run directory is published. A failed validation does not begin training.

### Outputs

A validation report with pass/fail status, resolved identities, warnings, and user-actionable errors.

### Example

```console
ehp-sn train validate experiment:arena-tem/v1 --level build
```

The command constructs the Arena–TEM training path and verifies one minimal batch without performing a training step.

### Errors

- Any resolution error described by `plan`.
- Runtime device is unavailable.
- Model or data construction fails.
- Minimal forward-path validation fails.

## `run EXPERIMENT`

Execute one validated training request and commit its run artifact.

```console
ehp-sn train run EXPERIMENT [OPTIONS]
```

### Options

`run` accepts the same resolution options as `plan`, plus `--quiet` to suppress progress bars and non-essential training telemetry while preserving errors and the final run result. It does not support a separate `--dry-run`; use `train plan` instead.

### Behavior

1. Resolves the request using the same path as `plan`.
2. Performs configured prerequisite validation.
3. Constructs the task data, binding, model, objective, and runtime.
4. Executes the experiment's training protocol.
5. Records metrics and checkpoints.
6. Selects checkpoints according to the declared policy.
7. Finalizes provenance and the run manifest.
8. Commits the run artifact and prints its reference.

Every non-resumed invocation creates a new run identity, even when its experiment, configuration, inputs, and seed match an earlier run. Training interruption must not make an incomplete run appear successfully completed. Recoverable checkpoint state may be retained for explicit resume.

### Inputs

- all inputs reported by `train plan`;
- training runtime and required dependencies;
- optional resume or initialization checkpoint.

### Outputs

A run artifact containing at least:

- resolved experiment and request configuration;
- source revision and environment information;
- role-specific seeds;
- checkpoints;
- training and validation telemetry;
- logs and diagnostics;
- final status and provenance manifest.

The default destination is defined by workspace or experiment configuration unless `--output` is supplied.

### Example

```console
ehp-sn train run experiment:arena-tem/v1 \
    --set protocol.training.max_steps=50000 \
    --seed 42 \
    --device cuda
```

On success, the command commits an Arena–TEM run artifact and prints the run reference and selected checkpoint references.

### Advanced example: resume

```console
ehp-sn train run experiment:arena-tem/v1 \
    --resume runs/arena-tem/run-001/checkpoints/last.ckpt
```

The command validates the original run identity and continues the same training lineage from its saved state.

### Errors

- Experiment, task corpus, or checkpoint cannot be resolved.
- Configuration or compatibility validation fails.
- Output conflicts with an existing run.
- Device, precision, or distributed runtime cannot be initialized.
- Training execution fails.
- Checkpoint or artifact publication fails.

## Related commands

- [`tasks`](tasks.md) — produces the task corpora consumed by training.
- [`evaluate`](evaluate.md) — evaluates checkpoints produced by training.

## See also

- [Configuration interface](../configuration/index.md)
- [Framework semantics](../../framework/index.md)
- [Architecture overview](../../architecture/index.md)
