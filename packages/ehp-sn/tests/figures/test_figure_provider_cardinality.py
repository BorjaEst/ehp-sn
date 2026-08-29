"""Figure provider cardinality, determinism, and failure tests (Phase 2).

These test the framework figure-provider composition surface
(:mod:`ehp_sn.figures.providers`) using **fake/injected entry points** for fast,
exhaustive coverage of provider-ordering, duplicate-identity, cardinality, and
loading/contribution behaviour (Phase-2 § 16.1, § 23).

They verify:

* one provider → zero or more ``FigureSpec``s (provider cardinality, § 7);
* catalogue construction is independent of randomized provider iteration order
  (P2-D / § 8);
* duplicate canonical ``FigureSpec`` identity fails deterministically through
  the ordinary component-catalogue conflict policy — no first/last/built-in/
  external/installation-order wins (P2-E / § 9);
* entry-point-name collisions (provider-discovery) and figure-identity
  collisions (component-authority) stay distinct (P2-7 / § 10);
* provider failures surface through the existing generic provider/catalogue
  failure policy with controlled diagnostics (P2-13 / § 17) — no figure-specific
  plugin lifecycle, retry, quarantine, or recovery.

No Matplotlib backend is needed here (no rendering).
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from importlib import import_module

import pytest
from ehp_sn.discovery import (
    ComponentRegistry,
    DuplicateRegistrationError,
    RegistryError,
)
from ehp_sn.experiments import ComponentRef
from ehp_sn.figures.contracts import (
    FIGURE_KIND,
    FigureInputRequirement,
    _DefaultsPartition,
    _ProjectionPartition,
    _VisualPartition,
)
from ehp_sn.figures.providers import (
    FIGURE_PROVIDER_ENTRY_POINT_GROUP,
    effective_figure_registry,
    register_installed_figure_providers,
)

# ---------------------------------------------------------------------------
# A minimal real FigureSpec used by fake providers
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class _SimpleFigure:
    """A minimal working ``FigureSpec`` for provider/catalogue tests."""

    ref_str: str
    ref: ComponentRef = field(init=False)
    kind: str = field(default=FIGURE_KIND, init=False)
    projection: _ProjectionPartition = field(init=False)
    visual: _VisualPartition = field(init=False)
    defaults: _DefaultsPartition = field(default_factory=_DefaultsPartition)

    def __post_init__(self) -> None:
        object.__setattr__(self, "ref", ComponentRef.parse(self.ref_str))
        object.__setattr__(
            self,
            "projection",
            _ProjectionPartition(
                semantics_version=1,
                preparation_version=1,
                requirement=FigureInputRequirement(role="graph", contract="simple-digraph/v1"),
                prepare=lambda content: content,
            ),
        )
        object.__setattr__(
            self,
            "visual",
            _VisualPartition(semantics_version=1, realize=lambda projection: None),
        )


@dataclass(frozen=True)
class _FakeEntryPoint:
    """Minimal stand-in for ``importlib.metadata.EntryPoint``.

    ``value`` names a ``module:attr`` dotted path; ``load()`` resolves it exactly
    like ``importlib.metadata`` does. The named object must therefore be a
    provider **function** ``(ComponentRegistry) -> None``.
    """

    name: str
    value: str
    group: str = FIGURE_PROVIDER_ENTRY_POINT_GROUP

    def load(self):
        module_name, _, attr = self.value.partition(":")
        return getattr(import_module(module_name), attr)


# ---------------------------------------------------------------------------
# Module-level provider functions referenced by fake entry points
# ---------------------------------------------------------------------------


def _provider_cardinal(registry: ComponentRegistry) -> None:
    """A provider that contributes two figures (cardinality contract test)."""
    registry.register(_SimpleFigure("figure:card-a/v1"))
    registry.register(_SimpleFigure("figure:card-b/v1"))


def _provider_p1(registry: ComponentRegistry) -> None:
    registry.register(_SimpleFigure("figure:prov-a/v1"))
    registry.register(_SimpleFigure("figure:prov-b/v1"))


def _provider_p2(registry: ComponentRegistry) -> None:
    registry.register(_SimpleFigure("figure:prov-c/v1"))
    registry.register(_SimpleFigure("figure:prov-d/v1"))


def _provider_p3(registry: ComponentRegistry) -> None:
    registry.register(_SimpleFigure("figure:prov-e/v1"))
    registry.register(_SimpleFigure("figure:prov-f/v1"))


def _provider_dup(registry: ComponentRegistry) -> None:
    """A provider that registers the shared duplicate identity."""
    registry.register(_SimpleFigure("figure:dup/v1"))


def _provider_foo_a(registry: ComponentRegistry) -> None:
    registry.register(_SimpleFigure("figure:foo-a/v1"))


def _provider_foo_b(registry: ComponentRegistry) -> None:
    registry.register(_SimpleFigure("figure:foo-b/v1"))


def _provider_raises_contribution(registry: ComponentRegistry) -> None:
    """A provider that raises while contributing."""
    raise RuntimeError("boom during contribution")


def _fake_entry_points(*entries: _FakeEntryPoint):
    def _entry_points(*, group: str | None = None) -> list[_FakeEntryPoint]:
        return list(entries)

    return _entry_points


# ---------------------------------------------------------------------------
# Provider cardinality (§ 7): one entry point → zero or more FigureSpecs
# ---------------------------------------------------------------------------


def test_one_provider_can_contribute_multiple_figures(monkeypatch: pytest.MonkeyPatch) -> None:
    """A single provider may register more than one ``FigureSpec``.

    The framework must not encode ``one entry point = one figure`` (§ 7).
    """
    import ehp_sn.discovery.providers as discovery_providers

    monkeypatch.setattr(
        discovery_providers.metadata,
        "entry_points",
        _fake_entry_points(_FakeEntryPoint(name="cardinal", value=f"{__name__}:_provider_cardinal")),
    )
    registry = ComponentRegistry()
    register_installed_figure_providers(registry)
    assert registry.contains("figure:card-a/v1")
    assert registry.contains("figure:card-b/v1")


# ---------------------------------------------------------------------------
# P2-D / § 8 — catalogue determinism under randomized provider order
# ---------------------------------------------------------------------------


def test_catalogue_is_deterministic_under_randomized_provider_order(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every permutation of provider order yields the same canonical catalogue."""
    import ehp_sn.discovery.providers as discovery_providers

    provider_fns = [_provider_p1, _provider_p2, _provider_p3]
    names = ["p1", "p2", "p3"]

    def _build(permutation):
        entries = [
            _FakeEntryPoint(name=names[i], value=f"{__name__}:{provider_fns[i].__name__}")
            for i in permutation
        ]
        monkeypatch.setattr(discovery_providers.metadata, "entry_points", _fake_entry_points(*entries))
        return effective_figure_registry()

    # Reference catalogue from one fixed order.
    reference = _build([0, 1, 2])
    expected = sorted(d.ref.canonical for d in reference.iter(kind="figure"))

    rng = random.Random(20260829)
    for _ in range(30):
        perm = [0, 1, 2]
        rng.shuffle(perm)
        catalogue = _build(perm)
        refs = sorted(d.ref.canonical for d in catalogue.iter(kind="figure"))
        # Same canonical catalogue (component identities + resolved definitions;
        # not object addresses or insertion artifacts).
        assert refs == expected


# ---------------------------------------------------------------------------
# P2-E / § 9 — duplicate canonical FigureSpec identity → deterministic conflict
# ---------------------------------------------------------------------------


def test_duplicate_canonical_figure_identity_fails_deterministically(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two providers contributing the same figure identity → controlled conflict.

    No first/last/built-in/external/alphabetical/installation-order wins (P2-E).
    The error identifies the conflicting canonical identity and never degrades
    into a KeyError or arbitrary replacement.
    """
    import ehp_sn.discovery.providers as discovery_providers

    monkeypatch.setattr(
        discovery_providers.metadata,
        "entry_points",
        _fake_entry_points(
            _FakeEntryPoint(name="a", value=f"{__name__}:_provider_dup"),
            _FakeEntryPoint(name="b", value=f"{__name__}:_provider_dup"),
        ),
    )
    # The second provider's register() of the same canonical identity fails as a
    # controlled duplicate (ARCH-003).
    with pytest.raises(DuplicateRegistrationError) as excinfo:
        effective_figure_registry()
    assert "figure:dup/v1" in str(excinfo.value)


# ---------------------------------------------------------------------------
# P2-7 / § 10 — entry-point-name collision is distinct from figure identity
# collision
# ---------------------------------------------------------------------------


def test_entry_point_name_collision_is_not_a_figure_identity_collision(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Two distributions may share an entry-point name yet contribute distinct figures.

    An entry-point-name collision is a provider-discovery concern, not itself a
    component-authority ambiguity. Two providers contributing *distinct*
    canonical figures under the same entry-point name must coexist.
    """
    import ehp_sn.discovery.providers as discovery_providers

    monkeypatch.setattr(
        discovery_providers.metadata,
        "entry_points",
        _fake_entry_points(
            _FakeEntryPoint(name="foo", value=f"{__name__}:_provider_foo_a"),
            _FakeEntryPoint(name="foo", value=f"{__name__}:_provider_foo_b"),
        ),
    )
    registry = ComponentRegistry()
    register_installed_figure_providers(registry)
    assert registry.contains("figure:foo-a/v1")
    assert registry.contains("figure:foo-b/v1")


# ---------------------------------------------------------------------------
# P2-13 / § 17 — provider failure follows the generic provider/catalogue policy
# ---------------------------------------------------------------------------


def test_provider_that_raises_while_contributing_surfaces_controlled_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A provider raising while contributing is not silently swallowed.

    The failure propagates to the catalogue builder; there is no
    figure-specific quarantine/retry/recovery (P2-13).
    """
    import ehp_sn.discovery.providers as discovery_providers

    monkeypatch.setattr(
        discovery_providers.metadata,
        "entry_points",
        _fake_entry_points(
            _FakeEntryPoint(name="bad", value=f"{__name__}:_provider_raises_contribution")
        ),
    )
    with pytest.raises(RuntimeError):
        effective_figure_registry()


def test_missing_provider_definition_raises_when_loaded(monkeypatch) -> None:
    """A provider entry point that cannot be loaded surfaces a controlled error.

    ``entry_point.load()`` fails (ImportError / AttributeError) — the generic
    provider-loading failure policy; the figure layer adds no retry.
    """
    import ehp_sn.discovery.providers as discovery_providers

    monkeypatch.setattr(
        discovery_providers.metadata,
        "entry_points",
        _fake_entry_points(_FakeEntryPoint(name="missing", value="test_figure_provider.no_such_attr")),
    )
    with pytest.raises((ImportError, AttributeError)):
        effective_figure_registry()


def test_provider_returning_invalid_definition_fails_registry() -> None:
    """A provider registering an invalid definition fails the generic registry.

    A definition whose declared kind disagrees with its reference kind is
    rejected by the ordinary registry (generic consistency invariant), not
    admitted half-way into a successful catalogue.
    """

    class _BadProvider:
        def __call__(self, registry: ComponentRegistry) -> None:
            @dataclass(frozen=True, slots=True)
            class _Bad:
                ref: ComponentRef = field(default_factory=lambda: ComponentRef.parse("figure:x/v1"))
                kind: str = "substrate"

            registry.register(_Bad())

    registry = ComponentRegistry()
    with pytest.raises(RegistryError):
        _BadProvider()(registry)
