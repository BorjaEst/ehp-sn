"""Public command-line surface of the ``ehp_sn`` framework.

Exposes the ``ehp-sn`` console entry point (``pyproject.toml``) as ``app``,
and the top-level command groups that orchestrate framework and installed
research definitions (``docs/docs/interfaces/cli/``).

The CLI is an orchestration layer (CLI-001): it exposes and sequences
operations whose scientific semantics are owned by framework and research
specifications. It defines no scientific semantics itself, and it never imports
concrete research packages (``ARCH-001``).
"""

from __future__ import annotations

from .app import app

__all__ = ["app"]
