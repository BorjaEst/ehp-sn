---
title: Repository invariants
authority: normative
status: specified
---

# Repository invariants

This document answers one question: **what must always hold, and how is it checked?**
These invariants define cross-cutting conditions that architectural, implementation, configuration, interface, and documentation changes must preserve.
Ownership and specification locations are in `docs/authority.md`. Undecided questions are in `docs/decisions.md`.
Every invariant has an entry in "Enforcement" below stating its observable check, or recording that it has none yet.

## Architecture

### ARCH-001 — Package dependency direction

```text
ehp_research → ehp_sn
```

`ehp_sn` must not depend on `ehp_research`.

### ARCH-002 — One semantic authority

A semantic contract must have one normative owner/specification.
Lower-authority code comments, READMEs, examples, and overview pages may summarize but must not redefine it.

### ARCH-003 — Registration does not reverse dependencies

Installed research definitions may register with framework-owned registries.
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
- information regime — which information of a task record is public, target, privileged or oracle-only, and withheld;
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

### DOC-006 — Specification frontmatter is present and valid

Every normative specification carries the frontmatter contract defined in `docs/authority.md` § "Specification frontmatter", using `status` as the canonical maturity field.

A second status vocabulary must not be introduced.

### DOC-007 — Agent configuration is not semantic authority

Files under `.claude/` define agent roles, procedures, and path scoping.

They must not define EHP-SN domain semantics, including ownership enumerations, excluded-semantics enumerations, contracts, or scientific vocabulary.

A domain claim an agent must apply belongs in the specification that owns it, and is referenced from `.claude/` by invariant ID or specification path rather than restated.

### DOC-008 — Published documentation links resolve

A relative link between published documentation files must resolve to an existing document.

Scope is the MkDocs source tree `docs/docs/`, where a broken link ships to readers as a dead page.

Agent configuration under `.claude/` is out of scope. A reference there is followed by an agent, not rendered for a reader, so it fails at the point of use rather than silently.

## Verification expectation

A change affecting an invariant must provide an observable check showing why the invariant still holds.

The following are not sufficient verification:

- "reviewed carefully";
- "followed best practices";
- "reasoned step by step".

## Enforcement

`test` means an automated check exists.
`manual` means the invariant is currently checked only by review.
`none` means no check exists yet and one should be added when the invariant is next relied upon.

| ID         | Observable check                                                                                                   | State  |
| ---------- | ------------------------------------------------------------------------------------------------------------------ | ------ |
| ARCH-001   | dependency declarations in `packages/ehp-sn/pyproject.toml`; no `ehp_research` import under `packages/ehp-sn/src/` | none   |
| ARCH-002   | no two `authority: normative` specifications declare the same component reference                                  | none   |
| ARCH-003   | framework source contains no import of a concrete research package by name; duplicate registration raises          | none   |
| DATA-001   | substrate schemas expose no task-only query, target, episode, reward, or metric field                              | manual |
| DATA-002   | substrate identity inputs exclude downstream task composition                                                      | manual |
| DATA-003   | parent selection is reproducible from resolved configuration                                                       | manual |
| DATA-004   | committed corpus loads and validates with parent artifacts absent                                                  | none   |
| DATA-005   | shared research contracts remain under `packages/ehp-research/src/`                                                | none   |
| DATA-006   | a committed release coordinate never resolves to changed content                                                   | none   |
| TASK-001   | task-owned semantics are absent from substrate specifications and implementations                                  | manual |
| BIND-001   | binding output preserves public/withheld split, truth, targets, splits, and metric meaning                         | manual |
| CONFIG-001 | scientific definitions declare requirements; configuration binds them                                              | manual |
| CONFIG-002 | public configuration surface exposes no backend-native syntax                                                      | none   |
| CONFIG-003 | identity-affecting selection appears in resolved configuration or provenance                                       | none   |
| CONFIG-004 | equivalent CLI and Python inputs produce equal resolved plans                                                      | none   |
| CLI-001    | CLI modules define no scientific semantics                                                                         | manual |
| CLI-002    | command names conform to the lifecycle vocabulary                                                                  | none   |
| CLI-003    | CLI help and documented options contain no Hydra-native syntax                                                     | none   |
| ART-001    | interrupted artifact production leaves no committed incomplete artifact                                            | none   |
| ART-002    | normal use of a committed artifact opens no parent artifact                                                        | none   |
| DOC-001    | README files introduce no `authority: normative` claim                                                             | manual |
| DOC-002    | unresolved conflicts appear in `docs/decisions.md`                                                                 | manual |
| DOC-003    | catalogue and status metadata match specification frontmatter                                                      | none   |
| DOC-004    | documented examples use current CLI, configuration, and reference syntax                                           | none   |
| DOC-005    | `docs/README.md` and `docs/docs/_index.md` are not cross-referenced as equivalents                                 | manual |
| DOC-006    | every `authority: normative` document under a specification root carries valid frontmatter                         | none   |
| DOC-007    | no file under `.claude/` declares `authority: normative` or enumerates owned or excluded domain semantics          | manual |
| DOC-008    | `mkdocs build --strict` in `.github/workflows/build-docs.yml` fails on an unresolved link under `docs/docs/`       | test   |

Checks marked `none` are the intended backlog for `tests/architecture/`, per `.claude/rules/tests.md`.

A `manual` entry is also backlog: promote it to `test` when a deterministic check becomes practical.
An entry's state records the check that exists today, not the check that is intended, and is updated in the same change that adds or removes one.

An invariant may be enforced over part of the repository before it can be enforced everywhere. Where coverage is partial, the enforcement row states the covered scope.

The same applies within an invariant.
The check description states what the existing check actually verifies, not what the invariant requires.
A row must not claim a reference class, path, or condition that its check does not test.
