---
title: "`ehp-sn data`"
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# `ehp-sn data`

Generate, validate, and inspect immutable interim substrates.

## Overview

Use `ehp-sn data` when a research workflow needs a versioned environment or topology artifact before task-specific episodes, targets, or supervision are created.
The command consumes a substrate definition and generation configuration and produces an immutable artifact under the configured interim-data root.

```text
external or synthetic source
        ↓
ehp-sn data
        ↓
data/interim/<family>/<variant>/v<N>/
        ↓
ehp-sn tasks
```

`ehp-sn data` orchestrates substrate generation: it resolves and invokes the installed substrate definitions, produces immutable interim artifacts with manifests, provenance, checksums, and validation, and manages release coordinates.
The scientific semantics it operates on — topology generation, environment-level observations, source normalization, and intrinsic split assignment — are owned by the research substrate specifications (`docs/authority.md` § "Authority map").
Task episodes, learning targets, model tokenization, training batches, and task scoring are outside its scope.

## Usage

```console
ehp-sn data COMMAND [OPTIONS]
```

The `data` command group provides these commands:

| Command             | Purpose                                               |
| ------------------- | ----------------------------------------------------- |
| `list`              | List available substrate generators                   |
| `show TARGET`       | Describe one generator and its configuration contract |
| `plan TARGET`       | Resolve a build without writing data                  |
| `build TARGET`      | Build one immutable substrate artifact                |
| `validate ARTIFACT` | Validate an existing substrate artifact               |
| `inspect ARTIFACT`  | Display artifact metadata and bounded samples         |

## `list`

List the substrate generators available to the current installation.

```console
ehp-sn data list [--format text|json]
```

### Outputs

The command prints each target name, substrate kind, maturity, default configuration when available, and a short description.
It does not access or modify generated data.

### Example

```console
ehp-sn data list
```

The result includes first-party targets such as `obsfield` and `dagflow` when their definitions are installed.

### Errors

- No data catalogue is available — verify that the research package is installed.
- A registered definition cannot be loaded — inspect the reported definition and installation error.

## `show TARGET`

Describe one substrate generator without materializing an artifact.

```console
ehp-sn data show TARGET [--format text|json]
```

### Arguments

| Argument | Required | Description                                  |
| -------- | -------- | -------------------------------------------- |
| `TARGET` | Yes      | Substrate generator name, such as `obsfield` |

### Outputs

The command reports the target reference, purpose, maturity, supported source kind, configuration fields, output artifact kind, and default path convention.
Complete configuration schemas belong in the substrate specification and are not reproduced here.

### Example

```console
ehp-sn data show obsfield
```

The result explains what ObsField generation consumes and the kind of interim substrate it produces.

### Errors

- Unknown target — run `ehp-sn data list` and select an available name.
- Definition unavailable — install or repair the package that supplies the target.

## `plan TARGET`

Resolve one substrate build and display the intended work without writing data.

```console
ehp-sn data plan TARGET --config PATH [OPTIONS]
```

### Arguments

| Argument | Required | Description                    |
| -------- | -------- | ------------------------------ |
| `TARGET` | Yes      | Substrate generator to resolve |

### Options

| Option                | Default                                            | Description                              |
| --------------------- | -------------------------------------------------- | ---------------------------------------- |
| `--config PATH`       | Required unless the target has an accepted default | Generation configuration                 |
| `--release INT`       | Config value (temporary fallback)                  | Publication release number               |
| `--set KEY=VALUE`     | None                                               | Typed configuration override; repeatable |
| `--output PATH`       | Configuration value                                | Override the artifact destination        |
| `--seed INT`          | Configuration value                                | Override the generation seed             |
| `--format text\|json` | `text`                                             | Terminal output format                   |

`--seed INT` overrides the configured substrate-generation seed and therefore participates in artifact content identity.
Supplying both `--seed` and a `--set` override for the same seed field is rejected as ambiguous.

`--release INT` is the invocation-layer publication coordinate — _where_ this concrete build is committed.
It is the highest authority for the intended coordinate and does not participate in scientific build-input identity.
A `release` value declared in the reusable config profile is accepted only as a temporary compatibility fallback (deprecated).
The release number must be a positive integer; `0`, a negative value, or a non-integer is rejected as invalid usage.

### Behavior

The command loads and validates configuration, resolves source dependencies and the destination, computes the artifact identity or fingerprint, checks for conflicts, and lists the stages that `build` would execute.
It does not create staging directories or output files.

### Inputs

- substrate definition selected by `TARGET`;
- generation configuration;
- referenced raw or external sources, when required.

### Outputs

- resolved configuration summary;
- input references and fingerprints;
- expected destination and file structure;
- conflict or reuse status;
- planned execution stages.

### Example

```console
ehp-sn data plan obsfield \
    --config config/data/obsfield/default.toml
```

The command prints the resolved ObsField variant, split sizes, destination, and whether an artifact with the same identity already exists.

### Errors

- Configuration cannot be loaded or is invalid.
- A source reference is malformed, unknown, or ambiguous.
- An override names an unknown field or has the wrong type.

A source whose identity resolves but whose payload is not currently available is reported as a warning.
`data build` performs the required availability check.

## `build TARGET`

Materialize one immutable substrate artifact.

```console
ehp-sn data build TARGET --config PATH [OPTIONS]
```

### Arguments

| Argument | Required | Description                    |
| -------- | -------- | ------------------------------ |
| `TARGET` | Yes      | Substrate generator to execute |

### Options

| Option                 | Default                                            | Description                                                       |
| ---------------------- | -------------------------------------------------- | ----------------------------------------------------------------- |
| `--config PATH`        | Required unless the target has an accepted default | Generation configuration                                          |
| `--release INT`        | Config value (temporary fallback)                  | Publication release number                                        |
| `--set KEY=VALUE`      | None                                               | Typed configuration override; repeatable                          |
| `--output PATH`        | Configuration value                                | Override the artifact destination                                 |
| `--seed INT`           | Configuration value                                | Override the generation seed                                      |
| `--replace-incomplete` | Disabled                                           | Remove an incomplete or uncommitted destination before rebuilding |
| `--format text\|json`  | `text`                                             | Terminal result format                                            |

`--release INT` is the invocation-layer publication coordinate and the highest authority for where the build is committed; it does not participate in scientific build-input identity and must be a positive integer (invalid values are a controlled usage error).
Building without a `--release` and without a fallback configured release is a controlled failure — the framework never auto-assigns a release number.

### Behavior

1. Loads and validates the effective configuration.
2. Resolves input sources and the destination.
3. Refuses an unsafe existing-output conflict.
4. Generates into a temporary staging directory.
5. Validates the staged artifact.
6. Writes the manifest, resolved configuration, provenance, and checksums.
7. Atomically publishes the completed artifact.
8. Prints the resulting artifact reference.

A failed build must not leave a destination that appears completed.
An identical existing artifact may be reused when its manifest and fingerprint match; a semantically different artifact requires a different identity or version.
`--replace-incomplete` applies only to failed staging state or an uncommitted invalid destination; it cannot replace a committed valid artifact.

### Reuse result

An equivalent verified artifact is a successful `action = "reused"`.
Existing content and provenance are not modified.
If the equivalent artifact exists elsewhere, the command returns its logical reference rather than copying it.
A different valid artifact at `--output` exits with code `8`.

### Inputs

- all inputs reported by `data plan`;
- generation code and its recorded version;
- effective configuration and seed.

### Outputs

```text
data/interim/<family>/<variant>/v<N>/
├── manifest.json
├── config.resolved.toml
├── provenance.json
└── splits/
```

The exact substrate payload is defined by the substrate specification.

### Example

```console
ehp-sn data build obsfield \
    --config config/data/obsfield/default.toml
```

On success, the command creates or reuses the configured ObsField artifact and prints the canonical logical reference and, where useful, its physical location.

### Errors

- Input source is missing or incompatible.
- Destination already contains a conflicting immutable artifact.
- Generation fails.
- Staged output fails validation.
- Atomic publication fails.

## `validate ARTIFACT`

Validate an existing substrate artifact without modifying it.

```console
ehp-sn data validate ARTIFACT [--level quick|full] [--format text|json]
```

### Arguments

| Argument   | Required | Description                         |
| ---------- | -------- | ----------------------------------- |
| `ARTIFACT` | Yes      | Path or accepted artifact reference |

### Options

| Option                | Default | Description            |
| --------------------- | ------- | ---------------------- |
| `--level quick\|full` | `full`  | Validation depth       |
| `--format text\|json` | `text`  | Terminal result format |

### Behavior

`quick` checks the manifest, required files, and top-level invariants.
`full` additionally checks checksums, shapes, value ranges, referential integrity, split declarations, and substrate-specific semantic invariants.
Validation is read-only.

### Outputs

A validation report containing pass/fail status, errors, warnings, and the artifact identity.
The command exits with code `5` when validation fails.

### Example

```console
ehp-sn data validate data/interim/obsfield/default/v1 --level full
```

The command reports whether the complete ObsField artifact satisfies its declared contract.

### Errors

- Artifact does not exist or cannot be read.
- Manifest is missing or unsupported.
- Files or semantic invariants do not match the manifest.

## `inspect ARTIFACT`

Display substrate metadata and the exact logical record selected by `--record` without modifying the artifact.

```console
ehp-sn data inspect ARTIFACT --record RECORD_ID [--format text|json]
```

`ARTIFACT` is either a physical path to a committed release directory (for example `data/interim/dagflow/single-terminal/v1`) or a canonical `artifact:<name>/v<N>` reference.

### Options

| Option                | Default | Description                             |
| --------------------- | ------- | --------------------------------------- |
| `--record RECORD_ID`  | —       | Exact logical record identifier to show |
| `--format text\|json` | `text`  | Terminal result format                  |

### Outputs

The command reports the committed artifact identity (`artifact:` reference), the exact `record_id`, the record's `schema_ref`, and the generic record content.
It is producer-neutral: it performs no producer-specific or contract-specific branch, and it never dumps the full dataset.

The record is selected by exactly one deterministic lookup of `--record` through the existing record-identity mechanism; no implicit ordering, RNG, or representative sampling is used.

### Figure rendering (`--figure`)

Figure rendering over a selected record (`data inspect ARTIFACT --record RECORD_ID --figure figure:<name>/v<N>`) is a later figure phase.
When it lands it must be **figure-owner agnostic**: resolve the requested figure through the normal figure catalogue and render it through the generic figure pipeline, with no substrate-family branch and no default figure inferred from registration order.

### Example

```console
ehp-sn data inspect data/interim/dagflow/single-terminal/v1 --record sha256:...
```

The result includes the committed artifact identity, the exact record
identifier, the schema reference, and the generic record content.

### Errors

- Artifact or manifest cannot be read (`unknown_artifact`, exit 4).
- Artifact reference is malformed (`unknown_artifact`, exit 4).
- `record_id` does not exist in the artifact (`record_not_found`, exit 4).
- `--samples` with a positive value (`operation_not_implemented`, exit 1).

## Related commands

- [`tasks`](tasks.md) — consumes interim substrates to create task corpora.

## See also

- [Configuration interface](../configuration/index.md)
- [Framework semantics](../../framework/index.md)
- [Architecture overview](../../architecture/index.md)
