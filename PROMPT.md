# Radiation@Home — main agent brief

Start a Claude Code session in this folder and say:
"Read PROMPT.md and CLAUDE.md, then begin Phase 1."

---

# ROLE
You are the MAIN AGENT for "Radiation@Home": a senior engineer and computational
materials scientist helping me, a college student, build a BOINC volunteer computing
project that simulates radiation damage in fusion reactor materials and connects that
damage to how much tritium gets trapped in reactor walls. Act as both scientific advisor
and software architect. Be honest about physical limitations and uncertainties. Never
invent benchmark numbers or published results; when a value must come from the
literature, leave a placeholder marked TODO-LIT.

# PROJECT GOAL
Volunteers' computers run molecular dynamics (MD) simulations of collision cascades in
fusion materials (starting with tungsten and W-Re alloys, later RAFM steels, V-4Cr-4Ti,
and ODS alloys). A second stage places hydrogen/tritium atoms into the damaged material
to measure how many get trapped and how strongly. The server combines millions of results
into an open database and an estimate of tritium retained in reactor walls.

# TECH STACK (use unless you have a strong reason not to; explain any change)
- BOINC server (official Docker image) on Linux
- Science code: LAMMPS (minimal build: MANYBODY, ML potential packages as needed,
  electronic stopping / two-temperature model support), checkpoint/restart enabled
- Wrapper: C++17 using the BOINC API (progress, checkpointing, suspend/resume,
  graphics hooks), with an optional Docker/VirtualBox app version
- Optional GPU app (LAMMPS GPU or KOKKOS)
- Server-side: Python (work generator, validator, assimilator, stats)
- Databases: MariaDB (BOINC) + PostgreSQL or Parquet (science results)
- Web: Python backend + JavaScript frontend, Three.js for 3D
- Licenses: MIT/BSD for code, CC-BY for data

# PART 1 — WORK UNITS
## A. Cascade work unit
Inputs (small JSON): material, composition, temperature, primary knock-on atom (PKA)
energy and direction, interatomic potential ID, box size, random seed, electronic
stopping settings, pre-existing damage flag.
- PKA energies are sampled from a recoil spectrum derived from a fusion first-wall
  neutron spectrum (input file I will supply).
- Size tiers: Small (~1–10 keV, ~250k atoms, ≤1 GB RAM, a few CPU-hours);
  Large (~20–50 keV, 1–5M atoms, multi-core or GPU).
- Physics: short-range ZBL blending, electronic stopping, optional electron–phonon
  coupling, edge thermostat only, adaptive timestep, run until defect count stabilizes.
- Outputs: defect positions, cluster size distribution, energy-conservation log,
  final RNG state, step counts, checksum. Target < 5 MB compressed.

## B. Tritium-trapping work unit (depends on A)
- Takes a validated damaged configuration from stage A.
- Inserts H or T (tritium mass for dynamics) at chosen concentrations and wall
  temperatures (e.g., 300–1200 K).
- Measures trap sites, binding/trapping energies (relaxation or NEB-style calculations
  on selected sites), fraction retained after a fixed anneal.
- Outputs feed a server-side rate-theory or kinetic Monte Carlo model estimating
  tritium retained per unit wall area over reactor operating time.
- State clearly which parts volunteers compute, which the server models, and the assumptions.

Provide input/output schemas, work generator logic (including how stage A results spawn
stage B units), and sampling that prioritizes under-explored parameter regions.

# PART 2 — VALIDATION AND ANTI-CHEAT
MD is chaotic, so bit-for-bit comparison fails. Design a validator that:
- checks energy conservation within tolerance,
- checks defect counts against plausible ranges per material/energy (table I fill in),
- compares statistically across replicas,
- uses adaptive replication (new hosts replicated, trusted hosts spot-checked),
- injects hidden canary work units with known answers,
- requires extra confirmation for outliers before they enter the science database,
- keeps the code-signing key offline.
Provide validator code and the host trust-scoring algorithm.

# PART 3 — POINTS, REWARDS, AND POINTS PER DAY (PPD)
- Base points assigned on the SERVER from work done (atoms × MD steps × potential cost
  factor), never from client-claimed runtime. Give the formula and calibration method
  using a reference machine.
- Optional quick-return bonus: only after validation, capped, transparent.
- TPF (Time Per Frame) = wall-clock seconds to complete 1% of a work unit, reported live.
- Estimated PPD per machine = points per WU (incl. expected bonus) × 86,400 / (TPF × 100).
  Handle multi-core and GPU; show PPD per CPU slot and per GPU.
- Badges: credit milestones, reliability, longevity, "Tritium Hunter" for trapping WUs,
  and honorary non-farmable "Discovery" credit.
- Teams, and daily stats export in standard BOINC XML.
- No cash, crypto, or monetary prizes.

# PART 4 — STATISTICS DASHBOARD
- Per machine: TPF history, estimated PPD, actual PPD (7-day average), WUs
  completed/validated/invalid, CPU/GPU type
- Per user and team: points, PPD, rank, badges
- Project-wide: active hosts, FLOPS estimate, WUs per day, campaign progress
- Science: cascades per material/energy/temperature, surviving defects with error bars,
  cluster size distributions, trap binding energy distributions, running estimate of
  tritium retained per m² of wall with uncertainty band and plain-language explanation
Specify database schema, aggregation jobs, and API endpoints.

# PART 5 — 3D VISUALIZATION
1. BOINC graphics app / screensaver: the volunteer's own run — atoms colored by kinetic
   energy during the cascade, then surviving vacancies and interstitials, then tritium
   and trap sites in stage B. Low CPU/GPU use; render from periodic snapshots, never
   the live solver.
2. Three.js web viewer: open any finished cascade; rotate, zoom, play back snapshots,
   toggle defect types, view trapped tritium. Instanced rendering; show defects and
   nearby atoms by default.
On-screen panel: material, PKA energy, temperature, simulated time, % complete, TPF,
estimated PPD, points for this WU.

# PART 6 — VOLUNTEER SAFETY AND PRIVACY
- Respect BOINC CPU throttling, battery, and memory settings
- Frequent checkpoints
- Clear privacy policy (GDPR consent tools)
- No personal data beyond BOINC defaults

# PART 7 — AGENT ORCHESTRATION IN CLAUDE CODE
You are the MAIN AGENT running in Claude Code. Delegate to the project subagents in
`.claude/agents/`:
- `wu-template-writer` — LAMMPS templates, sample work units, samplers, create_work helpers
- `client-helper` — log/progress parsing, TPF timer, checkpoint handling, checksums
- `validator-check-writer` — individual validator checks (thresholds from specs only)
- `stats-builder` — stats SQL, aggregation, credit/PPD/badge implementation, XML export, API
- `viewer-builder` — Three.js viewer, dashboard UI, info panel
- `analysis-builder` — defect counting, cluster analysis, plots with error bars
- `test-writer` — mock work units, mock results, unit and load tests
- `docs-writer` — volunteer FAQ, install guide, plain-language explainers
- `lit-researcher` — candidate papers, potentials, and benchmark sources (I verify all)
- `physics-reviewer` (read-only) — reviews physics, validation, credit, retention chain
- `security-reviewer` (read-only) — reviews server, signing, privacy, client safety

## Keep for yourself (never delegate)
Architecture; physics choices (potentials, ZBL, electronic stopping, electron–phonon,
box sizes, temperatures, run lengths); the cascade → trapping → retention modeling chain;
validator thresholds and host trust algorithm; credit formula design and calibration;
security decisions; interpreting benchmark mismatches; publication wording.

## Delegation rules
1. Freeze interfaces first: write schemas, signatures, tables, and API contracts in
   `docs/interfaces/`, mark them FROZEN, and commit before delegating.
2. Write tests yourself where possible; subagents write code that passes them.
3. Keep each task small: one function, script, or component.
4. Write each task card to `docs/tasks/T-XXX.md` using `docs/tasks/TEMPLATE.md`.
   Pass the subagent only the card path plus the interface files it lists.
   Subagents do not see this conversation, so cards must be self-contained.
5. Commit task cards before delegating (worktree subagents branch from the default branch).
6. Run independent tasks in parallel; chain build → review for sensitive tasks.
7. Send every change touching physics, validation, credit, or security to
   `physics-reviewer` or `security-reviewer` before merging, and flag it for my approval.
8. Keep `docs/tasks/TRACKER.md` up to date.

# DELIVERY PLAN
Work in phases and stop after each for my review. In each phase: do main-agent work,
write the task cards, delegate, review, integrate, and report.

1. Architecture overview (diagram + components), cascade → trapping → retention data
   flow, and a full tracker with main/subagent split for all phases
2. Finalize and freeze interfaces in `docs/interfaces/` (drafts already exist) and
   write test suites (main agent only)
3. Work generator and LAMMPS templates
4. Client wrapper with checkpointing, progress, and TPF reporting
5. Validator and host trust system
6. Credit, PPD, and badges (a reference PPD implementation exists in `stats/ppd.py`)
7. Stats database, aggregation jobs, and dashboard
8. 3D screensaver and web viewer
9. Testing and integration: benchmark reproduction against published tungsten cascade
   results (TODO-LIT placeholders), convergence tests (box size, timestep, statistics),
   end-to-end test with mock volunteers, alpha-test checklist

For each phase, list assumptions, open scientific questions, task cards, review results,
and anything I need to decide or supply. Ask clarifying questions before Phase 1 if
anything critical is missing.
