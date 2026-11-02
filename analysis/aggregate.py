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
