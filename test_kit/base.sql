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
SET client_min_messages TO WARNING;
CREATE OR REPLACE LANGUAGE plpythonu;
-- Import these are in the public schema of what ever data
-- base you are connected to.
DROP SCHEMA IF EXISTS staging CASCADE;
DROP SCHEMA IF EXISTS stg_rigel CASCADE;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS stg_rigel;
\ir pgtap.sql
-- The project root dir should be set correctly before firing the tests.
-- In this function we need to make sure the relative path of the
-- test kit is set to a directory that exists
CREATE OR REPLACE FUNCTION set_project_root_and_test_kit_path(
        project_root text, test_kit_rel_path text)
RETURNS boolean
AS $$
        import os
        import sys
        utils_dir_name = 'py_utils' # DO not change!
        # TODO(Sid): Add logger every where
        if project_root is None or project_root.strip() == '':
                raise ValueError('project root cannot be empty')
        if not os.path.exists(project_root):
                raise ValueError('The Project root does not exist')
        GD['project_root'] = project_root # Global dictionary with static data

        # Arguments should not be reassigned
        # See rules: http://www.postgresql.org/docs/9.3/static/plpython-funcs.html
        if test_kit_rel_path is None:
                _test_kit_relative_path = '../rsTAP/test_kit'
        else:
            _test_kit_relative_path = test_kit_rel_path
        relative_root = os.path.join(project_root, _test_kit_relative_path)
        if not os.path.exists(relative_root):
                raise ValueError(
                        'The relative root path to the test kit does not exist: {}'
                        ' Please follow the README to set up the project'.format(relative_root))
        GD['test_kit_relative_path'] = _test_kit_relative_path

        # We need to bootstrap the sys.path so that we can find all the libs.
        # Thats why this utility cannot be factored out

        # These are user defined libraries in the test kit
        custom_lib_dir = os.path.join(
                project_root, _test_kit_relative_path, utils_dir_name)
        if not os.path.exists(custom_lib_dir):
            raise ValueError(
                'Cant find custom lib dir {}'.format(custom_lib_dir))
        sys.path.append(custom_lib_dir)
        # These are 3rd party libraries submoduled into the testkit
        common_lib_dir = os.path.join(
                project_root, _test_kit_relative_path, 'lib')
        if not os.path.exists(common_lib_dir):
            raise ValueError(
                'Cant find common lib dir {}'.format(custom_lib_dir))

        # Finally we can use utilities in the path
        import utils
        # ... import them. dont forget to git clone these libs
        utils.append_libs(
            project_root, os.path.join(_test_kit_relative_path, 'lib'), sys.path)

        return True
$$ LANGUAGE plpythonu;

-- This is the path of the test_kit relative to
-- the project root from where the test is invoked.
SELECT set_project_root_and_test_kit_path(:'project_root', :'test_kit_relative_path');

-- Also give the current ROLE Access to the public
-- schema where all these??

-- This was created because we need to create
-- database commands from a function.
-- TODO(Sid): This spits out a warning
CREATE EXTENSION if not exists dblink;

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
