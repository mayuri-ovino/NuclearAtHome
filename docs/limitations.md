# What Nuclear@Home can and cannot tell us

Status: DRAFT (scientific scope; shown in plain language on the website's Overview page)

These limits are not about computing power. More volunteers do not remove any of them.

| Limitation | Root cause | What this project does about it |
|---|---|---|
| **No validation against fusion-relevant data** | No facility produces 14.1 MeV fusion neutrons at reactor-like flux (~10¹⁴ n/cm²/s); the experiment does not exist yet (infrastructure). | We validate against other MD studies that use the same potential and settings (benchmarks B1/B2 in `docs/interfaces/physics_settings.md`) and against internal checks (energy conservation, replication, canaries). Ion-beam and fission-neutron experiments are proxies only: their recoil spectra, transmutation (He/H) production and dose rates differ. Every number is published as a model prediction, never as a measurement. |
| **No full alloy complexity** | A potential for N elements must be fitted to DFT data covering every element pair and mixture; that data cost grows faster than linearly with N (DFT compute and data, not volunteer compute). | The alpha is pure tungsten. A material (W-Re, W-Ta, steels such as Eurofer97, SiC composites) is added only when a published, validated potential exists for it; until then it is not simulated. |
| **No confidence beyond the low-dose range** | MD gives isolated cascades of ~10–50 ps. Reaching 1 dpa needs very many overlapping cascades, and the methods that evolve damage over years (kinetic Monte Carlo, cluster dynamics) rely on mean-field assumptions that break down once clusters interact and microstructure forms (often quoted beyond ~10–100 dpa). | Cascade results are labelled *primary damage* (assumption A1 in `retention_chain.md`): one cascade in a perfect crystal. The planned retention model will be published only for low dose, with its assumptions listed, and never extrapolated to end-of-life wall damage. |
| **No coupling of transients with irradiation** | Disruptions (milliseconds), thermal cycles (minutes to hours) and damage accumulation (years) span ~10¹² in time, with two-way coupling; no code framework links them. | Out of scope. Runs are at fixed temperature (300 K in the alpha), with no disruptions, thermal cycling or stress. |

What the project *can* deliver: large, openly published statistics of primary damage in tungsten (defects per cascade, cluster sizes, their spread) under clearly stated assumptions, which other models can use as input.
