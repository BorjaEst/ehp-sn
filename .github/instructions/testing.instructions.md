---
description: "Use when writing or reviewing tests, architecture checks, or coupling/responsibility-isolation review."
applyTo: "tests/**/*.py, packages/*/tests/**/*.py, .github/workflows/**"
---

# EHP-SN testing instructions

## 0. Purpose

These instructions define how tests must be generated, placed, named, scoped, marked, and reviewed in EHP-SN.

The goal is not to maximize test count. The goal is to preserve the EHP-SN architecture:

```text
ehp_sn
    reusable framework

ehp_research
    reusable scientific components

experiments/<experiment>/vN
    concrete scientific compositions

root tests/
    repository-wide architecture, distribution, integration, and qualification
```

Every generated test must answer four questions before code is written:

```text
Who owns the invariant?
What size is the test?
What public or private surface is being tested?
What evidence does the test provide?
```

A test without a clear answer to those questions should not be generated.

---

## 1. Core rule

Test location follows semantic ownership.

```text
packages/ehp-sn/tests
    framework-owned semantics only

packages/ehp-research/tests
    reusable scientific component semantics only

experiments/<experiment>/vN/tests
    concrete experiment composition semantics only

root tests/
    repository architecture, distribution, public integration, and qualification only
```

Do not place a test where the implementation happens to be convenient. Place it where the semantic invariant is owned.

---

## 2. Ownership placement rules

### 2.1 Framework tests: `packages/ehp-sn/tests`

Use this location for tests of generic framework mechanics.

Allowed examples:

```text
contracts
artifacts
configuration
discovery
execution
planning
generic figures
generic Python interfaces
generic CLI behavior
generic task/model/binding abstractions
generic resource requirements
generic identity/provenance/digest behavior
```

Framework tests may test concepts such as:

```text
FigureSpec
FigureInputContract
FigureRequest
FigureSelection
ResolvedFigureSelection
FigureProjection
FigureComposition
RenderContext
RenderedFigure
FigureSink
FigureSchedule

DataArtifact
SubstrateArtifact
TaskCorpus
ExecutionPlan
ResourceRequirement
ParsedOperationConfiguration
ResolvedRequest
```

Framework tests must not import or depend on:

```text
ehp_research
experiments
Arena
MazeHard
Routebind
Prospect
TEM
TEM-t
HRM
HRM-rl
DungeonGen
Maze-ND
ObsField
Dagflow
```

If a framework test needs one of those concrete scientific concepts, the test is misplaced.

Use toy framework fixtures instead:

```text
ToyFigureSpec
ToyFigureData
ToyResolvedFigureSource
ToyTaskContract
ToyModelContract
ToyArtifact
ToyLogicalRecord
ToyRenderBackend
```

Toy fixtures must have no EHP research semantics.

---

### 2.2 Research tests: `packages/ehp-research/tests`

Use this location for reusable scientific components whose meaning remains coherent independently of one concrete experiment.

Allowed examples:

```text
substrates/dagflow
substrates/dungeongen
substrates/maze_nd
substrates/obsfield

tasks/arena
tasks/mazehard
tasks/prospect
tasks/routebind

models/tem
models/tem_t
models/hrm
models/hrm_rl

figures
analyses
metrics
registration
```

Research tests may import `ehp_sn` and `ehp_research`.

Research tests must not test concrete task-model experiment compositions such as:

```text
Arena + TEM
Arena + TEM-t
MazeHard + HRM
MazeHard + HRM-rl
Routebind + HRM
```

Those belong under `experiments/<experiment>/vN/tests`.

Research figure tests may test reusable scientific figures such as:

```text
Arena task overview
MazeHard task overview
Dagflow graph overview
HPC place-field summary
MEC grid summary
HRM latent-state dynamics
```

Research figure tests must not test experiment-local joint figures such as:

```text
Arena–TEM memory-pathway comparison
MazeHard–HRM reasoning-cycle diagnostic
MazeHard–HRM-RL deliberation-value comparison
Routebind–HRM semantic-spatial reasoning view
```

---

### 2.3 Experiment tests: `experiments/<experiment>/vN/tests`

Use this location for concrete scientific compositions.

Allowed examples:

```text
experiments/arena-tem/v1/tests
experiments/arena-tem-t/v1/tests
experiments/mazehard-hrm/v1/tests
experiments/mazehard-hrm-rl/v1/tests
experiments/routebind-hrm/v1/tests
```

Experiment tests may test:

```text
resolved experiment definition
concrete task-model binding
experiment-owned adapter configuration
experiment-specific objective composition
experiment-specific protocol composition
experiment-specific metric selection
experiment-specific trace selection
experiment-local figures
experiment-local resource requirements
experiment-local configuration defaults
```

Experiment tests may import:

```text
ehp_sn
ehp_research
the local experiment package/module/specification
```

Experiment tests must not redefine generic framework rules. They must assert that the concrete experiment uses those rules correctly.

---

### 2.4 Root tests: `tests/`

Use root tests only for repository-wide concerns.

Allowed folders:

```text
tests/architecture
tests/distribution
tests/integration
tests/qualification
tests/support
```

Root tests should normally use public surfaces only:

```text
CLI
public Python API
installed package imports
entry points
artifact manifests
configured workspaces
committed temporary artifacts
```

Root integration tests must not import private implementation modules.

Wrong:

```python
from ehp_sn.figures._internal import ...
from ehp_research.tasks.arena._builder import ...
```

Correct:

```python
from ehp_sn import train, evaluate
subprocess.run(["ehp-sn", "data", "inspect", ...])
```

---

## 3. Target directory structure

Use this structure as the target layout:

```text
packages/
  ehp-sn/
    src/
    tests/
      contracts/
        domains/
        topology/
        observations/
        graphs/
      artifacts/
      configuration/
      discovery/
      execution/
      figures/
      interfaces/
        cli/
        python/
      planning/
      support/

  ehp-research/
    src/
    tests/
      substrates/
        dagflow/
        dungeongen/
        maze_nd/
        obsfield/
      tasks/
        arena/
        mazehard/
        prospect/
        routebind/
      models/
        tem/
        tem_t/
        hrm/
        hrm_rl/
      figures/
      analyses/
      metrics/
      registration/
      support/

experiments/
  arena-tem/
    v1/
      plan.md
      tests/
        test_definition.py
        test_binding.py
        test_figures.py
        test_protocols.py

  arena-tem-t/
    v1/
      tests/

  mazehard-hrm/
    v1/
      tests/
        test_definition.py
        test_binding.py
        test_reasoning_figure.py
        test_evaluation_protocol.py

  mazehard-hrm-rl/
    v1/
      tests/

  routebind-hrm/
    v1/
      tests/

tests/
  architecture/
  distribution/
  integration/
  qualification/
  support/
```

The exact file names may vary, but ownership must not.

---

## 4. Test size model

Every test must be classified as one of:

```text
small
medium
large
```

This classification controls what the test may do.

### 4.1 Small tests

A small test checks local behavior.

Allowed:

```text
single module
single package boundary
pure functions
small in-memory objects
temporary files only when the filesystem is part of the invariant
deterministic toy data
```

Forbidden:

```text
subprocess
network
real repository data/artifacts/logs/models writes
cross-package end-to-end flows
expensive model training
large generated datasets
```

Examples:

```text
raster-topology rejects invalid passability length
FigureSelection tie-breaks by stable ID
RenderContext rejects scientific selection fields
configuration parser rejects duplicate explicit values
```

### 4.2 Medium tests

A medium test crosses one architectural boundary.

Allowed examples:

```text
configuration file -> resolved request
component registry -> resolved figure catalogue
artifact resolver -> resolved figure source
public Python API -> internal framework service
research component -> framework contract conformance
CLI command -> parser/service boundary
```

Medium tests may use `tmp_path` workspaces.

Medium tests may use subprocess only when the CLI itself is the surface under test.

### 4.3 Large tests

A large test exercises an end-to-end or qualification path.

Allowed examples:

```text
data build -> tasks build -> inspect figure
train plan -> evaluate plan -> analyze plan
analysis artifact -> report rendering
built wheel -> import -> entry point load
full figure projection -> render -> sink path
```

Large tests must be few, public-surface only, and isolated in temporary workspaces.

Large tests should normally live in:

```text
tests/integration
tests/qualification
```

---

## 5. Test purpose model

Each test should have one dominant purpose.

Allowed purposes:

```text
contract
conformance
composition
interface
regression
qualification
architecture
```

### 5.1 Contract test

Validates a framework semantic contract.

Example:

```text
categorical-field/v1 rejects observation IDs outside vocabulary bounds
```

Location:

```text
packages/ehp-sn/tests/contracts
```

### 5.2 Conformance test

Validates one concrete implementation against a contract.

Example:

```text
Dagflow single-terminal records conform to simple-digraph/v1 and expose exactly one terminal
```

Location:

```text
packages/ehp-research/tests/substrates/dagflow
```

### 5.3 Composition test

Validates a concrete experiment composition.

Example:

```text
MazeHard-HRM binding exposes public maze/start/goal information but not oracle route truth
```

Location:

```text
experiments/mazehard-hrm/v1/tests
```

### 5.4 Interface test

Validates CLI or public Python API behavior.

Example:

```text
ehp-sn data inspect reports ambiguous compatible figures instead of selecting first registered figure
```

Location depends on scope:

```text
packages/ehp-sn/tests/interfaces/cli
tests/integration
```

### 5.5 Regression test

Locks a stable public output shape or previously fixed bug.

Allowed only for stable or accepted behavior.

Examples:

```text
resolved configuration diagnostic category
manifest resource descriptor
normalized SVG structure for a stable report figure
```

Do not create golden files for exploratory, provisional, or backend-incidental behavior.

### 5.6 Qualification test

Validates acceptance-level invariants.

Examples:

```text
same semantic inputs produce same artifact identity
same figure projection inputs produce same projection identity
render-only changes do not change projection identity
committed artifact cannot be overwritten
CLI and Python equivalent inputs resolve to equivalent plans
```

Location:

```text
tests/qualification
```

### 5.7 Architecture test

Validates repository-level boundaries mechanically.

Examples:

```text
ehp_sn does not import ehp_research
ehp_sn does not import experiments
ehp_research.registration does not register experiment-local figures
root integration tests do not import private modules
tests do not write into repository data/artifacts/logs/models
```

Location:

```text
tests/architecture
```

---

## 6. Required pytest configuration

The project should use strict markers and importlib import mode.

Recommended baseline:

```toml
[tool.pytest.ini_options]
addopts = [
  "--import-mode=importlib",
  "--strict-markers",
]
testpaths = [
  "packages/ehp-sn/tests",
  "packages/ehp-research/tests",
  "experiments",
  "tests",
]
markers = [
  "small: local test with no external process or repository mutation",
  "medium: crosses one framework or package boundary",
  "large: end-to-end, packaging, or qualification path",
  "contract: validates a framework semantic contract",
  "conformance: validates one implementation against a contract",
  "composition: validates concrete experiment composition semantics",
  "interface: validates CLI or public Python API behavior",
  "regression: protects stable accepted behavior against recurrence",
  "architecture: validates repository ownership/import/path rules",
  "cli: invokes the public command-line interface",
  "figures: exercises figure projection, realization, or sink behavior",
  "telemetry: exercises runtime diagnostic figure paths",
  "qualification: acceptance-level reproducibility or release gate",
  "slow: excluded from normal local development loops",
]
```

Do not add markers casually. A marker must control execution policy, test size, or acceptance level. Do not duplicate folder names as markers unless the marker changes how tests are selected.

Every test must have a size marker:

```python
@pytest.mark.small
@pytest.mark.medium
@pytest.mark.large
```

A test may additionally have purpose markers:

```python
@pytest.mark.contract
@pytest.mark.conformance
@pytest.mark.figures
@pytest.mark.architecture
```

---

## 7. Fixture governance

Fixture location follows ownership.

```text
packages/ehp-sn/tests/support
    framework-only fixtures

packages/ehp-research/tests/support
    reusable scientific fixtures

experiments/<experiment>/vN/tests/conftest.py
    experiment-local fixtures

tests/support
    repository-level public-interface fixtures only
```

Promotion rule:

```text
A fixture may move upward only if its semantics are valid at the higher layer.
```

Examples:

```text
ToyRasterTopologyRecord
    allowed in packages/ehp-sn/tests/support

TinyDagflowRecord
    allowed in packages/ehp-research/tests/support

TinyMazeHardHrmCase
    allowed in experiments/mazehard-hrm/v1/tests

TemporaryWorkspace
    allowed in tests/support only if it contains no scientific defaults
```

Forbidden global fixtures:

```text
arena_tem_workspace
default_hrm_model
mazehard_case
dungeongen_artifact
```

Those encode scientific or experiment semantics and must remain local to the owning layer.

Use `tmp_path` for filesystem isolation.

Use `monkeypatch` for scoped environment changes.

Do not write to real repository paths:

```text
data/
artifacts/
logs/
models/
config/
notebooks/
```

Any test that needs those directory names must create them under `tmp_path`.

---

## 8. Import rules

### 8.1 `ehp_sn` tests

Allowed:

```python
import ehp_sn
from ehp_sn... import ...
```

Forbidden:

```python
import ehp_research
import experiments
```

### 8.2 `ehp_research` tests

Allowed:

```python
import ehp_sn
import ehp_research
```

Forbidden unless explicitly testing installed experiment discovery:

```python
import experiments
```

### 8.3 Experiment tests

Allowed:

```python
import ehp_sn
import ehp_research
import local experiment module/specification
```

### 8.4 Root integration tests

Allowed:

```text
public Python APIs
CLI subprocess calls
installed entry points
artifact manifests
```

Forbidden:

```text
private framework modules
private research modules
direct mutation of package internals
shortcuts around public resolvers
```

---

## 9. Filesystem and workspace rules

Tests must be hermetic.

Default rule:

```text
No test writes to repository-owned data, artifact, log, model, or config directories.
```

Use:

```python
def test_example(tmp_path):
    workspace = tmp_path / "workspace"
```

Do not use:

```python
Path("artifacts")
Path("data/interim")
Path("logs")
```

unless the path is under `tmp_path`.

Tests that verify “no repository mutation” should snapshot or monitor:

```text
data/
artifacts/
logs/
models/
config/
```

and fail if a test writes there.

Large tests may create realistic workspace layouts, but only inside `tmp_path`.

---

## 10. Randomness and determinism rules

Any test involving randomness must declare the seed role.

Allowed:

```text
framework toy seed
figure selection seed
task generation seed
evaluation case-selection seed
```

Forbidden:

```text
implicit global random state
ambient NumPy RNG
PyTorch global RNG without isolation
filesystem-order-dependent selection
dictionary-order-dependent selection
worker-completion-order-dependent selection
```

For deterministic tests, assert repeated runs produce the same result.

For stochastic figure selection, assert:

```text
figure RNG does not advance scientific RNG streams
exact selected IDs are recorded when reproducibility matters
changing figure seed changes only figure selection
enabling figures does not change training/evaluation/task RNG outputs
```

---

## 11. Golden-file rules

Golden files are allowed only for stable public contracts.

Allowed candidates:

```text
canonical logical-record serialization
resolved configuration examples
manifest examples
diagnostic error category examples
small normalized SVG fragments for stable public figures
```

Discouraged or forbidden candidates:

```text
full PNG byte output
large generated artifacts
Matplotlib private object dumps
stochastic outputs without fixed seed and resolved IDs
backend-dependent text layout
temporary telemetry images
```

Every golden file test must state:

```text
why the output is stable
which contract owns the output
what change requires updating the golden file
```

Golden files must be small and reviewable.

Prefer structural assertions over byte comparisons.

---

## 12. Property-based testing rules

Use property-based testing selectively where examples are too weak.

Good targets:

```text
ambient-domain/v1 coordinate and row-major identity
raster-topology/v1 passability and grid4 movement invariants
categorical-field/v1 vocabulary bounds and total assignment
simple-digraph/v1 endpoint, self-loop, duplicate-edge validation
FigureSelection total ordering and tie-breaking
ProjectionIdentity perturbation matrix
artifact staging/commit state machine
configuration duplicate-explicit conflict rules
```

Avoid property-based tests for:

```text
large model training
visual layout aesthetics
backend-specific rendering
exploratory analysis
tests whose property is not clearly defined
```

Property tests must still be deterministic enough for CI. Use bounded strategies and keep examples small.

---

## 13. Architecture tests required

Maintain architecture tests for these invariants:

```text
ehp_sn imports no ehp_research modules
ehp_sn imports no experiments modules
ehp_research does not register experiment-local figures
concrete experiment tests are not placed under packages/ehp-sn/tests
root integration tests do not import private modules
test fixtures do not create real repository artifacts
figure modules do not introduce FigureArtifact or figure-specific store lifecycle
figure rendering modules do not import scientific research concepts
framework figure tests use toy framework fixtures only
```

Architecture tests should inspect public surfaces, AST imports, module exports, and file paths.

Do not scan raw source text naively for forbidden words. Comments and docstrings may legitimately mention forbidden concepts as non-goals. Prefer checking:

```text
import statements
class/function definitions
public __all__
module paths
pytest collection metadata
actual filesystem writes
```

---

## 14. Figure testing rules

Figures require stricter testing because they cross source resolution, selection, preparation, visual composition, rendering, sinks, and telemetry.

### 14.1 Figure test ownership

Framework figure tests:

```text
packages/ehp-sn/tests/figures
```

May test:

```text
FigureInputContract mechanics
source-role validation
selection resolution
selection determinism
figure RNG isolation
prepare boundary mechanics
FigureProjection envelope
ProjectionIdentity
FigureComposition primitive contract
RenderContext validation
RenderRealizationIdentity
RenderedFigure envelope
FigureSink protocol
FigureSchedule mechanics
telemetry snapshot boundary
Python API equivalence for generic figures
```

Must use toy data only.

Research figure tests:

```text
packages/ehp-research/tests/figures
```

May test:

```text
Arena task overview
MazeHard task overview
Dagflow graph overview
HPC place-field summary
MEC grid summary
HRM latent-state dynamics
research FigureData schemas
research visual-composition semantics
research figure registration
```

Experiment-local figure tests:

```text
experiments/<experiment>/vN/tests
```

May test:

```text
Arena–TEM memory-pathway figure
MazeHard–HRM reasoning-cycle figure
MazeHard–HRM-RL deliberation-value figure
Routebind–HRM joint semantic-spatial reasoning figure
```

---

### 14.2 Projection tests

Every stable figure capability should have projection tests for:

```text
input-contract validation
required source roles
missing source role rejection
unsupported source schema rejection
channel/observable requirement rejection
authored selection representation
resolved selection representation
candidate population definition
filter behavior
ordering behavior
tie-breaking
missing-value policy
non-finite-value policy
duplicate-identity policy
seed role when stochastic
read-only source behavior
prepare() determinism
prepare() provenance
ProjectionIdentity construction
```

Projection tests must assert that `prepare()` does not:

```text
run model inference
compute missing metrics
train probes
perform statistical tests
repair invalid outputs
mutate sources
mutate model state
consume scientific RNG streams
```

If a desired figure needs a missing scientific quantity, the test should expect failure, not silent computation.

---

### 14.3 Projection identity perturbation matrix

Every figure family with persisted or reproducible projections must test identity perturbations.

Expected behavior:

```text
same exact sources
same resolved selection
same preparation semantics
same semantic parameters
    -> same ProjectionIdentity

different source identity
    -> different ProjectionIdentity

different selected entity
    -> different ProjectionIdentity

different preparation semantic version
    -> different ProjectionIdentity

different render DPI only
    -> same ProjectionIdentity

different output format only
    -> same ProjectionIdentity

different sink destination only
    -> same ProjectionIdentity
```

Projection identity must not include:

```text
DPI
image width
image height
font
output format
filesystem destination
notebook display handle
Matplotlib figure object identity
```

---

### 14.4 Visual-composition tests

Visual-composition tests should assert that a `FigureProjection` maps to the expected generic composition structure.

Assert:

```text
expected panels exist
expected axes exist
expected marks exist
expected colorbars or legends are declared
expected scientific labels are present
expected annotations are present
layout relationships are explicit
```

Do not assert private Matplotlib internals unless the backend wrapper itself is under test.

Framework visual-composition tests must not contain scientific terms such as:

```text
place cell
TEM
HRM
Arena
MazeHard
```

Research and experiment figure tests may contain those terms when they own the scientific meaning.

---

### 14.5 Rendering tests

Rendering tests must prove that rendering is downstream of projection.

Assert:

```text
renderer consumes FigureComposition + RenderContext
renderer does not call prepare()
renderer does not resolve new scientific sources
renderer does not select new scientific entities
renderer does not compute metrics
renderer does not run inference
renderer does not mutate FigureProjection
renderer does not mutate FigureData
renderer does not mutate scientific sources
```

Render-realization identity should include:

```text
ProjectionIdentity
visual-composition contract/version
RenderContext
render engine/backend identity
serialization policy
```

Render-realization identity should not include:

```text
filesystem destination
temporary path
CLI token position
notebook object address
```

Changing only destination must not change realization identity if serialized bytes are unchanged.

---

### 14.6 Visual regression tests

Use visual regression sparingly.

Preferred order:

```text
1. structural composition assertions
2. normalized SVG or metadata assertions
3. Matplotlib figure equality tests
4. image-baseline comparison only for stable public outputs
```

Visual regression is appropriate for:

```text
publication/report figures with stable visual contract
canonical documentation examples
backend wrapper behavior
```

Visual regression is not appropriate for:

```text
every telemetry snapshot
exploratory notebook output
all style permutations
large stochastic figures
minor layout choices not yet stable
```

When comparing images, keep examples tiny and deterministic.

---

### 14.7 Sink tests

Sink tests must verify that sinks define delivery, not scientific meaning.

Assert:

```text
EphemeralSink does not create committed artifacts
TelemetrySink follows telemetry policy
StagedArtifactSink respects artifact staging rules
ReportSink does not mutate source artifacts
ExportSink writes only to explicit destination
```

Sink destination must not enter scientific projection identity.

---

### 14.8 Telemetry figure tests

Telemetry tests must prove runtime isolation.

Assert:

```text
FigureTelemetrySnapshot is detached/read-only
telemetry exposes no model.forward()
telemetry exposes no backward()
telemetry exposes no optimizer.step()
telemetry exposes no task sampler mutation
telemetry exposes no scientific RNG mutation
captured tensors do not participate in active autograd graph
figure subsystem cannot rerun model inference
diagnostic inference, if any, is owned by the parent operation
```

Telemetry buffering tests must cover:

```text
maximum queued snapshots
maximum memory policy
blocking policy
drop or coalesce policy
failure reporting
shutdown behavior
```

Default expectation:

```text
optional telemetry may be dropped or coalesced;
scientific execution must continue unchanged.
```

---

## 15. Configuration tests

Configuration tests belong mostly in:

```text
packages/ehp-sn/tests/configuration
```

Test:

```text
public namespace validation
canonical field-path grammar
unknown field rejection
malformed path rejection
duplicate explicit value rejection
dedicated option vs --set conflict
frontend source precedence
workspace consumed projection
unused workspace fields do not affect identity
shadowed values do not affect identity
source provenance is recorded
diagnostic provenance does not affect semantic identity
```

Figure configuration tests must assert:

```text
no top-level figure.* namespace is introduced
figure definition ownership is separate from render request ownership
scientific selection is separate from presentation configuration
DPI/output format belong to realization/request or report profile
sink path does not define projection identity
telemetry cadence is request-level unless explicitly made scientific elsewhere
no backend-native rcParams tree becomes public stable config
no universal figure TOML schema is invented prematurely
```

---

## 16. Artifact tests

Artifact tests belong mostly in:

```text
packages/ehp-sn/tests/artifacts
tests/qualification
```

Test:

```text
staging directory is not committed artifact
failed build leaves no valid committed artifact
committed coordinate cannot be overwritten
reuse requires matching identity/fingerprint
different valid artifact at destination is conflict
manifest declares required resources
content digest validation detects mutation
task corpus is self-contained without parent artifacts
normal consumers do not require parent artifacts
```

Figure-related artifact tests must assert:

```text
figures do not introduce FigureArtifact
persisted projections or realizations live inside parent artifacts/resources
rendering into a committed artifact after commit is forbidden
reports may rerender existing science without mutating source artifacts
figure-specific digest systems are not introduced
```

---

## 17. CLI tests

CLI tests should live in:

```text
packages/ehp-sn/tests/interfaces/cli
tests/integration
```

Use package-local CLI tests for command parsing and service boundary behavior.

Use root integration tests for actual public workflows.

CLI tests must assert:

```text
documented commands exist
help output matches public contract
unknown target diagnostics are stable
configuration parse errors have stable categories
plan does not execute
validate does not mutate plan
inspect is read-only
build/run use staging before commit
```

Figure CLI tests must assert:

```text
inspect figures are read-only
ambiguous figure discovery fails explicitly
figure source roles are resolved semantically
render options do not change projection identity
destination options affect sink/placement only
```

Do not use CLI tests to cover every internal branch. Internal branches belong in smaller package tests.

---

## 18. Python API tests

Python API tests should live in:

```text
packages/ehp-sn/tests/interfaces/python
packages/ehp-research/tests/... where scientific implementation is owned
```

Test:

```text
public Python API and CLI resolve equivalent semantic inputs equivalently
prepare_figure returns a FigureProjection or stable projection view
render_figure_projection does not repeat selection/preparation
render_figure convenience is equivalent to prepare + render
multi-source figures require named roles
raw dict/tensor/path inputs are rejected unless explicitly supported
controlled framework errors are raised
```

Do not allow notebook convenience APIs to bypass validation.

---

## 19. Discovery and registration tests

Framework discovery tests:

```text
packages/ehp-sn/tests/discovery
```

Test generic catalogue behavior:

```text
duplicate reference rejection
ambiguous reference rejection
deterministic ordering
invalid provider isolation
no direct framework import of ehp_research
```

Research registration tests:

```text
packages/ehp-research/tests/registration
```

Test:

```text
all reusable research components register
research figures register only reusable research figures
experiment-local figures are not registered by ehp_research
broken provider imports are detected
top-level ehp_research import remains side-effect safe when required
```

Root distribution tests:

```text
tests/distribution
```

Test:

```text
packages build
entry points load
installed imports work
provider catalogue loads in installed form
README examples are marked executable/provisional correctly
```

---

## 20. Integration tests

Root integration tests should be few and public.

Recommended initial integration tests:

```text
test_data_to_tasks_minimal.py
test_task_corpus_inspect_minimal.py
test_generic_figure_pipeline_minimal.py
test_train_plan_minimal.py
test_evaluate_plan_minimal.py
test_analyze_report_minimal.py
test_cli_python_equivalence_minimal.py
```

Integration tests must use:

```text
tmp_path workspace
public CLI or public Python API
small deterministic fixtures
bounded data sizes
explicit seeds
```

Integration tests must not use:

```text
private imports
large generated corpora
real repository artifacts
training loops unless explicitly marked slow/qualification
```

---

## 21. Qualification tests

Qualification tests are acceptance gates, not normal development tests.

Use:

```text
tests/qualification
```

Recommended qualification tests:

```text
test_reproducible_artifact_identity.py
test_reproducible_figure_projection_identity.py
test_render_changes_do_not_change_projection_identity.py
test_cli_python_equivalence.py
test_committed_artifact_immutability.py
test_task_corpus_self_contained.py
test_no_source_tree_mutation.py
test_provider_catalogue_installed_environment.py
```

Qualification tests may be slower, but must remain deterministic and isolated.

---

## 22. Naming conventions

Use names that state the invariant.

Good:

```python
def test_projection_identity_ignores_render_dpi():
    ...

def test_top_k_selection_tie_breaks_by_cell_id():
    ...

def test_ehp_sn_does_not_import_ehp_research():
    ...

def test_committed_artifact_rejects_overwrite():
    ...
```

Bad:

```python
def test_figure():
    ...

def test_basic():
    ...

def test_utils():
    ...

def test_integration():
    ...
```

Prefer one invariant per test. A test name should make the expected failure obvious.

---

## 23. Negative tests are mandatory for contracts

Every stable contract must have both positive and negative tests.

Example for `raster-topology/v1`:

```text
positive:
    valid connected grid4 topology conforms

negative:
    invalid passable length rejected
    invalid movement self-loop rejected
    inconsistent state mapping rejected
```

Example for figure selection:

```text
positive:
    top-k selection resolves deterministic selected IDs

negative:
    missing tie-break rejected for reproducible selection
    duplicate entity IDs rejected
    NaN policy missing rejected
```

A contract tested only by happy-path examples is not sufficiently tested.

---

## 24. Test data policy

Use the smallest data that proves the invariant.

Preferred:

```text
2x2 raster
3x3 raster
three-node DAG
four-node graph with one branch
two-case corpus
single-step or three-step episode
one toy projection
```

Avoid:

```text
30x30 mazes
full Arena corpora
large HRM inputs
real training traces
large PNG baselines
```

Large examples belong only in slow integration or qualification tests.

---

## 25. Review checklist for generated tests

Before accepting a generated test, check:

```text
Does the test live under the owner of the invariant?
Does it have exactly one size marker?
Does it have the right purpose marker?
Does it avoid forbidden imports for its layer?
Does it use tmp_path for filesystem writes?
Does it avoid writing into real repository directories?
Does it avoid hidden scientific semantics in shared fixtures?
Does it assert the architectural boundary directly?
Does it include a negative case when testing a contract?
Is the data minimal?
Is randomness seeded and isolated?
Does the test fail for the intended bug?
Does it avoid freezing incidental backend behavior?
```

Reject or rewrite tests that fail this checklist.

---

## 26. Anti-patterns

Do not generate tests with these patterns.

### 26.1 Framework test importing research

Wrong:

```python
# packages/ehp-sn/tests/figures/test_projection.py
from ehp_research.tasks.arena import ...
```

Correction:

```python
# use ToyFigureSource or ToyLogicalRecord
```

### 26.2 Root fixture with experiment semantics

Wrong:

```python
# tests/support/fixtures.py
@pytest.fixture
def arena_tem_workspace(...):
    ...
```

Correction:

```text
move to experiments/arena-tem/v1/tests/conftest.py
```

### 26.3 Image baseline for every figure

Wrong:

```text
Every figure test compares full PNG output.
```

Correction:

```text
Most figure tests assert projection identity, composition structure, labels, and sink behavior.
Only stable public outputs get image regression tests.
```

### 26.4 Integration test using private shortcuts

Wrong:

```python
from ehp_research.tasks.arena._builder import build_internal
```

Correction:

```python
subprocess.run(["ehp-sn", "tasks", "build", ...])
```

or public Python API.

### 26.5 Test writes to real artifacts

Wrong:

```python
output = Path("artifacts/test-run")
```

Correction:

```python
output = tmp_path / "artifacts" / "test-run"
```

### 26.6 Test freezes implementation accident

Wrong:

```python
assert list(my_dict.keys()) == [...]
```

unless ordering is part of the public contract.

Correction:

```python
assert resolved_order == expected_order
```

where the order is produced by an explicit deterministic ordering rule.

### 26.7 Architecture test scans comments/docstrings naively

Wrong:

```python
assert "FigureArtifact" not in source_text
```

Correction:

```python
assert "FigureArtifact" not in exported_symbols
assert no class/function named "FigureArtifact" exists in AST
```

---

## 27. Minimum testing matrix for figures

Every implemented figure slice should satisfy the relevant rows below.

```text
Framework figure core
    small contract tests
    medium API tests
    architecture boundary tests

Reusable research figure
    research conformance tests
    composition semantics tests
    registration tests
    small deterministic source fixtures

Experiment-local figure
    experiment composition tests
    source-role compatibility tests
    projection identity tests
    fixed probe/selection tests if telemetry is involved

Rendering backend
    structural rendering tests
    realization identity tests
    mutation tests
    sparse visual regression only when stable

Telemetry figure path
    snapshot isolation tests
    no-inference tests
    bounded queue tests
    failure isolation tests
```

---

## 28. Minimum CI lanes

Recommended CI lanes:

```text
local-fast
    small tests only, no slow/integration/qualification

package-contract
    ehp-sn and ehp-research small+medium tests

architecture
    root architecture tests

integration
    root public-surface integration tests

qualification
    reproducibility, immutability, packaging, and acceptance-level tests

full
    all tests
```

Example commands:

```console
pytest packages/ehp-sn/tests packages/ehp-research/tests experiments \
  -m "small and not slow"

pytest packages/ehp-sn/tests packages/ehp-research/tests \
  -m "small or medium"

pytest tests/architecture -m architecture

pytest tests/integration -m "medium or large"

pytest tests/qualification -m qualification

pytest
```

Exact commands may be adapted to the CI system, but the lanes must preserve the same economics:

```text
many small tests
some medium tests
few large tests
qualification as an explicit gate
```

---

## 29. KPIs

Track these KPIs.

```text
ehp_sn tests importing ehp_research
    target: 0

ehp_sn tests importing experiments
    target: 0

concrete experiment tests under packages/ehp-sn/tests
    target: 0

tests writing to repository data/artifacts/logs/models/config
    target: 0

unknown pytest markers
    target: 0

small tests using subprocess
    target: 0

root integration tests importing private modules
    target: 0

figure projection identity changes caused only by rendering parameters
    target: 0

render-realization identity changes caused only by sink destination
    target: 0 unless serialized bytes or declared realization semantics change

golden PNG/SVG tests without stability rationale
    target: 0

stable contracts with at least one negative test
    target: 100%

artifact/figure identity perturbation matrices covered
    target: 100% for implemented stable slices

CI lanes documented and runnable
    target: 100%
```

Prefer these architectural KPIs over raw line coverage. Line coverage is useful but insufficient for EHP-SN because the major risks are semantic leakage, identity mistakes, nondeterminism, artifact mutation, and misplaced ownership.

---

## 30. Instruction for LLM/code agents generating tests

When generating a new test, follow this procedure:

```text
1. Identify the semantic invariant.
2. Identify the owner:
       ehp_sn
       ehp_research
       experiment
       root repository
3. Place the test under that owner.
4. Select exactly one size:
       small
       medium
       large
5. Select the purpose:
       contract
       conformance
       composition
       interface
       regression
       architecture
       qualification
6. Use the smallest deterministic fixture that proves the invariant.
7. Use tmp_path for all filesystem writes.
8. Avoid forbidden imports for the layer.
9. Add a negative test if the invariant is a contract.
10. Assert public semantics, not private accidents.
11. Ensure the test would fail for the intended architectural or behavioral bug.
```

Do not generate broad “coverage” tests that merely execute code.

Do not generate tests that silently encode new semantics.

Do not generate tests that make framework tests depend on research components.

Do not generate tests that make integration tests depend on private internals.

Do not generate tests that write into real repository data or artifact directories.

---

## 31. Final principle

The EHP-SN testing system exists to protect architectural meaning.

```text
Test location follows semantic ownership.
Test size controls cost and allowed dependencies.
Test purpose states the evidence provided.
Fixtures obey ownership boundaries.
Integration tests use public surfaces.
Figure tests protect projection, realization, identity, sink, and telemetry boundaries.
Qualification tests prove reproducibility and immutability.
```

A test that violates those principles should be moved, narrowed, or deleted.
