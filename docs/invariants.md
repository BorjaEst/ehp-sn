---
title: Repository invariants
authority: normative
document_status: specified
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

## Tasks, adapters, and bindings

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

### ADAPT-001 — Adapter genericity

An `InputAdapter` or `OutputAdapter` must be expressible entirely in terms of its declared source interface, target interface, and resolved configuration.

It must not branch on concrete task or model identity.

### ADAPT-002 — Adapter direction boundary

An `InputAdapter` must not change the task information boundary or introduce privileged information.

An `OutputAdapter` must not perform oracle repair or task-level scoring.

### ADAPT-003 — Single parameter ownership

A semantic parameter has one authoritative owner: the task, the model, or an adapter's own
authored configuration. Another component may constrain or derive a value from that owner but
must not independently author the same fact.

An `AdapterDefinition` must not declare authored configuration for a value already determined by
the resolved task-data, task-prediction, model-input, or model-output interface; such a value
must be declared derived and computed from those interfaces during resolution.

### BIND-001 — Binding boundary

A Binding is the resolved composition of one task, one model, one configured `InputAdapter`, and one configured `OutputAdapter`.

That composition must not change:

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

For every operation exposed through both the CLI and Python interfaces, equivalent canonical inputs must converge on equivalent:

- finalized scientific definitions;
- effective request values;
- resource bindings;
- derived values;
- identity-relevant plan fields.

The CLI and Python are not required to expose identical operation surfaces or identical convenience syntax. An interface-specific convenience (such as a CLI-only flag) is permitted only when it resolves into the same framework-owned canonical request/configuration fields the other interface would use; it must not introduce semantics that exist on only one interface.

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

`docs/docs/index.md` is the published MkDocs documentation landing page.

They must not be treated as interchangeable authorities.

### DOC-006 — Specification frontmatter is present and valid

Every normative specification carries the frontmatter contract defined in `docs/authority.md` § "Specification frontmatter".

Each maturity/stability dimension listed there has exactly one canonical vocabulary and one canonical home. A dimension must not reuse or conflate another dimension's field name or values, and a new dimension must not be introduced outside that section.

### DOC-007 — Agent configuration is not semantic authority

Files under `.claude/` define agent roles, procedures, and path scoping.

They must not define EHP-SN domain semantics, including ownership enumerations, excluded-semantics enumerations, contracts, or scientific vocabulary.

A domain claim an agent must apply belongs in the specification that owns it, and is referenced from `.claude/` by invariant ID or specification path rather than restated.

### DOC-008 — Published documentation links resolve

A relative link between published documentation files must resolve to an existing document.

Scope is the MkDocs source tree `docs/docs/`, where a broken link ships to readers as a dead page.

Agent configuration under `.claude/` is out of scope. A reference there is followed by an agent, not rendered for a reader, so it fails at the point of use rather than silently.

### DOC-009 — Tables serve reader comparison

A table is used only for data that is genuinely multi-dimensional and comparable — rows that share the same set of attributes across two or more columns.

- Data with only one substantive attribute per item uses a list, not a single-column table.
- A table introduces itself: a sentence immediately before it states what it contains and, where not obvious from the heading, why it is a table.
- A table too wide or multi-concerned to stay scannable is split by concern (for example: shape/requiredness in one table, visibility/role/meaning in another) rather than left as one wide table. Each resulting table keeps its own specific introductory sentence naming its concern — a sentence shared across the whole split does not satisfy the introduction requirement for its second and later tables.
- Rows follow a stated or evident logical order (declaration order, dependency order, severity) rather than an arbitrary one.
- Header cells are short, sentence-case, and free of trailing punctuation.
- Cell content stays short — a value, a term, a short phrase. Elaboration that does not fit belongs in prose after the table, not packed into a cell.
- A cell holds at most 100 characters. Content that does not fit at that length is compressed to its essential claim, with detail deferred to the surrounding prose or the definition the row points to — not wrapped or truncated with an ellipsis.

This governs table content and structure. It does not restate Markdown table syntax, which `docs/mkdocs.yml` § `markdown_extensions` and CommonMark/GFM already define.

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

### Automated (`test`)

DOC-008 is the only invariant with an automated check today: `mkdocs build --strict` in `build-docs.yml` fails on an unresolved `docs/docs/` link.

### Manual (`manual`)

These invariants are checked only by review; each is backlog to promote to an automated check when practical.

| ID         | Observable check                                                                                    |
| ---------- | --------------------------------------------------------------------------------------------------- |
| DATA-001   | substrate schemas expose no task-only query, target, episode, reward, or metric field               |
| DATA-002   | substrate identity inputs exclude downstream task composition                                       |
| DATA-003   | parent selection is reproducible from resolved configuration                                        |
| TASK-001   | task-owned semantics are absent from substrate specifications and implementations                   |
| BIND-001   | resolved binding output preserves public/withheld split, truth, targets, splits, and metric meaning |
| CONFIG-001 | scientific definitions declare requirements; configuration binds them                               |
| CLI-001    | CLI modules define no scientific semantics                                                          |
| DOC-001    | README files introduce no `authority: normative` claim                                              |
| DOC-002    | unresolved conflicts appear in `docs/decisions.md`                                                  |
| DOC-005    | `docs/README.md` and `docs/docs/index.md` are not cross-referenced as equivalents                   |
| DOC-007    | no `.claude/` file declares `authority: normative` or enumerates domain semantics                   |
| DOC-009    | every published table is multi-dimensional, self-introduced, and uses sentence-case headers         |

### Not yet checked (`none`)

No check exists yet for these invariants; each is backlog for `tests/architecture/`, per `.claude/rules/tests.md`, to be added when next relied upon.

| ID         | Observable check                                                                                |
| ---------- | ----------------------------------------------------------------------------------------------- |
| ARCH-001   | no `ehp_research` import under `packages/ehp-sn/src/`; none declared in `pyproject.toml`        |
| ARCH-002   | no two `authority: normative` specifications declare the same component reference               |
| ARCH-003   | framework source imports no concrete research package by name; duplicate registration raises    |
| DATA-004   | committed corpus loads and validates with parent artifacts absent                               |
| DATA-005   | shared research contracts remain under `packages/ehp-research/src/`                             |
| DATA-006   | a committed release coordinate never resolves to changed content                                |
| ADAPT-001  | adapter implementation contains no conditional keyed on concrete task or model identity         |
| ADAPT-002  | InputAdapter adds no privileged information; OutputAdapter performs no oracle repair or scoring |
| ADAPT-003  | adapter definition declares no authored field already determined by the resolved interfaces     |
| CONFIG-002 | public configuration surface exposes no backend-native syntax                                   |
| CONFIG-003 | identity-affecting selection appears in resolved configuration or provenance                    |
| CONFIG-004 | equivalent CLI and Python inputs produce equal resolved plans                                   |
| CLI-002    | command names conform to the lifecycle vocabulary                                               |
| CLI-003    | CLI help and documented options contain no Hydra-native syntax                                  |
| ART-001    | interrupted artifact production leaves no committed incomplete artifact                         |
| ART-002    | normal use of a committed artifact opens no parent artifact                                     |
| DOC-003    | catalogue and status metadata match specification frontmatter                                   |
| DOC-004    | documented examples use current CLI, configuration, and reference syntax                        |
| DOC-006    | every `authority: normative` document under a specification root carries valid frontmatter      |

An entry's state records the check that exists today, not the check that is intended, and is updated in the same change that adds or removes one.

An invariant may be enforced over part of the repository before it can be enforced everywhere. Where coverage is partial, the enforcement row states the covered scope.

The same applies within an invariant.
The check description states what the existing check actually verifies, not what the invariant requires.
A row must not claim a reference class, path, or condition that its check does not test.
