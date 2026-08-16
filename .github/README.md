# `.github/`

This directory holds GitHub-related CI configuration and the Copilot agent-instruction layer:

```text
.github/
├── agents/               # Custom Copilot agents (`.agent.md`)
├── copilot-instructions.md   # Global Copilot agent instructions (procedural)
├── prompts/              # Reusable Copilot prompts (`.prompt.md`)
├── instructions/         # Path-scoped procedural instructions (`.instructions.md`)
└── workflows/            # CI workflow definitions
```

The Copilot agent layer is the repository's single agent-instruction home (see `docs/invariants.md` DOC-007): agents, prompts, and instructions tell agents how to work with the authorities in `docs/authority.md` and `docs/invariants.md` and never define domain semantics.
Each path-scoped `instructions/*.instructions.md` file carries a `description` (for on-demand discovery) and `applyTo` globs (for explicit file matching); the custom `agents/*` definitions scope tooling and model per role.

This file is a descriptive entry point.
It does not define CI behavior; the workflow definitions under `workflows/` are authoritative for that, and the agent configuration is not semantic authority.
