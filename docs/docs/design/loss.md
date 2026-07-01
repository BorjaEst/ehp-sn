# Loss Design

<!-- canonical_package: ehp_sn  authority: canonical  status: accepted -->

> `ehp_sn.loss` — pure differentiable mathematical functions with no domain knowledge.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                                        |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Stateless loss primitives (`softmax_cross_entropy`, `mse_consistency`, `masked_mean`, etc.)                                                                                                  |
| **Must not own**      | Objective composition; task semantics; model execution; metric accumulation; training orchestration                                                                                          |
| **Public API**        | `masked_mean`, `masked_sum`, `softmax_cross_entropy`, `mse_consistency`, `gaussian_kl_divergence`                                                                                            |
| **Allowed imports**   | `torch` (only)                                                                                                                                                                               |
| **Forbidden imports** | Any `ehp_sn.*` package                                                                                                                                                                       |
| **Layer**             | L1 — Domain Primitives                                                                                                                                                                       |
| **Key invariant**     | Loss owns pure mathematical primitives; every function is a stateless tensor→tensor transformation with no domain knowledge; no `.item()`, `.detach()`, or `.numpy()` in differentiable path |

---

## 1. Vocabulary

| Term               | Definition                                                                                          | Example                                  |
| ------------------ | --------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| **Loss primitive** | A single differentiable mathematical function on tensors                                            | `mse_consistency(pred, target) → (B,)`   |
| **Objective**      | The complete optimisation policy for one model/task combination                                     | `TEMObjective`, `ACTSupervisedScorer`    |
| **Metric**         | Detached evaluation measurement — no gradient flow                                                  | `accuracy_obs_post_revisit`, `field_mae` |
| **Regulariser**    | A differentiable constraint not tied to a supervised target                                         | `l2_penalty(grid_code)`                  |
| **Signal**         | A scalar telemetry value accompanying an objective result — detached, logged, never back-propagated | `grid_post_norm`, `rpe_magnitude`        |

## 2. Three-layer architecture

```
torch → loss primitives → objectives → metrics/training/lightning
```

| Layer      | Package      | Responsibility                     |
| ---------- | ------------ | ---------------------------------- |
| Primitives | `loss`       | Pure `(B,D)→(B,)` tensor functions |
| Objectives | `objectives` | Compose, mask, weight, normalize   |
| Metrics    | `metrics`    | Detached evaluation measurement    |

## 3. Primitive inventory

**Reductions:** `masked_mean(values, mask, empty_policy)`, `masked_sum(values, mask)`.

> **Design decision (G-01):** `loss.primitives.masked_mean` is the canonical **scalar** masked reduction with `empty_policy`. The dim-aware general-purpose variant lives at `utils.tensors.masked_reduce_mean` (see `utils.md` §6). Distinct names, distinct semantics.

**Consistency:** `mse_consistency(pred, target) → (B,)`, `nll_consistency(pred, mean, std) → (B,)`.

**Cross-entropy:** `softmax_cross_entropy(logits, labels) → (B,S)`.

> **`stablemax_cross_entropy`** is **unavailable** (not exported).
> A concrete StableMax variant must be selected and defined in §7 before
> the function can be added to the public API. See §7 for the specification
> template.

**Regularization:** `l1_penalty(code) → (B,)`, `l2_penalty(code) → (B,)`.

**Divergences:** `gaussian_kl_divergence(posterior_mean, posterior_std, prior_mean, prior_std) → (B,)`.

All elementwise primitives return **unreduced** `(B,)` or `(B, S)` tensors. Reduction primitives aggregate explicitly. No `.item()`, `.detach()`, or logging.

## 4. Invariants

| Property          | Enforcement                                                          |
| ----------------- | -------------------------------------------------------------------- |
| No model imports  | Primitives depend only on `torch`                                    |
| No training state | Pure functions; `nn.Module` subclasses carry no trainable parameters |
| Unreduced output  | Elementwise primitives return `(B,)` or `(B, ...)`                   |
| Device-safe       | No `.item()`, `.cpu()`, `.numpy()` in differentiable path            |
| Graph-preserving  | No `.detach()` in loss value path                                    |

## 5. Design contract

> Loss owns pure mathematical primitives. Every function is a stateless tensor→tensor transformation with no domain knowledge. Objectives compose and weight these primitives. The dependency direction is strictly `loss ← objectives`.

## 6. Cross-entropy contract

`softmax_cross_entropy` SHALL accept logits of shape `(..., C)` and integer class-index targets of shape `(...)`. Targets SHALL use an integer dtype compatible with PyTorch class-index cross-entropy. One-hot or probabilistic targets are not accepted by this primitive.

```
logits: Tensor  # shape (B, S, C)
labels: Tensor  # shape (B, S), integer class indices in [0, C-1]
```

| Property       | Rule                                                                    |
| -------------- | ----------------------------------------------------------------------- |
| Target range   | `0 ≤ labels[i,j] < C`                                                   |
| Target dtype   | Integer (typically `int64`); floating-point targets rejected            |
| Output shape   | `(B, S)` — unreduced per-token loss                                     |
| `ignore_index` | Not supported by this primitive; masking is the caller’s responsibility |
| Soft targets   | Use a separately named primitive (e.g. `soft_target_cross_entropy`)     |

## 7. StableMax specification

`stablemax_cross_entropy` SHALL implement the StableMax variant defined by this specification. The implementation SHALL NOT delegate to ordinary softmax cross-entropy.

```
stablemax(logits) = normalize(stable_transform(logits))
loss = -log(stablemax(logits)[target])
```

| Property                         | Rule                                                             |
| -------------------------------- | ---------------------------------------------------------------- |
| Variant                          | TBD — poly-ST-Max, log-ST-Max, or another named variant          |
| Numerical stabilization          | TBD — must be specified before implementation                    |
| Logits shape                     | `(B, S, C)`                                                      |
| Target shape, dtype              | `(B, S)`, integer class indices                                  |
| Reduction                        | `"none"` — per-token `(B, S)` output                             |
| Masking / `ignore_index`         | Not supported by this primitive                                  |
| Mixed precision                  | TBD — must be specified before implementation                    |
| Class weighting, label smoothing | Not supported by this primitive                                  |
| Gradient behaviour               | Bounded gradients for arbitrarily large positive/negative logits |

**Until the variant and stabilization are specified, this function SHALL remain unimplemented** (must not silently behave as ordinary `softmax_cross_entropy`).

## 8. Package structure

```
ehp_sn/loss/
├── __init__.py         # Re-exports all primitives
└── primitives.py       # masked_mean, masked_sum, softmax_cross_entropy, mse_consistency,
                        #   nll_consistency, l1_penalty, l2_penalty, gaussian_kl_divergence
```
