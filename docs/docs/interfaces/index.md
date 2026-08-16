---
title: Interfaces
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Interfaces

EHP-SN exposes two operational interfaces — Python and CLI — and one shared input surface for configuration.

| Surface           | Role                                                           | Reference                                        |
| ----------------- | -------------------------------------------------------------- | ------------------------------------------------ |
| **Python API**    | Operational: notebooks, scripts, tests, programmatic use       | [Python overview](python/index.md)               |
| **CLI**           | Operational: the `ehp-sn` command for the research lifecycle   | [CLI overview](cli/index.md)                     |
| **Configuration** | Shared serialized input: TOML workspace and operation settings | [Configuration overview](configuration/index.md) |

Python and CLI are equivalent semantic frontends for operations exposed by both interfaces: equivalent inputs converge on the same framework-owned resolution, compatibility checks, and validation rules.
The two interfaces are not required to expose identical operation surfaces — an operation, or an interface-specific convenience such as a CLI flag, may exist on one side only.
Configuration supplies serialized values consumed by those paths; it does not initiate operations independently.

An interface-specific convenience may use its own syntax, but it must resolve into the same framework-owned canonical request/configuration fields the other interface would use — it must not introduce semantics that exist only on one interface.
See [`train --hardware-profile`](cli/train.md) for a convenience option held to this boundary.
