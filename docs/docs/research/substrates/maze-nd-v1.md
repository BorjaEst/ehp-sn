---
title: Maze-ND v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Maze-ND v1

## Normative summary

`maze-nd/v1` defines reusable raster maze topologies extracted and normalized from an authoritative external source.

One record represents one distinct normalized source topology realization in preserved source orientation and conforming to `raster-topology/v1`.
Maze-ND defines source identity, topology extraction, normalization, deduplication, and lineage.
The shared `raster-topology/v1` contract defines how downstream tasks read and interpret the resulting topology.

Source starts, goals, solution paths, token labels, and source problem splits are not Maze-ND topology channels.

## Scope and boundary

### Owned semantics

Maze-ND defines:

- authoritative upstream source identity;
- immutable source revision and content fingerprint;
- source-row identity;
- source topology extraction policy;
- wall, passability, overlay, padding, and orientation interpretation;
- normalized topology identity;
- exact topology deduplication policy;
- source-row-to-topology lineage;
- source occurrence and source split summaries;
- malformed-source and connectivity handling;
- family-specific validation of source extraction and provenance.

## Canonical identity and conformance

| Property                | Required value       |
| ----------------------- | -------------------- |
| Artifact kind           | `substrate`          |
| Family                  | `maze-nd`            |
| Specification reference | `maze-nd/v1`         |
| Initial variant         | `source-topology`    |
| Shared logical schema   | `raster-topology/v1` |

A conforming release satisfies:

1. the generic framework `SubstrateArtifact` contract;
2. the complete `raster-topology/v1` contract;
3. every applicable Maze-ND-specific source, normalization, deduplication, and lineage requirement in this specification.

A concrete release uses:

```text
data/interim/maze-nd/source-topology/v<release>/
```

## Conceptual model

### Source problem row

A source problem row is one upstream record that may combine:

- wall/passability geometry;
- a start marker;
- one or more goal markers;
- a solution annotation;
- source split membership;
- source-specific metadata.

A source problem row is not necessarily one Maze-ND topology record.

### Extracted source topology

The extracted source topology is the wall/passability structure recovered from a source problem row after task-instance overlays are removed while preserving their cells' underlying topology meaning.

### Normalized topology

A normalized topology is the canonical Maze-ND raster representation after the declared normalization policy has:

- interpreted source values;
- removed task-instance overlays;
- removed only explicitly non-semantic source padding;
- preserved source orientation;
- produced the authoritative passability raster required by
  `raster-topology/v1`.

### Source topology identity

A source topology identity identifies the extracted topology in the upstream source domain before EHP-SN normalization and deduplication.

### Normalized topology identity

A normalized topology identity identifies exact normalized topology content under Maze-ND's orientation-preserving equality rule.

Several source problem rows, and potentially several extracted source topology identities, may map to one normalized topology record.

### Source occurrence

A source occurrence is one source problem row that maps to a normalized Maze-ND topology record.

Occurrences retain source split and source-instance provenance without becoming topology channels.

## Unit of record and variant model

### Unit of record

One Maze-ND record represents:

> one distinct normalized raster topology realization in preserved source
> orientation.

Source problem rows with identical normalized extent and cell-wise passability map to one topology record.

The record does not contain source start, goal, or solution channels.

### Record identity

Each record has one framework-managed stable `record_id`.

Its family-specific identity depends on:

- exact source revision and fingerprint;
- extraction schema;
- normalization policy;
- preserved orientation;
- normalized extent;
- normalized passability raster;
- shared topology canonicalization.

Record identity must not depend on the first encountered duplicate source row, source enumeration accidents, or physical storage order.

### Variant model

Maze-ND v1 initially defines one variant:

| Variant           | Meaning                                                                              |
| ----------------- | ------------------------------------------------------------------------------------ |
| `source-topology` | Unique normalized raster topologies extracted from the declared authoritative source |

Source revision, source subset, and normalization policy are identity-bearing configuration, not coordinate variants.

## Shared topology interface

Every Maze-ND record conforms to `raster-topology/v1`.

That shared contract owns the task-facing semantics of:

- `record_id`;
- `extent`;
- authoritative raster `passable` structure;
- compact state identity;
- canonical row-major state enumeration;
- `state_to_row_col` and derived `row_col_to_state`;
- canonical grid4 movement ordering;
- `next_state` and `movement_valid`;
- invalid-movement representation;
- directedness and unit-cost movement semantics;
- component count and connectedness capabilities;
- absence of topology self-loops;
- common topology validation.

Maze-ND must not redefine those semantics.

### Required shared capabilities

`topology_kind`, `coordinate_system`, `movement_kind`, `directed`, `edge_cost_kind`, and `stay_included` are fixed by `raster-topology/v1` itself (see that contract's § "Fixed schema parameters") and are not redeclared here.

Maze-ND v1 records declare or resolve the remaining, genuinely producer-varying capabilities:

```text
connected: record-dependent or release-guaranteed
component_count: derived from normalized passability
```

The shared schema treats normalized raster passability as the authoritative structural representation.
Compact states and movement tables are canonical derived views.

### Family-specific lineage extension

Source lineage is not part of the common topology payload.

Each topology record resolves a bounded lineage summary containing at least:

- normalized topology record ID;
- source occurrence count;
- set of source split labels represented by contributing occurrences;
- reference to the complete source-lineage mapping resource.

The complete many-to-one mapping is stored in a separate logical lineage resource rather than embedding an unbounded list of source-row references in every task-facing topology record.

## Source and normalization contract

### Authoritative source identity

A conforming release identifies the source through:

- stable logical source reference;
- immutable revision, snapshot, or equivalent source coordinate;
- verified content fingerprint;
- applicable source schema or extraction profile.

A mutable repository or dataset name alone is insufficient.

### Source field classification

The extraction profile must classify every source field or value as one of:

- topology-bearing;
- task-instance overlay;
- source metadata;
- source-format padding;
- invalid or unsupported.

The profile must explicitly identify:

- wall values;
- traversable values;
- start overlays;
- goal overlays;
- solution overlays;
- invalid or padded cells;
- any additional labels.

### Overlay removal

Start, goal, and solution overlays are removed before topology identity is computed.

Their cells retain the underlying passability established by the source schema.
Maze-ND does not infer passability merely from the existence of an overlay without a declared source rule.

### Orientation preservation

Maze-ND v1 preserves source orientation.

It does not canonicalize:

- rotations;
- reflections;
- transpositions;
- geometric symmetries.

Two source mazes related only by such a transformation remain distinct unless their normalized rasters are already identical in preserved orientation.

### Padding and extent normalization

The normalization policy may remove only padding explicitly declared non-semantic by the source schema.

The resulting `extent` is the authoritative semantic raster canvas after this normalization.
The policy must not silently crop meaningful border walls or change source coordinates without declaring that transformation.

### Exact topology equality

Two selected source problem rows map to the same Maze-ND topology record if and only if, after the same extraction and normalization policy:

- their normalized extents are equal; and
- their cell-wise passability rasters are identical in preserved orientation.

Compact-state arrays and movement tables are derived from this authoritative raster and do not define a second equality relation.

### Selection and deduplication order

The release must declare one selection policy that fixes whether source rows are:

1. selected first and then normalized/deduplicated; or
2. fully normalized/deduplicated first and then unique topologies are selected.

These policies induce different topology distributions and are not interchangeable.

The initial release must record the selected policy explicitly.
Source-row frequency must not be lost without preserving occurrence counts and lineage.

### Connectivity and malformed-source policy

Maze-ND does not silently select the largest component or delete source-passable cells.

The source import policy must declare one of:

| Policy     | Meaning                                                                                    |
| ---------- | ------------------------------------------------------------------------------------------ |
| `preserve` | Preserve disconnected normalized topology and expose its component capabilities            |
| `reject`   | Reject source rows whose normalized topology violates a declared connectedness requirement |

The correct initial policy depends on the verified source revision.

Malformed or unsupported source rows fail or are rejected under an explicit policy and diagnostic.
They are not silently repaired.

### Source problem preservation

Removing source-instance fields from Maze-ND does not permit their loss.

Exact source starts, goals, solutions, source split labels, and other problem-instance annotations remain available through:

- immutable external or raw source material;
- complete source-lineage mapping;
- a MazeHard source-reproduction pipeline;
- a future normalized source-instance artifact only if multiple consumers justify that abstraction.

Maze-ND itself does not create a separate source-instance family by default.

### Verified, inherited, assumed, and observed claims

Every source-related claim must be classified as:

- guaranteed by authoritative source documentation;
- independently verified by EHP-SN;
- assumed for import;
- descriptively observed in the selected source revision.

Only supported topology properties may become hard Maze-ND invariants.
Solution optimality and source goal semantics are outside Maze-ND topology conformance.

## Split semantics

Maze-ND v1 does not impose intrinsic `train`, `validation`, or `test` splits on normalized topology records.

Source split labels belong to source problem occurrences.
They may not define a topology-level partition because one normalized topology can occur in several source splits through different problem rows.

A conforming release must:

- preserve each occurrence's source split through lineage;
- report source split membership sets per normalized topology;
- report topology overlap across source splits;
- avoid presenting source row splits as topology splits;
- leave experimental topology split construction to task corpus specifications.

A source-reproduction corpus may preserve original source-instance splits without turning those splits into Maze-ND topology semantics.

## Configuration and family-specific identity inputs

### Semantic configuration

| Key                             | Type                     | Requiredness | Meaning                                                         | Family-specific build input |
| ------------------------------- | ------------------------ | ------------ | --------------------------------------------------------------- | --------------------------: |
| `substrate.variant`             | enum                     | required     | `source-topology`                                               |                         Yes |
| `source.reference`              | immutable reference      | required     | Exact upstream dataset revision                                 |                         Yes |
| `source.fingerprint`            | digest                   | required     | Verified source content identity                                |                         Yes |
| `source.schema`                 | schema/profile reference | required     | Source field interpretation                                     |                         Yes |
| `source.selection_policy`       | policy reference         | required     | Source-row or unique-topology selection semantics               |                         Yes |
| `normalization.policy`          | policy reference         | required     | Extraction, overlay, padding, extent, and orientation semantics |                         Yes |
| `topology.connectivity_policy`  | enum                     | required     | `preserve` or `reject`                                          |                         Yes |
| `topology.deduplication_policy` | fixed policy reference   | required     | Exact normalized raster equality in preserved orientation       |                         Yes |

A deterministic source subset may additionally require a selection count and seed.
Those values are identity-bearing.

### Operational configuration

External cache paths, download concurrency, worker count, logging, progress reporting, and staging locations are operational and must not alter normalized topology content.

### Family-specific identity inputs

Maze-ND contributes:

- specification reference;
- variant;
- shared logical schema reference;
- exact source reference and fingerprint;
- extraction schema;
- selection policy and any deterministic sampling inputs;
- normalization and orientation policy;
- connectivity policy;
- exact deduplication policy;
- source-lineage construction policy;
- shared topology canonicalization.

The framework remains authoritative for build-input identity, artifact fingerprints, release reuse, conflicts, staging, and publication.

## Framework contract instantiation

| Framework property             | Maze-ND requirement                                                                                                   |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| Specification reference        | Exactly `maze-nd/v1`                                                                                                  |
| Family                         | Exactly `maze-nd`                                                                                                     |
| Variant                        | `source-topology`                                                                                                     |
| Shared schema                  | `raster-topology/v1`                                                                                                  |
| Required topology capabilities | Raster, row-column, grid4, undirected, unit-cost                                                                      |
| Required family descriptors    | Source identity, extraction schema, selection policy, normalization policy, connectivity policy, deduplication policy |
| Required lineage               | Complete source-occurrence-to-topology mapping resource                                                               |
| Bounded record summary         | Source occurrence count and source split membership set                                                               |
| Intrinsic experimental splits  | None                                                                                                                  |

The common topology record must remain bounded and independently usable.
Full source occurrence mappings belong in a separate logical lineage resource.

## Family-specific invariants and validation

Common raster, compact-state, movement, and capability invariants are owned by `raster-topology/v1` and are not duplicated here.

### MN-REC-001 — Source lineage resolution

Every topology record resolves to one or more immutable source problem occurrences in the declared source revision.

### MN-REC-002 — Overlay exclusion

No public Maze-ND topology channel contains source start, goal, or solution semantics.

### MN-REC-003 — Extraction conformance

The authoritative passability raster is exactly the result of the declared source extraction and normalization policy applied to every contributing occurrence.

### MN-REC-004 — Orientation preservation

The normalized topology applies no undeclared rotation, reflection, transposition, or coordinate reorientation.

### MN-REC-005 — Connectivity-policy conformance

Each record conforms to the declared `preserve` or `reject` connectivity policy.
No source-passable component is silently discarded.

### MN-REC-006 — Lineage summary consistency

The bounded occurrence count and source split membership set agree with the complete lineage resource.

### MN-ART-001 — Record identity uniqueness

Every normalized topology `record_id` is unique within the artifact.

### MN-ART-002 — Exact topology uniqueness

No two records have the same normalized extent and cell-wise passability raster in preserved source orientation.

### MN-ART-003 — Duplicate occurrence aggregation

All selected source occurrences yielding the same normalized topology are represented by one topology record and the complete many-to-one lineage mapping.

### MN-ART-004 — Source consistency

Every source occurrence belongs to the declared immutable source revision and is interpreted under the declared source schema.

### MN-ART-005 — Source split overlap reporting

The artifact reports every normalized topology whose source occurrences span more than one source split.

### MN-ART-006 — No intrinsic topology split claim

The artifact does not label topology records as `train`, `validation`, or `test`.

### MN-ART-007 — Selection-policy conformance

The imported topology collection and occurrence distribution agree with the declared selection-before-deduplication or deduplication-before-selection policy.

### Validation requirements

Full validation operates on committed topology, source identity, and lineage resources.

Diagnostics should identify:

- artifact coordinate;
- topology record ID;
- source occurrence ID;
- source revision;
- violated invariant;
- affected extraction or normalization rule;
- observed and expected values.

Validation of source solution optimality, source goal semantics, or task-case correctness is outside Maze-ND topology validation.

## Compatibility and downstream-use boundary

### New release under `maze-nd/v1`

A new release may change:

- source revision;
- selected source subset;
- selection policy parameters;
- normalized topology collection;
- occurrence counts and lineage;
- connectivity policy;
- individual topology record identities.

It remains `maze-nd/v1` when one record still means one unique normalized source topology and all shared topology and source-lineage semantics remain compatible.

### New specification version

A new specification version is required for incompatible changes to:

- inclusion of starts, goals, or solutions in the topology record;
- record meaning;
- topology equality;
- orientation-preservation semantics;
- rotation or reflection canonicalization;
- passability interpretation;
- silent component deletion;
- source-lineage meaning;
- intrinsic topology split semantics;
- compatibility with `raster-topology/v1`.

### Downstream use

Tasks and ObsField consume Maze-ND through `raster-topology/v1` and must not require family-specific source metadata for ordinary traversal.

Family identity and source revision may remain explicit experimental selection criteria.

MazeHard may generate starts, goals, and canonical solutions over a Maze-ND topology.
A source-reproduction corpus may instead resolve the original source problem occurrence through lineage.

## Open issues

- [`raster-topology/v1`](../../framework/contracts/topology/raster-topology-v1.md) now exists but remains `draft`; Maze-ND cannot move from `draft` to `specified` until that shared schema does.
- The authoritative source revision, fingerprint, and extraction profile must be verified and fixed for the initial release.
- The selected source revision must be inspected to choose the initial `preserve` or `reject` connectivity policy.
- The first release must decide and document whether selection occurs before or after topology deduplication.

## Related specifications

- [`Substrates`](./index.md)
- [`raster-topology/v1`](../../framework/contracts/topology/raster-topology-v1.md)
- [`Data artifacts`](../../framework/data-artifacts.md)
- [`Manifests`](../../framework/manifests.md)
- [`Identity`](../../framework/identity.md)
- [`Digests`](../../framework/digests.md)
- [`Provenance`](../../framework/provenance.md)
- [`References`](../../framework/references.md)
- [`Data CLI`](../../interfaces/cli/data.md)
- [`Data layout`](../../development/data-layout.md)
