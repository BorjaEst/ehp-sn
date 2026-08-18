---
title: Ownership model
authority: descriptive
document_status: draft
---

# Ownership model

This document explains _why_ semantic ownership in EHP-SN is shaped the way it is.
It is explanatory and descriptive: it defines no semantics.
The normative map lives in `docs/authority.md` and the hard cross-cutting rules in `docs/invariants.md`; individual concepts are defined by the normative specifications those documents point to.

It exists so a reader can quickly build the intended three-layer mental model without re-deriving it from scattered specifications, and so agents have a shared vocabulary for the placement algorithm before they read an authority or invariant.

## 1. The three layers

```text
ehp_sn
    reusable framework abstractions and orchestration

ehp_research
    reusable scientific building blocks

experiments/
    concrete scientific compositions using those building blocks
```

The placement rule is:

```text
generic software/framework semantics
    → ehp_sn

reusable scientific semantics
    → ehp_research

semantics created by selecting and connecting concrete scientific components
    → experiments/
```

Dependency direction is `ehp_research → ehp_sn`.
`ehp_sn` must not import `ehp_research` (`ARCH-001`).
Repository-level `experiments/` may depend on both.

## 2. Abstraction versus concrete composition

Many concepts exist at two levels: a generic framework abstraction and a concrete selection.

- The **`Binding` abstraction** — one task, one model, one configured `InputAdapter`, one configured `OutputAdapter` — is a framework contract.
  Its implementation abstraction lives in `ehp_sn`.
- A **concrete Binding** — the experiment-specific choice and configuration of those adapters for a particular task–model pair — is scientific composition.
  It is declared in `experiments/<experiment>/vN/experiment.toml`, and its composition lives under `experiments/<experiment>/vN/`.
- The **`ExperimentDefinition` abstraction** is a framework contract (what a resolved experiment composition contains).
  A **concrete `ExperimentDefinition`** is an instance declared in `experiments/<experiment>/vN/experiment.toml`.

The point of the split: the framework defines what these mechanics mean, `ehp_research` provides the reusable scientific blocks, and the experiment declares which concrete blocks it selects and connects.
No layer redefines the other's semantics.

`experiments/<name>/vN/experiment.toml` is a **concrete declaration** instantiating the framework specification, not another specification of its own.
An experiment's scientific narrative (if any) is carried by an optional descriptive `README.md`, and temporary design reasoning lives in informal `design/` notes.

## 3. Adapter versus Binding

An **Adapter** is a reusable transformation primitive (for example a sequence adapter, a slot adapter, a categorical adapter, a mask adapter, a field decoder).
It is expressible entirely in terms of its declared source interface, target interface, and resolved configuration (`ADAPT-001`).
Generic adapters belong to `ehp_sn`.

A **Binding** is the concrete integration of a selected task, model, and configured adapters.
The experiment-specific _choice and configuration_ of those adapters is the binding and belongs under `experiments/<experiment>/vN/`.

Wrong: `ehp_sn.adapters.arena_tem` (an experiment-specific adapter in the framework).
Right: `ehp_sn.adapters.sequence`, `ehp_sn.adapters.slots`, `ehp_sn.adapters.categorical`; the experiment selects and configures them.

## 4. Worked example: Arena ↔ TEM

```text
Arena task representation
        ↓
generic sequence adapter
        ↓
generic categorical adapter
        ↓
TEM native interface
        ↓
TEM
        ↓
generic output adapter
        ↓
Arena prediction representation
```

The generic adapters belong to `ehp_sn`.
The experience-specific choice and configuration of those adapters — how Arena observations map to TEM `sensory_id` values, how Arena actions map to `relation_id` values, which TEM output role is interpreted as an Arena prediction — is declared in `experiments/arena-tem/v1/experiment.toml`.
Such binding semantics are scientific and may exist only for this selected composition; that is legitimate experiment-local declaration content (`experiments/arena-tem/v1/`), not framework or `ehp_research` content.

## 5. Placement algorithm

When deciding where a concept belongs, ask in order:

1. Is it generic framework machinery reusable outside the EHP research programme? → `ehp_sn`.
2. Is it scientific meaning independently reusable across multiple possible experiments? → `ehp_research`.
3. Does this semantics exist specifically because one experiment chose to connect concrete scientific components? → `experiments/`.

```text
generic sequence adapter                    → ehp_sn
raster-topology/v1 (logical contract)       → ehp_sn
TEM                                         → ehp_research
Arena                                       → ehp_research
reusable revisit metric                     → ehp_research
Arena → TEM relation encoding               → experiments/arena-tem/
Arena + TEM + objective + protocols         → experiments/arena-tem/
```

## 6. Data architecture

Reusable substrate producers live in `ehp_research`.
They produce records conforming to framework-owned logical contracts (`ARCH-011`), for example `raster-topology/v1`, `categorical-field/v1`, `simple-digraph/v1`.
Research tasks consume those normalized contracts rather than the producer identity.
A committed `TaskCorpus` is self-contained for its declared normal consumers (`DATA-004`); parent substrate artifacts are build inputs and provenance, not runtime dependencies.

## 7. Why this matters during migration

Existing files may reflect an older architecture (for example package-owned `experiments/` or `bindings/` scaffolds, or documentation that assigns experiment families to `ehp_research`).
Under `ARCH-015`, existing historical placement is not precedent: when the target architecture is established, conflicting normative material is realigned in place and obsolete competing semantics are removed rather than preserved.
