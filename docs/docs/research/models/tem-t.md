---
title: TEM-t
authority: normative
document_status: draft
capability_status: planned
api_stability: provisional
---

# TEM-t

## Normative summary

TEM-t is the Transformer reformulation of TEM used in EHP-SN.

It preserves the separation between relational structure and sensory/content information, but realizes associative retrieval through Transformer-style attention over prior experience.

Its defining computation is:

```text
relation-dependent structural state
        +
sensory/content state
        ↓
attention query
        ↓
eligible prior key/value memory
        ↓
retrieved associative content
```

TEM-t owns the relation-dependent structural state, attention-memory construction and retrieval, and its native prediction and trace outputs.

## 1. Model definition

TEM-t uses relation-dependent latent structural state rather than ordinary sequence position.

Core variables are:

| Symbol | Meaning                                      |
| ------ | -------------------------------------------- |
| `x_t`  | sensory/content representation               |
| `g_t`  | relation-dependent structural representation |
| `q_t`  | attention query for the current step         |
| `K_<t` | eligible prior memory keys                   |
| `V_<t` | eligible prior memory values                 |
| `m_t`  | retrieved associative representation         |

The structural state evolves from prior model state and relation input:

```text
g_(t-1), relation_t
        ↓
relational update
        ↓
g_t
```

`g_t` is not absolute sequence index and is not a decoded physical coordinate.

TEM-t is distinct from TEM because associative memory and retrieval are implemented through attention over prior experience rather than the original TEM memory mechanism.

## 2. Architecture

```text
sensory_id ─→ sensory pathway ─→ x_t ────────────┐
                                                  │
relation_id → relational update ─→ g_t ──────────┤
                                                  ↓
                                             query q_t
                                                  ↓
                                 prior key/value memory
                                                  ↓
                                             attention
                                                  ↓
                                               m_t
                                                  ↓
                                      sensory prediction
```

### Relational structural state

The relation-dependent structural representation is model-owned.

Replacing it with ordinary absolute positional encoding changes the model.

### Attention memory

TEM-t uses previous valid experience as associative key/value memory.

For the current prediction step:

- attention is restricted to the model's eligible prior experience;
- reset starts a new memory scope;
- masked/padded positions are not eligible memory entries;
- current-step sensory information must not become retrievable through memory before a prediction role that is intended to test recall from prior experience;
- after the current-step computation, the experience may be inserted into memory for subsequent steps according to the adopted TEM-t schedule.

These temporal rules are part of the model rather than the binding.

## 3. Native interface

### Inputs

TEM-t consumes:

| Role            | Meaning                                                 |
| --------------- | ------------------------------------------------------- |
| `sensory_id`    | current categorical sensory/content identity            |
| `relation_id`   | relation producing the current step                     |
| `reset`         | initializes relational state and attention-memory scope |
| `sequence_mask` | optional validity mask                                  |

Categorical embeddings belong to TEM-t when these identifiers are native inputs.

### Outputs

The stable task-facing model output is the declared sensory-prediction role.

Model-native observables may expose:

- structural state `g_t`;
- sensory/content state;
- retrieved associative representation `m_t`;
- attention weights.

Prediction outputs must state their timing and conditioning explicitly.

## 4. State and computation

TEM-t maintains:

```text
relational structural state g
    recurrent across sequence steps

attention key/value memory
    contains eligible prior experience within the current memory scope

learned parameters
    persist across checkpoints/runs
```

A reset initializes both structural state and sequence-scoped attention memory.

One model step follows this semantic order:

1. apply reset when required;
2. encode sensory and relation identifiers;
3. update `g_t`;
4. construct the current attention query;
5. construct/select eligible prior memory keys and values;
6. retrieve associative content through attention;
7. produce the declared sensory prediction;
8. insert/update the current experience for use by later steps.

If a prediction pathway intentionally includes current sensory evidence, that pathway must be separately named rather than silently changing the causal memory rule above.

## 5. Model parameters

Model-owned parameters include:

- sensory and relation vocabulary capacities;
- structural representation width;
- Transformer/model width;
- attention-head count;
- attention-layer count;
- feed-forward dimensions;
- relational-transition architecture;
- native memory/sequence capacity where fixed.

Training schedule, optimizer, dataset, batch size, runtime device, and output placement are not model parameters.

## 6. Observables

Stable model-native observables are limited to scientifically meaningful states:

- structural representation `g_t`;
- sensory/content representation;
- attention weights;
- retrieved associative representation `m_t`;
- declared sensory prediction.

Raw query/key/value tensors are implementation diagnostics unless a later analysis contract explicitly requires them.

Each standardized observable must define timing and semantic axes.

## 7. Conformance

A conforming TEM-t implementation must satisfy:

- structural state is relation-dependent and model-internal;
- adapters do not construct `g_t`;
- attention retrieval uses only the declared eligible memory scope;
- reset prevents access to prior sequence memory;
- a recall prediction does not leak current-step sensory information through premature memory insertion;
- attention and memory construction remain model-owned;
- the model emits its declared sensory-prediction role without privileged task information.

## 8. Boundaries and related specifications

Bindings translate task semantics into the native sensory/relation sequence interface and map the declared sensory prediction back into task prediction semantics.

They must not construct relational state, attention memory, or associative retrieval.

Experiments own training/evaluation protocols and resource selection.

Relevant neighboring documents include:

- TEM;
- sequence adapters/bindings;
- TEM-t experiments and analyses.

## References

- Whittington, J. C. R., McCaffary, D., Bakermans, J. J. W., & Behrens, T. E. J. _Relating transformers to models and neural representations of the hippocampal formation_.
