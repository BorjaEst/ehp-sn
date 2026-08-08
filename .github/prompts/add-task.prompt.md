# Add or review a task

Create or review a task specification and implementation.

Define:

1. scientific purpose and supported claim;
2. logical task record;
3. public, target, privileged, and withheld information;
4. required parent roles and capabilities;
5. task-owned composition;
6. case/query/episode generation;
7. oracle/reference truth;
8. target semantics;
9. split and leakage semantics;
10. determinism and identity-relevant generation inputs;
11. validation;
12. task metrics;
13. binding boundary.

Do not encode exact deployment/workspace parent artifact choices into task semantics.

Represent exact parent selection through configuration-resolved resource bindings.

Do not introduce model-native tensor or token semantics into the task unless they are genuinely part of the scientific problem.

After the change, identify affected corpora, bindings, experiments, CLI/configuration docs, READMEs, and tests.
