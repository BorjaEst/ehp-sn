# Reporting Design

<!-- canonical_package: ehp_sn  authority: canonical  status: draft -->

> `ehp_sn.reporting` — deterministic composition service: selects evaluation evidence, normalises it, composes according to a report definition.

---

## Normative summary

| Rule                  | Value                                                                                                                                                                                        |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Report definitions, requests, source resolution; evidence normalisation; composition; serialisation; rendering; publication                                                                  |
| **Must not own**      | Model execution; metric computation; evaluation results; trace capture; figure rendering; scientific analysis                                                                                |
| **Public API**        | `ReportResult`, `ReportDefinition`, `ReportRequest`, `ReportSource`, `ReportContext`, `ReportDataPackage`, `ReportArtifact`, `open_report`                                                   |
| **Allowed imports**   | `analysis` (R: AnalysisResult), `figures` (R: FigureArtifact), `contracts` (R); **P:** `evaluation` (contracts), `diagnostics` (DiagnosticReport)                                            |
| **Forbidden imports** | `models`, `training`, `lightning`, `controllers`, `objectives`                                                                                                                               |
| **Layer**             | L6 — Post-Processing & Presentation                                                                                                                                                          |
| **Key invariant**     | Reporting is the terminal composition layer; it consumes typed results from evaluation, figures, analysis, and diagnostics without executing models, computing metrics, or rendering figures |

---

## 1. Core flow

```
evaluation evidence → normalised ReportContext → semantic ReportResult → serialised bundle or rendered document
```

`reporting = report definition + source resolution + evidence normalisation + compatibility validation + semantic section composition + provenance construction + serialisation + rendering + publication`

### Does not own

| Concern                               | Owner         |
| ------------------------------------- | ------------- |
| Model execution, checkpoint loading   | `models`      |
| Metric computation and accumulation   | `metrics`     |
| Primary scientific evaluation results | `evaluation`  |
| Trace capture, schemas, persistence   | `traces`      |
| Figure rendering                      | `figures`     |
| Post-hoc scientific computation       | `analysis`    |
| Model-health diagnostics              | `diagnostics` |
| Runtime event logging                 | `logging`     |
| Dataset construction                  | `data`        |

No downstream package may import `reporting`: `models / tasks / evaluation / metrics / figures / analysis ↑ reporting ↑ notebooks / CLI / documentation`.

## 2. Upstream integration

| Upstream package | Contract types consumed                        | Purpose                            | Status |
| ---------------- | ---------------------------------------------- | ---------------------------------- | ------ |
| `evaluation`     | `EvaluationResult`, `ArtifactRef`              | Primary evidence source            | R      |
| `analysis`       | `AnalysisResult`, `AnalysisPayload`            | Scientific interpretation evidence | R      |
| `figures`        | `FigureResult`, `FigureArtifact`               | Rendered figure resources          | R      |
| `diagnostics`    | `DiagnosticReport`, `DiagnosticFinding`        | Model-health evidence              | P      |
| `contracts`      | `ArtifactKey`, `ArtifactRef`, `Provenance`     | Artifact identity and provenance   | R      |
| `traces`         | (none — reporting does not consume raw traces) | —                                  | —      |

See also: [contracts.md §4.3](contracts.md) for consumer-owned protocol rules; [analysis.md](analysis.md) for `AnalysisResult` schema; [figures.md](figures.md) for `FigureArtifact`; [evaluation.md](evaluation.md) for `EvaluationResult`; [diagnostics.md](diagnostics.md) for `DiagnosticReport`.

## 3. Lifecycle

`ReportDefinition + ReportRequest + ReportSource → build_report() → ReportResult (renderer-neutral) → serialize (Data Package) / render (HTML/Markdown/PDF)`

## 4. Domain model

- **`ReportDefinition`**: name, version, task families, model families, sections (`SectionSpec` variants: `NarrativeSpec`, `MetricSummarySpec`, `MetricTableSpec`, `FigureGallerySpec`, `ProvenanceSpec`).
- **`ReportRequest`**: report name, `EvaluationSourceRef(uri, regime)`, parameter overrides, section selection. Serialisable.
- **`ReportSource`** (protocol): abstracts evidence retrieval. Implementations: `LocalReportSource`, `MlflowReportSource`, `InMemoryReportSource`.
- **`ReportContext`**: normalised, source-independent inputs (`EvaluationRecord`, `MetricTable`, `CaseRecord`, `FigureResource`, `ArtifactResource`, source provenance, warnings).
- **`ReportResult`**: renderer-neutral, immutable, deterministic (no wall-clock timestamps). Contains `sections: tuple[ResolvedSection, ...]`, `provenance`, `warnings`.
- **`RenderedReport`**: render output with `RenderProvenance` (renderer identity, timing).
- **`ReportDataPackage`**: in-memory serialisable bundle (Frictionless Data Package). The composable unit for serialisation; does not contain a storage locator.
- **`ReportArtifact`**: persisted output reference (locator + format + digest). A lightweight handle to a report that has been written to storage. Distinct from `ReportDataPackage` — one is the data, the other is a pointer to it.

## 5. Package structure

```
ehp_sn/reporting/
├── definitions.py, requests.py, results.py, records.py
├── validation.py, registry.py, builders.py, sources.py
├── serializers.py (Frictionless Data Package)
├── renderers/, publishers/, service.py, errors.py
```

## 6. Design contract

> Reporting is the terminal composition layer. It consumes typed results from evaluation, figures, analysis, and diagnostics. It never executes models, computes metrics, or renders figures. `ReportResult` is the stable boundary between artifact extraction and notebook/document presentation.
