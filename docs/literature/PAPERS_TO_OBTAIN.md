# Papers and data to obtain

Status: for the human. Each item says which value in `config/settings.toml` or
`docs/interfaces/physics_settings.md` it verifies. "Free" = open access (arXiv or OA).

## Needed to verify values in use now

| # | Source | Verifies | Access |
|---|---|---|---|
| 1 | Juslin & Wirth, "Interatomic potentials for simulation of He bubble formation in W", J. Nucl. Mater. 432, 61–66 (2013). DOI 10.1016/j.jnucmat.2012.07.023 | The real JW potential. **Also ask the authors (B. D. Wirth, Univ. of Tennessee) for the W–W potential file.** With it, W_EAM_A becomes the benchmark's exact potential instead of a stand-in | Paywalled (library) + email |
| 2 | Setyawan et al., "Displacement cascades and defects annealing in tungsten, Part I", J. Nucl. Mater. 462, 329 (2015). DOI 10.1016/j.jnucmat.2014.12.056 | a0 3.167 Å at 300 K; max displacement 0.005 Å per step; cluster cutoffs (3NN interstitial, 4NN vacancy) | Free: arXiv:1404.6490 |
| 3 | Byggmästar et al., "Four regimes of primary radiation damage in tungsten" | Electronic-stopping cutoff of 10 eV | Free: arXiv:2503.02710 |
| 4 | The electronic-stopping reference cited by Warrier & Bhardwaj (their ref. [21]) | Their exact friction model and cutoff; replaces source #3 if different | Look up in arXiv:2402.00359 |
| 5 | SRIM (srim.org), run for W ions in W, saved as `client/potentials/stopping_W.dat` (two columns: energy in eV, stopping in eV/Å) | The electronic-stopping table. **Blocks all real runs** | Free software (Windows; Wine works) |
| 6 | Warrier & Bhardwaj, arXiv:2402.00359, Fig. 2 | Defect counts at 5 and 10 keV, digitized, to replace the loose V7 range (0–47, 0–95) | Free (I read Sec. 2 and Tables 1–3 directly) |

## Background for the choices made

| # | Source | Why |
|---|---|---|
| 7 | Ackland & Thetford, Phil. Mag. A 56, 15–30 (1987). DOI 10.1080/01418618708204464 | Base of W_EAM_A (file from NIST IPR) | Paywalled |
| 8 | Ziegler, Biersack, Littmark, *The Stopping and Range of Ions in Solids* (1985) | ZBL formula used in the splice; it matches LAMMPS `pair_style zbl` to 3e-10 in force | Book |
| 9 | Norgett, Robinson, Torrens, Nucl. Eng. Des. 33, 50 (1975) | NRT formula behind the V7 sanity bound | Paywalled |
| 10 | Nordlund et al., "Improving atomic displacement and replacement calculations with physically realistic damage models", Nat. Commun. 9, 1084 (2018) | arc-dpa comparison for benchmark plots | Free |
| 11 | Sand, Dudarev, Nordlund, EPL 103, 46003 (2013) | Effect of the stopping cutoff (1–100 eV scan) | Paywalled |
