# Trace Architecture

<!-- canonical_package: ehp_sn  authority: canonical  status: draft -->

> `ehp_sn.traces` — turning runtime model state into stable, versioned, queryable scientific trace artifacts.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Owns**              | Trace vocabulary (`TraceKey`, `TraceFieldSpec`); capture profiles; extraction; collection lifecycle; dense/sparse storage; artifact manifests; reader API                                                                      |
| **Must not own**      | Metric computation; diagnostic interpretation; figure construction; report generation; model architecture; rollout execution                                                                                                   |
| **Public API**        | `TraceObserver`, `TraceSpec`, `TraceField`, `TraceValue`, `TraceSink`, `ZarrTraceSink`, `TraceStoreReader`, `open_trace`                                                                                                       |
| **Allowed imports**   | `contracts`, `rollouts` (`StepRecord`, `RolloutResult`, `StepBoundary`, `SourceContext` only — never runner implementations)                                                                                                   |
| **Forbidden imports** | `evaluation`, `diagnostics`, `figures`, `reporting`, `lightning`, `training`. Traces never imports evaluation. Evaluation imports traces for `TraceSink` (write path, R) and optionally for `TraceStoreReader` (read path, P). |
| **Layer**             | L5 — Observability & Evaluation                                                                                                                                                                                                |
| **Key invariant**     | Producers expose, specifications select, observers extract, collectors coordinate, sinks persist, readers retrieve, consumers interpret — a change to what is stored must not force changes in how it is interpreted           |

---

## 1. Pipeline

```
Producers (model/controller/task) → TraceSpec → TraceObserver → TraceCollector → TraceSink → TraceArtifact → TraceStoreReader / TraceArtifactReader → consumers
```

**Rule:** Producers expose. Specifications select. Observers extract. Collectors coordinate. Sinks persist. Readers retrieve. Consumers interpret.

## 2. Separation of concerns

> **Producers expose. Specifications select. Observers extract. Collectors coordinate. Sinks persist. Readers retrieve. Consumers interpret.**

| Concern             | Owner                      | Purpose                                         |
| ------------------- | -------------------------- | ----------------------------------------------- |
| Scientific traces   | `traces`                   | Persist model states, activations, trajectories |
| Metrics             | `metrics`                  | Numerical reduction of what happened            |
| Diagnostics         | `diagnostics`              | Interpretation of whether behaviour is healthy  |
| Figures             | `figures`                  | Visual representation of traces and metrics     |
| Reports             | `reporting`                | Assembled scientific communication              |
| Application logging | `logging`                  | Operational events while the program executes   |
| Execution profiling | PyTorch Profiler           | CPU/CUDA timing, operator shapes, memory        |
| Distributed tracing | OpenTelemetry (optional)   | Span trees, latency, service boundaries         |
| Experiment tracking | MLflow / Lightning loggers | Parameters, metrics, checkpoints, artifact URIs |

A change to _what is stored_ should not force changes in _how it is interpreted_. A new figure should not need to know whether data came from an in-memory tree or a Zarr directory.

## 3. Core domain types

- **`TraceKey`**: validated string identifier (not enum — field space grows).
- **`TraceAxis`**: `EPISODE | DELIBERATION | ENVIRONMENT | BATCH | FEATURE | LAYER | HEAD`.
- **`TraceFieldSpec`**: pure semantic schema (key, dtype, axes, storage kind, value range).
- **`TraceField`**: runtime binding — spec + extraction getter.
- **`TraceRequest`**: lightweight membership API for conditional computation (`trace.requires(key)`). Singleton `NO_TRACE` for disabled path.
- **`TraceCoordinates`**: runner-owned `environment_step` + controller-owned `deliberation_step`.
- **`TraceContribution`**: explicit producer output — wins over getter extraction.
- **`TraceEvent`**: sparse occurrences (episode boundaries, halts, anomalies).

## 4. TraceProfile vs TraceSpec

`TraceProfile` = declarative user-facing selection. `TraceSpec` = validated executable plan (resolved against producer capabilities).

## 5. Storage

| Backend             | Use                             |
| ------------------- | ------------------------------- |
| `ZarrTraceSink`     | Chunked compressed dense arrays |
| `ParquetEventSink`  | Columnar sparse events          |
| `InMemoryTraceSink` | Bounded RAM-backed tree         |

## 6. Reader API

Two reader protocols operate at different abstraction levels:

| Protocol              | Owner                       | Identity      | Methods                                                 |
| --------------------- | --------------------------- | ------------- | ------------------------------------------------------- |
| `TraceStoreReader`    | `traces`                    | `TraceKey`    | `read(key)`, `read_step(key, step)`, `list_available()` |
| `TraceArtifactReader` | `analysis` (consumer-owned) | `ArtifactRef` | `read(ref)`, `list_available()`                         |

`TraceStoreReader` is the low-level persisted-trace interface owned by
`traces`. It supports keyed field access and random step access — used
by diagnostics, trace tooling, and integrity checks.

`TraceArtifactReader` is the artifact-level consumer-owned protocol
defined in `analysis/contracts.py` (see `contracts.md` §4.3).
Analysis never imports traces; an integration adapter at the composition
boundary resolves `ArtifactRef` → `TraceStoreReader`.

`TraceTree` is an internal implementation. No consumer imports it
directly. `open_trace(uri)` returns a `TraceStoreReader`.

## 7. Integration

| Upstream/downstream package | Contract types                                                 | Direction       | Purpose                            | Status |
| --------------------------- | -------------------------------------------------------------- | --------------- | ---------------------------------- | ------ |
| `contracts`                 | `ArtifactKey`, `ArtifactRef`, `Provenance`                     | ← (imports)     | Artifact identity and metadata     | R      |
| `rollouts`                  | `StepRecord`, `RolloutResult`, `StepBoundary`, `SourceContext` | ← (imports)     | Runtime data to capture            | R      |
| `evaluation`                | (imports `TraceSink` from traces)                              | → (consumed by) | Trace collection during evaluation | R      |
| `diagnostics`               | (imports `TraceStoreReader`)                                   | → (consumed by) | Offline probe trace access         | P      |
| `analysis`                  | (defines `TraceArtifactReader`; adapter resolves)              | → (consumed by) | Artifact-level trace reading       | P      |
| `training`                  | (forbidden)                                                    | —               | —                                  | F      |
| `lightning`                 | (forbidden)                                                    | —               | —                                  | F      |
| `figures`                   | (forbidden)                                                    | —               | —                                  | F      |
| `reporting`                 | (forbidden)                                                    | —               | —                                  | F      |

See also: [contracts.md §4.1](contracts.md) for foundation artifact types; [rollouts.md §5](rollouts.md) for `StepRecord` and `RolloutResult`; [evaluation.md](evaluation.md) for `TraceSink` usage; [diagnostics.md](diagnostics.md) for `TraceStoreReader` usage; [analysis.md](analysis.md) for `TraceArtifactReader` definition; [contracts.md §4.3](contracts.md) for consumer-owned protocol rules.

## 8. Package structure

```
ehp_sn/traces/
├── definitions.py, vocabulary.py, profiles.py, capabilities.py
├── observer.py, collector.py, tree.py, events.py
├── sinks.py, artifacts.py, manifests.py, readers.py
├── validation.py, rollout.py
```

## 9. Design contract

> Traces owns the vocabulary, capture, persistence, and reading of scientific temporal data. Consumers read through `TraceStoreReader` (storage-level) or `TraceArtifactReader` (artifact-level, consumer-owned by analysis). Producers expose conditionally via `TraceRequest`. Storage backends are hidden behind `TraceSink`/`TraceStoreReader` protocols.
