\set ECHO
\set QUIET 1
-- Turn off echo and keep things quiet.

-- Format the output for nice TAP.
\pset format unaligned
\pset tuples_only true
\pset pager

-- Revert all changes on failure.
\set ON_ERROR_ROLLBACK 1
\set ON_ERROR_STOP true
\set QUIET 1
-- Import these are in the public schema of what ever data
-- base you are connected to.
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS stg_rigel CASCADE;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS stg_rigel;
\ir pgtap.sql

-- The project root dir should be set correctly before firing the tests.
CREATE OR REPLACE FUNCTION set_project_root(project_root varchar)
RETURNS boolean
AS $$
        import os
        # TODO verify that the project root also exists.
        if project_root is None or project_root.strip() == '':
                raise ValueError('project root cannot be empty')
        print 'Project root: ', project_root
        if not os.path.exists(project_root):
                raise ValueError('The Project root does not exist')
        GD['project_root'] = project_root # Global dictionary with static data
        return True
$$ LANGUAGE plpythonu;
SELECT set_project_root(:'project_root');

-- Also give the current ROLE Access to the public
-- schema where all these??

-- This was created because we need to create
-- database commands from a function.
CREATE EXTENSION if not exists dblink;
