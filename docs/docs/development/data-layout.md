---
authority: descriptive
status: specified
api_stability: not-applicable
---

# Data layout

The repository `data/` directory stores local source data, committed substrate artifacts, and committed task corpora.

This document describes the physical monorepo convention and developer workflow. It does not define artifact identity, manifest schemas, digest algorithms, or scientific channel semantics.

Normative contracts are defined in [Data artifacts](../framework/data-artifacts.md) and [Corpora](../framework/corpora.md).

## Directory structure

```text
data/
├── external/
├── raw/
├── interim/
└── processed/
```

## `external/`

`data/external/` contains data obtained from external projects or providers.

Examples include:

- downloaded benchmark datasets;
- third-party augmented datasets;
- externally maintained archives.

External data should remain as close as practical to the provider representation. Acquisition instructions, licensing constraints, and expected source fingerprints should be documented where applicable.

External data is not automatically an EHP-SN artifact.

## `raw/`

`data/raw/` contains local source material before publication as an EHP-SN artifact.

Examples include:

- procedural-generator output;
- extracted external records;
- source-preserving conversions;
- imported source files.

Raw data may be mutable or incomplete during development. Training and evaluation must not consume it unless another public contract explicitly permits that use.

## `interim/`

`data/interim/` contains committed substrate artifacts produced by `ehp-sn data`.

The conventional local layout is:

```text
data/interim/<family>/<variant>/v<N>/
```

Examples:

```text
data/interim/openfield/default/v1/
data/interim/dagflow/default/v1/
data/interim/dungeongen/default/v1/
data/interim/maze-nd/default/v1/
```

Despite the directory name, a committed release is complete, immutable, validated, and reusable.

Temporary staging directories are implementation details and must not occupy a path that appears to be a committed release.

## `processed/`

`data/processed/` contains committed task corpora produced by `ehp-sn tasks`.

The conventional local layout is:

```text
data/processed/<task>/<corpus>/v<N>/
```

Examples:

```text
data/processed/arena/default/v1/
data/processed/goaltrace/default/v1/
data/processed/mazehard/default/v1/
data/processed/routebind/default/v1/
data/processed/seqmaze/default/v1/
```

A processed corpus is self-contained and transportable. Normal consumers do not require the parent substrate artifact.

The corpus manifest and index still record exact parent identities for provenance and split validation.

## Typical artifact resources

A local release commonly contains files such as:

```text
manifest.json
config.resolved.toml
provenance.json
index.jsonl
```

Payloads may be organized under `splits/`, `shards/`, or another manifest-declared layout.

The manifest and index determine resource roles and split membership. Directory names alone are not authoritative.

## Build flow

The intended workflow is:

```text
external or raw source
        ↓
ehp-sn data plan/build
        ↓
data/interim/<family>/<variant>/v<N>/
        ↓
ehp-sn tasks plan/build
        ↓
data/processed/<task>/<corpus>/v<N>/
        ↓
ehp-sn train / ehp-sn evaluate
```

Example:

```console
ehp-sn data plan openfield \
    --config config/data/openfield/default.toml

ehp-sn data build openfield \
    --config config/data/openfield/default.toml

ehp-sn tasks plan arena \
    --config config/tasks/arena/default.toml

ehp-sn tasks build arena \
    --config config/tasks/arena/default.toml
```

The actual package-relative location from which `ehp_research` exposes these configuration assets must be documented by the package configuration convention. The paths above describe their logical monorepo-facing use.

## Release numbering

Each `(family, variant)` or `(task, corpus)` pair has an independent release sequence.

Examples:

```text
openfield/default/v1
openfield/default/v2

arena/default/v1
arena/default/v2
```

Any intentional change that produces different data requires a new release number, including a seed-only change.

The version is declared in configuration. The framework does not auto-assign the next release.

A committed coordinate must never be overwritten with different content.

Accidental corruption invalidates the existing release; it does not legitimize modifying the release in place.

## Planning outcomes

`plan` resolves the effective configuration and build-input identity, then reports one of these outcomes:

- `available`: no committed artifact occupies the coordinate;
- `reusable`: a committed valid artifact records the same build-input identity and passes required integrity checks;
- `conflict`: a committed artifact occupies the coordinate with incompatible build inputs;
- `invalid existing state`: incomplete or invalid content exists at the destination.

The final content fingerprint is created after payload generation. Planning does not predict unknown output resource digests.

## Git policy

Large generated payloads should normally be excluded from Git.

The repository may version small resources when required, such as:

- manifests used by tests;
- bounded fixtures;
- schema examples;
- reference metadata;
- tiny deterministic sample artifacts.

Generated release directories must not be partially committed in a way that makes them appear complete.

The exact `.gitignore` policy belongs to repository development configuration.

## Portability

A committed processed corpus should remain usable when copied to another machine or artifact store.

Consumers should rely on:

- manifest-declared relative resources;
- the corpus index;
- resource digests;
- logical artifact references;
- configured persistence bindings.

Absolute local paths must not participate in artifact identity.

## Cleanup

Developers may remove:

- raw inputs that can be reacquired;
- incomplete staging state;
- unneeded local copies of committed artifacts;
- non-authoritative caches.

Developers must not modify a committed artifact in place.

To change generated data, update the configuration and publish a new release.

## Ownership boundaries

`ehp_sn` owns:

- artifact and corpus contracts;
- planning, validation, and publication semantics;
- release identity application;
- CLI execution services.

`ehp_research` owns:

- concrete substrate and task definitions;
- builders;
- scientific schemas;
- package-owned default configurations.

The monorepo owns:

- local `data/` placement;
- repository-facing configuration bindings;
- cleanup and Git policy;
- reproduction assets under `experiments/`.

## Related documents

- [Data artifacts](../framework/data-artifacts.md)
- [Corpora](../framework/corpora.md)
- [OpenField v1](../research/substrates/openfield-v1.md)
- [Arena v1](../research/tasks/arena-v1.md)
- [`ehp-sn data`](../interfaces/cli/data.md)
- [`ehp-sn tasks`](../interfaces/cli/tasks.md)
