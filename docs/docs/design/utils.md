# Utility Architecture

<!-- canonical_package: ehp_sn  authority: canonical  status: accepted -->

> `ehp_sn.utils` — domain-neutral, dependency-light technical primitives. L0.

---

## Normative summary

| Rule                  | Value                                                                                                                               |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Domain-neutral tensor validation, tree traversal, graph algorithms                                                                  |
| **Must not own**      | Domain contracts; scientific computation; configuration; logging setup                                                              |
| **Public API**        | `tensors`, `trees`, `graph` (submodules only — `__all__ = []` at package level; all symbols accessed via qualified submodule paths) |
| **Allowed imports**   | stdlib, `numpy`, `torch`, `scipy` (narrow)                                                                                          |
| **Forbidden imports** | Any `ehp_sn.*` domain package (including `contracts` and `types`)                                                                   |
| **Layer**             | L0 — Foundation                                                                                                                     |
| **Key invariant**     | `utils` is not a dumping ground; owns no domain concepts                                                                            |

---

## 1. Admission rule

A function belongs in `utils` only when: (1) domain-neutral, (2) no policy, (3) multiple independent consumers, (4) narrow dependency cone, (5) explicit invariants documented and tested.

**Dependency invariant:** `stdlib, numpy, torch, scipy → ehp_sn.utils`. Utils is imported by `contracts, data, modules, models, …`. Utils never imports any `ehp_sn.*` domain package, including `contracts` and `types`.

**Rejected names** (must never exist): `common.py`, `helpers.py`, `misc.py`, `general.py`, `math.py`, `config.py`, `logging.py`, `io.py`, `model_utils.py`, `training_utils.py`, `paths.py`.

## 2. Submodules

| Module       | Purpose                                                                                          | Created when                                     |
| ------------ | ------------------------------------------------------------------------------------------------ | ------------------------------------------------ |
| `tensors`    | Shape/rank/device/dtype validation, masked reductions (`masked_reduce_mean`), structural row ops | Now — demanded by codebase                       |
| `trees`      | Recursive traversal, detach, clone, device movement, `tree_merge_rows`                           | Now — demanded by codebase                       |
| `graph`      | BFS, shortest path, path counting, layered DAG positions                                         | Now — demanded by codebase                       |
| `randomness` | `derive_seed`, `make_torch_generator`                                                            | Now                                              |
| `imports`    | Optional dependency detection                                                                    | When multiple packages duplicate detection logic |
| `symmetry`   | Dihedral transforms                                                                              | When ≥2 cross-package consumers exist            |

## 3. What does NOT belong in utils

| Excluded                                             | Owner                                 |
| ---------------------------------------------------- | ------------------------------------- |
| Domain contracts (`TaskRuntime`, `RolloutBatch`)     | `contracts/`                          |
| MEC/HPC logic (`inv_var_trans`, `connections`)       | `modules/spatial/`, `modules/memory/` |
| Projection construction (`create_downsample_matrix`) | `modules/projection.py`               |
| Loss semantics (`squared_error`)                     | `objectives/`                         |
| Task graph generation (`generate_hamiltonian_dag`)   | `data/substrate/`                     |
| Configuration merging (`apply_overrides`)            | `ehp_sn/configuration/` (planned)     |
| Wrappers over `torch.nn.functional`                  | Remove; use PyTorch directly          |

## 4. Consumer style

```python
from ehp_sn.utils.tensors import require_shape, merge_rows
from ehp_sn.utils.trees import tree_detach
from ehp_sn.utils.graph import shortest_path
```

Never: `from ehp_sn.utils import merge_rows` or `from ehp_sn.utils import *`.

## 5. Design contract

> Utils provides domain-neutral infrastructure. It depends only on stdlib, numpy, torch, scipy. It never imports any ehp_sn domain package. Submodules are created only when current code demonstrates need.

## 6. Resolved design decisions

| Decision                                         | Resolution                                                                                                                                                                                                | Date       |
| ------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------- |
| **G-01** — `masked_mean` collision with `loss`   | `utils.tensors` exports `masked_reduce_mean` (dim-aware reduction). `loss.primitives` owns `masked_mean` (scalar reduction with `empty_policy`). Distinct names, distinct semantics.                      | 2026-07-01 |
| **G-02** — `__all__` for submodule-only packages | `__all__ = []` at package level. No flattened symbols. Consumers use qualified submodule paths (e.g. `from ehp_sn.utils.tensors import require_shape`). This is an architectural invariant, not a defect. | 2026-07-01 |
