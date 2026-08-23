"""Workspace-facing reference and resolution package.

This package owns the generic canonical reference representation used across
the framework (``ComponentRef``) and will later own workspace experiment
discovery and resolution (``ExperimentRef`` / ``resolve_experiment``), per
``docs/docs/framework/components/experiment.md`` and the documented Python
surface ``from ehp_sn.experiments import ExperimentRef, resolve_experiment``.

Capability-scoping note: only the generic ``ComponentRef`` reference type is
established here. Workspace experiment discovery and
``ExperimentRef``/``resolve_experiment`` are documented targets (ARCH-014) and
are out of scope for the current capability.
"""

from __future__ import annotations

from .refs import ComponentRef, InvalidReferenceError

__all__ = ["ComponentRef", "InvalidReferenceError"]
