---
title: DungeonGen v1
authority: normative
document_status: specified
capability_status: specified
api_stability: provisional
---

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

A conforming DungeonGen substrate artifact declares these fixed identity values:

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

A concrete release uses the framework substrate release coordinate `dungeongen/<variant>/v<release>/`.
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

### First release dependency and protocol decision

The first executable release freezes one immutable external production dependency and one EHP-SN reference generation protocol.
These are the values that the implementation (`ehp_research/substrates/dungeongen/`) freezes and validates.

| Identity                             | Frozen value                                                                 |
| ------------------------------------ | ---------------------------------------------------------------------------- |
| Upstream repository                  | `https://github.com/benjcooley/dungeongen`                                   |
| Package                              | `dungeongen`                                                                 |
| Package version                      | `0.1.14`                                                                     |
| Upstream revision (exact Git commit) | `2d228f5d3f82ccaa4666b087942100e7800fb069` (message "v0.1.14")               |
| Dependency reference identity        | `git:benjcooley/dungeongen@2d228f5d3f82ccaa4666b087942100e7800fb069`         |
| Package-layer dependency             | `dungeongen==0.1.14` (verified to correspond to the frozen commit above)     |
| Supported upstream API               | `GenerationParams → DungeonGenerator(params).generate(seed=<int>) → Dungeon` |
| Reference generation protocol        | `dungeongen/generation/v1`                                                   |
| First generator profile              | `dungeongen/profile/general/v1`                                              |
| Conversion policy                    | `dungeongen:conversion/raster/v1`                                            |
| Component-selection policy           | `dungeongen:selection/largest-component/v1`                                  |
| Acceptance policy                    | `dungeongen:acceptance/size-and-connected/v1`                                |
| Duplicate policy (`general` variant) | `allow`                                                                      |
| Randomness role                      | `topology-candidate`                                                         |

The reference generation protocol (`dungeongen/generation/v1`) freezes:

- the exact upstream dependency identity above;
- the supported upstream API surface (`GenerationParams`, `DungeonGenerator`, `generate(seed=…)`) over the structured layout subsystem (`dungeongen.layout` only; the renderer / webview / drawing subsystems are **excluded**);
- the parameter interpretation — the full supported `GenerationParams` surface (below) and how each field maps to the upstream constructor, including the `size`/`room_count` mutual exclusion;
- candidate-seed derivation (below);
- the native output consumed (the `Dungeon` layout and its occupancy raster);
- the conversion-policy reference;
- failure behavior (a generator raise or an unexpected native structure is a controlled candidate rejection / build failure, never a silent substitution).

The protocol explicitly excludes webview, PNG/SVG rendering, water rendering, decorative graphics, and filesystem output.
The generator is a geometry source, not the public EHP topology representation.

### Supported generator parameter surface and EHP-owned defaults

The protocol's frozen contract is **how** generation works; the concrete scientific parameter values are **configuration** under the `general` variant (see [Variant model](#variant-model)).
The first profile `dungeongen/profile/general/v1` therefore does **not** freeze one dungeon distribution.
It defines the complete supported `GenerationParams` surface and the EHP-owned defaults that make any resolved configuration complete and explicit.

For every supported field the contract fixes the EHP field name, the exact upstream `GenerationParams` field, the type, the allowed domain, whether it is required, the EHP-owned default, the mutual-exclusion rule, and its identity-bearing status.
A configuration may set any subset of the scientific parameters; each omitted field resolves through its EHP-owned default, so the result is always a complete, explicit `GenerationParams` and no scientifically relevant parameter is ever silently inherited from a mutable upstream constructor default.

| `GenerationParams` field  | Type                  | Allowed values / domain                            | EHP-owned default | Mutual exclusion      |
| ------------------------- | --------------------- | -------------------------------------------------- | ----------------- | --------------------- |
| `archetype`               | enum                  | `classic/warren/temple/crypt/cavern/fortress/lair` | `classic`         | —                     |
| `size`                    | enum                  | `tiny/small/medium/large/xlarge`                   | `medium`          | excludes `room_count` |
| `room_count`              | `[min, max]` int pair | `1 <= min <= max`                                  | absent (`None`)   | excludes `size`       |
| `room_size_bias`          | float                 | `[-1.0, 1.0]`                                      | `0.0`             | —                     |
| `round_room_chance`       | float                 | `[0.0, 1.0]`                                       | `0.15`            | —                     |
| `hall_chance`             | float                 | `[0.0, 1.0]`                                       | `0.1`             | —                     |
| `density`                 | float                 | `[0.0, 1.0]`                                       | `0.5`             | —                     |
| `symmetry`                | enum                  | `none/bilateral/radial_2/radial_4/partial`         | `none`            | —                     |
| `symmetry_break`          | float                 | `[0.0, 1.0]`                                       | `0.2`             | —                     |
| `linearity`               | float                 | `[0.0, 1.0]`                                       | `0.3`             | —                     |
| `loop_factor`             | float                 | `[0.0, 1.0]`                                       | `0.3`             | —                     |
| `passage_width`           | positive integer      | `>= 1`                                             | `1`               | —                     |
| `winding`                 | float                 | `[0.0, 1.0]`                                       | `0.0`             | —                     |
| `extra_room_connections`  | float                 | `[0.0, 1.0]`                                       | `0.2`             | —                     |
| `extra_passage_junctions` | float                 | `[0.0, 1.0]`                                       | `0.15`            | —                     |
| `levels`                  | positive integer      | `>= 1`                                             | `1`               | —                     |
| `stair_frequency`         | float                 | `[0.0, 1.0]`                                       | `0.1`             | —                     |
| `water_enabled`           | boolean               | `true`/`false`                                     | `false`           | —                     |
| `water_threshold`         | float                 | `[-1.0, 1.0]`                                      | `0.15`            | —                     |

#### `size` vs `room_count` mutual exclusion

`size` and `room_count` are mutually exclusive and jointly optional:

- `size` set, `room_count` absent — **valid**.
  Room count derives from `size` inside the frozen upstream dependency.
  This derivation is upstream-owned (Correction 3); the EHP side does **not** reimplement a room-count formula.
- `room_count` set, `size` absent — **valid**.
  The explicit `room_count` pair overrides the size-derived count (`get_room_count_range` returns `room_count` when set).
  `size` resolves to its EHP-owned default for completeness, but has no effect because `room_count` wins.
- both set — **invalid** (conflict).
  Resolution rejects the configuration.
- both absent — **valid**; both fields resolve through EHP-owned defaults (`size=medium`, `room_count=None`).

An absent `room_count` (`None`) is the explicit "derive from `size`" state.
It is not identity-bearing beyond the `size` already encoded, whereas a set `room_count` is identity-bearing because it changes the generated output.

#### Named presets

Named reusable presets (for example `general-medium`, `general-large-dense`, `general-sparse`, `general-high-loop`) are **reusable parameter selections**, not variants, not protocols, and not separate framework capabilities.
A preset is a documented named selection of supported-parameter values; a concrete configuration may select a preset and override permitted fields.
After resolution, only the complete effective parameter set matters scientifically.

The fixed profile reference `dungeongen/profile/general/v1` identifies the supported parameter contract and the `general` variant's EHP-owned defaults.
Other named presets are reusable selections over that same surface; selecting a preset never changes the variant, the protocol, or the scientific identity of the concept, though the resolved parameter values (and therefore build-input identity) differ.

#### Resolution invariant

Every resolved configuration maps to a complete explicit `GenerationParams`.
The invariant is:

```text
user config
+ EHP-owned defaults
    ↓
complete resolved parameter declaration
    ↓
GenerationParams(...)
```

No scientifically relevant parameter is inherited accidentally from the external constructor.

### Candidate-seed derivation

The upstream generator accepts a seed; EHP-SN defines how that seed is obtained.
For logical topology index `i` and retry attempt `a` (see [Retry and exhaustion](#retry-and-exhaustion)), the candidate seed is a pure deterministic function:

```text
candidate_seed(i, a) = f(base_seed, protocol, profile, i, a, "topology-candidate")
```

where `f` is a stable hash (SHA-256) over the canonical concatenation of its arguments, reduced to a non-negative 31-bit integer accepted by the upstream generator's RNG.
The protocol, profile, and randomness role are fixed strings; `base_seed` is the configured `generation.seed`.

This scheme guarantees:

- same `(i, a)` → same candidate seed;
- a retry of index `i` (incrementing `a`) never consumes or alters the randomness of a different index, because each candidate seed depends only on its own `(i, a)`;
- increasing requested record count does not alter earlier indexes;
- worker count and scheduling do not alter output (the function is pure and parallel-safe);
- filesystem / container enumeration order does not alter output.

### Conversion policy (first release)

For the first release, the conversion policy `dungeongen:conversion/raster/v1` reads the structured native `Dungeon` layout **occupancy raster** produced during `generate()` — the spatial mapping from native cells to occupancy types that the layout generator populates from rooms, passages, doors, stairs, and exits.
It does **not** read rendered PNG/SVG and does not expose native room/door/object IDs as public content.

The policy asserts the following exact interpretation:

- **room interior cells** — the cells the occupancy raster classifies as `ROOM`; under the first conversion policy a rectangular room's bounded box is wholly `ROOM` (no separate interior/boundary distinction is emitted), and circular room discretization is already resolved by the generator into `ROOM` cells;
- **room boundary cells** — no separate `WALL` ring is emitted under the first conversion policy; the rectangular bounding box is passable `ROOM` up to its edges;
- **passage segments and width** — the cells the occupancy raster classifies as `PASSAGE` (including `passage_width` coverage);
- **doors, stairs, exits** — connection cells that the occupancy raster classifies as `ROOM` or `PASSAGE` (their DOOR / STAIRS / EXIT status is a _modifier_, not a separate passability type); they are passable because their base cell type is passable;
- **all other generator state** — `EMPTY`, `RESERVED`, `BLOCKED` (and any future `WALL`) cells are **non-passable**;
- **coordinate orientation** — native `x` maps to the raster column and native `y` maps to the raster row (`x` increases right, `y` increases down), so a native room `(x, y, width, height)` spans columns `[x, x+width)` and rows `[y, y+height)`;
- **unsupported native geometry** — unexpected cell kinds are treated as non-passable; a fully empty passable set is a controlled candidate failure.

The canonical result is a boolean passability raster over the native coordinate space.

### Semantic extent normalization (first release)

The native occupancy grid uses an implementation-specific canvas origin whose coordinates may be negative (observed ranges such as `x ∈ [-18, 17]`, `y ∈ [-18, 15]`).
Under `dungeongen:conversion/raster/v1` all cells lying strictly outside the tight bounding box of passable (`ROOM` / `PASSAGE`) cells are declared **non-semantic generator canvas margin**.
The canonical origin translation therefore:

1. recomputes the semantic extent as the tight bounding rectangle over passable cells;
2. translates that rectangle to origin `(0, 0)`;
3. emits the canonical row-major boolean passability over that extent.

Equal native geometry at different irrelevant canvas offsets therefore yields the same normalized topology because the offset is declared non-semantic.

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

For the first release the protocol fixes:

- **first attempt index** — `a = 0`;
- **attempt range** — `a ∈ [0, attempt_budget)`; the candidate seed for `(i, a)` is `candidate_seed(i, a)` from [Candidate-seed derivation](#candidate-seed-derivation);
- **retry driver** — a rejected candidate (under the resolved acceptance policy, and under the duplicate policy when it applies) increments `a` and derives a fresh candidate seed;
- **rejection diagnostics** — every rejection carries the named acceptance condition (or duplicate condition) that rejected the candidate, so each rejection is attributable to a configured condition;
- **exhaustion** — if `a` reaches `attempt_budget` without acceptance, the logical realization fails explicitly with an exhaustion error carrying the logical index, the attempt count, and the per-attempt rejection reasons; the builder never substitutes another realization index and never borrows a candidate seed from another index.

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

For the first release, the first executable profile (`general` variant via `independent-realizations`) uses **`allow`**: independent generation outcomes remain separate records even when canonical topology content (extent + cell-wise passability) repeats, and such repetition is detected and reported.
`allow` needs no cross-record retry machinery.

`reject-exact` remains a reusable but **not-yet-implemented** policy for the first release.
Because `reject-exact` requires prefix/parallel deterministic retry against earlier records, a configuration that declares it is rejected cleanly by the resolver until a release implements and registers it; it must not be silently downgraded and materialized as `allow`.

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

- Stable reusable room, corridor, and door region semantics remain unverified; `region_id` therefore remains optional (and is **absent** by default in the first release, per the "Optional family extension" requirement).
- `reject-exact` duplicate handling is defined but not implemented for the first release; the first executable profile uses `allow`, and a config declaring `reject-exact` is rejected cleanly until it is implemented and registered.

are now fixed (see [First release dependency and protocol decision](#first-release-dependency-and-protocol-decision)).

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
