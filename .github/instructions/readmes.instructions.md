---
description: "Use when writing or editing README files across the repository: keep them as orientation and summaries, not normative authorities."
applyTo: "README.md, docs/README.md, packages/*/README.md, config/README.md, experiments/**/README.md, .github/README.md"
---

# README instructions

README files are descriptive entry points.
They summarize authoritative specifications and current implementation status; they are not independent semantic authorities (DOC-001).

## Root README

The repository `README.md` should:

- explain the two-package architecture;
- state the dependency direction;
- summarize the end-to-end lifecycle;
- show current public workflow examples;
- explain specification-first status;
- link to detailed authorities;
- document how to run tests, static checks, and formatting commands.

It should not reproduce complete framework or research contracts.

## Framework package README

`packages/ehp-sn/README.md` should:

- explain reusable framework responsibilities;
- explain Task / Model / Binding / Experiment / Request / Artifact concepts;
- explain configuration/resource-binding at a high level;
- explain public Python and CLI equivalence;
- avoid concrete research semantics except as examples;
- document how to run the package's tests.

## Research package README

`packages/ehp-research/README.md` should:

- explain reusable scientific ownership;
- summarize the current substrate/task/model/binding/experiment catalogue;
- explain the dependency on `ehp_sn`;
- explain registration/discovery;
- keep substrate descriptions aligned with current research specifications;
- document how to run the package's tests.

It must not present concrete experiments or Bindings as package-owned; those belong to `experiments/`.

## Documentation README

`docs/README.md` is the contributor/development entry point for the MkDocs documentation project.
It must distinguish `docs/README.md` from `docs/docs/index.md` (DOC-005).

## GitHub README

`.github/README.md` is the entry point for the `.github/` directory.
It should explain:

- that `.github/` holds CI workflows and Copilot agent instructions (`.github/instructions/`, `copilot-instructions.md`);
- that these agent instructions are procedural, not semantic authority.

## Synchronization

DOC-001 governs this.
When a README conflicts with a normative specification, update the README.
Check especially:

- component references;
- component status/maturity;
- package ownership;
- concrete-experiment ownership.
