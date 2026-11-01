#!/usr/bin/env python3
"""Claude Code PreToolUse hook: block edits to FROZEN interface files.

Claude Code sends the tool call as JSON on stdin. If the target file already
exists and is marked frozen, exit with code 2 so the edit is blocked and the
message on stderr is shown to the agent.

A file is frozen if its first 15 lines contain either:
  Status: FROZEN            (Markdown, SQL comments, etc.)
  "_status": "FROZEN"       (JSON)

Only the human unfreezes a file, by changing the status outside Claude Code.
"""
import json
import re
import sys
from pathlib import Path

FROZEN_PATTERN = re.compile(r'(Status:\s*FROZEN|"_status"\s*:\s*"FROZEN")', re.IGNORECASE)


def is_frozen(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            head = "".join(handle.readline() for _ in range(15))
    except (OSError, IsADirectoryError):
        return False
    return bool(FROZEN_PATTERN.search(head))


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # Not our concern; let Claude Code handle malformed input.

    tool_input = payload.get("tool_input") or {}
    file_path = tool_input.get("file_path") or tool_input.get("path")
    if not file_path:
        return 0

    path = Path(file_path)
    if not path.is_absolute():
        cwd = payload.get("cwd") or "."
        path = Path(cwd) / path

    if path.exists() and is_frozen(path):
        print(
            f"Blocked: {file_path} is a FROZEN interface. Do not edit it. "
            "Report the conflict to the main agent; only the human can unfreeze it.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
