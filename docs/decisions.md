---
title: Open design register
authority: descriptive
document_status: specified
---

This document answers one question: **what is not yet decided?**

It is an ordinary open-questions register, not a semantic authority.
`docs/invariants.md` DOC-002 requires conflicting or missing authority to be recorded rather than silently reconciled. This register is where that is recorded.

Entries here are transient. An entry is deleted when the decision is made and the resulting semantics are captured in `docs/authority.md`, `docs/invariants.md`, or the owning specification. This document never becomes the permanent home of a resolved contract.

## Entry format

Each entry states:

- the conflicting or missing claims, with paths;
- the consequence of each interpretation;
- the decision required;
- what must not be done until it is decided.

Identifiers are permanent.
A resolved entry is deleted and its identifier is never reused, so gaps in the sequence are expected and do not indicate a missing record.

## DEC-025 — Raster-topology ambient-domain field name

Conflicting claims:

- `docs/docs/framework/contracts/topology/raster-topology-v1.md` § "Logical record schema" names the authoritative ambient-domain field `extent`.
- The contract-family structural slice places that field as `RasterTopology.domain` in `packages/ehp-sn/src/ehp_sn/contracts/data/structures/topology/raster_topology.py`, matching the composed `categorical_field` field name.

Consequence of each interpretation:

- If the authoritative name is `extent`, the Python attribute must be renamed to match, and any future domain comparison is spelled `topology.extent != field.domain`.
- If the authoritative name is `domain`, `raster-topology-v1.md` needs a field rename, which its own "Evolution → Breaking changes" section makes a breaking contract change.

Decision required: which field name is authoritative for `raster-topology/v1`.

Until decided: `RasterTopology.domain` stays rectangular-only, and no compatibility logic may read either name.

## DEC-026 — Hexagonal ambient-domain schema registration

Conflicting claims:

- `docs/docs/framework/contracts/domains/ambient-domain-v1.md` records the registered domain schemas as `rectangular-grid/v1` with hex "pending", and states that a release containing hex domains does not conform until a canonical hex schema defines its coordinate system, finite shape, shape parameters, canonical position set and enumeration, and `coordinate_structure: hexagonal-lattice`.
- `packages/ehp-sn/src/ehp_sn/contracts/data/structures/domains/hexagonal_grid.py` declares `SCHEMA_REF = "hexagonal-grid"` / `V1 = "hexagonal-grid/v1"`, and the contract-family structural slice now publishes `HexagonalDomain` as one of the closed `domains.Domain` union's alternatives.

Consequence of each interpretation:

- If the union slot does not register a schema, hex declarations remain non-conforming and `HexagonalDomain` is only a payload-free placeholder.
- If the union slot does register a schema, `ambient-domain-v1.md` must state that schema's conformance semantics before any hex record can conform.

Decision required: whether `hexagonal-grid/v1` is a registered schema, and what its coordinate convention, finite shape, shape parameters, and canonical enumeration are.

Until decided: no hex ambient-domain record is conformant, and no contract may rely on a hex position set or position enumeration.
