"""Producer-owned DungeonGen planning operation.

This module owns the DungeonGen side of the demonstrated planning boundary: the
typed planning resolver bound to the registered ``substrate:dungeongen/v1``
definition. It is supplied to the framework as a :data:`PlanningResolver`
callable via the research planning composition; the framework never imports
this package or reads any DungeonGen configuration field.

:data:`plan` resolves a generic loaded configuration through
:func:`ehp_research.substrates.dungeongen.configuration.resolve_configuration`
and declares the generic planning inputs:

* the effective :class:`DungeonGenConfiguration` (opaque to the framework);
* **no** logical resource requirements — DungeonGen is procedurally generated
  from the frozen external dependency and the resolved effective parameter
  declaration (EHP-owned defaults applied to user configuration), so it
  declares ``resources = ()``;
* the family-specific identity-bearing scientific inputs declared by the
  authoritative specification ``docs/docs/research/substrates/dungeongen-v1.md``
  § "Family-specific identity inputs".

It performs no file loading beyond the framework loader, no dependency
verification, no generation, and no artifact mutation. Expected output contract
is **not** declared here: it is invariant for the registered definition
(``raster-topology/v1``) and is owned by the definition.
"""

from __future__ import annotations

from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.planning import IdentityInput, PlanningDeclaration

from .configuration import (
    acceptance_policy_value,
    profile_identity_values,
    resolve_configuration,
)

#: Canonical names of the identity-bearing scientific inputs declared by
#: ``dungeongen-v1.md`` § "Family-specific identity inputs", in a stable order.
#: The framework never interprets these; they are producer-owned WHAT-labels.
_IDENTITY_ORDER: tuple[str, ...] = (
    "specification_reference",
    "variant",
    "generator_dependency",
    "generator_protocol",
    "generator_profile",
    "conversion_policy",
    "component_selection_policy",
    "acceptance_policy",
    "duplicate_policy",
    "randomness_role",
    "seed",
    "record_count",
    "attempt_budget",
    "profile",
)


def plan(document: LoadedConfiguration) -> PlanningDeclaration:
    """Resolve ``document`` into a DungeonGen configuration and declare planning inputs.

    This is the typed :data:`~ehp_sn.planning.PlanningResolver` for the
    registered ``substrate:dungeongen/v1`` definition.
    """
    configuration = resolve_configuration(document)

    values: dict[str, object] = {
        "specification_reference": "dungeongen/v1",
        "variant": configuration.variant,
        "generator_dependency": configuration.generator_dependency,
        "generator_protocol": configuration.generator_protocol,
        "generator_profile": configuration.generator_profile,
        "conversion_policy": configuration.conversion_policy,
        "component_selection_policy": configuration.component_selection_policy,
        "acceptance_policy": acceptance_policy_value(configuration),
        "duplicate_policy": configuration.duplicate_policy,
        "randomness_role": configuration.randomness_role,
        "seed": configuration.seed,
        "record_count": configuration.record_count,
        "attempt_budget": configuration.attempt_budget,
        "profile": profile_identity_values(configuration.profile),
    }
    identity_inputs = tuple(IdentityInput(name=name, value=values[name]) for name in _IDENTITY_ORDER)

    return PlanningDeclaration(
        configuration=configuration,
        resources=(),
        identity_inputs=identity_inputs,
    )


__all__ = ["plan"]
