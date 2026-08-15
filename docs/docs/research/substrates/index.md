---
title: Substrates
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Substrates

## Purpose

This section contains the research-owned specifications for substrate families implemented by `ehp_research`.

A substrate represents reusable, task-neutral domain structure from which one or more task corpora may be derived:

```text
substrate = reusable world, structure, or preserved source facts
task corpus = task-specific cases, episodes, inputs, and targets
```

Concrete substrate specifications define domain semantics.
Generic artifact identity, manifests, resources, lifecycle, validation mechanics, publication, and common I/O remain owned by the framework specifications.

## Documentation boundary

Concrete substrate specifications define:

- the scientific or domain meaning of a substrate family;
- the unit of record;
- the family and specification identity;
- stable consumer-visible variants;
- semantic channels and logical record schemas;
- topology, observation, source, and split semantics where applicable;
- generation or conversion protocol;
- family-specific configuration and identity inputs;
- testable domain invariants and validation requirements;
- downstream visibility and use restrictions;
- compatibility and evolution rules.

They do not redefine:

- generic `DataArtifact` or `SubstrateArtifact` semantics;
- coordinate immutability or release ordering;
- generic build-input identity or artifact fingerprints;
- generic manifest and resource-descriptor schemas;
- staging, commitment, reuse, conflict, or atomic publication;
- generic validation modes;
- CLI option spelling or configuration precedence;
- repository-local cleanup and staging paths.

## Terminology

### Family

A family is the stable namespace for one substrate concept, such as `obsfield`, `dungeongen`, or `dagflow`.

### Specification version

A specification version identifies one semantic contract for a family:

```text
<family>/v<N>
```

For example, `obsfield/v1` denotes the first ObsField semantic contract.
It is not a concrete data release.

### Variant

A variant is a stable, consumer-visible subdivision of a family represented in the artifact coordinate:

```text
data/interim/<family>/<variant>/v<N>/
```

A variant is not automatically equivalent to a package configuration preset.
A concrete family specification must define their relationship.

### Preset

A preset is a package-owned named configuration.
Presets are configuration conveniences unless a family specification explicitly assigns the same name and semantics to a coordinate variant.

### Release

A release is one committed substrate artifact.
Its final `v<N>` component is a monotonically increasing release number local to one `(family, variant)` pair.
Release semantics are defined by the framework.

### Record

A record is one independently addressable domain instance contained in a substrate artifact.
Each family specification defines its record boundary and stable identifier semantics.

### Channel

A channel is a named semantic component of a record or artifact.
Channel existence and meaning are independent of physical serialization.

### Logical record schema

A logical record schema defines the fields and channels that jointly form a valid record.
It is distinct from a physical serialization schema.

### Logical resource

A logical resource is a manifest-declared resource through which records, channels, indexes, or split descriptors are resolved.
The framework defines resource mechanics; family specifications define required semantic content.

## Generic substrate boundary

A substrate may contain reusable information such as:

- topology or connectivity;
- geometry and valid-state declarations;
- environment-level observations;
- regions or landmarks;
- source-preserved annotations;
- intrinsic split membership.

A substrate must not define task-specific protocol such as:

- task queries;
- task-generated trajectories or episodes;
- supervision targets or rewards;
- model tokenization or batch structures;
- task-specific evaluation metrics.

Whether a source field is task-neutral is a concrete family decision.
Calling a field an annotation does not by itself establish substrate ownership.

## Conformance of a substrate specification

A document conforms to this section when it:

1. uses the canonical family/specification/variant/release terminology;
2. explicitly defines its owned and excluded semantics;
3. defines one unambiguous unit of record;
4. defines all required channels and cross-channel constraints;
5. distinguishes semantic contracts from physical serialization;
6. defines testable family-specific invariants;
7. identifies unresolved interoperability decisions while its status is `draft`;
8. applies, rather than duplicates, the generic framework contracts.

A specification must not be marked `specified` while unresolved decisions can change record identity, required channels, consumer interpretation, split semantics, or validation outcomes.

## Required and conditional sections

Every concrete substrate specification must contain:

- normative summary;
- scope and boundary;
- canonical identity and conformance;
- conceptual model;
- unit of record;
- channels and logical record schema;
- source or generation contract;
- configuration and family-specific identity inputs;
- invariants and validation;
- compatibility and downstream-use boundary;
- related specifications.

The following sections are conditional:

- variant model;
- topology or graph semantics;
- observation semantics;
- intrinsic splits;
- randomness and determinism;
- family-specific index fields;
- privileged or validation-only channels;
- open issues.

## Evidence requirements

For externally sourced substrates, specifications must distinguish:

- properties guaranteed by the upstream source contract;
- properties verified by EHP-SN during conversion;
- assumptions introduced by EHP-SN;
- descriptive observations that are not normative guarantees.

Unsupported upstream claims must not be promoted to normative substrate semantics.

## Registered and proposed specifications

| Family       | Specification                       | Classification                                                         | Component maturity |
| ------------ | ----------------------------------- | ---------------------------------------------------------------------- | ------------------ |
| `obsfield`   | [`obsfield/v1`](obsfield-v1.md)     | Procedural spatial substrate                                           | Planned            |
| `dungeongen` | [`dungeongen/v1`](dungeongen-v1.md) | Procedural spatial substrate                                           | Planned            |
| `dagflow`    | [`dagflow/v1`](dagflow-v1.md)       | Procedural directed-graph substrate                                    | Specified          |
| `maze-nd`    | [`maze-nd/v1`](maze-nd-v1.md)       | Imported source-instance artifact; substrate classification unresolved | Planned            |

`Component maturity` reflects the component as a whole — specification, implementation, and validation evidence together — following the `planned → specified → implemented → validated → reference` progression.
It is derived from each specification's own `document_status` (linked above) plus implementation/validation state, not restated independently.

The table registers specification work, not concrete artifact releases.

## Shared logical record schemas

A logical record schema may be shared by more than one family.
Shared schemas are producer-agnostic: they define the object, its authoritative representation, and a capability vocabulary for compatibility, but not which family produces or consumes them.
They are `ehp_sn`-owned, registered in the framework's [`contracts/`](../../framework/contracts/index.md) section, not defined here.

## Related specifications

Framework contracts:

- [`Data artifacts`](../../framework/data-artifacts.md)
- [`Manifests`](../../framework/manifests.md)
- [`Identity`](../../framework/identity.md)
- [`Digests`](../../framework/digests.md)
- [`Provenance`](../../framework/provenance.md)
- [`References`](../../framework/references.md)

Other ownership areas:

- [`Contracts`](../../framework/contracts/index.md)
- [`Corpora`](../../framework/corpora.md)
- [`Data CLI`](../../interfaces/cli/data.md)
- [`Data layout`](../../development/data-layout.md)
