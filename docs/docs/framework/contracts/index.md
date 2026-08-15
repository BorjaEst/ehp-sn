---
title: Contracts
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Contracts

This section contains `ehp_sn`-owned standard scientific data contracts: producer-agnostic, consumer-agnostic logical record schemas for reusable structures such as spatial domains, topology, and relational graphs.

```text
                  ehp_sn — contracts/ (this section)
                              │
          ┌───────────────────┼───────────────────┬─────────────────────┐
          │                   │                   │                     │
       domains/          topology/           observations/          relations/
    ambient-domain     raster-topology     categorical-field       simple-digraph
          │                   │                   │                     │
   ───────┴───────────────────┴───────────────────┴─────────────────────┴───────
       ↑ producers                                consumers ↓

    substrate builders                         task builders
    (any conforming package)                    (any conforming package)
```

A contract defines one reusable semantic object, its authoritative representation and any canonical derived views, its logical schema, invariants, composition boundary, and any compatibility properties that consumers may constrain.
It does not define which package or family produces it, or which task consumes it — that coupling is deliberately absent, and no contract here imports or references a concrete `ehp_research` component.
`ehp_research → ehp_sn` is the only dependency direction.
No contract may normatively depend on, derive semantics from, or require a concrete `ehp_research` component; every contract must remain meaningful if `ehp_research` did not exist.

Compatibility currently reuses the [Resource requirements](../../interfaces/configuration/resource-requirements.md) schema-ID-plus-validator integration surface.
The intended producer-guarantee, consumer-requirement, property-scope, and deterministic matching model is deferred to the framework compatibility specification; see "Compatibility mechanism" below.

## Documentation boundary

A contract specification defines the object represented and its unit of record, authoritative content versus canonical derived views, the logical record schema independent of physical serialization, schema-fixed and derived compatibility properties, schema-level invariants, composition boundaries, and evolution rules.
It does not redefine generic artifact manifests, digests, lifecycle, publication, reuse, or generic record-envelope semantics.

## When a concept becomes a contract here

A schema belongs in this section when:

1. it represents a scientifically meaningful reusable abstraction;
2. independent producers or consumers can reasonably implement it;
3. standardizing it materially improves interoperability;
4. its semantics can be specified independently of any one research implementation;
5. it does not unnecessarily constrain alternative valid scientific designs.

This is the bar for framework ownership of a shared representation: a demonstrated generic requirement independent of concrete EHP research semantics, not merely that two research components happen to use the same schema.
Having a second producer or consumer is useful _evidence_ toward points 2 and 3; it is not, by itself, the criterion.

A schema whose current guarantees are narrower than its name implies should be named for what it actually guarantees (for example, `categorical-field/v1`, not a generic `observation-field/v1` that would misleadingly suggest it covers continuous, multimodal, or partial observation structures too).
A broader or different structure gets its own, separately named contract rather than becoming a "variant" of an existing one.

## Contract document structure

Every contract in this section must address the following normative concerns in this order.
The structure standardizes semantic authority and document navigation; it must not be expanded with boilerplate solely for symmetry.

```text
## Normative summary

## Scope and boundary
### Owned semantics
### Excluded semantics

## Canonical identity and conformance

## Conceptual model
### <contract-specific subsections>

## Logical record schema
### <contract-specific subsections>

## Properties and compatibility surface
### Fixed schema properties              # when applicable
### Derived compatibility properties     # when applicable

## Invariants and validation
### Record invariants
#### XX-REC-001 — ...
#### XX-REC-002 — ...
### Validation requirements

## Compatibility and composition boundary
### Compatibility requirements
### Composition rules                    # when applicable

## Evolution
### Compatible changes
### Breaking changes

## Related specifications
```

`Conceptual model` and `Logical record schema` may use contract-specific subsection names because the represented objects genuinely differ.
`Fixed schema properties`, `Derived compatibility properties`, and `Composition rules` are optional when they do not apply.

`Record invariants`, `Validation requirements`, `Compatibility requirements`, `Compatible changes`, and `Breaking changes` use those exact subsection names in every contract.

An `Artifact invariants` subsection is permitted only when the scientific contract itself owns an artifact-level invariant.
Generic artifact lifecycle, record addressing, record-ID uniqueness, index semantics, and record-envelope behavior must not be introduced here merely because a concrete artifact needs them.

Across those sections, every contract must:

- define exactly one reusable semantic object;
- identify authoritative semantic content and distinguish canonical derived views where they exist;
- define content equality or identity-bearing semantic inputs where meaningful;
- provide a complete logical representation rather than only physical channels;
- remain independent of physical serialization;
- distinguish schema-fixed properties from derived compatibility properties;
- avoid encoding producer guarantee scope, consumer requirement representation, or matching algorithms before the framework compatibility specification defines them;
- avoid redefining generic artifact, index, or record-envelope semantics;
- state its compatibility and composition boundary explicitly;
- state compatible and breaking contract changes separately;
- remain meaningful without any concrete producer, consumer, task, substrate family, or `ehp_research` package.

The following headings are not used as contract-level substitutes for the canonical structure:

- `Downstream use`;
- `Task-owned validation`;
- `New release under a producing family`;
- `New specification version of this schema`.

Their legitimate content belongs under `Compatibility requirements`, `Composition rules`, `Compatible changes`, or `Breaking changes`.

## Compatibility mechanism

`ehp_sn` will define a generic producer–consumer compatibility model for reusable scientific data contracts.
The intended model must support:

- canonical contract/schema references;
- producer guarantees over contract-defined properties;
- consumer requirements over those properties;
- explicit scope for artifact-wide guarantees versus per-record values;
- deterministic conformance and compatibility validation;
- integration with `ResourceRequirement` binding and validation.

The exact public type decomposition, serialization, guarantee-scope representation, requirement language, and compatibility-result model are intentionally deferred until the framework compatibility specification is written.

Until that specification exists:

- a contract defines only schema-fixed properties and the scientific meaning/value domain of derived compatibility properties;
- values such as `record-dependent`, `derived`, or `not-applicable` must not be used to encode guarantee scope when the underlying mathematical property has an ordinary value;
- [Resource requirements](../../interfaces/configuration/resource-requirements.md) remains the provisional operational integration surface through accepted schema IDs and package-owned compatibility validators;
- no contract here implies that public types such as `ContractRef`, `CapabilityDeclaration`, or `CapabilityRequirement` already exist.

## Per-record identity and record envelope — deferred

EHP-SN requires deterministic, independently addressable records within generated data artifacts.
A future framework specification will define the generic relationship among artifact indexes, record identifiers, logical record schemas, record addressing, and any common record envelope.

Until that specification exists, concrete data contracts may require a `record_id` field as a provisional interoperability requirement.
They must not define global identity semantics, hashing rules, cross-artifact equality, or physical serialization for that identifier.

## Registered contracts

| Schema                 | Specification                                                               |
| ---------------------- | --------------------------------------------------------------------------- |
| `ambient-domain/v1`    | [`domains/ambient-domain/v1`](domains/ambient-domain-v1.md)                 |
| `raster-topology/v1`   | [`topology/raster-topology/v1`](topology/raster-topology-v1.md)             |
| `categorical-field/v1` | [`observations/categorical-field/v1`](observations/categorical-field-v1.md) |
| `simple-digraph/v1`    | [`relations/simple-digraph/v1`](relations/simple-digraph-v1.md)             |

The table registers framework contract specifications, not concrete artifact releases or producing families.
Concrete producers and consumers declare their relationships to these contracts downstream; those relationships are not part of the contracts' normative authority.

## Related specifications

- [`Framework reference`](../index.md)
- [`Resource requirements`](../../interfaces/configuration/resource-requirements.md) — the provisional schema-ID-plus-validator integration surface
- [`Data artifacts`](../data-artifacts.md)
