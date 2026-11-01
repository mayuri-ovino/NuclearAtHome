Status: UNVERIFIED

# Published MD collision-cascade results in tungsten (benchmark candidates)

Prepared 2026-11-01 for section 6 of `docs/interfaces/physics_settings.md` (benchmarks B1, B2 are
W; B3 is Fe and not covered here) and section 2 (electronic effects). Nothing here is approved.
I did not choose benchmark energies, temperatures or potentials; that is for the human.

## How to read the provenance tags

- [FULL-HTML] I opened an HTML (arXiv, ar5iv or journal HTML) rendering of the full text through
  a summarising fetch tool. Numbers are relayed, not read by me from raw text. Re-check before use.
- [PDF-READ] I looked at page images of the PDF myself ("read directly").
- [ABSTRACT/METADATA] Only an abstract or record page was opened.
- [SEARCH-ONLY] Seen only in search-result summaries. NOT opened. Leads only.

Where I give a value, I say where it sits in the paper (table, figure or text) as reported by
the source rendering. "Figure only" means the paper shows the data in a plot and I saw no table
of the values. None of the papers below gave a downloadable data table in the pages I opened.

---

## 1. Primary cascade studies

### 1.1 Setyawan et al. 2015 (Part I: defect database)

- Citation: W. Setyawan, G. Nandipati, K. J. Roche, H. L. Heinisch, B. D. Wirth, R. J. Kurtz,
  "Displacement cascades and defects annealing in tungsten, Part I: defect database from molecular
  dynamics simulations", J. Nucl. Mater. 462, 329-337 (2015), DOI 10.1016/j.jnucmat.2014.12.056
  (DOI and page range from a search result). arXiv:1404.6490, https://arxiv.org/abs/1404.6490
- Tag: [FULL-HTML] (ar5iv). The arXiv rendering lists six authors; one OSTI listing in search
  results lists five. Check the journal record.
- Potential: Juslin-Wirth (2013) W potential, derived from Ackland-Thetford and hardened at short
  distance. No ZBL splice details stated.
- E_d used: 128 eV, determined at 10 K (text).
- PKA energies: 0.1-100 keV, 21 values, about 0.78 to 781 x E_d (Table 1).
- Temperatures: 300, 1025, 2050 K (homologous 0.07, 0.25, 0.5).
- Box size: cubic, 15 to 120 lattice constants per side (Table 1); lattice constants 3.167, 3.184,
  3.216 Å (Table 1).
- Runs per energy: 40 at sub-threshold energies (0.1-0.3 keV), 20 or 15 at higher energies,
  depending on temperature (Table 1).
- Electronic effects: not stated.
- Method: LAMMPS; 30 ps thermalisation at zero pressure with Nose-Hoover; about 10 ps NVE then a
  constant-volume thermostat; typical total run about 50 ps; adaptive step with 0.005 Å maximum
  displacement; displaced atom = more than 0.3 a0 from a lattice site.
- Reported quantities and where:
  - Surviving Frenkel pairs vs PKA energy, two power-law regions: exponent 0.74 below the
    transition at all temperatures; 1.30 above it at 300 K, 1.36 at 1025 and 2050 K (text).
    Transition near 280 E_d at 300 K and 230 E_d at 2050 K (Conclusions); the abstract says about
    250 E_d. Fit coefficients are in Fig. 1a only (figure only). Survival ratio to NRT has a
    minimum of about 0.25 (Fig. 1b). N_F at E* = 1 is about 0.5 (300 K), 0.3 (1025 K), 0.5 (2050 K)
    (text; sub-threshold standard error 0.08).
  - Clustering: SIA cutoff third-nearest-neighbour (NN3), vacancy cutoff NN4 (Fig. 2). SIA
    clustered fraction below 0.5 under the transition at 300 and 1025 K, 0.5-0.7 above, 0.6-0.85 at
    2050 K (Fig. 3a, figure only). Largest SIA cluster up to 5 atoms below the transition; about
    35 / 45 / 55 atoms above it at 300 / 1025 / 2050 K (Fig. 3b). Largest vacancy cluster about
    40-50 at 300 and 1025 K and about 10 at 2050 K (text and Fig. 3b).
  - Temperature trend stated by the authors: SIA clustering grows with temperature, vacancy
    clustering shrinks, so at 2050 K almost no large vacancy clusters form.
  - Loops: 13, 7 and 1 vacancy loops (all <100>{100}) at 300, 1025, 2050 K (text); SIA loop
    partitioning is in Table 2 (tabulated). Majority 1/2<111> at 300 and 1025 K, 3D clusters at
    2050 K.
- Limits: electronic stopping not mentioned; which energy axis (PKA vs damage energy) is plotted
  is not clear from my read.
- Companion Part II (annealing by kinetic Monte Carlo) was seen in search results only.

### 1.2 Sand, Dudarev, Nordlund 2013 (150 keV cascades)

- Citation: A. E. Sand, S. L. Dudarev, K. Nordlund, "High-energy collision cascades in tungsten:
  dislocation loops structure and clustering scaling laws", EPL 103, 46003 (2013). arXiv:1306.3824,
  https://arxiv.org/abs/1306.3824 (journal details from the UKAEA copy filename seen in search
  results).
- Tag: [FULL-HTML] (ar5iv).
- Potentials (PARCAS code): Derlet et al. modified EAM ("D-D"), Ackland-Thetford ("A-T"), and the
  Tersoff-type Ahlgren potential ("A-H"). All were "smoothly fitted" to universal ZBL at short
  distance. Splice range not given in what I read.
- PKA energy: 150 keV in the main study; 100 keV runs without electronic stopping.
- Temperature: 0 K start with a Berendsen thermostat on the cell borders; loops relaxed at 600 K
  for 100 ps. Box size: not stated in the text I retrieved.
- Runs: about 100 in total; Table 1 lists 92 (D-D 67, A-T 20, A-H 5). PKA direction random, plus
  checks within 2 degrees of <100> and <110>.
- Electronic stopping: SRIM-based friction with a low-energy cutoff Tc tested at 1, 5, 10, 20,
  100 eV.
- Reported (Table 1 unless noted): about 120 Frenkel pairs per cascade at Tc = 1 eV and about 200 at
  higher cutoffs; no subcascade break-up at 150 keV, with about 30,000 atoms molten at peak; no
  vacancy clusters at Tc = 1 eV; D-D at Tc = 10 eV has N_SIA about 179, largest SIA cluster 175; D-D
  at 100 keV N_SIA about 250, largest SIA cluster 433; A-T at Tc = 10 eV N_SIA about 124, largest 85;
  A-H largest SIA cluster 41 (little clustering). SIA cluster size distribution follows A/n^S with
  A = 7.45 ± 1.52, S = 1.63 ± 0.07 (Fig. 2). Loop probability above about 3 nm estimated at about 3%.
- Limitations stated: 0 K start may bias clustering; Tc is arbitrary and an electronic-stopping
  threshold in W is unconfirmed; large cascade-to-cascade variation and limited statistics; loop
  identification partly qualitative; extrapolations of the power law.

### 1.3 Zarkadoula et al. 2015 (two-temperature model, 300 keV)

- Citation: E. Zarkadoula, D. M. Duffy, K. Nordlund, M. A. Seaton, I. T. Todorov, W. J. Weber,
  K. Trachenko, "Electronic effects in high-energy radiation damage in tungsten", J. Phys.: Condens.
  Matter 27, 135401 (2015), DOI 10.1088/0953-8984/27/13/135401 (journal and volume from the DOI shown
  on the arXiv abstract page). arXiv:1411.7674, https://arxiv.org/abs/1411.7674
- Tag: [FULL-HTML] (ar5iv) plus arXiv abstract page.
- Potential: modified EAM joined to ZBL by a polynomial spline fitted to experimental threshold
  energies; ZBL parameters not given. One potential only.
- PKA energy 300 keV; temperatures 300 K and 800 K; six random PKA directions per case; about
  30 million atoms (box length about 800 Å); about 10 Å boundary thermostat layer.
- Electronic effects: friction vs 2T-MD. Friction 1.1 ps^-1 from SRIM tables, applied to atoms
  above a velocity set by twice the cohesive energy. 2T-MD: g_p = 7e17 W m^-3 K^-1 (experimental
  range 5-10e17), electronic conductivity 174 W/m/K (300 K) and 125 W/m/K (800 K), electronic heat
  capacity from ab initio data (values not in text), coupling on at 0.3 ps.
- Table 1 (Frenkel pairs by sphere criterion; standard error in brackets): friction 300 K 5500
  (1100); 2T-MD 300 K 1900 (200); friction 800 K 5500 (1700); 2T-MD 800 K 2700 (500).
  Fraction of vacancies in clusters larger than 3: 0.88 / 0.75 / 0.89 / 0.82 in the same column
  order. Largest SIA cluster: 374 / 140 / 317 / 164.
- Text (sec. III.3): the 10 largest interstitial clusters hold 438-1754 SIAs at 300 K and 391-5920 at
  800 K (2T-MD); no vacancy dislocation loops found; about half of large interstitial clusters
  are <111> loops.
- Limitations stated: electronic conductivity probably overestimated in the spike; g_p may be
  too high; parameters not varied widely; boundary thermostat partly reflects energy in friction runs;
  one potential.
- Caution: the fetch output gave text-level ratio statements (final defect ratio friction/2T-MD about 3 at
  300 K and about 2 at 800 K; N_def(300)/N_def(800) = 2.3 without electronic effects) that do not
  match Table 1 (friction 5500 vs 5500 at the two temperatures; 2T-MD 1900 vs 2700). Possibly the
  text ratios refer to peak, not final, counts. The human should read sec. III.1-III.2.

### 1.4 Sheng et al. 2025 (2T-MD parametric study)

- Citation: S. Sheng, S. Wei, C. Zhang, C. Zhang, G. Pu, B.-S. Li, "Effects of electronic excitation
  on cascade dynamics in tungsten", Frontiers in Physics 13, 1592186 (2025),
  doi 10.3389/fphy.2025.1592186. https://www.frontiersin.org/articles/10.3389/fphy.2025.1592186/full
- Tag: [FULL-HTML] (journal HTML).
- Potential: Finnis-Sinclair-type W potential attributed to "Deng et al." in the text; the
  reference-list entry appears to be Chen et al. 2019, so the citation may be inconsistent. ZBL joined
  to it with a connection function; parameters were lost in extraction.
- Setup: LAMMPS two-temperature model; PKA 10-150 keV; direction <135>; 250,000 atoms (50^3 cells)
  and 1,000,000 atoms (80^3 cells); 20 ps NPT at 300 K then NVE, 720,000 steps (about 100 ps);
  max displacement 0.005 Å per step; thermostat layer about 8 Å; at least 10 cascades per
  reported value.
- Electronic parameters: g_p = 5e17 W m^-3 K^-1; kappa_e = 174 W/m/K; electronic heat capacity from
  ab initio source; friction from SRIM; electron density 6/14/28 electrons per W atom tested;
  e-ph coupling activation time 0, 0.1, 0.5, 1.0 ps tested.
- Conditions: temperature 300-1500 K at 150 keV (the text also mentions 900 K).
- Reported: peak and surviving defects vs energy, electron density, temperature, activation time.
  Exact counts are in figures only (Figs 1-3); Table 1 compares low-energy stable Frenkel pairs with
  earlier work but its values were garbled in extraction. No cluster fractions.
- Findings as relayed: peak defects with 2T-MD are much lower than classical MD at high energy;
  surviving defects agree at low energy and diverge at high energy; surviving defects fall with
  temperature in classical MD but stay roughly flat in 2T-MD; later e-ph activation raises both
  peak and surviving counts.
- Limitations: gamma_p, kappa_e and g_p treated as independent of lattice temperature; one
  potential and one direction; no cluster analysis.

### 1.5 Liu et al. 2023 (NEP-ZBL, up to 200 keV, bulk and foils)

- Citation and potential: see the potentials file (item B4). arXiv:2305.08140.
- Tag: [FULL-HTML] (ar5iv).
- PKA energies (Table 1): 1, 5, 10, 20, 30, 40, 50, 100, 200 keV in bulk; 100 and 200 keV foils.
- Temperature: 300 K, 30 ps NPT equilibration at 0 GPa. Bulk cells 30^3 to 150^3 bcc cells (54,000
  to 6,750,000 atoms); foil cells up to 8.1 million atoms. Periodic bulk, free surfaces for foils.
- Runs: each case run 10 times with different PKA selections. Direction fixed at <135>.
- Electronic stopping: none (not implemented in GPUMD).
- Analysis: Wigner-Seitz defect counting, clustering in OVITO, dislocations by DXA.
- Reported:
  - Frenkel pairs vs energy compared with NRT and arc-dpa using E_d = 90 eV (Fig. 8, figure only).
    Fit above threshold N_F = a (E/E_d)^b with a = 0.03, b = 1.25, vs a = 0.02, b = 1.30 for
    Setyawan et al. (text; the data points are in Fig. 8).
  - Subcascade splitting: 70% at 200 keV and 20% at 100 keV (text).
  - Table 5 (tabulated): 100 keV bulk 183 vacancies and 183 interstitials, largest vacancy cluster 97,
    largest interstitial cluster 237, clustered fraction 55% (vacancies) and 86% (interstitials);
    200 keV bulk 329 / 329, largest 457 and 429, clustered 50% and 85%. Foil rows are in the same
    table (100 keV foil 898 vacancies, 61 interstitials; 200 keV foil 1200 and 200).
  - Dislocation densities in text only.
- Limitations: no electronic stopping; one direction; <100> loop in bulk seen in only one of ten
  cascades; stability tested over 1 ns only; the text's "37% and 19%" reductions are percentage-point
  differences in Table 5 (my fetch notes this internal inconsistency).

### 1.6 Warrier and Bhardwaj 2024/2025 (five potentials, 3,500 cascades)

- Citation and potentials: see the potentials file (item A6). arXiv:2402.00359.
- Tag: [FULL-HTML].
- PKA energies 5, 10, 20, 50, 75, 100, 150 keV; 100 PKA directions per energy per potential
  (3,500 runs); 300 K; NPT 10 ps equilibration; NVE up to 20 ps with variable time step; boundary
  cells fixed and two layers thermostatted at 300 K. Electronic stopping: frictional term.
- Box sizes (Table 1): 5 keV 50^3 cells (250,000 atoms); 10 keV 75^3 (843,750); 20 keV 85^3
  (1,228,250); 50 keV 100^3 (2,000,000); 75 keV 125^3 (3,906,250); 100 keV 150^3 (6,750,000);
  150 keV 200^3 (16,000,000).
- Reported: defect counts compared with arc-dpa (Fig. 2, figure only); the text says tabGAP gives the
  fewest defects at all energies and JW and MS agree closely. Clustered fraction about 0.65-0.8 at
  150 keV and 0.45-0.55 at 5 keV (text; Fig. 3), DND-BN highest and MS lowest. Vacancy cluster
  size and in-cluster fraction (Figs 4-5). <111> loops above 80% for JW and tabGAP, about 60% for
  MS and DND-BN, about 15% for WSNAP (text; Figs 6-7). Subcascade counts (Fig. 9). Frenkel-pair
  counts are not reported explicitly. Property comparisons (TDE, formation energies) are in Table 3.
- Limitations: tungsten only, no experimental validation, friction-only electronic effects, 20 ps
  runs, rare channeling; abstract (below 60 keV) and results (below 50 keV) disagree on the
  subcascade threshold.

### 1.7 Byggmästar et al. 2025 ("Four regimes", 40 eV to 2 MeV)

- Citation: J. Byggmästar, V.-M. Yli-Suutala, A. Fellman, J. Åström, J. Westerholm, F. Granberg,
  "Four regimes of primary radiation damage in tungsten", arXiv:2503.02710 (preprint; the page I
  opened shows revision dates in 2026 and no journal reference). https://arxiv.org/abs/2503.02710
- Tag: [FULL-HTML]. The fetch noted broken citation keys, so some references could not be matched.
- Potential: tabGAP, GPU runs in LAMMPS (Kokkos). No ZBL mentioned (the tabGAP uses its own
  repulsion; see the potentials file, item B5). Which W tabGAP version is not stated.
- Electronic stopping: friction above 10 eV from SRIM data.
- Setup (Table 1, Supplement S3): PKA 40 eV to 2 MeV; initial relaxation to 300 K and zero
  pressure; adaptive time step; 50 ps; NVE bulk with 8 Å Nose-Hoover border at 300 K.
  Box edge and atoms as reported: 0.04-0.25 keV 95.6 nm (54e6 atoms); 0.3-1 keV 63.7 nm (16e6);
  2-5 keV 12.74 nm (0.128e6); 10-20 keV 25.5 nm (1.024e6); 50 keV 51.0 nm (8.192e6); 100 keV
  63.7 nm (16e6); 200 keV 95.6 nm (54e6); 300-500 keV 127 nm (128e6); 1-2 MeV 255 nm (1.024e9).
  Runs per energy: 1000 (40-250 eV), 500 (0.3-1 keV), 100 (2-50 keV), 50 (200-500 keV), 20
  (1-2 MeV); random directions.
- Reported: Frenkel pairs vs PKA and damage energy (Fig. 2, figure only); max and mean vacancy and
  SIA cluster size and clustered fractions (Fig. 4); dislocation lengths (Fig. S1); histograms
  (Fig. S2). Four regimes: I near threshold (under one defect on average), II sublinear following
  arc-dpa, III superlinear from about 20-30 keV, IV linear from about 300 keV. New model (Eqs 1-2) with
  E_III = 140 keV and alpha = beta = 2 for W (text). TDE: minimum 42 eV, average 95 eV (text).
  Regime II agrees with arc-dpa only after raising the average TDE to 95 eV.
- Limitations as relayed: model parameters fitted to W; artificial heat-spike results are an upper
  limit; few runs at 1-2 MeV (20); 50 ps only.
- Note: this is the widest-energy W data set I found and the only one with 100-1000 runs per
  low energy. It uses a different potential family from the EAM+ZBL studies, so it is not a like-for-
  like cross-check of them.

### 1.8 Fikar and Schäublin 2007

- Citation: J. Fikar, R. Schaeublin, "Molecular dynamics simulation of radiation damage in bcc
  tungsten", Nucl. Instrum. Methods B 255(1), 27-31 (2007), DOI 10.1016/j.nimb.2006.11.007.
- Tag: [ABSTRACT/METADATA] (EPFL Infoscience record). The abstract says two universal short-range
  potentials were each joined smoothly to two EAM W potentials with the electron density truncated
  at low distances; Frenkel pairs, dumbbell orientations and cluster counts are given; a standard
  deviation ellipsoid estimates the affected volume; and a critical review of earlier MD results
  separates potential and temperature effects. No numbers seen. Possibly useful as a cross-reference
  for the effect of the ZBL join; full text not read.

---

## 2. Threshold energies, BCA comparison and efficiency functions

### 2.1 Nordlund et al. 2018 (arc-dpa and rpa)

- Citation: K. Nordlund, S. J. Zinkle, A. E. Sand, F. Granberg, R. S. Averback, R. Stoller,
  T. Suzudo, L. Malerba, F. Banhart, W. J. Weber, F. Willaime, S. L. Dudarev, D. Simeone,
  "Improving atomic displacement and replacement calculations with physically realistic damage
  models", Nature Communications 9, 1084 (2018), DOI 10.1038/s41467-018-03415-5. Open access:
  https://pmc.ncbi.nlm.nih.gov/articles/PMC5852139/ . (Author list is from my recollection of the
  search-result listing, which gave thirteen authors; check against the paper.)
- Tag: [FULL-HTML] (PMC). The fetch said the exponents in the NRT equation were garbled in the
  source rendering and gave a reconstruction; I repeat it only as a reconstruction. Check eqs 1, 6, 7
  in the paper.
- NRT-dpa: N = 0 for T_d below E_d; N = 1 up to 2E_d/0.8; N = 0.8 T_d / (2 E_d) above (reconstructed).
  arc-dpa: same, with the last branch multiplied by xi(T_d) = (1 - c) (T_d / (2E_d/0.8))^b + c
  (reconstructed from the text's statement that xi is continuous and equals 1 at the 2E_d/0.8
  boundary).
- Tungsten parameters (Table 1, as relayed): E_d = 70 eV, b_arc-dpa = -0.56 ± 0.02, c_arc-dpa =
  0.12 ± 0.01.
- Simulation basis for W: potentials listed as DD (Derlet-type), JW (Juslin-Wirth), AT
  (Ackland-Thetford), AH (Ahlgren), all joined to ZBL. Number of runs and PKA energies for W are
  not stated in the text I opened (W data are in Fig. 3b); the fit range is up to about 10 keV.
  Temperature: cells equilibrated at room temperature; the text says 0 K and 300 K results agree
  within statistics, and two W points at 800 K with DD also agree.
- Note the E_d value of 70 eV here versus the values other papers use for their own fits (below).
- The original NRT reference is Norgett, Robinson, Torrens, Nucl. Eng. Des. 33, 50 (1975). That is
  from my memory, not from a source I opened; verify. Byggmästar 2025 mentions a "Yang and Olsson"
  low-energy correction applied to NRT and arc-dpa; I did not open that reference.

### 2.2 De Backer et al. 2016 (TDE, BCA vs MD)

- Citation: see the potentials file (item A7). Tag: [PDF-READ] pages 1-3.
- Abstract-level findings I read directly: TDE by DFT-MD and classical MD; cascades up to 100 keV
  with a model that accounts for electronic losses (Sand et al. 2013 cited); two BCA codes (SDTrimSP
  and MARLOWE); the comparison gave a recombination distance of 12 Å, larger than the value in an
  earlier paper (Hou et al. 2010), because bulk cascades produce more defects than surface cascades;
  the BCA vs MD difference in defect clustering was much reduced after OKMC annealing at 473 K.
- TDE table: see the potentials file (A7). Useful as a short-range sensitivity check, not as a
  cascade benchmark.

### 2.3 Threshold displacement energies as reported across the sources opened

| Source | Method / potential | Directional minima or averages (eV) | Where |
|---|---|---|---|
| Byggmästar 2019 | GAP, 4,368-atom box, 0 K | <100> 45.5; <111> 51.5; <110> 78; average 93.6 ± 5.5; experiment 42 ± 1 (<100>), 44 ± 1 (<111>) | section V.3, Fig. 10 |
| Liu 2023 | NEP-ZBL, 30 K | <100> 49; "average" 117 (other directions) | text only |
| De Backer 2016 | DFT-MD vs Marinica+ZBL MD | See Table 1 in the potentials file | Table 1 (read directly) |
| Byggmästar 2025 | tabGAP | minimum 42; average 95 | text |
| Setyawan 2015 | Juslin-Wirth, 10 K | E_d = 128 (used for scaling) | text |
| Nordlund 2018 | arc-dpa fit | E_d = 70 | Table 1 |

---

## 3. Benchmark candidates by theme (for the human to choose from)

None of these is a recommendation. The point is where numbers actually exist.

- Surviving Frenkel pairs vs PKA energy, EAM+ZBL, 300 K: Setyawan 2015 (Fig. 1a, power laws in text;
  figure-only otherwise). Liu 2023 (fit coefficients in text; Fig. 8). Nordlund 2018 (Fig. 3b; fit
  parameters in Table 1).
- Surviving Frenkel pairs, ML potentials: Liu 2023 (Fig. 8; Table 5 for 100 and 200 keV bulk);
  Byggmästar 2025 (Fig. 2); Warrier and Bhardwaj (Fig. 2, no explicit counts).
- Cluster size distributions: Sand 2013 (power-law fit parameters in text; Fig. 2); Setyawan 2015
  (Fig. 3, Table 2); Warrier and Bhardwaj (Figs 4-8); Liu 2023 (Table 5 largest clusters).
- In-cascade clustering fraction: Setyawan 2015 SIA fraction (Fig. 3a); Liu 2023 (Table 5);
  Warrier and Bhardwaj (about 0.45-0.8 depending on energy and potential, text); Zarkadoula 2015
  (Table 1, vacancy fraction in clusters larger than 3 only).
- Temperature dependence: Setyawan 2015 (300, 1025, 2050 K, 0.1-100 keV); Zarkadoula 2015 (300 and
  800 K at 300 keV, with and without 2T); Sheng 2025 (300-1500 K at 150 keV, figures only); Nordlund
  2018 (0 K, 300 K and a couple of 800 K points).
- Electronic stopping and 2T-MD: Sand 2013 (cutoff Tc scan, Table 1), Zarkadoula 2015 (Table 1),
  Sheng 2025 (figures), Byggmästar 2025 (friction above 10 eV).

## 4. Disagreements between sources

1. Surviving-defect scaling above the transition: exponent 1.30 at 300 K (Setyawan) vs a fit with
   exponent 1.25 and prefactor 0.03 (Liu, with E_d = 90 eV for the NEP-ZBL potential) vs the
   Setyawan values as quoted by Liu (a = 0.02, b = 1.30). Different E_d and different potentials, so
   the prefactors are not directly comparable. Byggmästar 2025 reports a superlinear regime starting
   at about 20-30 keV and a linear regime from about 300 keV, which is a different functional picture
   from a single power law.
2. Effective E_d: 70 eV (arc-dpa fit), 90 (Liu NRT comparison), 95 (Byggmästar 2025 average TDE),
   117 (Liu average), 128 (Setyawan). The choice of E_d changes the NRT line and the
   "efficiency" read from every plot.
3. Subcascade splitting: Sand 2013 sees none at 150 keV (EAM with ZBL, 0 K); Liu sees 20% at 100 keV
   and 70% at 200 keV; Warrier and Bhardwaj report more subcascades below 50 keV for tabGAP and
   DND-BN. Potential and start temperature differ.
4. Electronic effects on surviving defects: Zarkadoula finds 2T-MD leaves fewer survivors than
   friction at 300 keV (1900 vs 5500 at 300 K, Table 1); Sheng finds 2T-MD reduces peak defects
   strongly while surviving defects diverge from classical MD only at high energy. Their g_p
   (7e17 vs 5e17) and potentials differ.
5. Temperature trend of survivors: Zarkadoula (Table 1) has friction-only survivors equal at 300 and 800 K
   (5500 each) but 2T-MD survivors rising from 1900 to 2700; Sheng (figures only) has classical-MD
   survivors falling with temperature and 2T-MD roughly flat; Setyawan (Fig. 1a; no electronic stopping
   stated) has N_F at E* = 1 of about 0.5, 0.3, 0.5 at 300, 1025, 2050 K and a slightly steeper
   high-energy exponent at the two higher temperatures (1.36 vs 1.30). No consistent trend across
   sources, and potentials, energies and electronic treatment all differ.
6. Clustered SIA fraction: Setyawan 0.5-0.7 above the transition at 300 K (Fig. 3a); Liu 86% at 100 keV
   bulk (Table 5); Warrier and Bhardwaj 0.65-0.8 at 150 keV depending on potential; definitions of
   clusters differ (Setyawan NN3 for SIA and NN4 for vacancy, other papers differ or do not say).
7. Defect-identification criteria differ (Zarkadoula uses a 0.75 Å sphere criterion; Setyawan uses
   0.3 a0; Liu and others use Wigner-Seitz). Frenkel-pair counts are therefore not directly
   comparable without re-analysis.

## 5. Gaps and cautions

- No source gave a table of surviving Frenkel pairs per energy and temperature that I could open.
  Most data are in plots (Setyawan Fig. 1a, Liu Fig. 8, Byggmästar 2025 Fig. 2, Sheng Figs 1-3). A
  digitisation or contact with authors may be needed. I did not find or open any data repository in
  these searches.
- The IAEA cascades database (cascadesdb.iaea.org) appeared in search results but returned HTTP 402 and
  could not be opened. It may hold W data; unverified.
- No opened source reports a table of 1-10 keV EAM+ZBL cascade results at the box sizes and run counts
  relevant to this project; Setyawan Table 1 gives the setup only.
- Box-size convergence tests were not described in any source I opened; only box-size choices appear
  (Liu Table 1, Warrier Table 1, Byggmästar Table 1).
- Electronic stopping cutoff and e-ph coupling are unresolved (see the potentials file, Part E).

## 6. Not opened (leads only)

- Sand, Aliaga, Caturla, Nordlund, "Surface effects and statistical laws of defects in primary
  radiation damage: Tungsten vs. iron", EPL 115, 36001 (2016), DOI 10.1209/0295-5075/115/36001.
  A record page was opened; the abstract was not displayed.
- Sand, Byggmästar, Zitting, Nordlund, "Defect structures and statistics in overlapping cascade
  damage in fusion-relevant bcc metals" (title and authors from a search result; venue not
  confirmed). A related cascade-overlap paper in J. Phys.: Condens. Matter (2019) was named in the
  same result.
- De Backer et al., cascades morphological analysis, J. Phys.: Condens. Matter 30, 405701 (2018)
  (from a repository filename in search results).
- Nordlund et al., "Primary radiation damage: a review of current understanding and models",
  J. Nucl. Mater. 512, 450-479 (2018) (record seen in search results).
- Hou et al. 2010, J. Nucl. Mater. 403, 89 (cited by De Backer 2016; not opened).
- Setyawan et al. Part II (annealing).
- A 2022 Aalto master's thesis applying 2T-MD to ion-beam mixing in W (search result only).

## 7. Counts

11 sources opened for this file: Setyawan, Sand 2013, Zarkadoula, Sheng, Liu, Warrier and Bhardwaj,
Byggmästar 2025, Nordlund 2018 (8 at full-text level via HTML), De Backer 2016 (3 PDF pages read),
and Fikar and Schäublin and the Sand 2016 record (abstract or record level only). Byggmästar 2019 is
used in the TDE table and is counted in the potentials file.
