# EHP-SN repository instructions

EHP-SN is developed from specification to code. Normative READMEs and documents define the intended system; the current implementation does not override them.

## Repository architecture

- The repository contains two Python packages: `ehp_sn` and `ehp_research`.
- The dependency direction is `ehp_research -> ehp_sn`.
- `ehp_sn` must never import `ehp_research`.
- `ehp_sn` owns reusable framework contracts and execution infrastructure.
- `ehp_research` owns concrete scientific implementations.
- Place each responsibility in the narrowest package and module that owns its semantics.
- Use explicit Python composition.
- Do not introduce plugin discovery, global registries, or additional infrastructure without a demonstrated requirement.

## Design direction

Reason from usage toward infrastructure:

```text
use case
-> scientific requirement
-> public contract
-> service
-> backend
```

- Do not change an agreed scientific requirement to fit the current implementation.
- When a justified requirement is unsupported, identify the contract gap.
- Do not duplicate framework infrastructure in `ehp_research`.
- Prefer the simplest design that satisfies the actual requirements.
- Generalize when a responsibility is inherently framework-level or when repeated workflows demonstrate stable commonality.

## Responsibility isolation

- Scientific task semantics belong to research tasks.
- Model semantics belong to research models.
- Task-model integration belongs to bindings.
- Final study composition belongs to experiments.
- Generic contracts, validation, execution, configuration, artifacts, and CLI infrastructure belong to `ehp_sn`.
- Repository-level experiment assets configure reproducible studies; generated runs are artifacts.

## Context use

Read context from broad to specific:

1. `README.md`;
2. the owning package README;
3. the detailed normative specification for the affected responsibility;
4. directly related specifications;
5. the current implementation.

For cross-package architecture, also consult the relevant documents under `docs/architecture/`.

When sources conflict, the more specific normative specification governs the affected behavior unless it violates a repository-level or package-level responsibility boundary.

## Ambiguity

When normative sources conflict, terminology is unresolved, or a required decision is missing:

1. identify the conflicting or missing information;
2. state the implementation consequence;
3. preserve the unresolved decision instead of silently choosing;
4. record the decision required to proceed.

Do not present an implementation preference as a scientific or architectural requirement.

## Changes

Before editing, establish:

- the objective;
- the owning package and module;
- the normative sources;
- the affected public contracts;
- the acceptance criteria.

Update tests and documentation when changing normative behavior, scientific semantics, compatibility, versions, or artifact schemas.
