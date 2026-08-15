---
title: Open architectural decisions
authority: normative
document_status: specified
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

## DEC-006 — Research registration contract beyond duplicate resolution

- `.claude/rules/research.md` § "Registration and discovery" (prior to synchronization with DOC-007) asserted that registration must: use canonical references; be deterministic; avoid import-order-dependent semantics; reject conflicting duplicate canonical registrations; and avoid expensive scientific execution during registration.
- `docs/invariants.md` ARCH-003 covers only "duplicate canonical registrations must fail rather than depend on import order" — the duplicate-resolution case, not general import-order independence for all registration behavior.
- `docs/docs/research/index.md` states only that model, binding, and experiment-family specifications will be added to this section as they are written, and no specification under a root in `docs/authority.md` § "Authority map" states that registration must use canonical references, must be deterministic in general, must avoid import-order dependence beyond resolving duplicates, or must avoid expensive scientific execution during registration.

**Consequence of each interpretation:** if these properties are intended as binding constraints on research registration, an implementation that is non-deterministic, import-order-sensitive outside duplicate handling, reference-informal, or that performs expensive scientific work at registration time would violate them; if they are not repository-level invariants, such implementations are not currently non-conformant on this basis alone, and the properties remain design guidance rather than settled authority.

**Decision required:** whether `docs/invariants.md` ARCH-003 (or a new invariant) should be extended to state these registration properties as normative, and if so, their exact wording and observable checks.

**Until decided:** do not treat "registration must use canonical references / be deterministic / avoid import-order dependence beyond duplicate resolution / avoid expensive scientific execution" as settled authority beyond what ARCH-003 already states. Do not reject or require a registration implementation on the basis of these properties alone.

## DEC-013 — Whether `experiments/` is tracked in version control

- `docs/authority.md` § "Authority map" lists `experiments/` as a specification root for research model, binding, and experiment-family semantics.
- `experiments/arena-tem/v1/plan.md` (formerly `README.md`; renamed because DOC-001 forbids a README carrying `authority: normative`, applied without exemption for specification-root READMEs) is the authoritative plan for the Arena–TEM reproduction asset.
- The `experiments/` directory is untracked, so nothing under it is recoverable from version control.

**Consequence of each interpretation:** if `experiments/` stays untracked, a document declared as a specification root's normative content is not actually reproducible or recoverable, undercutting the point of it being normative; if it is tracked, ordinary git workflow applies to it like any other specification root.

**Decision required:** whether `experiments/` should be added to version control.

**Until decided:** do not treat content under `experiments/` as recoverable authority, and do not run any enforcement check that assumes it is tracked.

## DEC-022 — No canonical field for `--hardware-profile`'s distributed-launch semantics

- `docs/docs/interfaces/index.md` and `docs/invariants.md` CONFIG-004 now require that an interface-specific convenience such as `--hardware-profile` resolve into the same framework-owned canonical request/configuration fields the other interface would use, and must not introduce semantics that exist on only one interface.
- `docs/docs/interfaces/cli/train.md` § "Options" states that `--hardware-profile` supplies execution defaults including `device` and `precision` (which are canonical `RuntimeConfiguration` fields per `docs/docs/interfaces/python/training.md` and `conventions.md`), but justifies its CLI-only, training-only scope by citing "distributed launch, process topology, and environment-specific resource coordination" — properties with no canonical request/configuration field defined anywhere under `docs/docs/interfaces/`.
- `docs/docs/interfaces/configuration/resolution.md` § "Runtime `auto` resolution" defines `Distributed: Forbidden unless an explicit distributed policy is supplied`, but does not define what that policy's canonical field path is.

**Consequence of each interpretation:** if a canonical field for distributed/process-topology settings is presumed to exist, `train.md` currently under-specifies it; if no such field exists yet, `--hardware-profile`'s distributed-launch and process-topology behavior is CLI-only semantic state, which the newly stated CONFIG-004 scope forbids.

**Decision required:** the canonical request/configuration field(s) for distributed strategy, process topology, and environment-specific resource coordination, or an explicit statement that `--hardware-profile` must not affect them until such fields exist.

**Until decided:** `--hardware-profile` must not be relied on for any effect beyond the `device`/`precision`-equivalent fields it shares with the direct runtime options.

