---
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# `ehp-sn analyze`

Execute an available scientific analysis over committed artifacts.

## Overview

Use `ehp-sn analyze` after evaluation has produced the metrics, cases, predictions, or traces required by an analysis. The command consumes one or more committed artifacts and produces an immutable analysis artifact containing derived results, tables, figure data, and scientific figures.

```text
evaluation artifact
        ↓
ehp-sn analyze
        ↓
analysis artifact
        ↓
report or notebook consumption
```

`analyze` owns derived scientific results, cross-case or explicitly supported cross-regime computations, analysis tables, and scientific figures derived from recorded artifacts. It does not rerun model inference, recompute primary evaluation metrics, or package final reports.

The initial stable target is a single analysis from the installed component catalogue consuming one evaluation artifact. Multi-artifact analysis is supported only when the selected analysis explicitly declares it.

## Usage

```console
ehp-sn analyze COMMAND [OPTIONS]
```

| Command             | Purpose                                       |
| ------------------- | --------------------------------------------- |
| `list`              | List available analyses                       |
| `show ANALYSIS`     | Describe one analysis and its required inputs |
| `plan ANALYSIS`     | Resolve inputs and outputs without execution  |
| `validate ANALYSIS` | Validate artifact compatibility               |
| `run ANALYSIS`      | Execute the analysis                          |
| `inspect ARTIFACT`  | Inspect an analysis artifact                  |

## Analysis identity and reuse

Analysis identity includes ordered input identities and verified digests, analysis version, semantic parameters, rendering parameters, selected figures, renderer version, and figure output format. The manifest may additionally expose a `scientific_result_id` that excludes presentation-only fields.

A verified result may be reused only when the analysis declares deterministic, idempotent behavior and every identity-affecting field matches. Reuse reports `action = "reused"` and does not modify provenance.

## `list`

List scientific analyses available to the current installation.

```console
ehp-sn analyze list [--format text|json]
```

### Outputs

The command reports each analysis reference, purpose, maturity, accepted input artifact kinds, and principal outputs.

### Example

```console
ehp-sn analyze list
```

The result includes `memory-diagnostics` when the corresponding research analysis is installed.

### Errors

- Analysis catalogue cannot be loaded.
- An analysis definition is invalid or unavailable.

## `show ANALYSIS`

Describe one analysis without resolving concrete artifacts.

```console
ehp-sn analyze show ANALYSIS [--format text|json]
```

### Arguments

| Argument   | Required | Description                                                             |
| ---------- | -------- | ----------------------------------------------------------------------- |
| `ANALYSIS` | Yes      | Canonical analysis reference, such as `analysis:memory-diagnostics/v1`, |

### Outputs

The command reports:

- analysis identity, version, maturity, and scientific purpose;
- accepted input artifact kinds and cardinality;
- required metrics, cases, predictions, or traces;
- configurable parameters;
- derived outputs, tables, and figures;
- determinism or ordering requirements.

### Example

```console
ehp-sn analyze show analysis:memory-diagnostics/v1
```

The result describes which Arena–TEM traces are required and which diagnostic tables and figures are produced.

### Errors

- Analysis is unknown or ambiguous.
- Analysis definition is invalid.

## `plan ANALYSIS`

Resolve one analysis request without executing computations or rendering figures.

```console
ehp-sn analyze plan ANALYSIS --input ARTIFACT [OPTIONS]
```

### Arguments

| Argument   | Required | Description                    |
| ---------- | -------- | ------------------------------ |
| `ANALYSIS` | Yes      | Analysis definition to execute |

### Options

| Option                | Default                  | Description                                    |
| --------------------- | ------------------------ | ---------------------------------------------- |
| `--input ARTIFACT`    | Required                 | Input artifact; repeatable only when supported |
| `--config PATH`       | Analysis defaults        | Analysis configuration                         |
| `--set KEY=VALUE`     | None                     | Typed override; repeatable                     |
| `--output PATH`       | Configured analysis root | Override the artifact destination              |
| `--format text\|json` | `text`                   | Terminal output format                         |

### Behavior

The command resolves the analysis definition and intended input artifact identities, preserves input ordering where the analysis declares it meaningful, resolves semantic analysis parameters and result identity, and reports intended tables, derived resources, and figures. It may report missing recorded resources as warnings, but it does not require full payload readability, load complete traces, render figures, or write output. Resource availability belongs to `analyze validate`.

### Inputs

- analysis definition from the installed component catalogue;
- one evaluation artifact for the initial stable contract;
- additional artifacts only for analyses that explicitly support them;
- optional analysis configuration.

### Outputs

- resolved input identities and digests;
- required and available resources;
- effective parameters;
- intended derived outputs and figures;
- expected destination;
- compatibility warnings.

### Example

```console
ehp-sn analyze plan analysis:memory-diagnostics/v1 \
    --input artifacts/evaluations/arena-tem/test-001
```

The command reports the traces required for memory diagnostics, whether their identities are declared by the input manifest, and the outputs that would be produced. Payload availability is checked by `analyze validate`.

### Errors

- Analysis or input-artifact reference is malformed, unknown, or ambiguous.
- The resolved input identity declares an unsupported artifact kind.
- The input manifest cannot establish required resource identities.
- Too many or too few inputs are supplied.
- Analysis configuration is invalid.

Resources declared by the manifest but unavailable on the current machine are reported as warnings. `analyze validate` performs the required payload checks.

## `validate ANALYSIS`

Validate concrete analysis inputs and configuration without executing the analysis.

```console
ehp-sn analyze validate ANALYSIS --input ARTIFACT [OPTIONS]
```

### Options

`validate` accepts the same resolution options as `plan`.

### Behavior

The command verifies manifest integrity, artifact compatibility, required resource availability, parameter validity, deterministic ordering requirements, output writability, and existing-output conflicts. It does not create an analysis artifact.

### Outputs

A validation report with pass/fail status, resolved identities, missing resources, warnings, and corrective guidance.

### Example

```console
ehp-sn analyze validate memory-diagnostics \
    --input artifacts/evaluations/arena-tem/test-001
```

The command confirms whether the selected evaluation artifact is sufficient for the analysis.

### Errors

- Any resolution error described by `plan`.
- Input manifest or resource validation fails.
- Output destination is unavailable or conflicting.

## `run ANALYSIS`

Execute one validated analysis and commit its artifact.

```console
ehp-sn analyze run ANALYSIS --input ARTIFACT [OPTIONS]
```

### Options

`run` accepts the same options as `plan`, plus `--quiet` to suppress progress and non-essential analysis telemetry while preserving errors and the final analysis result. It does not rerun evaluation when required data is missing.

### Behavior

1. Resolves the analysis and input artifacts.
2. Validates required recorded resources.
3. Creates a staging location.
4. Computes declared derived scientific results.
5. Produces analysis tables and figure-ready resources.
6. Renders declared scientific figures when the analysis includes them.
7. Validates the completed artifact.
8. Atomically commits the artifact and prints its reference.

An analysis artifact may be reused only when the analysis declares deterministic, idempotent behavior and every identity-affecting field matches: ordered input identities and verified digests, analysis version, semantic parameters, rendering parameters, selected figures, renderer version, and figure output format. A matching `scientific_result_id` alone is insufficient to reuse a rendered analysis artifact.

For the initial CLI contract, rendering parameters are part of the analysis request. Changing format, DPI, labels, theme, renderer version, or selected figures therefore produces a different analysis artifact. The manifest may additionally record a shared `scientific_result_id` derived only from scientific inputs, analysis version, and semantic parameters. A separate rendering-projection command is not part of the initial interface.

### Inputs

- all inputs reported by `analyze plan`;
- recorded artifact resources only;
- analysis implementation and version.

### Outputs

A typical artifact contains:

```text
artifacts/analyses/<analysis>/<analysis-id>/
├── manifest.json
├── request.resolved.toml
├── provenance.json
├── tables/
├── figures/
├── derived/
└── _SUCCESS
```

The exact resources are declared by the analysis definition.

### Example

```console
ehp-sn analyze run analysis:memory-diagnostics/v1 \
    --input artifacts/evaluations/arena-tem/test-001 \
    --output artifacts/analyses/arena-tem/memory-diagnostics
```

On success, the command creates a memory-diagnostics artifact from the recorded evaluation traces without rerunning inference.

### Errors

- Required recorded resources are missing.
- Input artifacts are incompatible or unordered incorrectly.
- Derived computation or figure rendering fails.
- Output conflicts with an existing analysis artifact.
- Artifact validation or commitment fails.

## `inspect ARTIFACT`

Inspect an existing analysis artifact without modifying it.

```console
ehp-sn analyze inspect ARTIFACT [--format text|json]
```

### Outputs

The command reports analysis identity, input artifacts, parameters, derived tables, figure catalogue, provenance, and validation status. It does not provide general interactive exploration or modify the artifact.

### Example

```console
ehp-sn analyze inspect artifacts/analyses/arena-tem/memory-diagnostics
```

The result lists the analysis inputs and available tables and figures.

### Errors

- Artifact cannot be read or is incomplete.
- Artifact kind is not an analysis artifact.

## Related commands

- [`evaluate`](evaluate.md) — produces the primary input artifacts.
- [`report`](report.md) — packages analysis outputs for presentation or export.

## See also

- [Configuration interface](../configuration/_index.md)
- [Framework semantics](../../framework/_index.md)
- [Architecture overview](../../architecture/_index.md)
