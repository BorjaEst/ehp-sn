# Design handoffs

This document owns the design-handoff mechanism: where handoffs live, how they are named, their structure, their status values, when a handoff may be written, the acceptance-criteria quality bar ("Rules"), and how the implementation phase is entered ("Flow").

It is procedural only and never defines domain semantics (see `docs/invariants.md` DOC-007).
Semantics live in repository authority (`docs/authority.md`, `docs/invariants.md`, and the owning normative specifications).

## Location

A handoff is a single Markdown file at:

```text
.github/handoffs/<identifier>.md
```

`README.md` is reserved for this document and is never a handoff.

Handoff files are tracked in git, so design decisions must still be persisted in their correct authoritative location — `docs/authority.md`, `docs/invariants.md`, or the owning specification — before a handoff is written.
A handoff is the implementation-facing residue of decisions that are already captured, not a substitute for capturing them.
`CAPTURE` must precede `HANDOFF`.

## Identifier form

- Each handoff has a short, lowercase, kebab-case identifier: `[a-z0-9][a-z0-9-]*`.
- The identifier names the design concern the handoff records.
- The identifier becomes a path, so it must not be normalized after it is chosen and must match the form above exactly.
- If the identifier does not match the form, stop and report.
  Do not guess a near match.

## Structure

A handoff is an implementation contract.
It constrains implementation; it does not plan implementation.

It is **not**:

- a conversation transcript;
- an investigation log;
- a literature review;
- a copy of repository documentation;
- an implementation roadmap;
- a worker-decomposition plan.

Include only what implementation requires:

- objective;
- agreed design;
- governing normative authority;
- semantic requirements;
- implementation constraints;
- known semantic impact surface;
- material external constraints;
- acceptance criteria;
- relevant assumptions;
- unresolved implementation questions.

Every material implementation constraint must be traceable to one of:

- repository normative authority;
- applicable external normative requirement;
- explicitly accepted repository design decision.

Do **not** include:

- implementation phases;
- worker assignments;
- agent-routing decisions;
- parallelization decisions;
- coding order;
- file-edit sequences;
- test execution phases;
- integration sequencing;
- implementation dependency graphs,

unless a particular ordering or constraint is itself part of the agreed semantic contract.
Include a rejected alternative only when the implementer could otherwise reasonably recreate it.
Do not copy external research into a handoff after its architectural consequence has been captured in repository authority.

## Frontmatter and status

Each handoff carries `status` frontmatter.
The status values are:

- `agreed` — the design is agreed and ready to implement.
  Written by the `design-handoff` prompt.
- `implemented` — implementation is complete and its acceptance criteria are met.
  Set by the `implement-handoff` prompt.
  Do **not** set this after a partial, blocked, or unreviewed implementation; report what remains and leave the status as `agreed`.

A `status: agreed` handoff is never overwritten without explicit confirmation.

## When a handoff may be written

A handoff may be written only when:

1. **It is explicitly requested.** A handoff is never created or updated on an agent's own initiative, even when a design decision feels fully resolved — report readiness and wait to be asked.
2. **The design is resolved.** If a material decision remains unresolved, write nothing.
   Report the unresolved decision, why it blocks implementation, the evidence-backed recommendation if one exists, and exactly what is still needed.
3. **Durable decisions are captured first.** Every durable semantic decision is persisted in its correct authoritative location — `docs/authority.md`, `docs/invariants.md`, or the owning specification — before the handoff is written, per the `copilot-instructions.md` § "Architectural source of truth" and § "Before changing architectural code or documentation".
   The handoff carries only the implementation-facing residue, so `CAPTURE` precedes `HANDOFF`.
4. **It is self-contained.** The handoff must be sufficient for a separate implementation session that has no access to the originating conversation: it must identify the governing contract, what must change, what must not change, the implementation scope, and how the result will be judged, without reconstructing the design discussion.

## Rules

The handoff's acceptance criteria are the quality bar implementation is judged against:

- Acceptance criteria state **observable conditions** the implementation must satisfy.
- An incorrect implementation must be **detectable** — not judged against unverifiable adjectives such as `clean`, `robust`, or `best practice`.
- Acceptance criteria do not prescribe the executor's execution strategy.

## Flow

The design phase is closed by the `design-handoff` prompt, which writes the handoff with `status: agreed`.
The implementation phase is entered by the `implement-handoff` prompt, which loads the handoff, validates it, loads authority, and implements it; on completion it sets `status: implemented`.

The `supervisor` agent must be launched as the main thread, never spawned as a subagent.
If the user names a handoff, `supervisor` reads it first and treats its content as the agreed objective.
There is no default handoff; if none is named, the request itself is the objective, and authority is established via `copilot-instructions.md` § "Architectural source of truth".

## References

- Design phase entry / handoff writing: `.github/prompts/design-handoff.md`
- Implementation phase entry / handoff consumption: `.github/prompts/implement-handoff.md`
- Orchestration: `.github/agents/supervisor.md`
- Handoff policy: `.github/agents/mentor.md` § "HANDOFF"
