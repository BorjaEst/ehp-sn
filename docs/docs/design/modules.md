# Module Design

<!-- canonical_package: ehp_sn  authority: canonical  status: accepted -->

> `ehp_sn.modules` — reusable `torch.nn.Module` components: the shared neural vocabulary.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                      |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Attention, MLP, transformer blocks; embeddings, projections; recurrent cells; memory read/write operators; spatial primitives; prediction heads; workspace slot-addressing |
| **Must not own**      | Complete TEM/HRM/EHP architectures; subsystem orchestration; ACT deliberation; loss objectives; training loops                                                             |
| **Public API**        | `Attention`, `MLP`, `ProjectionModule`, `SwiGLU`, `TransformerBlock`, `TransformerStack`, `TwoTimescaleCell`, `Workspace`                                                  |
| **Allowed imports**   | `contracts`, `types`, `utils`, `functional`, `einops`                                                                                                                      |
| **Forbidden imports** | `models`, `controllers`, `objectives`, `metrics`, `lightning`, `evaluation`, `training`, `rollouts`, `traces`, `diagnostics`                                               |
| **Layer**             | L2 — Computation                                                                                                                                                           |
| **Key invariant**     | Modules are reusable neural building blocks — one bounded transformation, independently testable without knowledge of model family, task, dataset, or training recipe      |

---

## 1. Distinguish modules from models

| Package   | Role                                                                                  | Test                                                                                      |
| --------- | ------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `modules` | Reusable building block — one bounded transformation                                  | Can be tested without knowing model family, task, dataset, controller, or training recipe |
| `models`  | Complete architecture — coordinates multiple transformations with lifecycle semantics | Cannot                                                                                    |

## 2. Component classification

Two questions decide placement:

> **Q1.** Can this component be instantiated and tested without knowing which model family, task, dataset, controller, or training recipe uses it?
> **Q2.** Does the component execute _one_ neural transformation, or does it coordinate a sequence with lifecycle and phase semantics?

**Q1 yes + Q2 "one transformation"** → `modules`. **Q1 no or Q2 "coordination"** → `models` or `controllers`.

| Component                                                                              | Current location                            | Classification          | Recommendation                 |
| -------------------------------------------------------------------------------------- | ------------------------------------------- | ----------------------- | ------------------------------ |
| `Attention`                                                                            | `modules/attention.py`                      | Reusable primitive      | **Keep**                       |
| `SwiGLU`, `MLP`                                                                        | `modules/mlp.py`                            | Reusable primitive      | **Keep**                       |
| `TransformerBlock`, `TransformerStack`                                                 | `modules/transformer.py`                    | Reusable primitive      | **Keep**                       |
| `TwoHotEncoder`                                                                        | `modules/autoencoder.py`                    | Reusable primitive      | **Keep**                       |
| `ProjectionModule`, `ProjectionBundle`                                                 | `modules/projection.py`                     | Reusable primitive      | **Keep**                       |
| `PlaceInference`                                                                       | `modules/memory/place.py`                   | Reusable primitive      | **Keep**                       |
| `AttractorRead`, `FactorRead`                                                          | `modules/memory/read.py`                    | Reusable primitive      | **Keep**                       |
| `HebbianWrite`, `EpisodicWrite`                                                        | `modules/memory/write.py`                   | Reusable primitive      | **Keep**                       |
| `PathIntegrator`                                                                       | `modules/spatial/path.py`                   | Reusable primitive      | **Keep**                       |
| `FrequencyFilter`                                                                      | `modules/spatial/filter.py`                 | Reusable primitive      | **Keep**                       |
| `FeatureNorm`                                                                          | `modules/spatial/norm.py`                   | Reusable primitive      | **Keep**                       |
| `HighLvRModule`, `LowLvRModule`                                                        | `modules/recurrent/high_lv.py`, `low_lv.py` | Recurrent cells         | **Keep**                       |
| `QValueEstimator`                                                                      | `modules/heads/qvalue.py`                   | Reusable primitive      | **Keep**                       |
| `Workspace`, `WorkspaceSchema`                                                         | `modules/workspace/core.py`, `schema.py`    | Reusable primitive      | **Keep**                       |
| `compute_rpe()`                                                                        | `functional/encoding.py`                    | Pure function           | **Keep** (moved, impl Q3 2026) |
| `HPCBase`                                                                              | (not yet implemented)                       | Subsystem orchestration | **Move** to `models.tem`       |
| `HPCAttractor`, `HPCAttention`                                                         | (not yet implemented)                       | Memory subsystems       | **Move** to `models.tem`       |
| `ReadCues`, `CueRead`, `TargetRead`                                                    | (not yet implemented)                       | TEM-specific semantics  | **Move** to `models.tem`       |
| `MECModel`                                                                             | (not yet implemented)                       | Subsystem orchestrator  | **Move** to `models.tem`       |
| `LECModel`                                                                             | (not yet implemented)                       | Subsystem orchestrator  | **Move** to `models.tem`       |
| `PFCModel`                                                                             | (not yet implemented)                       | Subsystem orchestrator  | **Move** to `models.hrm`       |
| `STRModelLinear`                                                                       | (not yet implemented)                       | Actor-critic subsystem  | **Move** to `models.hrm`       |
| `MECLayout`, `P2GMemory`, `OVCCorrection`, `DenseHebbianStoreBackend`, `HebbianLayout` | (not yet implemented)                       | TEM memory-coupled      | **Move** to `models.tem`       |

## 3. Module contract

- Subclass `torch.nn.Module`.
- One bounded neural transformation or local state transition.
- Document input shape, output shape, mask semantics, state semantics.
- Independently testable.
- No task, experiment, or training recipe dependency.
- Methods named `forward` (model-level verbs like `generative`, `inference` belong in `models`).
- Episode-boundary reset is a model-level concern — module state is explicit, passed in/out.

## 4. Distinguish modules from functional

|             | `functional`                   | `modules`                                     |
| ----------- | ------------------------------ | --------------------------------------------- |
| Interface   | `def fn(tensor, ...) → tensor` | `class Mod(nn.Module)` with `forward`         |
| Composition | Called directly                | Plugged into `nn.Sequential`, `torch.compile` |
| State       | No persistent state            | May own `nn.Parameter`, `register_buffer`     |

> **Note:** `ehp_sn/functional/` exists as an L1 package for stateless tensor functions (e.g. `compute_rpe()`). Pure equations that don't require `nn.Module` should live there, not in `modules/`.

## 5. Design contract

> Modules is the reusable neural vocabulary. Models are the architectural sentences. Controllers are the execution policy. Functional is the equations. Contracts is the shared language. Objectives are the learning criteria.
