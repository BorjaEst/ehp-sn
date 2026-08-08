# Review an architecture change

Critically review the proposed EHP-SN architecture change.

Establish:

- objective;
- affected domain;
- existing semantic owner;
- existing normative authority;
- constraints;
- affected consumers/components;
- unresolved assumptions.

Then determine:

1. which semantic ownership boundaries change;
2. whether a new abstraction solves a demonstrated reusable requirement;
3. whether the same goal can be achieved with a smaller change;
4. which normative specifications must change;
5. which implementations/tests must change;
6. which lower-authority documents only require synchronization;
7. identity, reproducibility, compatibility, and migration consequences;
8. relevant failure modes.

Check `docs/invariants.md`.

Return:

| Area | Current contract | Proposed change | Evidence/requirement | Risk | Recommendation |
| ---- | ---------------- | --------------- | -------------------- | ---- | -------------- |

Do not approve a framework abstraction solely because multiple current research components happen to share an implementation detail.
