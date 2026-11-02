# Transmutation of W in fusion: potentials, inventories, cascade studies

Status: UNVERIFIED
Compiled 2026-11-02 by literature-lead agent. Only pages marked "opened" were actually fetched. Page text was read through a summarizing fetch tool, not the raw PDF, so every number needs human check against the original.

## 1. Interatomic potentials (W-Re; no W-Re-Os found)

No ternary W-Re-Os potential was found in any source I opened. TODO-LIT: search for one (see next searches).

### 1a. Bonny, Bakaev, Terentyev, Mastrikov (2017)
- "Interatomic potential to study plastic deformation in tungsten-rhenium alloys", J. Appl. Phys. 121(16), 165107. DOI 10.1063/1.4982361.
- Form: EAM, LAMMPS `pair_style eam/alloy`, file WRe.eam.alloy. Distributed at NIST IPR (opened: https://www.ctcms.nist.gov/potentials/entry/2017--Bonny-G-Bakaev-A-Terentyev-D-Mastrikov-Y-A--W-Re/) and OpenKIM MO_234187151804_000 (seen in search results only, not opened).
- Aimed at plasticity (Re softening of W), per search-result summary of the paper; the NIST page does not mention ZBL or cascades. Tested for cascades / Re clustering: NOT confirmed. TODO-LIT: check the paper itself for a short-range ZBL join.

### 1b. Setyawan, Gao, Kurtz (2018)
- "A tungsten-rhenium interatomic potential for point defect studies", J. Appl. Phys. 123(20), 205102. DOI 10.1063/1.5030113.
- Form: EAM, `eam/alloy`, file WRe_Setyawan_set145.eam.alloy. NIST IPR (opened): https://www.ctcms.nist.gov/potentials/entry/2018--Setyawan-W-Gao-N-Kurtz-R-J--W-Re
- Search-result abstract says it was fitted to point-defect ab initio data and also evaluated on sigma and chi phase energies. NIST page: no ZBL/cascade mention. Cascade and clustering tests: NOT confirmed.

### 1c. Chen, Li, Gao, Zhou, Hu, Lu, Gao, Deng (2018)
- "New interatomic potentials of W, Re and W-Re alloy for radiation defects", J. Nucl. Mater. 502, 141-153. DOI 10.1016/j.jnucmat.2018.01.059.
- Form: EAM-style, `eam/fs`, file WRe_YC1.eam.fs. NIST IPR (opened): https://www.ctcms.nist.gov/potentials/testing/entry/2018--Chen-Y-Li-Y-H-Gao-N-et-al--W-Re
- Abstract (via search snippet) targets radiation defects and Re-rich clusters. NIST page: no ZBL/cascade mention. ZBL join and cluster results: NOT confirmed (TODO-LIT).

Limitation for all three: NIST pages warn that elemental pieces of alloy potentials may perform poorly for the pure element. Nuclear@Home's pure-W runs should keep using the potential in docs/interfaces/physics_settings.md.

## 2. Transmutation inventories

### 2a. Gilbert, Sublet, Dudarev (2017)
- "Spatial heterogeneity of tungsten transmutation in a fusion device", Nucl. Fusion (2017). arXiv:1612.03892 (opened via ar5iv https://ar5iv.labs.arxiv.org/html/1612.03892). Author list and journal taken from search result, not verified on page.
- Neutron transport plus inventory on spatially heterogeneous power-plant models (details of the model not captured; TODO-LIT).
- Numbers as extracted by the fetch tool (verify; table/figure in parentheses):
  - Re, scenario 1, after 2 full-power years (Fig. 6): max minus min difference "more than 4600 appm or 0.46 atm.%"; volume-average "around 3500 appm"; std deviation about that mean "more than 400 appm". Max is at the back of the W next to the steel-water moderator; minimum at about 1.2 cm depth.
  - Without self-shielding correction Re is over-predicted by 25-50%.
  - Scenario 2 (water channel behind W): Re more than 30% higher at the back, about 15% higher 50 mm from the water.
  - Os: text only, "a few hundred appm". Ta: no numbers; over 90% from 182W(n,2n) then decay.
  - He and H: NOT reported in this paper.
  - Experiment (HFR Petten, 208 effective full-power days): simulated Re 4 at.% (5% without correction); measured EDX 1.2-1.4 atm.%; corrected simulation 1.4 at.%.
- Limitation: only 2 fpy; no time series.

### 2b. Cottrell, Pampin, Taylor (Fusion Sci. Technol. vol. 50, c. 2006)
- "Transmutation and phase stability of tungsten armor in fusion power plants". Page opened: https://scientific-publications.ukaea.uk/?p=3989 (year/journal/DOI not on page; vol. 50 only inferred from a PDF filename; year 2006 comes from a search snippet). TODO-LIT: confirm citation and DOI (ANS page: https://ans.org/pubs/journals/fst/article-1224, not opened).
- Reports PPCS models A, B (softer spectrum): first-wall armor reaches about 91 at.% W, 6 at.% Re, 3 at.% Os at the rear face at end of service. Model AB (harder spectrum) transmutes markedly slower. Alloys stay single-phase bcc over service life. No service time given on the page. Ta not mentioned.

### 2c. Gilbert, "Transmutation and He Production in W and W-alloys" (UKAEA report)
- Opened: https://scientific-publications.ukaea.uk/?p=8690. Page has abstract only: no numbers, year, or DOI. Full report needed for He/H versus fpy. TODO-LIT.

### 2d. Not opened (leads only)
- Gilbert & Sublet 2011, Nucl. Fusion 51, 043005 (DOI believed 10.1088/0029-5515/51/4/043005, unconfirmed): not found in search. Probably the main source for Re/Os/Ta/He/H versus fpy.
- Chatzikos et al. 2025, Fusion Eng. Des.: experimental validation of W transmutation at BR2 (https://researchportal.sckcen.be/en/publications/experimental-validation-of-transmutation-products-calculations-in/).
- Lloyd et al. 2019 Scripta Mater.; Birmingham paper on isotopic enrichment to suppress Re/Os (https://research.birmingham.ac.uk/en/publications/suppression-of-rhenium-and-osmium-production-in-tungsten-by-selec/).

No source I opened gives He or H concentration versus fpy. All He/H numbers: TODO-LIT.

## 3. MD / OKMC and related studies

Not opened in full (paywalled copy was blocked, so Fu et al. content below is from a search snippet only):
- Fu et al., J. Nucl. Mater. (2019), MD of high-energy damage in W and W-Re (5 and 10 at.% Re), PKA up to 300 keV. Snippet says Re segregation pins interstitial clusters and 1/2<111> loops, lowering mobility versus pure W. Abstract: https://lammps.org/abstracts/abstract.16804.html. Potential used, ZBL: TODO-LIT.
- Later W-Re study with grain boundary / sigma phase (https://pubs.rsc.org/en/content/articlepdf/2022/ra/d2ra04138c): snippet says interstitials go to the GB, leaving more bulk vacancies in W-Re than W.
- Zhou, Li, Lu et al., Nucl. Fusion 2017 (first principles): snippet says Re atoms prefer to stay dispersed in W, and a 1.10 eV barrier at 10 Os atoms for Os clustering.
- Acta Mater. 2015 ion-irradiation APT of W-1Re-1Os and W-2Re (https://scientific-publications.ukaea.uk/wp-content/uploads/Preprints/ActaMaterialiaVOL87p121.pdf): snippet says Os promotes nucleation and Re promotes growth of precipitates.
- Pure-W reference: five-potential comparison of W cascades, arXiv:2402.00359 (https://arxiv.org/html/2402.00359v1): snippet says potential stiffness does not change defect counts or clustering. Relevant to the ZBL question; not opened.
- No OKMC study of Re/Os found.

## Disagreements / flags
- Re at end of service: about 6 at.% (Cottrell, PPCS A/B rear face) versus about 0.35-0.46 at.% after 2 fpy (Gilbert 2017). These are different designs, positions and times, so they are not a conflict, but they must not be mixed.

## Gaps
- No W-Re-Os potential; no cascade/ZBL validation confirmed for any W-Re potential.
- No He/H versus fpy; no ITER/DEMO divertor tables opened.
- No primary verification of MD papers.
