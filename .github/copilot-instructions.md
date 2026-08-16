# GitHub Copilot instructions

These instructions tell Copilot how to work with the EHP-SN repository's authorities. They are
procedural only and never define domain semantics (see `docs/invariants.md` DOC-007).

## Architectural source of truth

The single source of truth for where semantics live and what must always hold is:

- `docs/authority.md` — the authority map (which semantic area is owned and specified where).
- `docs/invariants.md` — the repository-wide non-negotiable architectural rules.
- The normative specification that `docs/authority.md` identifies for the concept at hand.

`docs/docs/architecture/ownership.md` is an explanatory walkthrough of the ownership model. It is
descriptive, not authoritative.

## Before changing architectural code or documentation

1. Locate the authority: find the concept's semantic owner and specification root in
   `docs/authority.md`.
2. Classify ownership: decide whether the concept is generic framework machinery (`ehp_sn`),
   reusable scientific meaning (`ehp_research`), or concrete experiment composition
   (`experiments/`). Apply the placement algorithm in `docs/docs/architecture/ownership.md`.
3. Inspect dependency direction: `ehp_research → ehp_sn`; `ehp_sn` must not reference
   `ehp_research`.
4. Inspect tests, imports, and examples: search before editing, and again after, for stale
   competing references.
5. Detect missing contracts: do not invent serialization, discovery, or catalogue formats when
   the framework contract is missing; report the gap.

## Canonical ownership summary

This is a convenience summary only, not a second specification. Prefer `docs/authority.md` and
`docs/invariants.md` when they apply.

```text
ehp_sn        = reusable framework (contracts, adapters, orchestration)
ehp_research  = reusable scientific building blocks
experiments/  = concrete scientific compositions
```

## Migration behavior

When the user has explicitly established a target architecture, conflicting normative material is
a migration target, not independent authority to preserve. Update the authoritative specification
in place and remove obsolete competing semantics rather than adding a parallel normative or
decision layer.
