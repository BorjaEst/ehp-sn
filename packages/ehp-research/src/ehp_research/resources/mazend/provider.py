from __future__ import annotations

from pathlib import Path

from ehp_sn import ResourceDescriptor


class MazeNDProvider:
    def acquire(self, resource: ResourceDescriptor, destination: Path) -> Path:
        raise NotImplementedError("mazend acquisition requires the external source implementation")
