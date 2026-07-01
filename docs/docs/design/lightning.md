# Lightning Adapter Design

<!-- canonical_package: ehp_sn  authority: canonical  status: draft -->

> A narrow execution adapter around framework-independent training runtimes.

---

## Normative summary

| Rule                  | Value                                                                                                                                                           |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | LightningModule adapters; DataModule adapters; Trainer/callback/logger construction; checkpoint storage integration; `loss.backward()` as framework primitive   |
| **Must not own**      | Model architecture; loss mathematics; metric definitions; rollout algorithms; dataset formats; backward policy (when to call)                                   |
| **Public API**        | `TaskLightningModule`, `ManualOptimizationLightningModule`, `EHPDataModule`, `build_trainer`, `build_lightning_optimization`                                    |
| **Allowed imports**   | `training` (R), `models` (R), `objectives` (R), `contracts` (R); **P:** `data`, `metrics`, `evaluation` (contracts), `utils`, `logging`                         |
| **Forbidden imports** | (none — top of dependency stack)                                                                                                                                |
| **Layer**             | Backend adapter boundary (sidecar). Not a domain architectural layer.                                                                                           |
| **Key invariant**     | Lightning imports domain packages to wrap them. No domain package (L0–L3, L5–L6) may import from `lightning/`. The dependency is strictly `lightning → domain`. |

---

## 1. Core principle: adapt, do not define

`ehp_sn.lightning` does not define how training works. It adapts an already-defined training runtime for execution by `lightning.pytorch.Trainer`. Lightning implements the `TrainingRuntime` protocol defined in `training/contracts.py`. Lightning's core function **requires** importing `training` for this protocol; without it, Lightning cannot wrap any EHP training runtime. The scientific system remains usable without Lightning.

```
Domain (training, models, objectives)
        ↓ (imports)
ehp_sn.lightning  ← Backend adapter (sidecar)
        ↓ (wraps)
lightning.pytorch.Trainer
```

> **Note:** The `lightning → training` import is a REQUIRED dependency. Lightning cannot function as a backend adapter without importing `training` for the `TrainingRuntime` protocol. This is the only case where a sidecar REQUIRES a domain package — all other sidecar imports are permitted (P).

### What it must not own

| Concern                                 | Owner         |
| --------------------------------------- | ------------- |
| Neural network architectures            | `models`      |
| Loss mathematics                        | `objectives`  |
| Metric definitions and route selection  | `metrics`     |
| Rollout algorithms                      | `rollouts`    |
| Recurrent carry semantics               | `rollouts`    |
| Dataset formats and source construction | `data`        |
| Task contracts                          | `tasks`       |
| Evaluation aggregation                  | `evaluation`  |
| Trace schemas                           | `traces`      |
| Experiment resolution                   | `experiments` |
| Model construction policy               | `experiments` |
| Figure generation                       | `figures`     |
| Backward policy (when to call)          | `training`    |
| Checkpoint emission policy              | `training`    |

**Invariant:** `ehp_sn.lightning` imports `ehp_sn.training, models, objectives` (R) and optionally `data, metrics, evaluation` (P). No domain package imports `lightning`. The dependency is strictly `lightning → domain`, never `domain → lightning`.

## 2. Package structure

```
ehp_sn/lightning/
├── modules.py          # TaskLightningModule, ManualOptimizationLightningModule
├── datamodule.py       # EHPDataModule
├── trainer.py          # build_trainer(), build_callbacks()
├── optimization.py     # build_lightning_optimization()
├── checkpointing.py    # Checkpoint schema metadata
├── callbacks/          # diagnostics, evaluation, figures, progress
└── logging.py          # MLflow logger construction
```

## 3. LightningModule adapters

Two adapters cover all regimes:

| Adapter                             | Optimisation           | Regimes                 |
| ----------------------------------- | ---------------------- | ----------------------- |
| `TaskLightningModule`               | Automatic              | TEM v1/v2, HRM v1 (ACT) |
| `ManualOptimizationLightningModule` | Manual (per-optimizer) | HRM v2 (actor-critic)   |

Both delegate to a framework-independent `TrainingRuntime` that owns all mutable state (carry, source cursor, schedule state, metric accumulators). The Lightning module sees only typed step results.

### TrainingRuntime protocol (in `training/`)

```python
class TrainingRuntime(Protocol):
    def training_step(self, batch, context) -> TrainingStepResult: ...
    def validation_step(self, batch, context) -> EvaluationStepResult: ...
    def compute_train_metrics(self) -> dict[str, float]: ...
    def compute_validation_metrics(self) -> dict[str, float]: ...
    def state_dict(self) -> dict: ...
    def load_state_dict(self, state): ...
```

**Critical rule:** The Lightning module must not import metric keys or route tuples. It receives **computed** scalars from `compute_validation_metrics()` — it never accumulates raw numerators.

## 4. DataModule adapter

`EHPDataModule` wraps a framework-independent `DataProvider` protocol. The Lightning module receives a **source factory** during construction, never reaches into `self.trainer.datamodule._train`.

## 5. Optimizer construction

`build_lightning_optimization(spec: OptimizationSpec)` translates project specs to Lightning's optimizer/scheduler format. The runtime owns parameter group mapping (`runtime.parameter_groups()`); the Lightning builder must not inspect submodule paths.

## 6. Evaluation callback

Evaluation callbacks enforce: `torch.inference_mode()` during evaluation, model restored to `train()` after, training carry saved/restored, isolated dataloaders. The callback calls a framework-independent evaluator and logs only scalar summaries.

## 7. Design contract

> `ehp_sn.lightning` is a replaceable backend adapter. It translates framework-independent EHP runtimes into Lightning's lifecycle. Every domain package remains Lightning-free. The invariant is: `lightning → domain`, never `domain → lightning`.
