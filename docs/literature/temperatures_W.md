# Temperatures for W cascade simulations: literature leads

Status: UNVERIFIED

Compiled 2026-11-02 by lit-researcher. "Opened" = page or PDF text actually read. Items from search snippets only are listed under "Leads not opened" and must not be used until checked. Anything unconfirmed is TODO-LIT.

## 1. Operating temperatures of W plasma-facing components

### Opened

**ITER divertor, inner vertical target (W monoblocks)**
- Source: ITER Organization newsline article, https://www.iter.org/newsline/-/3027 (no authors, no date read; web page).
- Reports: peak W surface temperature about 1,000 C in normal operation and about 2,000 C in off-normal conditions; heat flux 10-20 MW/m2; W melting point given as 3,400 C; monoblocks actively cooled by pressurized water (no coolant temperature on that page).
- Limits: popular-level page, not a design document; only the inner vertical target; first wall not covered. Bulk and coolant-side temperatures: not on this page.

**EU-DEMO divertor, W monoblock on CuCrZr tube**
- Greuner, Boeswirth, Barrett, Crescenzi, Gallay, Hunger, Richou, Visca, Mueller, You, "Progress in high heat flux testing of European DEMO divertor mock-ups", EUROfusion preprint WPDIV-CPR(18) 20060 (SOFT 2018 proceedings), 2018. https://scipub.euro-fusion.org/wp-content/uploads/eurofusion/WPDIVCPR18_20060_submitted-4.pdf (opened pp. 1-3 only; the final journal citation/DOI is TODO-LIT).
- Reports: hot-water-cooled targets, reliable operation for 2 h pulses at nominal 10 MW/m2 and up to 20 MW/m2 in slow transients (<10 s); DEMO coolant temperature 150 C (versus ITER, higher than ITER); design neutron dose 4 dpa in the W armour (13 dpa in the Cu-alloy tubes) over two full-power years.
- Limits: coolant temperature, not W surface temperature; I did not read the pages with the HHF test temperatures.

**EU DEMO substructure window (baseline water-cooled divertor)**
- D. Stork et al., "Developing Structural, High-heat flux and Plasma Facing Materials for a near-term DEMO Fusion Power Plant: the EU Assessment", arXiv:1408.3546 (published in J. Nucl. Mater., 2014; journal citation and DOI TODO-LIT). Opened abstract and sections 1-2 only.
- Reports: a water-cooled divertor target suggests a substructure operating window of about 200-350 C for W on a Cu-alloy substructure (abstract). Same abstract: water-cooled blankets about 290-320 C steel temperatures; He-cooled blankets above 650 C.
- Limits: 2012 roadmap-era concept, not the current EU-DEMO design. Concerns the substructure, not the W surface. Different from the 150 C coolant in Greuner (see Disagreements).

### Leads not opened (snippet-level only, do NOT use as numbers)
- ITER W divertor operating range, APS DPP 2018 abstract: https://archive.aps.org/dpp/2018/gm9/1 (search snippet: stationary range limited by recrystallization).
- ITER inlet/outlet coolant 70/120 C at 4 MPa: seen in snippets from an IAEA poster (El-Morshedy) and F4E procurement doc https://fusionforenergy.europa.eu/downloads/procurements/itercalls/372.pdf; not opened.
- Magnum-PSI monoblock test, surface up to 1580 C, recrystallization to 2.2 mm depth: https://www.differ.nl/sites/default/files/attachments/biblio/2020_1676.pdf; not opened.
- Marzullo et al., Fusion Eng. Des. 2024, DEMO divertor coolant minimum temperature (180 C mentioned in a snippet); not opened.
- EU assessment snippet: recrystallization above about 1200 C, bulk below about 650 C for swelling, ductile above about 600 C; this was a search summary of arXiv:1408.3546 and I did not read the relevant pages.

### Gaps for item 1 (TODO-LIT)
- ITER first-wall temperatures (Be armour, W-clad blankets): nothing found.
- EU-DEMO W first-wall armour surface and bulk temperatures: nothing found.
- ITER W monoblock bulk/coolant-side temperatures from a design document: only unopened snippets.
- EU-DEMO divertor W surface temperature in normal operation: TODO-LIT.

## 2. MD of temperature dependence of W primary damage

### Opened

**Setyawan et al. 2015 (the benchmark's source, a JW-type potential at three temperatures)**
- W. Setyawan, G. Nandipati, K.J. Roche, H.L. Heinisch, B.D. Wirth, R.J. Kurtz, "Displacement cascades and defects annealing in tungsten, Part I: defect database from molecular dynamics simulations", J. Nucl. Mater. 462, 329 (2015). arXiv:1404.6490, https://arxiv.org/abs/1404.6490 (opened full PDF, pp. 1-9). Journal DOI TODO-LIT.
- Method: LAMMPS; W potential "derived from Ackland-Thetford with hardened short range" (their ref [2]; the paper text does not name Juslin-Wirth on the pages I read, so equating it to JW is TODO-LIT; the repo already treats it as JW). 30 ps NPT-like thermalization (Nose-Hoover, zero pressure), NVE for ~10 ps then thermostat, adaptive step max 0.005 A. Lattice constants used: 3.167, 3.184, 3.216 A at 300, 1025, 2050 K (Table 1). PKA 0.1 to 100 keV; runs per point in Table 1 (20 runs for 5 keV at each T; 20/20/15 for 10 keV at 300/1025/2050 K). Cell 40 a0 at 5 keV, 50 a0 at 10 keV.
- Results: surviving Frenkel pairs follow N_F = a(E/E_d)^b above E* = 4, with E_d = 128 eV (their average). Table in Fig. 1a: Region 1 (a1, b1): 0.49, 0.74 at 300 K; 0.39, 0.74 at 1025 K; 0.38, 0.73 at 2050 K. Text: fit lines imply defects fall about 20% from 300 to 1025 K and about 5% from 1025 to 2050 K in Region 1. At E* = 1, N_F ~0.5 (300 K), 0.3 (1025 K), back to 0.5 (2050 K). Clustering: SIA clustering rises with T, vacancy clustering falls; at 2050 K practically no large vacancy clusters. Fig. 3 gives fractions only as curves (digitize). At 10 keV (E/E_d = 78) absolute N_F values are figure-only: TODO-DIGITIZE.
- Limits: N_F at each energy is graphical; only three temperatures; 2050 K is about 0.5 Tm (they state this for the potential), beyond expected normal-operation temperatures.

**Wang, Zhou, Li, Hou (potential paper, thermal expansion only; see sec. 3).** Not a cascade study.

**Sheng et al. 2025 (different potential)**
- S. Sheng, S. Wei, C. Zhang, C. Zhang, G. Pu, B.-S. Li, "Effects of electronic excitation on cascade dynamics in tungsten", Front. Phys. 13, 1592186 (2025), doi:10.3389/fphy.2025.1592186, https://www.frontiersin.org/articles/10.3389/fphy.2025.1592186/full (opened).
- Method: LAMMPS, Deng et al. FS-type W potential joined to ZBL, 2T-MD; 300-1500 K; PKA 10-150 keV; equilibrated at 300 K before irradiation.
- Reports (text only, counts in Fig. 3 only): peak defects increase with temperature; surviving defects in classical MD decrease with temperature; in 2T-MD surviving defects are similar for 300-1500 K.
- Limits: not JW/AT; no numbers in text.

### Leads not opened (abstract/snippet only)
- Liu et al., "Displacement cascades database from molecular dynamics simulations in tungsten", J. Nucl. Mater. 580, 154415 (2023), doi:10.1016/j.jnucmat.2023.154415 (publisher page redirected; I could not open the abstract). Per a search summary only: PKA 1-300 keV at 363 K, and 10/50/100/200 keV at 600 K; going 363 K to 600 K lowers Frenkel pairs by about 10% and promotes SIA clustering. Potential: TODO-LIT. Highly relevant as a 600 K benchmark if confirmed.
- Efficient atomistic simulations of radiation damage in W and W-Mo using ML potentials, arXiv:2208.00804 (10 keV cascades; temperature dependence unverified).
- A 1-25 keV, 100-900 K study (chinaxiv abstract 202303.00613): reported to find N_F declining with T; not opened, potential unknown.

### Gaps for item 2
- No study found that uses the exact Juslin-Wirth potential at 5-10 keV at several temperatures other than Setyawan (and Warrier & Bhardwaj at 300 K, already in repo).
- Numerical 10 keV N_F at 1025 K and 2050 K requires digitizing Setyawan Fig. 1a (TODO-DIGITIZE).

## 3. Lattice constant / thermal expansion of W

### Opened
- Setyawan et al. (above), Table 1: a0 = 3.167 A (300 K), 3.184 A (1025 K), 3.216 A (2050 K) for the W potential they used (AT-derived, JW-type). Compare directly with this project's NPT values: 3.1674 A at 300 K (physics_settings.md) agrees. Ratios: 3.184/3.167 = 1.54% larger at 1025 K; 3.216/3.167 = 1.55% larger at 2050 K -> note 3.216/3.184 gives 1.0% per 1025 K; (these are my arithmetic from the table; the values are given to 3-4 digits only).
- Wang, Zhou, Li, Hou, "A modified W-W interatomic potential based on ab initio calculations", arXiv:1306.4738, https://arxiv.org/abs/1306.4738 (opened full PDF pp. 1-8; journal citation TODO-LIT). Reports MD thermal expansion (2000 atoms, zero pressure, 0 to 3500 K, reference 293.15 K), comparing AT, DND and their potential with experiment (their refs [20,21]) only in Fig. 2 (not quantitative in text). Text: AT thermal expansion is significantly higher than experiment; DND shows negative expansion above about 300 K; their potential agrees reasonably. Also AT melting point about 5200 K (via Fikar et al.).
- Limits: AT, not JW, and the AT statement is qualitative. The experimental dataset they used (ref [20], 293.15 K reference) is not identified in what I read.

### Leads not opened
- P. Tolias, "Analytical expressions for thermophysical properties of solid and liquid tungsten relevant for fusion applications", Nucl. Mater. Energy 13, 42 (2017), doi:10.1016/j.nme.2017.08.002, arXiv:1703.06302. Abstract read only; says it covers mass density from room temperature to boiling; the PDF text was not readable by my tools, so I could not extract an expansion formula. Likely the best compiled source for experimental density/expansion: TODO-LIT.
- Secondary table (KnowledgeDoor) linear expansion coefficient about 4.49e-6 /K at 300 K and 9.05e-6 /K at 3000 K, from a snippet and not traceable to a primary source: do not use.
- Experimental references for lattice parameter: Shah & Straumanis (J. Appl. Phys. 1971) and Hidnert & Sweeney (NBS Sci. Paper 515) appeared in searches; not opened. Experimental a0(T) at 1000 K and 2000 K: TODO-LIT.

## Disagreements and cautions
- DEMO coolant temperature: Greuner (opened) says 150 C; the divertor water temperature from an unopened snippet range 130-200 C; Marzullo 2024 mentions 180 C minimum (unopened); Stork substructure window 200-350 C (opened, older concept). These are different quantities and design iterations; do not merge.
- Temperature effect on N_F: Setyawan finds about 20% fewer pairs from 300 to 1025 K but only about 5% more reduction to 2050 K (non-monotone at E* = 1); Sheng 2025 finds classical MD declining but 2T-MD flat. Liu 2023 (unopened) about 10% from 363 to 600 K. The magnitudes differ and depend on potential and energy.
- Setyawan equilibrates with NPT to the temperature-specific a0, but the repo currently uses a 300 K a0 with Langevin equilibration (physics_settings.md Sec. 3): a new temperature needs its own measured a0, with 3.184 A (1025 K) and 3.216 A (2050 K) as sanity checks.

## Suggested temperatures (for the main agent and human to decide)
1. 300 K: existing baseline (Warrier & Bhardwaj; Setyawan; Liu 2023 has 300 K at 10 and 50 keV per an unopened summary).
2. 600 K: about 327 C, sits in the DEMO W-on-Cu substructure window 200-350 C (Stork, opened; upper end 623 K) and matches Liu 2023's 600 K (unopened, verify). Warrier benchmark does not cover it, so Liu is the only candidate benchmark.
3. 1025 K (about 752 C): direct Setyawan benchmark (a0 3.184 A, N_F fit given); below the ITER normal-operation peak W surface of about 1000 C (1273 K) but the nearest benchmarked value; relevant to hot W surface regions.
4. Optional 2050 K (about 1777 C): Setyawan benchmark (a0 3.216 A); relevant only to off-normal conditions (ITER about 2000 C, iter.org); lower priority, clearly flagged as off-normal. A 1273 K point matching ITER normal operation has no published benchmark found: TODO-LIT.

## Next searches
- Liu 2023 full text (potential, N_F at 10 keV for 300 and 600 K).
- Digitize Setyawan Fig. 1a at E/E_d = 39 and 78.
- Tolias 2017 full text for W density/expansion; Touloukian TPRC vol. 12; Dubrovinsky/Hidnert lattice parameter data.
- ITER Physics Basis / divertor design papers (Pitts et al., Hirai et al.) for W monoblock surface/bulk temperatures; ITER first wall (Raffray, Merola) for Be/W FW temperatures.
- EU-DEMO first wall W armour temperatures (You et al., Nucl. Fusion / Fusion Eng. Des. 2022 DEMO divertor design).
