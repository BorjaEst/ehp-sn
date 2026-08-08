# Update a normative specification

Update the selected normative specification without changing unrelated semantic ownership.

Before editing:

1. identify the requirement motivating the change;
2. identify concepts owned by the selected specification;
3. identify upstream specifications it must obey;
4. identify downstream specifications, code, tests, interfaces, and summaries that may become stale.

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
