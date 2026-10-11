from __future__ import annotations

from ehp_sn import ResourceDescriptor


class FlaitenbergerResource:
    def describe(self) -> ResourceDescriptor:
        return ResourceDescriptor(
            id="flaitenberger",
            version="unresolved",
            kind="snapshot",
            location="external:flaitenberger",
        )
