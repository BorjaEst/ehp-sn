---
title: ExperimentDefinition
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# ExperimentDefinition

This document defines the framework abstraction for an **experiment definition**.

An `ExperimentDefinition` is the generic framework contract stating what a resolved scientific experiment composition contains and how it is resolved.
It defines no concrete experiment.

## What an ExperimentDefinition contains

A resolved experiment composition selects and combines:

- a task;
- a model;
- a concrete Binding (task + model + configured adapters);
- adapters;
- objectives;
- controllers;
- metrics;
- analyses;
- a training protocol;
- an evaluation protocol;
- traces;
- resource requirements.

## Resolution lifecycle

The framework owns the resolution mechanism.
Resolution conceptually proceeds from an experiment reference through a workspace experiment catalogue to the experiment definition, which carries component references resolved against the installed component registry, and finally to a resolved `ExperimentDefinition` and constructed concrete Binding.

The resolution mechanism is framework-owned; the repository owns the concrete experiment definition.

## Concrete ExperimentDefinition authority

The framework defines what a resolved experiment composition contains and how it is assembled.
Which components a particular experiment selects is the concrete `ExperimentDefinition`, owned by the experiment under `experiments/<experiment>/vN/` and specified in that experiment's `plan.md`.

## Not specified here

This document does not define a serialization schema, a discovery catalogue format, or a resolve-side loader.
Those are framework contracts that must be specified before implementation; do not invent them (`ARCH-014`).
