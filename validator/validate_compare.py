"""BOINC script_validator compare script: are two replicas of one WU both acceptable?

Configured as: --compare_script "python3 -I /path/validator/validate_compare.py wu_id runtime files runtime2 files2"
MD is chaotic, so replicas are not compared to each other: each must be consistent
with the bin's population (validator_spec.md). Exit 0 = equivalent, 1 = not.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis.lammps_output import OUTPUT_FILES  # noqa: E402
from server.settings import load, require  # noqa: E402
from validator.checks import zscore  # noqa: E402
from validator.common import bin_population, load_wu, record_for, wu_name_for  # noqa: E402


def consistent(n_frenkel: list[int], population: list[float], sigma: float, min_samples: int) -> bool:
    """Every replica within sigma of the bin; a bin below min_samples accepts all."""
    scores = [zscore(n, population, min_samples) for n in n_frenkel]
    return all(score is None or score <= sigma for score in scores)


def main(argv: list[str]) -> int:
    try:
        settings = load()
        if require(settings, "validator.population_test") != "zscore":
            raise ValueError("only the zscore population test is implemented")
        k = len(OUTPUT_FILES)
        runtime1, files1 = float(argv[2]), argv[3:3 + k]
        runtime2, files2 = float(argv[3 + k]), argv[4 + k:4 + 2 * k]
        wu, _ = load_wu(settings, wu_name_for(int(argv[1])))
        counts = [record_for(settings, f, r)["cascade"]["n_vacancies"] for f, r in ((files1, runtime1), (files2, runtime2))]
        ok = consistent(counts, bin_population(settings, wu),
                        require(settings, "validator.outlier_sigma"), require(settings, "validator.min_bin_samples"))
    except Exception as error:
        print(f"compare error: {error!r}", file=sys.stderr)
        return 3
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
