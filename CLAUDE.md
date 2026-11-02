# Nuclear@Home — project rules

Nuclear@Home is a BOINC volunteer computing project. Volunteers run molecular
dynamics (LAMMPS) simulations of collision cascades in fusion materials, then
insert hydrogen/tritium into the damaged material to measure trapping. The server
turns millions of results into an open database and an estimate of tritium
retained in fusion reactor walls.

Every agent working in this repository (main session and subagents) follows these rules.

## Roles
- The **main agent** (the top-level Claude Code session) owns architecture,
  physics decisions, interfaces, validator thresholds, the credit formula,
  security, and final integration. Its full brief is in `PROMPT.md`.
- **Subagents** in `.claude/agents/` implement task cards from `docs/tasks/`.
- The **human** approves physics choices, thresholds, credit calibration,
  anything security-related, and anything to be published.

## Frozen interfaces
- Files in `docs/interfaces/` marked `Status: FROZEN` (Markdown) or
  `"_status": "FROZEN"` (JSON) must not be edited by any agent. A hook enforces this.
- If a frozen interface seems wrong, stop and report the conflict. Do not work around it.
- Only the human changes a file from FROZEN back to DRAFT.

## Science integrity
- Never invent physics values, benchmark numbers, or literature results.
  Use placeholders marked `TODO-LIT` with a note on what source is needed.
- Physics settings (interatomic potentials, ZBL blending, electronic stopping,
  electron–phonon coupling, box sizes, temperatures, run lengths, thresholds)
  come only from `docs/interfaces/physics_settings.md`.
- Never weaken a validation check to make a test pass.

## Code standards
- Python 3.11+ (server, validator, stats, analysis), no project code on
  volunteer machines (BOINC's stock `wrapper` runs LAMMPS; the server parses its raw
  output), Linux x86_64 clients only,
  JavaScript + Three.js (viewer). SQL: MariaDB for BOINC, PostgreSQL for science data.
- Every code change ships with tests in `tests/` mirroring the source folder.
  Run `scripts/run-tests.sh` before reporting done.
- Keep functions small and documented. No new dependencies without listing them
  in the task report.

## Task workflow
1. The main agent writes a task card in `docs/tasks/T-XXX.md` from `docs/tasks/TEMPLATE.md`
   and adds a row to `docs/tasks/TRACKER.md`.
2. Interfaces and task cards are committed to git BEFORE delegating, because
   worktree subagents branch from the default branch.
3. The subagent implements the card, runs tests, and returns a report with:
   files changed, tests run and results, assumptions, open questions.
4. The main agent reviews, sends anything touching physics, validation, credit,
   or security to `physics-reviewer` or `security-reviewer`, then merges.
5. The tracker row is updated (status, reviewed).

## Security
- Never read, create, or print secrets. The BOINC code-signing private key is
  kept offline and never enters this repository.
- Never add code that collects volunteer data beyond BOINC defaults.

## Folder map
- `server/` work generator, assimilator, BOINC server config
- `client/` stock-wrapper job config, LAMMPS input template, LAMMPS build recipe
- `validator/` result checks and host trust scoring
- `stats/` credit, PPD, badges, stats aggregation, XML export, API
- `viewer/` Three.js web viewer and dashboard front end
- `analysis/` defect counting, cluster analysis, tritium retention model
- `tests/` all tests
- `docs/interfaces/` contracts; `docs/tasks/` task cards and tracker
