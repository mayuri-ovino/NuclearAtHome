import unittest

import numpy as np

from analysis.defects import cluster_cutoff, clusters, lattice_sites, wigner_seitz


class TestDefects(unittest.TestCase):
    def test_perfect_lattice_has_no_defects(self):
        sites = lattice_sites("bcc", 3, 3.0)
        self.assertEqual(len(sites), 54)
        vac, inter = wigner_seitz(sites + 0.1, sites, 9.0)
        self.assertEqual((len(vac), len(inter)), (0, 0))

    def test_one_frenkel_pair(self):
        sites = lattice_sites("bcc", 3, 3.0)
        positions = sites.copy()
        positions[0] = sites[5] + [0.5, 0.0, 0.0]
        vac, inter = wigner_seitz(positions, sites, 9.0)
        np.testing.assert_allclose(vac, [sites[0]])
        np.testing.assert_allclose(inter, [sites[5] + [0.5, 0.0, 0.0]])

    def test_clusters_join_across_periodic_boundary(self):
        points = np.array([[0.2, 1, 1], [8.9, 1, 1], [4.5, 4.5, 4.5]])
        self.assertEqual(clusters(points, 1.0, 9.0), [2, 1])
        self.assertEqual(clusters(np.empty((0, 3)), 1.0, 9.0), [])


if __name__ == "__main__":
    unittest.main()


class TestClusterCutoff(unittest.TestCase):
    def test_exact_shell_pairs_join_at_every_temperature(self):
        for a0 in (3.1674, 3.1726, 3.1837):  # measured a0 at 300, 600, 1025 K
            vac = np.array([[0.0, 0.0, 0.0], [a0 * 1.5, a0 * 0.5, a0 * 0.5]])  # 4NN: a0*sqrt(11)/2 apart
            self.assertEqual(clusters(vac, cluster_cutoff("bcc", a0, 4, 0.001), 100.0), [2])
            inter = np.array([[0.0, 0.0, 0.0], [a0, a0, 0.0]])  # 3NN: a0*sqrt(2) apart
            self.assertEqual(clusters(inter, cluster_cutoff("bcc", a0, 3, 0.001), 100.0), [2])
            nn5 = np.array([[0.0, 0.0, 0.0], [a0, a0, a0]])  # 5NN: never joined by a 4NN cutoff
            self.assertEqual(clusters(nn5, cluster_cutoff("bcc", a0, 4, 0.001), 100.0), [1, 1])

    def test_bad_cutoff_inputs_refused(self):
        for shell, tolerance in ((4, 0.05), (0, 0.001), (6, 0.001), (4, 0.0), (4, -0.001)):
            with self.subTest(shell=shell, tolerance=tolerance), self.assertRaises(ValueError):
                cluster_cutoff("bcc", 3.0, shell, tolerance)
