-- Nuclear@Home science and stats database (PostgreSQL). Mirrors docs/interfaces/stats_spec.md.
-- Trapping, discovery and retention tables are added with those stages (post-alpha, D1).

CREATE TABLE workunits (
    wu_name             text PRIMARY KEY,
    energy_ev           double precision NOT NULL,
    temperature_k       double precision NOT NULL,
    points_base         double precision NOT NULL,
    confirms_wu_name    text REFERENCES workunits(wu_name),   -- set on outlier confirmation WUs
    status              text NOT NULL DEFAULT 'in_flight' CHECK (status IN ('in_flight', 'done', 'failed')),
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
    held                boolean NOT NULL DEFAULT false,      -- outlier awaiting confirmation
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

CREATE INDEX wu_results_bin ON wu_results (material_family, potential_id, pka_energy_ev, temperature_k);
CREATE INDEX wu_results_host ON wu_results (host_id, reported_at);

-- Read-only role for the public API: science and stats only, never canaries.
CREATE ROLE nah_api NOLOGIN;
GRANT SELECT ON wu_results, cascade_stats, tpf_samples, host_daily, user_daily, team_daily, badges, science_aggregates TO nah_api;
