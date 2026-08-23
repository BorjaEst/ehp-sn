"""Dagflow substrate family container.

Exposes the authoritative ``substrate:dagflow/v1`` definition object
(``DAGFLOW_DEFINITION``) at the discovery level. The definition itself lives in
``definition.py`` with its scientific owner; this package only re-exports it.
"""

from __future__ import annotations

from .definition import DAGFLOW_DEFINITION

__all__ = ["DAGFLOW_DEFINITION"]
