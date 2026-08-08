# Add or review a substrate

Create or review a substrate specification and implementation against the substrate boundary.

Before drafting or coding:

1. establish the reusable task-neutral domain structure;
2. define one logical record;
3. determine whether an existing research-owned shared contract already represents the consumer-facing structure;
4. identify source/generation semantics;
5. identify family-specific identity inputs;
6. define deterministic invariants and validation.

Reject fields or behavior that exist only because of:

- a task query;
- a task-specific goal;
- a task-generated trajectory;
- supervision;
- evaluation;
- model encoding.

If several substrate families need the same consumer-visible structure, evaluate a research-owned shared contract before duplicating semantics.

Do not move the shared contract into the generic framework without an independently demonstrated framework requirement.

After the change, identify affected task consumers, catalogues, READMEs, and tests.
