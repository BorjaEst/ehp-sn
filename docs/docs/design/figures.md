# Figures Design

<!-- canonical_package: ehp_sn  authority: canonical  status: draft -->

> `ehp_sn.figures` — deterministic visualization layer over already-computed analysis data.

---

## Normative summary

| Rule                  | Value                                                                                                                                                               |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Figure definitions, views, builders, renderers; `FigureId`, `FigureStyle`, `FigureResult`; visual encoding; export                                                  |
| **Must not own**      | Scientific computation; trace loading; artifact paths; MLflow clients; GPU tensors                                                                                  |
| **Public API**        | `render`, `REGISTRY`, `FigureContext`, `FigureSpec`, `FigureResult`, `FigureStyle`, `list_figures`                                                                  |
| **Allowed imports**   | `analysis` (R: contracts/view models), `contracts` (R), `matplotlib`; **P:** `traces` (`TraceStoreReader` protocol)                                                 |
| **Forbidden imports** | `traces.trace_tree`, `evaluation`, `training`, `lightning`, `tasks`, `models`                                                                                       |
| **Layer**             | L6 — Post-Processing & Presentation                                                                                                                                 |
| **Key invariant**     | Figures convert typed analysis results into renderable Matplotlib figures without computing science, loading raw traces, or importing evaluation/training internals |

---

## 1. Data flow

```
TraceStoreReader / evaluation artifacts → analysis extraction → typed analysis result (analysis/contracts/)
    → figure view builder (select, sort, label, derive extents)
    → FigureView (immutable dataclass, CPU-resident numpy)
    → figures renderer (create axes, apply colormaps, legends)
    → FigureResult { figure, axes, provenance }
    → save / MLflow / notebook
```

**Core rule:** `evaluation` determines what happened; `analysis` computes derived representations; `figures` decides how those are visualized.

**Three distinct objects:** `raw trace (TraceTree, artifact files) ≠ analysis result (scientific product: computed metrics, provenances) ≠ figure view (presentation contract: selected samples, labels, extents)`. This separation avoids trace-schema coupling, prevents scientific computation from leaking into visualization, makes figures testable in isolation, and allows the same analysis results to feed notebooks, tables, reports, and multiple visualizations.

## 2. Responsibility boundaries

- **`analysis`** owns: rate maps, gridness scores, place-field statistics, RSA, PCA/UMAP, confidence intervals. May produce scientifically defined rankings.
- **`figures.builders`** owns: selecting already-scored units, sorting for display, panel ordering, labels, legend entries, display extents, clipping for contrast. **Must NOT:** compute gridness, place-field quality, RSA, or any other scientific quantity; load raw traces or access artifact paths.
- **`figures.views`** owns: immutable dataclass with pre-computed values, labels, masks, coordinates, color annotations. **Must NOT:** contain lazy loaders, file paths, TraceTree objects, GPU tensors.
- **`figures.renderers`** owns: creating Figure/Axes, applying colormaps, legends, colorbars, titles. **Must NOT:** compute science, save files, or modify global Matplotlib state.
- **`figures.export`** owns: saving to PNG/SVG/PDF.

## 3. Core contracts

- **`FigureId`**: validated string identifier (`^[a-z][a-z0-9_]*$`). Not an enum (external experiments may register figures).
- **`FigureStyle`**: `profile: "paper" | "notebook" | "presentation"`. Applied locally via `matplotlib.rc_context()` — no global state mutation.
- **`FigureDefinition[ViewT]`**: `(id, label, build, render, tags)` — generic over view type.
- **`FigureResult`**: `{ figure: Figure, axes: dict[str, Axes], provenance: FigureProvenance }`.

## 4. Package structure (domain-oriented)

```
ehp_sn/figures/
├── api.py, contracts.py, registry.py, styles.py, export.py, diagnostics.py
├── spatial/    (arena, tem)
├── representations/ (tem, hrm)
├── predictions/ (tem, mazehard)
└── deliberation/ (halting, routebind)
```

Each domain module contains its view, builder, and renderer together.

## 5. Design contract

> Figures converts typed analysis results into renderable Matplotlib figures. It never computes science, loads raw traces, or imports evaluation/training internals. All inputs are CPU-resident numpy arrays. Style is applied locally; no global state mutation.
