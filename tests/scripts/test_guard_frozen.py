"""Tests for the frozen-interface hook (scripts/guard_frozen.py)."""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOK = ROOT / "scripts" / "guard_frozen.py"
_spec = importlib.util.spec_from_file_location("guard_frozen", HOOK)
guard = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(guard)


class TestRepoFrozenFilesIntact(unittest.TestCase):
    def test_frozen_files_match_manifest(self):
        # Catches frozen-file changes from any route, including merges of subagent branches.
        self.assertEqual(guard.frozen_problems(ROOT), [])


class TestGuardFrozen(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.interfaces = self.root / "docs" / "interfaces"
        self.interfaces.mkdir(parents=True)
        self.spec = self.interfaces / "spec.md"
        self.spec.write_text("# Spec\n\nStatus: FROZEN\n")
        (self.interfaces / "draft.md").write_text("# Draft\n\nStatus: DRAFT\n")
        digest = hashlib.sha256(self.spec.read_bytes()).hexdigest()
        (self.interfaces / "FROZEN.sha256").write_text(
            f"# Status: FROZEN\n{digest}  docs/interfaces/spec.md\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_hook(self, payload):
        payload = {"cwd": str(self.root), **payload}
        env = dict(os.environ, CLAUDE_PROJECT_DIR=str(self.root))
        proc = subprocess.run([sys.executable, "-I", str(HOOK)], input=json.dumps(payload),
                              capture_output=True, text=True, env=env)
        return proc.returncode

    def edit(self, tool_name, **tool_input):
        return self.run_hook({"hook_event_name": "PreToolUse", "tool_name": tool_name,
                              "tool_input": tool_input})

    def after_bash(self):
        return self.run_hook({"hook_event_name": "PostToolUse", "tool_name": "Bash",
                              "tool_input": {"command": "anything"}})

    def test_edit_frozen_blocked_draft_allowed(self):
        self.assertEqual(self.edit("Edit", file_path="docs/interfaces/spec.md"), 2)
        self.assertEqual(self.edit("Write", file_path="docs/interfaces/FROZEN.sha256"), 2)
        self.assertEqual(self.edit("Edit", file_path="docs/interfaces/draft.md"), 0)

    def test_notebook_edit_frozen_blocked(self):
        self.assertEqual(self.edit("NotebookEdit", notebook_path="docs/interfaces/spec.md"), 2)

    def test_frozen_text_outside_interfaces_not_blocked(self):
        (self.root / "notes.md").write_text("Status: FROZEN\n")
        self.assertEqual(self.edit("Edit", file_path="notes.md"), 0)

    def test_bash_leaving_files_intact_passes(self):
        self.assertEqual(self.after_bash(), 0)

    def test_bash_that_changed_frozen_file_is_flagged(self):
        self.spec.write_text("# Spec\n\nStatus: FROZEN\nchanged by sed\n")
        self.assertEqual(self.after_bash(), 2)

    def test_agent_unfreezing_by_status_flip_is_flagged(self):
        self.spec.write_text("# Spec\n\nStatus: DRAFT\n")
        self.assertEqual(self.after_bash(), 2)

    def test_frozen_but_unregistered_is_flagged(self):
        (self.interfaces / "draft.md").write_text("Status: FROZEN\n")
        self.assertEqual(self.after_bash(), 2)

    def test_deleted_frozen_file_is_flagged(self):
        self.spec.unlink()
        self.assertEqual(self.after_bash(), 2)

    def test_malformed_payload_fails_closed(self):
        self.assertEqual(self.run_hook({"hook_event_name": "PreToolUse", "tool_input": "oops"}), 2)


if __name__ == "__main__":
    unittest.main()
