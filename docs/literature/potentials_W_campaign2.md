Status: UNVERIFIED

# W potentials for Campaign 2: DND-BN, M-S, and other cascade-tested potentials

Prepared 2026-11-02 for the Campaign 2 plan in `docs/scope.md` (JW vs DND-BN vs M-S, following
Bhardwaj, Sand and Warrier, arXiv:2009.14540). Nothing here is approved. The human verifies every
source and every number before use. Missing items are marked TODO-LIT.

Provenance tags used below:
- [PAGE-IMAGE] I looked at rendered page images of a PDF. Numbers come from my reading of those
  images (small digits can be misread). I flag where I also did a check.
- [TEXT-LAYER] Text extracted from a PDF. Minus signs and exponents can be lost in extraction.
- [HTML/SUMMARY] A web page passed through a summarising fetch tool. Numbers are relayed, not read
  by me from raw text.
- [ABSTRACT/METADATA] Only an abstract or repository entry page.
- [LEAD, NOT OPENED] Seen only in a search-result summary. Do not cite.

## 1. Short answer

| Potential | Can we build it now? | What is missing | Key benchmark numbers |
|---|---|---|---|
| DND-BN (Derlet 2007 base + Bjorkas 2009 short-range modification) | Yes in principle. Every input was found in papers I opened: the analytic W base potential (Derlet Table IV), the ZBL/polynomial pair splice and the cubic density splice (Bjorkas Tables I, II with the 2010 erratum). No ready LAMMPS file is distributed (NIST has no file; OpenKIM has a non-standard driver). We would write an `eam/fs` generator like `make_jw.py`. | Human check of my digit transcription (section 3.5); which r2 the benchmark paper's file used (2.25 vs 2.10 Å, section 3.4); ZBL shift for W not stated (my check suggests none, section 3.4); F(rho) table range. | Bjorkas TDE (4 K): min 41, <100> 41, <110> 93, <111> 41, average 84.5 eV. Warrier and Bhardwaj Table 3: TDE mean 100.57, min 42.30, <100> 42.30 eV. FP at 5 and 10 keV: figure-only (section 5). |
| M-S (Marinica 2013 stiffened by Sand 2016, "hard" version) | Base file: yes (NIST `w_eam4.fs`, eam/fs), if EAM4 is the right variant (not confirmed). Modification: no. | Sand et al. 2016 (J. Nucl. Mater. 470, 119) is the primary source and I could not open it. Missing: which Marinica variant, ZBL form and any shift, polynomial constraints, any distributed file. Only r1/r2 (1.3/2.0 Å) and stiffness numbers from secondary sources. | De Backer 2016 TDE for MS-h (<100>/<110>/<111>): 43/71/65 eV (MS-s 31/51/45). Warrier and Bhardwaj Table 3: TDE mean 96.79, min 43.00 eV. FP at 5 and 10 keV: figure-only. |
| tabGAP (ML) | Not with the stock LAMMPS build: needs a separate pair style from the tabGAP repository. | Which tabGAP file the benchmark papers used (the two papers cite different tabGAP papers); licence of the potential files. | Byggmästar 2025: 4.59 FP (5 keV) and 7.59 FP (10 keV), 100 runs each, 300 K; TDE min 42, average 95 eV. |
| Other ML (GAP, SNAP, NEP, ACE) | Not examined beyond leads; see section 6. | Primary sources not reopened in this session. | See `docs/literature/w_potentials.md` Part B (earlier session). |

## 2. Sources opened in this session

1. U. Bhardwaj, A. E. Sand, M. Warrier, "Comparison of SIA defect morphologies from different
   interatomic potentials for collision cascades in W", arXiv:2009.14540 (v3, 30 May 2021);
   published as Modelling Simul. Mater. Sci. Eng. 29, 065015 (2021), DOI 10.1088/1361-651X/ac095d
   (DOI as listed on the arXiv page and in the other paper's reference list).
   https://arxiv.org/abs/2009.14540 . [PAGE-IMAGE], whole paper read.
2. M. Warrier, U. Bhardwaj, "Statistical study of the defect cluster morphology in the primary damage of
   tungsten from collision cascades from five inter-atomic potentials", arXiv:2402.00359
   (v2, 4 Sep 2025; no journal reference on the page). https://arxiv.org/abs/2402.00359 .
   License on the arXiv page: CC BY 4.0. [PAGE-IMAGE], pages 1-14 read including Tables 1-3, Figs 1-4.
3. C. Bjorkas, K. Nordlund, S. Dudarev, "Modelling radiation effects using the ab-initio based
   tungsten and vanadium potentials", Nucl. Instrum. Methods B 267, 3204 (2009),
   DOI 10.1016/j.nimb.2009.06.123, author preprint
   http://www.mv.helsinki.fi/home/knordlun/pub/Bjo08cpreprint.pdf , bundled with
   Erratum, Nucl. Instrum. Methods B 268, 1529 (2010), DOI 10.1016/j.nimb.2010.01.011.
   [TEXT-LAYER] and [PAGE-IMAGE]. The erratum page is rotated and low resolution; its minus signs
   were missing from the text layer, so I recovered them from the image and by the checks in 3.4.
4. P. M. Derlet, D. Nguyen-Manh, S. L. Dudarev, "Multiscale modeling of crowdion and vacancy
   defects in body-centered-cubic transition metals", Phys. Rev. B 76, 054107 (2007),
   DOI 10.1103/PhysRevB.76.054107. I read the UKAEA preprint UKAEA FUS 544 (April 2007):
   https://scientific-publications.ukaea.uk/wp-content/uploads/UKAEA-FUS-544FINAL.pdf .
   [PAGE-IMAGE], pages 1-24 and the appendix tables (preprint page 30). Not the published version.
5. A. De Backer et al., "Primary damage in tungsten using the binary collision approximation,
   molecular dynamic simulations and the density functional theory", Phys. Scr. T167, 014018
   (2016), DOI 10.1088/0031-8949/T167/1/014018.
   https://scientific-publications.ukaea.uk/wp-content/uploads/Preprints/CCFE-PR1621.pdf .
   [PAGE-IMAGE], pages 1-4.
6. NIST IPR entry for Marinica et al. 2013, W-4 (EAM4):
   https://www.ctcms.nist.gov/potentials/entry/2013--Marinica-M-C-Ventelon-L-Gilbert-M-R-et-al--W-4
   and the file header of `w_eam4.fs`
   (https://www.ctcms.nist.gov/potentials/Download/2013--Marinica-M-C-Ventelon-L-Gilbert-M-R-et-al--W-4/1/w_eam4.fs).
   [HTML/SUMMARY] for the page; header lines as returned by the fetch.
7. NIST IPR W system list (first half of the page only):
   https://www.ctcms.nist.gov/potentials/system/W/ . [HTML/SUMMARY]
8. NIST IPR entry for Derlet et al. 2007 W:
   https://www.ctcms.nist.gov/potentials/entry/2007--Derlet-P-M-Nguyen-Manh-D-Dudarev-S-L--W
   [ABSTRACT/METADATA] (returned very little).
9. OpenKIM model pages: Derlet-Nguyen-Dudarev W, MO_195478838873_002
   (https://openkim.org/id/MO_195478838873_002 , DOI 10.25950/45d538ba) and Marinica EAM4,
   MO_046576227003_000 (https://openkim.org/id/MO_046576227003_000 , DOI 10.25950/ce93b9c6).
   [HTML/SUMMARY]
10. A. Roy, G. Nandipati, A. M. Casella, D. J. Senor, R. Devanathan et al. (author list truncated on
    the page I saw), "A review of displacement cascade simulations using molecular dynamics
    emphasizing interatomic potentials for TPBAR components", npj Mater. Degrad. 9, 1 (2025),
    DOI (from the URL identifier) 10.1038/s41529-024-00536-9. Secondary source. [HTML/SUMMARY],
    first ~100,000 of ~277,000 characters only.
11. J. Byggmästar, V.-M. Yli-Suutala, A. Fellman, J. Åström, J. Westerholm, F. Granberg, "Four regimes
    of primary radiation damage in tungsten", arXiv:2503.02710 (HTML v2),
    https://arxiv.org/abs/2503.02710 . [HTML/SUMMARY] (includes supplement Table S3 values as relayed).
12. tabGAP code repository, https://gitlab.com/jezper/tabgap (project page and README only).
    [HTML/SUMMARY]
13. J. Byggmästar, K. Nordlund, F. Djurabekova, "Modeling refractory high-entropy alloys with
    efficient machine-learned interatomic potentials: defects and segregation", Phys. Rev. B 104,
    104101 (2021), arXiv:2106.03369. [ABSTRACT/METADATA]
14. D. R. Mason, D. Nguyen-Manh, C. S. Becquart, "An empirical potential for simulating vacancy
    clusters in tungsten" (EUROfusion preprint WPMAT-PR(17) 18391; J. Phys.: Condens. Matter 29,
    505501, 2017).
    https://scipub.euro-fusion.org/wp-content/uploads/eurofusion/WPMATPR17_18391_submitted.pdf .
    [PAGE-IMAGE], title page and abstract only.

Not opened (blocked or paywalled), important for M-S: A. Sand, J. Dequeker, C. Becquart, C. Domain,
K. Nordlund, "Non-equilibrium properties of interatomic potentials in cascade simulations in
tungsten", J. Nucl. Mater. 470, 119-127 (2016), DOI 10.1016/j.jnucmat.2015.12.012. Publisher link
only redirected; HAL record blocked; a conference slide deck returned HTTP 402; no open copy found.

## 3. DND-BN

### 3.1 What it is
Derlet-Nguyen-Manh-Dudarev (DND) Finnis-Sinclair-type potential for non-magnetic bcc metals
(Derlet 2007), with the repulsive pair term and the density function altered at short range by
Bjorkas, Nordlund and Dudarev (2009) so that threshold displacement energies match experiment.
Bhardwaj/Sand/Warrier call the result "DND-BN" (their ref. [34] is the Bjorkas paper).

### 3.2 Where the base potential is distributed and in what format
- NIST IPR: an entry exists, but the W-list fetch showed no downloadable LAMMPS file; it lists
  OpenKIM only (MO_195478838873). [HTML/SUMMARY]
- OpenKIM: the model uses the `EAM_MagneticCubic` driver, a non-standard form; the page did not list
  file names, and I could not see its parameter files. Its verification summary reports energy
  continuity (C0) but a failed dimer C1 continuity check (grade F). I do not know what that means for
  cascades. TODO-LIT: open the OpenKIM archive to see whether the parameters are plain tables.
- The paper itself gives the full analytic potential (section 3.5), so the base potential can be
  tabulated without any distributed file. The Derlet paper states that, without a short-range
  correction, the potentials are "not suitable for simulating high-energy collision cascades".
- No ready modified DND-BN file found anywhere. TODO-LIT: ask the Helsinki/UKAEA authors, or the
  Warrier/Bhardwaj group, whether one is distributed.

### 3.3 Functional form (Derlet 2007, preprint pp. 13-15)
E = sum_i F(rho_i) + (1/2) sum_{i!=j} V(r_ij); rho_i = sum_j f(r_ij); F(rho) = -A sqrt(rho);
f(r) = sum_n f_n (r_n^f - r)^3 Theta(r_n^f - r); V(r) = sum_n V_n (r_n^V - r)^3 Theta(r_n^V - r).
The paper says the equilibrium density rho_0 is chosen as unity.

### 3.4 Short-range modification (Bjorkas 2009 Eqs. 1-5, Tables I-II, with the erratum)
Pair term (Eq. 1): V_BN = V_ZBL for r <= r1; V_int (fifth-order polynomial, Eq. 2) for r1 < r < r2;
V_DND for r >= r2. The polynomial was built for continuity of value and of the first and second
derivatives at r1 and r2. ZBL is the universal potential (Ziegler, Biersack, Littmark 1985).
Density (Eq. 4): f_BN = rho_0 (a constant) for r <= r3; a cubic (Eq. 5) for r3 < r < r4;
f_DND for r >= r4. rho_0 here is the Bjorkas Table I symbol, not the equilibrium density.

Corrected W values (erratum Tables 1 and 2, W row). The original paper's W values were wrong
because of a mix-up (erratum); the erratum says the W cascades were run with the erroneous
potential but agreed within statistics. [TEXT-LAYER + PAGE-IMAGE]

| Quantity | Corrected value (erratum) | Original paper (superseded) |
|---|---|---|
| r1 (Å) | 1.10002200044 | 1.10002200044 |
| r2 (Å) | 2.10004200084 | 2.2500450009 |
| r3 (Å) | 1.5000300006 | same |
| r4 (Å) | 1.80003600072 | same |
| rho_0 (density plateau) | 10.0064910346 | same |

Polynomial coefficients, V_int(r) = a0 + a1 r + ... + a5 r^5, in eV and Å (erratum):
- a0 = +1.389653276380862e4
- a1 = -3.596912431628216e4
- a2 = +3.739206756369099e4
- a3 = -1.933748081656593e4
- a4 = +0.495516793802426e4
- a5 = -0.050264585985867e4

Density cubic, f_int(r) = b0 + b1 r + b2 r^2 + b3 r^3 (unchanged by the erratum):
- b0 = -0.659035020672109e3
- b1 = +1.199684049310425e3
- b2 = -0.707527073754107e3
- b3 = +0.136726326994010e3

The superseded original-paper a-coefficients are not reproduced here on purpose; use the erratum.

ZBL shift: the text says a 10 eV reduction of ZBL was used for vanadium (and the erratum says that
for V it was actually an increase). For tungsten no shift is mentioned in anything I read.

My checks (by hand arithmetic, about 3-4 significant figures; the human should redo them in code):
- V_int(r1) = 282.0 eV, against unshifted universal ZBL(r1) = 281.8 eV (ZBL as coded in
  `make_jw.py`: Z = 74, a_u = 0.4685/(2 Z^0.23)). They agree to about 0.1%, which supports "no
  shift for W" and the sign pattern +,-,+,-,+,- of the a-coefficients.
- V_int(r2 = 2.10004) = 16.01 eV, against V_DND(2.10004) = 16.02 eV evaluated from Derlet Table IV.
  Agreement supports the erratum r2 = 2.10004 and the Table IV transcription. (With r2 = 2.25 and
  these coefficients there is no reason to expect a join.)
- f_int(r3) = 10.0065 and f_int'(r3) = 0, matching rho_0 = 10.00649.
- f_int(r4) = 5.3958 against f_DND(r4) = 5.396 from Table IV.
I did not check second-derivative continuity.

Disagreement to resolve: Warrier and Bhardwaj Table 2 list DND-BN r1 = 1.1 and r2 = 2.25 Å, which is
the uncorrected value from the first print of the Bjorkas paper. Either they used a file built from
the uncorrected table, or the 2.25 is just copied. The erratum says the effect on cascades is within
statistics, but the two files are different potentials. TODO-LIT: which file did Bhardwaj/Warrier use?

### 3.5 Derlet 2007 tungsten parameters (preprint Table IV, p. 30) [PAGE-IMAGE, digits read from a
rendered page; verify every digit against the published paper]

A = 10.84238200368439. Knots (r in Å):

| r_n^f | f_n | r_n^V | V_n |
|---|---|---|---|
| 3.3216 | 1.677334871575606 | 4.2689 | -0.1036435865158945 |
| 3.165333333333333 | -1.673137509507131 | 3.98568 | -0.2912948318493851 |
| 3.009066666666667 | -4.737051994974169 | 3.70246 | -2.096765499656263 |
| 2.8528 | 7.870789420780674 | 3.41924 | 19.16045452701010 |
| 2.7411 | -3.7924230525563378e-4 (sign read from image, uncertain) | 3.13602 | -41.01619862085917 |
| 2.604045 | 6.190816158916646 | 2.8528 | 46.05205617244703 |
| 2.46699 | -0.9565713891199151 | 2.7411 | 26.42203930654883 |
| | | 2.604045 | 15.35211507804088 |
| | | 2.46699 | 14.12806259323987 |

My check of this transcription (hand arithmetic): with a0 = 3.1652 Å, 8 neighbours at 2.7411 and
6 at 3.1652, rho = 1.0001 (should be 1, as the paper states); the cohesive energy comes out
-8.900 eV (paper Table II: -8.9). The 2.10004 and 1.80004 joins in 3.4 additionally test the
short-range knots. The one uncertain digit is the sign of the tiny f_n at 2.7411 (a flip changes f
by less than 1e-3 near r = 1.8 Å).
Paper Table II targets for W (fit in brackets): a0 3.1652 Å, E_c -8.9 eV, B 310.4 GPa, C' 160.6,
C44 159.0, E_vac 3.56 (3.56), E_<111> dumbbell 9.548 (9.550), <110> 9.844 (9.841),
<100> 11.490 (11.513), tetrahedral 11.050 (10.999), octahedral 11.680 (11.709) eV.

### 3.6 Build recipe (to be turned into a task card by the main agent)
1. Evaluate F, f, V from 3.3 and 3.5 on a fine grid; apply the Bjorkas splices (3.4).
2. Write `eam/fs` (one element): F(rho) table, rho(r) = f_BN(r), r*V_BN(r). Cutoff: V ends at
   4.2689 Å, f at 3.3216 Å.
3. F(rho) = -A sqrt(rho) has an infinite slope at rho = 0 and the density plateau is about 10 per
   neighbour at close range, so the rho range of the table must be chosen with care (TODO-DECIDE;
   I have not checked how LAMMPS treats rho beyond the table).
4. Acceptance tests from published numbers: Derlet Table II (a0 3.1652, B 310.4, formation
   energies); Bjorkas Table III TDE; Warrier and Bhardwaj Table 3 (section 5).
5. Flag: Warrier Table 3 gives DND-BN a = 3.17 Å and B = 315.29 GPa, but the splices act only below
   2.1 Å and so should not change perfect-lattice properties, which Derlet gives as a0 = 3.1652 Å
   and B = 310.4 GPa. A 1.6% difference in B is unexplained (different file, tabulation, or
   measurement temperature). Test our rebuilt file before trusting either.

### 3.7 Licence and redistribution
Not stated on any page I opened (NIST entry, OpenKIM page, the papers). The Derlet UKAEA preprint
carries a UKAEA copyright notice. A file we generate from published equations is our own
computation, but whether it can be redistributed as "DND-BN" is TODO-LIT (ask the authors).

## 4. M-S (Marinica 2013, stiffened by Sand et al. 2016)

### 4.1 Where the base potential is distributed
- NIST IPR W-4 (EAM4), LAMMPS `pair_style eam/fs`, file `w_eam4.fs`, "sent by M.-C. Marinica on
  9 January 2017 and posted with his permission". Header read from the file: 1 element W;
  Nrho = 100001, drho = 1.67096602091006e-4; Nr = 100001, dr = 5.5e-5 Å; cutoff 5.5 Å; line
  "74 183.84 3.14339 BCC". So the grid is fine enough for any splice (dr = 5.5e-5 Å), and the F table
  reaches rho = 16.7. Download:
  https://www.ctcms.nist.gov/potentials/Download/2013--Marinica-M-C-Ventelon-L-Gilbert-M-R-et-al--W-4/1/w_eam4.fs
  Entries for W-2 and W-3 (files `w_eam2.fs`, `w_eam3.fs`) were in the NIST W list. [HTML/SUMMARY]
- OpenKIM EAM4: MO_046576227003 (a newer version _001 exists), DOI 10.25950/ce93b9c6, "C1 continuous".
- Which Marinica variant Sand et al. stiffened is NOT confirmed by any source I opened. A search
  summary named EAM4 but I did not open its source [LEAD, NOT OPENED]. The Roy review says only "a
  tungsten potential by Marinica". TODO-LIT. (Update in section 10: Warrier and Bhardwaj arXiv v1 names EAM4.)
- Marinica 2013 itself (J. Phys.: Condens. Matter 25, 395502, DOI 10.1088/0953-8984/25/39/395502)
  states these potentials are not meant for distances below about 2.2 Å; see
  `docs/literature/w_potentials.md` A1 (read in an earlier session; not reopened now).

### 4.2 The short-range modification
What I could verify from opened sources:
- Bhardwaj/Sand/Warrier 2021 (ref. [24] there is Sand 2016) and Warrier and Bhardwaj 2025 call the
  potential "M-S" or "MS_h": Marinica's potential "stiffened for cascade simulations by Sand et al."
- Warrier and Bhardwaj Table 2 (MS row, specifically the MS_h potential): r1 = 1.3 Å, r2 = 2.0 Å,
  R = 1.45 Å, S = -137, S/R = -95 per Å. R is "the inter-atomic separation for which the pair
  potential is 30 eV" and S the slope there. By my own estimate of the ZBL values, R for JW
  (1.4 Å) does not match the pair term alone (ZBL-10 is about 76 eV at 1.4 Å), so I think their
  Fig. 1 and Table 2 use the total two-atom energy including embedding. I did not verify this. So R
  and S cannot be used to set r1/r2.
- Roy et al. 2025 review (secondary): Sand et al. used "a fifth-degree polynomial" to spline ZBL and
  made two interpolations of a Marinica potential. M-S_h: S = -140.5 eV/Å, R = 1.5 Å; M-S_s:
  S = -552.0 eV/Å, R = 1.1 Å (S/R 93.7 and 501.8). These are consistent with the Warrier row (-137,
  1.45, -95) for the hard version. Warrier's text also quotes "S = -552 and R = -502" for an "MS_x"
  potential; I read this as a typo mixing S and S/R of M-S_s (-552/1.1 = -502), my inference.
- De Backer 2016: one of Marinica's potentials "interpolated to ZBL" in a soft (MS-s) and a hard
  (MS-h) version; no radii or form given there. Its Fig. 1b shows MS-h close to ZBL.

What is missing (TODO-LIT, all needed to rebuild like `make_jw.py`):
- r1 and r2 for the soft version (a search summary said 0.6 and 1.2 Å [LEAD, NOT OPENED]).
- ZBL form actually used (universal ZBL assumed), and whether it was shifted (as for JW, -10 eV) or
  not.
- Polynomial constraints (value only? value and slope? value, slope and curvature as in Bjorkas?) and
  coefficients. Only "fifth-degree" is known, from a secondary source.
- Whether the F(rho) and rho(r) tables are modified too (Bjorkas modified the density for DND).
- Whether a ready file exists. None found.
Route: obtain Sand 2016 (library, or ask A. E. Sand). If the constraints are Bjorkas-like
(continuity of value, slope, curvature at both ends), a quintic from r1 = 1.3 and r2 = 2.0 Å and the
EAM4 pair term plus ZBL would be fully determined, but that is my inference and the ZBL shift is
unknown. Do not treat a provisional build as "M-S".

### 4.3 Licence
NIST page: no licence or terms found; the file is posted with the contributor's permission. OpenKIM
page text I captured stated no licence. TODO-LIT.

## 5. Benchmarks from the papers

All from opened sources. Caution: the comparisons are not like for like (temperatures, stopping,
cell sizes, thermostat and analysis differ).

### 5.1 Warrier and Bhardwaj 2025 (the most relevant: LAMMPS, 5-150 keV, 300 K, 100 random
directions, NVE with edge thermostat, variable timestep, friction stopping per Hemani et al.;
box sizes as in our project: 5 keV 50^3 cells, 10 keV 75^3 cells)
Table 3 [PAGE-IMAGE; DFT and experimental columns as printed there]:

| Property | DFT | Expt | JW | MS | DND-BN | tabGAP |
|---|---|---|---|---|---|---|
| a (Å) | 3.185 | 3.165 | 3.160 | 3.160 | 3.17 | 3.18 |
| C11 / C12 / C44 (GPa) | 521/195/147 | 522/204/161 | 494.46/200.44/152.08 | 619.76/255.88/192.40 | 535.60/205.13/159.73 | 543.21/186.52/137.86 |
| B (GPa) | 315 | 310 | 298.45 | 377.18 | 315.29 | 305.42 |
| Vacancy formation (eV) | 3.36 | 3.8 | 3.84 | 3.56 | 3.65 | 3.40 |
| SIA <100> / <110> / <111> dumbbell (eV) | 12.2/10.58/10.29 | 11.5/10.6/10.3 | 12.19/10.15/9.91 | 11.50/9.83/9.54 | 10.17/10.01/9.57 | 11.93/10.72/10.56 |
| <110>-<111> difference (eV) | 0.29 | 0.30 | 0.24 | 0.29 | 0.44 | 0.15 |
| Thermal expansion (1e-6/K) | 4.9 | 4.5 | 8.74 | 5.19 | -0.97 | 6.79 |
| TDE mean (eV) | | 90.0 | 133.79 | 96.79 | 100.57 | 109.85 |
| TDE max / min (eV) | | | 249.0/54.3 | 199.70/43.00 | 163.00/42.30 | 187.70/38.30 |
| TDE "100" (eV) | | 42.0 | 54.30 | 43.00 | 42.30 | 38.30 |

("TDE 100" is my reading as the <100> direction; the paper does not define it on the page I read.)
Defect counts: only in Fig. 2 (number of defects vs energy, log scale, error bars = standard
deviation over 100 directions, arc-dpa curve shown). By eye at 5 keV the EAM potentials lie between
about 5 and 7 and tabGAP near 4.3; at 10 keV between about 7 and 10 and tabGAP near 6.5. These are
my eyeball estimates, good to perhaps +-1, and the curves overlap within the error bars. TODO-DIGITIZE
(already planned for JW in `physics_settings.md` B1/B2; the same figure carries DND-BN and MS).
Clustered fraction of defects (Fig. 3, by eye): the text says it ranges 0.45-0.55 across potentials
at 5 keV. At 5-10 keV MS is lowest (about 0.44) and JW, DND-BN and tabGAP are near 0.5. At high
energy the text and figure give DND-BN the largest fraction and MS the smallest.
Text also says JW and MS agree closely in defect count and tabGAP gives the fewest at all energies.
Their main conclusion: defect counts agree across the EAM potentials within the spread, but
clustering and morphology differ (about 80% of clusters are 1/2<111> for JW and tabGAP, about 60%
for MS and DND-BN; MS makes the most ring/C15-like clusters).

### 5.2 Bhardwaj, Sand, Warrier 2021 (100 and 200 keV, PARCAS, 0 K thermostat, 10 eV stopping cutoff
with SRIM tables; too high in energy for our boxes, and very few cascades)
Cascades: JW 5 and 5, M-S 5 and 5, DND-BN 20 and 9 (at 100 and 200 keV). Table 3 clusters found:
JW 41/83, M-S 59/93, DND-BN 170/128. In-cluster defect fraction rises with energy for all three.
Their statements: JW prefers parallel (dislocation-loop) clusters; DND-BN additionally makes very
large multi-component loops; M-S makes the most ring (C15-like) clusters, mostly small. They note
M-S predicts a melting point far above experiment (citing Sand 2016; the value is not given in
what I read). The sample is tiny, so treat these as qualitative.

### 5.3 Bjorkas, Nordlund, Dudarev 2009 (DND-BN's own paper)
- TDE (Table III, 4 K for W, eV): modified potential, minimum over 1096 directions 41 +- 1;
  <100> 41 +- 1, <110> 93 +- 1, <111> 41 +- 1; average threshold 84.5 +- 0.9. Unmodified: 55, 55,
  >100, 93, average 88.3 +- 0.7. Experiment as printed: 42 +- 1 (<7 K), 40 +- 2, 44 +- 1, 42 +- 1
  (4 K), 50 +- 2 (350 K).
- Cascades (0.5-20 keV, no electronic stopping, N_FP from Fig. 4, figure-only): W gives clearly fewer
  Frenkel pairs than Fe and V; by eye about 7 at 5 keV and about 8 at 10 keV (the paper's Fig. 5
  labels a 10 keV W peak of 320 +- 20 pairs at 0.75 ps). NRT efficiency uses E_d(W) = 85.4 eV. W
  interstitial clustered fraction rises from about 9% at 0.5 keV to about 72% at 20 keV (text).
  Temperature and run length of those cascades were not found in what I read. Not directly
  comparable with a 300 K run with stopping.

### 5.4 TDEs for M-S (De Backer 2016, Table 1, MD from 36 K, 7000 runs, plus DFT-MD)
| Orientation | DFT (minimal valence) | DFT with semi-core | MS-s | MS-h |
|---|---|---|---|---|
| <100> | 40 | 58 | 31 | 43 |
| <110> | 63 | >80 | 51 | 71 |
| <111> | 44 | >80 | 45 | 65 |
The paper links higher TDE to a harder pair interaction between 1 and 1.5 Å. Cascades there: full MD
for 1-100 keV with MS-s and MS-h (not read in detail); the softer potential leaves more vacant sites at
the peak and more surviving defects.
Roy et al. (secondary) give ranges across the five W potentials of Sand 2016: <100> 31-63, <110>
51-103, <111> 41-89 eV (their "experiment": 40, 70, 44; this differs from the experimental list in
Bjorkas Table III).

### 5.5 tabGAP at our energies (Byggmästar et al. 2025, supplement Table S3 as relayed)
5 keV: damage energy 4.12 keV, N_FP = 4.59 (std 1.97, stderr 0.20, 100 runs). 10 keV: damage energy
8.06 keV, N_FP = 7.59 (std 2.93, stderr 0.29, 100 runs). 300 K, 10 eV friction cutoff with SRIM,
Nose-Hoover border thermostat, 50 ps, adaptive timestep. TDE minimum 42, average 95 eV. The page did
not state the tabGAP version or short-range treatment.

## 6. Other cascade-tested W potentials (brief)

- tabGAP (Mo-Nb-Ta-V-W). Code and some potential files in the repository's `potentials` folder (the
  README does not say which elements), run with a standalone LAMMPS pair style that must be compiled
  (build instructions in the repo's `lammps/` folder). The project page lists GPL v3 or later; the
  README states no licence for the potential files. Citation request: Byggmästar et al., PRM 6,
  083801 (2022) and PRB 104, 104101 (2021). Short-range treatment not stated in the pages I read
  (an earlier session recorded screened Coulomb repulsion from the 2022 paper). Disagreement:
  Warrier and Bhardwaj cite PRB 104, 104101 (2021) for the tabGAP they ran, while the 2025 paper
  cites the 2022 PRM paper (and its reference list is mislabeled per the fetch). Which file was used
  for the 5/10 keV numbers is TODO-LIT. Project impact: the volunteer LAMMPS is a stock build;
  tabGAP needs a custom pair style in the build recipe, a design decision for the main agent.
- WSNAP (Wood and Thompson SNAP): in the five-potential comparison it is fitted to ZBL and needs no
  stiffening (Warrier Table 2); it gives the most defects above 20 keV and about 15% 1/2<111>
  clusters. Primary paper not reopened this session (arXiv:1702.07042; see `w_potentials.md` B3).
- GAP W (Byggmästar 2019, arXiv:1908.07330), NEP-ZBL (Liu 2023, arXiv:2305.08140), Goryaeva 2021: only
  covered by the earlier file `w_potentials.md`; I did not reopen them. I could not extract the GAP
  PDF text this session.
- Mason, Nguyen-Manh, Becquart 2017 (MNB), EAM `eam/fs` file `W_MNB_JPCM17.eam.fs` on NIST
  (NIST list). The abstract (opened) says interstitial and short-range pair behaviour stay close
  to Ackland-Thetford and calls it "well suited" to post-cascade microstructure evolution. A fetch
  summary of a different paper (arXiv:2205.09165, ar5iv page opened) described a Mason 2017 variant
  labelled "EAM+ZBL" that adds universal ZBL to Ackland-Thetford; this contradicts the earlier
  note that no ZBL is present, so check Mason 2017 before using it. No cascade benchmark found.
- ACE/MTP for W cascades: none found in this session.

## 7. Disagreements and cautions

1. DND-BN r2: 2.25 Å in Warrier Table 2 and in the first print of Bjorkas, 2.10004 Å in the erratum,
   with different polynomial coefficients. My hand check supports the erratum.
2. DND-BN TDE: Bjorkas average 84.5 eV, <110> 93 eV, min 41 eV versus Warrier Table 3 mean 100.57,
   max 163, min 42.30 eV. Different directions sampled, temperature, and possibly different files.
3. DND-BN lattice properties: Warrier a = 3.17 Å, B = 315.29 GPa versus Derlet a0 = 3.1652 Å, B = 310.4 GPa.
4. JW lattice constant: Warrier Table 3 gives 3.160 Å; the project's rebuilt JW gives 3.1652 Å (0 K)
   and 3.1674 Å (300 K), and Setyawan quotes 3.167 Å at 300 K. Different measurement or file;
   matters if Campaign 2 compares our JW with theirs.
5. MS naming: "MS_h" with r1/r2 = 1.3/2.0 (Warrier) versus text mentioning "MS_x" with S = -552; the
   review says M-S_s has S = -552. Not resolved without Sand 2016.
6. tabGAP citation (2021 vs 2022 paper), see section 6.
7. Warrier and Bhardwaj internal inconsistency: their conclusion says DND-BN "shows strong agreement"
   with experiment for the <110>-<111> dumbbell energy difference, but their Table 3 gives 0.44 eV
   against 0.30 eV experiment (-51.72%, marked bold), the worst of the three EAMs; JW is 0.24 and
   MS 0.29. They also report negative thermal expansion for DND-BN (-0.97e-6 per K) and large
   elastic deviations. Do not quote their wording on DND-BN without checking.

## 8. Gaps and TODO-LIT

- TODO-LIT: Sand et al. 2016 full text (M-S construction, base variant, ZBL, shift, joins, melting
  point, TDE and defect tables per potential, any file).
- TODO-LIT: DND-BN ready-made file or confirmation of which r2/coefficients Bhardwaj/Warrier used.
- TODO-LIT: soft version join radii (0.6/1.2 Å unconfirmed).
- TODO-DIGITIZE: Warrier and Bhardwaj Fig. 2 (defect counts) and Fig. 3 (clustered fraction) at 5 and
  10 keV for JW, MS, DND-BN, tabGAP; also confirm the "TDE 100" meaning.
- TODO-LIT: licence terms for NIST/OpenKIM W files and for any generated DND-BN or M-S file.
- TODO-LIT: tabGAP W potential file, version, licence, LAMMPS build effort.
- Code check needed (not done; I had no code execution here): scripted verification of the DND-BN
  splice (value, slope, curvature continuity; a0, B, formation energies; TDE).

## 9. Suggested next searches

1. Library or author request for Sand et al. 2016 (J. Nucl. Mater. 470, 119) and its supplementary
   data; ask A. E. Sand and K. Nordlund (Helsinki) for the stiffened Marinica files.
2. Becquart et al., J. Nucl. Mater. 547, 152816 (2021) and De Backer et al., J. Nucl. Mater. 549,
   152887 (2021): they use the same W potentials and may restate the stiffening parameters.
3. Bjorkas thesis (Helsinki) or Bjorkas and Nordlund NIMB 259, 853 (2007) (Fe splice method) for the
   exact ZBL and polynomial conditions.
4. Open the OpenKIM archive for MO_195478838873 to see whether the DND parameter files are plain
   knot tables; compare with Table IV.
5. tabGAP repository `potentials` folder, licence file, W-only tabGAP; Byggmästar 2019 GAP W data
   availability (gitlab.com/acclab/gap-data per the earlier file).
6. Mason et al. 2017 full text: confirm or refute the "EAM+ZBL" description.

## 10. Where to get the Sand et al. M-S files

Added 2026-11-03. Status UNVERIFIED like the rest of this file. Provenance tags as in the header.
Result in one line: I found no public location that contains the M-S (MS_h or MS_s) files or the
polynomial coefficients. Only the construction outline (base potential, join radii) is public, in
secondary papers. The route to the files is to ask the authors (10.5).

### 10.1 Correction to the request's premises (check these)
- The 2016 paper (J. Nucl. Mater. 470, 119) has five authors: A. E. Sand, J. Dequeker, C. S. Becquart,
  C. Domain, K. Nordlund. There is no Dudarev. Seen in the reference lists of Bhardwaj 2021 (ref. 24) and
  Warrier 2025 (ref. 6) [PAGE-IMAGE], and in the OpenAlex and Crossref records [HTML/SUMMARY]. Dudarev is
  on the 2013 EPL paper (Sand, Dudarev, Nordlund), which is a different paper.
- The EPL 2013 paper did not introduce the stiffened Marinica potential. I read arXiv:1306.3824v1
  (17 Jun 2013) [TEXT-LAYER + PAGE-IMAGE]: its potentials are a modified Derlet potential (D-D), the
  Ackland-Thetford EAM (A-T) and a Tersoff-type potential (A-H), each joined to universal ZBL. No
  Marinica potential. Caveat: I read the arXiv v1 only, not the published EPL version, and did not check
  whether the published version added anything.
- Sand's later overlapping-cascade paper (Sand, Byggmästar, Zitting, Nordlund, EUROfusion preprint
  WPMAT-PR(18)19992, "preprint submitted to Elsevier", March 2018) used the Derlet W potential joined to ZBL,
  not M-S [PAGE-IMAGE, methods page]. So the stiffening was first published in the 2016 JNM paper, as far
  as I can tell.

### 10.2 What is publicly stated about the construction (secondary sources, opened)
| Item | Statement | Where |
|---|---|---|
| Base potential | EAM4 of Marinica et al. 2013 | Warrier and Bhardwaj, arXiv:2402.00359v1, section 2.4, p. 5 [PAGE-IMAGE]. I could not find this sentence in v2, whose text only says "Marinica et al.'s tungsten EAM potential" (v2 pp. 2-3). |
| Soft version (MS_s) | pair term of EAM4 interpolated to ZBL between r1 = 0.6 and r2 = 1.2 Å | same, v1 p. 5 |
| Hard version (MS_h) | interpolation between r1 = 1.3 and r2 = 2.0 Å | same, v1 p. 5; and Table 2 in v1 and v2 |
| Which version was run | MS_h ("MS (specifically the MS_h potential)") | Warrier and Bhardwaj v1 and v2, section 2.1 |
| Stiffness numbers | MS_h: R = 1.45 Å, S = -137, S/R = -95 /Å (Table 2); MS_s: S = -552, R quoted as -502 (v2 p. 7; my reading is that this is S/R) | v2 pp. 4, 7 |
| TDE (eV, <100>/<110>/<111>) | MS-s 31/51/45; MS-h 43/71/65 | De Backer 2016 Table 1 [PAGE-IMAGE]; Warrier v1 p. 5 gives 31/51/45 and calls it "the MS potential", which matches the soft one |
| Fig. 1 of Warrier (v2) | its caption says "total potential energy of a pair of atoms" | v2 p. 11 [PAGE-IMAGE]. This supports my guess in 4.2 that R and S refer to the total two-atom energy, not the bare pair term. |

Not public in anything I opened: the polynomial constraints and coefficients, the ZBL form and any shift,
whether the embedding F(rho) and density rho(r) tables were touched, and the file names.
A search summary and the Roy review (secondary, see 4.2) say "fifth-degree polynomial"; I did not open a
primary statement of it.

### 10.3 Candidate locations checked, and what each contains
| # | Location | Contains the M-S file or parameters? | Notes |
|---|---|---|---|
| 1 | Sand et al. 2016 on the publisher site, DOI 10.1016/j.jnucmat.2015.12.012 (https://doi.org/10.1016/j.jnucmat.2015.12.012) | Unknown. I could not open the article, so I cannot say whether a supplementary file exists. | OpenAlex (record W2197455486) says is_oa false, no open full text anywhere. Crossref lists only an Elsevier text-mining licence, no open licence [HTML/SUMMARY]. |
| 2 | HAL, https://edf.hal.science/hal-01828022 | Unknown | The page returned a bot-protection "Access Denied" page. OpenAlex lists it as a submitted version with no PDF URL, so it may be metadata only. I did not try to get around the block. |
| 3 | Sand's CCN5 slides (IAEA, 2017), https://amdis.iaea.org/media/presentations/CCN5-20171116-Sand.pdf | Unknown | HTTP 402, not opened. Search snippets say the slides describe "hard" and "soft" stiffened Marinica variants and compare TDE and defect counts. [LEAD, NOT OPENED] |
| 4 | NIST IPR, W system list, https://www.ctcms.nist.gov/potentials/system/W/ | No. | I read about 200,000 of 201,545 characters through a summarising tool. Marinica entries are W-2, W-3, W-4 only (files `w_eam2.fs`, `w_eam3.fs`, `w_eam4.fs`, sent by M.-C. Marinica on 9 Jan 2017). No entry by Sand, Nordlund, Domain or Dequeker, and none described as stiffened or ZBL-modified Marinica. Becquart appears only on the Mason 2017 entry. [HTML/SUMMARY] |
| 5 | OpenKIM EAM4 page, https://openkim.org/id/MO_046576227003_000 | No. | Plain EAM4 (Finnis-Sinclair, `EAM_Dynamo` driver), no files named, no licence stated, no ZBL or stiffened variant mentioned, a newer version _001 is noted. A web search for a KIM model of stiffened or hardened Marinica W returned nothing relevant. [HTML/SUMMARY] |
| 6 | Zenodo (two keyword queries through its API) | No hit. | Not a complete search: I read only the first ~100,000 characters of each result. The only potential-like W record was the tabGAP W-B record (Bergero, Byggmästar, Granberg, DOI 10.5281/zenodo.21898767), unrelated to M-S. |
| 7 | Figshare, IDA, Fairdata, HELDA | Not searched with their own search tools | Only general web searches, which found nothing. |
| 8 | GitLab, Byggmästar profile and https://gitlab.com/jezper/tabgap | No. | Profile page shows no project list. The tabGAP page shows a README and a GPL v3-or-later LICENSE and no Marinica or MS files. I did not browse its folders. [HTML/SUMMARY] |
| 9 | Nordlund group publication list, old page https://www.mv.helsinki.fi/home/knordlun/pub/ | No preprint of Sand 2016 listed | The page says it is no longer maintained and points to a newer list whose host (beam.helsinki.fi) did not resolve from here. A guessed preprint filename gave 404. |
| 10 | Theses (HELDA, Aalto) | Not found | I found no thesis by A. E. Sand that treats this. Not proven that none exists. |
| 11 | Bhardwaj, Sand, Warrier 2021, arXiv:2009.14540 and published MSMSE 29, 065015 | No file. | No data availability statement in the pages I read. The arXiv page comments (via summarising tool) say results are in a web app linked to a GitHub user "csaransh". github.com/csaransh gave HTTP 404, so I could not check it, and it holds analysis results rather than potentials as far as I can tell. |
| 12 | Warrier and Bhardwaj 2025, arXiv:2402.00359 (v1 and v2) | No file. | v2 acknowledgements thank only the HPC team. No statement of where the MS_h file came from (I did not read the v1 acknowledgements). |
| 13 | Bhardwaj, Sand, Warrier, arXiv:2201.13022 (stability of <100> dislocations) | Not determined | Abstract says three potentials; I read pages 1-4 only and did not reach the potentials section. |
| 14 | Becquart, De Backer, Olsson, Domain, J. Nucl. Mater. 547, 152816 (2021) and De Backer et al., J. Nucl. Mater. 549, 152887 (2021) | Not opened | Both analyse stiffening of seven W potentials (per Warrier's introduction). OpenAlex says Part 1 has an accepted manuscript on ScienceDirect (`.../article/am/pii/S0022311521000398`, HTTP 403 for me) and a HAL record hal-03159140; Part 2 has HAL record hal-03159136 with a PDF link (`https://hal.science/hal-03159136/document`, blocked by the bot check). Best remaining open-access lead for the stiffening details. I do not know that they use the Sand M-S files. |

Other papers that I opened and that do not use or distribute M-S: Warrier and Bhardwaj arXiv:2405.03344
(DND-BN and SNAP), Zhang et al. RSC Adv. 2022 (PMC9380701; two modified EAM potentials), Wu et al.
arXiv:2409.15856 (Mason EAM; first 100,000 characters), Dominguez-Gutierrez et al. 2020 (GAP; first two
pages), De Backer et al. preprint UKAEA-CCFE-PR(20)74 (Fe, Ackland potential plus ZBL), Byggmästar,
Granberg, Nordlund 2018 preprint (Fe; title page and abstract only). A 2026 Acta Physica Sinica page
(Xu et al., DOI 10.7498/aps.75.20260698) tests ZBL, Moliere and Kr-C joins on A-T and Mason potentials, with no
Marinica potential and no files [HTML/SUMMARY].

### 10.4 Disagreements and cautions specific to M-S
1. "Soft" and "hard" are used the opposite way from hard-sphere usage. Warrier v1 (footnote on p. 5) says
   that in Sand 2016 the word soft means the higher gradient and hard the lower gradient. Check that
   against Sand 2016 before labelling files. In numbers: MS_s joins ZBL at 0.6-1.2 Å with S = -552, MS_h at
   1.3-2.0 Å with S about -137 to -140, and MS_h gives the higher TDEs (De Backer).
2. S and R for MS_h: Warrier gives S = -137, R = 1.45 Å; the Roy review gives S = -140.5 eV/Å, R = 1.5 Å
   (section 4.2). About 3% apart in both. Probably different definitions or rounding. Unresolved.
3. Variant evidence: EAM4 is now stated in a paper I opened (Warrier v1), but that is still secondary, and
   v2 of the same paper no longer says it. The primary statement is in Sand 2016.
4. Warrier v1 p. 5 attributes TDE 31/51/45 to "the MS potential" while the MS potential they ran is MS_h
   (Table 3 TDE min 43.00 eV, consistent with De Backer MS-h <100> = 43). The 31/51/45 values belong to
   MS-s. Do not use the v1 sentence as the TDE of the file they ran.
5. "Marinica potential" could mean any of EAM2, EAM3 or EAM4 in some papers. De Backer 2016 says only
   "one of Marinica et al. potentials". Only Warrier v1 names EAM4.

### 10.5 If nothing public: who to ask (addresses printed in documents I opened; nothing guessed)
- A. E. Sand is first author of the 2016 paper. OpenAlex marks her as the corresponding author
  [metadata; Crossref does not flag a corresponding author, so this is not confirmed from the paper].
  Affiliations: Department of Applied Physics, Aalto University, and Department of Physics, University of
  Helsinki (both listed on the 2021 paper). The Aalto profile page lists andrea.sand@aalto.fi
  (https://www.aalto.fi/fi/ihmiset/andrea-sand) [HTML/SUMMARY, so confirm on the page]. The 2018 preprint
  printed andrea.meinander@helsinki.fi as the corresponding-author address for A. E. Sand (old; may be dead).
- K. Nordlund (University of Helsinki, Department of Physics): last author of the 2016 paper and author of
  the PARCAS code used by the group. I did not retrieve a contact address.
- Co-authors from the French side: C. S. Becquart (Univ. Lille, UMET), C. Domain (EDF R&D, MMC),
  J. Dequeker (Lille, 2016). Becquart, De Backer, Olsson and Domain wrote the 2021 stiffening studies
  (10.3, row 14).
- A. De Backer (CCFE, now UKAEA) ran MD with the soft and hard versions in 2016; the 2016 paper printed
  andree.debacker@ccfe.ac.uk, likely stale.
- M. Warrier and U. Bhardwaj (BARC, Visakhapatnam and Mumbai) ran MS_h in LAMMPS in 2025, so they hold a
  LAMMPS-usable file. Addresses printed on arXiv v1: manoj.warrier@gmail.com and haptork@gmail.com. A. E.
  Sand is a co-author of their 2021 paper.
- M.-C. Marinica (CEA) supplied the base EAM files to NIST. He is the right person for base-file and
  licence questions, not for the stiffening.
Suggested request for the human to send: ask for (a) the MS_h and MS_s LAMMPS files, (b) the polynomial
constraints and ZBL form used, (c) permission to use them in a public BOINC project and in a published
dataset, (d) the preferred citation. The licence is the likely sticking point: NIST and OpenKIM state none
for the base file.

### 10.6 What this changes in earlier sections
- 4.1: the variant is probably EAM4 (Warrier v1, secondary). Still TODO-LIT for a primary source.
- 4.2: r1/r2 for the soft version (0.6/1.2 Å) now come from an opened paper (Warrier v1 p. 5), not only a
  search snippet. Still secondary.
- 8: "TODO-LIT: soft version join radii" can be downgraded to "confirm in Sand 2016". The M-S file itself
  remains missing. A provisional rebuild from EAM4 + ZBL with a quintic is not M-S (see 4.2).

### 10.7 Sources opened for this section
Opened: arXiv:1306.3824v1; arXiv:2402.00359 v1 and v2; arXiv:2009.14540 (pages 1-6, 13-14, 19-21) and its abs
page; arXiv:2201.13022 (pages 1-4); De Backer et al. 2016 UKAEA preprint CCFE-PR1621 (pages 1-3);
WPMAT-PR(18)19992 (pages 3-7); UKAEA-CCFE-PR(20)74 (pages 1-8); WPMAT-PR(18)20456 (title page, abstract);
NIST W list; OpenKIM EAM4; OpenAlex and Crossref records for Sand 2016; OpenAlex list of 84 works citing
Sand 2016 (titles only); Aalto profile; Zenodo API (two queries); gitlab.com/jezper and /jezper/tabgap;
Dominguez-Gutierrez 2020 (pages 1-2); arXiv:2405.03344, PMC9380701, arXiv:2409.15856, Acta Phys. Sin.
landing page (summaries).
Not opened (blocked or paywalled): Sand 2016 publisher page, HAL records, IAEA CCN5 slides (HTTP 402), IAEA
cascades database reference page (HTTP 402), Becquart 2021 Parts 1 and 2 full text, Roy 2025 npj review
(redirected to a login handshake this time, which I did not follow).
