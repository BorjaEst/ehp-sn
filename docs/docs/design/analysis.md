# Analysis Design

<!-- canonical_package: ehp_sn  authority: canonical  status: draft -->

> `ehp_sn.analysis` — deterministic post-evaluation transformation: consumes artifacts, produces typed domain-level analytical results.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                                                          |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Scientific interpretation (grid scores, place fields, RSA, pathway aggregates, latent projections); `AnalysisDefinition`, `AnalysisResult`; consumer-owned protocols (`TraceArtifactReader`, `TraceView`)      |
| **Must not own**      | Model execution; visual rendering; trace loading; artifact persistence                                                                                                                                         |
| **Public API**        | `AnalysisDefinition`, `AnalysisRequest`, `AnalysisPlan`, `AnalysisResult`, `AnalysisPayload`, `TraceArtifactReader`, `TraceView`, `analyze`, `compile_analysis`, `execute_analysis`                            |
| **Allowed imports**   | `evaluation` (R: contracts only), `contracts` (R), `types` (R), `numpy`, `scipy`; **P:** `diagnostics` (`DiagnosticFinding`); `traces` (P: types only — `TraceKey`, `TraceArtifact`, for adapter construction) |
| **Forbidden imports** | `figures`, `training`, `controllers`, `objectives`, `lightning`                                                                                                                                                |
| **Layer**             | L6 — Post-Processing & Presentation                                                                                                                                                                            |
| **Key invariant**     | Analysis consumes immutable artifacts via reader protocols; never executes evaluation or training                                                                                                              |

> **Cross-reference:** `contracts.md` §2: analysis may import evaluation _contract types_ only, never execution machinery.

---

## 1. Architectural position

```
model/runtime → evaluation (produces artifacts) → analysis (consumes artifacts, produces domain results) → figures/reports
```

One-way downstream of evaluation. Never imports from figures, training, controllers, objectives, or lightning.

## 2. Lifecycle

```
AnalysisDefinition → AnalysisRequest → AnalysisPlan (resolved, validated, topo-sorted DAG)
    → execute → AnalysisResult (payload + provenance) → PersistedAnalysisResult (artifacts)
```

## 3. Core concepts

### 3.1 Product model

Analysis declares what it needs, not how to collect it. A `ProductInventory` resolves requirements against available descriptors.

```python
@dataclass(frozen=True)
class ProductRequirement:
    key: str
    schema_version: int

@dataclass(frozen=True)
class ProductDescriptor:
    key: str
    schema_version: int
    media_type: str          # e.g. "application/zarr"
    dimensions: tuple[str, ...]
    producer_identity: str | None = None

class ProductInventory(Protocol):
    def lookup(self, requirement: ProductRequirement) -> ProductDescriptor | None: ...
    def list_available(self) -> tuple[ProductDescriptor, ...]: ...
```

### 3.2 Definition–implementation separation

`AnalysisDefinition` is pure declarative data (name, version, required products, produced artifact keys, parameter schema). `AnalysisBinding` couples a definition to the factory that constructs its analyzer — keeping definitions pure and factories independently evolvable.

### 3.3 Analysis payload

Analyzers return a semantic payload — no persistence, no artifact references. The executor wraps it with provenance.

```python
@dataclass(frozen=True)
class AnalysisPayload:
    scalars: Mapping[str, Scalar]
    tables: Mapping[str, xr.Dataset | pa.Table]
    arrays: Mapping[str, xr.DataArray]
    diagnostics: tuple[Diagnostic, ...] = ()

@dataclass(frozen=True)
class AnalysisResult:
    analysis_name: str
    analysis_version: int
    parameters: Mapping[str, JSONValue]
    provenance: Provenance
    payload: AnalysisPayload
```

`AnalysisResult` does **not** contain output artifact references — those don't exist until persistence. Output references live in `PersistedAnalysisResult.artifacts`.

### 3.4 Pure kernels and analyzers

- **Pure kernels**: `compute_gridness(autocorrelation, geometry) → GridnessResult`. Testable without storage, registries, or MLflow. NumPy only.
- **Analyzers**: wrap kernels with parameter resolution. Still I/O-free. The executor owns loading and persistence.
- **Provenance**: every result carries immutable `Provenance(operation_name, version, implementation_path, code_revision, parameter_digest, input_artifacts)`.
- **Diagnostics**: `Diagnostic` objects at multiple lifecycle points (plan, context, payload). Single model avoids duplication.

## 4. I/O separation

| Operation | Nature          | Test strategy    |
| --------- | --------------- | ---------------- |
| `load`    | effectful read  | mock reader      |
| `compute` | pure            | synthetic arrays |
| `persist` | effectful write | mock writer      |

## 5. Multi-resolution API

- **Tier 1**: `analyze(AnalysisRequest(...))` — ordinary consumer.
- **Tier 2**: `compile_analysis(request, registry, inventory) → plan; execute_analysis(plan, registry, reader, writer, context)` — framework integrator.
- **Tier 3**: `compute_gridness(autocorrelation, geometry)` — scientific developer (fastest iteration).

## 6. Design contract

> Analysis owns scientific interpretation. It consumes immutable evaluation and trace artifacts via reader protocols. Pure kernels are testable without infrastructure. The executor owns I/O. Results carry provenance.
