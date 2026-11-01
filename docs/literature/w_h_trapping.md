Status: UNVERIFIED

# Hydrogen / deuterium / tritium trapping in tungsten (DFT and experiment)

Prepared 2026-11-01 for section 1 (W-H potential validation: H solution and vacancy-H binding
energies) and section 4 (trapping stage) of `docs/interfaces/physics_settings.md`, and for later
retention validation. Nothing here is approved.

## How to read the provenance tags

- [PDF-READ] I looked at page images of the PDF myself ("read directly").
- [FULL-HTML] I opened an HTML rendering of the full text through a summarising fetch tool. Numbers
  are relayed, not read by me from raw text. Re-check before use.
- [ABSTRACT/METADATA] Only an abstract or record page was opened.
- [SEARCH-ONLY] Seen only in web-search result summaries. NOT opened. Leads only; do not cite.

Important limit: I could not open any primary experimental paper at full-text level. Several
publisher, HAL, IAEA and EUROfusion pages blocked automated access (HTTP 402/403 or bot-protection
pages), and some EUROfusion "preprint" PDFs were cover pages only. The experimental section is
therefore thin; see the leads list for what to fetch by hand.

---

## 1. DFT sources opened

### 1.1 Ohsawa et al. 2010 (multiple H in a W monovacancy)

- Citation: K. Ohsawa, J. Goto, M. Yamakami, M. Yamaguchi, M. Yagi, "Trapping of multiple hydrogen
  atoms in a tungsten monovacancy from first principles", Phys. Rev. B 82, 184117 (2010).
  DOI 10.1103/PhysRevB.82.184117. Open copy: Kyushu University repository,
  https://hdl.handle.net/2324/26364
- Tag: [PDF-READ] pages 1-5 (abstract through Table I).
- Method: VASP, PAW, GGA (PBE); mostly a 54-site bcc supercell (3x3x3x2) with 5x5x5 k-points and a
  350 eV cutoff; some cases checked in a 128-site cell with 3x3x3 k-points and a 300 eV cutoff.
  Forces below 2e-3 eV/Å. Random initial H positions inside the vacancy, ground state chosen from
  several relaxations. ZPE from the harmonic approximation.
- Binding energy definition (Eq. 1): energy gained when m H atoms move from distant T-sites into
  the vacancy, so values are relative to H at a bulk T-site. E_zc (Eq. 3) adds the ZPE correction.
- Bulk H (section III.A, read directly): the T-site is favoured over the O-site by 0.380 eV; ZPE of H
  is 0.264 eV (T-site) and 0.253 eV (O-site) (Table I footer).
- Key result: with increasing H number the stable H sites move from near the octahedral site toward
  tetrahedral-like sites, and a maximum of 12 H can be trapped in a monovacancy (abstract and
  Fig. 10).
- Table I (read directly). m = number of H; E_tot = total binding (eV); E_avr = average per H (eV);
  E_zc = binding with ZPE correction (eV).
  - m = 1: E_tot 1.182, E_avr 1.182, E_zc 1.318
  - m = 2: 2.353, 1.176, 2.626
  - m = 3: 3.423, 1.141, 3.708
  - m = 4: 4.368, 1.092, 4.723
  - m = 5: 5.256, 1.051, 5.652
  - m = 6: 5.888, 0.981, 6.329
  - m = 7: 6.173, 0.881, 6.597
  - m = 8: 6.514-6.532, about 0.815, about 6.94 (two near-degenerate states)
  - m = 9: 6.638, 0.737, 7.041
  - m = 10: 6.979, 0.697, 7.407
  - m = 11: 7.101, 0.645, 7.550
  - m = 12: 7.391, 0.615, 7.863
  - m = 13: 6.541, 0.503, 7.082
  - m = 14: 7.365, 0.526, 7.819
- Incremental (n-th H) binding from the E_tot column, computed by me by subtraction and not stated in
  the paper: n = 1: 1.182; 2: 1.171; 3: 1.070; 4: 0.945; 5: 0.888; 6: 0.632; 7: 0.285; 8: about 0.34
  (m = 8 state mix-up possible; check Table I); 9: about 0.12. The drop after about the sixth H is
  visible in the totals.
- Limitations: zero temperature; no entropy (so the equilibrium number of H at a given temperature
  and pressure is not given by this paper); harmonic ZPE; GGA only; one monovacancy; supercell and
  cutoff checks only on some cases; neither D nor T was computed explicitly, though the text says ZPEs
  for D and T are smaller than for H (introduction).

### 1.2 Jin et al. 2023 (lattice location of D in W; DFT plus NRA/C simulation)

- Citation: X. Jin, F. Djurabekova, E. A. Hodille, S. Markelj, K. Nordlund, "Analysis of lattice
  locations of deuterium in tungsten and its application for predicting deuterium trapping
  conditions", arXiv:2312.09112 (late 2023; no journal reference on the page).
- Tag: [FULL-HTML] (ar5iv; about 100,000 of 102,914 characters read).
- Method: VASP, PAW, PBE, 54-atom (3x3x3) cell, ZPE for H and He; NRA/C simulation tool built on
  RBSADEC; rate-equation (macroscopic) modelling for vacancy filling.
- Perfect W (Table I, section 3.1): H prefers the tetrahedral site with formation energy 0.96 eV
  (1.07 eV with ZPE); the octahedral site is a second-order saddle at 1.35 eV.
- Interstitial-type traps (section 3.2): binding about 0.23 eV for the <11x> self-interstitial, 0.05 eV
  for interstitial C and 0.24 eV for interstitial O. Weak compared with vacancy traps.
- Vacancy (section 3.3): vacancy formation energy 3.38 eV. H moves from near-octahedral (1 H) toward
  tetrahedral sites as filling rises, with 12 H the maximum. Binding falls with filling; using a
  0.69 eV threshold for V1H6 taken from Fernandez et al., the authors limit plausible filling to 6 H.
  C and O bind to a vacancy with 2.16 and 3.26 eV; He prefers the vacancy centre.
- Rate-equation result (section 4): V1H5 favoured without helium; V1He1H5 dominant once He is included.
  Ab initio MD at 300 K showed some H leaving the vacancy so room-temperature filling is below 12.
- Experiment used: NRA angular scans of 30 keV D implanted in W (Picraux and Vook, cited, not opened).
  The authors find agreement only if He from the 3He probe beam is included; D positions shifted after
  further He irradiation. No TDS data presented.
- Limitations: 54-atom cell; PBE; the paper treats H lattice locations, not detrapping energies;
  experiment comparison is angular-scan shape, not retention.

### 1.3 Kaur et al. 2025 (multi-occupancy trap model; uses DFT binding energies for W)

- Citation: S. Kaur, D. R. Mason, P. Srinivasan, S. Dixon, S. Mungale, T. Orr, M. Yu. Lavrentiev,
  D. Nguyen-Manh, "The effect of multi-occupancy traps on the diffusion and retention of multiple
  hydrogen isotopes in irradiated tungsten and vanadium", arXiv:2508.15341 (v3, Nov 2025; no journal
  reference seen).
- Tag: [FULL-HTML] (first 100,000 of about 114,000 characters read).
- W trap and migration energies in Table 1 (W column), which the paper attributes to Heinola's DFT work
  (its refs 16 and 33), in eV, with the ZPE correction beside each:
  E1b 1.28 (0.15); E2b 1.25 (0.16); E3b 1.11 (0.11); E4b 1.00 (0.11); E5b 0.91 (0.09);
  E6b 0.32 (0.15); Ef(H_int) 0.69 (0.27); Em (migration) 0.21 (-0.04). The paper states the
  ZPE-corrected migration barrier as 0.17 eV. I take "Ef(H_int)" to be the H interstitial formation
  or solution energy, but 0.69 eV does not match other sources (0.93-0.96 eV below) and may be a
  differently defined quantity; verify in the paper. These are secondary values; the Heinola paper
  itself was not opened.
- Isotopes: H, D and T share one framework; occupancy states are labelled by counts of each isotope;
  ZPE corrections are scaled by 1/sqrt(2) for D and 1/sqrt(3) for T. For vanadium at 300 K the
  model gives asymmetric exchange, with H flushing T more strongly than the reverse when ZPE is
  included; without ZPE the two mirror each other. W-specific isotope exchange results are not in the
  part I read.
- Experimental comparison: Markelj et al. NRA depth profiles in 20 MeV W6+ irradiated polycrystalline W
  exposed sequentially to atomic H and D at 600 K (fluxes 6.9e18 and 5.8e18 m^-2 s^-1). The model
  used no fitting parameters. Vacancy density came from SRIM dpa converted to monovacancies using MD
  cascades at 300 K. Result: reasonable bulk depth-profile shape, retention overestimated (attributed
  to the MD vacancy density being too high for a 600 K experiment), narrow surface peak not reproduced;
  D beyond about 2.5 um attributed to unmodelled traps (possibly helium from the NRA probe).
- Limitations stated: no tunnelling or other quantum effects; monovacancies only (no clusters, voids,
  loops, impurities); steady-state trap assumption valid in W above about 500 K; source and
  implantation parameters are order-of-magnitude estimates; comparison with experiment is only
  qualitative for release.

### 1.4 Mason et al. 2023 (potential paper, quoted DFT reference values)

- Citation and tag: see the potentials file, item D1 ([FULL-HTML]). This is an empirical-potential paper,
  but it lists DFT reference values from other work.
- DFT reference values as quoted (Table 4, relayed): T-site H solution energy 0.93 eV; O-T gap
  0.44 eV; tet-tet migration barrier 0.21 eV; H crowdion relaxation volume 1.719 Omega_0; (110) surface H
  binding 0.75 eV (Table 5); trivacancy migration 1.146 eV. The paper's own DFT source for each number
  was not visible in what I retrieved.
- The potential's value for binding per H at a vacancy rises from about 1.23 eV (monovacancy) to about
  1.7 eV for large vacancy clusters (Figs 9b, 10b). The paper says the earlier Wang potential lacks this
  rise, and that the energy ordering of defects changes with the H-to-defect ratio (abstract).
  Zero-point energy is excluded from their fit and added separately.

### 1.5 Johnson and Carter 2010

- Citation: D. F. Johnson, E. A. Carter, "Hydrogen in tungsten: absorption, diffusion, vacancy
  trapping, and decohesion", J. Mater. Res. 25(2), 315-327 (2010), DOI 10.1557/jmr.2010.0036.
- Tag: [ABSTRACT/METADATA] (Princeton research record).
- Periodic DFT. Inward H uptake barriers through the surface of at least 2.08 eV (W(001)) and
  1.77 eV (W(110)); outward barriers very small; bulk dissolution endothermic; vacancies trap multiple
  H exothermically; adsorbed H stabilises surfaces. The page gives no solution energy or vacancy
  binding values. Full text not read.

### 1.6 Opened, not useful for numbers

- Tirumala et al. 2025 (W-H-He potential): H binding to He-filled voids, Tables 4-5 (see potentials file D2).
  Not a trapping benchmark for pure H.
- Li et al. 2022, Frontiers in Materials 9, 935129 (effective H diffusion coefficient from phase-field
  simulations): no DFT or trapping energies. Opened, not relevant.
- Hou et al. 2019, arXiv:1912.05750 (MD study of H and He diffusion as non-Markovian jumps): abstract
  only, no barrier values; not relevant to DFT trapping energies.
- Zhang et al. 2025, arXiv:2507.20121 (cluster dynamics of H saturation retention in W): abstract only.
  Reports unsaturated D retention governed by grain boundaries and ion-induced defects below a
  saturation fluence of about 1e23 m^-2; no detrapping energies given on the page.

---

## 2. Experimental sources opened (abstract level only)

### 2.1 Shimada et al. 2011

- Citation: M. Shimada, Y. Hatano, P. Calderoni, T. Oda, Y. Oya, M. Sokolov, K. Zhang, G. Cao,
  R. Kolasinski, J. P. Sharpe, "First result of deuterium retention in neutron-irradiated tungsten
  exposed to high flux plasma in TPE", J. Nucl. Mater. 415(1) Suppl., S667-S671 (2011),
  DOI 10.1016/j.jnucmat.2010.11.050.
- Tag: [ABSTRACT/METADATA] (ORNL record).
- Pure W (99.99%) irradiated in HFIR at 323 K to 0.025 dpa; one sample exposed to D plasma in the Tritium
  Plasma Experiment (ion flux 5e21 m^-2 s^-1, fluence 4e25 m^-2). D retention was 40% higher than in
  unirradiated W. The broad desorption spectrum and TMAP modelling suggest more than three trap energies.
- Limits: a single sample; abstract only; no trap energies on the page.

### 2.2 Hatano et al. 2013 (Materials Transactions)

- Citation: Y. Hatano, M. Shimada, Y. Oya, G. Cao, M. Kobayashi, M. Hara, B. J. Merrill, K. Okuno,
  M. A. Sokolov, Y. Katoh, "Retention of hydrogen isotopes in neutron irradiated tungsten", Mater. Trans.
  54(4), 437-441 (2013), DOI 10.2320/matertrans.MG201204.
- Tag: [ABSTRACT/METADATA] (ORNL record; the page notes typographical errors in the abstract text).
- Pure W irradiated in HFIR at about 50 C to 0.025 dpa, then exposed to high-flux D plasma at INL. After
  exposure at 200 C and 500 C, D concentrations in irradiated specimens ranged from 0.1 to 0.4 mol%,
  significantly above unirradiated specimens. At 500 C D penetrated to roughly 50-100 um (garbled in
  source). D release in TDS continued up to 900 C. Compares with ion-irradiated W.
- Note: no tritium data in the abstract. This is not the "Hatano et al., Nucl. Fusion 53 (2013)" paper
  listed under leads.

### 2.3 Experimental numbers used by Kaur 2025 and Jin 2023 (secondary)

- Kaur 2025 compares to Markelj's NRA data (see 1.3). Jin 2023 compares to Picraux-Vook angular scans
  (see 1.2). Neither is a retention-versus-dose table.

---

## 3. Isotope effect (H, D, T)

- What I found in opened sources: Ohsawa 2010 states that ZPEs for D and T are smaller than for H
  (introduction), and Kaur 2025 implements isotope dependence only through mass-scaled ZPE
  (1/sqrt(2), 1/sqrt(3)) in the trapping energies, with no tunnelling. Kaur 2025 reports an
  asymmetric flushing result for vanadium at 300 K but I did not see a W isotope-exchange result.
- Not found: any opened source that directly compares H, D and T retention, trapping or detrapping in
  displacement-damaged W, experimentally or by DFT. The tritium TDS and TMAP papers named below are
  leads only. The Hatano 2013 abstract has no tritium.
- Cautions: the isotope dependence in DFT is a ZPE and vibrational-entropy correction on a mass-independent
  0 K energy surface; classical MD with a W-H EAM has no ZPE at all and no tunnelling, so classical MD
  trapping for T will differ from a quantum-corrected value. That is my reading of the sources above,
  not a statement from a single paper. The Mason 2023 paper says ZPE is added outside the potential fit.

---

## 4. Disagreements and cautions

1. H solution energy at the tetrahedral site: DFT 0.93 eV (Mason 2023, Table 4, relayed), 0.96 eV
   (Jin 2023, Table I), and a value of 0.69 eV listed as Ef(H_int) in Kaur 2025 Table 1 attributed to
   Heinola (definition uncertain). ZPE addition: +0.11 eV (Jin, 0.96 to 1.07), +0.25 eV (Mason's potential,
   0.798 to 1.049), 0.27 eV (Kaur Table 1 ZPE column). Not necessarily the same quantity.
2. T-site vs O-site: 0.380 eV (Ohsawa), 0.39 eV (Jin, 1.35 minus 0.96), 0.44 eV (the Mason 2023 DFT
   reference). A spread of 0.06 eV across DFT setups.
3. First-H binding at a monovacancy (relative to bulk T-site H): 1.182 eV (Ohsawa, no ZPE; 1.318 with
   ZPE correction), 1.28 eV (Heinola values as listed by Kaur, with +0.15 ZPE correction), about 1.23 eV
   (Mason 2023 potential, an empirical fit, not DFT). The functional is PBE in the two DFT sources I could
   verify; the Heinola paper's settings were not opened.
4. Incremental binding versus H number: Ohsawa-derived increments (1.18, 1.17, 1.07, 0.95, 0.89, 0.63) and the
   Heinola values listed by Kaur (1.28, 1.25, 1.11, 1.00, 0.91, 0.32) agree within about 0.1 eV up to the
   fifth H but differ at the sixth (0.63 vs 0.32 eV). Could be different configurations, cell sizes, or a
   transcription issue in Kaur's table; needs the primary papers.
5. Maximum H per vacancy: 12 (Ohsawa, 0 K, Fig. 10); up to five at room temperature (Heinola abstract, via a
   search-result summary only); 6 from a binding threshold of 0.69 eV for V1H6 (Jin citing Fernandez);
   V1H5 favoured by rate equations (Jin); "about six at finite temperature" attributed to Ohsawa, Hatano and
   Yamaguchi in a search-result summary (not opened). The answer depends on temperature, H pressure and the
   criterion used, so any trapped-vs-free criterion in section 4 of `physics_settings.md` should state which.
6. DFT versus experiment on detrapping: DFT gives binding energies relative to bulk interstitial H. A measured
   detrapping (activation) energy in TDS/NRA fits would be larger by about the migration barrier. That
   relation is general physics and is my note, not a statement from a source opened here. Experimental fit
   values seen only in search-result summaries (not opened) are 0.85-0.87 and 1.00 eV intrinsic traps, 1.5 eV
   for an ion-induced trap, 1.65-2.06 eV for damage traps in a self-damaged W study, 1.83 eV used in a
   tritium TMAP4 analysis, and 2.1 eV with an unknown prefactor in a presentation. They use different models,
   prefactors, and materials, and several are lower than the DFT first-H binding plus migration (about 1.4-1.5
   eV), so a like-for-like comparison needs the primary papers.
7. D retention levels: the leads below give maximum D concentrations of about 1.4 at.% (0.23 dpa) in one
   summary and about 1.7 at.% (above about 0.1 dpa, 290 K) in another, with saturation quoted at 0.1, 0.25, and
   0.5-1 dpa in different presentations. They may reflect different damage energies, temperatures, or NRA
   definitions, so do not treat them as one number.

---

## 5. Gaps

- Primary experimental data: TDS and NRA retention versus dpa in self-ion-damaged W (Schwarz-Selinger,
  Markelj, Tyburska, Alimov, Ogorodnikova, Wampler and Doerner) not opened. Need full text or
  digitised figures.
- Primary DFT papers not opened: Heinola 2010 (H-point defects, with ZPE), Fernandez 2015 (DFT plus
  statistical models), Ohsawa 2015 (H-assisted vacancy formation), Liu et al. 2009 (vacancy trapping).
  Note a Kyushu repository copy of Heinola 2010 did not download (HTTP 404).
- Vacancy clusters (divacancy, voids) and dislocation or loop trapping DFT: only Mason's potential
  paper (empirical) was opened.
- Isotope-effect studies for tritium: none opened.
- Neutron-irradiated W and tritium: Shimada 2011 and Hatano 2013 abstracts only.
- Experimental H solution energy and diffusivity (Frauenfelder 1969): not opened; only mentioned in a
  search-result summary of Fernandez 2015.

## 6. Not opened (leads only; do not cite from these)

- K. Heinola, T. Ahlgren, K. Nordlund, J. Keinonen, "Hydrogen interaction with point defects in tungsten",
  Phys. Rev. B 82, 094102 (2010), DOI 10.1103/PhysRevB.82.094102. Search summary: DFT with ZPE; a monovacancy
  can hold up to five H at room temperature; substitutional Re and Os have little effect on trapping; a
  Helsinki-hosted PDF exists (link failed).
- N. Fernandez, Y. Ferro, D. Kato, "Hydrogen diffusion and vacancies formation in tungsten: density functional
  theory calculations and statistical models", Acta Mater. 94, 307-318 (2015),
  DOI 10.1016/j.actamat.2015.04.052. Search summary: two diffusion regimes reconcile DFT with Frauenfelder's
  1969 measurement. HAL copy blocked.
- "Hydrogen assisted vacancy formation in tungsten: a first-principles investigation", J. Nucl. Mater. 465,
  135-141 (2015). Search summary: spontaneous vacancy formation when more than two H are added. Authors not
  confirmed.
- Ohsawa, Hatano, Yamaguchi group finite-temperature work (about six H per monovacancy) and Kato et al.
  thermodynamic model (search summaries only; no full citation confirmed).
- Y. Hatano et al., "Deuterium trapping at defects created with neutron and ion irradiations in tungsten",
  Nucl. Fusion 53(7) (2013). Search summary: neutron 0.3 dpa at about 323 K, D plasma at 473 and 773 K.
- T. Schwarz-Selinger, "A critical review of experiments on deuterium retention in displacement-damaged
  tungsten as function of damaging dose", Mater. Res. Express 10(10) (2023), DOI 10.1088/2053-1591/acfdf8.
  Search summary: retention generally rises with damage; scatter of about three orders of magnitude between
  experiments; 20.3 MeV self-ion damage at room temperature, 0.001-2.3 dpa; deviation from linear growth at
  about 0.005 dpa; maximum about 1.4 at.% at 0.23 dpa. Strong candidate for validation targets.
- T. Schwarz-Selinger, Bauer, Elgeti, Markelj, Nucl. Mater. Energy 17, 228-234 (2018),
  DOI 10.1016/j.nme.2018.10.005. Search summary: D stabilises damage; rate-equation fit with original
  detrapping energies and only higher trap densities.
- S. Markelj et al., "The first study of deuterium retention in tungsten simultaneously damaged by high energy
  W ions and loaded by D" (EUROfusion preprint WPPFC-PR(16) 14774; I opened the PDF and it was a cover page
  only); Nucl. Mater. Energy 12, 169-174 (2017), DOI 10.1016/j.nme.2016.11.010 per search results.
- E. A. Hodille et al., macroscopic rate-equation modelling of H isotope trapping in W (HAL record
  hal-01230501; search summary: intrinsic traps about 0.87 and 1.00 eV and an ion-induced trap at 1.50 eV);
  a related HAL record "Simulations of atomic deuterium exposure in self-damaged tungsten" (hal-01528018;
  search summary: bulk detrapping energies 1.65, 1.85 and 2.06 eV in damaged W, intrinsic 0.85 and 1.00 eV).
  Venues and exact citations not confirmed; HAL pages blocked.
- B. Tyburska et al., J. Nucl. Mater. 395, 150 (2009); V. Kh. Alimov et al., J. Nucl. Mater. 420, 370 (2012)
  (citations from a search result that did not open them).
- IAEA 2024 Zibrov and IAEA Markelj presentations on D retention in self-ion-damaged W (maximum about
  1.7 at.% at 290 K damage, about four times lower at 800 K; saturation above about 0.1-0.25 dpa); blocked
  (HTTP 403).
- Japan-US TITAN / PHENIX neutron-irradiated W programme: NIFS annual-report pages and a presentation
  mention tritium TMAP4 modelling with a 1.83 eV detrapping energy and void-dominated trapping in
  high-temperature neutron-irradiated W. Not opened.
- A TMAP8 validation page (trap-creation model of Dark et al. 2024) returned HTTP 403.

## 7. Counts

Sources opened and used here: 7 with data (Ohsawa 2010 [PDF-READ]; Jin 2023; Kaur 2025; Mason 2023 (shared with
the potentials file); Johnson and Carter 2010 [abstract]; Shimada 2011 [abstract]; Hatano 2013 Materials
Transactions [abstract]). A further 4 were opened but not useful for numbers (Tirumala 2025, Li 2022, Hou 2019,
Zhang 2025). Primary experimental data at full-text level: none.
