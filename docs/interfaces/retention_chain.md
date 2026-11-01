# Tritium retention chain

Status: DRAFT

How volunteer results become an estimate of tritium retained in reactor walls.
Every link has assumptions; they must be listed here and shown wherever the
estimate is displayed.

## The chain

```
Neutron spectrum at the wall (from FusionBlanket@home or literature)
        │  converted to recoil energies (server)
        ▼
Stage A: cascade WUs (volunteers)
        │  surviving defects, cluster sizes per energy, temperature, material
        ▼
Defect production statistics (server)
        │  defects produced per unit damage dose, with uncertainty
        ▼
Stage B: trapping WUs (volunteers)
        │  trap types, occupancy, binding energies
        ▼
Trap parameter table (server)
        │  trap concentration per dose + binding energy distribution
        ▼
Rate-theory or kinetic Monte Carlo transport model (server)
        │  diffusion + trapping/detrapping over reactor operating time
        ▼
Tritium retained per m² of wall vs. time, with uncertainty band
```

## Assumptions to resolve (main agent + human)

| # | Assumption | Status |
|---|---|---|
| A1 | Defect production from isolated cascades represents early-dose damage | TODO-DECIDE |
| A2 | How cascade overlap and defect evolution beyond MD timescales are handled | TODO-DECIDE |
| A3 | Trap binding energies from MD/relaxation are transferable to the transport model | TODO-DECIDE |
| A4 | Wall temperature profile and tritium flux at the surface | TODO-LIT |
| A5 | Transport model choice (rate theory vs. kinetic Monte Carlo) and its parameters (diffusivity etc.) | TODO-LIT |
| A6 | Isotope effects between H and T | TODO-LIT |
| A7 | Surface effects (recombination, desorption) | TODO-LIT |

## Uncertainty propagation

Report three separate contributions: statistical (sample size), model
(spread across interatomic potentials), and chain (assumptions A1–A7, by
varying them). Never report a single number without its band.

## Validation targets

Compare predicted retention trends against published experiments on
irradiated tungsten (e.g., deuterium retention after ion or neutron damage):
TODO-LIT sources.
