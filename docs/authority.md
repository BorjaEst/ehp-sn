---
title: Documentation and semantic authority
authority: normative
document_status: specified
---

# Documentation and semantic authority

This document defines where EHP-SN concepts are semantically owned and where their normative specifications live.

EHP-SN is specification-first:

```text
normative specification
    defines intended public semantics

implementation
    implements those semantics

tests
    verify observable conformance

interfaces and READMEs
    expose or summarize those semantics
```

Implementation must not silently become a competing semantic authority.

## Package ownership

```text
ehp_research → ehp_sn
```

`ehp_sn` owns reusable framework contracts and services.

`ehp_research` owns concrete scientific definitions and research-owned shared domain contracts.

`ehp_sn` must not depend on `ehp_research`.

## Authority matrix

| Concern | Semantic owner | Normative specification | Implementation / operational surface |
|---|---|---|---|
| Package dependency direction | repository architecture | this document + framework architecture specifications | package metadata, imports, architecture tests |
| Generic Task / Model / Binding contracts | `ehp_sn` | `docs/docs/framework/` and applicable design specifications | `packages/ehp-sn/src/` |
| Generic artifact semantics | `ehp_sn` | `docs/docs/framework/` | `packages/ehp-sn/src/` |
| `DataArtifact` / `SubstrateArtifact` | `ehp_sn` | `docs/docs/framework/data-artifacts.md` | framework artifact implementation |
| `TaskCorpus` | `ehp_sn` | `docs/docs/framework/corpora.md` | framework corpus implementation |
| References, identity, digests, manifests, provenance | `ehp_sn` | applicable framework specifications | framework implementation |
| Resource requirements | `ehp_sn` | `docs/docs/interfaces/configuration/resource-requirements.md` | configuration/resolution implementation |
| Configuration model and resolution | `ehp_sn` | `docs/docs/interfaces/configuration/` | framework configuration implementation |
| Public CLI behavior | `ehp_sn` | `docs/docs/interfaces/cli/` | framework CLI implementation |
| Public Python behavior | `ehp_sn` | `docs/docs/interfaces/python/` | framework public Python implementation |
| Shared research substrate schemas | `ehp_research` | corresponding specification under `docs/docs/research/substrates/` | research implementation |
| Raster topology semantics | `ehp_research` | `raster-topology/v1` specification when added | research substrate/task implementations |
| Observation-field semantics | `ehp_research` | ObsField/shared observation-field specifications | research substrate/task implementations |
| DungeonGen semantics | `ehp_research` | `docs/docs/research/substrates/dungeongen-v1.md` | research substrate implementation |
| Maze-ND semantics | `ehp_research` | `docs/docs/research/substrates/maze-nd-v1.md` | research substrate implementation |
| ObsField semantics | `ehp_research` | `docs/docs/research/substrates/obsfield-v1.md` | research substrate implementation |
| Dagflow semantics | `ehp_research` | `docs/docs/research/substrates/dagflow-v1.md` | research substrate implementation |
| Arena semantics | `ehp_research` | `docs/docs/research/tasks/arena.md` | research task implementation |
| MazeHard semantics | `ehp_research` | `docs/docs/research/tasks/mazehard.md` | research task implementation |
| Routebind semantics | `ehp_research` | `docs/docs/research/tasks/routebind.md` | research task implementation |
| Prospect semantics | `ehp_research` | `docs/docs/research/tasks/prospect.md` | research task implementation |
| Model semantics | `ehp_research` | corresponding research model specification | research model implementation |
| Binding semantics | `ehp_research` | corresponding research binding specification | research binding implementation |
| Experiment-family semantics | `ehp_research` | corresponding research experiment specification | research experiment implementation |
| Package overview | descriptive | package README | N/A |
| Repository overview | descriptive | root README | N/A |

## Conflict resolution

When two statements disagree:

1. identify the concept;
2. identify the semantic owner;
3. identify the normative specification;
4. update lower-authority implementations, interfaces, summaries, or examples to conform.

If two normative specifications both claim authority over the same concept and disagree, do not resolve the conflict implicitly.

Record it as an architectural decision that must be resolved explicitly.

## Ownership versus orchestration

Ownership means defining semantics.

Orchestration means exposing or executing semantics owned elsewhere.

For example:

```text
ehp_research Arena specification
    owns Arena task semantics

ehp-sn tasks CLI
    orchestrates Arena corpus construction

ehp_sn TaskCorpus contract
    owns generic corpus lifecycle/completeness mechanics
```

Do not use CLI presence as evidence of semantic ownership.

## Duplication rule

Normative semantics should have one authoritative home.

Other documents should:

- reference the authority;
- summarize only what is needed locally;
- avoid reproducing complete contracts.

## README rule

READMEs are descriptive projections of the current specification set.

They must not override normative specifications.

## Generated information

Information that can be derived mechanically should not be manually maintained in multiple authoritative-looking locations.

Prefer generated or mechanically validated:

- component reference;
- title;
- kind;
- status;
- maturity;
- semantic owner;
- specification path;
- catalogue membership.
