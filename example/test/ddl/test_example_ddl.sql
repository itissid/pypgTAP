\ir ../../../test_kit/base.sql
\ir ../../../test_kit/utils.sql

BEGIN;
    -- Genrally this is not needed unless someone has mucked around in the DB.
    -- All table creations are rolled back automatically.

    DROP GROUP IF EXISTS etl_readers;
    DROP GROUP IF EXISTS astronauts;
    DROP GROUP IF EXISTS knewton_devs;
    DROP GROUP IF EXISTS database_writers;
    DROP GROUP IF EXISTS bi_tools;
    CREATE GROUP etl_readers;
    CREATE GROUP astronauts;
    CREATE GROUP knewton_devs;
    CREATE GROUP database_writers;
    CREATE GROUP bi_tools;
    -- Your up is complete
    SELECT SETUP_DDL(format_ddl('ddl/example_ddl.sql'));

    -- We now make multiple assert statements about the data
    SELECT plan(5);
    SELECT tables_are(
        'staging',
        ARRAY[
        'lnrt_response_time',
        'f_lnrt_param_summary_stats'
        ]);
    SELECT tables_are(
        'stg_rigel',
        ARRAY[
        'f_lnrt_param_summary_stats'
        ]);
    SELECT table_privs_are(
        'staging',
        'lnrt_response_time',
        'database_writers',
        ARRAY['SELECT', 'INSERT', 'DELETE', 'UPDATE']);
    SELECT table_privs_are(
        'staging',
        'lnrt_response_time',
        'knewton_devs',
        ARRAY['SELECT']);

    SELECT table_privs_are(
        'stg_rigel',
        'f_lnrt_param_summary_stats',
        'etl_readers',
        ARRAY['SELECT']);
    -- Finish the tests and clean up.
    SELECT * FROM finish();
-- ROLLBACK WILL DELETE ALL THE TEST CHANGES TO THE
-- SCHEMA AND TO THE DB.
ROLLBACK;
