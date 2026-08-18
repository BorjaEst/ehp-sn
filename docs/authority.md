---
title: Documentation and semantic authority
authority: normative
document_status: specified
---

# Documentation and semantic authority

This document answers one question: **where is a concept owned, and where does its normative specification live?**

It does not state rules.
Cross-cutting rules are numbered invariants in `docs/invariants.md`.
Undecided ownership is recorded in `docs/decisions.md`.

EHP-SN is specification-first:

```text
normative specification
    defines intended public semantics

implementation
    implements those semantics

tests
    verify observable conformance

interfaces and READMEs
    expose or summarize those semantics
```

Implementation must not silently become a competing semantic authority (`docs/invariants.md` ARCH-002).

## Package ownership

```text
ehp_research → ehp_sn
```

`ehp_sn` owns reusable framework contracts and services.

`ehp_research` owns reusable scientific definitions (substrates, tasks, models, objectives, controllers, metrics, analyses) and research-owned shared domain contracts.
Concrete repository-level experiments and Bindings belong to `experiments/` (ARCH-005/006).

The dependency direction is normative and enforced by `docs/invariants.md` ARCH-001.

## Ownership versus orchestration

Ownership means defining semantics.

Orchestration means exposing or executing semantics owned elsewhere.

For example:

```text
ehp_research Arena specification
    owns Arena task semantics

ehp-sn tasks CLI
    orchestrates Arena corpus construction

ehp_sn TaskCorpus contract
    owns generic corpus lifecycle/completeness mechanics
```

Do not use CLI presence as evidence of semantic ownership.

## Authority map

Ownership is assigned by specification root, not per component.
A specification's location determines its semantic owner.

| Concept category                                         | Specification root                        | Implementation surface       |
| -------------------------------------------------------- | ----------------------------------------- | ---------------------------- |
| Package dependency direction, authority model            | `docs/authority.md`, `docs/invariants.md` | metadata, imports, tests     |
| Generic framework contracts and services                 | `docs/docs/framework/`                    | `packages/ehp-sn/src/`       |
| Public configuration model, resolution, and requirements | `docs/docs/interfaces/configuration/`     | `packages/ehp-sn/src/`       |
| Public CLI behavior                                      | `docs/docs/interfaces/cli/`               | `packages/ehp-sn/src/`       |
| Public Python behavior                                   | `docs/docs/interfaces/python/`            | `packages/ehp-sn/src/`       |
| Research substrate semantics                             | `docs/docs/research/substrates/`          | `packages/ehp-research/src/` |
| Research task semantics                                  | `docs/docs/research/tasks/`               | `packages/ehp-research/src/` |
| Research model semantics                                 | `docs/docs/research/models/`              | `packages/ehp-research/src/` |
| Concrete experiment declaration                          | `experiments/<name>/vN/experiment.toml`   | `experiments/<name>/vN/`     |
| Experiment narrative and rationale                       | `experiments/<name>/vN/README.md`         | `experiments/<name>/vN/`     |

Generic `Task` and `Model` _contracts_ are framework-owned; their concrete scientific _definitions_ are research-owned.
The distinction is the one drawn in "Ownership versus orchestration" above.

## Target categories

EHP-SN distinguishes three kinds of content:

```text
SPECIFICATIONS      define semantics            → docs/docs/framework/, docs/docs/research/
DECLARATIONS        instantiate specifications  → experiments/<name>/vN/experiment.toml
OPERATIONAL         explain, note, or support   → READMEs, design notes, decisions register, agent instructions
```

The framework and research specifications define semantics; `experiment.toml` declares one concrete experiment conforming to them;
READMEs, design notes, the decisions register, and agent instructions have procedural or explanatory roles and define no domain contracts.

```text
Binding abstraction
    normative semantics → docs/docs/framework/ (components/binding.md)
    implementation abstraction → ehp_sn

Concrete Binding
    declaration → experiments/<experiment>/vN/experiment.toml
    concrete composition → experiments/<experiment>/vN/

ExperimentDefinition abstraction
    normative semantics → docs/docs/framework/ (components/experiment.md)
    implementation abstraction → ehp_sn

Concrete ExperimentDefinition
    declaration → experiments/<experiment>/vN/experiment.toml
    concrete composition → experiments/<experiment>/vN/
```

A concrete experiment's composition is declared in `experiments/<experiment>/vN/experiment.toml`, canonical for that experiment and validated against the framework specification.
The declaration is not a second semantic specification (`ARCH-002`); a concept too substantial to express as declaration belongs in the owning task, model, or adapter specification.
Any experimental narrative (motivation, rationale, reproducibility) is carried by an optional descriptive `README.md`; temporary design reasoning lives in informal `design/` notes.

The concrete Binding is embedded in that declaration and is not independently registered or discovered (`ARCH-006`).

There is no `ehp_research.experiments` and no `ehp_research.bindings`.
Concrete experiments and concrete task-model Bindings belong to repository-level `experiments/`.

### Descriptive and procedural content

Some paths are recorded here for the closure rule below without being semantic-ownership claims: they describe or orchestrate rather than define, so they are listed rather than tabulated — none has an implementation surface to compare against the table above.

- **Repository and package overview** (descriptive) — root and package READMEs.
- **Published documentation orientation content** (descriptive):
  - `docs/docs/index.md`
  - `docs/docs/architecture/`
  - `docs/docs/concepts/`
  - `docs/docs/decisions/`
  - `docs/docs/guides/`
  - `docs/docs/getting-started/`
  - `docs/docs/development/`
- **Agent procedures and path scoping** (procedural) — `.github/instructions/`, `.github/copilot-instructions.md`.

`Binding` is not an independently specified contract: it is the resolved, validated connection of one task and one model, formed by one configured `InputAdapter` and one configured `OutputAdapter`.
`InputAdapter` and `OutputAdapter` are generic framework contracts, specified under `docs/docs/framework/` (`docs/docs/framework/adapters/index.md`).
A concrete resolved Binding is assembled as part of a concrete experiment composition; its scientific semantics and adapter configuration are experiment-owned under `experiments/<experiment>/vN/`.

### Closure rule

A normative path not covered by a specification root above has **no recorded owner**.

For such a path:

- do not treat it as normative for any concept owned elsewhere;
- do not assert ownership of it from a lower-authority location, including `.github/instructions/` path scoping, a README, or an `index.md`;
- record the gap in `docs/decisions.md`.

## Component index

Per-component ownership is **derived, not listed here**.
Listing every component beside its owner and specification path would manually duplicate metadata that `docs/invariants.md` DOC-003 requires to be generated or mechanically validated, and that duplication is the observed cause of the divergences recorded in `docs/decisions.md`.

A component's authority is established by:

1. its specification's location under a root in the authority map, which determines the semantic owner;
2. its specification frontmatter, which declares its identity and maturity;
3. the catalogue or `index.md` for that root, which should be generated from or validated against that frontmatter.

### Specification frontmatter

Maturity and stability are not one axis.
EHP-SN distinguishes several dimensions, each with its own subject, vocabulary, and canonical home.
A dimension must not reuse or conflate another dimension's field name or values (`docs/invariants.md` DOC-006).

Every normative specification declares these per-document fields:

| Field               | Meaning                                                                | Values                                    |
| ------------------- | ---------------------------------------------------------------------- | ----------------------------------------- |
| `title`             | human-readable specification title                                     | free text                                 |
| `authority`         | whether the document defines or only summarizes semantics              | `normative`, `descriptive`                |
| `document_status`   | maturity of the specification writing itself                           | `draft`, `specified`                      |
| `capability_status` | the document's own self-declared belief about the described capability | `planned`, `partial`, `available`         |
| `api_stability`     | stability of the described public interface, when applicable           | `provisional`, `stable`, `not-applicable` |

Two further dimensions exist but are not per-document frontmatter fields, because their subject is not one document:

| Dimension                | Values                                                              | Subject                                                                                                                       | Canonical home                                                                                                                            |
| ------------------------ | ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `component_maturity`     | `planned` → `specified` → `implemented` → `validated` → `reference` | one component as a whole — specification, implementation, and validation evidence together, which may span multiple documents | catalogue tables, e.g. `docs/docs/research/substrates/index.md`, `docs/docs/research/tasks/index.md`, `docs/docs/interfaces/cli/index.md` |
| `compatibility_maturity` | `declared` → `implemented` → `validated` → `reference`              | one task–model(–binding) pair's compatibility                                                                                 | `docs/docs/framework/compatibility.md`                                                                                                    |

`capability_status` and `component_maturity` describe related but distinct things at different granularity and evidentiary bar: `capability_status` is a document's own three-level self-declaration; `component_maturity` is a coarser-grained, potentially externally verified five-level rollup shown in a catalogue.
Neither substitutes for the other.

A catalogue column must state which dimension it displays (for example, a "Component maturity" column heading, not a bare "Status") so readers and mechanical validation can tell which vocabulary its values come from.

Presence and validity of the per-document frontmatter is required by `docs/invariants.md` DOC-006.

## Related authority

Each row states a question about repository authority and which document holds the answer.

| Question                                        | Document                              |
| ----------------------------------------------- | ------------------------------------- |
| Where is a concept owned and specified?         | this document                         |
| What must always hold, and how is it checked?   | `docs/invariants.md`                  |
| What is not yet decided?                        | `docs/decisions.md` (register)        |
| How should an agent act on a given path?        | `.github/instructions/`               |
| Why is ownership shaped this way? (explanatory) | `docs/docs/architecture/ownership.md` |

`docs/architecture/ownership.md` is `authority: descriptive`.
It explains the three layers, Adapter versus Binding, and the placement algorithm with worked examples.
It defines no semantics; it points to the normative specifications this document maps.

Rules previously restated here are owned as invariants:

- one normative home per semantic contract — ARCH-002;
- READMEs are projections, not authorities — DOC-001;
- unresolved conflicts are reported, not silently reconciled, while an established target is realigned in place — DOC-002;
- derivable metadata is generated or validated, not duplicated — DOC-003;
- agent instructions under `.github/instructions/` are procedural and never semantic authority — DOC-007.
