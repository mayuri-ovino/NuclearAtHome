"""Reference implementation of Nuclear@Home credit and PPD math.

This file is the reference for docs/interfaces/credit_spec.md. Any other
implementation (SQL, JavaScript) must produce identical numbers.

Calibration constants (ref_points, ref_work, cost factors, bonus k and cap) are
passed in explicitly. Their real values are TODO-DECIDE / TODO-CALIBRATE in the spec.
"""
from __future__ import annotations

import math
from typing import Iterable

SECONDS_PER_DAY = 86_400


def _require_finite(**values: float) -> None:
    """Raise ValueError on NaN or infinity, which would silently corrupt credit totals."""
    bad = [name for name, value in values.items() if not math.isfinite(value)]
    if bad:
        raise ValueError(f"non-finite value for: {', '.join(bad)}")


def work_done(n_atoms: int, md_steps: int, cost_factor: float) -> float:
    """Work for one WU: atoms x steps x relative cost of the potential."""
    _require_finite(n_atoms=n_atoms, md_steps=md_steps, cost_factor=cost_factor)
    if n_atoms <= 0 or md_steps <= 0:
        raise ValueError("n_atoms and md_steps must be positive")
    if cost_factor <= 0:
        raise ValueError("cost_factor must be positive")
    return float(n_atoms) * float(md_steps) * float(cost_factor)


def base_points(n_atoms: int, md_steps: int, cost_factor: float,
                ref_work: float, ref_points: float) -> float:
    """Server-side base points, proportional to work done.

    A WU with exactly ref_work of work earns ref_points.
    """
    _require_finite(ref_work=ref_work, ref_points=ref_points)
    if ref_work <= 0 or ref_points <= 0:
        raise ValueError("ref_work and ref_points must be positive")
    return ref_points * work_done(n_atoms, md_steps, cost_factor) / ref_work


def quick_return_multiplier(elapsed_s: float, deadline_s: float, k: float, cap: float,
                            *, validated: bool, trusted: bool) -> float:
    """Bonus multiplier, min(cap, max(1, sqrt(k * deadline / elapsed))).

    Returns 0 for unvalidated results (no points at all) and 1 for untrusted hosts.
    validated and trusted have no defaults and must be real bools (not a trust score),
    so a caller cannot pay a bonus by omission or by passing the wrong type.
    elapsed_s must be measured by the server, never claimed by the client.
    """
    if not isinstance(validated, bool) or not isinstance(trusted, bool):
        raise TypeError("validated and trusted must be bool")
    if not validated:
        return 0.0
    if elapsed_s <= 0 or deadline_s <= 0:
        raise ValueError("elapsed_s and deadline_s must be positive")
    _require_finite(elapsed_s=elapsed_s, deadline_s=deadline_s, k=k, cap=cap)
    if k <= 0 or cap < 1:
        raise ValueError("k must be positive and cap must be >= 1")
    if not trusted:
        return 1.0
    return min(cap, max(1.0, math.sqrt(k * deadline_s / elapsed_s)))


def awarded_points(base: float, multiplier: float) -> float:
    """Points actually credited for one result."""
    return base * multiplier


def estimated_ppd(points_per_wu: float, tpf_s: float) -> float:
    """Estimated points per day for one slot.

    PPD = points_per_wu * 86400 / (TPF * 100), where TPF is seconds per 1%.
    """
    _require_finite(points_per_wu=points_per_wu, tpf_s=tpf_s)
    if tpf_s <= 0:
        raise ValueError("tpf_s must be positive")
    if points_per_wu < 0:
        raise ValueError("points_per_wu must be non-negative")
    return points_per_wu * SECONDS_PER_DAY / (tpf_s * 100.0)


def estimated_ppd_with_bonus(base: float, tpf_s: float, deadline_s: float,
                             k: float, cap: float, *, trusted: bool) -> float:
    """Estimated PPD including the expected bonus if the WU returns at TPF * 100.

    Display only: never use this to award points.
    """
    elapsed = tpf_s * 100.0
    multiplier = quick_return_multiplier(elapsed, deadline_s, k, cap,
                                         validated=True, trusted=trusted)
    return estimated_ppd(awarded_points(base, multiplier), tpf_s)


def machine_ppd(slot_ppds: Iterable[float]) -> float:
    """Machine PPD is the sum over all concurrently running slots (CPU and GPU)."""
    return float(sum(slot_ppds))


def actual_ppd(validated_points_last_7_days: float) -> float:
    """Actual PPD: validated points over the last 7 days divided by 7."""
    _require_finite(points=validated_points_last_7_days)
    if validated_points_last_7_days < 0:
        raise ValueError("points must be non-negative")
    return validated_points_last_7_days / 7.0
