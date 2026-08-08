# `.github/`

This directory holds GitHub-specific CI configuration only:

```text
.github/
└── workflows/   # CI workflow definitions
```

Agent configuration — agents, rules, skills, hooks, and handoffs — lives under
[`.claude/`](../.claude/), not here. Do not add agent instructions, prompts, or
Copilot-style configuration to `.github/`.

This file is a descriptive entry point. It does not define CI behavior; the
workflow definitions under `workflows/` are authoritative for that.
