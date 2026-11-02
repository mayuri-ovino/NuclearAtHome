"""Wigner-Seitz defect analysis and defect clustering, on the server.

For a Bravais lattice such as bcc, the Wigner-Seitz cell of a site is the region
closer to it than to any other site, so assigning every atom to its nearest perfect
lattice site is an exact Wigner-Seitz analysis.
"""
from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree

BASIS = {"bcc": [(0, 0, 0), (0.5, 0.5, 0.5)],
         "fcc": [(0, 0, 0), (0.5, 0.5, 0), (0.5, 0, 0.5), (0, 0.5, 0.5)]}


def lattice_sites(lattice: str, cells: int, a0: float) -> np.ndarray:
    """Perfect-lattice site positions for a cubic box of cells^3 unit cells."""
    grid = np.stack(np.meshgrid(*[np.arange(cells)] * 3, indexing="ij"), axis=-1).reshape(-1, 3)
    return np.concatenate([(grid + np.array(b)) * a0 for b in BASIS[lattice]])


def wigner_seitz(positions: np.ndarray, sites: np.ndarray, box_length: float) -> tuple[np.ndarray, np.ndarray]:
    """Vacancy positions (empty sites) and interstitial positions (extra atoms per site).

    At a site holding k > 1 atoms, the k - 1 atoms farthest from the site are interstitials.
    """
    tree = cKDTree(sites % box_length, boxsize=box_length)
    dist, idx = tree.query(positions % box_length)
    occupancy = np.bincount(idx, minlength=len(sites))
    vacancies = sites[occupancy == 0]
    extra = []
    for site in np.flatnonzero(occupancy > 1):
        members = np.flatnonzero(idx == site)
        extra.extend(members[np.argsort(dist[members])][1:])
    return vacancies, positions[np.array(extra, dtype=int)] % box_length


def clusters(points: np.ndarray, cutoff: float, box_length: float) -> list[int]:
    """Cluster sizes (descending): points closer than cutoff, with periodic images, join."""
    n = len(points)
    if n == 0:
        return []
    parent = list(range(n))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, j in cKDTree(points % box_length, boxsize=box_length).query_pairs(cutoff):
        parent[find(i)] = find(j)
    sizes = np.bincount([find(i) for i in range(n)])
    return sorted((int(s) for s in sizes if s > 0), reverse=True)


def final_defects(frame: dict, *, lattice: str, cells: int, a0: float) -> tuple[np.ndarray, np.ndarray, float]:
    """Vacancies, interstitials and box length from the final.dump frame."""
    lengths = frame["bounds"][:, 1] - frame["bounds"][:, 0]
    box_length = float(lengths[0])
    if not np.allclose(lengths, box_length * np.ones(3)) or not np.isclose(box_length, cells * a0):
        raise ValueError("final box does not match the WU's lattice")
    cols = frame["columns"]
    xyz = frame["data"][:, [cols.index("x"), cols.index("y"), cols.index("z")]] - frame["bounds"][:, 0]
    vacancies, interstitials = wigner_seitz(xyz, lattice_sites(lattice, cells, a0), box_length)
    return vacancies, interstitials, box_length
