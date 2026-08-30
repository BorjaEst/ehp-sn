"""Figure provider for the ``test-figure-provider`` fixture distribution.

This distribution advertises one provider under the framework figure-provider
entry-point group (``ehp_sn.figures.providers``):

```toml
[project.entry-points."ehp_sn.figures.providers"]
test-provider = "test_figure_provider.provider:figure_provider"
```

A provider is a callable ``(ComponentRegistry) -> None`` that registers the
figures it owns. One entry point is one *provider*, not one figure: this
provider contributes two **test-only** companion ``FigureSpec``s to prove
provider cardinality (Phase-2 § 7, P2-C) and to make ``--figure auto``
ambiguous with the corresponding framework built-in inspectors.

The framework-owned record inspectors (``figure:simple-digraph-inspection/v1``
and ``figure:categorical-field-inspection/v1``) are **built-in figures in
``ehp_sn``**; this fixture does **not** re-register them (that would be a
duplicate canonical identity, rejected by the registry, ``ARCH-003``). Instead
it contributes one compatible test-only figure per contract so the real
installed-provider seam is proven (§ 39) and ambiguity for ``--figure auto`` is
exercised without adding a second production figure (§ 40).

This is explicitly **not** production ``ehp_sn``/``ehp_research`` code. It is a
test fixture distribution used to prove the real installed-provider extension
seam. It stays outside canonical discovery paths of the production framework and
is only visible when installed into the test environment (Phase-2 § 5, § 16.2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, cast

from ehp_sn.contracts.observations import SCHEMA_REF as CATEGORICAL_FIELD_SCHEMA_REF
from ehp_sn.discovery import ComponentRegistry
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

from .graph import DIGRAPH_SUMMARY_REF, register_digraph_summary

#: The canonical reference of the test-only categorical companion figure.
FIELD_SUMMARY_REF = "figure:field-summary/v1"


@dataclass(frozen=True, slots=True)
class FieldSummaryFigure:
    """A test-only companion ``FigureSpec`` compatible with ``categorical-field/v1``.

    Consumes ``categorical-field/v1`` (same role ``field`` as the built-in
    categorical-field inspector) and realizes a minimal text-only summary. Its
    purpose is to make ``--figure auto`` over a categorical-field record
    ambiguous with the built-in inspector (Phase-2 § 40) and to prove the real
    installed-provider seam for a second contract. It is never a second
    production figure.
    """

    ref: ComponentRef = field(default_factory=lambda: ComponentRef.parse(FIELD_SUMMARY_REF))
    kind: str = field(default=FIGURE_KIND)
    projection: _ProjectionPartition = field(
        default_factory=lambda: _ProjectionPartition(
            semantics_version=1,
            preparation_version=1,
            requirement=FigureInputRequirement(
                role="field",
                contract=CATEGORICAL_FIELD_SCHEMA_REF,
            ),
            prepare=_prepare_field_summary,
        )
    )
    visual: _VisualPartition = field(
        default_factory=lambda: _VisualPartition(
            semantics_version=1,
            realize=_realize_field_summary,
        )
    )
    defaults: _DefaultsPartition = field(
        default_factory=lambda: _DefaultsPartition(
            rc_params={"figure.figsize": (5.0, 3.0), "font.size": 9}
        )
    )


def _prepare_field_summary(source: object) -> object:
    """A minimal identity-like prepare exposing the authoritative vocabulary K."""
    from ehp_sn.contracts.observations import CategoricalField, categorical_field

    if isinstance(source, CategoricalField):
        return {"cardinality": source.vocabulary.cardinality}
    if isinstance(source, dict):
        domain = source.get("domain")
        vocabulary = source.get("vocabulary")
        observation_id = source.get("observation_id")
        if not isinstance(domain, dict) or not isinstance(vocabulary, dict):
            raise TypeError("field-summary/v1 source missing authoritative domain/vocabulary")
        if not isinstance(observation_id, (list, tuple)):
            raise TypeError("field-summary/v1 source missing authoritative observation_id")
        from ehp_sn.contracts.observations import AnonymousVocabulary

        field_ = categorical_field(
            _domain_from_decl(domain),
            _vocab_from_decl(vocabulary),
            list(observation_id),
        )
        _ = AnonymousVocabulary
        return {"cardinality": field_.vocabulary.cardinality}
    raise TypeError(f"field-summary/v1 unexpected source type {type(source).__name__}")


def _domain_from_decl(decl: dict):
    from ehp_sn.contracts.domains import rectangular_row_column_domain

    return rectangular_row_column_domain(int(decl["height"]), int(decl["width"]))


def _vocab_from_decl(decl: dict):
    from ehp_sn.contracts.observations import ExternalVocabulary

    kind = decl.get("kind")
    cardinality = decl.get("cardinality")
    if kind == "anonymous":
        from ehp_sn.contracts.observations import AnonymousVocabulary

        return AnonymousVocabulary(identity=decl["identity"], cardinality=int(cardinality))
    if kind == "external":
        return ExternalVocabulary(
            ref=decl["ref"], identity=decl["identity"], cardinality=int(cardinality)
        )
    raise TypeError(f"unknown vocabulary kind {kind!r}")


def _realize_field_summary(projection: FigureProjection) -> Any:
    """A trivial text-only realization."""
    import matplotlib.pyplot as plt

    view = projection.content
    cardinality = cast(dict, view)["cardinality"]
    figure, axes = plt.subplots(1, 1)
    axes.text(0.5, 0.5, f"categorical-field summary: K={cardinality}", ha="center", va="center")
    axes.set_axis_off()
    return figure


#: The test-only companion figures contributed by this distribution's provider
#: (the graph companion is registered via ``register_digraph_summary``).
_PROVIDER_FIGURES: tuple[FigureSpec, ...] = (FieldSummaryFigure(),)


def figure_provider(registry: ComponentRegistry) -> None:
    """Register every figure this distribution owns into ``registry``.

    This is the advertised provider entry point. It registers only **test-only
    companion** figures (``figure:digraph-summary/v1`` over ``simple-digraph/v1``
    and ``figure:field-summary/v1`` over ``categorical-field/v1``) into the
    ordinary component catalogue. The framework built-in record inspectors are
    not re-registered here (``ARCH-003``). Registration uses canonical component
    references; conflicting duplicate canonical references are rejected by the
    registry.
    """
    register_digraph_summary(registry)
    for figure in _PROVIDER_FIGURES:
        registry.register(figure)


__all__ = [
    "DIGRAPH_SUMMARY_REF",
    "FIELD_SUMMARY_REF",
    "FieldSummaryFigure",
    "figure_provider",
]
