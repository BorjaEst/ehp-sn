---
authority: provisional
status: provisional
api_stability: provisional
---

# `ehp-sn report`

> **Provisional.** This command group should not become stable until at least two completed experiment workflows demonstrate shared reporting requirements. Command names and package details on this page are proposed rather than implementation commitments.
> See the [CLI overview](_index.md) for shared help, configuration, output, and error conventions.

Package existing evaluation and analysis results for presentation or export.

## Overview

Use `ehp-sn report` when scientific results have already been computed and need to be assembled into a portable presentation package or exported document. The command consumes committed evaluation or analysis artifacts and produces a report package or an export. It does not run training, inference, evaluation, or new scientific analyses.

```text
evaluation and analysis artifacts
        ↓
ehp-sn report
        ↓
report package
        ↓
exported document
```

`report` may select already-computed tables and figures, apply presentation templates, assemble a package, export delivery formats, and preserve provenance. It must not compute primary metrics, generate new scientific conclusions, or modify source artifacts.

The exact report-package standard and supported export formats remain provisional. Report packages are proposed replaceable presentation projections, not authoritative scientific artifacts; their source evaluation and analysis artifacts remain immutable and authoritative.

For this reason, report operations may expose `--overwrite`. Authoritative data, task, training, evaluation, and analysis artifacts use immutable publication rules and may expose only `--replace-incomplete` for failed staging state.

## Usage

```console
ehp-sn report COMMAND [OPTIONS]
```

| Command           | Purpose                                      |
| ----------------- | -------------------------------------------- |
| `plan SOURCE`     | Resolve a report build without writing       |
| `build SOURCE`    | Build a proposed report package              |
| `validate REPORT` | Validate an existing proposed report package |
| `inspect REPORT`  | Inspect package contents and provenance      |
| `export REPORT`   | Export a package to a delivery format        |

## `plan SOURCE`

Resolve one report build without writing a package.

```console
ehp-sn report plan SOURCE --output PATH [OPTIONS]
```

### Arguments

| Argument | Required | Description                                          |
| -------- | -------- | ---------------------------------------------------- |
| `SOURCE` | Yes      | Evaluation or analysis artifact used as report input |

The initial contract accepts one source artifact. Multi-source reports remain provisional.

### Options

| Option                  | Default         | Description                                       |
| ----------------------- | --------------- | ------------------------------------------------- |
| `--output PATH`         | Required        | Destination of the report package                 |
| `--config PATH`         | Report defaults | Report-build configuration                        |
| `--report-profile NAME` | None            | Presentation profile selecting existing resources |
| `--format text\|json`   | `text`          | Terminal output format                            |

### Behavior

The command resolves the source identity and manifest-level resource declarations, selects existing metrics, tables, and figures according to the configuration or report profile, determines the destination, and reports unavailable payloads or conflicts. It does not require every payload to be readable, compute new scientific quantities, or write output. `report build` performs the required payload checks.

### Inputs

- one committed evaluation or analysis artifact;
- optional report configuration or profile.

### Outputs

- resolved source identity;
- selected package resources;
- expected destination and package contents;
- provenance links;
- warnings and conflicts.

### Example

```console
ehp-sn report plan artifacts/analyses/arena-tem/memory-diagnostics \
    --output artifacts/reports/arena-tem
```

The command lists the existing tables and figures that would be included in the Arena–TEM report package.

### Errors

- Source reference is malformed, unknown, or ambiguous.
- Source manifest cannot establish the resource identities required by the selected profile.
- Destination conflicts with an existing report.

A declared source resource whose payload is unavailable is reported as a warning. `report build` performs the required readability checks.

## `build SOURCE`

Build and commit one report package from existing scientific outputs.

```console
ehp-sn report build SOURCE --output PATH [OPTIONS]
```

### Options

| Option                  | Default         | Description                                                                       |
| ----------------------- | --------------- | --------------------------------------------------------------------------------- |
| `--output PATH`         | Required        | Destination report package                                                        |
| `--config PATH`         | Report defaults | Report-build configuration                                                        |
| `--report-profile NAME` | None            | Presentation profile                                                              |
| `--overwrite`           | Disabled        | Replace an existing report projection; never modifies source scientific artifacts |
| `--format text\|json`   | `text`          | Terminal result format                                                            |

### Behavior

1. Resolves and validates the source artifact.
2. Selects already-computed resources.
3. Creates a staging package.
4. Copies or references selected tables and figures according to the package contract.
5. Writes package metadata and source provenance.
6. Validates package structure and references.
7. Atomically publishes the report package.

`build` does not rerun analysis or rerender scientific figures unless a future accepted package specification explicitly defines presentation-only rendering from existing figure data.

### Inputs

- all inputs reported by `report plan`.

### Outputs

At minimum, a report package must contain:

- package manifest;
- source artifact references and provenance;
- catalogue of included resources;
- selected tables and figures or stable references to them;
- completion and validation status.

The exact filenames remain provisional until the report-package specification is accepted.

### Example

```console
ehp-sn report build artifacts/analyses/arena-tem/memory-diagnostics \
    --output artifacts/reports/arena-tem
```

On success, the command creates a portable package containing the selected Arena–TEM analysis outputs.

### Errors

- Source is missing, incomplete, or incompatible.
- Required report resource is unavailable.
- Destination exists and `--overwrite` is not supplied.
- Package validation or publication fails.

## `validate REPORT`

Validate a report package without rebuilding it.

```console
ehp-sn report validate REPORT [--format text|json]
```

### Arguments

| Argument | Required | Description                                        |
| -------- | -------- | -------------------------------------------------- |
| `REPORT` | Yes      | Report package path or accepted artifact reference |

### Behavior

The command verifies the currently proposed package metadata, source provenance, declared resource paths, completion state, and structural invariants. Its exact checks remain provisional until a report-package specification is accepted. It does not validate the original scientific computations beyond checking their referenced artifact identities.

### Outputs

A validation report with pass/fail status, missing or invalid resources, and warnings.

### Example

```console
ehp-sn report validate artifacts/reports/arena-tem
```

The command reports whether the package is complete and internally consistent.

### Errors

- Report does not exist or is unreadable.
- Package format or version is unsupported.
- Declared resources or source references are missing.

## `inspect REPORT`

Display report contents and provenance without modifying the package.

```console
ehp-sn report inspect REPORT [--format text|json]
```

### Outputs

The command reports package identity, source artifacts, included tables and figures, profile or configuration, export history when recorded, and validation status.

### Example

```console
ehp-sn report inspect artifacts/reports/arena-tem
```

The result lists the report's source analysis artifact and included resources.

### Errors

- Report package or manifest cannot be read.
- Package is incomplete or unsupported.

## `export REPORT`

Create a delivery artifact from an existing report package.

```console
ehp-sn report export REPORT --export-format FORMAT --output PATH [OPTIONS]
```

### Options

| Option                   | Default  | Description                               |
| ------------------------ | -------- | ----------------------------------------- |
| `--export-format FORMAT` | Required | Accepted delivery format                  |
| `--output PATH`          | Required | Export file or directory                  |
| `--overwrite`            | Disabled | Explicitly replace the export destination |
| `--format text\|json`    | `text`   | Terminal result format                    |

### Behavior

The command validates the report package, renders or serializes only presentation-level content defined by the package, writes the export to a separate destination, and records source provenance when the export format permits it. The report package is the immediate source for the export, but neither the package nor the export supersedes the authoritative evaluation and analysis artifacts.

### Example

```console
ehp-sn report export artifacts/reports/arena-tem \
    --export-format html \
    --output exports/arena-tem.html
```

The command creates an HTML projection of the existing report package without changing the package or its scientific sources.

### Errors

- Report package is invalid.
- Export format is unsupported or its renderer is unavailable.
- Destination exists and `--overwrite` is not supplied.
- Export fails or produces an invalid result.

## Related commands

- [`evaluate`](evaluate.md) — may provide source evaluation artifacts.
- [`analyze`](analyze.md) — provides derived tables and figures for reports.

## See also

- [Configuration interface](../configuration/_index.md)
- [Framework semantics](../../framework/_index.md)
- [Architecture overview](../../architecture/_index.md)
