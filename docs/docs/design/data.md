# Data Subsystem

<!-- canonical_package: ehp_sn  authority: canonical  status: draft -->

> `ehp_sn.data` — producing, identifying, validating, storing, resolving, and reading canonical datasets.

---

## Normative summary

| Rule                  | Value                                                                                                                                    |
| --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **Owns**              | Dataset identity (`DatasetRef`, `DatasetLocation`); manifests; indexes; build pipeline; storage backends; sampling; collation; loading   |
| **Must not own**      | Model architecture; task semantics; training loops; evaluation orchestration; metric computation                                         |
| **Public API**        | `DatasetRef`, `DatasetSelection`, `DatasetLocation`, `open_dataset`, `ProcessedDataset`, `DataLoaderConfig`, `build_data_loader`         |
| **Allowed imports**   | `contracts`, `types`                                                                                                                     |
| **Forbidden imports** | `models`, `controllers`, `objectives`, `training`, `lightning`, `evaluation`, `adapters`, `rollouts`                                     |
| **Layer**             | L1 — Domain Primitives                                                                                                                   |
| **Key invariant**     | Data owns dataset identity, storage, and loading up to the task/model adapter boundary; build plane produces immutable versioned corpora |

---

## 1. Two-plane architecture

```
Build plane:   sources → substrates → layouts → task corpora → publish
Runtime plane: resolve → open → sample → collate → batch → adapter (boundary)
```

**Ownership boundary:** `ehp_sn.data` owns data semantics up to where task/model-specific interpretation begins. The Lightning adapter lives in `lightning/datamodule.py`, **not** inside `data/`, enforcing `lightning → data` dependency direction.

## 2. Package layout

```
ehp_sn/data/
├── __init__.py
├── references.py         # DatasetRef, DatasetLocation, resolve_dataset
├── manifests.py          # DatasetManifest, read/write
├── indexes.py            # DatasetIndexEntry, read/write
├── lineage.py            # validate_shared_parent
├── errors.py             # DataError taxonomy
├── datasets.py           # ProcessedDataset, open_dataset
├── sampling.py           # Sampler, ShuffledEpisodeSource
├── collators.py          # Collator protocol, default, padded, recurrent
├── loaders.py            # DataLoaderConfig, build_data_loader
├── transforms.py         # SampleTransform, RandomDihedral, Compose
├── lifecycle/            # Transactional build pipeline (staging, publishing, validation)
├── source/               # External/procedural source descriptions
├── substrate/            # Shared structural representations (grid2d, dungeongen, maze_nd, dagflow, openfield)
├── layout/               # Intermediate layout contracts (spatial, relational)
└── validation/           # Schema conformance
```

Split into subpackages only when multiple implementations, materially different dependencies, or a stable public abstraction exists. Otherwise prefer flat modules.

## 3. Identity layer

- **`DatasetRef(kind, family, name, version)`**: logical reference to a versioned root. No split included.
- **`DatasetSelection(dataset, split)`**: selects a split within a resolved root.
- **`DatasetLocation(ref, root)`**: resolved filesystem path. No metadata loaded yet.
- **`resolve_dataset(ref, *, data_root) → DatasetLocation`**: stat-only, cheap.

## 4. Manifest and index

**`DatasetManifest`**: schema_version, record_count, splits, content_digest, input_fingerprint, generator_version, parent_refs. Authoritative declaration.

**`DatasetIndexEntry`**: id, split, record_offset, metadata. Enumerates; validator cross-checks.

## 5. Build plane (transactional)

```
begin staging → write records → write index.jsonl → write manifest.json → validate → atomically rename to v<N>/
```

Invariants: immutability (never modify after creation), transactional atomicity (`.building-v<N>/` temp dir), structural validation before rename.

## 6. Runtime plane

- **`ProcessedDataset`**: mmap-backed, opens manifest/index, verifies digest, decodes on `__getitem__`.
- **`Sampler`**: record-selection order. `SequentialSampler`, `RandomSampler`, `DistributedSampler`.
- **`ShuffledEpisodeSource`**: emits full records (episodes), not integer indices. For recurrent replay path.
- **`Collator`**: stacking, padding, mask construction, tensor conversion.
- **`SampleTransform`**: genuine data transformations (`RandomDihedral`, `Compose`). Never tokenize for specific models.

## 7. Three schema levels

| Level           | Owner               | Examples                                                |
| --------------- | ------------------- | ------------------------------------------------------- |
| Persistent data | `data`              | `DatasetManifest`, `DatasetIndexEntry`, `SpatialLayout` |
| Task contracts  | `tasks`             | `TaskSpec`, target encoding                             |
| Model contracts | `models`/`adapters` | `ModelInput`, `ModelOutput`                             |

## 8. Design contract

> Data owns dataset identity, storage, and loading up to the task/model adapter boundary. Build plane produces immutable versioned corpora transactionally. Runtime plane provides backend-agnostic access via `ProcessedDataset`. Lightning adapter lives in `lightning/datamodule.py`, not inside `data/`. Data provides `Source` implementations that satisfy the `Source` protocol defined in `rollouts/contracts.py`; data does not import rollouts.
