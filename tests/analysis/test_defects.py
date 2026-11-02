import unittest

import numpy as np

from analysis.defects import clusters, lattice_sites, wigner_seitz


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
