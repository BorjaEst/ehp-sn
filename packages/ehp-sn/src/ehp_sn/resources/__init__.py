from __future__ import annotations

from .acquisition import ResourceAcquirer, ResourceProvider
from .descriptor import GeneratorResource, ResourceDescriptor, SnapshotResource
from .inspection import ResourceInspection, ResourceInspector
from .validation import EXTERNAL_RESOURCE_V1, ResourceDescriptorValidator

__all__ = [
    "EXTERNAL_RESOURCE_V1",
    "GeneratorResource",
    "ResourceAcquirer",
    "ResourceDescriptor",
    "ResourceDescriptorValidator",
    "ResourceInspection",
    "ResourceInspector",
    "ResourceProvider",
    "SnapshotResource",
]
