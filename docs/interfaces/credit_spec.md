# Credit, PPD, and badges specification

Status: DRAFT

Reference implementation: `stats/ppd.py` (tests in `tests/stats/test_ppd.py`).
Any other implementation must produce identical numbers.

## 1. Base points (server-side only)

Work done by a work unit:

    work = n_atoms × md_steps × cost_factor[potential_id]

Base points:

    base_points = ref_points × work / ref_work

- `cost_factor`: relative cost per atom-step of each potential, measured on the
  reference machine (EAM = 1.0 by definition; ML potentials TODO-CALIBRATE).
- `ref_work`, `ref_points`: the work and points of a reference WU.
  `ref_points` = 1760 (human decision). `ref_work` = work of the 5 keV reference WU by definition:
  250,000 atoms × 30,000 planned steps (10,000 equilibration + 20,000 cascade at the 1 fs maximum) × 1.0 = 7.5e9.
  Adaptive dt makes real step counts higher, so this under-credits rather than over-credits.
- `md_steps` is the planned step count from the WU (or the server-verified
  completed count), never client-claimed time.
- Points are fixed when the WU is created and stored in the WU's `points` field.

## 2. Quick-return bonus (validated results only)

    multiplier = min(cap, max(1, sqrt(k × deadline_s / elapsed_s)))
    awarded    = base_points × multiplier      (if validated, else 0)

- `elapsed_s` is measured by the SERVER (send time to report time).
- `k`, `cap`: TODO-DECIDE. Hosts with trust score below a threshold get multiplier 1.

## 3. TPF and PPD

- **TPF** (Time Per Frame): wall-clock seconds to complete 1% of a WU.
- **Estimated PPD** for one slot:

      PPD = points_per_wu × 86400 / (TPF × 100)

  where `points_per_wu` includes the expected bonus at elapsed = TPF × 100.
- **Machine PPD** = sum of estimated PPD over all slots running concurrently
  (each CPU task slot and each GPU).
- **Actual PPD** = validated points over the last 7 days ÷ 7.

Worked example: 1,000-point WU, TPF = 180 s → PPD = 1000 × 86400 / 18000 = 4,800.

## 4. Badges

| Badge | Condition | Thresholds |
|---|---|---|
| Credit milestones (Lithium → Beryllium → Breeder → Ignition) | Total validated points | TODO-DECIDE |
| Tritium Hunter | Validated trapping WUs | TODO-DECIDE |
| Reliable | Validation rate over last N results | N and rate TODO-DECIDE |
| Veteran | Days active | TODO-DECIDE |
| Discovery (honorary) | See section 5 | — |

## 5. Discovery credit (honorary, no points)

Awarded to the host/user whose result is either:
- used in a published figure, or
- the first confirmed instance of a new defect or trap configuration,

AND confirmed by at least 2 independent trusted hosts or a project cluster run,
AND approved by the project team. Discovery cannot be farmed because the server
assigns all work units; it carries no points.

## 6. Rules
- No cash, crypto, or monetary prizes.
- Daily stats export in standard BOINC XML format.
- All credit changes are logged publicly (aggregate) in the transparency log.
