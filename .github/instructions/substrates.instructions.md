---
description: "Use when working on scientific substrates: reusable task-neutral domain structure, excluded semantics, or substrate identity."
applyTo: "docs/docs/research/substrates/**/*.md, packages/ehp-research/src/substrates/**/*.py, packages/ehp-research/tests/substrates/**/*.py, tests/architecture/**/*data*.py, tests/integration/**/*data*.py"
---

# Substrate instructions

Substrates are research-owned reusable, task-neutral domain structures (`docs/authority.md` § "Authority map"; specification root `docs/docs/research/substrates/`).

## Excluded semantics

DATA-001 and DATA-002 govern what a substrate must not define: information that exists only because a task poses a problem is task-owned, not substrate-owned.

Diagnostic question (applying DATA-001):

> Would this information still have meaning if no downstream task existed?

If not, it normally does not belong to the substrate.

## Shared research contracts

When several research substrate producers and task consumers require the same task-facing structure, first check `docs/docs/framework/contracts/index.md` § "Registered contracts" for an existing framework contract — a shared structure does not become research-owned merely because research components currently produce and consume it (DATA-005).
Only a structure with no fitting framework contract, and no demonstrated framework-generic requirement, stays research-owned.

## Identity independence

DATA-002 governs substrate identity independence, including its examples.
Consult it rather than re-enumerating its examples here.

Diagnostic check before adding a field to a substrate's identity computation: would that field's value change, or would it stop being meaningful, if a different downstream task consumed the substrate instead — or if no downstream task existed at all? If so, it is task composition leaking into substrate identity, not an intrinsic property of the substrate, and it does not belong in the identity computation.
