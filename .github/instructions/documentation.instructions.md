---
description: "Use when writing or editing documentation: normative claims, READMEs, summaries, or doc-consistency review."
applyTo: "docs/**, README.md, packages/*/README.md, experiments/**/README.md"
---

# Documentation instructions

## Preserve

- Do not duplicate normative semantics.
  Each kind of statement has exactly one authoritative home.
- READMEs summarize and orient; they introduce no new normative semantics (`DOC-001`).
- The authority map points; invariants constrain; normative domain documents define.
- No README-defined architecture that disagrees with `docs/authority.md` or `docs/invariants.md` (ARCH-015).

## Roles

- `docs/authority.md`: map — where each semantic area is owned and specified.
- `docs/invariants.md`: repository-wide cross-cutting rules.
- Normative domain specs: the actual semantics of each concept.
- READMEs / summaries: orientation, examples, links.

## Reviewing documentation as one system

When reviewing documentation consistency: resolve the concept, its owner and normative authority (`docs/authority.md`), its upstream and downstream specifications, then compare actual claims.
Classify each finding as `consistent`, `stale`, `contradictory`, `underspecified`, or `missing authority`.
For every non-consistent finding state the claim, the authority, the evidence of mismatch, why it matters, and which file should change.
Do not modify a higher-authority specification merely to make it agree with a README or overview.
If two authoritative specs disagree and no target architecture has been established, record the conflict in `docs/decisions.md` as unresolved (DOC-002).
When the target architecture is explicitly established, realign the conflicting normative material in place and remove obsolete competing semantics instead of re-logging it (DOC-002/ARCH-015).

## Before changing a normative claim

1. Identify the concept; 2. identify its owner; 3. identify its normative specification;
2. identify documents that summarize or depend on it; 5. distinguish a semantic change from a synchronization change.

Do not create a second normative definition of an existing concept (`docs/invariants.md` DOC-006/ARCH-014).
Reference authoritative contracts rather than reproducing them when a summary suffices.

This file is procedural and never defines semantics.
