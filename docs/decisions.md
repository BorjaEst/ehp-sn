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

## DEC-018 — No specification exists for the integrated EHP model

- `docs/authority.md` § "Authority map" assigns "Research model, binding, and experiment-family semantics" to `ehp_research` with specification roots `docs/docs/research/` and `experiments/`.
- `model:hrm/v1` (`docs/docs/research/models/hrm.md`) is written and catalogued under `docs/docs/research/models/`. `docs/docs/research/bindings/` (which formerly held `binding:mazehard-hrm/v1` as an independently specified research binding) has been retired: `docs/docs/framework/adapters/index.md` now defines the generic, framework-owned `InputAdapter`/`OutputAdapter` contracts, `docs/docs/research/tasks/mazehard.md` § 14 illustrates MazeHard's concrete adapter configuration, and the resolved `task:maze-hard/v1` × `model:hrm/v1` binding composition belongs to the experiment definition rather than to a standalone research binding document. This established the location and document-contract pattern for this specification-root pair.
- `model:tem/v1` (`docs/docs/research/models/tem.md`), `model:tem-t/v1` (`tem-t.md`), and `model:hrm-rl/v1` (`hrm-rl.md`) are now likewise written and catalogued, following the same pattern. `binding:arena-tem/v1` is grounded by the existing `experiment:arena-tem/v1` composition (Python factory `arena_tem_v1`, referenced throughout `docs/docs/interfaces/python/`), which predates the model specification but is no longer a forward reference to an unwritten model now that `tem.md` exists. This resolves the TEM portion of what this entry originally covered.
- No specification exists yet for an integrated EHP model. `packages/ehp-research/README.md` (lines 45, 140, 142) still describes "integrated EHP model" families and "Routebind–EHP" bindings as an intended, planned part of the research programme. The previous version of `docs/docs/research/models/index.md` listed `EHP` in its catalogue as "Planned, not yet written"; the current catalogue (TEM, TEM-t, HRM, HRM-rl) omits an EHP row entirely.
- No document currently presents an `model:ehp/v1`-shaped reference as a current example, so DOC-004 is not presently violated by this gap — this entry tracks a roadmap/catalogue-completeness question, not an observed inconsistency.

**Consequence of each interpretation:** if EHP is still an intended future model, `docs/docs/research/models/index.md`'s catalogue is incomplete relative to what the package README already commits to; if EHP has been deliberately dropped from the roadmap, `packages/ehp-research/README.md` should be updated to stop describing it as planned.

**Decision required:** whether `docs/docs/research/models/index.md` should re-list `EHP` as a planned/not-yet-written catalogue entry (matching `packages/ehp-research/README.md`), or whether the README's EHP references should be revised to reflect a changed roadmap.

**Until decided:** do not treat "integrated EHP model" as a catalogued or specified component, and do not remove the EHP references from `packages/ehp-research/README.md` on the assumption that the roadmap has changed.

## DEC-022 — No canonical field for `--hardware-profile`'s distributed-launch semantics

- `docs/docs/interfaces/index.md` and `docs/invariants.md` CONFIG-004 now require that an interface-specific convenience such as `--hardware-profile` resolve into the same framework-owned canonical request/configuration fields the other interface would use, and must not introduce semantics that exist on only one interface.
- `docs/docs/interfaces/cli/train.md` § "Options" states that `--hardware-profile` supplies execution defaults including `device` and `precision` (which are canonical `RuntimeConfiguration` fields per `docs/docs/interfaces/python/training.md` and `conventions.md`), but justifies its CLI-only, training-only scope by citing "distributed launch, process topology, and environment-specific resource coordination" — properties with no canonical request/configuration field defined anywhere under `docs/docs/interfaces/`.
- `docs/docs/interfaces/configuration/resolution.md` § "Runtime `auto` resolution" defines `Distributed: Forbidden unless an explicit distributed policy is supplied`, but does not define what that policy's canonical field path is.

**Consequence of each interpretation:** if a canonical field for distributed/process-topology settings is presumed to exist, `train.md` currently under-specifies it; if no such field exists yet, `--hardware-profile`'s distributed-launch and process-topology behavior is CLI-only semantic state, which the newly stated CONFIG-004 scope forbids.

**Decision required:** the canonical request/configuration field(s) for distributed strategy, process topology, and environment-specific resource coordination, or an explicit statement that `--hardware-profile` must not affect them until such fields exist.

**Until decided:** `--hardware-profile` must not be relied on for any effect beyond the `device`/`precision`-equivalent fields it shares with the direct runtime options.

## DEC-023 — `experiment:mazehard-hrm/v1` and `experiment:routebind-hrm/v1` are used as examples with no backing definition

- `docs/docs/interfaces/cli/index.md` § "Component and resource references" lists `experiment:mazehard-hrm/v1` and `experiment:routebind-hrm/v1` in its canonical-reference catalogue, alongside `experiment:arena-tem/v1`.
- `experiment:arena-tem/v1` is backed by a concrete Python factory (`arena_tem_v1`, `docs/docs/interfaces/python/experiments.md`) and is used consistently as a worked example across `docs/docs/interfaces/cli/` and `docs/docs/interfaces/python/`.
- `experiment:mazehard-hrm/v1` and `experiment:routebind-hrm/v1` each appear exactly once in the entire `docs/docs/` tree, at those two lines only. Neither has a Python factory, an experiment definition, or any other citation.
- The underlying components exist and are specified independently: `docs/docs/research/tasks/mazehard.md` and `routebind.md` § 14 ("Binding boundary") already illustrate concrete adapter configuration against HRM, and `docs/docs/research/models/hrm.md` is written. Only the composed `experiment:`/`binding:` identity for each pair is undefined.
- `docs/invariants.md` DOC-004 requires documented examples to use current component references.
- This is the same shape as the `goaltrace`/`goaltrace-hrm`/`seqmaze` placeholder problem this register previously tracked and resolved (see DEC-018 history), but was never itself tracked.

**Consequence of each interpretation:** if `mazehard-hrm`/`routebind-hrm` name intended experiment compositions, `cli/index.md` is an example of unwritten specifications and DOC-004 cannot be satisfied; if they are placeholders, `cli/index.md` presents placeholder identifiers as current component references with the same visual weight as the fully-grounded `arena-tem` example.

**Decision required:** whether `experiment:mazehard-hrm/v1` and `experiment:routebind-hrm/v1` are written now — each requiring only a resolved binding composition and an experiment definition, since the task, model, and adapter configuration pattern already exist — or the two references in `cli/index.md` are marked non-current or removed.

**Until decided:** do not treat `experiment:mazehard-hrm/v1` or `experiment:routebind-hrm/v1` as a catalogued component.
