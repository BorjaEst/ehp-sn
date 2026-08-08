# EHP-SN repository instructions

Specification-first monorepo, two packages: `ehp_research → ehp_sn`.
`ehp_sn` must not depend on `ehp_research` (`docs/invariants.md` ARCH-001).

## Authority first

Before changing architecture, public interfaces, scientific semantics, or documentation:

1. name the concept being changed;
2. find its semantic owner and specification root in `docs/authority.md`;
3. check the invariants it touches in `docs/invariants.md`;
4. check `docs/decisions.md` — do not build on a question recorded there as undecided;
5. identify downstream code, tests, interfaces, and summaries that become stale.

Never resolve disagreeing normative specifications by guessing. Record the conflict in
`docs/decisions.md` and report the decision required (DOC-002).

## Change discipline

Prefer the smallest coherent change that satisfies a demonstrated requirement.
Do not add abstractions, registries, protocols, or framework mechanisms without one.

Ownership boundaries — framework/research, substrate/task, task/model, public/backend,
resource selection — are normative and live in `docs/invariants.md` and `docs/authority.md`.
Consult them before proposing a design that crosses one. The matching `.claude/rules/*.md`
are procedural: they cite those boundaries and never define them (DOC-007).

When an authoritative contract changes, change in this order:
authority → implementation and tests → interface documentation → READMEs and summaries.
Lower-authority documents summarize; they never redefine.

## Verification

Justify a change with observable checks, not with "reviewed carefully", "best practices",
or "reasoned step by step" (`docs/invariants.md` § Verification expectation, § Enforcement).
