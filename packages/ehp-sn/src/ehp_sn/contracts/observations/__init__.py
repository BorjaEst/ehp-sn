"""Observation contracts (``ehp_sn`` framework-owned).

Subpackage re-exports the observation contract implementations, for example
:class:`~ehp_sn.contracts.observations.categorical_field.CategoricalField`. The
normative semantics live in
``docs/docs/framework/contracts/observations/``.
"""

from __future__ import annotations

from .categorical_field import (
    COVERAGE,
    PERSISTENT,
    SCHEMA_REF,
    VALUE_KIND,
    AnonymousVocabulary,
    CategoricalField,
    CategoricalFieldError,
    ExternalVocabulary,
    Vocabulary,
    categorical_field,
)

__all__ = [
    "COVERAGE",
    "AnonymousVocabulary",
    "CategoricalField",
    "CategoricalFieldError",
    "ExternalVocabulary",
    "PERSISTENT",
    "SCHEMA_REF",
    "VALUE_KIND",
    "Vocabulary",
    "categorical_field",
]
