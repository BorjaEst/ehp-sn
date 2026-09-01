---
title: Figure extension and conformance guide
authority: descriptive
document_status: draft
---

# Figure extension and conformance guide

This guide explains how to add a figure to EHP-SN without changing the figure framework.
It is operational guidance: it summarizes and links to the normative specifications rather than redefining them.

The authoritative contracts are:

- the framework figure specifications under [`framework/figures/`](../framework/figures/index.md);
- the repository-wide figure invariants `FIG-001`–`FIG-004` in `docs/invariants.md`;
- the figure extension and conformance evidence in `packages/ehp-sn/tests/figures/`.

## Where a figure belongs

Follow the ordinary ownership model ([`architecture/figures.md`](../architecture/figures.md) § "Three semantic placement levels"):

```text
ehp_sn.figures.builtin
    framework contract-level figures (meaning expressible via a shared contract)

ehp_research.figures
    reusable scientific figures (meaning independent of one concrete experiment)

experiments/<experiment>/vN/
    joint figures (meaning depends on one concrete composition)
```

A new **producer** that emits an already-supported contract (for example `raster-topology/v1`) needs no new figure at all: the existing contract inspection figure works automatically over the new producer's records.

## Adding a framework contract figure

A framework contract figure's meaning is expressible purely through a framework-owned logical contract.
To add one:

1. **Confirm visual inspection has material value** — the figure must not duplicate an existing text-only inspection; it selects/aligns/renders already-authoritative information.
2. **Define the `FigureSpec`** — a registered executable capability with three partitions: `projection` (scientific-view semantics), `visual` (scientific-encoding semantics), and `defaults` (presentation-only).
   See [core.md](../framework/figures/core.md).
3. **Declare the semantic input requirement** — one `FigureInputRequirement` naming the `role`, the framework `contract`, and the `scope` (`record` or `artifact`).
   See [projection.md](../framework/figures/projection.md).
4. **Prepare domain-specific `FigureData`** — the `prepare()` implementation selects/aligns/labels only; it must not compute new scientific evidence (`FIG-002`).
5. **Define scientific visual semantics** — how the prepared variables map to marks, axes, labels, and any protected `rc`-parameters (for example a scientifically fixed colormap).
   See [visual-semantics.md](../framework/figures/visual-semantics.md).
6. **Register through the ordinary provider/component authority** — contribute the `FigureSpec` through the figure-provider entry-point group (`ehp_sn.figures.providers`); there is no parallel figure registry.
7. **Add conformance tests** — value/structure assertions over projection identity, selected identities, coordinate mapping, normalization, and category mapping; register a deterministic-selection and immutability test.

## Adding a research producer figure

Add a research figure **only when** the producer-owned authoritative semantics cannot be adequately represented by the shared contract figures.
For example a producer generation summary interprets producer-declared descriptors that a contract-level figure must not interpret.

Reuse the generic rendering implementation where the visual object is generic; own only the scientific meaning — source-role requirements, scientific preparation, `FigureData`, and scientific visual-composition semantics.
See [`research/figures/index.md`](../research/figures/index.md).

## Adding a new producer using an existing contract

When a producer emits an already-supported contract:

```text
existing generic contract inspection works automatically
```

No generic figure-framework modification should be required.

## Conformance checklist

A figure conforms to the architecture when it satisfies the Phase-7C conformance suite dimensions:

- **dependency direction** — generic orchestration names no producer, task, or model;
- **provider conformance** — catalogue semantics are independent of provider discovery order; a duplicate canonical identity is a deterministic error;
- **source resolution** — the figure consumes already-resolved generic sources; it does not implement artifact/record search, fingerprinting, or storage roots;
- **canonical contract conformance** — the figure's interpretation matches the logical contract validator;
- **identity partition** — `ProjectionIdentity` changes only for projection-semantic inputs; presentation/serialization change only `RealizationIdentity` (the [perturbation matrix](../framework/figures/rendering.md#realizationidentity));
- **determinism** — selection is independent of filesystem, dict, worker, and provider order;
- **scientific visual semantics** — quantitative panels share real normalization/domain; categorical IDs stay categorical; raster orientation is explicit and rcParams-independent; graph node IDs are not coordinates;
- **mutation** — rendering/preparation does not mutate the authoritative source or projection;
- **scientific authority** — figure code computes no acceptance evidence;
- **interface convergence** — CLI and Python resolve the same projection.
