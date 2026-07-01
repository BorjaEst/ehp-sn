# Diagnostics Architecture

<!-- canonical_package: ehp_sn  authority: canonical  status: draft -->

> `ehp_sn.diagnostics` — model internals inspection: probes, health checks, and trace assessments.

---

## Normative summary

| Rule                  | Value                                                                                                                                                             |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Health checks; diagnostic probes; `DiagnosticFinding`, `DiagnosticReport`; severity classification; probe registry                                                |
| **Must not own**      | Metric accumulation; trace capture; figure rendering; training execution; evaluation orchestration                                                                |
| **Public API**        | `DiagnosticFinding`, `DiagnosticReport`, `DiagnosticSeverity`, `DiagnosticCode`, `ProbeDefinition`, `HealthCheck`, `run_health_checks`                            |
| **Allowed imports**   | `contracts` (R), `types` (R); **P:** `models` (state types and health-check protocols only), `traces` (`TraceStoreReader` — offline probes only)                  |
| **Forbidden imports** | `training`, `lightning`, `evaluation` (execution internals), `controllers`, `objectives`, `rollouts`, `figures`, `analysis`, `reporting`                          |
| **Layer**             | L5 — Observability & Evaluation                                                                                                                                   |
| **Key invariant**     | Diagnostics inspects model internals through three paths (offline probes, health checks, evaluation traces); measurement thresholds are separate from probe logic |

---

## 1. Three diagnostic paths

| Path              | Purpose                            | Trigger                  | Output                     |
| ----------------- | ---------------------------------- | ------------------------ | -------------------------- |
| Offline probes    | Deep single-episode mechanism test | Manual (script/notebook) | Pydantic Result (JSON)     |
| Health checks     | Runtime safety/sanity              | Lifecycle hooks          | `DiagnosticFinding` list   |
| Evaluation traces | Population-level evidence          | Evaluation run           | Zarr archive + metrics.csv |

## 2. Core contracts

### 2.1 `DiagnosticCode` — canonical vocabulary

Codes follow a `subsystem.short_name` convention. Consumers filter and route findings by code without knowing the producing module.

```python
class DiagnosticCode(StrEnum):
    # TEM memory
    MEMORY_DYNAMICS = "tem.memory_dynamics"
    ATTRACTOR_DIVERGENCE = "tem.attractor_divergence"
    QUERY_ALIGNMENT_FAILURE = "tem.query_alignment_failure"
    CONVERGENCE_DEPTH = "tem.convergence_depth"
    WEAK_SENSORY_CORRECTION = "tem.weak_sensory_correction"
    # TEM pathway
    PATHWAY_CONTENT_LOSS = "tem.pathway_content_loss"
    PATHWAY_LATE_DECAY = "tem.pathway_late_decay"
    PATHWAY_PLACE_CODE_LOSS = "tem.pathway_place_code_loss"
    PATHWAY_DECODER_MISMATCH = "tem.pathway_decoder_mismatch"
    # HRM dynamics
    HRM_HIGH_LEVEL_COLLAPSE = "hrm.high_level_collapse"
    HRM_LOW_LEVEL_COLLAPSE = "hrm.low_level_collapse"
    HRM_DELTA_RATIO_ANOMALY = "hrm.delta_ratio_anomaly"
    # Numerical health
    NAN_IN_GRADIENTS = "numerical.nan_in_gradients"
    NAN_IN_ACTIVATIONS = "numerical.nan_in_activations"
    EXPLODING_GRADIENTS = "numerical.exploding_gradients"
    VANISHING_GRADIENTS = "numerical.vanishing_gradients"
    PARAMETER_UPDATE_RATIO = "numerical.parameter_update_ratio"
    # Replay / carry health
    CARRY_STALE_STATE = "replay.carry_stale_state"
    HALT_REACTIVATION = "replay.halt_reactivation"
    SLOT_UNDERUTILIZATION = "replay.slot_underutilization"
    # Resource health
    CUDA_MEMORY_GROWTH = "resource.cuda_memory_growth"
    STEP_TIME_REGRESSION = "resource.step_time_regression"
```

### 2.2 `DiagnosticFinding` and `DiagnosticReport`

```python
@dataclass(frozen=True, slots=True)
class DiagnosticFinding:
    code: DiagnosticCode
    severity: DiagnosticSeverity  # PASS < WARNING < ERROR < CRITICAL < SKIPPED < INTERNAL
    message: str
    details: str | None = None
    source: str = ""                # e.g. "tem_memory_probe", "grad_check"
    observed: Mapping[str, float] = field(default_factory=dict)
    expected: Mapping[str, float] = field(default_factory=dict)
    threshold: Mapping[str, float] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class DiagnosticReport:
    findings: tuple[DiagnosticFinding, ...]
    worst_severity: DiagnosticSeverity
    source_hint: str = ""
```

### 2.3 `ProbeDefinition`

- **`ProbeDefinition[InputT, ResultT]`**: name, model families, produce callable, load callable.

**Policy separation:** Measurement thresholds live in policy objects (`NumericalHealthPolicy`, `ReplayHealthPolicy`), not embedded in probe logic. This decouples measurement, policy, and interpretation.

## 3. Probe catalogue

| Probe                 | Model  | Question                         | Status |
| --------------------- | ------ | -------------------------------- | ------ |
| `tem_memory`          | TEM    | Can Hebbian M self-retrieve?     | STUB   |
| `tem_pathway`         | TEM    | Where is content lost in decode? | STUB   |
| `tem_query_alignment` | TEM    | Does mec_to_hpc(g) index memory? | STUB   |
| `cue_recall`          | HRM v1 | Can HRM recall cued WM item?     | STUB   |
| `hrm_dynamics`        | HRM    | How do PFC states evolve?        | STUB   |

## 4. Health check catalogue

| Check                 | Hook             | Tests                                   | Status |
| --------------------- | ---------------- | --------------------------------------- | ------ |
| `nan_activations`     | `after_forward`  | NaN in activations (CRITICAL)           | STUB   |
| `nan_gradients`       | `after_backward` | NaN in gradients (CRITICAL)             | STUB   |
| `exploding_gradients` | `after_backward` | Max grad norm > threshold (WARNING)     | STUB   |
| `vanishing_gradients` | `after_backward` | Min grad norm < threshold (WARNING)     | STUB   |
| `loss_divergence`     | `after_loss`     | Loss increased >10× in one step (ERROR) | STUB   |
| `latent_collapse`     | `after_forward`  | Mean hidden norm < threshold (WARNING)  | STUB   |

## 5. Integration

| Upstream/downstream package | Contract types                      | Direction       | Purpose                              | Status |
| --------------------------- | ----------------------------------- | --------------- | ------------------------------------ | ------ |
| `contracts`                 | Foundation types                    | ← (imports)     | Shared vocabulary, error hierarchy   | R      |
| `models`                    | State types, health-check protocols | ← (imports)     | Model internals for probe inspection | P      |
| `traces`                    | `TraceStoreReader`                  | ← (imports)     | Offline probe trace access           | P      |
| `evaluation`                | (execution internals forbidden)     | — (no import)   | —                                    | F      |
| `training`                  | (forbidden)                         | — (no import)   | —                                    | F      |
| `lightning`                 | (forbidden)                         | — (no import)   | —                                    | F      |
| `controllers`               | (forbidden)                         | — (no import)   | —                                    | F      |
| `objectives`                | (forbidden)                         | — (no import)   | —                                    | F      |
| `rollouts`                  | (forbidden)                         | — (no import)   | —                                    | F      |
| `analysis`                  | (consumer of `DiagnosticFinding`)   | → (consumed by) | Scientific interpretation input      | P      |
| `figures`                   | (forbidden as import source)        | —               | —                                    | F      |
| `reporting`                 | (consumer of `DiagnosticReport`)    | → (consumed by) | Model-health evidence in reports     | P      |

See also: [contracts.md §4.2](contracts.md) for producer-owned contracts; [models.md](models.md) for state types; [traces.md §6](traces.md) for `TraceStoreReader`; [analysis.md](analysis.md) for `Diagnostic` consumption; [reporting.md](reporting.md) for `DiagnosticReport` consumption.

## 6. Package structure

```
ehp_sn/diagnostics/
├── contracts.py       # DiagnosticFinding, DiagnosticReport, DiagnosticCode, DiagnosticSeverity
├── probes.py          # ProbeDefinition, probe registry, offline probe implementations
├── health.py          # HealthCheck protocol, health check implementations
└── policies.py        # NumericalHealthPolicy, ReplayHealthPolicy
```

## 7. Design contract

> Diagnostics inspects model internals through three paths: offline probes for deep mechanism tests, lifecycle health checks for runtime safety, and trace assessments for population evidence. Policies are separate from measurements. All outputs are `DiagnosticFinding` objects with canonical codes.
