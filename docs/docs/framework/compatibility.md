---
title: Compatibility
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Compatibility

This document defines component compatibility declarations, support levels, and maturity classifications. It is the authoritative home for task–model compatibility semantics.

## Support levels

A binding declares exact supported task–model combinations:

```yaml
task: task:routebind/v1
model: model:hrm/v2
support: supported
compatibility_maturity: declared
```

Support is either:

| Support       | Meaning                                             |
| ------------- | --------------------------------------------------- |
| `supported`   | Accepted for framework use at the recorded maturity |
| `unsupported` | Explicitly considered and rejected                  |

No declaration means the combination is unavailable for framework use. It does not imply scientific impossibility.

## Compatibility maturity

`compatibility_maturity` describes one task–model(–binding) pair's compatibility, distinct from either component's own document or capability maturity:

| `compatibility_maturity` | Meaning                                              |
| ------------------------ | ---------------------------------------------------- |
| `declared`               | Support is asserted by the binding specification     |
| `implemented`            | Construction and basic execution exist               |
| `validated`              | Conformance and scientific validation evidence exist |
| `reference`              | Used in a reference reproduction                     |

This is a per-pair dimension, not the maturity of the task or model component individually.
A component's own catalogue maturity is declared where that component is catalogued (for example, `docs/docs/research/tasks/index.md` for tasks), not here.

## Compatibility validation

Compatibility is validated at experiment construction time. Incompatible combinations are rejected before any runtime resources are allocated.

## Related documents

- [References](references.md)
- [Identity](identity.md)
