---
name: update-specification
description: "Update a normative specification without changing unrelated semantic ownership."
---

# Update a normative specification

Update the selected normative specification without changing unrelated semantic ownership.

Before editing, identify the requirement motivating the change, then follow `CLAUDE.md` § "Authority first" and `.claude/rules/documentation.md` § "Before changing a claim" to identify the concept, its owner and normative specification, the upstream specifications it must obey, and the downstream specifications, code, tests, interfaces, and summaries that may become stale.

During editing:

- change only semantics owned by this specification;
- reference upstream generic contracts instead of copying them;
- preserve `docs/invariants.md`;
- distinguish semantic requirements from implementation choices;
- define observable validation conditions;
- explicitly record unresolved issues rather than inventing answers.

After editing:

1. verify internal consistency;
2. verify relevant repository invariants;
3. identify implementation/tests requiring change;
4. identify downstream documentation requiring synchronization;
5. identify any new missing authority exposed by the change.
