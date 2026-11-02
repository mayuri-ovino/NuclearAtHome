import tempfile
import unittest
from pathlib import Path

from server.settings import TodoValue, load, require


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.s = {"a": {"b": 3, "todo": "TODO-LIT", "nested": [[1, "TODO-DECIDE"]]}}

    def test_returns_decided_value(self):
        self.assertEqual(require(self.s, "a.b"), 3)

    def test_todo_and_missing_raise(self):
        for key in ("a.todo", "a.nested", "a.missing", "x.y"):
            with self.subTest(key=key), self.assertRaises(TodoValue):
                require(self.s, key)

    def test_repo_settings_fail_closed(self):
        with self.assertRaises(TodoValue):
            require(load(), "badges.veteran_days")

    def test_load_reads_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "s.toml"
            path.write_text("[x]\ny = 1\n")
            self.assertEqual(load(path), {"x": {"y": 1}})


if __name__ == "__main__":
    unittest.main()
