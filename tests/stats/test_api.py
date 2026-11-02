import io
import json
import unittest

from stats.api import make_app


def fake_query(sql, args):
    if "FROM host_daily" in sql:
        return [("2026-11-01", 10.0, 2, 1, 480.0, 300.0)] if args == (5,) else []
    if "FROM tpf_samples" in sql:
        return [("2026-11-01 10:00", 36.0)]
    if "FROM user_daily" in sql:
        return [("2026-11-01", 10.0, 1.4, 1)]
    if "FROM badges" in sql:
        return [("lithium",)]
    if "count(DISTINCT host_id)" in sql:
        return [(3,)]
    if "count(*) / 7.0" in sql:
        return [(2.0,)]
    if "FROM science_aggregates" in sql:
        return [("W", "W_EAM_A", 1000.0, 300.0, 4, 2.0, 0.5, 1.1, 2.9, {"1": 3})] if "material_family," in sql else [(1000.0, 300.0, 4)]
    if "SELECT c.snapshot_file" in sql:
        return [("/srv/x/snap", "W", 1000.0, 300.0, 1.4, 2)]
    if "SELECT snapshot_file" in sql:
        return [("/srv/x/snap",)]
    return []


def call(path, method="GET", query=""):
    app = make_app(fake_query, read_file=lambda p: b"ITEM: TIMESTEP\n")
    seen = {}
    body = b"".join(app({"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query,
                         "wsgi.input": io.BytesIO()}, lambda status, headers: seen.update(status=status)))
    return seen["status"], body


class TestAPI(unittest.TestCase):
    def test_host(self):
        status, body = call("/api/v1/hosts/5")
        self.assertEqual(status, "200 OK")
        self.assertEqual(json.loads(body)["tpf_history"][0]["tpf_s"], 36.0)

    def test_unknown_host_404(self):
        self.assertEqual(call("/api/v1/hosts/6")[0], "404 Not Found")

    def test_user_has_badges(self):
        self.assertEqual(json.loads(call("/api/v1/users/1")[1])["badges"], ["lithium"])

    def test_summary_and_science(self):
        self.assertEqual(json.loads(call("/api/v1/project/summary")[1])["active_hosts_7d"], 3)
        bins = json.loads(call("/api/v1/science/cascades", query="material=W&energy_bin=500,1500")[1])["bins"]
        self.assertEqual(bins[0]["mean_frenkel"], 2.0)

    def test_bad_parameter_400(self):
        self.assertEqual(call("/api/v1/science/cascades", query="energy_bin=abc")[0], "400 Bad Request")

    def test_snapshots(self):
        meta = json.loads(call("/api/v1/cascades/WA-0001-00000001/snapshots")[1])
        self.assertEqual(meta["frenkel_pairs"], 2)
        status, body = call(meta["files"][0])
        self.assertEqual((status, body), ("200 OK", b"ITEM: TIMESTEP\n"))

    def test_read_only_and_no_traversal(self):
        self.assertEqual(call("/api/v1/hosts/5", method="POST")[0], "405 Method Not Allowed")
        self.assertEqual(call("/api/v1/cascades/../../etc/snapshots")[0], "404 Not Found")


if __name__ == "__main__":
    unittest.main()
