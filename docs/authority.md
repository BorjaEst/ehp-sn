---
title: Documentation and semantic authority
authority: normative
document_status: specified
---

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

## Semantic ownership

```text
ehp_sn
    reusable framework contracts and services

ehp_research
    reusable scientific definitions

experiments/
    concrete scientific compositions and model IO specifications
```

Dependency direction:

```text
experiments → ehp_research
experiments → ehp_sn
ehp_research → ehp_sn
```

The dependency direction is normative; ARCH-001 enforces `ehp_research → ehp_sn`, and `experiments/` may depend on both (ARCH-005/006).

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
For a normative specification, its admitted location determines its semantic owner.

Normative status and publication status are independent.
A repository-authoritative specification need not be part of the MkDocs publication set.

A document is normative only when:

1. its frontmatter declares `authority: normative`; and
2. its path is either an explicitly governed normative file in the authority map or lies beneath a normative specification root admitted below.

Normative frontmatter outside an admitted normative location is invalid.
A descriptive document may live inside a specification root when its frontmatter explicitly declares `authority: descriptive`.

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
| Research figure semantics                                | `docs/docs/research/figures/`             | `packages/ehp-research/src/` |
| Concrete experiment declaration                          | `experiments/<name>/vN/experiment.toml`   | `experiments/<name>/vN/`     |
| Experiment-local scientific figure semantics             | `experiments/<name>/vN/figures/`          | `experiments/<name>/vN/`     |

Generic `Task` and `Model` _contracts_ are framework-owned; their concrete scientific _definitions_ are research-owned.
The distinction is the one drawn in "Ownership versus orchestration" above.

## Target categories

EHP-SN distinguishes three kinds of content:

```text
SPECIFICATIONS      define semantics            → docs/docs/framework/, docs/docs/research/,
                                                → experiments/<name>/vN/figures/
DECLARATIONS        instantiate specifications  → experiments/<name>/vN/experiment.toml
OPERATIONAL         explain, note, or support   → READMEs, design notes, decisions register, agent instructions
```

Framework and research specifications define reusable semantics.
An explicitly admitted experiment-local figure specification may define scientific visualization semantics whose meaning depends on one concrete experiment composition.
`experiment.toml` remains canonical for that experiment's composition; an experiment-local figure specification does not redefine the composition it visualizes.
READMEs, design notes, the decisions register, and agent instructions have procedural or explanatory roles and define no domain contracts.

```text
ModelIOSpec abstraction
    normative semantics → docs/docs/framework/ (components/model-io.md)
    implementation abstraction → ehp_sn

Concrete ModelIOSpec
    declaration → experiments/<experiment>/vN/experiment.toml
    embedded in the declaration, not independently registered or discovered (ARCH-006)

ExperimentDefinition abstraction
    normative semantics → docs/docs/framework/ (components/experiment.md)
    implementation abstraction → ehp_sn

Concrete ExperimentDefinition
    declaration → experiments/<experiment>/vN/experiment.toml
    concrete composition → experiments/<experiment>/vN/
```

A concrete experiment's composition is declared in `experiments/<experiment>/vN/experiment.toml`, canonical for that experiment and validated against the framework specification.
The declaration is not a second semantic specification (`ARCH-002`); a concept too substantial to express as declaration belongs in the owning normative specification root admitted above.
Any experimental narrative (motivation, rationale, reproducibility) is carried by an optional descriptive `README.md`; temporary design reasoning lives in informal `design/` notes.

An experiment may also contain normative scientific figure specifications under `experiments/<experiment>/vN/figures/`.
That root is admitted only for figure semantics whose scientific meaning depends on the concrete experiment composition.
It does not make `README.md`, `design/`, or other experiment-local Markdown normative, and it does not establish filesystem-based runtime discovery.
Figure discovery remains governed by framework component/provider contracts.

A `ModelIOSpec` reconciles the declared interfaces of one task and one model through one configured `InputAdapter` and one configured `OutputAdapter`, defined in `components/model-io.md`.
The concrete `ModelIOSpec` is embedded in the experiment declaration and is not independently registered or discovered (`ARCH-006`).

There is no `ehp_research.experiments` and no `ehp_research.model_io`.
Concrete experiments and concrete model IO specifications belong to repository-level `experiments/`.

### Publication boundary

`docs/docs/` is the normal MkDocs source tree for published project documentation.
That publication boundary does not determine semantic authority.

In particular:

- `docs/authority.md`, `docs/invariants.md`, and `docs/decisions.md` govern the repository but are not automatically MkDocs pages;
- `experiments/<name>/vN/figures/` may contain repository-authoritative figure specifications but is not automatically part of the MkDocs publication set;
- if an authoritative document outside `docs/docs/` is later projected into the published site, that projection must not become a second manually maintained semantic authority.

A specification path must never silently become a production discovery protocol merely because documentation tooling can locate it.

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

### Closure rule

A document declaring `authority: normative` outside an explicitly governed normative file or admitted specification root above has **no recorded owner** and is invalid as a normative specification.

For such a path:

- do not treat it as normative for any concept owned elsewhere;
- do not assert ownership of it from a lower-authority location, including `.github/instructions/` path scoping, a README, or an `index.md`;
- record the ownership gap in `docs/decisions.md` when the correct authority is genuinely unresolved;
- when the target authority is already established, realign the material in place under DOC-002/ARCH-015 rather than creating a second authority.

## Component index

Per-component ownership is **derived, not listed here**.
Listing every component beside its owner and specification path would manually duplicate metadata that `docs/invariants.md` DOC-003 requires to be generated or mechanically validated, and that duplication is the observed cause of the divergences recorded in `docs/decisions.md`.

A component's authority is established by:

1. its specification's location under a root in the authority map, which determines the semantic owner;
2. `authority: normative` plus the required specification frontmatter, which establishes that the document is a normative specification and declares its identity/maturity metadata;
3. the catalogue or `index.md` for that root, which should be generated from or validated against that frontmatter.

A versioned canonical component should map to one exact normative specification version.
Family, catalogue, or index pages spanning multiple component versions are descriptive unless an owning specification explicitly defines otherwise.

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
| `compatibility_maturity` | `declared` → `implemented` → `validated` → `reference`              | one task–model pair's compatibility                                                                                           | `docs/docs/framework/compatibility.md`                                                                                                    |

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
