# `ehp-sn evaluate`

<!-- authority: canonical  status: specified -->

Plan, validate, and execute model evaluation for an experiment and checkpoint.
See the [CLI overview](_index.md) for shared help, configuration, output, and error conventions.

## Overview

Use `ehp-sn evaluate` after a compatible checkpoint exists. The command consumes an experiment definition, one checkpoint, and one declared evaluation regime. It performs inference and produces an immutable evaluation artifact containing metrics, validity records, cases, traces, and provenance.

Evaluation uses the experiment's declared evaluation protocol and named regimes. It does not maintain a separate public evaluation-recipe catalogue.

`evaluate` owns inference, declared primary and secondary metrics, validity records, configured traces, and case records. It does not own cross-run comparison, exploratory analysis, publication figures, or report export.

## Usage

```console
ehp-sn evaluate COMMAND [OPTIONS]
```

| Command               | Purpose                                              |
| --------------------- | ---------------------------------------------------- |
| `list`                | List experiments that declare evaluation regimes     |
| `show EXPERIMENT`     | Show an experiment's evaluation definition           |
| `plan EXPERIMENT`     | Resolve an evaluation without executing              |
| `validate EXPERIMENT` | Validate checkpoint, data, regime, and compatibility |
| `run EXPERIMENT`      | Execute evaluation and commit an artifact            |

## `list`

List experiments available for evaluation.

```console
ehp-sn evaluate list [--format text|json]
```

### Outputs

The command reports each experiment reference, task and model references, available regime names, primary metrics, and maturity.

### Example

```console
ehp-sn evaluate list
```

The result includes `experiment:arena-tem/v1` and its declared regimes when installed.

### Errors

- Experiment catalogue cannot be loaded.
- An experiment declares an invalid evaluation protocol.

## `show EXPERIMENT`

Display the evaluation-relevant part of one experiment definition.

```console
ehp-sn evaluate show EXPERIMENT [--format text|json]
```

### Arguments

| Argument     | Required | Description                    |
| ------------ | -------- | ------------------------------ |
| `EXPERIMENT` | Yes      | Canonical experiment reference |

### Outputs

The command reports:

- experiment, task, model, and binding references;
- declared regime names and purposes;
- default data or split for each regime;
- primary and secondary metrics;
- required traces and case records;
- checkpoint compatibility requirements.

### Example

```console
ehp-sn evaluate show experiment:arena-tem/v1
```

The result lists the Arena–TEM evaluation regimes and their declared outcomes.

### Errors

- Experiment is unknown or ambiguous.
- Experiment does not declare evaluation regimes.
- Evaluation protocol is invalid.

## Evaluation identity and reuse

A complete evaluation identity includes experiment and regime versions, checkpoint logical identity and verified digest, evaluation-data identity, case-selection policy and selected case IDs, evaluation seed, metric versions, trace versions, and numerically relevant runtime settings.

Changing only `--output` changes placement, not identity. Changing metrics, traces, seed, case selection, precision, or deterministic runtime settings changes request identity.

Evaluation reuse is request-identity based, not merely scientific-result based. Equivalent complete evaluations are reused only when all identity-affecting request fields match and the existing artifact is verified. Reuse reports success with `action = "reused"`, does not modify provenance, and returns the existing logical reference rather than silently copying it to another location. A conflicting valid destination exits with code `8`.

### Diagnostic case selection

`--max-cases N` creates a diagnostic request unless the regime explicitly defines `N` as complete. Cases are selected deterministically from the regime's ordered candidate set using the resolved seed and case-selection policy. Ordered selected case IDs are recorded. Diagnostic evaluations record `purpose = "diagnostic"` and cannot satisfy complete-regime or reference-result requirements.

## `plan EXPERIMENT`

Resolve one concrete evaluation request without loading the full model or running inference.

```console
ehp-sn evaluate plan EXPERIMENT --checkpoint CHECKPOINT [OPTIONS]
```

### Arguments

| Argument     | Required | Description                       |
| ------------ | -------- | --------------------------------- |
| `EXPERIMENT` | Yes      | Experiment definition to evaluate |

### Options

| Option                    | Default                                 | Description                                 |
| ------------------------- | --------------------------------------- | ------------------------------------------- |
| `--checkpoint CHECKPOINT` | Required                                | Local path or accepted checkpoint reference |
| `--regime NAME`           | Experiment default when one is declared | Named regime from the experiment protocol   |
| `--config PATH`           | Experiment defaults                     | Additional evaluation configuration         |
| `--set KEY=VALUE`         | None                                    | Typed override; repeatable                  |
| `--output PATH`           | Configured evaluation root              | Override the artifact destination           |
| `--seed INT`              | Regime or request default               | Evaluation sampling seed                    |
| `--device DEVICE`         | `auto`                                  | Runtime device                              |
| `--precision POLICY`      | Experiment or runtime default           | Runtime precision                           |
| `--max-cases INT`         | Regime default                          | Bound execution for diagnostics             |
| `--format text\|json`     | `text`                                  | Terminal output format                      |

`--seed INT` overrides the request-level evaluation sampling seed. Supplying both `--seed` and a `--set` override for the same seed field is rejected as ambiguous.

### Behavior

The command resolves the experiment and named regime, intended checkpoint identity, declared evaluation data, metrics, validity rules, case-selection policy, trace requirements, runtime settings, and destination. It checks definition-level compatibility and reports unavailable resources or reproducibility concerns as warnings, but it does not require the checkpoint and data payloads to be readable, load the full model, or run inference. Resource availability belongs to `evaluate validate`.

Changing the dataset is not a normal invocation override because it may change the scientific meaning of the evaluation. Such changes should normally be represented by an experiment or regime definition.

A `--max-cases` override creates a bounded diagnostic evaluation unless the regime explicitly declares that case count as part of a valid scientific evaluation. A bounded diagnostic request has a distinct evaluation identity, records `purpose = diagnostic`, and cannot satisfy a complete-regime or reference-result requirement.

### Inputs

- experiment definition and named regime;
- trained checkpoint;
- evaluation corpus or split declared by the regime;
- optional request-level overrides.

### Outputs

- resolved checkpoint and data identities;
- regime, metrics, validity rules, and trace plan;
- case-selection policy;
- expected destination and evaluation identity;
- compatibility and reproducibility warnings.

### Example

```console
ehp-sn evaluate plan experiment:arena-tem/v1 \
    --checkpoint runs/arena-tem/checkpoints/best.ckpt \
    --regime test
```

The command prints the checkpoint digest, Arena test corpus, selected metrics, expected case count, and target artifact path.

### Errors

- Experiment, regime, checkpoint reference, or evaluation-data reference is malformed, unknown, or ambiguous.
- Resolved checkpoint metadata identifies an incompatible model family.
- Metric, validity-rule, or trace definition is unavailable or incompatible.

A resolved checkpoint or evaluation dataset whose payload is unavailable is reported as a warning. `evaluate validate` performs the required readability and artifact checks.

## `validate EXPERIMENT`

Validate an evaluation request without running inference.

```console
ehp-sn evaluate validate EXPERIMENT --checkpoint CHECKPOINT [OPTIONS]
```

### Options

`validate` accepts the same resolution options as `plan`.

### Behavior

Validation checks:

- experiment and regime validity;
- checkpoint readability, metadata, and model-family compatibility;
- data existence, schema, and split availability;
- task–model binding compatibility;
- metric, validity-rule, and trace availability;
- runtime device and precision support;
- output writability and conflicts.

No evaluation artifact is committed when validation fails.

### Outputs

A validation report containing pass/fail status, resolved identities, warnings, and user-actionable errors.

### Example

```console
ehp-sn evaluate validate experiment:arena-tem/v1 \
    --checkpoint runs/arena-tem/checkpoints/best.ckpt \
    --regime test
```

The command verifies that the selected checkpoint can be evaluated under the Arena–TEM test regime.

### Errors

- Any resolution error described by `plan`.
- Runtime prerequisites are unavailable.
- Checkpoint, data, metrics, or traces fail compatibility checks.

## `run EXPERIMENT`

Execute one validated evaluation request and commit an immutable artifact.

```console
ehp-sn evaluate run EXPERIMENT --checkpoint CHECKPOINT [OPTIONS]
```

### Options

`run` accepts the same resolution options as `plan`, plus `--quiet` to suppress progress bars and non-essential evaluation telemetry while preserving errors and the final evaluation result. It does not support `--dry-run`; use `evaluate plan` instead.

### Behavior

1. Resolves the request using the same path as `plan`.
2. Validates the experiment, regime, checkpoint, data, and runtime.
3. Creates a staging location.
4. Loads the model and executes inference.
5. Aggregates declared metrics and validity records.
6. Captures configured cases, predictions, and traces.
7. Finalizes manifests and provenance.
8. Atomically commits the evaluation artifact.
9. Prints the artifact reference and primary outcomes.

Evaluation does not generate general publication figures. Scientific derived views and figures belong to [`analyze`](analyze.md).

### Inputs

- all inputs reported by `evaluate plan`;
- evaluation runtime and required dependencies.

### Outputs

```text
artifacts/evaluations/<experiment>/<evaluation-id>/
├── manifest.json
├── request.resolved.toml
├── provenance.json
├── metrics.json
├── cases/
├── traces/
└── _SUCCESS
```

The artifact records whether the run used the complete regime or a bounded diagnostic case selection. Diagnostic artifacts may be consumed only by analyses that explicitly accept diagnostic inputs and must not be presented as complete reference evaluations.

### Example

```console
ehp-sn evaluate run experiment:arena-tem/v1 \
    --checkpoint runs/arena-tem/checkpoints/best.ckpt \
    --regime test
```

On success, the command commits the Arena–TEM test artifact, prints its reference, and displays the primary metrics.

### Advanced example: bounded diagnostic run

```console
ehp-sn evaluate run experiment:arena-tem/v1 \
    --checkpoint runs/arena-tem/checkpoints/best.ckpt \
    --regime test \
    --max-cases 32
```

The resulting artifact is explicitly marked as a bounded diagnostic evaluation rather than a complete reference result.

### Errors

- Experiment, regime, checkpoint, or data cannot be resolved.
- Compatibility or validation fails.
- Output conflicts with an existing immutable evaluation.
- Inference or metric aggregation fails.
- Required traces cannot be captured.
- Artifact commitment fails.

## Related commands

- [`train`](train.md) — produces checkpoints consumed by evaluation.
- [`analyze`](analyze.md) — consumes committed evaluation artifacts.

## See also

- [Configuration interface](../configuration/_index.md)
- [Framework semantics](../../framework/_index.md)
- [Architecture overview](../../architecture/_index.md)
