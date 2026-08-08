---
paths:
  - ".claude/agents/*.md"
  - ".claude/skills/*/SKILL.md"
---

# Agent and skill instructions

Agent files define roles. Skill files define procedures. They are composed at runtime, not by reference: a skill is invoked inside whatever session is active, and that session's agent definition is already its system prompt.

## Writing an agent file

An agent file defines what a role owns, what it must not do, when it stops, and when it escalates. It must remain correct when no skill is invoked.

An agent file must not name a skill or make its behavior conditional on one existing. Express a trigger as a condition — "only on explicit user request" — not as a command name.

An agent **may** name a sibling agent when delimiting ownership — stating what belongs to another role is how a boundary is expressed.

## Writing a skill file

A skill file defines one procedure: preconditions, ordered steps, failure handling, result. It must remain correct in any session permitted to perform the operation.

A skill file must not name an agent, instruct the session to read an agent file, or assume which agent is active. Say "under your own operating policy".

## Shared rules

Neither an agent file nor a skill file may name the other.

The `agent:` frontmatter field with `context: fork` is a mechanical binding rather than prose coupling, and is permitted where a skill genuinely must run as a specific subagent.

Command names, agent launch commands, and the sequence connecting phases belong in the document describing the workflow — such as `.claude/handoffs/README.md` — not in role definitions or skill procedures.

Do not create a second definition of a role, routing policy, or artifact convention.
