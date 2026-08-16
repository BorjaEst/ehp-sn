---
name: review-doc-consistency
description: "Review documentation consistency as one specification system."
---

# Review documentation consistency

Review the selected documentation as one specification system.

Do not begin by rewriting files.

1. Identify the concepts discussed by each affected file.
2. Resolve the semantic owner and normative authority using `docs/authority.md`.
3. Identify upstream specifications.
4. Identify downstream specifications, implementations, tests, and summaries.
5. Compare actual claims.

Classify each relevant finding using the vocabulary defined in `.claude/rules/documentation.md` § "Conflict classification".

For every issue provide:

| File | Claim | Authority | Evidence of conflict | Required change | Priority |
| ---- | ----- | --------- | -------------------- | --------------- | -------- |

Do not modify a higher-authority specification merely to make it agree with a README or overview.

If two authoritative specifications disagree, mark the issue as an unresolved architecture decision.

Check at minimum:

- package dependency and ownership;
- substrate/task/model/binding boundaries;
- resource requirements and exact resource binding;
- artifact and corpus semantics;
- CLI vocabulary and syntax;
- configuration semantics;
- component references;
- status and maturity;
- examples and quick starts;
- table content and structure (DOC-009).

Finish by identifying deterministic checks that could prevent recurrence.
