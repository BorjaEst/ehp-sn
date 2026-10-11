from __future__ import annotations

from pathlib import Path

from ehp_sn import ResourceDescriptor


class DungeonGenProvider:
    def acquire(self, resource: ResourceDescriptor, destination: Path) -> Path:
        raise NotImplementedError(
            "dungeongen acquisition requires the external generator implementation"
        )
