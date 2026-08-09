---
title: Identity
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Identity

This document defines identity categories for EHP-SN components, requests, plans, and artifacts.
It is the authoritative home for what constitutes identity and what does not.

## Identity categories

| Category                       | Scope                                                  | Defined by                                                   |
| ------------------------------ | ------------------------------------------------------ | ------------------------------------------------------------ |
| Component identity             | Canonical reference + version                          | [References](references.md)                                  |
| Scientific definition identity | Resolved experiment digest                             | Experiment specification                                     |
| Request identity               | Target + invocation-specific values                    | Operation specification                                      |
| Plan identity                  | Resolved request + bound resources                     | Resolution specification                                     |
| Artifact identity              | Manifest + artifact fingerprint + provenance reference | [Data artifacts](data-artifacts.md) § "Artifact fingerprint" |
| Scientific result identity     | Inputs + analysis version + semantic parameters        | Analysis specification                                       |
| Run identity                   | Every non-resumed invocation                           | Training specification                                       |

## Identity inputs

Identity is determined by canonical semantic values.
The following do not contribute to identity:

- absolute source file paths;
- current working directory;
- CLI token positions;
- original textual spelling;
- frontend source class when effective values are equal;
- unused or shadowed configuration fields;
- diagnostic provenance.

## Equality invariants

- Equal effective semantic values → equal scientific-invocation identity.
- Equal experiments → equal resolved digests.
- Unequal resolved digests → unequal effective scientific definitions.
- Changing only physical placement does not change identity.

## Artifact republishing and composition

| Relationship         | Rule                                                           |
| -------------------- | -------------------------------------------------------------- |
| Republishing         | Preserves the artifact ID; does not create a new identity      |
| Logs and checkpoints | Resources of one training-run artifact; not separate artifacts |

## Analysis-specific identity

Analysis artifacts additionally distinguish a scientific result from its rendered presentation.
This cardinality model is specific to analysis artifacts and does not apply to other artifact kinds (substrate, corpus, training-run, evaluation), whose identity is the general artifact identity defined in "Identity categories" above.

Its authoritative definition, including the `scientific_result_id` / `analysis_artifact_id` formula, is in [Analysis](../interfaces/python/analysis.md) § "Scientific and rendering identity".

## Related documents

- [References](references.md)
- [Digests](digests.md)
- [Artifacts](artifacts.md)
- [Provenance](provenance.md)
