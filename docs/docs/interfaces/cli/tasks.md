---
authority: normative
status: specified
api_stability: provisional
---

# `ehp-sn tasks`

Build, validate, and inspect immutable processed task corpora.
See the [CLI overview](_index.md) for shared help, configuration, output, and error conventions.

## Overview

Use `ehp-sn tasks` after the required interim substrates exist and before training or evaluation. The command consumes a task definition, task-generation configuration, and one or more substrate artifacts. It produces a versioned corpus containing task inputs, targets, splits, and provenance.

```text
data/interim/<substrate>/...
        ↓
ehp-sn tasks
        ↓
data/processed/<task>/<corpus>/v<N>/
        ↓
ehp-sn train / ehp-sn evaluate
```

`tasks` owns episode or case generation, task inputs and targets, task-specific sequences, corpus manifests, split materialization, and corpus validation. It does not own substrate generation, model architecture, model tokenization, training batches, or evaluation execution.

## Usage

```console
ehp-sn tasks COMMAND [OPTIONS]
```

| Command           | Purpose                                    |
| ----------------- | ------------------------------------------ |
| `list`            | List available task families               |
| `show TASK`       | Describe one task-generation contract      |
| `plan TASK`       | Resolve corpus generation without writing  |
| `build TASK`      | Build one immutable task corpus            |
| `validate CORPUS` | Validate an existing corpus                |
| `inspect CORPUS`  | Inspect corpus metadata or bounded samples |

## `list`

List task families available to the current installation.

```console
ehp-sn tasks list [--format text|json]
```

### Outputs

The command reports each task name, protocol version, maturity, required substrate kinds, and a short description.

### Example

```console
ehp-sn tasks list
```

The result includes task families such as `arena` and `goaltrace` when their definitions are installed.

### Errors

- Task catalogue cannot be loaded.
- A task definition is registered but unavailable.

## `show TASK`

Describe one task-generation contract without creating a corpus.

```console
ehp-sn tasks show TASK [--format text|json]
```

### Arguments

| Argument | Required | Description                       |
| -------- | -------- | --------------------------------- |
| `TASK`   | Yes      | Task family name, such as `arena` |

### Outputs

The command reports:

- canonical task reference and protocol version;
- scientific purpose and maturity;
- required substrate kinds;
- public input and target channels;
- generated corpus kind;
- supported configuration fields;
- relevant task specification.

It summarizes schemas but does not reproduce complete task or corpus specifications.

### Example

```console
ehp-sn tasks show arena
```

The result explains which substrate Arena requires and which episode channels its corpus contains.

### Errors

- Unknown task — run `ehp-sn tasks list`.
- Task definition cannot be loaded.

## `plan TASK`

Resolve one task-corpus build without writing files.

```console
ehp-sn tasks plan TASK --config PATH [OPTIONS]
```

### Arguments

| Argument | Required | Description            |
| -------- | -------- | ---------------------- |
| `TASK`   | Yes      | Task family to resolve |

### Options

| Option                | Default                                    | Description                              |
| --------------------- | ------------------------------------------ | ---------------------------------------- |
| `--config PATH`       | Required unless an accepted default exists | Corpus-generation configuration          |
| `--set KEY=VALUE`     | None                                       | Typed configuration override; repeatable |
| `--output PATH`       | Configuration value                        | Override the corpus destination          |
| `--format text\|json` | `text`                                     | Terminal output format                   |

### Behavior

The command validates the task-generation configuration, resolves parent substrate references and fingerprints, determines splits and expected sample counts, computes the corpus identity, checks for an existing output, and reports the stages that `build` would execute. It does not create staging directories or samples.

### Inputs

- task definition selected by `TASK`;
- task-generation configuration;
- parent substrate references declared by the configuration.

### Outputs

- resolved task and configuration;
- parent artifact references and fingerprints;
- destination and conflict status;
- split and sample counts;
- corpus fingerprint;
- planned generation stages.

### Example

```console
ehp-sn tasks plan arena \
    --config config/tasks/arena/default.toml
```

The command reports the resolved OpenField input, Arena split sizes, expected episode counts, and target corpus path.

### Errors

- Task configuration is invalid.
- A parent-substrate reference is malformed, unknown, or ambiguous.
- The resolved substrate identity is incompatible with the task definition.
- An override is unknown or type-invalid.

A substrate whose identity resolves but whose payload is unavailable is reported as a warning. `tasks build` performs the required availability and artifact-kind checks.

## `build TASK`

Generate and atomically publish one immutable task corpus.

```console
ehp-sn tasks build TASK --config PATH [OPTIONS]
```

### Arguments

| Argument | Required | Description             |
| -------- | -------- | ----------------------- |
| `TASK`   | Yes      | Task family to generate |

### Options

| Option                 | Default                                    | Description                                                       |
| ---------------------- | ------------------------------------------ | ----------------------------------------------------------------- |
| `--config PATH`        | Required unless an accepted default exists | Corpus-generation configuration                                   |
| `--set KEY=VALUE`      | None                                       | Typed configuration override; repeatable                          |
| `--output PATH`        | Configuration value                        | Override the corpus destination                                   |
| `--replace-incomplete` | Disabled                                   | Remove an incomplete or uncommitted destination before rebuilding |
| `--format text\|json`  | `text`                                     | Terminal result format                                            |

### Behavior

1. Resolves the task definition and effective configuration.
2. Loads and validates parent substrate artifacts.
3. Refuses unsafe existing-output conflicts.
4. Generates the corpus in a staging directory.
5. Validates structural and task-specific invariants.
6. Writes the manifest, resolved configuration, provenance, and parent fingerprints.
7. Atomically publishes the corpus.
8. Prints the corpus artifact reference.

A different corpus identity or semantic configuration requires a different version. `--replace-incomplete` never removes or mutates a committed valid corpus.

### Reuse result

An equivalent verified corpus is a successful `action = "reused"`. Existing content and provenance are not modified. If the equivalent corpus exists elsewhere, the command returns its logical reference rather than copying it. A different valid corpus at `--output` exits with code `8`.

### Inputs

- all parent substrates reported by `tasks plan`;
- task-generation configuration and seed policy;
- task definition and builder version.

### Outputs

```text
data/processed/<task>/<corpus>/v<N>/
├── manifest.json
├── config.resolved.toml
├── provenance.json
└── splits/
```

The payload contains task-specific cases or episodes and their declared input and target channels.

### Example

```console
ehp-sn tasks build arena \
    --config config/tasks/arena/default.toml
```

On success, the command creates or reuses the configured Arena corpus and prints its artifact reference.

### Errors

- Parent substrate is missing or invalid.
- Task and substrate are incompatible.
- Destination contains a conflicting immutable corpus.
- Corpus generation fails.
- Generated samples fail validation.
- Artifact publication fails.

## `validate CORPUS`

Validate a processed task corpus without modifying it.

```console
ehp-sn tasks validate CORPUS [--level manifest|sample|full] [OPTIONS]
```

### Arguments

| Argument | Required | Description                                |
| -------- | -------- | ------------------------------------------ |
| `CORPUS` | Yes      | Corpus path or accepted artifact reference |

### Options

| Option                           | Default    | Description                      |
| -------------------------------- | ---------- | -------------------------------- |
| `--level manifest\|sample\|full` | `full`     | Validation depth                 |
| `--split NAME`                   | All splits | Restrict validation to one split |
| `--format text\|json`            | `text`     | Terminal result format           |

### Behavior

The task family and schema version are read from the corpus manifest; users do not repeat the task name. `manifest` validates descriptors and files, `sample` validates representative structural invariants, and `full` validates all samples and task-specific semantic invariants.

### Outputs

A report containing the corpus identity, validation level, errors, warnings, and pass/fail status. Validation failure exits with code `5`.

### Example

```console
ehp-sn tasks validate data/processed/arena/default/v1 --level full
```

The command checks all Arena splits and reports any invalid episode with a bounded, actionable diagnostic.

### Errors

- Corpus does not exist or cannot be read.
- Manifest does not identify a supported task corpus.
- Declared channels, shapes, or values are invalid.
- Task-specific semantic invariants fail.

## `inspect CORPUS`

Inspect corpus metadata, aggregate statistics, or one bounded sample.

```console
ehp-sn tasks inspect CORPUS [OPTIONS]
```

### Options

| Option                | Default    | Description                |
| --------------------- | ---------- | -------------------------- |
| `--split NAME`        | All splits | Select a split             |
| `--index INDEX`       | None       | Display one decoded sample |
| `--format text\|json` | `text`     | Terminal result format     |

### Outputs

Without `--index`, the command reports corpus identity, parent artifacts, split counts, channel summaries, and bounded aggregate statistics. With `--index`, it prints a decoded task-specific view of that sample. It does not dump the full corpus.

### Example

```console
ehp-sn tasks inspect data/processed/arena/default/v1 \
    --split validation \
    --index 12
```

The result displays the selected Arena episode and its declared inputs and targets.

### Errors

- Corpus or manifest cannot be read.
- Requested split or case index does not exist.
- Artifact kind is not a processed task corpus.

## Related commands

- [`data`](data.md) — produces the parent substrates.
- [`train`](train.md) — consumes task corpora for training.
- [`evaluate`](evaluate.md) — consumes declared evaluation data or corpora.

## See also

- [Configuration interface](../configuration/_index.md)
- [Framework semantics](../../framework/_index.md)
- [Architecture overview](../../architecture/_index.md)
