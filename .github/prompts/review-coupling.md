---
name: review-coupling
description: "Evaluate and correct coupling and responsibility-isolation violations against repository ownership boundaries."
---

# Review coupling and responsibility isolation

Evaluate the selected specifications and implementation for unnecessary coupling and responsibility-isolation violations, then correct what has one clear owner.

Do not begin by rewriting files.

## Reference frameworks

Grade every finding against a named, external standard, not prose intuition:

- **Coupling — Connascence** (Page-Jones).
  Name the form present: static (Name, Type, Meaning/Convention, Position, Algorithm) or dynamic (Execution Order, Timing, Value, Identity).
  Apply the governing rule as the reproducible test: connascence must weaken, not strengthen, as it crosses an encapsulation boundary.
  A repository boundary from `docs/authority.md` (framework/research, substrate/task, task/model, public/backend, resource selection) is such a boundary — a strong or dynamic form crossing one is the defect, independent of which invariant also names it.
- **Responsibility isolation — Single Responsibility Principle.** Enumerate the reason(s) to change for the component under review.
  More than one independent reason, or a reason that belongs to a different owner in `docs/authority.md`, is the defect.

## Evaluate

1. Identify the concept or components under review and which boundary they sit near: framework/research, substrate/task, task/model, public/backend, or resource selection (`CLAUDE.md` § "Authority first").
2. Resolve semantic ownership for each side of the boundary using `docs/authority.md` § "Authority map".
3. Identify the invariants that boundary must satisfy in `docs/invariants.md` — select only the ones the concept actually touches from ARCH-001..003, DATA-001..006, TASK-001, ADAPT-001..003, BIND-001, CONFIG-001..004, CLI-001..003, ART-001..002.
4. For each candidate finding, classify it under both frameworks above, then tag the repository invariant it also violates (the invariant says which repo rule; the framework says why it is a defect at all):
   - **coupling** — named-family coupling, a shared contract naming a concrete producer, consumer, task, substrate family, or research package (Connascence of Name/Type/Identity crossing a producer-agnostic boundary; DATA-005, `docs/docs/framework/contracts/index.md`); an unmet framework-ownership claim over a shared representation (same authority); reverse dependency pressure (Connascence of Identity/Algorithm crossing the framework/research boundary; ARCH-001, ARCH-003); backend vocabulary leaking into a public surface (Connascence of Meaning crossing the public/backend boundary; CONFIG-002, CONFIG-004, CLI-003);
   - **responsibility isolation** — ownership leakage, a lower-authority location redefining semantics owned elsewhere (a second reason to change introduced from outside; ARCH-002); adapter genericity or parameter-ownership violations, branching on concrete task/model identity or authoring a value the source/target interface already determines (a reason to change borrowed from the task or model owner; ADAPT-001, ADAPT-003); boundary-changing orchestration, a binding/adapter/CLI layer changing information boundary, truth, target, split, or metric meaning instead of orchestrating it (a reason to change that belongs to the task owner, not the orchestrator; BIND-001, ADAPT-002, CLI-001).
5. Report findings as a table:

| Location | Concept | Owner (should be) | Classification (Connascence form / reasons-to-change) | Invariant/authority | Correction |
| -------- | ------- | ----------------- | ----------------------------------------------------- | ------------------- | ---------- |

Do not modify a higher-authority specification merely to relieve coupling found in a lower-authority one.

If two normative specifications disagree, or the boundary has no recorded owner (`docs/authority.md` § "Closure rule"), do not correct that finding — record it in `docs/decisions.md` per its entry format and stop there (DOC-002).

## Correct

For every finding that has one clear owner and no open disagreement:

- apply the smallest coherent change that removes the coupling (`CLAUDE.md` § "Change discipline") — do not introduce a new abstraction, registry, or protocol to do it;
- move or restate the semantics into their owning specification rather than duplicating them;
- keep a shared contract meaningful without naming any concrete producer, consumer, task, substrate family, or research package;
- follow the edit order in `CLAUDE.md` § "Authority first": authority → implementation and tests → interface documentation → READMEs and summaries;
- re-run the checks in `docs/invariants.md` § "Enforcement" relevant to the changed invariant(s) after editing.

## Finish

- Confirm every finding is either corrected or recorded as undecided in `docs/decisions.md`.
- Identify any invariant relied on in this review that is still `manual` or `none` in `docs/invariants.md` § "Enforcement", as a candidate deterministic check under `tests/architecture/` (`.claude/rules/tests.md`).
- Report what changed, what was recorded as undecided, and what was left untouched and why.
