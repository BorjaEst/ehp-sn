"""Producer-owned Dagflow planning declaration capability (Capability 6).

This module owns the Dagflow side of the demonstrated planning boundary: it
exposes the registered ``substrate:dagflow/v1`` definition's planning capability
to the generic framework orchestration, without the framework importing this
package or reading any Dagflow configuration field.

:class:`DagflowPlanningCapability` implements the framework-owned
:class:`~ehp_sn.planning.SubstratePlanningCapability` protocol. Its
:meth:`~DagflowPlanningCapability.plan` resolves a generic loaded configuration
through :func:`ehp_research.substrates.dagflow.configuration.resolve_configuration`
(Capability 5) and declares the generic planning inputs:

* the effective :class:`DagflowConfiguration` (opaque to the framework);
* **no** logical resource requirements — Dagflow v1 is procedurally generated
  and requires no external source, so it declares ``resources = ()``;
* the family-specific identity-bearing scientific inputs declared by the
  authoritative specification ``docs/docs/research/substrates/dagflow-v1.md``.

It performs no file loading beyond Capability 4's loader, no resource binding,
no generation, and no artifact mutation. Expected output contract is **not**
declared here: it is invariant for the registered definition and is owned by the
definition (``simple-digraph/v1``); the plan derives it from the definition so
there is a single authority for it.
"""

from __future__ import annotations

from ehp_sn.configuration import LoadedConfiguration
from ehp_sn.planning import (
    IdentityInput,
    PlanningDeclaration,
    SubstratePlanningCapability,
)

from .configuration import DagflowConfiguration, resolve_configuration

#: Canonical names of the identity-bearing scientific inputs declared by
#: ``dagflow-v1.md`` § "Family-specific identity inputs", in a stable order.
#: The framework never interprets these; they are producer-owned WHAT-labels.
_IDENTITY_ORDER: tuple[str, ...] = (
    "specification_reference",
    "variant",
    "generation_protocol",
    "node_count_policy",
    "additional_edge_probability",
    "splits_train_count",
    "splits_validation_count",
    "splits_test_count",
    "seed",
)


def _node_count_policy(configuration: DagflowConfiguration) -> object:
    """Encode the single active node-count policy as one identity value.

    The Dagflow configuration carries exactly one policy: the fixed ``node_count``
    or the complete bounded triple. Coding the two inactive fields as separate
    identity inputs would make the same effective policy compare unequal across
    the two encodings, so the producer folds them into one canonical value
    (framework-agnostic; the framework only stores it).
    """
    if configuration.node_count is not None:
        return ("fixed", configuration.node_count)
    return (
        "bounded",
        configuration.node_count_minimum,
        configuration.node_count_maximum,
        configuration.node_count_distribution,
    )


class DagflowPlanningCapability(SubstratePlanningCapability):
    """Planning capability for the registered ``substrate:dagflow/v1`` definition."""

    def plan(self, document: LoadedConfiguration) -> PlanningDeclaration:
        """Resolve ``document`` into a Dagflow configuration and declare planning inputs."""
        configuration = resolve_configuration(document)

        values = {
            "specification_reference": "dagflow/v1",
            "variant": configuration.variant,
            "generation_protocol": configuration.generation_protocol,
            "additional_edge_probability": configuration.additional_edge_probability,
            "splits_train_count": configuration.splits_train_count,
            "splits_validation_count": configuration.splits_validation_count,
            "splits_test_count": configuration.splits_test_count,
            "seed": configuration.seed,
        }
        values["node_count_policy"] = _node_count_policy(configuration)

        identity_inputs = tuple(IdentityInput(name=name, value=values[name]) for name in _IDENTITY_ORDER)

        return PlanningDeclaration(
            configuration=configuration,
            resources=(),
            identity_inputs=identity_inputs,
        )


__all__ = ["DagflowPlanningCapability"]
