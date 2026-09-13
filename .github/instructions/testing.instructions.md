# EHP-SN testing instructions

## 0. Purpose

EHP-SN does **not** invent a testing framework.

EHP-SN uses the standard Python testing stack:

```text
pytest
pytest markers
pytest tmp_path / monkeypatch
pytest importlib import mode
Hypothesis for property-based tests
Import Linter or equivalent import-boundary checks
CI lanes based on test size and purpose
```

The EHP-SN-specific policy is a thin architectural layer on top:

```text
semantic ownership determines test location
test size determines allowed cost and dependencies
test purpose determines evidence
architecture tests enforce package boundaries
qualification tests protect reproducibility, identity, and immutability
```

The goal is not to maximize test count. The goal is to protect the EHP-SN architecture:

```text
ehp_sn
    reusable framework

ehp_research
    reusable scientific components

experiments/<experiment>/vN
    concrete scientific compositions

root tests/
    repository architecture, distribution, public integration, and qualification
```

Every generated test must answer four questions before code is written:

```text
What invariant is being tested?
Who owns that invariant?
What size is the test?
What evidence does the test provide?
```

A test without clear answers should not be generated.

## 1. External conventions adopted

EHP-SN follows these recognizable conventions.

### 1.1 Pytest as the test framework

Pytest is the project test runner and public test convention.

The test suite uses:

```text
pytest test discovery
pytest markers
pytest fixtures
pytest tmp_path
pytest monkeypatch
pytest importlib import mode
pytest strict marker validation
```

Pytest recommends `src` layout for installable packages and notes that `--import-mode=importlib` avoids pytest modifying `sys.path` in surprising ways. Pytest strict markers make unknown marks fail instead of silently passing. Pytest also provides `tmp_path` for per-test temporary files and `monkeypatch` for scoped environment or attribute changes.

### 1.2 Google-style test sizes

EHP-SN classifies every test as:

```text
small
medium
large
```

This follows the common Google test-size model: small tests are local/unit-like, medium tests cross a nearby boundary, and large tests are end-to-end or system-level.

### 1.3 Test pyramid economics

EHP-SN follows test pyramid economics:

```text
many small tests
some medium tests
few large tests
explicit qualification gates
```

The test pyramid is a practical convention for keeping most checks fast and local while reserving expensive end-to-end tests for higher-value workflow evidence.

### 1.4 Arrange–Act–Assert / Given–When–Then

Tests should normally be readable as:

```text
Arrange
Act
Assert
```

or equivalently:

```text
Given
When
Then
```

Given–When–Then is a common reformulation of setup/exercise/verify test structure, and Arrange–Act–Assert is the same idea in unit-test terminology.

Preferred shape:

```python
def test_projection_identity_ignores_render_dpi():
    # Arrange
    projection = make_toy_projection()
    low_dpi = RenderContext(dpi=150)
    high_dpi = RenderContext(dpi=600)

    # Act
    low_identity = projection.identity_with(low_dpi)
    high_identity = projection.identity_with(high_dpi)

    # Assert
    assert low_identity == high_identity
```

Do not force comments when the phases are obvious, but the structure should be visible.

### 1.5 Property-based testing

Use Hypothesis for property-based tests when example tests are too weak.

Good targets:

```text
canonical ordering
identity perturbation matrices
schema validation
configuration conflict rules
artifact state machines
selection tie-breaking
```

Hypothesis is the standard property-based testing library for Python. Hypothesis tests must still have deterministic outcomes when used with pytest.

### 1.6 Architecture testing

Use import-boundary tooling where possible.

Import Linter supports layered architecture contracts where lower layers are forbidden from importing higher layers.

For EHP-SN, import contracts should enforce:

```text
ehp_sn
    must not import ehp_research
    must not import experiments

ehp_research
    may import ehp_sn
    must not import concrete experiments

experiments
    may import ehp_sn
    may import ehp_research
```

Use custom pytest architecture tests only for repository-specific rules that import tooling cannot express well, such as test placement, fixture placement, and no writes to repository runtime directories.

## 2. Core placement rule

Test location follows semantic ownership.

```text
packages/ehp-sn/tests
    framework-owned semantics only

packages/ehp-research/tests
    reusable scientific component semantics only

experiments/<experiment>/vN/tests
    concrete experiment composition semantics only

tests/
    repository architecture, distribution, public integration, and qualification only
```

Do not place a test where implementation access is convenient. Place it where the invariant is owned.

## 3. Target test layout

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
        test_model_io.py
        test_figures.py
        test_protocols.py

  arena-tem-t/
    v1/
      tests/

  mazehard-hrm/
    v1/
      tests/
        test_definition.py
        test_model_io.py
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

The exact filenames may vary. Ownership must not.

## 4. Ownership rules

### 4.1 Framework tests

Location:

```text
packages/ehp-sn/tests
```

Use this location for generic framework contracts and services.

Allowed subjects:

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
generic task/model/model-IO abstractions
resource requirements
identity/provenance/digest behavior
```

Framework tests may test generic figure concepts:

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

Use toy fixtures instead:

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

### 4.2 Research tests

Location:

```text
packages/ehp-research/tests
```

Use this location for reusable scientific components whose meaning remains coherent independently of one concrete experiment.

Allowed subjects:

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

Research tests may import:

```python
import ehp_sn
import ehp_research
```

Research tests must not test concrete task-model compositions such as:

```text
Arena + TEM
Arena + TEM-t
MazeHard + HRM
MazeHard + HRM-rl
Routebind + HRM
```

Those belong under the corresponding experiment.

A research conformance test may still be `small` when it imports both `ehp_sn` and `ehp_research`, provided it uses tiny deterministic fixtures and does not cross an operational boundary.

### 4.3 Experiment tests

Location:

```text
experiments/<experiment>/vN/tests
```

Use this location for concrete scientific compositions.

Allowed subjects:

```text
resolved experiment definition
concrete model IO specifications
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

```python
import ehp_sn
import ehp_research
import local_experiment_module
```

Experiment tests must not redefine generic framework rules. They assert that the concrete experiment uses those rules correctly.

### 4.4 Root tests

Location:

```text
tests/
```

Use root tests only for repository-wide concerns.

Allowed folders:

```text
tests/architecture
tests/distribution
tests/integration
tests/qualification
tests/support
```

Root integration and qualification tests should use public surfaces:

```text
CLI
public Python API
installed package imports
entry points
artifact manifests
configured workspaces
temporary committed artifacts
```

Wrong:

```python
from ehp_sn.figures._internal import ...
from ehp_research.tasks.arena._builder import ...
```

Correct:

```python
from ehp_sn import train, evaluate
subprocess.run(["ehp-sn", "data", "inspect", artifact])
```

Architecture tests are an exception to the public-surface-only rule. They may inspect:

```text
AST imports
module paths
package metadata
public exports
pytest collection metadata
filesystem writes
```

They still must not depend on private runtime shortcuts to execute workflows.

## 5. Test size model

Every test must have exactly one size marker:

```python
@pytest.mark.small
@pytest.mark.medium
@pytest.mark.large
```

The size marker controls allowed cost and dependencies.

### 5.1 Small tests

A small test checks local behavior.

Allowed:

```text
single module or narrow package-local behavior
pure functions
small in-memory objects
tiny deterministic fixtures
tmp_path only when filesystem behavior is the invariant
research component conformance against framework contracts using tiny fixtures
```

Forbidden:

```text
subprocess
network
real repository data/artifacts/logs/models writes
cross-operation workflows
expensive model training
large generated datasets
```

Examples:

```text
raster-topology rejects invalid passability length
FigureSelection tie-breaks by stable ID
RenderContext rejects scientific selection fields
configuration parser rejects duplicate explicit values
Dagflow tiny graph conforms to simple-digraph/v1
```

### 5.2 Medium tests

A medium test crosses one architectural boundary.

Allowed examples:

```text
configuration file -> resolved request
component registry -> resolved figure catalogue
artifact resolver -> resolved figure source
public Python API -> internal framework service
research component -> framework contract conformance with resolver involvement
CLI command -> parser/service boundary
```

Medium tests may use `tmp_path` workspaces.

Medium tests may use subprocess only when the CLI itself is the surface under test.

### 5.3 Large tests

A large test exercises an end-to-end or qualification path.

Allowed examples:

```text
data build -> tasks build -> inspect figure
train plan -> evaluate plan -> analyze plan
analysis artifact -> report rendering
built wheel -> import -> entry point load
full figure projection -> render -> sink path
```

Large tests must be few, deterministic, public-surface only, and isolated in temporary workspaces.

Large tests normally live in:

```text
tests/integration
tests/qualification
```

## 6. Test purpose model

Each test should have one dominant purpose marker.

Allowed purpose markers:

```text
contract
conformance
composition
interface
regression
architecture
qualification
```

### 6.1 Contract

Validates a framework semantic contract.

Example:

```text
categorical-field/v1 rejects observation IDs outside vocabulary bounds
```

Location:

```text
packages/ehp-sn/tests/contracts
```

### 6.2 Conformance

Validates one concrete implementation against a contract.

Example:

```text
Dagflow single-terminal records conform to simple-digraph/v1 and expose exactly one terminal
```

Location:

```text
packages/ehp-research/tests/substrates/dagflow
```

### 6.3 Composition

Validates a concrete experiment composition.

Example:

```text
MazeHard-HRM binding exposes public maze/start/goal information but not oracle route truth
```

Location:

```text
experiments/mazehard-hrm/v1/tests
```

### 6.4 Interface

Validates public CLI or public Python API behavior.

Examples:

```text
ehp-sn data inspect reports ambiguous compatible figures
render_figure convenience equals prepare_figure + render_figure_projection
```

Location depends on scope:

```text
packages/ehp-sn/tests/interfaces
tests/integration
```

### 6.5 Regression

Locks stable accepted behavior or a previously fixed bug.

Allowed only for stable or accepted behavior.

Examples:

```text
resolved configuration diagnostic category
manifest resource descriptor
normalized SVG fragment for a stable public figure
```

Do not create golden files for exploratory, provisional, or backend-incidental behavior.

### 6.6 Architecture

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

### 6.7 Qualification

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

## 7. Required pytest configuration

Use strict markers and importlib import mode.

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
  "medium: crosses one framework, package, or public-interface boundary",
  "large: end-to-end, packaging, or qualification path",

  "contract: validates a framework semantic contract",
  "conformance: validates one implementation against a contract",
  "composition: validates concrete experiment composition semantics",
  "interface: validates CLI or public Python API behavior",
  "regression: protects stable accepted behavior against recurrence",
  "architecture: validates repository ownership, imports, or path rules",
  "qualification: acceptance-level reproducibility, immutability, or release gate",

  "cli: invokes the public command-line interface",
  "figures: exercises figure projection, realization, sink, or telemetry behavior",
  "telemetry: exercises runtime diagnostic figure paths",
  "slow: excluded from normal local development loops",
]
```

Do not add markers casually. A marker must control execution policy, size, purpose, or acceptance level.

Every test must have exactly one size marker.

A test may additionally have one or more purpose/domain markers.

Example:

```python
@pytest.mark.small
@pytest.mark.contract
@pytest.mark.figures
def test_projection_identity_ignores_render_dpi():
    ...
```

## 8. Optional import-linter baseline

Use Import Linter or an equivalent import-boundary tool to enforce package direction.

Illustrative configuration:

```toml
[tool.importlinter]
root_package = "ehp_sn"

[[tool.importlinter.contracts]]
name = "ehp_sn must not import ehp_research"
type = "forbidden"
source_modules = ["ehp_sn"]
forbidden_modules = ["ehp_research"]

[[tool.importlinter.contracts]]
name = "ehp_sn must not import experiments"
type = "forbidden"
source_modules = ["ehp_sn"]
forbidden_modules = ["experiments"]
```

Because `ehp_research` is a separate package, a second root or invocation may be needed:

```toml
[tool.importlinter]
root_package = "ehp_research"

[[tool.importlinter.contracts]]
name = "ehp_research must not import concrete experiments"
type = "forbidden"
source_modules = ["ehp_research"]
forbidden_modules = ["experiments"]
```

Exact configuration may differ depending on monorepo packaging. The invariant must not differ.

## 9. Test suite governance

Add a repository architecture test module:

```text
tests/architecture/test_test_suite_governance.py
```

It should enforce:

```text
every collected test has exactly one size marker
no unknown markers exist
framework tests do not import ehp_research
framework tests do not import experiments
research tests do not import concrete experiments
root integration tests do not import private modules
concrete experiment tests are not placed under packages/ehp-sn/tests
framework figure tests use toy fixtures only
tests do not write into real repository runtime directories
```

Collection-time failure is preferred over relying on review comments.

## 10. Fixture governance

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

Allowed examples:

```text
ToyRasterTopologyRecord
    packages/ehp-sn/tests/support

TinyDagflowRecord
    packages/ehp-research/tests/support

TinyMazeHardHrmCase
    experiments/mazehard-hrm/v1/tests

TemporaryWorkspace
    tests/support, only if it contains no scientific defaults
```

Forbidden global fixtures:

```text
arena_tem_workspace
default_hrm_model
mazehard_case
dungeongen_artifact
```

Those encode scientific or experiment semantics and must remain local to the owning layer.

## 11. Import rules

### 11.1 Framework tests

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

### 11.2 Research tests

Allowed:

```python
import ehp_sn
import ehp_research
```

Forbidden unless explicitly testing installed experiment discovery:

```python
import experiments
```

### 11.3 Experiment tests

Allowed:

```python
import ehp_sn
import ehp_research
import local_experiment_module
```

### 11.4 Root integration tests

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

## 12. Filesystem and workspace rules

Tests must be hermetic.

Default rule:

```text
No test writes to repository-owned data, artifact, log, model, or config directories.
```

Forbidden real paths:

```text
data/
artifacts/
logs/
models/
config/
notebooks/
```

Use `tmp_path`:

```python
def test_example(tmp_path):
    workspace = tmp_path / "workspace"
    output = workspace / "artifacts" / "run-001"
```

Do not use:

```python
Path("artifacts/test-run")
Path("data/interim")
Path("logs")
```

unless the path is under `tmp_path`.

Large tests may create realistic workspace layouts, but only inside `tmp_path`.

Use `monkeypatch` for scoped environment changes.

## 13. Randomness and determinism

Any test involving randomness must declare the seed role.

Allowed seed roles:

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

For deterministic behavior, assert repeated runs produce the same result.

For stochastic figure selection, assert:

```text
figure RNG does not advance scientific RNG streams
exact selected IDs are recorded when reproducibility matters
changing figure seed changes only figure selection
enabling figures does not change training/evaluation/task RNG outputs
```

## 14. Golden-file rules

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

Every golden-file test must state:

```text
why the output is stable
which contract owns the output
what change requires updating the golden file
```

Prefer structural assertions over byte comparisons.

## 15. Property-based testing

Use Hypothesis selectively.

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

Property tests must be bounded, deterministic enough for CI, and cheaper than the bug class they protect against.

## 16. Negative tests

Every stable contract must have positive and negative tests.

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

## 17. Figure testing rules

Figures require stricter tests because they cross source resolution, selection, preparation, visual composition, rendering, sinks, and telemetry.

### 17.1 Figure test ownership

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
Routebind–HRM semantic-spatial reasoning figure
```

### 17.2 Projection tests

Every stable figure capability should test:

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

### 17.3 Projection identity perturbation matrix

Every figure family with persisted or reproducible projections must test:

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

### 17.4 Visual-composition tests

Visual-composition tests assert that a `FigureProjection` maps to the expected generic composition structure.

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

Framework visual-composition tests must not contain scientific semantics such as:

```text
place cell
TEM
HRM
Arena
MazeHard
```

Research and experiment figure tests may contain those terms when they own the scientific meaning.

### 17.5 Rendering tests

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

Changing only destination must not change realization identity if serialized bytes and declared realization semantics are unchanged.

### 17.6 Visual regression tests

Use visual regression sparingly.

Preferred order:

```text
1. structural composition assertions
2. normalized SVG or metadata assertions
3. backend wrapper tests
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

Avoid full PNG byte comparison unless the rendering contract explicitly guarantees byte stability.

### 17.7 Sink tests

Sink tests verify that sinks define delivery, not scientific meaning.

Assert:

```text
EphemeralSink does not create committed artifacts
TelemetrySink follows telemetry policy
StagedArtifactSink respects artifact staging rules
ReportSink does not mutate source artifacts
ExportSink writes only to explicit destination
```

Sink destination must not enter scientific projection identity.

### 17.8 Telemetry tests

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
optional telemetry may be dropped or coalesced
scientific execution must continue unchanged
```

## 18. Configuration tests

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
semantic provenance is recorded
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

## 19. Artifact tests

Artifact tests belong mostly in:

```text
packages/ehp-sn/tests/artifacts
tests/qualification
```

Test:

```text
staging directory is not a committed artifact
failed build leaves no valid committed artifact
committed coordinate cannot be overwritten
reuse requires matching identity/fingerprint
different valid artifact at destination is a conflict
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

## 20. CLI tests

CLI tests should live in:

```text
packages/ehp-sn/tests/interfaces/cli
tests/integration
```

Use package-local CLI tests for command parsing and service-boundary behavior.

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

## 21. Python API tests

Python API tests should live in:

```text
packages/ehp-sn/tests/interfaces/python
packages/ehp-research/tests/... when scientific implementation is owned there
experiments/<experiment>/vN/tests when composition is experiment-owned
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

Notebook convenience APIs must not bypass validation.

## 22. Discovery and registration tests

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

## 23. Integration tests

Root integration tests should be few and public.

Recommended initial tests:

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

## 24. Qualification tests

Qualification tests are acceptance gates, not normal development tests.

Location:

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

## 25. Naming conventions

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

## 26. Test data policy

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

## 27. CI lanes

Recommended CI lanes:

```text
local-fast
    small tests only, no slow/integration/qualification

package-contract
    package small+medium tests

architecture
    import-boundary and repository-governance checks

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
  -m "(small or medium) and not slow"

pytest tests/architecture -m architecture

pytest tests/integration -m "(medium or large) and not slow"

pytest tests/qualification -m qualification

pytest
```

Exact commands may be adapted to the CI system, but the economics must remain:

```text
many small tests
some medium tests
few large tests
qualification as an explicit gate
```

## 28. KPIs

Track architectural KPIs over raw line coverage.

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

tests without exactly one size marker
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

Line coverage may be collected, but it is not the primary quality signal. EHP-SN’s highest risks are semantic leakage, identity mistakes, nondeterminism, artifact mutation, misplaced ownership, and hidden scientific computation.

## 29. Review checklist

Before accepting a generated test, check:

```text
Does the test state one invariant?
Does the test live under the owner of that invariant?
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

## 30. Anti-patterns

### 30.1 Framework test importing research

Wrong:

```python
# packages/ehp-sn/tests/figures/test_projection.py
from ehp_research.tasks.arena import ...
```

Correct:

```python
# use ToyFigureSource or ToyLogicalRecord
```

### 30.2 Root fixture with experiment semantics

Wrong:

```python
# tests/support/fixtures.py
@pytest.fixture
def arena_tem_workspace(...):
    ...
```

Correct:

```text
move to experiments/arena-tem/v1/tests/conftest.py
```

### 30.3 Image baseline for every figure

Wrong:

```text
Every figure test compares full PNG output.
```

Correct:

```text
Most figure tests assert projection identity, composition structure, labels, and sink behavior.
Only stable public outputs get image regression tests.
```

### 30.4 Integration test using private shortcuts

Wrong:

```python
from ehp_research.tasks.arena._builder import build_internal
```

Correct:

```python
subprocess.run(["ehp-sn", "tasks", "build", ...])
```

or a public Python API.

### 30.5 Test writes to real artifacts

Wrong:

```python
output = Path("artifacts/test-run")
```

Correct:

```python
output = tmp_path / "artifacts" / "test-run"
```

### 30.6 Test freezes implementation accident

Wrong:

```python
assert list(my_dict.keys()) == [...]
```

unless ordering is part of the public contract.

Correct:

```python
assert resolved_order == expected_order
```

where the order is produced by an explicit deterministic ordering rule.

### 30.7 Architecture test scans comments/docstrings naively

Wrong:

```python
assert "FigureArtifact" not in source_text
```

Correct:

```python
assert "FigureArtifact" not in exported_symbols
assert no class/function named "FigureArtifact" exists in AST
```

## 31. LLM/code-agent procedure

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
6. Use Arrange–Act–Assert.
7. Use the smallest deterministic fixture that proves the invariant.
8. Use tmp_path for all filesystem writes.
9. Avoid forbidden imports for the layer.
10. Add a negative test if the invariant is a contract.
11. Assert public semantics, not private accidents.
12. Ensure the test would fail for the intended architectural or behavioral bug.
```

Do not generate broad “coverage” tests that merely execute code.

Do not generate tests that silently encode new semantics.

Do not generate framework tests that depend on research components.

Do not generate integration tests that depend on private internals.

Do not generate tests that write into real repository data or artifact directories.

## 32. Final principle

The EHP-SN testing system is a pytest-based, standard Python test suite with an architectural ownership policy.

```text
pytest provides the framework
Google-style sizes control cost
test pyramid economics control distribution
AAA/GWT controls readability
Hypothesis strengthens pure contracts
Import Linter and architecture tests enforce boundaries

EHP-SN adds:
    semantic ownership decides location
    fixtures obey ownership boundaries
    integration tests use public surfaces
    figure tests protect projection/render/sink/telemetry separation
    qualification tests prove reproducibility and immutability
```

A test that violates those principles should be moved, narrowed, or deleted.
