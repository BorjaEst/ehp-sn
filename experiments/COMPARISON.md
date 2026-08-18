# Cross-example comparison — design exemplars (Phase C/D output)

> **PROVISIONAL DESIGN EXEMPLAR SYNTHESIS.** This matrix aggregates the four per-exemplar
> `design/matrix.md` rows. It is **non-authoritative** and **non-discoverable**; it exists to
> derive framework contracts per `ARCH-016`, and must not be treated as a contract or stability
> promise (`ARCH-014`). It feeds the framework `Binding`/`ExperimentDefinition`/adapter review.

## Fixed dimensions × four exemplars

| Dimension         | arena-tem/v1                | arena-tem-t/v1              | mazehard-hrm/v1                  | mazehard-hrm-rl/v1               |
| ----------------- | --------------------------- | --------------------------- | -------------------------------- | -------------------------------- |
| Task/model        | arena × tem                 | arena × tem-t (model swap)  | mazehard × hrm                   | mazehard × hrm-rl                |
| Input adaptation  | relational-seq (obs/action) | relational-seq (same task)  | raster-seq (S=P=900)             | raster-seq (S=P=900) + reset     |
| Output adaptation | observation-prediction      | observation-prediction      | raster-prediction (schema_slots) | raster-prediction (schema_slots) |
| Pipeline/steps    | 1 in + 1 out                | 1 in + 1 out                | 1 in + decoder + 1 out           | 1 in + decoder + 1 out + ctrl    |
| Objectives        | 1 (supervised CE)           | 1 (supervised CE)           | 2 (CE + ACT halting)             | 2 (CE + RL control)              |
| Controllers       | none                        | none                        | none (supervised halt)           | **reusable deliberation ctrl**   |
| Protocols         | supervised replay           | supervised replay           | supervised CE + halting          | hybrid: supervised + RL          |
| Resources         | arena corpus (dg/obsfield)  | arena corpus                | mazehard corpus (maze-nd)        | mazehard corpus (maze-nd)        |
| Evaluation        | A_obs^rev + 3 pathways      | revisit metrics + its split | exact-solution + token + any-opt | same + halt/value diagnostics    |
| CLI UX            | ref-by-name; binding hidden | identical                   | identical + show needs decoder   | identical; RL invisible          |
| Python UX         | resolve + train             | same                        | same                             | same, hides controller           |
| Variation point   | baseline                    | model substitutability      | raster + decoder + 2nd objective | controller + RL objective        |

## Verdicts on the draft abstractions (evidence-based, pending framework review)

### `Binding` (components/binding.md, BIND-001)

**Verdict: does NOT survive unchanged — split/revised is required.**

Evidence:

- arena-tem and arena-tem-t both fit `Binding = task + model + input_adapter + output_adapter`
  with **zero shape change** — the substitutability axis supports the single-adapter shape.
- mazehard-hrm required a **binding-owned `decoder`** role (HRM decoding is binding-owned;
  TEM/TEM-t keep decoding in-model). `schema_slots → decoder → [5-class]` is a transformation the
  single-adapter shape must be able to express.
- mazehard-hrm-rl requires a **controller** that is not an input or output transformation at
  all: it reads `q_values`/`state_value` and drives `halt`/`continue`, forming an **interaction
  loop around the model**, not a `model output → task output` mapping. This is direct
  counter-evidence to BIND-001, and it points to a concern **orthogonal** to adaptation rather
  than to a wider output pipeline.

**The exemplars expose three distinct kinds of integration, not one:**

```text
input adaptation         task → model-native input
prediction adaptation    model-native representation → task prediction
control interaction      model-native control outputs → deliberation action (halt/continue)
```

The HRM-RL controller is an interaction loop:

```text
HRM-RL
    q_values / state_value
          ↓
deliberation controller
          ↓
halt / continue
          ↓
resume model or terminate
```

It is **not** an output adapter in the same sense as a decoder. We therefore resist the candidate
that flattens `output_pipeline = decoder + controller + output_adapter`, because it conflates
semantically different concepts merely because they execute after some model computation. The
evidence suggests `Binding` may need to distinguish at least:

```text
representation integration      task ↔ model
execution/control composition   model ↔ controller
learning composition            predictions/control ↔ objectives
```

That is more significant than changing `OutputAdapter` into `tuple[OutputStep, ...]`, and it raises
whether `Binding` itself currently carries too many concerns.

Framework-review candidates (to discriminate in review, not chosen here):

```text
A. Minimal Binding
   Binding = task, model, input_adapter, output_adapter
   Controller remains ExperimentDefinition-owned.
   Decoder must be representable as an OutputAdapter or generic adapter composition.

B. Composed representation Binding
   Binding = task, model, input_pipeline, output_pipeline
   Controller remains a separate ExperimentDefinition component.

C. Explicit prediction integration
   Binding = task, model, input_adapter, prediction_adapter, optional integration_module
   Controller remains orthogonal.
```

We currently reject any candidate that places the HRM-RL controller inside the output pipeline,
unless further exemplars demonstrate that control really is an adapter concern.

**Decoder finding.** "Binding-owned decoder" is semantically correct, but the evidence does not
yet prove `decoder` must be a first-class framework concept. If the decoder is a trainable generic
transformation (`schema_slots → Linear(D, 5) → task logits`), it may be better represented as a
configured `OutputAdapter` that can own trainable parameters — an implementation role inside an
adapter, not another top-level `Binding` field. The evidence proves only that
"`OutputAdapter` = simple stateless mapping" is too weak, **not** that a separate decoder
abstraction is required.

### `ExperimentDefinition` (components/experiment.md)

**Verdict: the unit's component split is sound but its axis boundaries need revision. The
`ExperimentDefinition` should hold an experiment-local composition of tasks, models, bindings,
_controllers_, objectives, protocols, metrics, and analyses — with a controller axis kept
orthogonal to Binding.**

Evidence:

- The `objectives` tuple held 1 objective (arena) and 2 objectives (mazehard-hrm ACT halting)
  fine; mazehard-hrm-rl adds a third (RL deliberation). Several candidate exemplar shapes
  over-fit this by adding distinct `rl_objective`/`act_objective` fields.
- The experiment correctly does NOT own device/seeds/runtime (train.toml keeps those in
  `request.*`) — consistent with the plan's ARCH-013 distinction.

**Objective composition should be a homogeneous, ordered collection with typed per-objective
contracts, not one field per paradigm.** Prefer:

```python
objectives = (
    route_prediction_objective,     # supervised CE
    deliberation_control_objective, # RL TD
)
```

where each objective has an explicit contract stating its required model/binding roles, required
predictions, required targets/signals, training-phase applicability, and loss/output semantics.
Then supervised CE, ACT supervision, and RL TD remain different reusable scientific components
without forcing the `ExperimentDefinition` shape to enumerate every learning paradigm. Avoid
`objective` / `rl_objective` / `act_objective` field proliferation — it does not scale.

**Ownership wording.** The concrete **Arena–TEM `ExperimentDefinition` declaration** is
`experiments/arena-tem/v1/experiment.toml` (canonical concrete declaration). The **resolved
`ExperimentDefinition` runtime object** is framework-produced during resolution and is not itself
a repository-owned artifact:

```text
declared composition (experiment.toml)
        ↓
ehp_sn resolution
        ↓
resolved immutable ExperimentDefinition object
```

### Controller

**Verdict: control is orthogonal to adaptation and does not belong inside `Binding`'s
input/output pipeline.** The exemplars support a separate experiment-owned composition axis:

```text
Binding     "How can this task and model exchange representations?"
Controller  "How is iterative model computation externally governed?"
Objective   "How are the resulting predictions/control quantities learned?"
Experiment  "Which of these pieces are composed for this scientific experiment?"
```

This separation fits the exemplars. MazeHard–HRM has no external controller (ACT stays
model-owned); MazeHard–HRM-RL adds the reusable deliberation controller with the task/model
interface held nearly fixed — precisely the variation that isolates the control axis.

### Input/Output adapter split (adapters/index.md)

**Verdict: the input/output direction split survives. The exemplars show that output adaptation
must support trainable or multi-stage decoding semantics; they do not yet establish whether this
requires multiple adapters, an explicit pipeline abstraction, or a more capable single
`OutputAdapter`.**

Evidence:

- The IN direction is uniformly one adapter (relational-seq or raster-seq) across all four.
- The OUT direction is where the shape diverges: single scored output (arena), decoder-before-
  render (mazehard), and route + orthogonal controller interaction (hrm-rl).
- The controlled-deliberation case points to a **controller axis orthogonal to adaptation**, not
  evidence that the output adapter must become a pipeline. Whether `decoder` is a trainable role
  inside one capable `OutputAdapter` (see Binding verdict) is an open framework-review question.

## Reusable vs experiment-local findings

The reusable/experiment-local split follows the established three-layer rule:

```text
generic interface-level transformation      → ehp_sn
scientific component with standalone meaning → ehp_research
concrete task↔model correspondence          → experiments/
```

- **`ehp_sn` (reusable framework):** generic `InputAdapter`/`OutputAdapter` abstractions, generic
  adapter transformation primitives, and generic pipeline/composition mechanics if they are
  required. Adapter primitives belong here, **not** in `ehp_research` — they are framework
  mechanics whose meaning is independent of EHP research.
- **`ehp_research` (reusable scientific building blocks):** tasks, models, objectives, controllers,
  metrics, analyses, and the schematic objectives/controller invoked by the exemplars
  (e.g. deliberation control, route prediction).
- **`experiments/<exp>/vN/` (concrete composition):** the concrete Binding, concrete
  adapter/decoder selection and configuration, controller selection/configuration, objective
  composition, and the concrete `ExperimentDefinition` declared in `experiment.toml`.

The central result: the controller and RL objective read as **reusable scientific building blocks**
(`hrm-rl.md` § 8 lists them as neighboring research documents), composed here — NOT
experiment-local inventions, and NOT part of `ehp_sn`'s framework core either.

The resolved `ExperimentDefinition` **object** is framework-produced during resolution and is not
itself an experiment-owned artifact; only its authored scientific semantics belong to
`experiments/<exp>/vN/`.

## The strongest result and the framework-review framing

The matrix's most informative result is the controlled variation across the four:

```text
Arena–TEM / TEM-t      demonstrate substitution (same task family, model swapped)
MazeHard–HRM           demonstrates representation adaptation beyond trivial mapping
MazeHard–HRM-RL        demonstrates that control is orthogonal to representation adaptation
```

This reframes the framework-review question. It is not "single adapter or pipeline?" It is:

> **What are the independent axes of experiment composition?**

From these four exemplars the current hypothesis is:

```text
ExperimentDefinition
│
├── task
├── model
│
├── binding
│   ├── input adaptation
│   └── prediction/output adaptation
│
├── controller(s)
├── objective(s)
│
├── training protocol
├── evaluation protocol
│
├── metrics
├── analyses/traces
└── resource requirements
```

This is notably cleaner than placing the controller inside `Binding`. Under this reading each
component answers one question:

Each question maps to one component:

```text
Binding      "How can this task and model exchange representations?"
Controller   "How is iterative model computation externally governed?"
Objective    "How are the resulting predictions/control quantities learned?"
Experiment   "Which of these pieces are composed for this scientific experiment?"
```

For MazeHard–HRM versus MazeHard–HRM-RL, this keeps the task/model interface nearly fixed while
varying control and learning semantics:

| Component  | MazeHard–HRM                      | MazeHard–HRM-RL                         |
| ---------- | --------------------------------- | --------------------------------------- |
| task       | MazeHard                          | MazeHard                                |
| model      | HRM                               | HRM-RL                                  |
| binding    | raster input; HRM→route decoder   | same raster input; HRM-RL→route decoder |
| controller | none externally (ACT model-owned) | reusable deliberation controller        |
| objectives | route CE + ACT supervision        | route CE + RL deliberation objective    |

That comparison is extremely informative for isolating the control axis.

## Four questions the framework review should answer

1. Can an `OutputAdapter` be stateful/trainable and contain a decoder?
2. Does a `Binding` need pipelines, or can one sufficiently expressive adapter encapsulate
   composition?
3. Is controller composition orthogonal to `Binding`? (The current evidence strongly says yes.)
4. Can heterogeneous objectives live in one ordered collection with typed semantics, or does the
   framework need separate supervised/RL objective axes? (The evidence prefers the typed
   collection: `objectives[]`, each with an explicit contract.)

## Next steps (NOT executed here — gated on this evidence)

1. Framework review of `Binding`/`ExperimentDefinition`/adapter contracts against these verdicts.
2. Revise the draft specs (`components/binding.md`, `components/experiment.md`, `adapters/index.md`)
   and BIND-001 if the verdicts hold.
3. Specify the canonical experiment discovery/serialization/resolution contract.
4. Convert these exemplars into canonical implementations.

These steps are deliberately out of scope for the exemplar phase (`ARCH-014`, `ARCH-016`).
