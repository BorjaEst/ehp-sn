"""Research-owned DungeonGen generation-summary figure (Phase 5, Stage D).

This module implements ``figure:dungeongen-generation-summary/v1``, a
producer-owned scientific figure in ``ehp_research`` that summarizes one
committed DungeonGen ``raster-topology/v1`` artifact release. It consumes the
same record collection the generic ``figure:raster-topology-artifact-summary/v1``
consumes plus the committed artifact's producer-owned metadata through the
artifact-metadata surfaces (``producer-descriptors``, ``provenance``,
``auxiliary``), and reports **facts** about the configured generation — it
renders no acceptance/rejection verdict (Phase-5 · SRF-019).

Producer identity is a research-owned guard, not a framework detail
(``ARCH-001``): the figure starts by reading the committed provenance's
``specification_reference`` and raises a controlled :class:`TypeError` when it
is not ``dungeongen/v1``. All producer vocabulary here is interpreted only by
this producer-owned figure.

This figure performs no scientific selection (``select=None``): it is a
factual generation summary over the whole committed collection plus its
accepted-attempt/duplicate lineage.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Any, Final, cast

from ehp_sn.contracts.topology import SCHEMA_REF as RASTER_TOPOLOGY_SCHEMA_REF
from ehp_sn.experiments import ComponentRef
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputRequirement,
    FigureSpec,
    _DefaultsPartition,
    _ProjectionPartition,
    _VisualPartition,
)
from ehp_sn.figures.projection import FigureProjection
from ehp_sn.figures.scope import SCOPE_ARTIFACT
from ehp_sn.figures.source import (
    SURFACE_AUXILIARY,
    SURFACE_PRODUCER_DESCRIPTORS,
    SURFACE_PROVENANCE,
)

from ._producer_summary_common import (
    find_auxiliary,
    guard_producer_identity,
    identity_inputs_to_dict,
    record_descriptor,
)

#: The canonical component reference of the DungeonGen generation summary.
DUNGEONGEN_GENERATION_SUMMARY_REF = "figure:dungeongen-generation-summary/v1"

#: The expected producer specification reference for the provenance guard.
_DUNGEONGEN_SPEC_REF = "dungeongen/v1"

#: The projection-semantics version of the generation summary.
_PROJECTION_SEMANTICS_VERSION: Final = 1

#: The preparation-semantics version of the figure.
_PREPARATION_VERSION: Final = 1

#: The visual-semantics version of the figure.
_VISUAL_SEMANTICS_VERSION: Final = 1

#: The artifact-metadata surfaces this producer figure declares.
_METADATA_SURFACES: Final = frozenset(
    {SURFACE_PRODUCER_DESCRIPTORS, SURFACE_PROVENANCE, SURFACE_AUXILIARY}
)

#: The figure's declared metadata surface requirement.
_INPUT_REQUIREMENT = FigureInputRequirement(
    role="dungeongen_generation",
    contract=RASTER_TOPOLOGY_SCHEMA_REF,
    scope=SCOPE_ARTIFACT,
    artifact_metadata_surfaces=_METADATA_SURFACES,
)

#: Private/provisional presentation defaults (never part of projection identity).
_DEFAULT_RC_PARAMS: Final = {
    "figure.figsize": (11.0, 8.0),
    "font.size": 10,
}

#: The lineage auxiliary resource name and its duplicate-report key.
_LINEAGE_RESOURCE = "dungeongen-lineage"
_DUPLICATE_REPORTS_KEY = "duplicate_exact_reports"


@dataclass(frozen=True, slots=True)
class DungeonGenGenerationSummaryData:
    """Stable research-owned prepared view for ``figure:dungeongen-generation-summary/v1``.

    Carries the exact committed values needed to render the summary: the
    authored generator configuration (dependency/protocol/profile/policies/
    budget), the accepted-attempt distribution counted from per-record
    ``accepted_attempt`` descriptors, the retry set, the persisted duplicate
    report count, and the compaction validation status (verbatim, when an
    auxiliary ``dungeongen-validation`` resource exists).

    This view owns no scientific computation — it is assembled by ``prepare()``
    from authoritative committed values only (Phase-5 § 38).
    """

    generator_dependency: Any
    generator_protocol: Any
    generator_profile: Any
    conversion_policy: Any
    component_selection_policy: Any
    acceptance_policy: Any
    duplicate_policy: Any
    record_count: int
    attempt_budget: int
    seed: Any
    attempt_distribution: tuple[tuple[int, int], ...]
    retry_record_ids: tuple[str, ...]
    retry_record_count: int
    duplicate_report_count: int
    validation_status: Any


def _prepare_dungeongen(source: object) -> object:
    """``prepare``: assemble the stable :class:`DungeonGenGenerationSummaryData` view.

    Reads already-authoritative committed values (provenance identity inputs,
    per-record accepted-attempt descriptors, and the persisted lineage's
    duplicate reports) and returns the typed view. It derives no
    acceptance/rejection or data-quality evidence (Phase-5 § 38).
    """
    content = cast(Any, source)
    inputs = identity_inputs_to_dict(content.provenance)
    guard_producer_identity(inputs, _DUNGEONGEN_SPEC_REF, DUNGEONGEN_GENERATION_SUMMARY_REF)

    records = content.records
    attempt_counter: Counter[int] = Counter()
    retry_ids: list[str] = []
    for record in records:
        attempt = record_descriptor(record, "accepted_attempt")
        if attempt is not None:
            attempt_counter[int(attempt)] += 1
        if attempt is not None and int(attempt) > 0:
            retry_ids.append(record.record_id)
    retry_ids.sort()
    attempt_distribution = tuple(sorted(attempt_counter.items()))

    duplicates = _duplicate_report_count(content)
    validation = find_auxiliary(content, "dungeongen-validation")

    return DungeonGenGenerationSummaryData(
        generator_dependency=inputs.get("generator_dependency"),
        generator_protocol=inputs.get("generator_protocol"),
        generator_profile=inputs.get("generator_profile"),
        conversion_policy=inputs.get("conversion_policy"),
        component_selection_policy=inputs.get("component_selection_policy"),
        acceptance_policy=inputs.get("acceptance_policy"),
        duplicate_policy=inputs.get("duplicate_policy"),
        record_count=int(inputs.get("record_count") or 0),
        attempt_budget=int(inputs.get("attempt_budget") or 0),
        seed=inputs.get("seed"),
        attempt_distribution=attempt_distribution,
        retry_record_ids=tuple(retry_ids),
        retry_record_count=len(retry_ids),
        duplicate_report_count=duplicates,
        validation_status=validation.content if validation is not None else None,
    )


def _duplicate_report_count(content: Any) -> int:
    """Count persisted duplicate reports from the lineage auxiliary resource.

    The ``dungeongen-lineage`` resource content is a dict (the persisted
    lineage view); its ``duplicate_exact_reports`` is a list of per-report
    objects recording a duplicate occurrence. The count is the number of those
    reports. If the resource is absent or malformed the count is ``0`` — the
    figure reports facts only and never synthesizes a verdict.
    """
    lineage = find_auxiliary(content, _LINEAGE_RESOURCE)
    if lineage is None:
        return 0
    raw = lineage.content
    if not isinstance(raw, dict):
        return 0
    reports = raw.get(_DUPLICATE_REPORTS_KEY)
    if not isinstance(reports, (list, tuple)):
        return 0
    return len(reports)


def _realize_dungeongen(projection: FigureProjection) -> Any:
    """``realize``: draw configuration text, attempt distribution, retry and duplicates.

    Uses a 2×2 Matplotlib grid of factual panels: generator configuration text,
    the accepted-attempt distribution, a retry-set summary, and the duplicate
    report count. It renders only facts — no pass/fail verdict appears anywhere.
    """
    import matplotlib.pyplot as plt

    data = cast(DungeonGenGenerationSummaryData, projection.content)
    figure, axes = plt.subplots(2, 2, figsize=(11.0, 8.0))

    config_ax, attempt_ax = axes[0]
    retry_ax, duplicate_ax = axes[1]

    _render_config(config_ax, data)
    _render_attempt_distribution(attempt_ax, data)
    _render_retry(retry_ax, data)
    _render_duplicates(duplicate_ax, data)

    figure.suptitle(
        f"DungeonGen raster-topology/v1 generation summary — {data.record_count} records",
        fontsize=12,
    )
    figure.tight_layout(rect=(0, 0, 1, 0.95))
    return figure


def _render_config(ax: Any, data: DungeonGenGenerationSummaryData) -> None:
    """Render the authored generator configuration as factual text rows."""
    ax.axis("off")
    lines = [
        f"generator_dependency: {data.generator_dependency}",
        f"generator_protocol: {data.generator_protocol}",
        f"generator_profile: {data.generator_profile}",
        f"conversion_policy: {data.conversion_policy}",
        f"component_selection_policy: {data.component_selection_policy}",
        f"acceptance_policy: {data.acceptance_policy}",
        f"duplicate_policy: {data.duplicate_policy}",
        f"record_count: {data.record_count}",
        f"attempt_budget: {data.attempt_budget}",
        f"seed: {data.seed}",
    ]
    if data.validation_status is not None:
        if isinstance(data.validation_status, dict):
            for key, value in data.validation_status.items():
                lines.append(f"validation.{key}: {value}")
        else:
            lines.append(f"validation: {data.validation_status}")
    else:
        lines.append("validation: not provided")
    ax.text(
        0.02,
        0.99,
        "\n".join(lines),
        transform=ax.transAxes,
        va="top",
        ha="left",
        family="monospace",
        fontsize=8,
    )
    ax.set_title("generation configuration")


def _render_attempt_distribution(ax: Any, data: DungeonGenGenerationSummaryData) -> None:
    """Render the accepted-attempt distribution as a bar chart (facts only)."""
    attempts = [a for a, _ in data.attempt_distribution]
    counts = [c for _, c in data.attempt_distribution]
    if not attempts:
        ax.text(0.5, 0.5, "no attempt data", transform=ax.transAxes, ha="center", va="center")
    else:
        ax.bar([str(a) for a in attempts], counts, color="#2f6f4f")
        ax.set_xticks(range(len(attempts)), [str(a) for a in attempts])
    ax.set_xlabel("accepted_attempt")
    ax.set_ylabel("records")
    ax.set_title("accepted-attempt distribution")


def _render_retry(ax: Any, data: DungeonGenGenerationSummaryData) -> None:
    """Render the retry-set summary as a factual panel."""
    ax.axis("off")
    lines = [
        f"records with accepted_attempt > 0: {data.retry_record_count}",
    ]
    if data.retry_record_ids:
        lines.append(f"retry record ids ({len(data.retry_record_ids)}):")
        for rid in data.retry_record_ids[:20]:
            lines.append(f"  {rid[:16]}")
        if len(data.retry_record_ids) > 20:
            lines.append(f"  … and {len(data.retry_record_ids) - 20} more")
    else:
        lines.append("no retried records")
    ax.text(
        0.02,
        0.99,
        "\n".join(lines),
        transform=ax.transAxes,
        va="top",
        ha="left",
        family="monospace",
        fontsize=9,
    )
    ax.set_title("retry set summary")


def _render_duplicates(ax: Any, data: DungeonGenGenerationSummaryData) -> None:
    """Render the persisted duplicate-report count as a factual panel."""
    ax.axis("off")
    lines = [f"duplicate reports: {data.duplicate_report_count}"]
    if isinstance(data.validation_status, dict) and "duplicate_report_count" in data.validation_status:
        lines.append(
            f"validation.duplicate_report_count: {data.validation_status['duplicate_report_count']}"
        )
    ax.text(
        0.5,
        0.5,
        "\n".join(lines),
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=12,
    )
    ax.set_title("duplicate reports")


@dataclass(frozen=True, slots=True)
class DungeonGenGenerationSummaryFigure:
    """The ``figure:dungeongen-generation-summary/v1`` reusable scientific figure."""

    ref: ComponentRef = field(
        default_factory=lambda: ComponentRef.parse(DUNGEONGEN_GENERATION_SUMMARY_REF)
    )
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=_PROJECTION_SEMANTICS_VERSION,
            preparation_version=_PREPARATION_VERSION,
            requirement=_INPUT_REQUIREMENT,
            select=None,
            prepare=_prepare_dungeongen,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=_VISUAL_SEMANTICS_VERSION,
            realize=_realize_dungeongen,
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(rc_params=dict(_DEFAULT_RC_PARAMS))
    )


#: The canonical DungeonGen generation-summary figure instance contributed by the provider.
DUNGEONGEN_GENERATION_SUMMARY_FIGURE: FigureSpec = DungeonGenGenerationSummaryFigure()


__all__ = [
    "DUNGEONGEN_GENERATION_SUMMARY_FIGURE",
    "DUNGEONGEN_GENERATION_SUMMARY_REF",
    "DungeonGenGenerationSummaryData",
]
