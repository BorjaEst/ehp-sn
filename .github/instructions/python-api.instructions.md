---
description: "Use when working on the EHP-SN Python API: public interface, CLI/Python equivalence, or ownership boundary of the framework surface."
applyTo: "docs/docs/interfaces/python/**/*.md, packages/ehp-sn/src/**/*.py, packages/ehp-sn/tests/**/*.py"
---

# Python API instructions

The public `ehp_sn` Python interface exposes the same framework semantics as the CLI through direct calls rather than command invocation.

## Ownership boundary

`docs/authority.md` § "Authority map" assigns "Public Python behavior" to `ehp_sn`, with specification root `docs/docs/interfaces/python/`.
Consult that specification root for what the public Python surface defines; do not re-enumerate it here.

The CLI-001 orchestration boundary applies equally to the Python surface: it exposes framework and research semantics and does not become their owner merely because it is the call site.

The generic Python interface resolves experiments through canonical references (`ExperimentRef.parse` + `resolve_experiment`).
It does not import concrete package-owned experiment factories.

## CLI/Python equivalence

CONFIG-004 governs CLI/Python semantic equivalence.
Consult it, and `docs/docs/interfaces/python/index.md` § "Python and CLI equivalence", rather than re-deriving the convergence requirements here.

## Configuration boundary

Public Python configuration must resolve through the same EHP-SN-owned semantic model as the CLI.
`configuration.instructions.md` governs the resolution model and the backend boundary; consult it rather than restating them here.

## Internal ownership boundary

ARCH-002 and `docs/authority.md` § "Authority map" govern this: a semantic contract has one normative owner, and the Python surface must not become a second normative home for semantics owned elsewhere.
