-- Nuclear@Home science and stats database (PostgreSQL). Mirrors docs/interfaces/stats_spec.md.
-- Trapping, discovery and retention tables are added with those stages (post-alpha, D1).

CREATE SEQUENCE wu_serial;  -- WU name serials; never reused

CREATE TABLE workunits (
    wu_name             text PRIMARY KEY,
    energy_ev           double precision NOT NULL,
    temperature_k       double precision NOT NULL,
    points_base         double precision NOT NULL,
    status              text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_flight', 'done', 'failed')),
    created_at          timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE wu_results (
    wu_id               text PRIMARY KEY REFERENCES workunits(wu_name),
    wu_type             text NOT NULL,
    campaign_id         text NOT NULL,
    host_id             bigint NOT NULL,
    user_id             bigint NOT NULL,
    team_id             bigint NOT NULL DEFAULT 0,
    material_family     text NOT NULL,
    potential_id        text NOT NULL,
    temperature_k       double precision NOT NULL,
    pka_energy_ev       double precision NOT NULL,
    validated           boolean NOT NULL,
    outlier             boolean NOT NULL DEFAULT false,      -- far from its bin: kept in aggregates, flagged
    points_base         double precision NOT NULL,
    points_awarded      double precision NOT NULL,
    sent_at             timestamptz NOT NULL,
    reported_at         timestamptz NOT NULL
);

CREATE TABLE cascade_stats (
    wu_id               text PRIMARY KEY REFERENCES wu_results(wu_id),
    n_vacancies         integer NOT NULL,
    n_interstitials     integer NOT NULL,
    peak_displaced      integer,
    final_sha256        text NOT NULL UNIQUE,    -- replay detection (validator V2)
    energy_sha256       text NOT NULL UNIQUE,
    boundary_hit        boolean NOT NULL,        -- a recoil above the flag energy reached the thermostat/fixed layer
    cluster_sizes_vac   integer[] NOT NULL,
    cluster_sizes_int   integer[] NOT NULL,
    snapshot_file       text
);

CREATE TABLE tpf_samples (
    host_id             bigint NOT NULL,
    wu_id               text NOT NULL REFERENCES wu_results(wu_id),
    slot_kind           text NOT NULL DEFAULT 'cpu',
    tpf_s               double precision NOT NULL CHECK (tpf_s > 0),
    recorded_at         timestamptz NOT NULL
);

CREATE TABLE host_daily (
    host_id bigint, day date, points double precision, wus_valid integer, wus_invalid integer,
    est_ppd double precision, actual_ppd_7d double precision, PRIMARY KEY (host_id, day)
);
CREATE TABLE user_daily (id bigint, day date, points double precision, ppd double precision, rank integer, PRIMARY KEY (id, day));
CREATE TABLE team_daily (id bigint, day date, points double precision, ppd double precision, rank integer, PRIMARY KEY (id, day));
CREATE TABLE badges (user_id bigint, badge_id text, awarded_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (user_id, badge_id));

-- Science aggregates per bin, written by stats/jobs.py (which can exclude canaries);
-- the API reads only this table for science, never the raw rows joined with canaries.
CREATE TABLE science_aggregates (
    material_family text, potential_id text, pka_energy_ev double precision, temperature_k double precision,
    n integer NOT NULL, mean_frenkel double precision, se_frenkel double precision,
    ci95_low double precision, ci95_high double precision, cluster_size_hist jsonb,
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (material_family, potential_id, pka_energy_ev, temperature_k)
);

-- SERVER-ONLY canary tables. The API role gets no privileges on them (see grants below).
CREATE TABLE canary_pool (
    pool_id             serial PRIMARY KEY,
    wu_record           jsonb NOT NULL,          -- WU parameters of a reference run (serial/wu_id replaced on use)
    ref_mean_frenkel    double precision NOT NULL,
    ref_sd_frenkel      double precision NOT NULL CHECK (ref_sd_frenkel > 0),
    used_by_wu_name     text UNIQUE
);
CREATE TABLE canaries (
    wu_name             text PRIMARY KEY REFERENCES workunits(wu_name),
    pool_id             integer NOT NULL REFERENCES canary_pool(pool_id),
    created_at          timestamptz NOT NULL DEFAULT now()
);

-- BOINC privacy choices, copied daily by stats/jobs.py; the API shows a user only with
-- stats_export consent and a host only if its owner allows showing computers.
CREATE TABLE privacy (
    user_id bigint PRIMARY KEY, show_hosts boolean NOT NULL, stats_export boolean NOT NULL
);

CREATE INDEX wu_results_bin ON wu_results (material_family, potential_id, pka_energy_ev, temperature_k);
CREATE INDEX wu_results_host ON wu_results (host_id, reported_at);

-- Read-only role for the public API: science and stats only, never canaries.
CREATE ROLE nah_api NOLOGIN;
GRANT SELECT ON wu_results, cascade_stats, tpf_samples, host_daily, user_daily, team_daily, badges, science_aggregates, privacy TO nah_api;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
-- Login roles (passwords set outside this repo):
--   nah_api_login  LOGIN IN ROLE nah_api, CONNECTION LIMIT 20   (API)
--   nah_validator  SELECT on wu_results, cascade_stats, canaries, canary_pool (validator, read-only)
--   nah_writer     generator, assimilator, stats jobs (read/write; owns no other database)
-- BOINC MariaDB user for these scripts: SELECT(id, name, canonical_resultid) ON workunit,
--   SELECT(id, hostid, userid, sent_time, received_time, elapsed_time, granted_credit, validate_state) ON result,
--   SELECT(id, teamid, show_hosts) ON user, SELECT ON consent, consent_type. Never the full-rights project user.
