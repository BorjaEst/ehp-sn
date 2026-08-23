---
title: Identity
authority: normative
document_status: specified
capability_status: partial
api_stability: provisional
---

# Identity

This document defines identity categories for EHP-SN components, requests, plans, and artifacts.
It is the authoritative home for what constitutes identity and what does not.

The ownership chain places this document between resource semantics and resolution:

```text
Resource requirements
        ↓
Identity
        ↓
Configuration resolution
```

[Resource requirements](../interfaces/configuration/resource-requirements.md) defines what a resource requirement and binding is; this document decides which resolved facts are identity-bearing; [Configuration resolution](../interfaces/configuration/resolution.md) applies those identity rules when constructing the immutable plan.

## Identity categories

| Category                       | Scope                                                  | Defined by                                                   |
| ------------------------------ | ------------------------------------------------------ | ------------------------------------------------------------ |
| Component identity             | Canonical reference + version                          | [References](references.md)                                  |
| Scientific definition identity | Resolved experiment digest                             | Experiment specification                                     |
| Request identity               | Target + invocation-specific values                    | Operation specification                                      |
| Plan identity                  | Canonical resolved plan inputs + bound resources       | [Identity specification](#plan-identity)                     |
| Artifact identity              | Manifest + artifact fingerprint + provenance reference | [Data artifacts](data-artifacts.md) § "Artifact fingerprint" |
| Scientific result identity     | Inputs + analysis version + semantic parameters        | Analysis specification                                       |
| Run identity                   | Every non-resumed invocation                           | Training specification                                       |

`Plan identity` is defined by this specification.
Resolution supplies the inputs and computes when identity is applied; it does not define what plan identity means.

## Canonical identity inputs

Identity is determined by canonical semantic values.

Included:

- canonical semantic values of identity-bearing fields;
- normalization rule IDs and derivation rule IDs when changing them could change an effective semantic value.

The following do not contribute to identity:

- absolute source file paths;
- current working directory;
- CLI token positions;
- original textual spelling;
- frontend source class when effective values are equal;
- unused or shadowed configuration fields;
- diagnostic provenance.

## Producer-declared identity inputs for plans

This section records the implemented ownership boundary for plan identity, as demonstrated by substrate planning.

```text
producer (ehp_research)
    declares which family-specific resolved scientific values are identity-bearing

framework (ehp_sn)
    canonicalizes those declared values and combines them according to the generic plan-identity rule
```

The framework neither recognizes nor branches on concrete producer-family identity when interpreting identity inputs.
It receives canonical identity-bearing inputs declared by the producer and incorporates them into the immutable framework plan without inspecting producer configuration types.

Producer-declared scientific inputs form part of plan identity.
Which producer-specific values are identity-bearing is decided by the owning `ehp_research` specification; the framework canonicalizes the declared values without interpreting producer-specific fields.

Bound resources contribute to plan identity according to the identity rule for the operation and artifact in question.
[Resource requirements](../interfaces/configuration/resource-requirements.md) defines what facts a bound resource exposes — requirement reference, selected logical resource reference, immutable version, and verification evidence when available.
This document decides which of those facts are identity-bearing and how they combine into plan identity.

The applicable identity rule must be declared before resolution begins; it is not decided dynamically during resolution.
A plan may be considered identity-complete only when every identity component required by its owning identity rule is available.
`BOUND` is sufficient when the applicable identity rule requires only information available at binding time.
If an identity rule requires evidence available only at `VERIFIED` state, the plan cannot claim that identity to be complete before that evidence exists.

For the currently implemented substrate slice, the owning substrate specification establishes what is identity-sufficient for the plan.
Typically this is an exact logical resource reference plus the producer-declared immutable inputs — including any family-specific revision or fingerprint the producer supplies as identity inputs — without depending on a later storage-integrity digest that exists only after `VERIFIED` validation.

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

## Implementation status

Plan identity is the implemented slice demonstrated by current substrate planning: producer-declared identity inputs are canonicalized and incorporated into the immutable plan.
Broader identity categories, component identity, artifact identity, and integrity semantics on this page are not yet satisfied by code.

## Related documents

- [References](references.md)
- [Digests](digests.md)
- [Artifacts](artifacts.md)
- [Provenance](provenance.md)
- [Resource requirements](../interfaces/configuration/resource-requirements.md)
- [Configuration resolution](../interfaces/configuration/resolution.md)
