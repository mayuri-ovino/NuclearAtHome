Status: UNVERIFIED

# 11. DND thermal expansion check (to be appended to `potentials_W_campaign2.md`)

Prepared 2026-11-03. This text is written so it can be pasted under the heading "11. DND thermal
expansion check" in `docs/literature/potentials_W_campaign2.md`. I had no Edit tool in this session, so
I did not touch that file; this is a separate file. Nothing here is approved. The human verifies every
source and number. Provenance tags as in that file: [PAGE-IMAGE] = I looked at a rendered page image,
[HTML/SUMMARY] = a web page passed through a summarising fetch tool, [LEAD, NOT OPENED] = seen only in a
search result, do not cite. I could not run code, so every number from our own build is the one the
request gave me.

## 11.1 Result in one paragraph

Negative thermal expansion of the DND tungsten potential is reported in the literature, by an
independent group, in a figure that shows the same shape and roughly the same size as what our build
gives. The original paper fitted only the zero-temperature quasi-harmonic expansion coefficient (positive
for W), not the finite-temperature anharmonic behaviour. A second paper reports a negative coefficient for
DND-BN. The published Table IV for W agrees with `make_dndbn.py` in all 16 numbers as I read them.
So the evidence points to a real property of the potential, not a transcription error. It is not a proof:
I found no source that states the DND lattice constants at 300, 600 and 1025 K, and our build has not been
checked against the one quantity Derlet did fit (11.5).

## 11.2 Sources opened

1. J. Wang, Y. Zhou, M. Li, Q. Hou, "A modified W-W interatomic potential based on ab initio
   calculations", Modelling Simul. Mater. Sci. Eng. 22, 015004 (2014); arXiv:1306.4738 (v2, 23 Jul 2013);
   DOI 10.1088/0965-0393/22/1/015004 (DOI from the arXiv page). https://arxiv.org/abs/1306.4738 .
   [PAGE-IMAGE] pages 1-27 of the arXiv PDF (text, Table 1, Fig. 2).
2. P. M. Derlet, D. Nguyen-Manh, S. L. Dudarev, Phys. Rev. B 76, 054107 (2007), DOI
   10.1103/PhysRevB.76.054107. Published version (PDF hosted by UKAEA, "Published" folder):
   https://scientific-publications.ukaea.uk/wp-content/uploads/Published/PRBVOL76p054107.pdf .
   [PAGE-IMAGE] pages 1-2, 9-11 (Eqs. 6-10 start, Table II) and 19-22 (Table IV, appendix text).
   Also the UKAEA preprint FUS 544 already used in section 3.5: pages 18-27 and 36 (Eqs. 6-10, Table II,
   Table IV), https://scientific-publications.ukaea.uk/wp-content/uploads/UKAEA-FUS-544FINAL.pdf .
3. M. Warrier, U. Bhardwaj, arXiv:2402.00359 (v2), https://arxiv.org/abs/2402.00359 . [PAGE-IMAGE] pages
   3-8, Table 3 re-read (already source 2 of the main file).
4. U. Bhardwaj, M. Warrier, "Molecular dynamics simulations of the defect evolution in tungsten on
   successive collision cascades", arXiv:2405.03344 (v2), https://arxiv.org/html/2405.03344v2 .
   [HTML/SUMMARY] only.
5. OpenKIM model page MO_195478838873_002, https://openkim.org/id/MO_195478838873_002 , DOI
   10.25950/45d538ba, and its driver page
   https://openkim.org/id/EAM_MagneticCubic__MD_620624592962_002 . [HTML/SUMMARY]
6. NIST IPR entry for Derlet 2007 W,
   https://www.ctcms.nist.gov/potentials/entry/2007--Derlet-P-M-Nguyen-Manh-D-Dudarev-S-L--W .
   [HTML/SUMMARY]
7. M.-C. Marinica et al., J. Phys.: Condens. Matter 25, 395502 (2013), DOI 10.1088/0953-8984/25/39/395502,
   UKAEA copy https://scientific-publications.ukaea.uk/wp-content/uploads/Published/JnlPhyCondVOL25p395502.pdf .
   [PAGE-IMAGE] pages 1-3 only (abstract, introduction, start of the potential section).
8. S. Chiesa, P. M. Derlet, S. L. Dudarev, H. Van Swygenhoven, "Optimization of the magnetic potential for
   alpha-Fe", J. Phys.: Condens. Matter 23, 206001 (2011), DOI 10.1088/0953-8984/23/20/206001. Seen only
   through the NIST entry page
   https://www.ctcms.nist.gov/potentials/testing/entry/2011--Chiesa-S-Derlet-P-M-Dudarev-S-L-Swygenhoven-H-V--Fe-33
   [HTML/SUMMARY]. Iron, not tungsten; included because it is the same group fixing the same issue.
9. R. C. Ehemann et al., arXiv:1702.04660 (MEAM W at high pressure), pages 1-3 [PAGE-IMAGE]. Its Fig. 1c
   shows good thermal expansion for its own potential. It does not discuss DND, so it is not evidence
   about DND. Listed only so nobody opens it expecting more.

## 11.3 Evidence on question 1 (thermal expansion or Gruneisen behaviour of DND / DND-BN)

### 11.3.1 Wang et al. 2014: DND expands negatively in MD
- Intro (p. 3): DND "predicts negative thermal expansion when the temperature is above approximately
  300 K", in conflict with experiment. The abstract and conclusions repeat that the new potential
  overcomes the negative thermal expansion of the Derlet-Nguyen-Manh-Dudarev potential. [PAGE-IMAGE]
- Method (pp. 5-6): linear expansion beta(T) = [L(T) - L0]/L0 with reference 293.15 K; a sample of 2000 W
  atoms relaxed by MD at temperatures from 0 to 3500 K, with an electron-phonon coupling model acting as
  a thermostat; "for each temperature, the system volume was adjusted to maintain a pressure of
  approximately 0 kbar". Potentials compared: AT (Ackland-Thetford), DND, and their own.
  They do not say which file or parameters they used for DND (they cite Derlet 2007).
- Fig. 2 (arXiv PDF p. 24), my eyeball reading of the DND markers, uncertain by perhaps +-30 %: close to
  zero up to about 300 K, then falling to a minimum of about -4e3 to -4.5e3 (units of the y axis not
  printed; I infer parts per million, because the experimental curve reaches about 2.1e4 at 3500 K, about
  2 % linear expansion) near 1500-1800 K, then rising and crossing zero near 2700-2900 K, ending near
  +5e3 at 3500 K. At about 1000 K I read roughly -3e3 to -3.5e3. AT gives a strong positive expansion
  and their own potential follows experiment.
- Our numbers for comparison (from the request; strain relative to our 300 K value 3.1651 A):
  600 K: -0.0046 A, about -1.45e-3 (-1450 ppm). 1025 K: -0.0105 A, about -3.3e-3 (-3300 ppm). JW in the
  same script: 600 K +1.6e-3, 1025 K +5.2e-3. The DND shape (flat to about 300 K, then falling) and the
  size at about 1000 K agree with my reading of Fig. 2 to within what I can read. This needs a proper
  digitisation (TODO-DIGITIZE) before anyone treats it as quantitative agreement.
- Same paper (Table 1 and p. 7): DND a = 0.3165 nm, B = 310 GPa, C11/C12/C44 = 525/203/159 GPa; melting
  point of DND quoted as about 3750 K from Fikar and Schaublin (J. Nucl. Mater. 386-388, 97, 2009; not
  opened), the paper says DND "can closely predict the melting point". Wang's own potential: 4100 +- 50 K
  against experiment 3695 K.
- Limitation: a single group, one figure, no numbers in text, and the sample is small (2000 atoms).

### 11.3.2 Warrier and Bhardwaj 2025: DND-BN alpha is negative
- Table 3 of arXiv:2402.00359v2 [PAGE-IMAGE, re-read for this section]: thermal expansion coefficient
  alpha in 1e-6 per K: DFT 4.9, experiment 4.5, JW 8.74, MS 5.19, DND-BN -0.97 (error -119.83 %, bold),
  WSNAP 7.14, tabGAP 6.79. Lattice parameter a: JW 3.160, MS 3.160, DND-BN 3.17, WSNAP 3.18, tabGAP 3.18 A.
- Conclusions (p. 8): DND-BN "displays limitations including negative thermal expansion and substantial
  deviations in elastic properties".
- What is not stated: the temperature or temperature range of the alpha and a values, the ensemble, the
  cell size, whether alpha is a mean over a range or a derivative. The only stated protocol (p. 3) is
  NPT at 300 K and 0 bar for 10 ps before each cascade. So their "3.17" is probably just 3.1652
  rounded to two decimals (my guess, not a statement in the paper), which would mean no temperature
  at all, and that is the answer to the "at what temperature" question: not stated.
- Disagreement: their alpha = -0.97e-6 per K is about five times smaller in magnitude than the mean slope of
  our numbers (-4.6e-6 per K from 300 to 1025 K, computed from the request's values). Different
  temperature window is the obvious cause, since Wang's curve is nearly flat below 300 K. Unresolved.
- Their JW alpha 8.74e-6 per K is a little above our JW mean slope of about 7.1e-6 per K from 300 to
  1025 K (computed from the request's values); consistent given the unknown window.
- arXiv:2405.03344v2 (same group, DND-BN vs SNAP, cascades at 20 and 50 keV, relaxation by NPT at 300 K
  and 0 bar for 10 ps): the summary says DND-BN gives low swelling and shows no lattice-vs-temperature
  data [HTML/SUMMARY]. A search snippet of an IAEA poster by Warrier says DND-BN is bad for "swelling
  studies (thermal expansion and elastic constants)" [LEAD, NOT OPENED; HTTP 403].

### 11.3.3 Derlet 2007 itself: what was fitted
- Eq. 6-10 (published p. 9 and 11; preprint pp. 13-14): the potentials were also fitted to the
  "zero temperature isotropic thermal expansion coefficient" beta = (1/B)(dP/dT)_V, evaluated in the
  quasiharmonic classical limit as beta = (k_B/(B V)) sum of Gruneisen parameters gamma_i (Eq. 10).
  The paper says including it brings in derivatives higher than second order, which it calls a first step
  toward including anharmonic information.
- Table II (published p. 11 and preprint p. 16), row beta (1e-4): V 0.252 (1.28), Nb 0.219 (0.57), Ta 0.189
  (0.107), Mo 0.144 (0.154), W 0.135 (0.120), with the fitted value in brackets. Units are not printed in
  what I read. My inference: units of 1/K and a volume coefficient, since 0.135e-4 = 3 x 4.5e-6, the
  experimental linear coefficient of W that Warrier's Table 3 lists as 4.5e-6.
- So the fitted W value, 0.120e-4 per K (about 4.0e-6 per K linear), is positive, about 11 % below the
  target, in the classical T -> 0 limit. Nothing in the paper tests finite-temperature MD lattice
  expansion. The fit was weak for V and Nb (factors of 5 and 2.6), so the fit of this quantity was not
  tight in general. The weighting was lowest after the interstitial and vacancy energies (preprint p. 15).
- Consequence for us: the potential is designed to have positive expansion at low T. Negative expansion at
  300 K and above would then have to come from anharmonic terms, as Wang's statement "above approximately
  300 K" implies. That is compatible with a(300 K) of our build being 0.0001 A below a(0 K).

### 11.3.4 OpenKIM and NIST
- OpenKIM MO_195478838873_002: the page lists only 0 K visualizers (BCC lattice constant, cohesive
  energy, elastic constants, dislocation core energies at 0 K and zero pressure, and others for other
  lattices). No thermal expansion or lattice-vs-temperature test is listed. [HTML/SUMMARY] The verification
  checks are mostly P; the dimer C1 continuity check is F (informational) and states the model is only C0
  continuous (already noted in section 3.2).
- NIST IPR entry: no files, no thermal expansion; it says the new computed properties (dynamic relaxes of
  crystal and liquid, melting temperatures) are on the OpenKIM-model results page
  `.../MO_195478838873.html`, which returned an empty page to my fetch tool. So I do not know whether it
  contains a melting temperature or a dynamic-relax lattice parameter. TODO-LIT: open that page in a
  browser.
- OpenKIM and NIST both say the parameter files are inside the `EAM_MagneticCubic` driver archive, which I
  could not download or unpack with my tools (the files listing needs the live site).

### 11.3.5 Other papers asked about
- Marinica et al. 2013 (pages 1-3 only): introduction says Derlet et al. derived new parametrisations and
  used them for crowdion migration, with deficiencies such as a degenerate screw core. No thermal-expansion
  statement in the pages I read. Their own form uses the same cubic knots but F(x) = a1 sqrt(x) + a2 x^2
  (Eq. 4); DND has only the square root. I did not read the rest of the paper.
- Not found or not opened: Bjorkas 2009 does not mention thermal expansion in anything I read in the
  earlier session; Mason 2017 (title page and abstract only), Byggmastar 2019 GAP, Chen 2018, Bonny,
  Setyawan: no DND thermal expansion statement found. A search snippet claimed a Setyawan-type comparison
  exists, but I could not find it.

## 11.4 Question 2: is this a known property of DND-type potentials?

- For W DND: yes, in two independent places (Wang 2014, Warrier and Bhardwaj 2025 for DND-BN). Wang
  names it as the reason for building a different potential.
- For other bcc metals with the same cubic-knot, minus-square-root form (V, Nb, Ta, Mo from Derlet Tables
  III-IV): I found no source that reports finite-temperature thermal expansion. Derlet Table II shows that
  only the T -> 0 coefficient was fitted and was poorly matched for V and Nb.
- For related potentials by the same group: Chiesa et al. 2011 (Fe, NIST entry only) report that adding
  third-order elastic constants to the fit, which "govern thermal expansion", gives positive thermal
  expansion for all three of their new parameterisations. That suggests the group knew expansion was a risk
  for this family, but the text I saw does not say what happened with the earlier DND W potential.
  [HTML/SUMMARY]
- I found no paper that explains the mechanism for DND W (for example whether the minus-square-root
  embedding is the cause).

## 11.5 Question 3: independent copy of Table IV, and a digit comparison

I found no distributed parameter file (NIST: none; OpenKIM: archive not readable by my tools). I did find
a second, independent rendering: the published PRB page (054107-20), separate from the UKAEA preprint
used in section 3.5.

Published Table IV, tungsten, as I read it from the page image, compared with `make_dndbn.py`
(A, F_KNOTS, V_KNOTS). All of these agree with the script, digit for digit as far as I can read:
- A = 10.84238200368439.
- f knots (r, f_n): (3.3216, 1.677334871575606), (3.165333333333333, -1.673137509507131),
  (3.009066666666667, -4.737051994974169), (2.8528, 7.870789420780674),
  (2.7411, -3.7924230525563378e-4), (2.604045, 6.190816158916646), (2.46699, -0.9565713891199151).
- V knots (r, V_n): (4.2689, -0.1036435865158945), (3.98568, -0.2912948318493851),
  (3.70246, -2.096765499656263), (3.41924, 19.16045452701010), (3.13602, -41.01619862085917),
  (2.8528, 46.05205617244703), (2.7411, 26.42203930654883), (2.604045, 15.35211507804088),
  (2.46699, 14.12806259323987).
- The sign of the tiny f_n at 2.7411 (uncertain in section 3.5): in the published page it is printed as a
  minus with exponent 10^-4, and in the preprint also. So it is negative, as in the script. This resolves
  that uncertainty.
- The preprint (FUS 544, page 30) agrees with the published page on every value I compared.
Caveats: both are page images at modest resolution, so I can distinguish the printed numbers but a single
swapped digit deep inside a 16-digit string is possible for me to miss. The published appendix says all
printed digits should be used. This check does not show that Derlet's own printed table is right; both
versions come from the same authors.

Other facts read in the same PDFs: the published page states these potentials are "currently unsuitable"
for high-energy collision dynamics (appendix text). Derlet states the first four V knots and A were solved
exactly to reproduce a0, E_c and the elastic constants (preprint p. 14: "outermost four knot
coefficients of the repulsive potential"), so a build that reproduces a0, B, C' and C44 tests A and the
four outer V knots, not the inner ones.

## 11.6 Disagreements

1. Wang: negative expansion for DND above about 300 K (a figure, with a curve minimum near -4e3 ppm);
   Warrier: alpha = -0.97e-6 per K for DND-BN, without a stated window. Magnitudes differ by about 5 x
   against our own mean slope. Unresolved.
2. Derlet: fitted positive quasiharmonic beta (0.120e-4 per K); Wang and Warrier: negative expansion in MD.
   These do not contradict each other (classical T -> 0 limit versus finite-T anharmonic MD), but no paper I
   opened shows both on the same potential, so this is my reading.
3. Wang's melting point for DND (about 3750 K) is taken from Fikar and Schaublin, which I did not open.

## 11.7 Limits of this check

- Our own numbers (3.1651 / 3.1605 / 3.1546 A) and the 0 K properties come from the request and from
  `make_dndbn.py`'s description; I did not run or read the test outputs.
- Wang's Fig. 2 is read by eye. Their DND file and their NPT protocol are not stated.
- I could not read the Warrier IAEA poster (HTTP 403) or the Fikar and Schaublin 2009 paper.
- I did not find the lattice constant of DND at 300, 600 or 1025 K in any text. The comparison is to a
  figure only.
- `make_dndbn.py` tabulates F(rho) on DRHO = 0.05 (10000 points) with LAMMPS interpolation. I found no
  source on whether that coarse a grid affects thermal expansion. It is a cheap thing to test (11.8),
  not evidence from literature.

## 11.8 Suggested checks (none run by me; for the main agent or the human)

1. Reproduce what Derlet fitted: NVT at a = 3.1652 A and low T (for example 20, 50, 100 K), measure the
   mean pressure and its slope. The paper's value implies dP/dT = beta x B of about 0.120e-4 per K x 310.4
   GPa, about 37 bar per K, positive (my arithmetic from the Table II values and my inference that beta is
   a volume coefficient in 1/K). Alternatively compute the Gruneisen parameter from phonon frequencies at
   two lattice constants. If the build gives a positive slope near 37 bar per K, it carries the fitted
   anharmonicity and the high-T negative expansion is a property of the potential. If it gives a different
   sign or a very different size, look for an error in the inner knots.
2. Reproduce Derlet Table II elastic constants (B 310.4, C' 160.6, C44 159.0 GPa) and defect energies
   (E_d111 9.548 (9.550), E_d110 9.844 (9.841), E_d100 11.490 (11.513), E_tet 11.050 (10.999), E_oct
   11.680 (11.709), E_crd 9.551 (9.557) eV, fitted values in brackets). E_d111 and the others test the
   inner knots that the lattice constant, E_c and E_vac do not.
3. Rebuild the table with DRHO = 0.005 (or finer) and the same r grid, and rerun the 300/600/1025 K NPT
   runs. If a(T) does not change, tabulation is ruled out.
4. Digitise Wang et al. Fig. 2 (DND curve) and compare with the NPT strains relative to 293 K. For a fair
   comparison use their protocol: 2000 atoms, zero pressure, reference 293.15 K.
5. Ask the authors (Warrier and Bhardwaj) for the temperature at which alpha = -0.97e-6 per K and a = 3.17
   A were obtained, and whether they used a file based on the uncorrected or corrected Bjorkas table.

## 11.9 Gaps and suggested next searches

- OpenKIM archive of MO_195478838873_002 (driver parameter files), to compare with Table IV mechanically.
  The `.../MO_195478838873.html` computed-properties page on NIST (empty for my tool).
- Fikar and Schaublin, J. Nucl. Mater. 386-388, 97 (2009): DND at high temperature, melting point 3750 K,
  possibly lattice parameter vs T.
- Sand, Dudarev, Nordlund, EPL 2013 (arXiv:1306.3824; "modified Derlet potential" in the earlier file
  section 10.1): whether the modification changed the thermal expansion. I did not check.
- A mechanism paper for negative expansion in minus-square-root EAM potentials (none found), and tests of
  Derlet-type V, Nb, Ta, Mo potentials at finite temperature.
- The Warrier IAEA poster (https://conferences.iaea.org/event/403/contributions/35096/attachments/19606/33552/PosterMKWarrier.pdf, HTTP 403).
