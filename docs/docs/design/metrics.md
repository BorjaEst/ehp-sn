# Metrics Design

<!-- canonical_package: ehp_sn  authority: canonical  status: accepted -->

> `ehp_sn.metrics` owns the **mathematical definition and accumulation semantics** of every measurement.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                                        |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Metric formulas; sufficient statistics (`update`/`compute`/`reset`); denominator and masking semantics; distributed reduction                                                                |
| **Must not own**      | Metric selection for evaluations; recipe orchestration; observation feeding; result assembly; training loops                                                                                 |
| **Public API**        | `Metric` subclasses (`ExactSequenceMatch`, `MaskedCategoricalAccuracy`, `HaltRate`, …); `functional/` variants                                                                               |
| **Allowed imports**   | `contracts`, `torch`                                                                                                                                                                         |
| **Forbidden imports** | `evaluation`, `training`, `lightning`, `objectives`, `models`, `tasks`                                                                                                                       |
| **Layer**             | L1 — Domain Primitives                                                                                                                                                                       |
| **Key invariant**     | Every metric formula has one authoritative implementation shared by functional and stateful APIs; sufficient statistics produce correct results under uneven batches, DDP, and dynamic masks |

---

## 1. Metrics vs evaluation: who aggregates what

| Concern                                                              | Owner        |
| -------------------------------------------------------------------- | ------------ |
| Metric formulas, sufficient statistics, `update`/`compute`/`reset`   | `metrics`    |
| Denominator and masking semantics                                    | `metrics`    |
| Distributed sufficient-statistic reduction                           | `metrics`    |
| Choosing which metrics, feeding observations, coordinating execution | `evaluation` |
| Placing computed values into `EvaluationResult`                      | `evaluation` |

## 2. Two metric APIs

**Functional** (stateless): `exact_sequence_match(predictions, targets, *, mask) → Tensor`. For tests, notebooks, offline datasets.

**Stateful** (`torchmetrics.Metric`): `ExactSequenceMatch().update(...).compute()`. For training loops, distributed evaluation, Lightning integration.

Both share a single private sufficient-statistics helper — one formula, one test suite.

## 3. Metric catalogue

| Family             | Metric                     | Kind      | Description                                  |
| ------------------ | -------------------------- | --------- | -------------------------------------------- |
| Arena              | `path_efficiency`          | RatioStat | Ratio of shortest path to actual path length |
| Arena              | `goal_reached_rate`        | RatioStat | Fraction of episodes reaching goal           |
| Arena              | `mean_trajectory_length`   | Scalar    | Mean steps per episode                       |
| MazeHard           | `exact_sequence_match`     | Accuracy  | Full output sequence equals target           |
| MazeHard           | `token_accuracy`           | Accuracy  | Per-position token match rate                |
| MazeHard           | `mean_deliberation_steps`  | Scalar    | Mean ACT steps per maze                      |
| MazeHard           | `halt_rate`                | RatioStat | Fraction of steps where halt was chosen      |
| Goaltrace          | `field_mae`                | Scalar    | Mean absolute error in predicted field       |
| Goaltrace          | `goal_proximity_rank`      | Scalar    | Rank of goal location in predicted field     |
| Routebind          | `field_mae`                | Scalar    | Mean absolute error in predicted field       |
| Routebind          | `route_direction_accuracy` | Accuracy  | Correct route-choice direction               |
| SeqMaze            | `edge_prediction_accuracy` | Accuracy  | Correctly predicted transition edges         |
| SeqMaze            | `path_completion_rate`     | RatioStat | Fraction of correctly completed paths        |
| TEM (cross-family) | `reconstruction_error`     | Scalar    | Sensory reconstruction MSE                   |
| TEM (cross-family) | `latent_consistency`       | Scalar    | Consistency of latent codes across views     |

Every metric name maps to one authoritative implementation shared by functional and stateful APIs.

## 4. Sufficient statistics — never batch averages

Correct: `self.correct += number_correct; self.total += number_valid`
Wrong: `self.batch_accuracies.append(batch_accuracy)`

| Metric                  | Accumulated state                  |
| ----------------------- | ---------------------------------- |
| Accuracy                | `correct` count, `valid` count     |
| MSE                     | `squared_error_sum`, `valid` count |
| Exact sequence accuracy | `exact` count, `total` sequences   |
| Mean ACT steps          | `step_sum`, `valid_slot_count`     |
| Halt rate               | `halted_count`, `eligible_count`   |

## 5. Mergeability and masks

Every custom metric must be reducible through associative sufficient statistics (required for DDP). Document: what state, how reduced, bounded memory, exact mergeability, distributed equivalence.

**Empty-support policy:** project-wide default is **NaN** via `_safe_ratio()`. Override to 0.0 only when semantics define zero as correct empty value.

## 6. Semantic inputs — not evaluator-specific

Metric `update()` accepts explicit semantic tensors (`predictions`, `targets`, `mask`), never evaluator context objects. Related families may use typed input objects (`PathwayInput`). Never a universal `MetricContext` with optional-everything.

## 7. Output contract

`compute()` returns `Tensor` or `dict[str, Tensor]`. The evaluation boundary reads `ScalarMetricResult(value, direction)` from `metrics/contracts.py` and wraps it into `EvaluatedMetricResult` for result assembly.

## 8. MetricSpec placement

`MetricSpec` and `TaskScoringSpec` live canonically in `contracts/scoring.py`.
Both `tasks` and `metrics` import them from `ehp_sn.contracts`.

`RatioStat` lives canonically in `contracts/statistics.py` and is shared
by `metrics` (aggregation) and `objectives` (`TaskStepEvaluation`).

## 9. Package structure

```
ehp_sn/metrics/
├── contracts.py       # MetricRequirements, ScalarMetricResult
├── functional/        # Stateless metric functions (exact_sequence_match, token_accuracy, …)
├── state.py           # torchmetrics.Metric subclasses (ExactSequenceMatch, MaskedCategoricalAccuracy, …)
└── catalog.py         # Metric name → implementation mapping
```

## 10. Design contract

> Metrics owns aggregation algorithms. Evaluation owns aggregation orchestration. Every metric formula has one authoritative implementation shared by functional and stateful APIs. Sufficient statistics produce correct results under uneven batches, variable-length sequences, DDP, dynamic masks, and unequal splits.
