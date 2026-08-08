---
title: Repository invariants
authority: normative
document_status: specified
---

# Repository invariants

These invariants define cross-cutting conditions that architectural, implementation, configuration, interface, and documentation changes must preserve.

Each invariant should be backed by observable checks where practical.

## Architecture

### ARCH-001 — Package dependency direction

```text
ehp_research → ehp_sn
```

`ehp_sn` must not depend on `ehp_research`.

Observable checks should include:

- dependency declarations in `packages/ehp-sn/pyproject.toml`;
- imports under `packages/ehp-sn/src/`;
- architecture tests.

### ARCH-002 — One semantic authority

A semantic contract must have one normative owner/specification.

Lower-authority code comments, READMEs, examples, and overview pages may summarize but must not redefine it.

### ARCH-003 — Registration does not reverse dependencies

Installed research definitions may register with framework-owned containers/registries.

The framework must not import concrete research packages by name to populate its catalogue.

Duplicate canonical registrations must fail rather than depend on import order.

## Data and substrates

### DATA-001 — Substrate neutrality

A substrate contains reusable task-neutral domain structure.

It must not contain semantics that exist only because a downstream task posed a particular problem.

Specification check:

- substrate schemas do not contain task-only query, target, episode, reward, or metric semantics.

Implementation check:

- substrate builders do not generate task cases, task targets, or model-native encodings.

### DATA-002 — Independent substrate identity

A substrate's identity must not depend on downstream task composition.

Examples:

- ObsField identity does not include topology identity;
- topology identity does not include Arena/MazeHard/Routebind use;
- Dagflow node identity does not include observation binding.

### DATA-003 — Explicit task parent binding

Tasks declare parent roles and compatibility requirements.

Exact parent artifacts are selected through resolved task-build configuration or another explicitly specified reproducible binding mechanism.

Identity-affecting parent selection must not depend on:

- hidden builder randomness;
- implicit filesystem discovery;
- import order;
- unrecorded user choices.

### DATA-004 — Self-contained task corpus

A committed `TaskCorpus` must contain all resources required by its declared normal consumers.

Parent artifacts are build inputs and provenance, not normal runtime dependencies.

Normal training/evaluation/inspection must not silently reopen parent substrate artifacts.

### DATA-005 — Shared research contracts remain research-owned

A representation shared by several research components does not become a framework contract solely because it is shared.

Framework ownership requires a demonstrated generic framework requirement independent of concrete EHP research semantics.

### DATA-006 — Release coordinate immutability

A committed scientific data release coordinate must never be rebound to different content.

A new intentional content identity requires a new release coordinate.

## Tasks and bindings

### TASK-001 — Task ownership

Tasks own:

- scientific problem meaning;
- information regime;
- parent-role semantics;
- task-owned composition;
- case/query/episode generation;
- oracle truth;
- targets;
- validity;
- task-level metrics.

### BIND-001 — Binding boundary

Bindings may adapt task semantics to model-native representations.

Bindings must not change:

- public versus withheld information;
- task truth;
- target meaning;
- split meaning;
- metric meaning.

## Configuration and resources

### CONFIG-001 — Requirements before resources

Scientific definitions declare resource requirements.

Configuration binds those requirements to exact permitted resources.

### CONFIG-002 — Backend independence

Hydra or another backend must not become the public configuration language or semantic authority.

### CONFIG-003 — Reproducible resolution

Identity-affecting configuration and resource selection must be represented in resolved configuration and/or semantic provenance according to the authoritative contracts.

### CONFIG-004 — CLI/Python semantic equivalence

Equivalent CLI and Python inputs must converge on equivalent:

- finalized scientific definitions;
- effective request values;
- resource bindings;
- derived values;
- identity-relevant plan fields.

## CLI

### CLI-001 — Orchestration, not scientific ownership

CLI commands expose and orchestrate operations.

Scientific semantics remain owned by framework/research specifications.

### CLI-002 — Common lifecycle vocabulary

Equivalent operations should use the established lifecycle vocabulary unless a demonstrated requirement requires another operation:

```text
list
show
plan
validate
build
run
inspect
```

### CLI-003 — Stable public configuration boundary

The CLI must expose EHP-SN-owned configuration semantics rather than backend-native Hydra syntax.

## Artifacts and execution

### ART-001 — Committed scientific artifacts are immutable

Artifact-producing operations must stage, validate, and commit without leaving incomplete state that appears valid.

### ART-002 — Provenance is not runtime dependency

Provenance may reference parent/build inputs without requiring those resources for normal use of a self-contained committed artifact.

## Documentation

### DOC-001 — README projection

README files summarize existing specifications and must not introduce new normative semantics.

### DOC-002 — No silent authority repair

When two normative specifications conflict, an agent or implementation change must report the conflict rather than silently reconcile them.

### DOC-003 — Derived metadata is not manually duplicated unnecessarily

Status, component references, catalogue membership, and similar derivable metadata should be generated or mechanically validated where practical.

### DOC-004 — Examples conform to current interfaces

Quick starts and examples must use the currently specified CLI, Python, configuration, reference, and artifact semantics.

### DOC-005 — Docs development and published docs are distinct

`docs/README.md` documents the documentation project and contributor workflow.

`docs/docs/_index.md` is the published MkDocs documentation landing page.

They must not be treated as interchangeable authorities.

## Verification expectation

A change affecting an invariant must provide an observable check showing why the invariant still holds.

The following are not sufficient verification:

- "reviewed carefully";
- "followed best practices";
- "reasoned step by step".
