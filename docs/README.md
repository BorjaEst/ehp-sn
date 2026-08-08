# EHP-SN documentation

This directory contains the EHP-SN documentation project and its documentation-governance files.

```text
docs/
├── README.md
├── authority.md
├── invariants.md
├── mkdocs.yml
├── docs/
│   ├── _index.md
│   ├── api/
│   ├── data/
│   ├── design/
│   ├── development/
│   ├── framework/
│   ├── interfaces/
│   ├── models/
│   ├── regimes/
│   └── research/
└── site/
```

## File roles

### `README.md`

This file is the contributor/development entry point for the documentation project.

It explains how the documentation tree is organized and how semantic authority is managed.

It is not the public documentation homepage.

### `authority.md`

[`authority.md`](authority.md) defines which package/specification owns each class of semantics and how conflicts are resolved.

Agents and contributors should consult it before changing architectural or normative claims.

### `invariants.md`

[`invariants.md`](invariants.md) defines cross-cutting repository conditions that specifications, implementations, interfaces, and documentation must preserve.

### `mkdocs.yml`

`mkdocs.yml` configures the MkDocs documentation build.

The published documentation source is the nested `docs/docs/` directory.

### `docs/_index.md`

`docs/docs/_index.md` is the public documentation landing page rendered by MkDocs.

It should orient readers to framework, research, interface, and development documentation. It should not duplicate the contributor guidance in this file.

### `site/`

`site/` is generated documentation output and must not be treated as a semantic source of truth.

## Documentation hierarchy

Published documentation is organized by responsibility:

```text
docs/docs/
├── framework/       reusable ehp_sn contracts
├── interfaces/      public CLI, Python, and configuration interfaces
├── research/        ehp_research scientific specifications
├── design/          architectural/design decomposition
├── development/     repository/development contracts
├── api/             API reference entry points
├── data/            data-oriented documentation entry points
├── models/          model documentation entry points
└── regimes/         evaluation-regime documentation entry points
```

The semantic owner of a concept is authoritative, not the directory depth.

Use [`authority.md`](authority.md) when ownership is unclear.

## Specification-first workflow

For semantic changes:

```text
requirement / design decision
        ↓
normative specification
        ↓
implementation
        ↓
tests
        ↓
interface documentation
        ↓
README / overview synchronization
```

Do not begin by changing a README and then force specifications to match it.

## Documentation consistency

Before finishing a documentation change:

- check affected links;
- check component references;
- check status and maturity;
- check CLI and configuration examples;
- check package ownership;
- check terminology against the authority;
- identify downstream summaries that became stale.

Information such as component references, status, and catalogue membership should be generated or mechanically validated where practical.

## GitHub Copilot

Repository instructions live under:

```text
.github/
├── copilot-instructions.md
├── instructions/
└── prompts/
```

Path-specific instructions follow architectural responsibility across documentation, source code, and tests.

For example, task instructions apply to both task specifications and task implementations rather than only to Markdown files.

## Building the documentation

Use the repository's documented MkDocs/development commands.

The authoritative MkDocs configuration is `docs/mkdocs.yml`.

Generated `docs/site/` content should not be edited manually.

## Generating the docs

Use [mkdocs](http://www.mkdocs.org/) structure to update the documentation.

Build locally with:

```bash
    mkdocs build
```

Serve locally with:

```bash
    mkdocs serve
```
