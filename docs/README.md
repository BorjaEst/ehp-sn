# EHP-SN documentation

This directory contains the EHP-SN documentation project and its documentation-governance files.

```text
docs/
├── README.md
├── authority.md
├── invariants.md
├── decisions.md
├── mkdocs.yml
├── docs/
│   ├── _index.md
│   ├── architecture/
│   ├── concepts/
│   ├── decisions/
│   ├── development/
│   ├── framework/
│   ├── getting-started/
│   ├── guides/
│   ├── interfaces/
│   └── research/
└── site/
```

## File roles

### `README.md`

This file is the contributor/development entry point for the documentation project.

It explains how the documentation tree is organized and how semantic authority is managed.

It is not the public documentation homepage.

### Governance files

Each governance file answers exactly one question. None of them restates another's content.

| Question                                      | File                              |
| --------------------------------------------- | --------------------------------- |
| Where is a concept owned and specified?       | [`authority.md`](authority.md)    |
| What must always hold, and how is it checked? | [`invariants.md`](invariants.md)  |
| What is not yet decided?                      | [`decisions.md`](decisions.md)    |

[`authority.md`](authority.md) assigns ownership by specification root rather than per component, so a document's owner follows from its location. It also defines the specification frontmatter contract.

[`invariants.md`](invariants.md) defines numbered cross-cutting conditions and, in § "Enforcement", the observable check for each one.

[`decisions.md`](decisions.md) records conflicting or missing authority as required by DOC-002. Its entries are transient and are deleted once the decision is captured in the owning document.

Agents and contributors should consult all three before changing architectural or normative claims.

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
├── architecture/     architectural decomposition (ownership unresolved)
├── concepts/         cross-cutting concept documentation (ownership unresolved)
├── decisions/        recorded design decisions (ownership unresolved)
├── development/      repository/development contracts
├── framework/        reusable ehp_sn contracts
├── getting-started/  onboarding documentation (ownership unresolved)
├── guides/           task-oriented guides (ownership unresolved)
├── interfaces/       public CLI, Python, and configuration interfaces
└── research/         ehp_research scientific specifications
```

See [`decisions.md`](decisions.md) DEC-001 for the directories whose semantic owner is not yet decided.

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

## Claude Code

Repository instructions live under:

```text
CLAUDE.md
.claude/
├── rules/
├── skills/
├── agents/
└── handoffs/
```

`.claude/handoffs/` holds the untracked design → implementation contracts described by `.claude/handoffs/README.md`.

Path-specific rules follow architectural responsibility across documentation, source code, and tests.

For example, task rules apply to both task specifications and task implementations rather than only to Markdown files.

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
