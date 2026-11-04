# Nuclear@Home: what it is for, what it can and cannot do

Status: DRAFT (project direction, 2026-11-02). Plain-language version on the website Overview.

## The focus

**Measure how uncertain and how variable primary radiation damage in tungsten really is,
at sample sizes no single research group runs.**

Molecular dynamics (MD) of a single collision cascade is routine: any group with a cluster can
run a few hundred. What nobody can easily afford is the *same* question asked tens of thousands
of times, or asked once for every published interatomic potential. Two things then become
visible that small samples hide:

1. **Model uncertainty.** Published W potentials agree on how many defects a cascade leaves
   but disagree strongly on the *shapes* of the defect clusters (Bhardwaj, Sand & Warrier,
   arXiv:2009.14540, comparing three potentials at 100–200 keV). Every downstream model of
   wall damage inherits that disagreement, usually without error bars.
2. **The tails of the distribution.** Rare events (very large clusters, channeling recoils,
   unusual defect morphologies) are, by definition, poorly sampled by 100 runs per scenario;
   how much they contribute to long-term damage is a question for the models that use this
   data (TODO-LIT: a source for their weight in damage evolution).

That is the project's job: open, reproducible distributions of primary damage in tungsten,
with honest uncertainty bands, for the people who model reactor walls over years.

## Why volunteers win here, and only here

Each cascade is an independent job that fits a volunteer computer. Measured on this project:

| Work unit | Atoms | Time | Memory | Upload |
|---|---|---|---|---|
| 5 keV, one CPU core | 250,000 | 1.6 h (5,800 s) | 314 MB | 3.8 MB |
| 5 keV, RTX 4070 laptop GPU (+1 core) | 250,000 | 30 min | 0.54 GB host RAM | 3.8 MB |
| 10 keV, one CPU core | 843,750 | being measured (estimate 5–6 h) | — | — |

Jobs need no communication with each other, checkpoint every ~5 minutes, survive restarts and
are replicated, so ordinary home computers are enough. Volunteer capacity scales with the
number of computers. For example (estimate): 100 volunteers giving 8 cores each run
about 500 five-keV cascades per hour, 12,000 per day, which matches the sample sizes this
plan needs and would cost a single group a large cluster allocation for weeks.

## What it can do

- **Large ensembles of single cascades** at fixed energy and temperature: Frenkel-pair counts,
  vacancy and interstitial cluster sizes, and (with the Bhardwaj-style analysis) cluster shapes,
  each as a full distribution with confidence intervals.
- **Compare interatomic potentials** on the same scenarios (energy, temperature, random PKA
  directions), run by the same code with the same settings, so differences come from the
  potentials, not from the simulation setup. Pairing the same directions across potentials would
  sharpen the comparison further (a Campaign 2 design decision).
- **Sample rare events** by sheer volume: the size distribution's tail, channeling, rare
  cluster types.
- **Cover a grid of conditions:** PKA energies from about 1 keV to 10–20 keV (box size and
  memory set the ceiling, below) and wall-relevant temperatures (300, 600 and 1025 K now).
- **Publish an open dataset** with full provenance: every result is validated, replicated,
  traceable to its input, potential and code version, and re-analysable later.
- **Run on Linux and Windows,** on CPU cores and NVIDIA GPUs (OpenCL, double precision).

## What it cannot do

- **No single big simulation.** Each work unit runs on one computer; volunteers cannot be
  linked into one parallel job. Box size is limited by volunteer memory and time: about
  1.3 KB of RAM per atom, so roughly 1–2 million atoms (≈ 15–25 keV cascades) is a
  practical ceiling (estimate). 100 keV and above, where cascades split into subcascades,
  need clusters.
- **No time beyond picoseconds.** Each run follows the cascade for 20 ps (after a 10 ps
  thermal warm-up). Damage build-up over months and years, cascade overlap at high dose, and defect
  migration all need other methods (kinetic Monte Carlo, cluster dynamics) that *use* this
  project's output as input. The project does not run them.
- **No tritium inventory.** The headline number, "tritium retained in a reactor wall", needs
  transport and time-evolution models outside MD. This project can at most supply trapping
  statistics for damaged tungsten (a planned later stage), never the inventory itself.
- **No experimental truth.** No facility yet produces fusion neutrons at reactor flux. Every
  result is a model prediction, validated against other simulations, never against a wall.
- **No better physics than the potentials.** Results are only as good as the interatomic
  potentials. The project measures *how much* they disagree; it cannot say which one is right.
- **No alloys or transmutation yet.** Real walls turn partly into Re and Os over years; a
  material is added only when a published, cascade-tested potential exists for it
  (`docs/limitations.md`).
- **No speed for urgent work.** Throughput depends on volunteers' spare time; results arrive
  over days to weeks, not hours.

## Campaigns, in order

| # | Campaign | Question | Gate to start |
|---|---|---|---|
| 1 | **Validation** (running) | Does the pipeline reproduce published W cascades? 5 and 10 keV at 300, 600, 1025 K with the JW potential, 100 runs each. | Done when results match Warrier & Bhardwaj and Setyawan within their error bars. |
| 2 | **Potential uncertainty** | How much do primary damage and cluster shapes depend on the potential? Same scenarios with several published W potentials (e.g. the three compared by Bhardwaj et al.: JW, DND-BN, M-S), ~1,000+ runs each. | Campaign 1 passed; each potential obtained, cascade-tested (short-range join) and given measured a0(T) and validation ranges; cluster-shape analysis added. |
| 3 | **Distribution tails** | What are the rare outcomes, and the tail of the cluster-size distribution? 10,000+ runs in selected bins. | Campaign 2's best-understood potentials; storage plan for the larger dataset. |
| 4 | **Higher energies** | 15–25 keV, toward the subcascade regime, within volunteer memory. | 10 keV calibration; GPU memory and run time measured at the larger boxes. |
| 5 | **Hydrogen/tritium trapping** | How strongly do the damaged structures trap H? | A tested W–H potential, the trapping-stage design (`docs/interfaces/retention_chain.md`). |

What every campaign needs from people, not code: a researcher in fusion materials to frame the
questions and vouch for the results (TODO item 13), and the human approval of each physics
choice that the project rules require.
