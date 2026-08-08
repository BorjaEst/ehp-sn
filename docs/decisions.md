---
title: Open architectural decisions
authority: normative
status: specified
---

# Open architectural decisions

This document answers one question: **what is not yet decided?**

`docs/invariants.md` DOC-002 requires conflicting or missing authority to be recorded rather than silently reconciled. This register is where it is recorded.

Entries here are transient. An entry is deleted when the decision is made and the resulting semantics are captured in `docs/authority.md`, `docs/invariants.md`, or the owning specification. This document never becomes the permanent home of a resolved contract.

## Entry format

Each entry states:

- the conflicting or missing claims, with paths;
- the consequence of each interpretation;
- the decision required;
- what must not be done until it is decided.

Identifiers are permanent. A resolved entry is deleted and its identifier is never reused, so gaps in the sequence are expected and do not indicate a missing record.

## DEC-001 — Unowned published documentation directories

These directories exist under `docs/docs/` but are not covered by a specification root in `docs/authority.md` § "Authority map". Their semantic owner is undecided.

| Directory                    | Note                                                              |
| ---------------------------- | ----------------------------------------------------------------- |
| `docs/docs/architecture/`    | successor to the removed `docs/docs/design/` not confirmed        |
| `docs/docs/concepts/`        | may span `ehp_sn` and `ehp_research`                              |
| `docs/docs/decisions/`       | may span `ehp_sn` and `ehp_research`; distinct from this register |
| `docs/docs/guides/`          | presumed descriptive                                              |
| `docs/docs/getting-started/` | presumed descriptive                                              |

**Decision required:** for each directory, either add a specification root to the authority map with an owner, or mark it `authority: descriptive`.

**Until decided:** the closure rule in `docs/authority.md` applies. Do not treat these paths as normative for any concept owned elsewhere, and do not assert their ownership from a README, an `_index.md`, or `.claude/rules/` path scoping.

## DEC-002 — ObsField / OpenField specification identity

- `packages/ehp-research/src/substrates/openfield/` exists in implementation.
- `docs/docs/research/substrates/obsfield-v1.md` exists and is normative.
- `docs/docs/development/data-layout.md`, `docs/docs/research/substrates/_index.md`, and `docs/docs/research/tasks/arena-v1.md` link to `openfield-v1.md`, which does not exist.

**Consequence of each interpretation:** either the substrate is ObsField and three documents carry a wrong reference, or it is OpenField and both the specification filename and the implementation-facing references are wrong.

**Decision required:** the substrate's canonical name.

**Until decided:** do not rename either side.

## DEC-003 — Duplicate Arena specification

`docs/docs/research/tasks/` contains both `arena.md` and `arena-v1.md`. Both declare `authority: normative` and both declare `title: Arena v1`.

Two normative specifications for one concept violates `docs/invariants.md` ARCH-002.

**Decision required:** which file is authoritative.

**Until decided:** do not add references to either file, and do not treat either as settled authority for Arena semantics.

**Resolution:** remove or demote the non-authoritative file; a demoted file must set `authority: descriptive` and must not restate the contract.

## DEC-005 — "One logical task record" ownership constraint

- `.claude/rules/tasks.md` § "Task ownership" (prior to synchronization with DOC-007) asserted that a task owns "one logical task record."
- `docs/invariants.md` TASK-001 enumerates what a task owns (scientific problem meaning, information regime, parent-role semantics, task-owned composition, case/query/episode generation, oracle truth, targets, validity, task-level metrics) but does not state a "one logical task record" constraint.
- `docs/docs/research/tasks/_index.md` § "Task-document contract" asks every task specification to answer "What does one logical task record represent?" as the first of six required questions. This presupposes "one logical task record" as vocabulary an author must define, but it is a documentation prompt, not a normative clause: it does not use **must**/**must not** to assert that a task is constrained to exactly one such record, and it does not state a cardinality or uniqueness requirement. It asks authors to define what their record represents, not to limit themselves to a single record. This passage is judged insufficient to establish the claim as settled semantics.

**Consequence of each interpretation:** if a task record is constrained to be exactly one logical record, task implementations and corpus layouts that split a task's owned information across multiple independently-identified records would violate the constraint; if no such constraint exists, that structural question is open and current or future implementations may split task-owned information across multiple records without violating TASK-001.

**Decision required:** whether TASK-001 should be extended with a "one logical task record" constraint, or whether this is not a repository-level invariant at all.

**Until decided:** do not treat "a task owns exactly one logical task record" as settled authority. Do not reject or require an implementation on the basis of this claim alone.

## DEC-006 — Research registration contract beyond duplicate resolution

- `.claude/rules/research.md` § "Registration and discovery" (prior to synchronization with DOC-007) asserted that registration must: use canonical references; be deterministic; avoid import-order-dependent semantics; reject conflicting duplicate canonical registrations; and avoid expensive scientific execution during registration.
- `docs/invariants.md` ARCH-003 covers only "duplicate canonical registrations must fail rather than depend on import order" — the duplicate-resolution case, not general import-order independence for all registration behavior.
- `docs/docs/research/_index.md` is empty (0 lines) and no other specification under a root in `docs/authority.md` § "Authority map" states that registration must use canonical references, must be deterministic in general, must avoid import-order dependence beyond resolving duplicates, or must avoid expensive scientific execution during registration.

**Consequence of each interpretation:** if these properties are intended as binding constraints on research registration, an implementation that is non-deterministic, import-order-sensitive outside duplicate handling, reference-informal, or that performs expensive scientific work at registration time would violate them; if they are not repository-level invariants, such implementations are not currently non-conformant on this basis alone, and the properties remain design guidance rather than settled authority.

**Decision required:** whether `docs/invariants.md` ARCH-003 (or a new invariant) should be extended to state these registration properties as normative, and if so, their exact wording and observable checks.

**Until decided:** do not treat "registration must use canonical references / be deterministic / avoid import-order dependence beyond duplicate resolution / avoid expensive scientific execution" as settled authority beyond what ARCH-003 already states. Do not reject or require a registration implementation on the basis of these properties alone.
