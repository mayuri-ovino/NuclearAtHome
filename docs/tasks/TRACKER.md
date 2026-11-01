# Task tracker

Status values: todo, in-progress, review, done, blocked
Owner `main` = main agent; `human` = you. "post-alpha" in Depends on = not needed for the alpha (decision D1).
Reviewer: who must review before merge (physics-reviewer / security-reviewer / main). Anything touching physics,
validation, credit, or security is also flagged for human approval.

| ID | Title | Phase | Owner | Status | Depends on | Reviewer | Reviewed |
|---|---|---|---|---|---|---|---|
| T-002 | Finalize + freeze `workunit_schema.json` | 2 | main | todo | Phase 1 approval | physics-reviewer | no |
| T-003 | Finalize + freeze `result_schema.json` | 2 | main | todo | T-002 | physics-reviewer | no |
| T-004 | Fill `physics_settings.md` from verified sources + decisions; freeze | 2 | main + human | todo | lit verified by human | physics-reviewer | no |
| T-005 | Rewrite `validator_spec.md` for script_validator + BOINC trust (D3); freeze | 2 | main + human | todo | T-003, D3 | physics-reviewer | no |
| T-006 | Update `credit_spec.md` for `--credit_from_wu`, no alpha bonus (D2); freeze | 2 | main + human | todo | D2 | physics-reviewer | no |
| T-007 | `stats_spec.md`: PostgreSQL DDL + API contract; freeze | 2 | main | todo | T-003 | security-reviewer | no |
| T-008 | New `client_contract.md`: job.xml, slot file names, `nah-helper` CLI; freeze | 2 | main | todo | T-003 | security-reviewer | no |
| T-009 | New `server_deploy.md`: VM layout, ports, backups, signing procedure; freeze | 2 | main | todo | — | security-reviewer | no |
| T-010 | `retention_chain.md`: mark post-alpha, freeze structure | 2 | main + human | todo | — | physics-reviewer | no |
| T-011 | Test suites from frozen interfaces (schema fixtures, validator vectors, credit cases) | 2 | main | todo | T-002..T-008 | main | no |
| T-020 | LAMMPS cascade input template (restart-aware, progress file, energy log, WS defects) | 3 | wu-template-writer | todo | T-004, T-008 | physics-reviewer | no |
| T-021 | WU JSON renderer to LAMMPS variables + sample WUs | 3 | wu-template-writer | todo | T-002, T-020 | main | no |
| T-022 | Parameter sampler favoring under-sampled bins (fixed energy grid, D7) | 3 | wu-template-writer | todo | T-002, T-007 | physics-reviewer | no |
| T-023 | Base points at WU creation + `create_work` helper | 3 | wu-template-writer | todo | T-006 | physics-reviewer | no |
| T-024 | Work generator daemon (incl. canary creation into `canaries` table) | 3 | wu-template-writer | todo | T-021..T-023 | security-reviewer | no |
| T-025 | Local benchmark-run harness for the dev machine (CPU and GPU) | 3 | wu-template-writer | todo | T-020 | physics-reviewer | no |
| T-026 | Trapping input template | 3 | wu-template-writer | todo | post-alpha | physics-reviewer | no |
| T-027 | Stage B spawning in work generator | 3 | wu-template-writer | todo | post-alpha, T-024 | physics-reviewer | no |
| T-030 | Static LAMMPS Linux x86_64 build recipe (pinned version, published source) | 4 | client-helper | todo | T-004 | security-reviewer | no |
| T-031 | `nah-helper` Rust crate skeleton; `cargo test` wired into `run-tests.sh` | 4 | client-helper | todo | T-008 | main | no |
| T-001 | TPF timer: rewrite card for Rust `nah-helper monitor` (suspend-gap rule, D11) | 4 | client-helper | todo | T-031 | physics-reviewer | no |
| T-032 | Defect clustering from WS output in `nah-helper package` | 4 | client-helper | todo | T-031, T-004 | physics-reviewer | no |
| T-033 | Result packaging: `result.json`, sha256, compression | 4 | client-helper | todo | T-031, T-003 | security-reviewer | no |
| T-034 | job.xml + app version layout (unsigned dev build) | 4 | main | todo | T-020, T-030..T-033 | security-reviewer | no |
| T-035 | Kill/suspend/restart integration test on a local BOINC client | 4 | test-writer | todo | T-034 | main | no |
| T-036 | Python reference defect/cluster analysis for server re-checks | 4 | analysis-builder | todo | T-004 | physics-reviewer | no |
| T-040 | Checks V1 schema, V2 integrity, V8 atom count | 5 | validator-check-writer | todo | T-005, T-011 | security-reviewer | no |
| T-041 | Checks V3 completeness, V5 stabilization | 5 | validator-check-writer | todo | T-005 | physics-reviewer | no |
| T-042 | Check V4 energy conservation (across restart segments) | 5 | validator-check-writer | todo | T-005 | physics-reviewer | no |
| T-043 | Checks V6 Frenkel balance, V7 plausible range | 5 | validator-check-writer | todo | T-005, R5 ranges filled | physics-reviewer | no |
| T-044 | Checks V9, V10 (trapping) | 5 | validator-check-writer | todo | post-alpha | physics-reviewer | no |
| T-045 | `script_validator` init/compare glue + replica population test | 5 | validator-check-writer | todo | T-040..T-043 | physics-reviewer | no |
| T-046 | Trust: adaptive replication config, canary-failure reset, outlier hold/reissue | 5 | main | todo | T-045 | security-reviewer | no |
| T-047 | Mock results: good, broken, and cheating (forged in-range) | 5 | test-writer | todo | T-011 | physics-reviewer | no |
| T-050 | Credit calibration on reference machine (`ref_work`, cost factors) | 6 | main + human | todo | T-025 | physics-reviewer | no |
| T-051 | Hourly estimated-PPD job from TPF samples | 6 | stats-builder | todo | T-007 | physics-reviewer | no |
| T-052 | Badges (thresholds from `credit_spec.md`) | 6 | stats-builder | todo | T-006, T-007 | main | no |
| T-053 | `db_dump` XML export config + public credit transparency log | 6 | stats-builder | todo | T-007 | security-reviewer | no |
| T-060 | PostgreSQL DDL + migrations | 7 | stats-builder | todo | T-007 | security-reviewer | no |
| T-061 | Assimilator: ingest to PostgreSQL + file storage | 7 | stats-builder | todo | T-060, T-033 | security-reviewer | no |
| T-062 | Daily host/user/team aggregation + ranks | 7 | stats-builder | todo | T-060 | main | no |
| T-063 | Science aggregates with SE + bootstrap CI | 7 | analysis-builder | todo | T-060 | physics-reviewer | no |
| T-064 | Read-only JSON API | 7 | stats-builder | todo | T-060 | security-reviewer | no |
| T-065 | Dashboard pages | 7 | viewer-builder | todo | T-064 | security-reviewer | no |
| T-066 | Privacy policy, GDPR consent setup, volunteer FAQ | 7 | docs-writer | todo | T-009 | security-reviewer + human | no |
| T-067 | Retention model (rate theory or kinetic Monte Carlo) | 7 | main + analysis-builder | todo | post-alpha, T-010 | physics-reviewer | no |
| T-070 | Snapshot file format for viewer (interface) | 8 | main | todo | T-008 | main | no |
| T-071 | Three.js cascade viewer | 8 | viewer-builder | todo | T-070, T-064 | security-reviewer | no |
| T-072 | WU info panel (material, energy, TPF, PPD, points) | 8 | viewer-builder | todo | T-071 | main | no |
| T-073 | BOINC screensaver graphics app | 8 | viewer-builder | todo | post-alpha (D5) | security-reviewer | no |
| T-080 | Benchmark reproduction (B1, B2) on dev machine | 9 | main + analysis-builder | todo | T-025, T-036, T-004 | physics-reviewer + human | no |
| T-081 | Convergence tests: box size, timestep, sample size | 9 | main + analysis-builder | todo | T-025 | physics-reviewer | no |
| T-082 | End-to-end test with mock volunteers on a staging server | 9 | test-writer | todo | T-024, T-046, T-061 | security-reviewer | no |
| T-083 | Server load test | 9 | test-writer | todo | T-082 | main | no |
| T-084 | Deploy + harden cloud VM, backups | 9 | main + human | todo | T-009 | security-reviewer | no |
| T-085 | Code-signing ceremony on offline machine | 9 | human | todo | T-034, T-084 | security-reviewer | no |
| T-086 | Alpha checklist, invite-only beta, launch news post | 9 | docs-writer + human | todo | T-080..T-085 | human | no |
