---
description: "Use when writing or reviewing tests, architecture checks, or coupling/responsibility-isolation review."
applyTo: "tests/**/*.py, packages/*/tests/**/*.py, .github/workflows/**"
---

# Testing instructions

## Preserve

- Tests verify observable conformance to normative specifications; they do not become a competing authority.
- Architecture tests mechanically verify selected invariants from `docs/invariants.md` § Enforcement.
  When an invariant gains a check, update its enforcement row in the same change.
- Justify changes with observable checks, not with "reviewed carefully" or "reasoned step by step" (`docs/invariants.md` § Verification expectation).

## Architecture tests

`docs/invariants.md` § "Enforcement" lists every invariant with its observable check and whether that check exists.
Entries marked `none` are the backlog; when a change relies on such an invariant, add its check.

Priority coverage:

- ARCH-001 (`ehp_sn`/`ehp_research` dependency direction);
- ARCH-002 (canonical component references are unique);
- ARCH-003 (duplicate registrations fail);
- CONFIG-001 / CONFIG-003 (resource requirements declared and reproducibly bound);
- DATA-001 / TASK-001 (substrate/task ownership boundaries), where mechanically testable.

## Contract-oriented testing

Test observable public behavior rather than private implementation layout unless the layout itself is an architectural invariant.
Do not use snapshots as the sole authority for scientific semantics.

## Coupling and responsibility-isolation review

When reviewing a change for coupling or responsibility-isolation defects, grade each finding against the ownership boundaries in `docs/authority.md` and the invariants in `docs/invariants.md`; the invariant names the repo rule, the coupling framework says why it is a defect.

- Coupling: a strong or dynamic connascence form (Name/Type/Identity/Meaning/Algorithm/Position) crossing an ownership boundary — e.g. a shared contract naming a concrete producer/consumer/ task/substrate family/research package; or backend vocabulary leaking into a public surface.
- Responsibility isolation: a lower-authority location redefining semantics owned elsewhere (ARCH-002); an adapter branching on concrete task/model identity or authoring a value the resolved interfaces already determine (ADAPT-001/003); a binding/adapter/CLI layer changing information boundary, truth, target, split, or metric meaning (BIND-001, ADAPT-002, CLI-001).

Report each finding as: location, concept, correct owner, classification, invariant, correction.
Do not modify a higher-authority specification merely to relieve coupling found in a lower-authority one.
If two normative specs disagree or the boundary has no recorded owner and no target architecture has been established, record it in `docs/decisions.md` (DOC-002) rather than correcting it.
When the target architecture is explicitly established, realign the conflicting normative material in place and remove obsolete competing semantics instead of re-logging it (DOC-002/ARCH-015).

## Authority

Invariants and their enforcement state are authoritative in `docs/invariants.md`. This file is procedural and never defines semantics.
