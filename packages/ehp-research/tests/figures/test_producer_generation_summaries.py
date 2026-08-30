"""Phase 5 Stage D — producer generation-summary figure tests.

This suite validates the three producer-owned generation-summary figures in
``ehp_research`` against their **real committed releases**:

* ``figure:dagflow-generation-summary/v1``   over ``data/interim/dagflow/single-terminal/v1``
* ``figure:dungeongen-generation-summary/v1`` over ``data/interim/dungeongen/general/v3``
* ``figure:obsfield-generation-summary/v1``  over ``data/interim/obsfield/categorical-complete/v1``

For each figure it asserts (Phase-5 § 38):

* structural correctness of the prepared data against provenance-expected
  counts/splits;
* deterministic representative selection (run twice, same result);
* Matplotlib rendering without error;
* registration in the ordinary figure catalogue (``effective_figure_registry``).

It also carries a producer-blindness unit test: the generic
``simple-digraph-artifact-summary`` / ``raster-topology-artifact-summary``
figures (which declare no artifact-metadata surface) still receive the plain
record tuple, not an :class:`ArtifactSourceContent`, and are unchanged.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import pytest
from ehp_research.figures.dagflow_generation_summary import (
    DAGFLOW_GENERATION_SUMMARY_REF,
    DagflowGenerationSummaryData,
)
from ehp_research.figures.dungeongen_generation_summary import (
    DUNGEONGEN_GENERATION_SUMMARY_REF,
    DungeonGenGenerationSummaryData,
)
from ehp_research.figures.obsfield_generation_summary import (
    OBSFIELD_GENERATION_SUMMARY_REF,
    ObsFieldGenerationSummaryData,
)
from ehp_sn.artifacts import load_release
from ehp_sn.contracts.observations import CategoricalField
from ehp_sn.contracts.relations import SimpleDigraph
from ehp_sn.figures import inspect_artifact_figure, list_figures_for_artifact
from ehp_sn.figures.providers import effective_figure_registry
from ehp_sn.figures.service import _build_collection_source
from ehp_sn.figures.source import ArtifactSourceContent

#: The repository's interim-data root (committed releases live under
#: ``data/interim/<family>/<variant>/v<N>/``).
_REPO_ROOT: Path = Path(__file__).resolve().parents[4]
_ARTIFACT_ROOT: Path = _REPO_ROOT / "data" / "interim"


@pytest.fixture(autouse=True)
def _close_figures() -> None:
    """Close every Matplotlib figure after each test to avoid leakage."""
    yield
    import matplotlib.pyplot as plt

    plt.close("all")


def _registry():
    """The ordinary figure catalogue including built-in and research figures."""
    return effective_figure_registry()


def _prepared(artifact: str, figure_ref: str) -> object:
    """Project ``figure_ref`` over the committed ``artifact`` and return the prepared view."""
    result = inspect_artifact_figure(
        artifact,
        figure_ref,
        artifact_root=_ARTIFACT_ROOT,
        registry=_registry(),
    )
    return result.projection.content


# ---------------------------------------------------------------------------
# Dagflow generation summary
# ---------------------------------------------------------------------------


def test_dagflow_figure_listed_for_artifact() -> None:
    refs = list_figures_for_artifact(
        "artifact:dagflow/single-terminal/v1",
        artifact_root=_ARTIFACT_ROOT,
        registry=_registry(),
    )
    assert DAGFLOW_GENERATION_SUMMARY_REF in refs


def test_dagflow_prepared_matches_provenance() -> None:
    data = _prepared("artifact:dagflow/single-terminal/v1", DAGFLOW_GENERATION_SUMMARY_REF)
    assert isinstance(data, DagflowGenerationSummaryData)
    # Configured and observed split counts must match provenance (10000/1000/1000).
    assert data.split_order == ("train", "validation", "test")
    assert data.observed_split_counts == (10000, 1000, 1000)
    assert data.configured_split_counts == (10000, 1000, 1000)
    assert data.node_count_policy == ["fixed", 64]
    assert data.additional_edge_probability == 0.4
    assert data.generation_protocol == "constructive-forward/v1"
    # validation auxiliary not present in the committed v1 release → None.
    assert data.validation_status is None


def test_dagflow_gallery_deterministic_and_typed() -> None:
    a = _prepared("artifact:dagflow/single-terminal/v1", DAGFLOW_GENERATION_SUMMARY_REF)
    b = _prepared("artifact:dagflow/single-terminal/v1", DAGFLOW_GENERATION_SUMMARY_REF)
    assert isinstance(a, DagflowGenerationSummaryData)
    assert isinstance(b, DagflowGenerationSummaryData)
    assert a.selected_ids == b.selected_ids
    assert a.selected_splits == b.selected_splits
    # Each split contributes up to three selected records → up to 9, all typed.
    assert len(a.selected_ids) <= 9
    assert len(a.selected_ids) == len(a.selected_splits) == len(a.selected_graphs)
    assert all(isinstance(g, SimpleDigraph) for g in a.selected_graphs)
    for split in a.split_order:
        assert split in a.selected_splits


def test_dagflow_renders() -> None:
    result = inspect_artifact_figure(
        "artifact:dagflow/single-terminal/v1",
        DAGFLOW_GENERATION_SUMMARY_REF,
        artifact_root=_ARTIFACT_ROOT,
        registry=_registry(),
    )
    import matplotlib.figure

    assert isinstance(result.figure, matplotlib.figure.Figure)


# ---------------------------------------------------------------------------
# DungeonGen generation summary
# ---------------------------------------------------------------------------


def test_dungeongen_figure_listed_for_artifact() -> None:
    refs = list_figures_for_artifact(
        "artifact:dungeongen/general/v3",
        artifact_root=_ARTIFACT_ROOT,
        registry=_registry(),
    )
    assert DUNGEONGEN_GENERATION_SUMMARY_REF in refs


def test_dungeongen_prepared_matches_provenance() -> None:
    data = _prepared("artifact:dungeongen/general/v3", DUNGEONGEN_GENERATION_SUMMARY_REF)
    assert isinstance(data, DungeonGenGenerationSummaryData)
    assert data.record_count == 500
    assert data.attempt_budget == 100
    assert data.seed == 0
    assert data.generator_protocol == "dungeongen/generation/v1"
    assert data.duplicate_policy == "allow"
    # Accepted-attempt distribution counts sum to the record count.
    assert sum(count for _, count in data.attempt_distribution) == data.record_count
    # Exactly one persisted duplicate report in the committed release.
    assert data.duplicate_report_count == 1
    # One retried record (accepted_attempt > 0).
    assert data.retry_record_count == 1
    assert len(data.retry_record_ids) == 1
    # validation auxiliary not present in the committed v3 release → None.
    assert data.validation_status is None


def test_dungeongen_renders() -> None:
    result = inspect_artifact_figure(
        "artifact:dungeongen/general/v3",
        DUNGEONGEN_GENERATION_SUMMARY_REF,
        artifact_root=_ARTIFACT_ROOT,
        registry=_registry(),
    )
    import matplotlib.figure

    assert isinstance(result.figure, matplotlib.figure.Figure)


# ---------------------------------------------------------------------------
# ObsField generation summary
# ---------------------------------------------------------------------------


def test_obsfield_figure_listed_for_artifact() -> None:
    refs = list_figures_for_artifact(
        "artifact:obsfield/categorical-complete/v1",
        artifact_root=_ARTIFACT_ROOT,
        registry=_registry(),
    )
    assert OBSFIELD_GENERATION_SUMMARY_REF in refs


def test_obsfield_prepared_matches_provenance() -> None:
    data = _prepared("artifact:obsfield/categorical-complete/v1", OBSFIELD_GENERATION_SUMMARY_REF)
    assert isinstance(data, ObsFieldGenerationSummaryData)
    assert data.assignment_protocol == "categorical-random/v1"
    assert data.distribution == "uniform"
    assert data.domain_schema == "rectangular-row-column/v1"
    assert data.domain_height == 30
    assert data.domain_width == 30
    assert data.vocabulary_identity == "obs-vocabulary:anonymous-45/v1"
    assert data.vocabulary_cardinality == 45
    assert data.realization_count == 100
    # Legacy release has no per-record realization_index descriptor; the figure
    # falls back to a deterministic canonical-order ranking → 100 indexes.
    assert len(data.realization_indexes) == 100
    assert data.validation_status is None


def test_obsfield_gallery_deterministic_and_typed() -> None:
    a = _prepared("artifact:obsfield/categorical-complete/v1", OBSFIELD_GENERATION_SUMMARY_REF)
    b = _prepared("artifact:obsfield/categorical-complete/v1", OBSFIELD_GENERATION_SUMMARY_REF)
    assert isinstance(a, ObsFieldGenerationSummaryData)
    assert isinstance(b, ObsFieldGenerationSummaryData)
    assert a.selected_ids == b.selected_ids
    assert len(a.selected_ids) <= 3
    assert len(a.selected_ids) == len(a.selected_fields)
    assert all(isinstance(f, CategoricalField) for f in a.selected_fields)


def test_obsfield_renders() -> None:
    result = inspect_artifact_figure(
        "artifact:obsfield/categorical-complete/v1",
        OBSFIELD_GENERATION_SUMMARY_REF,
        artifact_root=_ARTIFACT_ROOT,
        registry=_registry(),
    )
    import matplotlib.figure

    assert isinstance(result.figure, matplotlib.figure.Figure)


# ---------------------------------------------------------------------------
# Producer-blindness: generic artifact summaries are unchanged
# ---------------------------------------------------------------------------


def test_generic_summaries_receive_plain_tuple_not_source_content() -> None:
    """A figure without surfaces still receives the plain record tuple.

    The generic ``simple-digraph-artifact-summary`` figure declares no
    artifact-metadata surface, so the framework hands its ``select``/``prepare``
    the plain record tuple (``source.content``) — never an
    :class:`ArtifactSourceContent` (Phase-5 § 17).
    """
    from ehp_sn.figures.builtin.simple_digraph_artifact_summary import (
        SIMPLE_DIGRAPH_ARTIFACT_SUMMARY_FIGURE,
    )
    from ehp_sn.figures.service import _handed_source_content

    committed = load_release(_ARTIFACT_ROOT / "dagflow" / "single-terminal" / "v1")
    source = _build_collection_source(committed, "simple-digraph/v1")
    requirement = SIMPLE_DIGRAPH_ARTIFACT_SUMMARY_FIGURE.projection.requirement
    assert requirement.artifact_metadata_surfaces == frozenset()
    handed = _handed_source_content(requirement, source)
    # The generic figure declares no surfaces → handed is the plain tuple.
    assert handed is source.content
    assert type(handed) is tuple
    assert not isinstance(handed, ArtifactSourceContent)
    assert len(handed) == 12000


def test_generic_simple_digraph_summary_still_renders() -> None:
    result = inspect_artifact_figure(
        "artifact:dagflow/single-terminal/v1",
        "figure:simple-digraph-artifact-summary/v1",
        artifact_root=_ARTIFACT_ROOT,
        registry=_registry(),
    )
    import matplotlib.figure

    assert isinstance(result.figure, matplotlib.figure.Figure)
