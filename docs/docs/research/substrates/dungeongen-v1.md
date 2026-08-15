---
title: DungeonGen v1
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# DungeonGen v1

## Normative summary

`dungeongen/v1` defines reusable, procedurally generated irregular raster topologies for downstream task-corpus construction.

One record represents one accepted and normalized procedural topology realization conforming to `raster-topology/v1`.
DungeonGen defines how such a topology is generated, converted, accepted, and provenanced.
The shared `raster-topology/v1` contract defines how tasks read and interpret the resulting topology.

DungeonGen does not contain observation assignments, starts, goals, paths, solutions, trajectories, targets, rewards, task splits, or model-facing encodings.

## Scope and boundary

### Owned semantics

DungeonGen defines:

- procedural generator identity and immutable revision;
- generator protocol and profile;
- raw-generator-to-raster conversion policy;
- wall, room, corridor, passage, and door interpretation where applicable;
- candidate component-selection policy;
- topology acceptance criteria;
- retry ordering, attempt limits, and exhaustion behavior;
- record-addressable topology-generation randomness;
- accepted-attempt lineage;
- optional reusable generator-derived region semantics;
- duplicate-topology policy;
- family-specific validation of generation and conversion provenance.

## Canonical identity and conformance

| Property                | Required value       |
| ----------------------- | -------------------- |
| Artifact kind           | `substrate`          |
| Family                  | `dungeongen`         |
| Specification reference | `dungeongen/v1`      |
| Initial variant         | `general`            |
| Shared logical schema   | `raster-topology/v1` |

A conforming release satisfies:

1. the generic framework `SubstrateArtifact` contract;
2. the complete `raster-topology/v1` contract;
3. every applicable DungeonGen-specific requirement and invariant in this specification.

A concrete release uses:

```text
data/interim/dungeongen/<variant>/v<release>/
```

The release number is independent of the `v1` specification version.

## Conceptual model

### Raw candidate

A raw candidate is one output of the declared procedural generator before EHP-SN conversion, component selection, acceptance, and normalization.

A raw candidate may contain generator-specific geometry, internal padding, unstable room identifiers, door objects, corridor labels, or other implementation-specific state.
It is not yet a public DungeonGen record.

### Converted candidate

A converted candidate is the raster passability interpretation obtained from a raw candidate under the declared conversion policy.

The conversion policy must define how all generator-specific spatial concepts map to passable or non-passable raster positions and which source padding is non-semantic.

### Accepted topology realization

An accepted topology realization is the normalized raster topology remaining after:

1. raw generation;
2. conversion;
3. component selection;
4. canonical raster normalization;
5. acceptance validation.

The resulting record conforms to `raster-topology/v1`.

### Topology realization identity

A topology realization has an identity independent of any observation field or task case.
The same DungeonGen record may be referenced by multiple ObsField realizations and multiple processed corpora.

### Region annotation

A region annotation is an optional reusable categorical partition or labeling of valid topology states.

A region channel is permitted only when its meaning is defined by a stable region schema.
Generator-internal room numbers are not public substrate semantics merely because they exist during generation.

## Unit of record and variant model

### Unit of record

One record represents:

> one accepted procedural topology realization after generation, conversion,
> component selection, normalization, and acceptance.

A record does not include an observation realization.

Each record is independently addressable and independently reconstructable.
Record order in a resource has no scientific meaning.

### Record identity

Each record has one framework-managed stable `record_id`.

Family-specific inputs to one logical topology realization include:

- generator dependency and revision;
- generator protocol and profile;
- conversion policy;
- component-selection policy;
- acceptance policy;
- logical topology index;
- accepted retry-attempt index;
- deterministic randomness derivation.

The record ID must not depend on physical filename, container order, worker
assignment, or completion order.

### Variant model

DungeonGen v1 initially defines one variant:

| Variant   | Meaning                                                                                                             |
| --------- | ------------------------------------------------------------------------------------------------------------------- |
| `general` | Irregular raster topologies produced under explicitly declared generation, conversion, and acceptance configuration |

Size limits, density settings, room preferences, and downstream adapter bounds are configuration or presets under `general` unless they define a durable consumer-visible structural class.

Names derived from tasks or models, such as `routebind-30`, are not canonical DungeonGen variants.

## Shared topology interface

Every DungeonGen record conforms to `raster-topology/v1`.

That shared contract owns the task-facing semantics of:

- `record_id`;
- `extent`;
- authoritative raster `passable` structure;
- compact `state_id` domain;
- canonical row-major state enumeration over passable positions;
- `state_to_row_col` and derived `row_col_to_state`;
- canonical grid4 movement ordering;
- `next_state` and `movement_valid`;
- invalid-movement representation;
- directedness and unit-cost movement semantics;
- component count and connectedness capabilities;
- absence of topology self-loops;
- common raster-topology validation.

DungeonGen must not redefine those semantics.

### Required shared capabilities

`topology_kind`, `coordinate_system`, `movement_kind`, `directed`, `edge_cost_kind`, and `stay_included` are fixed by `raster-topology/v1` itself (see that contract's § "Fixed schema parameters") and are not redeclared here.

DungeonGen v1 records declare or satisfy the remaining, genuinely producer-varying capabilities:

```text
connected: true
component_count: 1
```

The shared schema treats normalized raster passability as the authoritative structural representation.
Compact states and movement tables are canonical derived views.

### Optional family extension: `region_id`

DungeonGen may provide `region_id[state_id]` as an optional extension.

When present:

- the region schema reference is declared;
- IDs are local categorical labels with no ordinal meaning;
- every assigned label has a defined reusable topology meaning;
- missing or unassigned semantics are explicit;
- corridor, door, and room treatment is specified;
- tasks may ignore the extension while still consuming the common topology.

## Generation and conversion contract

### Generator dependency

A conforming release identifies the exact procedural generator dependency by immutable revision, source digest, package artifact, or equivalent stable coordinate.

A mutable package name or local import path is insufficient.

The generator is a reference production dependency, not the public task-facing interface.

### Conversion policy

The conversion policy must define:

- generator cells or objects interpreted as walls;
- generator cells or objects interpreted as passable;
- door and passage interpretation;
- treatment of room and corridor boundaries;
- removal of non-semantic generator padding;
- coordinate orientation;
- component selection;
- recomputation of semantic extent after normalization;
- canonicalization required before shared topology derivation.

### Component-selection policy

DungeonGen v1 uses an explicit largest-component conversion policy unless a release declares another compatible policy.

Under the standard policy:

1. identify all four-connected passable components in the converted candidate;
2. select the component with greatest cell count;
3. when tied, select the component whose lexicographically smallest `(row, column)` coordinate is smallest;
4. discard all other passable components;
5. normalize the retained topology according to the conversion policy;
6. evaluate acceptance criteria on the retained normalized topology.

Component selection is an identity-bearing transformation, not hidden repair.

### Acceptance policy

The resolved acceptance policy defines every condition capable of rejecting a normalized candidate, including any:

- minimum or maximum state count;
- natural-extent bounds;
- required connectedness properties beyond the standard retained-component
  guarantee;
- room, corridor, bottleneck, or dead-end constraints;
- required region availability;
- topology-quality thresholds.

Approximate observed generator ranges are descriptive and must not be treated as hard requirements unless represented by exact acceptance fields.

### Retry and exhaustion

For logical topology index `i`, the generator evaluates a deterministic candidate stream indexed by retry attempt `a`.

The protocol must define:

- the first attempt index;
- deterministic attempt-state derivation;
- the maximum number of attempts;
- rejection diagnostics;
- exhaustion behavior;
- the accepted-attempt lineage recorded for the final record.

Exhaustion fails the logical realization explicitly.
The builder must not silently substitute another realization index.

### Record-addressable determinism

Candidate generation is derived from semantic inputs including:

```text
base seed
topology index
retry attempt index
generator protocol
generator profile
randomness role
```

The protocol must guarantee:

- increasing requested record count does not alter earlier logical topology
  indexes;
- worker count and scheduling do not alter output;
- retries for one topology do not consume randomness belonging to another;
- filesystem or container enumeration does not alter output;
- retry exhaustion is reproducible;
- fixed semantic inputs and dependency revision reproduce the same normalized
  topology.

The specification does not require a particular RNG library unless the referenced generator protocol requires one for exact reproducibility.

### Duplicate-topology policy

DungeonGen v1 does not impose universal topology uniqueness.

Each release declares one duplicate policy:

| Policy         | Meaning                                                                                                         |
| -------------- | --------------------------------------------------------------------------------------------------------------- |
| `allow`        | Independent generation outcomes remain separate records even when canonical topology content repeats            |
| `reject-exact` | A candidate duplicating an earlier canonical topology is rejected under the declared deterministic retry policy |

Duplicate detection and reporting are required under both policies.

The policy is identity-bearing because it changes the resulting record
collection and, for `reject-exact`, retry behavior.

## Configuration and family-specific identity inputs

### Semantic configuration

| Key                         | Type                                | Requiredness | Meaning                                 | Family-specific build input |
| --------------------------- | ----------------------------------- | ------------ | --------------------------------------- | --------------------------: |
| `substrate.variant`         | enum                                | required     | `general`                               |                         Yes |
| `generator.dependency`      | immutable reference                 | required     | Exact generator dependency and revision |                         Yes |
| `generator.protocol`        | specification reference             | required     | Record-addressable generation protocol  |                         Yes |
| `generator.profile`         | profile reference                   | required     | Generator parameter profile             |                         Yes |
| `conversion.policy`         | policy reference                    | required     | Raw-to-normalized topology semantics    |                         Yes |
| `acceptance.policy`         | policy reference or resolved object | required     | Candidate acceptance conditions         |                         Yes |
| `generation.attempt_budget` | positive integer                    | required     | Maximum attempts per logical topology   |                         Yes |
| `generation.seed`           | integer                             | required     | Base deterministic seed                 |                         Yes |
| `generation.record_count`   | non-negative integer                | required     | Number of topology records              |                         Yes |
| `topology.size_policy`      | schema-defined object               | required     | Allowed extent and state-count policy   |                         Yes |
| `topology.duplicate_policy` | enum                                | required     | `allow` or `reject-exact`               |                         Yes |
| `region.policy`             | policy reference                    | optional     | Optional reusable region derivation     |            Yes when present |

DungeonGen does not impose intrinsic `train`, `validation`, or `test` splits by default.
Task corpora own experimental split composition.

### Operational configuration

Worker count, logging, progress reporting, cache location, and temporary paths are operational and must not alter topology content.

### Family-specific identity inputs

DungeonGen contributes:

- specification reference;
- variant;
- shared logical schema reference;
- generator dependency and revision;
- generator protocol and profile;
- conversion and component-selection policy;
- acceptance policy;
- attempt budget and exhaustion semantics;
- size policy;
- duplicate policy;
- optional region policy;
- randomness derivation policy;
- base seed;
- requested record count.

The framework remains authoritative for build-input identity, artifact fingerprints, release reuse, conflicts, staging, and publication.

## Framework contract instantiation

| Framework property             | DungeonGen requirement                                                                          |
| ------------------------------ | ----------------------------------------------------------------------------------------------- |
| Specification reference        | Exactly `dungeongen/v1`                                                                         |
| Family                         | Exactly `dungeongen`                                                                            |
| Variant                        | `general`                                                                                       |
| Shared schema                  | `raster-topology/v1`                                                                            |
| Required topology capabilities | Raster, row-column, grid4, undirected, unit-cost, connected                                     |
| Required family descriptors    | Generator dependency, protocol, profile, conversion policy, acceptance policy, duplicate policy |
| Required lineage               | Logical topology index and accepted retry attempt                                               |
| Optional extension             | Declared `region_id` schema                                                                     |
| Intrinsic experimental splits  | None by default                                                                                 |

Generator profile and conversion policy should be artifact-level descriptors when homogeneous across the release.
Per-record materialization is required only for values that actually vary between records.

Accepted-attempt identity belongs to record lineage or validation metadata, not the common topology payload.

## Family-specific invariants and validation

Common raster, compact-state, movement, and capability invariants are owned by `raster-topology/v1` and are not duplicated here.

### DG-REC-001 — Declared production identity

Every record resolves to the artifact's declared generator dependency, protocol, profile, conversion policy, acceptance policy, and randomness
policy.

### DG-REC-002 — Canonical component selection

The committed passability raster is exactly the normalized component selected from the accepted raw candidate by the declared component-selection policy.

### DG-REC-003 — Acceptance conformance

The accepted normalized topology satisfies every configured acceptance requirement.

### DG-REC-004 — Retry lineage

The accepted-attempt index lies within the configured attempt budget.
Every prior attempt for the same logical topology index is rejected under the same
declared policy.

### DG-REC-005 — Region extension validity

When `region_id` is present, it conforms to the declared region schema.
When no stable region semantics are declared, the channel is absent.

### DG-REC-006 — Observation exclusion

No public DungeonGen record channel assigns an environmental observation to a state.

### DG-ART-001 — Record identity uniqueness

Every `record_id` is unique within the artifact.

### DG-ART-002 — Requested record count

The artifact contains exactly the configured number of topology records.

### DG-ART-003 — Duplicate-policy conformance

The record collection and retry history conform to the declared duplicate policy.
Exact duplicates are reported under `allow` and absent under `reject-exact`.

### DG-ART-004 — Prefix and parallel stability

Reproduction checks establish that record content for existing logical indexes is stable under increased requested counts and different worker counts.

### Validation requirements

Full validation operates on committed topology resources and production lineage, not only on generator runtime objects.

Diagnostics should identify:

- artifact coordinate;
- record ID;
- logical topology index;
- accepted retry attempt;
- violated invariant;
- affected conversion, acceptance, or region rule;
- observed and expected values.

## Compatibility and downstream-use boundary

### New release under `dungeongen/v1`

A new release may change:

- seed;
- record count;
- generator profile values;
- accepted topologies;
- extent or state-count policy values;
- acceptance thresholds;
- duplicate policy;
- optional region configuration.

It remains `dungeongen/v1` when one record still means one normalized procedural raster topology and all shared topology semantics remain compatible.

### New specification version

A new specification version is required for incompatible changes to:

- record meaning;
- generator-to-topology ownership boundary;
- component-selection meaning;
- inclusion of observations or task instances;
- region semantics made newly mandatory or reinterpreted;
- family-specific production lineage meaning;
- compatibility with `raster-topology/v1`.

### Downstream use

Tasks and ObsField consume DungeonGen through `raster-topology/v1` and must not require family-specific metadata for ordinary traversal.

Family identity may still be used as an explicit experimental selection criterion.

Downstream consumers must not treat accepted-attempt indexes, generator seeds, or generator-internal labels as model inputs or topology features.

## Open issues

- Stable reusable room, corridor, and door region semantics remain unverified; `region_id` therefore remains optional.
- Exact generator dependency and reference protocol must be fixed against the implementation selected for the first release.

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
