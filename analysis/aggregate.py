"""Science aggregates: mean, standard error and a bootstrap 95% interval, with n."""
from __future__ import annotations

import numpy as np


def summarize(values: list[float], bootstrap_samples: int, seed: int = 0) -> dict:
    """Mean, standard error, bootstrap 95% CI of the mean, and sample size.

    The bootstrap uses a fixed seed so published aggregates are reproducible.
    """
    x = np.asarray(values, dtype=float)
    n = len(x)
    if n == 0:
        return {"n": 0, "mean": None, "se": None, "ci95": None}
    mean = float(x.mean())
    if n == 1:
        return {"n": 1, "mean": mean, "se": None, "ci95": None}
    se = float(x.std(ddof=1) / np.sqrt(n))
    rng = np.random.default_rng(seed)
    means = rng.choice(x, size=(bootstrap_samples, n), replace=True).mean(axis=1)
    low, high = np.percentile(means, [2.5, 97.5])
    return {"n": n, "mean": mean, "se": se, "ci95": [float(low), float(high)]}


def exact_interval(k: int, n: int) -> tuple[float, float]:
    """95% Clopper-Pearson interval for a fraction k/n: never below its nominal coverage, which
    matters for rare events (Wilson's coverage dips near 0, Brown, Cai & DasGupta 2001)."""
    from scipy.stats import beta
    low = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    high = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return low, high


def percentile(sorted_values: np.ndarray, q: float, min_beyond: int) -> dict | None:
    """Nearest-rank q-quantile with a distribution-free 95% interval from binomial order
    statistics; None unless at least min_beyond values lie above it (else p99 of 50 runs is
    just the maximum), or if the interval would need ranks outside the sample."""
    from scipy.stats import binom
    n = len(sorted_values)
    rank = int(np.ceil(round(q * n, 9)))  # 1-based; rounding avoids 100*(1-0.9) = 9.999...
    if n - rank < min_beyond:
        return None
    low = int(binom.ppf(0.025, n, q))
    high = int(binom.ppf(0.975, n, q)) + 1
    if low < 1 or high > n:
        return None
    return {"value": int(sorted_values[rank - 1]), "ci95": [int(sorted_values[low - 1]), int(sorted_values[high - 1])]}


def clusters_per_cascade(cluster_lists: list[list[int]], size: int, samples: int, min_cascades: int,
                         seed: int = 0) -> dict:
    """Mean number of clusters of at least `size` per cascade (the source term a cluster-dynamics
    model needs), with a bootstrap 95% interval that resamples whole cascades, because clusters
    of one cascade are correlated. The bootstrap says nothing when few cascades hold such a
    cluster (0 of 100 gives [0, 0]), so below min_cascades the interval is None and only the
    number of cascades with one is given; the share-of-cascades row has the exact interval."""
    per = np.array([sum(1 for s in sizes if s >= size) for sizes in cluster_lists], dtype=float)
    with_one = int((per > 0).sum())
    out = {"size": size, "mean": float(per.mean()), "cascades_with_one": with_one, "ci95": None}
    if with_one >= min_cascades and len(per) > 1:
        rng = np.random.default_rng(seed)
        means = per[rng.integers(0, len(per), size=(samples, len(per)))].mean(axis=1)
        out["ci95"] = [float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))]
    return out


def tails(frenkel: list[int], int_clusters: list[list[int]], vac_clusters: list[list[int]],
          boundary_hit: list[bool], thresholds: list[int], min_beyond: int, bootstrap_samples: int) -> dict:
    """Rare-event statistics of one bin (Campaign 3), one value per independent cascade:
    Frenkel-pair percentiles with intervals, the share of cascades whose largest interstitial
    (vacancy) cluster reaches each size (exact interval), the mean number of such clusters per
    cascade (cascade bootstrap), and how many runs had a recoil reach the boundary layers, in
    total and within each tail cell (large cascades are the ones likeliest to reach it).
    Intervals are per cell (95% each), not simultaneous across a table."""
    n = len(frenkel)
    if n == 0:
        return {"n": 0}
    hits = np.asarray(boundary_hit, dtype=bool)
    counts = np.asarray(frenkel)
    x = np.sort(counts)
    out = {"n": n, "boundary_hits": int(hits.sum()), "frenkel": {"largest_of_n": int(x[-1])}}
    for name, q in (("p50", 0.5), ("p90", 0.9), ("p99", 0.99)):
        p = percentile(x, q, min_beyond)
        if p is not None:  # boundary hits among the cascades above this percentile
            p["boundary_hits_above"] = int(hits[counts > p["value"]].sum())
        out["frenkel"][name] = p
    for name, lists in (("interstitial", int_clusters), ("vacancy", vac_clusters)):
        largest = np.array([max(sizes, default=0) for sizes in lists])
        rows = []
        for size in thresholds:
            reach = largest >= size
            k = int(reach.sum())
            rows.append({"size": size, "count": k, "fraction": k / n, "ci95": list(exact_interval(k, n)),
                         "boundary_hits": int(hits[reach].sum())})
        out[f"largest_{name}_cluster_at_least"] = rows
        out[f"{name}_clusters_per_cascade_at_least"] = [
            clusters_per_cascade(lists, s, bootstrap_samples, min_beyond) for s in thresholds]
    return out
