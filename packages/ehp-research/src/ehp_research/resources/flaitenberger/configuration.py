from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from ehp_sn import resources
from ehp_sn.configuration import BoundProducerConfiguration, ConfigurationSchema


@dataclass(frozen=True)
class Configuration:
    """How the acquisition provider is configured.

    The framework owns repository, revision, file selection, and verification
    fields through `HuggingFaceSnapshotConfiguration`; this integration does not
    repeat them.
    """

    dataset: resources.HuggingFaceSnapshotConfiguration


def resolve(document: BoundProducerConfiguration) -> Configuration:
    """Interpret the authored acquisition declaration into typed transport settings.

    The authored declaration keeps its provider-specific shape
    (`[location]`/`[selection]`/`[integrity]`); this hook maps it onto the
    framework-owned transport model so the fields are not redefined here.
    """
    producer = document.producer
    location = _require_table(producer, "location")
    selection = _require_table(producer, "selection")
    integrity = producer.get("integrity", {})
    if not isinstance(integrity, Mapping):
        raise ValueError("the acquisition declaration's [integrity] must be a table")

    dataset: dict[str, object] = {
        "repository": location["repository"],
        "revision": location["revision"],
        "files": _selected_files(selection),
    }
    if "fingerprint" in integrity:
        dataset["fingerprint"] = integrity["fingerprint"]
    if "verify" in integrity:
        dataset["verify"] = integrity["verify"]

    schema = ConfigurationSchema(model=Configuration)
    return schema.resolve(
        document=BoundProducerConfiguration(document.variant, producer={"dataset": dataset})
    )


def _require_table(producer: Mapping[str, object], name: str) -> Mapping[str, object]:
    table = producer.get(name)
    if not isinstance(table, Mapping):
        raise ValueError(f"the acquisition declaration must declare a [{name}] table")
    return table


def _selected_files(selection: Mapping[str, object]) -> list[str]:
    include = selection.get("include", ())
    if not isinstance(include, (list, tuple)):
        raise ValueError("the acquisition declaration's [selection] include must be a list")
    return [str(name) for name in include]


__all__ = ["Configuration", "resolve"]
