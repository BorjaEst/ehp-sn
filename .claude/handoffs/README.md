# Implementation handoffs

A handoff is the design → implementation contract between the two agent phases used in this repository:

```text
mentor (design, opus)  →  .claude/handoffs/<name>.md  →  supervisor (implementation, sonnet)
```

`supervisor` has no access to the `mentor` conversation.
The handoff and the authoritative documentation it references are the only channel between the phases.
A constraint that appears in neither does not reach implementation.

## Flow

```text
claude --agent mentor
    /design-handoff <name>        creates .claude/handoffs/<name>.md

claude --agent supervisor
    /implement-handoff <name>     consumes .claude/handoffs/<name>.md
```

`supervisor` must always be launched as the main thread via `claude --agent supervisor`, never spawned as a subagent — its delegation allowlist is enforced only when it runs as the main thread.

`mentor` writes a handoff only when a design discussion has converged on an explicit decision _and_ the necessary information is not already fully represented by authoritative repository documentation.
`supervisor` reads it first, before anything else — followed by the authoritative documentation it references, `CLAUDE.md`, and applicable `.claude/rules/*.md`.

`/design-handoff` never implements.
`/implement-handoff` never redesigns.

## When a handoff may be written

Write one only when all of the following hold:

- the objective is clear;
- every material design decision is accepted, not still under discussion;
- the governing repository authority is identified;
- no unresolved question would materially change the architecture;
- the information is not already fully recoverable from authoritative repository documentation.

If a material decision is still open, report the unresolved decision and what is needed to settle it, and write nothing.

A handoff records an agreed design, not a proposal.

## Naming

One file per design concern:

```text
.claude/handoffs/artifact-manifest-ownership.md
```

The identifier is lowercase kebab-case matching `[a-z0-9][a-z0-9-]*`, and names the design concern rather than a date, ticket, or branch.
Because the identifier becomes a path, both skills reject an identifier containing `/`, `..`, whitespace, or uppercase instead of normalizing it.

## Not tracked

Handoff files are untracked local scratch; `.gitignore` in this directory excludes everything except itself and this README.

Two consequences:

- **Durable decisions must be captured in authoritative documentation before the handoff is written.**
  A handoff cannot be recovered from git history. Anything that must survive the design phase belongs in `docs/authority.md`, `docs/invariants.md`, or the owning specification — the handoff carries only the implementation-facing residue.
- **A missing handoff is a normal case.** On a machine without the named file, `/implement-handoff` reports what is available and stops.
  It does not reconstruct the design.

Captured means committed.
An uncommitted authority edit and the handoff that depends on it can drift apart between sessions, and the implementation phase cannot tell a superseded staged version from a current working-tree one.
Commit the authority change and the handoff together, before the implementation phase begins.

## Structure

```markdown
---
status: agreed
---

# Implementation Handoff

## Objective

## Agreed Design

## Requirements

## Constraints

## Acceptance Criteria

## Relevant Authority

## Known Affected Areas

## Open Questions
```

`status` is the only metadata field:

- `agreed` — design accepted, implementation not complete. Written by `mentor` when the handoff is created.
- `implemented` — implementation landed and its acceptance criteria were met.
  Set at the end of a successful `/implement-handoff` run.
  The file is then historical local scratch, is not authority for anything, and may be deleted at any time.

Do not add a name or identifier field; the identifier is derivable from the filename.

## Rules

- Distinguish clearly between agreed decisions, requirements, assumptions, and unresolved questions — do not blur them together.
- Prefer referencing normative repository documentation (`docs/authority.md`, `docs/invariants.md`, an updated specification) over duplicating it here.
  If the decision is already captured there, point to it instead of restating it.
- Acceptance criteria must make an incorrect implementation detectable.
  Prefer observable properties — required behavior, permitted and forbidden dependency directions, ownership boundaries, expected validation failures, required tests — over unverifiable adjectives.
- This is the implementation-relevant result of the design discussion, not a transcript of it.
- The repository remains the source of truth.
  Neither this file nor agent conversation history may become the authoritative source for project semantics — durable decisions belong in authoritative documentation as part of the same coherent change.
