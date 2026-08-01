---
title: Interfaces
authority: normative
document_status: specified
capability_status: planned
api_stability: provisional
---

# Interfaces

EHP-SN exposes two operational interfaces — Python and CLI — and one shared input surface for configuration.

| Surface           | Role                                                           | Reference                                         |
| ----------------- | -------------------------------------------------------------- | ------------------------------------------------- |
| **Python API**    | Operational: notebooks, scripts, tests, programmatic use       | [Python overview](python/_index.md)               |
| **CLI**           | Operational: the `ehp-sn` command for the research lifecycle   | [CLI overview](cli/_index.md)                     |
| **Configuration** | Shared serialized input: TOML workspace and operation settings | [Configuration overview](configuration/_index.md) |

Python and CLI are equivalent operational paths. They resolve through the same package-owned constructors, compatibility checks, and validation rules. Configuration supplies serialized values consumed by those paths; it does not initiate operations independently.
