---
name: EHP research
description: Scientific-first rules for research code, research specifications, experiments, configuration, scripts, and research tests
applyTo: "packages/ehp-research/**,docs/research/**,experiments/**,config/**,scripts/**,tests/research/**"
---

# Research development

Read, in order:

1. `README.md`;
2. `packages/ehp-research/README.md`;
3. the scientific specification for the affected component;
4. directly related research specifications.

These are the primary design inputs.

Do not inspect the complete framework implementation first and then reshape the scientific component to fit it.

## Documentation routing

Use the relevant research documents:

```text
substrate work
    docs/research/substrates/<substrate>.md

task work
    docs/research/tasks/<task>.md

model work
    docs/research/models/<family>/overview.md
    docs/research/models/<family>/<version>.md

binding work
    task specification
    model specification
    docs/research/bindings/<binding>.md

metric work
    docs/research/metrics/<metric-family>.md

analysis work
    docs/research/analyses/<analysis>.md

configured experiment
    experiments/<study>/README.md
    participating task, model, binding, metric, and protocol documents
```

For operational scripts without a scientific component, read the framework service, configuration, CLI, or artifact contract that the script invokes.

After deriving the scientific requirement, inspect the smallest relevant framework surface under `docs/framework/`. Expand framework context only when the requirement crosses additional contracts or services.

## Design direction

Reason from the scientific use case:

```text
scientific question
-> task or model semantics
-> required data and behavior
-> relevant framework contract
-> implementation
```

Use an existing framework contract when it expresses the scientific requirement without changing its meaning.

## Framework gaps

When the framework cannot express a justified requirement:

1. identify the missing capability;
2. explain the scientific requirement;
3. determine the owning responsibility;
4. assess whether the capability is reusable or inherently framework-level;
5. propose the minimal framework change;
6. do not implement parallel generic infrastructure in `ehp_research`.

Correct:

```text
scientific requirement
-> identify contract gap
-> change the owning framework contract
-> implement the research integration
```

Prohibited outcomes:

```text
framework limitation
-> weaken scientific semantics
```

```text
framework limitation
-> duplicate generic infrastructure in ehp_research
```

## Responsibility

`ehp_research` owns:

- concrete substrate generators and scientific assumptions;
- task semantics, targets, oracles, and invariants;
- model architectures, memory, and model-specific regularization;
- versioned task-model bindings;
- domain-specific controllers, objectives, metrics, and analyses;
- reusable experiment definitions.

Generic contracts, lifecycle services, artifact machinery, configuration infrastructure, and CLI execution belong to `ehp_sn`.

## Scientific boundaries

- Keep task semantics independent of model representation.
- Keep models independent of concrete tasks.
- Use a binding for each supported task-model integration.
- Preserve public, target, and privileged information exactly as specified.
- Keep task instances immutable and runtime state separate.
- Do not weaken validity rules or information boundaries for implementation convenience.
- Do not infer scientific compatibility from matching shapes.
- Preserve unresolved scientific choices as unresolved.
- Do not turn an implementation preference into a scientific requirement.

## Component procedure

1. establish the scientific objective and terminology;
2. identify inputs, outputs, hidden information, phases, and invariants;
3. expose ambiguity and unresolved decisions;
4. define acceptance criteria and semantic microcases;
5. derive the required framework contracts;
6. implement the narrowest scientific responsibility;
7. add deterministic tests and provenance;
8. update the component catalogue and detailed documentation.

## Experiments

- `ehp_research.experiments` contains reusable Python composition.
- `experiments/` contains configured studies and reproduction assets.
- Generated runs are artifacts and do not belong in source directories.
- Use configuration for parameter changes.
- Add a new Python experiment definition only when scientific composition or execution semantics change.
- If an experiment conflicts with a component specification, identify the conflict rather than silently reconciling it.

A configured study should identify:

```text
Scientific objective:
Task and version:
Model and version:
Binding and version:
Controller:
Objective terms and weights:
Training protocol:
Evaluation protocol:
Metrics and traces:
Inputs:
Expected outputs:
Acceptance criteria:
Reproducibility metadata:
Known limitations:
```

## Configuration

Configuration selects and parameterizes defined behavior.

- Use it for versions, parameters, paths, seeds, resources, and execution options.
- Do not hide scientific composition or introduce new semantics in configuration.
- Use explicit names and units.
- Validate ranges and cross-field constraints.
- Preserve resolved configuration in artifacts.
- Do not add fallbacks that silently change a study.

## Scripts

Scripts are thin operational entry points.

They may parse arguments, load explicit configuration or `module:object` references, construct requests, invoke services, format results, and map exit codes.

They must not own scientific logic, binding transformations, objectives, metric semantics, training algorithms, evaluation algorithms, or artifact lifecycle behavior.

## Research tests

Research tests verify:

- substrate invariants;
- task instances, targets, and oracles;
- model behavior and state;
- binding encoding and decoding;
- scientific objectives and metrics;
- semantic microcases;
- reference behavior.

Each test should identify the requirement, invariant, or acceptance criterion it verifies.

Use deterministic seeds and independently known expected results. Do not weaken scientific assertions to fit the implementation.
