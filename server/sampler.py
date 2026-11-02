"""Choose WU parameters: the least-sampled bin, a seed, and a PKA direction."""
from __future__ import annotations

import itertools
import math
import random

# Low-index directions <100>, <110>, <111> (all signs and permutations), normalized.
_FAMILIES = [(1, 0, 0), (1, 1, 0), (1, 1, 1)]
LOW_INDEX = sorted({
    tuple(s * c / math.sqrt(sum(x * x for x in fam)) for s, c in zip(signs, perm))
    for fam in _FAMILIES
    for perm in itertools.permutations(fam)
    for signs in itertools.product((1, -1), repeat=3)
})


def pick_bin(counts: dict[tuple[float, float], int], energies: list[float],
             temperatures: list[float], target: int) -> tuple[float, float] | None:
    """The (energy, temperature) bin with the fewest WUs, or None when all reach target."""
    open_bins = [(counts.get((e, t), 0), i, (e, t))
                 for i, (e, t) in enumerate(itertools.product(energies, temperatures))
                 if counts.get((e, t), 0) < target]
    return min(open_bins)[2] if open_bins else None


def angle_to_low_index_deg(direction: tuple[float, float, float]) -> float:
    """Smallest angle between a unit vector and any low-index direction."""
    best = max(sum(a * b for a, b in zip(direction, d)) for d in LOW_INDEX)
    return math.degrees(math.acos(min(1.0, best)))


def sample_direction(rng: random.Random, exclusion_deg: float) -> tuple[float, float, float]:
    """Uniform random unit vector, rejected while within exclusion_deg of a channeling direction."""
    while True:
        v = [rng.gauss(0.0, 1.0) for _ in range(3)]
        norm = math.sqrt(sum(c * c for c in v))
        if norm == 0.0:
            continue
        unit = tuple(c / norm for c in v)
        if angle_to_low_index_deg(unit) >= exclusion_deg:
            return unit


def sample_seed(rng: random.Random) -> int:
    """Seed in the schema's range: LAMMPS aborts above 900000000, and the template uses seed + 1 + restarts."""
    return rng.randint(1, 899_990_000)  # headroom for seed + 1 + restarts
