from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from ehp_sn import RasterTopology


class FlaitenbergerAdapter:
    def load(self, source: Path) -> Iterator[RasterTopology]:
        raise NotImplementedError(
            "flaitenberger decoding requires the external source format specification"
        )
