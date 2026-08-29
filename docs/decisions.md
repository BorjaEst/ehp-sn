---
title: Open design register
authority: descriptive
document_status: specified
---

# Open design register

This document answers one question: **what is not yet decided?**

It is an ordinary open-questions register, not a semantic authority.
`docs/invariants.md` DOC-002 requires conflicting or missing authority to be recorded rather than silently reconciled. This register is where that is recorded.

Entries here are transient. An entry is deleted when the decision is made and the resulting semantics are captured in `docs/authority.md`, `docs/invariants.md`, or the owning specification. This document never becomes the permanent home of a resolved contract.

## Entry format

Each entry states:

- the conflicting or missing claims, with paths;
- the consequence of each interpretation;
- the decision required;
- what must not be done until it is decided.

Identifiers are permanent.
A resolved entry is deleted and its identifier is never reused, so gaps in the sequence are expected and do not indicate a missing record.

## DEC-023 — Adapter reference kind: `adapter:` vs `input-adapter:`/`output-adapter:`

**Conflicting claims**

- `docs/docs/framework/references.md` ("Component and resource references", `authority: normative`) declares itself the authoritative home for reference kinds and enumerates the adapter kinds as `input-adapter` and `output-adapter`; it has no `adapter` kind.
- `docs/docs/framework/components/experiment.md` § "Full declaration field catalogue (v1)" (normative) specifies the binding adapter reference as kind `adapter` (`adapter = "adapter:<kind>/v1"`).
- All five authored concrete declarations (`experiments/{arena-tem,arena-tem-t,mazehard-hrm,mazehard-hrm-rl,routebind-hrm}/v1/experiment.toml`) reference adapters with kind `adapter` (for example `adapter:raster-sequence/v1`).

**Consequence of each interpretation**

- If the canonical kind is `adapter`, then `references.md` must add an `adapter` kind (or a binding-scoped adapter reference form) and the resolver accepts `adapter`.
- If the canonical kinds are `input-adapter`/`output-adapter`, then the field catalogue and all five declarations must be realigned to the split kinds, and the resolver validates by kind.

**Decision required**

Choose the canonical adapter reference kind, then realign `references.md`, the experiment field catalogue, and the declaration files in place (`ARCH-015`).

**What must not be done until it is decided**

The resolver must not enforce a single kind enum unilaterally. It currently accepts `adapter`, `input-adapter`, and `output-adapter` and validates the adapter role by side; this is a provisional reconciliation, not a settled contract.

## DEC-024 — Home for non-experiment ARCH-016 design exemplars

**Conflicting / missing claims**

- The existing design-exemplar convention is experiment-attached: `experiments/<name>/vN/design/` holds non-authoritative exemplars that explore candidate framework contracts for a concrete experiment.
- A substrate/framework design exemplar (for example Dagflow or ObsField) is **not** an experiment composition (`ARCH-005`/`ARCH-006`), so placing it under `experiments/` would mislabel it.
- `tests/design_exemplars/substrates/` was adopted in this workstream as a provisional home for such non-experiment exemplars, but no authority or register entry establishes that location as a durable convention. It was a working choice, not a resolved decision.

**Consequence of each interpretation**

- If `tests/design_exemplars/<area>/...` is intended as the durable convention for non-experiment exemplars, it must be recorded as a decision in the owning authority (for example the framework development guide or a research-substrate convention note), so it is a real convention rather than a silent habit.
- If the location is only temporary, it must be treated as provisional and no architectural assumption may be built on the path (for example discovery or scanning must not assume it).

**Decision required**

Decide whether `tests/design_exemplars/<area>/...` is (a) a recorded, durable home for non-experiment ARCH-016 exemplars, or (b) explicitly temporary work-in-progress material.

**What must not be done until it is decided**

No production code and no discovery/scanning may depend on the `tests/design_exemplars/` location as a settled convention. Exemplar content there remains non-authoritative, non-discoverable, and never imported by production `ehp_sn`/`ehp_research` (`ARCH-014`).
