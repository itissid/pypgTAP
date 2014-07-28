--- Table creation queries ---------
CREATE TABLE staging.lnrt_response_time (
    user_id char(36),
    unit_id char(36),
    log_time timestamp,
    curr_interaction_time timestamp,
    normalized_time_quitting float8,
    normalized_time_non_quitting float8,
    posterior_quit_prob float8,
    gaussian_quantiles_non_quitting float8,
    gaussian_quantiles_quitting float8
)
DISTKEY(unit_id)
SORTKEY(log_time);

GRANT SELECT, INSERT, DELETE, UPDATE ON staging.lnrt_response_time TO GROUP database_writers;
GRANT SELECT ON staging.lnrt_response_time TO GROUP astronauts, GROUP knewton_devs;

--TODO(Sid): Rename staging to presentation
CREATE TABLE staging.f_lnrt_param_summary_stats(
    subgraph_id         CHAR(36),
    parameter_name      CHAR(100),-- speed_r, speed_q etc
    kl_dvg              FLOAT8, -- the value of kl divergence
    -- Over time we can add more stats
    time_from           TIMESTAMP,  -- Will contain the start time stamp after which the param was measured
    time_to             TIMESTAMP, -- Will contain the end time stamp before which the param was measured
    time_slice_name     CHAR(100), -- Will contain the representative name of the time slice(last 1 week, last 1 month etc)

-- Date and time synthetic keys for faster join
    time_from_date_id   INT,
    time_to_date_id     INT,
    time_from_time_id   INT,
    time_to_time_id     INT

);
GRANT SELECT, INSERT, DELETE, UPDATE ON staging.f_lnrt_param_summary_stats TO GROUP database_writers;
GRANT SELECT ON staging.f_lnrt_param_summary_stats TO GROUP etl_readers, GROUP astronauts, GROUP knewton_devs, GROUP bi_tools;

CREATE TABLE stg_rigel.f_lnrt_param_summary_stats(
    subgraph_id         CHAR(36),
    parameter_name      CHAR(100),-- speed_r, speed_q etc
    kl_dvg              FLOAT8, -- the value of kl divergence
    -- Over time we can add more stats
    time_from           TIMESTAMP,  -- Will contain the start time stamp after which the param was measured
    time_to             TIMESTAMP, -- Will contain the end time stamp before which the param was measured
    time_slice_name     CHAR(100), -- Will contain the representative name of the time slice(last 1 week, last 1 month etc)

-- Date and time synthetic keys for faster join
    time_from_date_id   INT,
    time_to_date_id     INT,
    time_from_time_id   INT,
    time_to_time_id     INT
);
GRANT SELECT, INSERT, DELETE, UPDATE ON stg_rigel.f_lnrt_param_summary_stats TO GROUP database_writers;
GRANT SELECT ON stg_rigel.f_lnrt_param_summary_stats TO GROUP etl_readers, GROUP astronauts, GROUP knewton_devs, GROUP bi_tools
