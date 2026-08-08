# EHP-SN repository instructions

EHP-SN is a specification-first multipackage monorepo.

## Repository model

The repository contains two installable packages:

```text
ehp_research → ehp_sn
```

- `ehp_sn` owns reusable framework contracts and services.
- `ehp_research` owns concrete scientific components and research-owned domain contracts.
- `ehp_sn` must not depend on `ehp_research`.

Do not introduce a reverse dependency.

## Authority first

Before changing architecture, public interfaces, scientific semantics, or documentation:

1. Identify the concept being changed.
2. Find its semantic owner and normative specification using `docs/authority.md`.
3. Identify upstream specifications the change must obey.
4. Identify downstream code, tests, interfaces, READMEs, and documentation that may become stale.
5. Apply all matching path-specific instructions under `.github/instructions/`.
6. Check the relevant repository invariants in `docs/invariants.md`.

Do not resolve conflicting authoritative specifications by guessing.

If two authoritative specifications conflict, report the conflict and the decision required.

## Specification-first rule

Normative specifications define intended public semantics.

Implementation is evidence of implemented behavior, but implementation must not silently redefine the specification.

When implementation exposes a missing or contradictory contract:

- identify the missing or conflicting authority;
- keep the local implementation from inventing an incompatible semantic contract;
- update the authoritative specification as part of the same coherent change when the design decision is clear.

## Change discipline

Prefer the smallest coherent change that satisfies the requirement.

Do not introduce:

- framework abstractions without a demonstrated framework-level requirement;
- task semantics into substrates;
- model-native representation into task semantics;
- research-specific semantics into generic framework contracts;
- backend-native semantics into public interfaces;
- hidden resource selection that affects reproducibility.

Do not use generic statements such as "follow best practices", "think carefully", or "reason step by step" as verification.

Use observable checks.

## Synchronization rule

When an authoritative semantic contract changes:

1. update the authority first;
2. update implementations and tests that implement that contract;
3. update interface documentation;
4. update summaries and READMEs last.

README files, examples, tutorials, comments, and catalogues must not become independent semantic authorities.

## Generated and duplicated information

Prefer deriving or mechanically validating information that appears in several places, including:

- component reference;
- title;
- kind;
- status;
- maturity;
- owner;
- specification path;
- catalogue membership.

Do not manually duplicate authoritative metadata when it can be generated or checked.
