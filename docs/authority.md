---
title: Documentation and semantic authority
authority: normative
document_status: specified
---

# Documentation and semantic authority

This document answers one question: **where is a concept owned, and where does its normative specification live?**

It does not state rules. Cross-cutting rules are numbered invariants in `docs/invariants.md`. Undecided ownership is recorded in `docs/decisions.md`.

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

`ehp_research` owns concrete scientific definitions and research-owned shared domain contracts.

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

Ownership is assigned by specification root, not per component. A specification's location determines its semantic owner.

| Concept category                                                     | Semantic owner          | Specification root                                                                                                                                | Implementation surface                        |
| -------------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------- |
| Package dependency direction, authority model                        | repository architecture | `docs/authority.md`, `docs/invariants.md`                                                                                                         | package metadata, imports, architecture tests |
| Generic framework contracts and services                             | `ehp_sn`                | `docs/docs/framework/`                                                                                                                            | `packages/ehp-sn/src/`                        |
| Public configuration model, resolution, and requirements             | `ehp_sn`                | `docs/docs/interfaces/configuration/`                                                                                                             | `packages/ehp-sn/src/`                        |
| Public CLI behavior                                                  | `ehp_sn`                | `docs/docs/interfaces/cli/`                                                                                                                       | `packages/ehp-sn/src/`                        |
| Public Python behavior                                               | `ehp_sn`                | `docs/docs/interfaces/python/`                                                                                                                    | `packages/ehp-sn/src/`                        |
| Research substrate semantics                                         | `ehp_research`          | `docs/docs/research/substrates/`                                                                                                                  | `packages/ehp-research/src/`                  |
| Research task semantics                                              | `ehp_research`          | `docs/docs/research/tasks/`                                                                                                                       | `packages/ehp-research/src/`                  |
| Research model semantics and resolved experiment/binding composition | `ehp_research`          | `docs/docs/research/`, `experiments/`                                                                                                             | `packages/ehp-research/src/`, `experiments/`  |
| Repository and package overview                                      | descriptive             | root and package READMEs                                                                                                                          | not applicable                                |
| Published documentation orientation content                          | descriptive             | `docs/docs/index.md`, `docs/docs/architecture/`, `docs/docs/concepts/`, `docs/docs/decisions/`, `docs/docs/guides/`, `docs/docs/getting-started/` | not applicable                                |
| Agent roles, procedures, and path scoping                            | procedural              | `.claude/`                                                                                                                                        | not applicable                                |

Generic `Task` and `Model` _contracts_ are framework-owned; their concrete scientific _definitions_ are research-owned. The distinction is the one drawn in "Ownership versus orchestration" above.

`Binding` is not an independently specified contract: it is the resolved, validated connection of one task and one model, formed by one configured `InputAdapter` and one configured `OutputAdapter`. `InputAdapter` and `OutputAdapter` are generic framework contracts, specified under `docs/docs/framework/` (`docs/docs/framework/adapters.md`); a concrete resolved binding — its adapter configuration and the composition itself — is assembled by an `ExperimentDefinition` and is research-owned, following the same generic-contract/concrete-definition split.

### Closure rule

A normative path not covered by a specification root above has **no recorded owner**.

For such a path:

- do not treat it as normative for any concept owned elsewhere;
- do not assert ownership of it from a lower-authority location, including `.claude/rules/` path scoping, a README, or an `index.md`;
- record the gap in `docs/decisions.md`.

## Component index

Per-component ownership is **derived, not listed here**. Listing every component beside its owner and specification path would manually duplicate metadata that `docs/invariants.md` DOC-003 requires to be generated or mechanically validated, and that duplication is the observed cause of the divergences recorded in `docs/decisions.md`.

A component's authority is established by:

1. its specification's location under a root in the authority map, which determines the semantic owner;
2. its specification frontmatter, which declares its identity and maturity;
3. the catalogue or `index.md` for that root, which should be generated from or validated against that frontmatter.

### Specification frontmatter

Maturity and stability are not one axis. EHP-SN distinguishes several dimensions, each with its own subject, vocabulary, and canonical home. A dimension must not reuse or conflate another dimension's field name or values (`docs/invariants.md` DOC-006).

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

`capability_status` and `component_maturity` describe related but distinct things at different granularity and evidentiary bar: `capability_status` is a document's own three-level self-declaration; `component_maturity` is a coarser-grained, potentially externally verified five-level rollup shown in a catalogue. Neither substitutes for the other.

A catalogue column must state which dimension it displays (for example, a "Component maturity" column heading, not a bare "Status") so readers and mechanical validation can tell which vocabulary its values come from.

Presence and validity of the per-document frontmatter is required by `docs/invariants.md` DOC-006.

## Related authority

| Question                                      | Document             |
| --------------------------------------------- | -------------------- |
| Where is a concept owned and specified?       | this document        |
| What must always hold, and how is it checked? | `docs/invariants.md` |
| What is not yet decided?                      | `docs/decisions.md`  |
| How should an agent act on a given path?      | `.claude/rules/*.md` |

Rules previously restated here are owned as invariants:

- one normative home per semantic contract — ARCH-002;
- READMEs are projections, not authorities — DOC-001;
- conflicting specifications are reported, not silently reconciled — DOC-002;
- derivable metadata is generated or validated, not duplicated — DOC-003;
- agent configuration under `.claude/` is procedural and never semantic authority — DOC-007.
