# Interfaces

Status: DRAFT (index file; never frozen)

These files are the contracts every agent builds against. They start as **DRAFT**.
In Phase 2 the main agent finalizes each one, the human approves it, and its status
line changes to **FROZEN**. A hook then blocks all agent edits to it.

| File | What it defines | Owner |
|---|---|---|
| `workunit_schema.json` | Inputs for cascade (A) and trapping (B) work units | main agent |
| `result_schema.json` | What the client returns | main agent |
| `physics_settings.md` | Every physics choice and analysis setting | main agent + human |
| `retention_chain.md` | How trapping results become a wall-retention estimate | main agent + human |
| `validator_spec.md` | Checks, tolerances, replication, trust scoring | main agent + human |
| `credit_spec.md` | Points, bonus, TPF, PPD, badges, discovery credit | main agent + human |
| `stats_spec.md` | Stats tables, aggregation jobs, API endpoints | main agent |

Placeholders:
- `TODO-LIT` — value must come from a verified published source
- `TODO-DECIDE` — a design choice the human must make
- `TODO-CALIBRATE` — value set by measurement on a reference machine
