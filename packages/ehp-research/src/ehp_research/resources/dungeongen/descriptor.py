from __future__ import annotations

from ehp_sn import ResourceDescriptor


class DungeonGenResource:
    def describe(self) -> ResourceDescriptor:
        return ResourceDescriptor(
            id="dungeongen", version="0.1.14", kind="generator", location="python:dungeongen"
        )
