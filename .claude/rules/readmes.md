---
paths:
  - "README.md"
  - "docs/README.md"
  - "packages/*/README.md"
  - "config/README.md"
  - "experiments/**/README.md"
  - ".github/README.md"
---

# README instructions

README files are descriptive entry points.

They summarize authoritative specifications and current implementation status; they are not independent semantic authorities.

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

- explain concrete scientific ownership;
- summarize the current substrate/task/model/binding/experiment catalogue;
- explain the dependency on `ehp_sn`;
- explain registration/discovery;
- keep substrate descriptions aligned with current research specifications;
- document how to run the package's tests.

## Documentation README

`docs/README.md` is the contributor/development entry point for the MkDocs documentation project.

It should explain:

```text
docs/
├── README.md
├── authority.md
├── invariants.md
├── decisions.md
├── mkdocs.yml
└── docs/          # published MkDocs source
```

It must distinguish `docs/README.md` from `docs/docs/index.md`.

## GitHub README

`.github/README.md` is the entry point for the `.github/` directory.

It should explain:

- that agent configuration (agents, rules, skills, hooks, handoffs) lives under `.claude/`, not `.github/`;
- that `.github/` holds CI workflows only.

It must not restate `.claude/` agent configuration or introduce normative semantics of its own.

## Synchronization

DOC-001 governs this. When a README conflicts with a normative specification, update the README.

Check especially:

- component references;
- component status/maturity;
- package ownership;
- CLI syntax;
- configuration examples;
- implementation status;
- substrate/task descriptions.

Prefer generated or mechanically validated catalogues when practical.
