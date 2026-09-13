---
title: ModelIOSpec
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# ModelIOSpec

This document defines the framework abstraction for a **model IO specification**: the declaration of how one selected task's declared interfaces are reconciled with one selected model's declared interfaces.

An experiment selects one task and one model independently. A `ModelIOSpec` selects neither; it is the narrow contract for the correspondence between their declared interfaces, formed by one configured `InputAdapter` and one configured `OutputAdapter`.
It is the framework's generic contract for that composition; it defines no concrete task, model, or experiment.

## What a ModelIOSpec is

A `ModelIOSpec` is not an additional scientific concept layered on top of a task and a model.
It does not select, own, or re-reference the task or the model.
It declares only the reconciliation of their declared interfaces: the input adapter maps the task-data interface to the model-input interface; the output adapter maps the model-output/prediction interface to the task-prediction interface.

A `ModelIOSpec` is a declarative specification, not the executable transformation.
It declares which configured adapters reconcile which declared interfaces.
The executable transformations are the reusable adapters owned by the framework, selected and configured per experiment.

## What a ModelIOSpec must contain

- the configured `InputAdapter`;
- the configured `OutputAdapter`;
- the declared source and target interfaces each adapter is resolved against, by reference to the task and model interfaces the experiment has selected.

The task and the model are selected by the experiment, not by the `ModelIOSpec`.

## Constraints

The composition must not change (`MIO-001`):

- public versus withheld information;
- task truth;
- target meaning;
- split meaning;
- metric meaning.

An `InputAdapter` must not add privileged information or change the task information boundary (`ADAPT-002`).
An `OutputAdapter` must not perform oracle repair or task-level scoring (`ADAPT-002`).

## Identity and reference semantics

A `ModelIOSpec` has no independent reference kind and no independent canonical reference.
It is embedded in the experiment declaration and identified through the experiment that declares it (`ARCH-006`).
Changing a configured adapter or its configuration changes the resolved experiment composition and, where identity-affecting, the experiment's resolved digest.

## Adapter composition

`v1` admits exactly two slots: one configured `InputAdapter` and one configured `OutputAdapter`, corresponding to the two directions for which adapter contracts exist.

Additional named slots, an ordered adapter chain within a slot, and a target-side slot are not yet specified.
They must not be invented by a declaration or an implementation until the framework owns that contract (`ARCH-014`).

## Concrete ModelIOSpec authority

The framework defines what a `ModelIOSpec` is and how it is validated.
Which adapters a particular experiment selects and configures — including adapters assembled through experiment-local configuration — is the concrete `ModelIOSpec`, declared in `experiments/<experiment>/vN/experiment.toml` and validated against this specification and the referenced adapter contracts.

A concrete `ModelIOSpec` is an integral part of the experiment that declares it: it is embedded in the experiment's declaration, conforming to this framework contract, and is not an independently registered or discoverable research component (`ARCH-006`).
There is no separately discoverable installed component that represents it.
A resolved `ModelIOSpec` may carry an internal/scoped identity for provenance, but that identity is subordinate to the experiment.
The concrete `ModelIOSpec` adds no semantics of its own: any concept too substantial to express as declaration configuration belongs in the owning task, model, or adapter specification, not in an experiment-level document.
