---
title: Open architectural decisions
authority: normative
document_status: specified
---

# Open architectural decisions

This document answers one question: **what is not yet decided?**

`docs/invariants.md` DOC-002 requires conflicting or missing authority to be recorded rather than silently reconciled. This register is where it is recorded.

Entries here are transient. An entry is deleted when the decision is made and the resulting semantics are captured in `docs/authority.md`, `docs/invariants.md`, or the owning specification. This document never becomes the permanent home of a resolved contract.

## Entry format

Each entry states:

- the conflicting or missing claims, with paths;
- the consequence of each interpretation;
- the decision required;
- what must not be done until it is decided.

Identifiers are permanent.
A resolved entry is deleted and its identifier is never reused, so gaps in the sequence are expected and do not indicate a missing record.
