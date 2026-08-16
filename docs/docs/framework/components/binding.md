---
title: Binding
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# Binding

This document defines the framework abstraction for a task–model **Binding**.

A Binding is the resolved, validated connection of one task and one model, formed by one configured `InputAdapter` and one configured `OutputAdapter`.
It is the framework's generic contract for that composition; it defines no concrete task, model, or experiment.

## What a Binding is

A Binding is not an additional scientific concept layered on top of a task and a model.
It is the composition of one task, one model, one configured `InputAdapter`, and one configured `OutputAdapter` (BIND-001).
The input adapter maps the task-data interface to the model-input interface; the output adapter maps the model-output/prediction interface to the task-prediction interface.

## What a Binding must contain

- the single task reference;
- the single model reference;
- the configured `InputAdapter`;
- the configured `OutputAdapter`.

## Constraints

The composition must not change (BIND-001):

- public versus withheld information;
- task truth;
- target meaning;
- split meaning;
- metric meaning.

An `InputAdapter` must not add privileged information or change the task information boundary (ADAPT-002).
An `OutputAdapter` must not perform oracle repair or task-level scoring (ADAPT-002).

## Identity and reference semantics

A Binding is identified by the canonical references of its task, model, and configured adapters, per `docs/docs/framework/references.md`.
The adapter contribution to the composition is defined in `docs/docs/framework/adapters/index.md`.
Changing any component or its configuration constitutes a different resolved composition and, where identity-affecting, a different binding identity.

## Concrete Binding authority

The framework defines what a Binding is and how it is validated.
Which task, model, and adapter configuration a particular experiment selects — including adapters assembled through experiment-local configuration — is the concrete Binding, owned by the experiment under `experiments/<experiment>/vN/` and specified in that experiment's `plan.md`.
