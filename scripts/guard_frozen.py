#!/usr/bin/env python3
"""Claude Code hook that protects FROZEN interface files in docs/interfaces/.

Claude Code sends the tool call as JSON on stdin.

- PreToolUse (Edit, Write, MultiEdit, NotebookEdit): if the target is an existing
  frozen file in docs/interfaces/, exit 2 so the edit is blocked.
- PostToolUse (Bash): re-hash every frozen file against the human-maintained
  manifest docs/interfaces/FROZEN.sha256 and exit 2 with the problems if any
  differ. This catches every way a command can change a file (sed, scripts,
  checkouts, merges) without guessing from the command text.

A file is frozen if its first 15 lines contain a status line set to FROZEN, in
Markdown style or JSON style (see FROZEN_PATTERN).

Freezing: the human sets the status line, then appends `sha256sum <file>` output to
the manifest. Unfreezing: the human changes the status back and removes the line.
Both happen outside Claude Code and are committed.
"""
import hashlib
import json
import os
import re
import sys
from pathlib import Path

FROZEN_PATTERN = re.compile(r'(Status:\s*FROZEN|"_status"\s*:\s*"FROZEN")', re.IGNORECASE)
INTERFACES_DIR = "docs/interfaces"
MANIFEST = "FROZEN.sha256"


def is_frozen(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            head = "".join(handle.readline() for _ in range(15))
    except (OSError, IsADirectoryError):
        return False
    return bool(FROZEN_PATTERN.search(head))


def read_manifest(project_dir: Path) -> dict[str, str]:
    """Map 'docs/interfaces/<name>' -> sha256 from the manifest (sha256sum format)."""
    manifest = project_dir / INTERFACES_DIR / MANIFEST
    if not manifest.exists():
        return {}
    entries = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.startswith("#"):
            digest, name = line.split(maxsplit=1)
            entries[name.lstrip("*")] = digest
    return entries


def frozen_problems(project_dir: Path) -> list[str]:
    """Every mismatch between the frozen files on disk and the manifest. Empty means intact."""
    entries = read_manifest(project_dir)
    problems = []
    for path in sorted((project_dir / INTERFACES_DIR).glob("*")):
        name = f"{INTERFACES_DIR}/{path.name}"
        if path.is_file() and path.name != MANIFEST and is_frozen(path) and name not in entries:
            problems.append(f"{name} is marked FROZEN but not registered in {MANIFEST} (the human must register it)")
    for name, digest in entries.items():
        path = project_dir / name
        if not path.is_file():
            problems.append(f"{name} is registered as FROZEN but missing")
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            problems.append(f"{name} is FROZEN but its content changed")
    return problems


def check_edit(tool_input: dict, payload: dict, project_dir: Path) -> int:
    """PreToolUse: block Edit/Write/NotebookEdit on an existing frozen interface file."""
    file_path = tool_input.get("file_path") or tool_input.get("path") or tool_input.get("notebook_path")
    if not file_path:
        return 0
    path = Path(file_path)
    if not path.is_absolute():
        path = Path(payload.get("cwd") or ".") / path
    inside = path.resolve().is_relative_to((project_dir / INTERFACES_DIR).resolve())
    if inside and path.exists() and is_frozen(path):
        print(
            f"Blocked: {file_path} is a FROZEN interface. Do not edit it. "
            "Report the conflict to the main agent; only the human can unfreeze it.",
            file=sys.stderr,
        )
        return 2
    return 0


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0  # Not our concern; let Claude Code handle malformed input.
    try:
        project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or ".")
        if payload.get("hook_event_name") == "PostToolUse":
            problems = frozen_problems(project_dir)
            if problems:
                print("FROZEN interface check failed after this command. Restore the files with "
                      "`git checkout -- <file>` and report to the main agent:\n- " + "\n- ".join(problems),
                      file=sys.stderr)
                return 2
            return 0
        return check_edit(payload.get("tool_input") or {}, payload, project_dir)
    except Exception as error:  # A crashing hook would let the tool call through, so fail closed.
        print(f"guard_frozen error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
