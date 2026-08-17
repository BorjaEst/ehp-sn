---
name: design-handoff
description: "Close out the current design discussion and write the design to implementation handoff."
disable-model-invocation: true
argument-hint: "[handoff-name]"
arguments: handoff
---

# Prepare the design handoff

Close out the current design discussion and write the handoff that carries it into implementation.

Use only the decisions, evidence, and open issues already established in this conversation.
Do not reconstruct the discussion from scratch, and do not investigate new questions here.

## Handoff identifier

The requested identifier is `$handoff`.

- If it is empty, derive a lowercase kebab-case identifier naming the design concern decided in this conversation, and confirm it with the user before writing anything.
- If it does not match `[a-z0-9][a-z0-9-]*`, stop and report. Do not normalize it — the identifier becomes a path.
- The target file is `.github/handoffs/<identifier>.md`.
- If that file already exists, report its current `status` and confirm whether to overwrite it or use a new identifier. Never overwrite a `status: agreed` handoff without confirmation.

## Procedure

1. Apply the readiness test in `.github/handoffs/README.md` § "When a handoff may be written".
2. If a material decision remains unresolved, write nothing.
   Report the unresolved decision, why it blocks implementation, the evidence-backed recommendation if one exists, and exactly what is still needed.
   Stop there.
3. If ready, persist every durable semantic decision in its correct authoritative location first — `docs/authority.md`, `docs/invariants.md`, or the owning specification — per `copilot-instructions.md` § "Architectural source of truth" and § "Before changing architectural code or documentation".
   A durable decision left only in a handoff is not established authority, so this ordering is what prevents design loss. The handoff carries only the implementation-facing residue.
4. Then write the handoff file per `.github/handoffs/README.md`, with `status: agreed` frontmatter.
5. Verify the handoff is sufficient for a separate implementation session that has no access to this conversation: it must identify the governing contract, what must change, what must not change, the implementation scope, and how the result will be judged, without reconstructing the design discussion.
6. Report the design being handed off, the handoff identifier and path, the authoritative files changed, and any implementation-relevant issue that remains open.

This skill closes the design phase. It does not implement, and it does not enter the implementation phase — `.github/handoffs/README.md` § "Flow" describes how that phase is entered.
