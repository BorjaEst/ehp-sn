from __future__ import annotations

from ehp_sn import ResourceDescriptor


class MazeNDResource:
    def describe(self) -> ResourceDescriptor:
        return ResourceDescriptor(
            id="mazend", version="unresolved", kind="generator", location="external:mazend"
        )
