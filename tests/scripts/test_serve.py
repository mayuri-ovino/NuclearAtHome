import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import serve


def call(path):
    captured = {}
    body = b"".join(serve.app({"PATH_INFO": path}, lambda status, headers: captured.update(status=status)))
    return captured["status"], body


def make_slot(data: Path, slot: str, wu: str, progress: str) -> Path:
    folder = data / "slots" / slot
    folder.mkdir(parents=True)
    (folder / "in.cascade.lmp").write_text("# template\n")
    (folder / "params.lmp").write_text(f"variable wu_name string {wu}\n")
    (folder / "progress.txt").write_text(progress)
    (folder / "snapshots.dump").write_text("ITEM: TIMESTEP\n")
    (folder / "secret.txt").write_text("not served")
    return folder


class TestLiveView(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.data = Path(tmp.name)
        make_slot(self.data, "3", "WA-0001-00000003", "0.25")
        make_slot(self.data, "7", "WA-0001-00000007", "0.75")
        (self.data / "slots" / "9").mkdir()  # another project's slot: no cascade template
        for name, value in (("BOINC_DATA", [self.data]), ("LIVE_DIR", None)):
            patcher = mock.patch.object(serve, name, value)
            patcher.start()
            self.addCleanup(patcher.stop)

    def test_tasks_listed_most_advanced_first(self):
        status, body = call("/live/tasks.json")
        self.assertEqual(status, "200 OK")
        self.assertEqual([(t["slot"], t["wu"]) for t in json.loads(body)],
                         [("7", "WA-0001-00000007"), ("3", "WA-0001-00000003")])

    def test_only_allowed_files_of_cascade_slots(self):
        self.assertEqual(call("/live/7/progress.txt"), ("200 OK", b"0.75"))
        self.assertEqual(call("/live/7/secret.txt")[0], "404 Not Found")
        self.assertEqual(call("/live/9/progress.txt")[0], "404 Not Found")
        self.assertEqual(call("/live/../7/progress.txt")[0], "404 Not Found")

    def test_api_without_database_is_unavailable_not_an_error(self):
        with mock.patch.dict("os.environ", {"NAH_API_PG_DSN": ""}):
            self.assertEqual(call("/api/v1/project/summary")[0], "503 Service Unavailable")

    def test_missing_boinc_folder_lists_nothing(self):
        with mock.patch.object(serve, "BOINC_DATA", [self.data / "absent"]):
            self.assertEqual(json.loads(call("/live/tasks.json")[1]), [])


if __name__ == "__main__":
    unittest.main()
