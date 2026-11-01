Status: UNVERIFIED

# Tungsten interatomic potentials for collision cascades (candidate list)

Prepared 2026-11-01 for the placeholders `W_EAM_A`, `W_ML_A`, `WRe_A`, `WH_A` in
`docs/interfaces/physics_settings.md` section 1 (short-range treatment, validated
properties, source). Nothing here is approved. The human verifies every entry.

## How to read the provenance tags

- [FULL-HTML] I opened an HTML (arXiv/ar5iv) rendering of the full text. The page was
  passed through a summarising fetch tool, so numbers are relayed, not read by me from raw
  text. Re-check against the paper before use.
- [PDF-READ] I looked at page images of the PDF myself. Numbers marked "read directly" come
  from these.
- [ABSTRACT/METADATA] I opened only an abstract page or a repository entry page (NIST IPR,
  institutional record). No full text.
- [SEARCH-ONLY] Seen only in web-search result summaries. NOT opened. Listed at the end as
  leads. Do not cite from them.

Caveats. (1) The fetch tool sometimes said "not in page" for items that may be in the paper,
so "not stated" means "not found in what I opened". (2) For most EAM potentials I never saw a
ZBL splice range in a primary source. Where one is listed it comes from a comparison paper
(Warrier and Bhardwaj, item A6), which is a secondary source.

## Key findings for the project (read first)

- The Marinica 2013 EAM2/3/4 potentials were not built for close approaches. The paper says they
  should not be used where interatomic distances fall below about 2.2 Å and names a ZBL
  extension as future work (section 2.2, read directly from the PDF). Cascade use needs a
  ZBL join added by the user.
- None of the NIST IPR W entries I opened mention a ZBL term (NIST W list; entries for
  Marinica EAM3, Mason 2017, Ackland-Thetford, Zhou 2004, Bonny W-Re, Setyawan W-Re, Chen W-Re).
  The Ackland-Thetford entry says a short-range repulsive core was added in the 1987 fit, which
  is not a ZBL blend for keV energies.
- TDE and cascade yield depend on how the potential is joined to ZBL (De Backer 2016 Table 1: a
  soft and a hard join of one Marinica potential give different TDEs). So "which EAM" is not a
  complete specification. The splice range and function must be recorded in
  `physics_settings.md` too.
- Only the ML potentials (GAP, NEP-ZBL, tabGAP, SNAP) carry an explicit short-range treatment
  in their own papers, and only the Byggmästar GAP and NEP papers give explicit switching
  ranges.

---

## Part A. EAM / Finnis-Sinclair family

### A1. Marinica et al. 2013 (parameter sets EAM1-4; EAM2, EAM3, EAM4 distributed)

- Citation: M.-C. Marinica, L. Ventelon, M. R. Gilbert, L. Proville, S. L. Dudarev, J. Marian,
  G. Bencteux, F. Willaime, "Interatomic potentials for modelling radiation defects and
  dislocations in tungsten", J. Phys.: Condens. Matter 25, 395502 (2013).
  DOI 10.1088/0953-8984/25/39/395502.
  Open copy: https://scientific-publications.ukaea.uk/wp-content/uploads/Published/JnlPhyCondVOL25p395502.pdf
- Tag: [PDF-READ] pages 1-6 (introduction, fitting procedure, Tables 1-3, start of surfaces
  section). Remaining pages (gamma surfaces, dislocations, appendix with parameters) NOT read.
  [ABSTRACT/METADATA] for the NIST entry.
- Type: EAM, Finnis-Sinclair-style embedding (square-root term plus quadratic term), cubic-spline
  pair and density functions (eqs 1-4). Force-matching fit (ASSIMPOT code) to a mixed database:
  experimental lattice constant, cohesive energy and elastic constants; DFT (SIESTA, GGA)
  point-defect formation energies; DFT forces on liquid configurations. The paper says EAM1 is
  not used further because of a poor screw-core description.
- Short-range treatment: no ZBL. The smallest interatomic distance in the fitting database was
  2.2 Å and the authors say the potentials are unsuitable below that (section 2.2). They cite
  Björkas et al. for a ZBL extension of the DND potential and say the same would be done for
  these potentials later.
- Validated properties (Table 1, read directly). Columns are target / EAM2 / EAM3 / EAM4:
  - a0 (Å): 3.1648 / 3.14000 / 3.18737 / 3.14339. EAM2 and EAM4 are about 0.02 Å below the
    target, EAM3 about 0.02 Å above.
  - C11 (GPa): 523 / 544 / 519 / 523. C12: 203 / 208 / 203 / 202. C44: 160 / 160 / 159 / 161.
  - Vacancy formation (eV, target is SIESTA GGA): 3.49 / 3.49 / 4.38 / 3.81.
  - <111> dumbbell (eV): 10.53 / 10.52 / 10.53 / 10.53. <110>: 10.82 / 10.82 / 10.95 / 10.82.
    <100>: 12.87 / 12.86 / 11.18 / 12.72.
  - Interstitial clusters I2 and I4 (Table 2): all variants agree with DFT that <111> is most
    stable, but formation energies scatter by about 1 eV with the DFT pseudopotential choice.
    EAM2 and EAM4 put the C15 I4 cluster below the <111> I4 cluster, unlike DFT; the authors
    call this not severe for large-scale use.
  - Di-vacancy (Table 3): every variant gives strongly bound vacancies at both 1NN and 2NN,
    contrary to DFT (weak or no 1NN binding, 2NN repulsive). The authors say second-moment EAM
    cannot capture this.
  - Surface energies (Fig. 1): underestimated versus DFT; (110) is the lowest-energy surface.
  - Melting point: not seen in the pages I read. TDE: not reported in this paper.
- Repositories: NIST IPR has entries W-2, W-3, W-4 (EAM2/3/4), LAMMPS `pair_style eam/fs`.
  I opened the EAM3 entry: file `w_eam3.fs`, posted with Marinica's permission 2017-01-09.
  https://www.ctcms.nist.gov/potentials/entry/2013--Marinica-M-C-Ventelon-L-Gilbert-M-R-et-al--W-3
  The NIST EAM3 page gives OpenKIM MO_706622909913. An EAM4 OpenKIM listing
  (MO_046576227003) appeared in search results; not opened.
- Limitations: no ZBL; di-vacancy anomaly; EAM3 vacancy (4.38 vs 3.49 eV) and <100> dumbbell
  (11.18 vs 12.87 eV) are poor; EAM2 and EAM4 lattice constants are off.
- Cascade usage: De Backer 2016 (A7) joined a Marinica potential to ZBL in soft and hard
  versions.

### A2. Mason, Nguyen-Manh, Becquart 2017 ("MNB")

- Citation: D. R. Mason, D. Nguyen-Manh, C. S. Becquart, "An empirical potential for simulating
  vacancy clusters in tungsten", J. Phys.: Condens. Matter 29(50), 505501 (2017).
  DOI 10.1088/1361-648x/aa9776.
- Tag: [ABSTRACT/METADATA] (NIST entry). I did not open the paper.
- Type: EAM, LAMMPS `pair_style eam/fs`, file `W_MNB_JPCM17.eam.fs`, provided by D. Mason on
  2021-11-16.
- Short range: the NIST abstract says interstitial and short-range pair behaviour stay close
  to Ackland-Thetford. No ZBL on the NIST page. Validation: abstract-level only (surface
  energies, vacancy clusters). TDE, elastic and melting data not seen.
- Repositories: NIST IPR
  https://www.ctcms.nist.gov/potentials/testing/entry/2017--Mason-D-R-Nguyen-Manh-D-Becquart-C-S--W ;
  an OpenKIM listing (MO_268730733493) appeared in search results, not opened.
- Limitations: no ZBL; NIST page carries the generic warning about alloy-derived elemental
  potentials. This is the W-W base for the Mason 2023 W-H potential (D1).

### A3. Derlet, Nguyen-Manh, Dudarev 2007 ("DND/DD") and the ZBL-extended version

- Citation: P. M. Derlet, D. Nguyen-Manh, S. L. Dudarev, "Multiscale modeling of crowdion and
  vacancy defects in body-centered-cubic transition metals", Phys. Rev. B 76, 054107 (2007).
  DOI 10.1103/physrevb.76.054107.
- Tag: [ABSTRACT/METADATA] (NIST entry; it did not list pair_style or files in my fetch). The
  entry names OpenKIM MO_195478838873 with model driver "EAM_MagneticCubic". That looks like a
  non-standard functional form; check it is usable in plain LAMMPS before relying on it.
- ZBL-extended version: C. Björkas, K. Nordlund, S. Dudarev, "Modelling radiation effects using
  the ab-initio based tungsten and vanadium potentials", Nucl. Instrum. Methods B 267,
  3204-3208 (2009), DOI 10.1016/j.nimb.2009.06.123. Tag: [ABSTRACT/METADATA] (Helsinki research
  portal). The abstract says the repulsive part and the electron density function were
  modified to reproduce experimental defect threshold energies, with short-range interactions
  from the universal screened Coulomb potential.
- Splice range: not in what I opened. A secondary source (A6) lists "DND-BN" with ZBL
  r1/r2 = 1.1 / 2.25 Å and notes negative thermal expansion and large elastic-constant
  deviations for it.

### A4. Ackland-Thetford 1987 ("AT") and Juslin-Wirth hardening

- Citation: G. J. Ackland, R. Thetford, "An improved N-body semi-empirical model for
  body-centred cubic transition metals", Phil. Mag. A 56, 15-30 (1987).
  DOI 10.1080/01418618708204464. Tag: [ABSTRACT/METADATA] (NIST entry).
  Type EAM/FS, `eam/fs`, file `Ackland_Thetford_1987_W.eam.fs`
  (https://www.ctcms.nist.gov/potentials/entry/1987--Ackland-G-J-Thetford-R--W).
  Short range: repulsive cores fitted to electron-gas dimer calculations were added to fix
  unphysical behaviour at small separations. This alone is not a keV-cascade ZBL blend; cascade
  papers join AT to ZBL themselves (Sand 2013, benchmarks file).
- Juslin and Wirth, J. Nucl. Mater. 432, 61-66 (2013), DOI 10.1016/j.jnucmat.2012.07.023:
  primary paper NOT opened (publisher redirect only). Setyawan et al. 2015 (opened, benchmarks
  file) describe it as AT hardened at short distance. Warrier and Bhardwaj list ZBL
  r1/r2 = 1.39 / 2.6 Å for "JWPot" (secondary). Treat the splice range as unverified.

### A5. Zhou, Johnson, Wadley 2004

- Citation as given by NIST: X. W. Zhou, R. A. Johnson, H. N. G. Wadley, Phys. Rev. B 69, 144113
  (2004), DOI 10.1103/physrevb.69.144113. The NIST page lists the title as "Misfit-energy-
  increasing dislocations in vapor-deposited CoFe/NiFe multilayers".
- Tag: [ABSTRACT/METADATA] (NIST entry).
- Type: EAM generator for 16 elements including W; `pair_style eam/alloy` (file
  `W_Zhou04.eam.alloy`, ipr2, generated 2018-04-13). OpenKIM MO_621445647666 (superseded),
  MO_524392058194, MO_914556822329.
- Short range: not documented on the NIST page. I saw no W-specific validation or cascade use.
  The page says the potentials were not designed for compounds. Only a generic baseline.

### A6. Five-potential cascade comparison (secondary source for ZBL ranges)

- Citation: M. Warrier, U. Bhardwaj, "Statistical Study of the Defect Cluster Morphology in the
  Primary Damage of Tungsten from Collision Cascades from Five Inter-atomic potentials",
  arXiv:2402.00359 (v2, Sep 2025; no journal reference shown). https://arxiv.org/abs/2402.00359
- Tag: [FULL-HTML].
- Table 2 (as relayed): ZBL joining r1/r2 (Å); R = separation where the pair potential is 30 eV:
  - WSNAP (Wood-Thompson SNAP): not stiffened; R 1.4.
  - tabGAP (Byggmästar): not stiffened; R 1.27.
  - DND-BN (Björkas): 1.1 / 2.25; R 1.3.
  - "MS" (called MS_h, from Sand et al., their ref. 6): 1.3 / 2.0; R 1.45.
  - JWPot (Juslin-Wirth): 1.39 / 2.6; R 1.4.
  I did not see which paper their ref. 6 is or whether MS is a ZBL-joined Marinica potential.
  The naming matches De Backer 2016 (A7), which suggests it, but that is my inference.
- Table 3 compares TDEs, formation energies, elastic constants for each potential. The fetch
  returned no numbers, so the human should open Table 3 directly.
- Limits: tungsten only, no experimental validation of morphologies; Table 3 alignment was
  ambiguous in the extracted text.

### A7. TDE versus ZBL join (De Backer et al. 2016)

- Citation: A. De Backer, A. Sand, C. J. Ortiz, C. Domain, P. Olsson, E. Berthod, C. S. Becquart,
  "Primary damage in tungsten using the binary collision approximation, molecular dynamic
  simulations and the density functional theory", Phys. Scr. T167, 014018 (2016).
  DOI 10.1088/0031-8949/T167/1/014018. Preprint:
  https://scientific-publications.ukaea.uk/wp-content/uploads/Preprints/CCFE-PR1621.pdf
- Tag: [PDF-READ] pages 1-3 only (abstract, introduction, TDE section, Table 1).
- Method: DFT-MD (VASP, PAW; minimal-valence vs semi-core; at least 648-atom non-cubic cells)
  and classical MD with a Marinica potential interpolated to ZBL in a "soft" (MS-s) and a
  "hard" (MS-h) version. MD TDE statistics: 7000 runs, 12x12x16 cells, 6 ps thermalisation at
  36 K, 12 ps runs.
- Table 1 TDEs in eV (read directly), <100> / <110> / <111>:
  - DFT (minimal valence): 40 / 63 / 44.
  - DFT-sc (semi-core): 58 / >80 / >80.
  - MS-s: 31 / 51 / 45.
  - MS-h: 43 / 71 / 65.
- Take-away: TDE tracks the pair interaction at 1-1.5 Å (the paper correlates higher quasi-
  stopping energy there with higher TDE) and depends on the DFT pseudopotential. This bears
  directly on the validation step in section 1 of `physics_settings.md`.

---

## Part B. Machine-learned potentials

### B1. GAP for W, Byggmästar et al. 2019

- Citation: J. Byggmästar, A. Hamedani, K. Nordlund, F. Djurabekova, "Machine-learning
  interatomic potential for radiation damage and defects in tungsten", Phys. Rev. B 100, 144105
  (2019). DOI 10.1103/PhysRevB.100.144105. arXiv:1908.07330.
- Tag: [FULL-HTML] (ar5iv) plus arXiv abstract page.
- Type: Gaussian Approximation Potential (SOAP many-body term plus explicit repulsive pair
  term). In LAMMPS it needs a QUIP-type interface (the SNAP paper, B3, mentions USER-QUIP for
  GAP).
- Training set (paper Table 2): 3,749 structures, 42,410 atoms; about 2,496 distorted bcc
  cells, 46 liquid structures, 100 "short-range" structures with an added interstitial, 13
  dimers, vacancies, SIAs, surfaces.
- Short-range treatment: screened Coulomb pair potential with the screening function refitted
  to W-W all-electron DFT (DMol) data, not plain ZBL. Switched off between r1 = 1 Å and
  r2 = 2.2 Å (eqs 3-6). GAP is trained to near-zero contribution below 1.1 Å. Numerical
  instability below about 0.03 Å (Appendix A).
- Validated (Table 3 unless noted): a0 3.1852 Å (DFT 3.1854, exp 3.165); C11/C12/C44 =
  526/200/149 GPa (exp 522/204/161); vacancy formation 3.32 eV (exp 3.67 ± 0.2; DFT 3.22-3.36
  by cell size); <111> SIA 10.34 eV (DFT 10.25); melting 3540 ± 10 K (exp 3687 K, section V.1);
  (110) surface 204 meV/Å^2. TDE (section V.3, Fig. 10): minima 45.5 eV <100>, 51.5 eV <111>,
  78 eV <110> (10 degree tolerance); average 93.6 ± 5.5 eV; experiment quoted as 42 ± 1 (<100>)
  and 44 ± 1 (<111>). Also di-vacancy binding (Fig. 14), SIA clusters (Fig. 13), vacancy
  clusters (Fig. 15).
- No cascade simulations in this paper (no PKA energies, electronic stopping).
- Limitations stated: 2-3 orders of magnitude slower than analytical potentials; phonon
  discrepancies near H, P, N; about 15% overestimate of room-temperature thermal expansion;
  adatom barriers 20-30% low; <110>-<111> SIA gap 0.21 eV vs 0.29 eV DFT; only SIA clusters of
  size 1 and 2 were trained.
- Repositories: no NIST or OpenKIM entry in the NIST W list I opened. Training data and
  potential location per the 2020 paper (B2): gitlab.com/acclab/gap-data.

### B2. GAPs for bcc V, Nb, Mo, Ta, W, Byggmästar et al. 2020

- Citation: J. Byggmästar, K. Nordlund, F. Djurabekova, "Gaussian approximation potentials for
  body-centered-cubic transition metals", Phys. Rev. Materials 4, 093802 (2020).
  DOI 10.1103/PhysRevMaterials.4.093802. arXiv:2006.14365. Tag: [FULL-HTML] (ar5iv).
- W training data are those of the 2019 W GAP (rescaled to the correct lattice parameter);
  the paper calls them virtually identical. The fetch gave an ambiguous statement about
  gamma-surface training (absent in 2019 and in 2020?). Treat as unclear and check.
- Short range: refitted screened Coulomb to DMol data; GAP learns the difference. No W splice
  distance in this paper.
- Validated (W column): a0 3.185 Å; C11 524, C44 148 GPa (Table 1); vacancy formation 3.32 eV,
  migration 1.71 eV (Table 3); <111> SIA 10.35 eV vs DFT 10.29 (Table 4); melting 3540 K vs
  3687 K (Tables 5-6); heat capacity and thermal expansion (Table 2); <100> TDE compared with
  experiment in Fig. 10 (single W data point, good agreement).
- Limitations: melting point about 4% low (attributed to PBE); nonmagnetic bcc only; not tested
  for high-pressure transitions.
- Repositories: Supplemental Material and gitlab.com/acclab/gap-data. NIST/OpenKIM not mentioned.

### B3. SNAP for W, Wood and Thompson

- Citation: M. A. Wood, A. P. Thompson, "Quantum-accurate molecular dynamics potential for
  tungsten", arXiv:1702.07042 (2017). I could not confirm a journal reference from what I
  opened. https://arxiv.org/abs/1702.07042
- Tag: [FULL-HTML] (ar5iv).
- Type: linear SNAP (bispectrum) with a ZBL reference pair potential for core repulsion; radial
  cutoff 4.734 Å; genetic-algorithm fit (DAKOTA SOGA). LAMMPS `pair_style snap`; the paper says
  LAMMPS ships a W/He example.
- Training data (Table 1): subset of the Szlachta 2014 GAP W data (elastic deformations,
  vacancies, free surfaces, 300 K DFT-MD) plus EOS, liquids, multi-vacancies; dislocation data
  omitted. DFT: VASP PBE.
- Validated: a0 3.1805 Å; C11/C12/C44 518/195/144 GPa (Table 2); point defects within about
  3.5% of DFT including a repulsive divacancy (Table 3); He defects using a separate
  Juslin-Wirth He pair potential.
- Not reported: melting point, TDE, dislocations.
- Limitations stated: not tested outside the training set; subjective hyperparameters.
  Secondary note (A6): WSNAP cascades give only about 15% <111> loops and mostly C15-like
  rings, and its <110> dumbbell parameter deviates from experiment. A significant caveat for
  cluster statistics.
- Repositories: no NIST W entry seen. NIST lists a 2023 W-Zr-C SNAP (Sikorski et al.) with a
  hybrid ZBL overlay; not opened.

### B4. NEP-ZBL for W, Liu et al. 2023

- Citation: J. Liu, J. Byggmästar, Z. Fan, P. Qian, Y. Su, "Large-scale machine-learning
  molecular dynamics simulation of primary radiation damage in tungsten", arXiv:2305.08140
  (v3, Aug 2023). No journal reference on the arXiv page I opened.
- Tag: [FULL-HTML] (ar5iv).
- Type: neuroevolution potential (NEP) plus a W-W-optimised ZBL-like screened pair term (same
  screening as the Byggmästar GAP). Tersoff-type cutoff, inner 1.0 Å, outer 2.0 Å (Sec. II.1).
  Trained on the Byggmästar 2020 W reference set (3,526 structures, fcc, hcp, sc, diamond
  removed). Radial cutoff 6 Å, angular 4 Å. Run in GPUMD; 1.3e7 atom-step/s on one A100
  (Table 4). LAMMPS support is not mentioned in the paper.
- Validated (Table 3): a 3.185 Å; C11/C12/C44 = 518/201/144 GPa; B 307 GPa; vacancy
  formation 3.28 eV, migration 1.74 eV; SIA dumbbells 10.87 / 11.09 / 12.15 eV for <111> /
  <110> / <100> (overestimated, as the paper says); melting 3540 K (13,500-atom coexistence;
  exp 3687 K, DFT 3450 ± 100 K). TDE (text only): minimum 49 eV for <100> at 30 K; 117 eV
  "average" from six other directions, called a first approximation.
- Limitations stated: no electronic stopping (not implemented in GPUMD); one PKA direction
  (<135>); SIA energies overestimated. My fetch noted inconsistencies: E_d = 90 eV for the
  NRT/arc-dpa comparison vs 117 eV in the fit discussion.
- Repositories: no NIST/OpenKIM entry mentioned.

### B5. tabGAP (Mo-Nb-Ta-V-W), Byggmästar et al. 2022

- Citation: J. Byggmästar, K. Nordlund, F. Djurabekova, "Simple machine-learned interatomic
  potentials for complex alloys", Phys. Rev. Materials 6, 083801 (2022).
  DOI 10.1103/PhysRevMaterials.6.083801. arXiv:2203.08458. Tag: [FULL-HTML] (ar5iv).
- Type: tabulated GAP (2-body + 3-body + EAM-like density descriptor), 2-3 orders of magnitude
  faster than SOAP GAPs. External screened Coulomb repulsion; EAM pair-density functions held
  constant below a user-set r_min. No splice distances in the paper.
- Validation in the paper is for equiatomic MoNbTaVW (Table 1), not pure W. No W-specific
  elastic constants, SIA energies or melting point are reported there.
- Availability: code gitlab.com/jezper/tabgap; data and potential DOI
  10.23729/1e6d0215-d26b-4f5f-8f5b-df575efa6594 (as stated in the paper; I did not follow
  it). LAMMPS pair style not named in the paper. NIST/OpenKIM not mentioned.
- Used for cascades in Warrier and Bhardwaj (A6) and Byggmästar et al. 2025 (benchmarks file).
  The 2025 paper does not say which tabGAP version it used for W; verify.

### B6. Goryaeva et al. 2021 (ML potentials for Fe and W)

- Citation: A. M. Goryaeva, J. Dérès, C. Lapointe, P. Grigorev, T. D. Swinburne, J. R. Kermode,
  L. Ventelon, J. Baima, M.-C. Marinica, Phys. Rev. Materials 5, 103803 (2021),
  "Efficient and transferable machine learning potentials for the simulation of crystal
  defects in bcc Fe and W". DOI 10.1103/PhysRevMaterials.5.103803.
  Accepted manuscript record: https://wrap.warwick.ac.uk/159497/
- Tag: [ABSTRACT/METADATA] (WRAP record page only; PDF not read).
- The page describes linear and quadratic mappings from a descriptor space and does not name the
  descriptor family, so I cannot say whether it is ACE-, SNAP- or MTP-like. It reports negative
  di-vacancy binding in W and kink-pair energies. No short-range or ZBL information. Aimed at
  dislocations, point defects and clusters, not cascades. No potential-file link found.

### B7. ACE and MTP for W

- I found no ACE or MTP tungsten potential paper that I could open (gap). Search results only
  surfaced a conference abstract for a "dp-hyb-zbl" deep potential for W cascades (lead,
  not opened).

---

## Part C. W-Re potentials

None of the NIST W-Re entries mentions a ZBL or other short-range correction, and none is
documented as cascade-ready. All are [ABSTRACT/METADATA]. WRe_A for cascades would need a user-
supplied ZBL join plus validation.

| Entry | Type | Notes from NIST page |
|---|---|---|
| Bonny, Bakaev, Terentyev, Mastrikov 2017, J. Appl. Phys. 121, 165107, DOI 10.1063/1.4982361 | EAM, `eam/alloy`, WRe.eam.alloy; OpenKIM MO_234187151804 | Fitted to experiment and DFT with emphasis on point defects, elastic constants and dislocations; reproduces solution softening. Aimed at plasticity. Files sent 2017-11-02. |
| Setyawan, Gao, Kurtz 2018, J. Appl. Phys. 123, 205102, DOI 10.1063/1.5030113 | EAM, `eam/alloy`, WRe_Setyawan_set145.eam.alloy | Force-matched to DFT; for point-defect studies; good Re defect formation energies and W SIA-Re binding; pure Re melts at 3130 K vs 3459 K experiment. Repository warns pure-element behaviour may be poor. |
| Chen, Li, Gao, Zhou, Hu, Lu, Gao, Deng 2018, J. Nucl. Mater. 502, 141-153, DOI 10.1016/j.jnucmat.2018.01.059 | EAM, `eam/fs`, WRe_YC1.eam.fs | "New potentials of W, Re and W-Re for radiation defects", fitted to DFT. Only the NIST page opened, not the paper. |
| Chen, Fang, Liu et al. 2019 (Y-C_2) | EAM, `eam/fs`, WRe_YC2.eam.fs | Per NIST list: improves on Y-C_1 for interstitial migration and binding. Only the NIST system list opened. |

I found no W-Re cascade paper using a ZBL-joined W-Re potential in the search results. That is
a literature gap, not proof none exists.

---

## Part D. W-H (and W-H-He) potentials

For the trapping stage (`WH_A`). The potentials I opened are fitted at zero temperature.

### D1. Mason, Nguyen-Manh, Lindblad, Granberg, Lavrentiev 2023 ("MNL6")

- Citation: D. R. Mason, D. Nguyen-Manh, V. W. Lindblad, F. G. Granberg, M. Yu. Lavrentiev,
  "An empirical potential for simulating hydrogen isotope retention in highly irradiated
  tungsten", arXiv:2305.10814 (May 2023). The journal version appears to be
  J. Phys.: Condens. Matter 35, 495901 (2023), judged only from a UKAEA repository filename in
  a search result. The arXiv page I opened gives no journal reference. Verify.
- Tag: [FULL-HTML] (ar5iv) plus arXiv abstract page. NIST entry seen in the H-W system list.
- Type: EAM, `pair_style eam/alloy`, file `MNL6_WH.eam.alloy`, Finnis-Sinclair-style form with a
  spline correction to the embedding function. W-W part refitted starting from MNB (A2). W-H
  and H-H started from Wang et al. 2017 (J. Phys.: Condens. Matter 29, 435401; not opened).
- Short range: universal ZBL added from r = 0 to r2, with a small correction near equilibrium
  (Appendix). The r2 value was not in what I retrieved. This is the only W-H potential I opened
  with an explicit ZBL term.
- Validated (as relayed): H tetrahedral solution energy 0.798 eV (1.049 eV with zero-point
  energy) vs DFT 0.93 eV (Table 4); O-T gap 0.35 eV vs DFT 0.44; tet-tet migration barrier
  0.216 eV vs DFT 0.21 eV (Table 4, Fig. 2b); binding per H at vacancy clusters rising from
  about 1.23 eV (monovacancy) to about 1.7 eV for large clusters (Figs 9b, 10b); relaxation
  volumes (Fig. 4); (110) surface H binding 0.487 eV vs DFT 0.75 eV (Table 5).
- Limitations stated: trivacancy migration barrier 1.752 eV vs DFT 1.146 eV; (100) surface
  energy ordering wrong; H surface binding underestimated; <100> vs 1/2<111> loop energy gap
  smaller than DFT; zero-temperature configurations; MD may trap H in transient states. Versus
  Wang 2017: Wang has surface energies about 30% below DFT and lacks the rise of H binding
  with vacancy-cluster size.
- Repositories: NIST IPR 2023 entry
  https://www.ctcms.nist.gov/potentials/entry/2023--Mason-D-R-Nguyen-Manh-Lindblad-V-W-et-al--W-H
  (`eam/alloy`, files provided 2023-09-26).

### D2. Tirumala et al. 2025 (W-H-He, `eam/he`)

- Citation: S. Tirumala, D. R. Mason, O. Shattock, D. Nguyen-Manh, F. Hofmann, M. Boleininger,
  "An empirical potential to simulate helium and hydrogen in highly irradiated tungsten",
  arXiv:2509.22012 (Sep 2025). Tag: [FULL-HTML] (first 100,000 of about 130,000 characters read).
- Type: generalised Finnis-Sinclair with negative electron-density contributions allowed;
  implemented as `pair_style eam/he` (availability in stock LAMMPS not checked). W-H part builds
  on Mason 2023.
- Short range: ZBL as prior for pair potentials, splines constrained to match ZBL; the
  r1/r2/rc values are in an appendix that was truncated in my read.
- Focus is He and H-He. H solution energy, diffusion barrier and TDE are not covered in the part
  I read. Limitations: He formation energy overestimated (6.73 vs 6.16 eV DFT, Table 1);
  artificial void-H2 attraction (section V.4); accuracy drops at high stress where ZBL dominates
  (Fig. 3).
- Availability: on request to the UKAEA publications manager; no repository link seen.

### D3. Bonny, Grigorev, Terentyev 2014 (W-H-He, EAM1/EAM2)

- Citation: G. Bonny, P. Grigorev, D. Terentyev, "On the binding of nanometric hydrogen-helium
  clusters in tungsten", J. Phys.: Condens. Matter 26(48), 485001 (2014).
  DOI 10.1088/0953-8984/26/48/485001. Tag: [ABSTRACT/METADATA] (NIST entry).
- Type: EAM, `eam/alloy`, file `potential-WHHe-EAM2.eam.alloy`; OpenKIM MO_626183701337 for the
  EAM2 listing. Only W has an electron-density function; H and W embedding functions take the
  W density (contributor note on NIST). NIST does not name the W-W base or mention ZBL.
- Tirumala 2025 says this potential was not fitted to reproduce gaseous H and He properties.

### D4. Other W-H items (not opened beyond lists)

- Oh, Sung, Jang, Ko, Han 2024, MEAM (`meam`), files WH.meam and library.meam (NIST H-W list).
- Wang et al. 2017 is described by Mason 2023 as giving the best H-vacancy-cluster binding in
  earlier literature with poor surface energies. Li et al. (bond-order) and Yang et al. (hybrid
  of Marinica W-W, Wang W-H, Juslin W-He) are referred to in Tirumala 2025. None opened.

---

## Part E. Electronic-effect parameters seen in sources (for `es_default`, `eph_ttm_A`)

Values the sources used, not recommendations. From [FULL-HTML] reads; see the benchmarks file.

- Zarkadoula et al. 2015 (J. Phys.: Condens. Matter 27, 135401): friction 1.1 ps^-1 from SRIM
  tables, applied above a velocity set by twice the cohesive energy (no numeric cutoff given);
  g_p = 7e17 W m^-3 K^-1 (experimental range cited 5-10e17); electronic thermal conductivity
  174 W/m/K at 300 K and 125 W/m/K at 800 K; electronic heat capacity from ab initio data
  (values not in the text); coupling switched on at 0.3 ps.
- Sheng et al. 2025 (Frontiers in Physics 13, 1592186): g_p = 5e17 W m^-3 K^-1,
  kappa_e = 174 W/m/K, electronic heat capacity from a cited ab initio source, friction from SRIM.
- Sand et al. 2013: SRIM friction with a low-energy cutoff Tc tested at 1, 5, 10, 20, 100 eV.
- Byggmästar et al. 2025: friction above 10 eV, SRIM data.
- Disagreement: coupling constants differ (7e17 vs 5e17) and the friction cutoff ranges from 1 to
  100 eV across papers. No source I opened measured the cutoff in W; Sand 2013 itself says a
  threshold in W is unconfirmed.

---

## Comparison table

"Splice" = short-range switching range as stated in the cited source. "n/s" = not stated in what
I opened.

| Potential | Type | Short-range / splice | Validated per source | NIST / OpenKIM | LAMMPS style | Main limitation |
|---|---|---|---|---|---|---|
| Marinica EAM2/3/4 (2013) | EAM FS | None in paper; unsuitable below 2.2 Å | a0, C_ij, vacancy, SIA, I2/I4, surfaces (Tables 1-3) | NIST W-2/3/4; OpenKIM EAM3 MO_706622909913 | eam/fs | Needs ZBL join; di-vacancy binding wrong |
| MNB (Mason 2017) | EAM FS | Inherits AT; no ZBL stated | Vacancy clusters, surfaces (abstract only) | NIST; OpenKIM MO_268730733493 (search only) | eam/fs | Paper not opened |
| DND (Derlet 2007) | EAM (magnetic-cubic form in OpenKIM) | None | Crowdion, vacancy (abstract) | NIST list; OpenKIM MO_195478838873 | n/s | Non-standard OpenKIM driver |
| DND-BN (Björkas 2009) | EAM + ZBL | 1.1/2.25 Å (secondary, A6) | Experimental threshold energies (abstract) | Not found | n/s | Negative thermal expansion, elastic deviations (A6) |
| Ackland-Thetford 1987 | EAM FS | Dimer-fitted core only | Basic bcc properties | NIST | eam/fs | Needs ZBL join for cascades |
| JW (Juslin-Wirth 2013) | AT hardened | 1.39/2.6 Å (secondary, A6) | Not opened | Not found | n/s | Primary not opened |
| Zhou 2004 | EAM | n/s | n/s for W | NIST + 3 OpenKIM | eam/alloy | Not designed for cascades |
| GAP W (Byggmästar 2019) | GAP | Screened Coulomb, switch 1.0-2.2 Å | a0, C_ij, E_vac, SIA, melting 3540 K, TDE | Not found | via QUIP | Slow (2-3 orders); TDE average 93.6 eV |
| GAP bcc (2020) | GAP | Same, no W splice stated | As above plus thermal, migration | Not found | n/s | Melting 4% low |
| SNAP W (Wood-Thompson) | SNAP + ZBL | ZBL, range n/s (A6: R 1.4) | a0, C_ij, point defects | Not found | snap | Few properties tested; C15/loop morphology (A6) |
| NEP-ZBL W (Liu 2023) | NEP + ZBL | 1.0-2.0 Å | a0, C_ij, E_vac, SIA, melting, TDE min | Not found | GPUMD (LAMMPS n/s) | SIA overestimated; no electronic stopping in GPUMD |
| tabGAP MoNbTaVW (2022) | tabulated GAP | Screened Coulomb, no splice given | Alloy only (Table 1) | Not found | n/s | Pure W not validated in that paper |
| Goryaeva 2021 | ML (family n/s) | n/s | Divacancy, Peierls, kink pairs | Not found | n/s | No short-range information |
| Mason 2023 W-H (MNL6) | EAM + ZBL | ZBL to r2 (value not retrieved) | H solution, barrier, binding, relaxation volumes | NIST W-H | eam/alloy | Trivacancy barrier, surface binding |
| Tirumala 2025 W-H-He | gen. FS | ZBL prior (ranges not retrieved) | He, H-He, H-void | Not found | eam/he | Over-stabilised trap mutation |
| Bonny 2014 W-H-He | EAM | Not mentioned | H-He cluster binding | NIST H-He-W; OpenKIM EAM1/EAM2 | eam/alloy | Not fitted to gaseous H, He |
| Bonny 2017 W-Re | EAM | Not mentioned | Plasticity, point defects | NIST; OpenKIM MO_234187151804 | eam/alloy | No ZBL |
| Setyawan 2018 W-Re | EAM | Not mentioned | Point defects, Re clusters | NIST | eam/alloy | No ZBL; pure-Re melt 3130 K |
| Chen 2018/2019 W-Re | EAM | Not mentioned | (NIST page only) | NIST | eam/fs | Papers not opened |

## Disagreements and cautions to flag

1. TDE spread: GAP 2019 average 93.6 ± 5.5 eV (minima 45.5-78 eV); NEP-ZBL "average" 117 eV
   (minimum 49 eV); De Backer Table 1 has DFT <100> at 40 eV vs 58 eV with semi-core, and soft vs
   hard ZBL join moving MD <111> from 45 to 65 eV. Experiment quoted in the GAP paper is 42-44 eV
   for <100>/<111>.
2. Cluster statistics differ strongly by potential (Warrier and Bhardwaj): SNAP mostly C15-like
   rings, tabGAP fewest defects, EAM variants differ in clustered fraction. Potential choice is a
   first-order uncertainty for any cluster benchmark.
3. GAP 2019 vs 2020 gamma-surface training statement is unclear (B2).
4. Several NIST entries carry the generic warning that elemental potentials taken from alloy
   descriptions may not work for the pure element.

## Sources not opened (leads only; do not cite from these)

- Juslin and Wirth 2013 primary paper (publisher redirect only).
- Wang et al. 2017, J. Phys.: Condens. Matter 29, 435401 (W-H EAM).
- Szlachta et al. 2014 W GAP (cited by the GAP and SNAP papers I opened; full citation not verified).
- Mason, Nguyen-Manh, Becquart 2017 primary paper.
- Chen et al. 2018 and 2019 primary papers (W-Re).
- A conference abstract for a "dp-hyb-zbl" deep potential for W cascades (aconf.org, search
  results only).
- NIST W MEAM entries (Hiremath 2022, Oh 2022, Sharifi 2025): list only; mechanics-oriented, no
  ZBL noted.

## Counts

21 sources opened (papers or repository entries): Part A 8 (Marinica, MNB, DND, Björkas, Ackland-
Thetford, Zhou, Warrier and Bhardwaj, De Backer); Part B 6 (GAP 2019, GAP 2020, SNAP, NEP-ZBL, tabGAP,
Goryaeva); Part C 4 (Bonny 2017, Setyawan 2018, Chen 2018, Chen 2019 via the NIST list only); Part D 3
(Mason 2023, Tirumala 2025, Bonny 2014). Reading depth: 10 at full-text level, whole or in part (Marinica
and De Backer as PDF pages, Warrier, GAP 2019, GAP 2020, SNAP, NEP-ZBL, tabGAP, Mason 2023, Tirumala 2025 as
HTML); 11 at abstract or repository-entry level. Three NIST system-list pages (W, Re-W, H-W) were also
opened.
