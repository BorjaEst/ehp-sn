---
applyTo: "tests/**/*.py,packages/*/tests/**/*.py"
---

# Test instructions

Tests validate public contracts and architecture invariants.

Prefer deterministic checks whenever the requirement is deterministic.

## Architecture tests

Architecture tests should cover relevant invariants from `docs/invariants.md`, including:

- `ehp_sn` does not depend on or import `ehp_research`;
- canonical component references are unique;
- duplicate registrations fail;
- configured resource binding is deterministic;
- substrate/task ownership boundaries are preserved where mechanically testable.

## Documentation/interface consistency tests

Where practical, test:

- referenced files exist;
- catalogue/status metadata matches specification metadata;
- canonical component references are unique;
- deprecated CLI/configuration syntax is absent;
- required frontmatter exists;
- documentation dependency references resolve;
- CLI help agrees with documented command names/options.

## Contract-oriented testing

Test observable public behavior rather than private implementation layout unless the layout itself is an architectural invariant.

Do not use snapshots as the sole authority for scientific semantics.
