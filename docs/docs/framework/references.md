---
title: Component and resource references
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Component and resource references

This document defines the canonical reference grammar for EHP-SN components and resources. It is the authoritative home for reference syntax, version semantics, and reference kinds.

## Canonical reference grammar

A canonical reference has the form:

```text
<kind>:<name>/v<N>
```

Where:

- `kind` identifies the component or resource category (`task`, `model`, `input-adapter`, `output-adapter`, `binding`, `experiment`, `artifact`, `requirement`, `analysis`);
- `name` is a unique identifier within the kind namespace and may contain internal path separators (for example, a release coordinate such as `arena-corpus/default`);
- `v<N>` is the specification version for component kinds (`task`, `model`, `input-adapter`, `output-adapter`, `binding`, `experiment`, `analysis`), or the release number for release-coordinate kinds (`artifact`, `requirement`) whose targets are substrates or task corpora.

A `binding` reference denotes a resolved composition — one task, one model, and their configured
`input-adapter`/`output-adapter` pair — rather than an independently specified component; see
[Adapters](adapters/index.md).

Examples:

```text
task:arena/v1
model:tem/v1
input-adapter:RelationalSequenceAdapter
output-adapter:ObservationPredictionAdapter
binding:arena-tem/v1
experiment:arena-tem/v1
artifact:arena-corpus/default/v1
requirement:corpus/arena-training/v1
analysis:memory-diagnostics/v1
```

Two kinds do not fit this grammar and are documented as exceptions rather than forced into it:

- `checkpoint` is not a top-level kind: a checkpoint is a resource scoped under a parent artifact rather than an independently versioned component. See [Resource references](#resource-references).
- An `artifact` reference to a run-identified artifact (a training run, evaluation, or analysis output — for example `artifact:runs/01JXYZ123`) has no `/v<N>` component, because the run is identified by a unique run ID rather than a specification version or release number.
  This is a second `artifact`-reference shape alongside the release-coordinate shape shown above; which shape applies depends on the artifact kind being referenced.

## Version semantics

A version changes when the component's public contract or scientific meaning changes. Supported parameter specialization does not require a new version, but changes the resolved digest.

Component specification versions are separate from package releases, Git revisions, configuration digests, run identifiers, checkpoints, and trained-model registry versions.

## Reference resolution

A reference is resolved by kind-specific resolvers. Resolution produces a typed reference object with:

- canonical string form;
- kind;
- name;
- version;
- optional digest (resource digest or artifact fingerprint, per kind) when available.

Malformed references are rejected at parse time. Unknown references are rejected at resolution time. Unavailable references are resource-validation errors.

## Resource references

Resource references identify manifest-declared resources owned by an artifact, such as `checkpoint:runs/01JXYZ123/best` for a training-run checkpoint. Their namespace and version grammar are defined by the owning artifact kind; for checkpoints, see [Checkpoints](checkpoints.md).

## Fragment references within declarations

A declaration may reference a **named member** of a component by appending a `#` fragment to a component reference.
Each fragment name and its meaning are owned by the referenced component's specification, not re-enumerated here.

For example, an experiment's `[metrics]` table references task-owned metric definitions by task reference plus fragment, in the form:

```text
task:<task>/vN#<metric-id>
```

`<metric-id>` is a task-specification-defined metric identifier (`components/experiment.md` § Field catalogue, `[metrics]`).
The fragment is declaration-local selection syntax; it does not introduce a new top-level reference kind, and it is resolved only in the context of a declaration that references the owning component.

## Logical vs physical identity

A canonical reference is a logical identity. It is portable across processes and machines. Physical paths and storage locations are not logical identities and do not substitute for canonical references.

## Related documents

- [Adapters](adapters/index.md)
- [Compatibility](compatibility.md)
- [Identity](identity.md)
