from __future__ import annotations

from ehp_sn import artifacts
from ehp_sn.contracts.data.datasets.sequences import sequence_dataset
from ehp_sn.core import BuildResult

from .configuration import Configuration


def generate(
    config: Configuration,
    *,
    topology: artifacts.ArtifactRef,
    observation: artifacts.ArtifactRef,
) -> BuildResult[sequence_dataset.Artifact]: ...


__all__ = ["generate"]
