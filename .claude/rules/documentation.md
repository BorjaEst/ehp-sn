---
paths:
  - "docs/docs/**/*.md"
  - "docs/authority.md"
  - "docs/invariants.md"
  - "docs/decisions.md"
---

# Documentation instructions

Documentation changes must preserve the authority model in `docs/authority.md` and the invariants in `docs/invariants.md`.

Ownership is assigned by specification root, not per component. Determine a document's owner from its location in the authority map.

## Before changing a claim

For every normative or architectural claim being changed:

1. identify the concept;
2. identify its semantic owner;
3. identify its normative specification;
4. identify documents that summarize or depend on it;
5. distinguish a semantic change from a synchronization change.

Do not create a second normative definition of an existing concept.

Reference authoritative contracts rather than reproducing them when a local summary is sufficient.

## Conflict classification

When reviewing documentation consistency, classify findings as:

- `consistent`;
- `stale`;
- `contradictory`;
- `underspecified`;
- `missing authority`.

For every non-consistent finding state:

- the claim;
- the authority;
- the evidence of mismatch;
- why it matters;
- which file should change.

If two authoritative specifications disagree, do not silently merge them. Record the conflict in `docs/decisions.md` and report the decision required (DOC-002).

## Specification metadata

The frontmatter contract is defined by `docs/authority.md` § "Specification frontmatter" and required by `docs/invariants.md` DOC-006. `status` is the canonical maturity field.

Do not invent a second metadata vocabulary, and do not restate the field list here.

When catalogue/status metadata can be generated or checked from specification frontmatter, prefer generation or deterministic validation over manual duplication (DOC-003).

## Examples

Examples must conform to the current normative interfaces.

In particular, verify:

- current CLI command form;
- current configuration paths;
- current component references;
- current artifact/resource terminology;
- current package ownership.

Examples are not allowed to define behavior that is absent from the authoritative interface specification.
