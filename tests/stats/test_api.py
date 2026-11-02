import io
import json
import unittest

from stats.api import make_app


def fake_query(sql, args):
    if "FROM privacy p JOIN wu_results" in sql:  # host 5's owner shows hosts; host 7's does not
        return [(1,)] if args == (5,) else []
    if "FROM privacy WHERE" in sql:  # user 1 consented to stats export, user 2 did not
        return [(1,)] if args == (1,) else []
    if "FROM host_daily" in sql:
        return [("2026-11-01", 10.0, 2, 1, 480.0, 300.0)] if args == (5,) else []
    if "FROM tpf_samples" in sql:
        return [("2026-11-01 10:00", 36.0)]
    if "FROM user_daily" in sql:
        return [("2026-11-01", 10.0, 1.4, 1)]
    if "FROM badges" in sql:
        return [("lithium",)]
    if "sum(points_awarded), 0)" in sql:
        return [(4, 7040.0)]
    if "ORDER BY r.reported_at DESC" in sql:
        return [("WA-0001-00000001", 5000.0, 300.0, 9, 1760.0, "2026-11-02")]
    if "count(DISTINCT host_id)" in sql:
        return [(3,)]
    if "count(*) / 7.0" in sql:
        return [(2.0,)]
    if "FROM science_aggregates" in sql:
        return [("W", "W_EAM_A", 1000.0, 300.0, 4, 2.0, 0.5, 1.1, 2.9, {"1": 3})] if "material_family," in sql else [(1000.0, 300.0, 4)]
    if "SELECT c.snapshot_file" in sql:
        return [("WA-0001-00000001/snap_3", "W", 1000.0, 300.0, 1.4, 2)]
    if "SELECT snapshot_file" in sql:
        return {("WA-0001-00000001",): [("WA-0001-00000001/snap_3",)],
                ("WA-0001-00000003",): [("WA-0001-00000003/..",)]}.get(args, [("../../etc/passwd",)])
    return []


def call(path, method="GET", query="", headers=None):
    app = make_app(fake_query)
    seen = {}
    body = b"".join(app({"REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query,
                         "wsgi.input": io.BytesIO()},
                        lambda status, hdrs: seen.update(status=status, headers=dict(hdrs))))
    if headers is not None:
        headers.update(seen["headers"])
    return seen["status"], body


class TestAPI(unittest.TestCase):
    def test_host(self):
        status, body = call("/api/v1/hosts/5")
        self.assertEqual(status, "200 OK")
        self.assertEqual(json.loads(body)["tpf_history"][0], {"day": "2026-11-01 10:00", "tpf_s": 36.0})

    def test_hidden_host_and_non_consenting_user_404(self):
        self.assertEqual(call("/api/v1/hosts/7")[0], "404 Not Found")
        self.assertEqual(call("/api/v1/users/2")[0], "404 Not Found")

    def test_unknown_host_404(self):
        self.assertEqual(call("/api/v1/hosts/6")[0], "404 Not Found")

    def test_user_has_badges(self):
        self.assertEqual(json.loads(call("/api/v1/users/1")[1])["badges"], ["lithium"])

    def test_summary_and_science(self):
        self.assertEqual(json.loads(call("/api/v1/project/summary")[1])["active_hosts_7d"], 3)
        bins = json.loads(call("/api/v1/science/cascades", query="material=W&energy_bin=500,1500")[1])["bins"]
        self.assertEqual(bins[0]["mean_frenkel"], 2.0)

    def test_summary_totals_and_campaign(self):
        body = json.loads(call("/api/v1/project/summary")[1])
        self.assertEqual((body["total_wus"], body["total_points"]), (4, 7040.0))
        self.assertEqual(body["campaign"]["target_per_bin"], 100)

    def test_recent_workunits_have_no_host_or_user(self):
        wu = json.loads(call("/api/v1/workunits/recent")[1])["workunits"][0]
        self.assertEqual(wu["frenkel_pairs"], 9)
        self.assertFalse({"host_id", "user_id"} & set(wu))

    def test_bad_parameter_400(self):
        self.assertEqual(call("/api/v1/science/cascades", query="energy_bin=abc")[0], "400 Bad Request")

    def test_snapshots(self):
        meta = json.loads(call("/api/v1/cascades/WA-0001-00000001/snapshots")[1])
        self.assertEqual(meta["frenkel_pairs"], 2)
        headers = {}
        status, body = call(meta["files"][0], headers=headers)
        self.assertEqual((status, body), ("200 OK", b""))
        self.assertEqual(headers["X-Accel-Redirect"], "/_results/WA-0001-00000001/snap_3")

    def test_bad_stored_path_never_reaches_nginx(self):
        self.assertEqual(call("/api/v1/cascades/WA-0001-00000002/snapshots/0")[0], "404 Not Found")
        self.assertEqual(call("/api/v1/cascades/WA-0001-00000003/snapshots/0")[0], "404 Not Found")

    def test_read_only_and_no_traversal(self):
        self.assertEqual(call("/api/v1/hosts/5", method="POST")[0], "405 Method Not Allowed")
        self.assertEqual(call("/api/v1/cascades/../../etc/snapshots")[0], "404 Not Found")


if __name__ == "__main__":
    unittest.main()
