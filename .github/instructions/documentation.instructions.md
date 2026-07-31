---
name: EHP-SN documentation
description: Responsibility and specification rules for Markdown documentation
applyTo: "**/*.md"
---

# Documentation

Documentation is part of the normative specification.

Apply only the sections relevant to the document being edited. Do not force scientific or architecture templates onto unrelated Markdown.

When the document belongs to framework or research responsibilities, apply these documentation rules together with the corresponding path-specific instructions.

## Context routing

```text
README.md
    repository architecture and package relationship

packages/ehp-sn/README.md
    root README
    relevant docs/architecture documents

packages/ehp-research/README.md
    root README
    concrete docs/research catalogues

docs/framework/**
    framework README
    relevant docs/architecture documents

docs/research/**
    research README
    related scientific specifications
    relevant framework contract on demand

docs/architecture/**
    root README
    docs/architecture/responsibilities.md
    owning package README when package-specific
    both package READMEs when cross-package

experiments/*/README.md
    experiment assets
    participating scientific component specifications
    relevant framework contracts
```

## README hierarchy

### Root `README.md`

Owns:

- repository identity and scope;
- repository structure;
- relationship between `ehp_sn` and `ehp_research`;
- complete-workspace installation and testing;
- repository navigation and status.

It does not define framework contracts or catalogue scientific components in detail.

### `packages/ehp-sn/README.md`

Owns:

- framework vocabulary and public contracts;
- framework module responsibilities;
- component composition;
- protocols, services, validation, and artifacts;
- framework-only installation and testing.

It does not catalogue concrete research systems.

### `packages/ehp-research/README.md`

Owns:

- scientific scope;
- concrete substrate, task, model, and binding catalogues;
- supported integrations and component status;
- research metrics, analyses, and experiments;
- research-package installation and testing.

It links to the framework README for framework definitions rather than redefining them.

## Detailed document ownership

- `docs/architecture/` owns cross-cutting structure, responsibility boundaries, decisions, and rationale.
- `docs/framework/` owns normative reusable framework contracts.
- `docs/research/substrates/` owns concrete substrate semantics and invariants.
- `docs/research/tasks/` owns task semantics, mathematics, information boundaries, validity, and evaluation.
- `docs/research/models/` owns model architecture, state, memory, objectives, capabilities, and traces.
- `docs/research/bindings/` owns concrete task-model integrations.
- `docs/research/metrics/` owns metric definitions, required information, interpretation, and limitations.
- `docs/research/analyses/` owns derived analyses over existing artifacts.
- `experiments/*/README.md` owns one configured study or reproduction procedure.
- `docs/development/` owns contributor workflows and conventions.

## Scientific document review dimensions

Use these as review dimensions. Include them as visible headings only when they suit the document type.

```text
Objective:
Terms and definitions:
Inputs and outputs:
Public and privileged information:
Assumptions:
Invariants:
Acceptance criteria:
Evidence or derivation:
Unresolved decisions:
```

Do not silently reconcile contradictions or fill scientific gaps with implementation choices.

## Architecture document review dimensions

Use these as review dimensions. Include them as visible headings only when they suit the document type.

```text
Context:
Objective:
Constraints:
Decision:
Responsibility allocation:
Alternatives:
Trade-offs:
Consequences:
Verification criteria:
Open questions:
```

Distinguish architectural requirements from implementation choices.

## Writing rules

- Explain what the subject is before design rationale.
- Keep one authoritative home for each concept.
- Link to the owning document instead of repeating its explanation.
- Preserve agreed terminology, identifiers, versions, and dependency direction.
- Distinguish normative requirements from examples and future possibilities.
- Define scientific semantics before code or CLI details.
- Include a detail only when omitting it would make the document incomplete or unusable; otherwise link to the owning document.
- Use equations, tables, or pseudocode when they make behavior more precise.
- State ambiguity, limitations, contradictions, and unresolved decisions explicitly.
- Update documentation with every normative contract or scientific-semantic change.
