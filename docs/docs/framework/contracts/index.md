---
title: Contracts
authority: normative
document_status: draft
capability_status: planned
---

# Contracts

This section contains `ehp_sn`-owned standard scientific data contracts: producer-agnostic, consumer-agnostic logical record schemas for reusable structures such as spatial domains, topology, and relational graphs.

```text
                ehp_sn — contracts/ (this section)
                            │
          ┌─────────────────┼─────────────────┼─────────────────┐
          │                 │                 │                 │
       domains/       topology/         observations/       relations/
    ambient-domain   raster-topology   categorical-field   simple-graph
          │                 │                 │                 │
   ───────┴─────────────────┴─────────────────┴─────────────────┴───────
       ↑ producers                                consumers ↓

    substrate builders                         task builders
    (any package, including                    (any package, including
     ehp_research/research/substrates/)         ehp_research/research/tasks/)
```

A contract defines the object represented, its authoritative and derived representations, and a capability vocabulary producers declare and consumers require.
It does not define which package or family produces it, or which task consumes it — that coupling is deliberately absent, and no contract here imports or references a concrete `ehp_research` component.
`ehp_research → ehp_sn` is the only dependency direction; a contract must remain meaningful if `ehp_research` did not exist.

Compatibility is checked through schema ID plus declared/required capabilities.
Today this reuses the mechanism [Resource requirements](../../interfaces/configuration/resource-requirements.md) already defines generically (accepted schema IDs plus, where schema equality alone is insufficient, a package-owned compatibility validator).
See "Compatibility mechanism" below for the planned generic form.

## Documentation boundary

A contract specification defines:

- the object represented and its unit of record;
- the authoritative representation versus any canonical derived views;
- the capability vocabulary;
- the logical record schema, independent of physical serialization;
- schema-level invariants that hold for every conforming record, regardless of producer;
- compatibility and evolution rules for the schema itself.

A contract specification does not define:

- which family produces it, or that family's generation/production process;
- which task consumes it, or that task's scientific semantics;
- generic artifact manifests, digests, lifecycle, publication, or reuse.

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

## Compatibility mechanism

`ehp_sn` will define a generic producer–consumer compatibility contract for reusable scientific data schemas.
The mechanism will support canonical contract/schema references, producer-declared capabilities, consumer-required capabilities, and deterministic conformance validation.
The exact public type decomposition and serialization are deferred until the framework compatibility specification is written.

Until that specification exists, a contract in this section states its capability vocabulary in its own "Capabilities" section, and binding is described informally in terms of the existing [Resource requirements](../../interfaces/configuration/resource-requirements.md) schema-ID-plus-validator mechanism.
No contract here should be read as implying that `ContractRef`, `CapabilityDeclaration`, or `CapabilityRequirement` already exist as public types.

## Registered contracts

| Schema                 | Specification                                                               | Producing families (current) |
| ---------------------- | --------------------------------------------------------------------------- | ---------------------------- |
| `ambient-domain/v1`    | [`domains/ambient-domain/v1`](domains/ambient-domain-v1.md)                 | shared building block        |
| `raster-topology/v1`   | [`topology/raster-topology/v1`](topology/raster-topology-v1.md)             | `dungeongen`, `maze-nd`      |
| `categorical-field/v1` | [`observations/categorical-field/v1`](observations/categorical-field-v1.md) | `obsfield`                   |
| `simple-graph/v1`      | [`relations/simple-graph/v1`](relations/simple-graph-v1.md)                 | `dagflow`                    |

The table registers specification work, not concrete artifact releases.
"Producing families (current)" lists today's `ehp_research` producers as evidence, not as part of the contract's own normative scope.

## Related specifications

- [`Framework reference`](../index.md)
- [`Substrates`](../../research/substrates/index.md) — families that produce records conforming to these contracts
- [`Tasks`](../../research/tasks/index.md) — tasks that require records conforming to these contracts
- [`Resource requirements`](../../interfaces/configuration/resource-requirements.md) — the schema-ID-plus-capability compatibility mechanism
- [`Data artifacts`](../data-artifacts.md)
