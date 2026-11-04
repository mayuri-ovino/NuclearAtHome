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


Bin = tuple[str, float, float]  # (potential_id, PKA energy eV, temperature K)


def campaign_bins(potentials: list[str], energies: list[float], temperatures: list[float],
                  default_target: int, bin_targets: list[dict]) -> dict[Bin, int]:
    """Every (potential, energy, temperature) bin with its target: the campaign default, or a
    larger per-bin target (Campaign 3, distribution tails) for the listed bins."""
    if default_target <= 0:
        raise ValueError("target_per_bin must be positive")
    targets = {bin_: default_target for bin_ in itertools.product(potentials, energies, temperatures)}
    seen = set()
    for extra in bin_targets:
        bin_ = (extra["potential_id"], float(extra["energy_ev"]), float(extra["temperature_k"]))
        if bin_ not in targets:
            raise ValueError(f"bin_targets entry {bin_} is not a campaign bin")
        if bin_ in seen:
            raise ValueError(f"bin_targets lists {bin_} twice")
        if int(extra["target"]) < default_target:
            raise ValueError(f"bin_targets may only raise a target: {bin_}")
        seen.add(bin_)
        targets[bin_] = int(extra["target"])
    return targets


def pick_bin(counts: dict[Bin, int], targets: dict[Bin, int]) -> Bin | None:
    """The open bin furthest from its target (fewest WUs relative to target), or None when all
    are full. Relative, so a 10,000-run tail bin does not starve the 100-run bins."""
    open_bins = [(counts.get(bin_, 0) / target, i, bin_)
                 for i, (bin_, target) in enumerate(targets.items()) if counts.get(bin_, 0) < target]
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
