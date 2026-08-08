#!/usr/bin/env bash
# Diagnostic hook: record which instruction files Claude Code loads, and why.
#
# Purpose: settle whether a path-scoped rule under .claude/rules/ fires when a
# governed file is CREATED (Write) rather than READ. The documentation states
# that path-scoped rules "trigger when Claude reads files matching the pattern",
# which leaves greenfield file creation unverified.
#
# Registered against the InstructionsLoaded event with matcher "path_glob_match".
# That event's exit code is ignored; this hook only observes and never blocks.
#
# Read the result with:
#   cut -f2- ~/.claude/ehp-sn-instructions.log | sort | uniq -c

set -uo pipefail

export EHP_INSTRUCTIONS_LOG="${HOME}/.claude/ehp-sn-instructions.log"

python3 -c '
import datetime
import json
import os
import sys

try:
    payload = json.load(sys.stdin)
except Exception:
    raise SystemExit(0)

row = "\t".join(
    [
        datetime.datetime.now().isoformat(timespec="seconds"),
        str(payload.get("load_reason", "?")),
        str(payload.get("file_path", "?")),
    ]
)

with open(os.environ["EHP_INSTRUCTIONS_LOG"], "a", encoding="utf-8") as handle:
    handle.write(row + "\n")
'

exit 0
