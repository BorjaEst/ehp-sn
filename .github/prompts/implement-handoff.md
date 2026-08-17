---
name: implement-handoff
description: "Load an agreed design handoff and open the implementation phase for it."
disable-model-invocation: true
argument-hint: "[handoff-name]"
arguments: handoff
---

# Implement a design handoff

Open the implementation phase for an already-agreed design.

This skill consumes a design. It does not produce one. If the handoff is missing, invalid, incomplete, or in conflict with current repository authority, stop and return the issue to the design phase — do not complete the design here.

## 1. Resolve

The requested identifier is `$handoff`. The handoff file is `.github/handoffs/<identifier>.md`.

- If the identifier is empty, list `.github/handoffs/*.md` excluding `README.md`, with each file's `status`, and ask which one to implement.
- If the identifier does not match `[a-z0-9][a-z0-9-]*`, stop and report.
- If the file does not exist, list the available identifiers and stop. Do not guess a near match, and do not reconstruct the design from repository state — if no handoff exists for the concern, that is a normal case and a new design phase is required.
- If its `status` is already `implemented`, say so and ask whether to proceed.

## 2. Validate

Read the handoff and check it against `.github/handoffs/README.md` — § "Structure", § "When a handoff may be written", and § "Rules":

- the required sections are present;
- the objective and agreed design are stated as decisions, not options;
- every referenced authority path resolves;
- acceptance criteria are observable — an incorrect implementation would be detectable, rather than judged against unverifiable adjectives such as clean, robust, or best practice;
- no open question would materially change what gets built.

## 3. Escalate instead of repairing

If validation fails, or the handoff contradicts current repository authority, stop and report:

- what is missing or contradictory;
- why it blocks implementation;
- the decision the design phase must make.

Do not redesign, do not fill a gap in the agreed design, and do not reinterpret architecture.

## 4. Load authority

Then read, in order:

1. the authoritative repository documentation the handoff references;
2. `.github/copilot-instructions.md`;
3. applicable `.github/instructions/*.instructions.md` for the paths in scope.

Apply `copilot-instructions.md` § "Architectural source of truth" for anything the handoff leaves to implementation judgment.

## 5. Report before starting

State the handoff identifier, the objective, the governing authority, and the acceptance criteria the result will be judged against.

Then implement it under your own operating policy, which this skill neither supplies nor overrides.

## 6. Mark the handoff implemented

When implementation is complete and its acceptance criteria are met, set the handoff's `status: implemented`.

Do not set it after a partial, blocked, or unreviewed implementation. Report what remains instead, leaving the status as `agreed`.
