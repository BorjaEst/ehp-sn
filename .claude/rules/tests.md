---
paths:
  - "tests/**/*.py"
  - "packages/*/tests/**/*.py"
---

# Test instructions

Tests validate public contracts and architecture invariants.

Prefer deterministic checks whenever the requirement is deterministic.

## Architecture tests

`docs/invariants.md` § "Enforcement" lists every invariant with its observable check and whether that check exists. Entries marked `none` are the backlog; when a change relies on such an invariant, add its check.

Priority coverage:

- ARCH-001 (`ehp_sn`/`ehp_research` dependency direction) holds;
- ARCH-002 (canonical component references are unique) holds;
- ARCH-003 (duplicate registrations fail) holds;
- CONFIG-001 (resource requirements are declared and bound through configuration) and CONFIG-003 (identity-affecting resource selection is reproducibly represented in resolved configuration/provenance) hold;
- DATA-001/TASK-001 (substrate/task ownership boundaries) are preserved where mechanically testable.

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
