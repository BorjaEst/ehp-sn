"""Frozen DungeonGen v1 production dependency and reference policy identity.

This module is the single authoritative home for the exact immutable external
generator identity frozen by the Phase 5.3 decision, plus the canonical
reference identities of the EHP-SN generation protocol, first generator
profile, conversion policy, component-selection policy, and acceptance policy.

The upstream revision is verified by direct comparison: every installed
``dungeongen/layout/*.py`` module at package version ``0.1.14`` has a Git blob
SHA equal to the upstream blob at the frozen commit ``2d228f5…``. See
``docs/docs/research/substrates/dungeongen-v1.md`` § "First release dependency
and protocol decision".

A change to the installed ``dungeongen`` code therefore changes the dependency
identity and must be re-frozen under a new revision before it may be used.
"""

from __future__ import annotations

from typing import Final

#: Upstream repository.
UPSTREAM_REPOSITORY: Final = "https://github.com/benjcooley/dungeongen"
#: Installed PyPI package name.
PACKAGE_NAME: Final = "dungeongen"
#: Installed package version.
PACKAGE_VERSION: Final = "0.1.14"
#: Exact upstream Git commit the installed ``0.1.14`` package corresponds to.
UPSTREAM_REVISION: Final = "2d228f5d3f82ccaa4666b087942100e7800fb069"
#: Canonical immutable dependency reference identity.
DEPENDENCY_REFERENCE: Final = f"git:benjcooley/dungeongen@{UPSTREAM_REVISION}"
#: Package-layer pinned dependency.
PACKAGE_DEPENDENCY: Final = f"{PACKAGE_NAME}=={PACKAGE_VERSION}"

#: Reference generation protocol.
PROTOCOL_REFERENCE: Final = "dungeongen/generation/v1"
#: First generator profile.
PROFILE_REFERENCE: Final = "dungeongen/profile/general/v1"
#: Conversion policy.
CONVERSION_POLICY: Final = "dungeongen:conversion/raster/v1"
#: Component-selection policy.
COMPONENT_SELECTION_POLICY: Final = "dungeongen:selection/largest-component/v1"
#: Acceptance policy.
ACCEPTANCE_POLICY: Final = "dungeongen:acceptance/size-and-connected/v1"
#: Randomness role label.
RANDOMNESS_ROLE: Final = "topology-candidate"
#: Canonical lineage schema reference.
LINEAGE_SCHEMA: Final = "dungeongen:lineage/v1"

__all__ = [
    "ACCEPTANCE_POLICY",
    "COMPONENT_SELECTION_POLICY",
    "CONVERSION_POLICY",
    "DEPENDENCY_REFERENCE",
    "LINEAGE_SCHEMA",
    "PACKAGE_DEPENDENCY",
    "PACKAGE_NAME",
    "PACKAGE_VERSION",
    "PROFILE_REFERENCE",
    "PROTOCOL_REFERENCE",
    "RANDOMNESS_ROLE",
    "UPSTREAM_REPOSITORY",
    "UPSTREAM_REVISION",
]
