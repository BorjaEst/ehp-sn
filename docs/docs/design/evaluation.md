# Evaluation Design

<!-- canonical_package: ehp_sn  authority: canonical  status: draft -->

> `ehp_sn.evaluation` — owns the **meaning and orchestration** of evaluation.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                                                   |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Evaluation specifications, protocols, suites; execution orchestration; metric selection/coordination; criteria; `EvaluationResult`; provenance                                                          |
| **Must not own**      | Metric formulas; trace capture; scientific analysis; figure rendering; report composition                                                                                                               |
| **Public API**        | `EvaluationRequest`, `EvaluationResult`, `EvaluationProtocol`, `EvaluationSuite`, `Criterion`, `evaluate`, `validate`                                                                                   |
| **Allowed imports**   | `rollouts` (R: contracts), `metrics` (R), `traces` (R: `TraceSink`; P: `TraceStoreReader`), `contracts` (R); **P:** `data`, `tasks`, `models` (resolution-time, isolated in `evaluation/resolution.py`) |
| **Forbidden imports** | `analysis`, `figures`, `lightning`, `training` (execution internals), `objectives`, `controllers`                                                                                                       |
| **Layer**             | L5 — Observability & Evaluation                                                                                                                                                                         |
| **Key invariant**     | Evaluation owns specification, orchestration, and metric coordination; metrics owns formulas; every boundary has a named contract                                                                       |

---

## 1. Core lifecycle

```
EvaluationRequest → EvaluationPlan → resolve + validate → ResolvedEvaluationPlan → execute → EvaluationResult → persist
```

Internal phases of `evaluate(request)`:

```
1. Resolve
   ├── model reference → concrete checkpoint + model factory
   ├── dataset reference → versioned split
   ├── suite alias → immutable EvaluationSuite
   ├── protocol defaults + overrides
2. Validate (before inference)
   ├── model capabilities satisfy suite requirements
   ├── dataset provides required channels
   ├── suite metrics have available inputs
   ├── checkpoint is compatible
   ├── protocol is internally consistent
3. Execute
   ├── open resources
   ├── torch.inference_mode()
   ├── delegate recurrent stepping to rollouts
   ├── update metrics per step
4. Aggregate
   ├── merge metric state across batches/episodes
   ├── finalize sufficient statistics
5. Validate results → criteria check
6. Persist → artifacts, MLflow
```

### Ownership boundary

| Does not own                             | Owner         |
| ---------------------------------------- | ------------- |
| Metric formulas, accumulation algorithms | `metrics`     |
| Denominator and masking semantics        | `metrics`     |
| Distributed reduction                    | `metrics`     |
| Dataset construction, splits, batching   | `data`        |
| Task semantics, targets                  | `tasks`       |
| Model construction, inference contracts  | `models`      |
| Recurrent execution, carry, stepping     | `rollouts`    |
| Trace collection (observers, sinks)      | `traces`      |
| Post-hoc scientific computation          | `analysis`    |
| Visual rendering                         | `figures`     |
| Report composition                       | `reporting`   |
| Model-health diagnostics                 | `diagnostics` |

## 2. Domain model

- **`ModelReference`**: `CheckpointReference(path, digest) | MLflowModelReference(run_id, artifact_path) | RegisteredModelReference(name, version)`. Serialisable, reproducible. In-memory `nn.Module` uses separate `evaluate_model()` entry point with a `LoadedModel` reference.
- **`EvaluationPlan`**: Unresolved plan stage between `EvaluationRequest` and `ResolvedEvaluationPlan`. Contains identifiers and references, not yet resolved to concrete objects.
- **`EvaluationProtocol`**: `seed`, `RolloutProtocol` (max_steps, action mode, memory policy), `AggregationProtocol` (unit: step|episode|environment, CI method), `StateResetProtocol` (between_cases, between_chunks).
- **`EvaluationSuite`**: name, task family, model families, metrics (`MetricSelection` from task scoring catalog), criteria.
- **`Criterion`**: `metric_name`, `operator` (>=, <=, >, <, ==), `threshold`.
- **`EvaluationResult`**: `evaluation_id`, `model`, `dataset`, `protocol`, `suite`, `summary` (metric→value), `decision` (PASSED|FAILED|NOT_EVALUATED), `provenance`, `issues`. Execution status and benchmark decision are separate.

## 3. Metric data API

Metrics declare `MetricRequirements(predictions, targets, masks, metadata)` in `metrics/contracts.py`. They consume `EvaluationObservation` — a frozen typed dataclass constructed by a task-owned typed adapter, validated by `EvaluationFieldSpec` schemas. Raw metric values use `ScalarMetricResult` in `metrics`; evaluation wraps them in `EvaluatedMetricResult` for result assembly.

## 4. Package structure

```
ehp_sn/evaluation/
├── contracts.py       # EvaluationResult, EvaluationPlan, EvaluationSuite, Criterion
├── definitions.py     # Suite registry, protocol defaults
├── resolution.py      # ModelReference resolution, dataset resolution (imports data, tasks, models)
├── execution.py       # evaluate(), EvaluationRunner
├── models.py          # ModelReference, CheckpointReference, MLflowModelReference
├── payload.py         # EvaluationPayload, MetricCollection
└── cli.py             # evaluate command
```

## 5. Design contract

> Evaluation owns specification, orchestration, metric coordination, criteria, and result persistence. Metrics owns formulas. Traces owns capture. Analysis owns post-hoc computation. Figures owns visualization. Reporting owns composition. Every boundary has a named contract.
