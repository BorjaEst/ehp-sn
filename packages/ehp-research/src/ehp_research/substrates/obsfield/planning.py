"""Producer-owned ObsField planning operation.

This module owns the ObsField side of the demonstrated planning boundary: the
typed planning resolver bound to the registered ``substrate:obsfield/v1``
definition. It is supplied to the framework as a :data:`PlanningResolver`
callable via the research planning composition; the framework never imports this
package or reads any ObsField configuration field.

:data:`plan` resolves a generic loaded configuration through
:func:`ehp_research.substrates.obsfield.configuration.resolve_configuration`
and declares the generic planning inputs:

* the effective :class:`ObsFieldConfiguration` (opaque to the framework);
* **no** logical resource requirements — ObsField is procedurally generated over
  a self-contained ambient domain, so it declares ``resources = ()``;
* the family-specific identity-bearing scientific inputs declared by the
  authoritative specification ``docs/docs/research/substrates/obsfield-v1.md``.

It performs no file loading beyond the framework loader, no resource binding,
no generation, and no artifact mutation. Expected output contract is **not**
declared here: it is invariant for the registered definition
(``categorical-field/v1``) and is owned by the definition.
"""

from __future__ import annotations

from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.planning import IdentityInput, PlanningDeclaration

from .configuration import Distribution, resolve_configuration

#: Canonical names of the identity-bearing scientific inputs declared by
#: ``obsfield-v1.md`` § "Family-specific identity inputs", in a stable order.
#: The framework never interprets these; they are producer-owned WHAT-labels.
_IDENTITY_ORDER: tuple[str, ...] = (
    "specification_reference",
    "variant",
    "assignment_protocol",
    "domain_schema",
    "vocabulary_identity",
    "vocabulary_cardinality",
    "distribution",
    "domain_height",
    "domain_width",
    "seed",
    "realization_count",
)


def _distribution_value(distribution: Distribution) -> object:
    """Encode the distribution as one canonical identity value."""
    if distribution == "uniform":
        return "uniform"
    return list(distribution)


def plan(document: LoadedConfiguration) -> PlanningDeclaration:
    """Resolve ``document`` into an ObsField configuration and declare planning inputs.

    This is the typed :data:`~ehp_sn.planning.PlanningResolver` for the
    registered ``substrate:obsfield/v1`` definition.
    """
    configuration = resolve_configuration(document)

    values: dict[str, object] = {
        "specification_reference": "obsfield/v1",
        "variant": configuration.variant,
        "assignment_protocol": configuration.assignment_protocol,
        "domain_schema": configuration.domain_schema,
        "vocabulary_identity": configuration.vocabulary_identity,
        "vocabulary_cardinality": configuration.vocabulary_cardinality,
        "distribution": _distribution_value(configuration.distribution),
        "domain_height": configuration.height,
        "domain_width": configuration.width,
        "seed": configuration.seed,
        "realization_count": configuration.realization_count,
    }
    identity_inputs = tuple(IdentityInput(name=name, value=values[name]) for name in _IDENTITY_ORDER)

    return PlanningDeclaration(
        configuration=configuration,
        resources=(),
        identity_inputs=identity_inputs,
    )


__all__ = ["plan"]
