# Logging Architecture

<!-- canonical_package: ehp_sn  authority: canonical  status: accepted -->

> `ehp_sn.logging` — operational event infrastructure. L0. No domain imports.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                                                            |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Logger acquisition (`get_logger`); configuration (`configure_logging`); context binding (`logging_context`, `bind_context`); rank filtering                                                                      |
| **Must not own**      | Domain results; ML artifacts; experiment tracking; metric infrastructure; tensor summarization                                                                                                                   |
| **Public API**        | `LogFormat`, `LogLevel`, `LoggingConfig`, `get_logger`, `configure_logging`, `logging_context`, `bind_context`, `clear_context`, `LoggingConfig` fields: `console_ranks`, `file_ranks` — per-sink rank filtering |
| **Allowed imports**   | stdlib, `structlog`                                                                                                                                                                                              |
| **Forbidden imports** | `torch`, `lightning`, `mlflow`, `zarr`, `matplotlib`, any `ehp_sn.*` domain package                                                                                                                              |
| **Layer**             | L0 — Foundation                                                                                                                                                                                                  |
| **Key invariant**     | Logging depends only on stdlib + structlog, never on any EHP domain package or torch; it records events without defining their meaning                                                                           |

---

## 1. Scope

Logging records **that** an event happened. The subsystem that understands the event owns its schema and semantics. Logging infrastructure is available to all runtime packages via `get_logger(__name__)`.

| Concern             | Owner                      |
| ------------------- | -------------------------- |
| Application logging | `ehp_sn.logging`           |
| Experiment tracking | MLflow / Lightning loggers |
| Domain traces       | `ehp_sn.traces`            |
| Evaluation results  | `ehp_sn.evaluation`        |
| Diagnostics         | `ehp_sn.diagnostics`       |

### What logging is NOT responsible for

| Concern                        | Owner                 |
| ------------------------------ | --------------------- |
| TensorBoard metric logging     | `lightning.loggers`   |
| MLflow run lifecycle           | `evaluation.tracking` |
| Domain traces and replay data  | `traces`              |
| Diagnostic probes and findings | `diagnostics`         |
| Evaluation metrics and results | `evaluation`          |
| Report composition             | `reporting`           |
| Lightning callbacks            | `lightning.callbacks` |

### Tensor-aware serialization

Logging normalises only standard Python values: `Path`, `Enum`, dataclasses as dictionaries, bounded strings, scalars, and scalar mappings. It does **not** understand Torch types. Tensor summarisation belongs in `diagnostics`. The logging package must **never** call `.item()`, `.detach()`, or `torch.isfinite()` — those require the Torch dependency that logging must not have.

## 2. Public API (8 exports)

- `get_logger(name) → structlog.stdlib.BoundLogger` — per-module logger acquisition. No global singleton.
- `configure_logging(config, *, force=False)` — called by entry points only, never by imported modules.
- `logging_context(**fields)` — temporary context binding (context manager).
- `bind_context(**fields)` / `clear_context()` — lifecycle-long binding; clear at execution boundaries.

## 3. Configuration

`LoggingConfig(console_format, file_format, log_level, log_file, level_overrides, include_timestamp, include_source, console_ranks, file_ranks)`. Console to stderr. Independent console/file formatters. `level_overrides` applies to both first-party and third-party loggers. `console_ranks` and `file_ranks` control rank-based sink eligibility.

## 4. Context field taxonomy

**Stable** (for `bind_context`): `command`, `run_id`, `experiment`, `phase`, `task`, `dataset`, `model_family`, `checkpoint_id`, `rank`, `world_size`.

**Event-local** (per-event kwargs): `epoch`, `global_step`, `worker_id`, `example_count`, `duration_seconds`.

## 5. Design contract

> Logging is pure infrastructure. It depends only on stdlib + structlog, never on any EHP domain package. It records events without defining their meaning. Entry points configure it; modules acquire loggers; context enriches records.

## 6. Rank filtering

### 6.1 Separation of identity and policy

Distributed rank identity SHALL be represented by the stable context fields `rank` and `world_size` and established through `bind_context`. Rank-based emission SHALL be configured per logging sink through `configure_logging`. Rank filtering implementations are internal and SHALL NOT introduce public `set_rank()` or `clear_rank()` functions.

| Responsibility                                    | Owner                              |
| ------------------------------------------------- | ---------------------------------- |
| Discover the current distributed rank             | Training / runtime integration     |
| Bind `rank` and `world_size` into logging context | `ehp_sn.logging.bind_context`      |
| Decide which ranks a handler emits                | `ehp_sn.logging.configure_logging` |
| Implement the actual predicate / filter           | Internal logging implementation    |
| Change rank dynamically                           | Not part of the normal public API  |

### 6.2 Configuration

```python
configure_logging(
    ...,
    console_ranks={0},    # only rank 0 emits to console
    file_ranks=None,       # all ranks emit to file (per-rank suffix)
)
```

- `console_ranks=None`: all ranks emit to console.
- `console_ranks={0}`: only rank 0 emits to console.
- `file_ranks=None`: all ranks emit to configured file sinks.
- Filtering is evaluated from the bound `rank` field on each record.
- In a non-distributed process where `rank` is absent from the bound context, the effective rank is treated as 0.

### 6.3 File output policy

When file logging is enabled and multiple ranks are eligible, a per-rank suffix is appended to the filename (e.g. `train.rank-000.log`, `train.rank-001.log`). This avoids the data-races and interleaving issues inherent in multi-process writes to a single ordinary file.

### 6.4 Typical integration

```python
configure_logging(
    console_ranks={0},
    file_ranks=None,
)

bind_context(
    rank=distributed_rank,
    world_size=distributed_world_size,
)
```

Ranks are discovered by the training/runtime integration (e.g. from `torch.distributed.get_rank()`) and bound into logging context as opaque metadata. The logging layer applies sink policy independently.

## 7. Package structure

```
ehp_sn/logging/
├── __init__.py          # get_logger, configure_logging, logging_context, bind_context, clear_context
├── _config.py           # LoggingConfig, LogFormat, LogLevel
├── _context.py          # ContextVar management for bind_context / clear_context
├── _logger.py           # structlog configuration, processor chain
├── config.py            # Public configuration types
└── core.py              # Internal implementation
```
