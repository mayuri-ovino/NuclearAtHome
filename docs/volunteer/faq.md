# Nuclear@Home: volunteer FAQ

Status: DRAFT for human review. Items marked **TODO-DECIDE** or **TODO-VERIFY** must be checked
before publication.

Terms used here:
- **BOINC** is free software that runs volunteer computing projects. You install it, add our project,
  and it runs our work on your computer.
- **Work unit (WU)** is one job from the project. Each work unit is one simulation.
- **Tungsten** is a metal. It is used in fusion reactor walls, and it is the only material in the
  current simulations.
- **Fusion** is the process that powers the Sun. Fusion reactors try to copy it on Earth.
- **Atom** is the smallest piece of an element.
- **Electron volt (eV)** is a very small unit of energy. A thousand electron volts is one keV
  (kilo-electron volt).
- **Picosecond (ps)** is one trillionth of a second.

## 1. What is this project?

Nuclear@Home simulates radiation damage in tungsten, the kind of metal that might line the walls of a
future fusion reactor.

In a fusion reactor, fast neutrons (uncharged particles that come out of the fusion reaction) hit
the wall. A neutron can knock a tungsten atom out of its place in the metal crystal. That atom then
knocks others, and the knocks spread out like a small burst of billiard balls. This burst is called a
**cascade**. It lasts a few picoseconds.

After a cascade, some atoms are left out of place. Each missing atom leaves an empty spot
(a **vacancy**), and each displaced atom sits in a gap between atoms (an **interstitial**). Together,
a vacancy and an interstitial are called a **Frenkel pair**. The project counts these defects.

The research aims to help us understand how wall metals wear out over time. Thousands of simulated
cascades give statistics on how many defects one neutron hit leaves, and how large the groups of
defects are.

Later, the project plans to add a second step. This step will check how much tritium (a heavy form of
hydrogen used as fusion fuel) gets stuck in the damage. **That step is not in the first test run.**
It needs more work first.

## 2. What does my computer actually do?

Your computer runs one simulation at a time:

1. It builds a small block of tungsten atoms in a regular crystal pattern.
2. It warms the block to room temperature (300 kelvin, about 27 °C) and lets it settle for 10 ps.
3. It gives one central atom a large kick, of 5 keV or 10 keV (5,000 or 10,000 electron volts).
   The kick stands in for one neutron hit. The neutron itself is not simulated.
4. It follows the atoms for 20 ps, watching the collisions.
5. It counts the defects that are left, and writes out the results.
6. It sends the results back to our server. The server checks them before any points are given.

The program is the standard LAMMPS simulation program (a free tool for simulating atoms). It runs
without any extra code from the project. The project's job files describe each step.

The first test runs use a block of 250,000 atoms (5 keV) or 843,750 atoms (10 keV).

## 3. What is simulated, and what is not?

**Simulated:**
- One cascade in a perfect tungsten crystal.
- Pure tungsten. Only one element is in the block.
- A fixed temperature of 300 K in the first test run.
- A fixed run length of 20 ps of cascade, with no early stop.

**Not simulated (yet):**
- Alloys (metal mixtures) such as steel or tungsten-rhenium. A material is added only when a trusted,
  published model of its atoms exists.
- Years of damage piling up in a wall. One cascade is a single first moment of damage.
- Sudden events like plasma disruptions (very fast losses of the plasma inside a reactor), heat
  cycles or stress.
- Changes of one element into another (transmutation), such as the helium or hydrogen that
  neutrons can create inside a metal.
- The neutron itself. We start from the atom it hits.
- The tritium step. It needs more work before the first test run can include it.

Read the full list in the project's **limitations** page.

## 4. What do I need?

- A **64-bit Linux or Windows computer on an Intel or AMD processor** (x86_64). Other systems,
  including Macs and the Raspberry Pi, are not supported yet. On Windows, only CPU tasks are
  available for now; GPU tasks need Linux.
- BOINC installed. On Windows, use the installer from https://boinc.berkeley.edu/download.php.
  On Ubuntu or Debian: `sudo apt install boinc-client boinc-manager`.
- **CPU tasks** use about one CPU core each. Peak memory was about 314 MB in one measured run on the
  developers' reference laptop. **TODO-DECIDE:** the memory figure to publish (rounded), once the
  calibration is done.
- **GPU tasks (optional).** An NVIDIA graphics card that works with OpenCL. Each GPU task also uses
  about one CPU core. A GPU task needs about 550 MB of memory on the computer (measured on the
  reference laptop). **TODO-DECIDE:** whether the GPU version ships in the first public test.

## 5. How long does one task take?

- **5 keV task, CPU:** about 1.6 hours (5,800 seconds) on the developers' reference laptop, using one
  core. This is one measurement, not an average.
- **5 keV task, GPU:** about 34 minutes on an NVIDIA RTX 4070 card. This is one run, and the GPU was
  shared with another computing project at the time.
- **10 keV task:** **TODO-CALIBRATE.** We have not measured this yet.

Your time will differ. It depends on your processor, your other programs, and whether the computer is
busy.

## 6. Can a crash or a restart lose my work?

Little is lost. The program saves a **checkpoint** (a saved copy of its progress) every 2,000
simulation steps, which is about 2 ps of simulated time. If your computer restarts, suspends, or
the program crashes, it resumes from the last checkpoint.

**TODO-CALIBRATE:** how often a checkpoint happens in real time. The team estimated about every
5 minutes. This has not been measured yet.

## 7. How do points work?

- **Points** measure how much work a result did. They are for fun. They have no cash or crypto value.
- A **5 keV work unit** is worth **1,760 points**. That is the reference value the project chose.
- A **10 keV work unit** is worth about **5,940 points**. This comes from the same formula, because
  it has more atoms and more steps.
- **Points are given only for validated results.** The server runs checks on each result. A result
  that fails the checks earns nothing.
- A new computer always has its work unit checked by a second computer. A trusted computer is
  sometimes checked this way. A result earns points only if the server marks it valid.
- The first test run has **no speed bonus**. Every valid result earns its base points, however fast
  or slow it was.
- **PPD** (points per day) is how many points a computer earns in a day. The stats pages show an
  **estimated PPD** (from recent speed) and an **actual PPD** (from the last 7 days of valid results).
- **TPF** (time per frame) is the time your computer takes to finish 1% of a work unit. The site
  shows the TPF history for each computer.

## 8. Badges

Badges show milestones on your account. They are shown on the stats pages when your stats are public.

| Badge | How you earn it | Threshold |
|---|---|---|
| Lithium | Total valid points | 10,000 |
| Beryllium | Total valid points | 100,000 |
| Breeder | Total valid points | 1,000,000 |
| Ignition | Total valid points | 10,000,000 |
| Reliable | Of your last 50 judged results, at least 98% are valid | 50 results, 98% |
| Veteran | 365 days since your first valid result | 365 days |
| Tritium Hunter | Valid trapping work units | **Not yet available.** It waits for the tritium step. |

A "judged" result is one the server has finished checking, either valid or invalid.

The **Discovery** honour is different. It has no points. It is given only when a result is used in a
published figure, or is the first confirmed example of a new defect, and a team of reviewers approves
it. **TODO-DECIDE:** whether to mention this in the FAQ.

## 9. The 3D viewer

Some finished cascades have a 3D view. You can open it from the **Machines** page or the **Work Units**
page.

- The view shows the block of atoms. Atoms that are moving fast are coloured differently. Empty spots
  (vacancies) are shown too.
- Three buttons switch between views.
- The view opens on the surviving defects. Press **Play** to watch the cascade again.
- Not every work unit has a 3D view. The site shows which ones do.

The 3D view runs in your web browser. It needs no install.

## 10. Teams

You can create a team or join one from your account page on the project website. Your points count
for your team as well as for you. Team totals are shown by team number.

**TODO-VERIFY:** join codes for teams are planned for the beta. Check that they work before publishing
this section.

## 11. Privacy

The project collects nothing beyond BOINC's default records, and our database keeps only the copies
listed in the privacy policy. Read the privacy policy (`privacy.md`) for details, including:
- What the public can see.
- How to turn off stats export and showing your computers.
- What happens when you delete your account.

## 12. Money

Nuclear@Home does not pay cash or crypto. Points are for fun.

## 13. How do I pause or stop?

- **Pause for a while.** In BOINC Manager, pick the project and suspend it. Or set the computing
  preferences to run only when the computer is idle. **TODO-VERIFY** the exact menu names in the
  BOINC version you run.
- **Leave the project.** In BOINC Manager, remove the project from your list. **TODO-VERIFY** the exact
  menu name. Your results already sent stay in the database, as described in the privacy policy.
- **Delete your account.** Use the BOINC account page. **TODO-VERIFY** the exact steps and what BOINC
  removes.

## 14. Where do I get help?

Ask on the Nuclear@Home Discord: https://discord.gg/EpMVWUCFZ9. For privacy questions, email
nuclearathome@gmail.com.

The project address (the address you enter in BOINC Manager) will appear on the join page when the
invite-only beta opens. **TODO-DECIDE:** the address and the beta start date.
