/**
* The idea here is to read a json file and copy it into a table you have
 * already created. The json_path_file should be either be absolute path or be
 * somewhere in the azkaban/Projects/ subdirectory ALL time stamps should be in
 * milliseconds.
 * If time stamp is not in milliseconds it should be a string that is a PG
 * compatible timestamp: '%Y-%m-%d %H:%M:%S'
 * An important thing:
 * This table uses the column order in json path file as the order in which data is filled no matter what the keys are in the data file.
*/
CREATE OR REPLACE FUNCTION copy_json(
    table_name varchar, json_file_name varchar, json_path_file_name varchar,
    convert_time_stamps boolean)
RETURNS boolean
AS $$
    import os, json
    import sys
    import datetime as dt
    if 'project_root' not in GD:
        raise ValueError(
            'expected project root in the Global dictionary you forget to include base.sql?')
    test_kit_relative_path = GD['test_kit_relative_path']
    project_root = GD['project_root']
    # Utility that hacks a solution to get some
    # libs that are needed by the json path parser

    def add_utils_to_path(project_root):
        """
        We need to bootstrap the sys.path so that we can find all the libs.
        Thats why this utility can't be anywhere else.
        """
        lib_dir = os.path.join(project_root, test_kit_relative_path, 'py_utils')
        if not os.path.exists(lib_dir):
            raise ValueError('Expected a lib dir in project_root {}'.format(project_root))
        sys.path.append(lib_dir)

    # Add utils to your project path
    add_utils_to_path(project_root)

    import utils
    # ... import them
    utils.append_libs(project_root, sys.path)

    from jsonpath_rw import parse as jp_parse

    # Now append rest of the libs
    json_file = open(os.path.join(project_root, json_file_name))
    json_path_file = open(os.path.join(project_root, json_path_file_name))

    redshift_json_path_json = json.load(
        json_path_file, object_hook = utils._decode_dict)
    data = []
    with json_file as lines:
        for line in lines:
            row_data = []
            for column, value in utils.parse_redshift_json_path(
                    redshift_json_path_json, json.loads(line)):
                # Hack for trying to guess if a field is time
                if 'time' in column and convert_time_stamps is True:
                    ts = utils.try_guess_and_convert_pg_timestamp(value)
                    row_data.append((column, ts))
                else:
                    row_data.append((column, value))

            statement = "insert into {table_name} values({values})".format(
                    table_name=table_name,
                    values=", ".join("'%s'"%s if isinstance(s, basestring) else "%s"%s for _, s in row_data))
            prep_statement = plpy.execute(statement)
$$ LANGUAGE plpythonu;

/*
 * In case the schema does not exist create it.
*/
CREATE OR REPLACE FUNCTION create_test_schema_if_not_exists(
    under_test_schema_name CHARACTER VARYING) RETURNS void
AS $$
DECLARE
    exists_result boolean;
BEGIN
    -- Now if the schema does not exist create it.
    EXECUTE 'SELECT EXISTS(SELECT 1 FROM information_schema.schemata
              WHERE information_schema.schemata.schema_name = ' ||
            quote_literal(under_test_schema_name) ||')'
    INTO exists_result;

    IF NOT exists_result
    THEN
        EXECUTE 'CREATE SCHEMA ' || under_test_schema_name;
        RAISE NOTICE 'Created schema %', under_test_schema_name;
    END IF;
END;
$$ LANGUAGE plpgsql strict;

-- Because there aint a dang method to do this!
CREATE OR REPLACE FUNCTION drop_table_if_exists(
        under_test_table_name CHARACTER VARYING,
        under_test_schema_name CHARACTER VARYING) RETURNS void
AS $$
DECLARE
   table_exists boolean;
BEGIN

    EXECUTE 'SELECT EXISTS(SELECT 1 FROM pg_catalog.pg_class c
        JOIN   pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE  n.nspname =' || quote_literal(under_test_schema_name) ||
        ' AND c.relname = ' || quote_literal(under_test_table_name) ||
        ' AND c.relkind = '|| quote_literal('r') || ')' into table_exists;
    IF table_exists
        THEN
            EXECUTE 'DROP TABLE ' || under_test_schema_name || '.' || under_test_table_name;
    END IF;
END
$$ LANGUAGE plpgsql strict;

CREATE OR REPLACE FUNCTION drop_tables_if_exists(
    under_test_tables character varying[], under_test_schema_name varchar)
RETURNS VOID
AS $$
DECLARE
 table_name character varying;
BEGIN
    foreach table_name in ARRAY under_test_tables
        LOOP
             PERFORM drop_table_if_exists(table_name, under_test_schema_name);
        END LOOP;
END
$$ LANGUAGE plpgsql strict;

-- SELECT debug() to insert a break point
-- anywhere.
CREATE OR REPLACE FUNCTION debug()
RETURNS VOID
AS $$
    import pdb
    pdb.set_trace()

$$ LANGUAGE plpythonu;


-- Execute a ddl statement in a string
CREATE OR REPLACE FUNCTION SETUP_DDL(
    setup_statement character varying)
RETURNS void
AS $$
BEGIN
    EXECUTE setup_statement;
END
$$ LANGUAGE plpgsql strict;

-- A hack to get around all the new additions for redshift in the ddl
-- statement.  What we really should do is recompile an edited postgresql
-- source that does some meaningful things for the new code.
CREATE OR REPLACE FUNCTION format_ddl(
    sql_module_file character varying)
RETURNS character varying
AS $$
    import re, os
    replace_dist_key = re.compile('(DISTKEY[^;\n,]*)', flags=re.I)
    replace_sort_key = re.compile('(SORTKEY[^;\n,]*)', flags=re.I)
    replace_diststyle = re.compile('(DISTSTYLE[^;\n,]*)', flags=re.I)
    replace_identity = re.compile('IDENTITY\(.*\)[^,\n;]*', flags=re.I)
    if 'project_root' not in GD:
        raise ValueError(
            'expected project root in the did you forget to include base.sql?')
    project_root = GD['project_root']
    sql_statement = ''.join(
        n for n in open(os.path.join(project_root, sql_module_file)).readlines())
    sql_statement =  replace_dist_key.sub('', sql_statement)
    sql_statement = replace_sort_key.sub('', sql_statement)
    sql_statement = replace_diststyle.sub('', sql_statement)
    sql_statement = replace_identity.sub('', sql_statement)
    return sql_statement
$$ LANGUAGE plpythonu;
