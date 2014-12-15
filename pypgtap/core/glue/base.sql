SET client_min_messages TO WARNING;
CREATE OR REPLACE LANGUAGE plpythonu;

-- TODO(Sid): Lets move these to some sort of setup function that users can
-- call.
\ir pgtap.sql


-- This simply sets the project_dir key global data directory with the
-- argument. The project_dir must be an existant absolute path

CREATE OR REPLACE FUNCTION _set_pypgtap_key_value(key varchar, value varchar)
RETURNS VOID AS $$
BEGIN
    EXECUTE 'CREATE TABLE IF NOT EXISTS __pypgtap_data
            ( name varchar UNIQUE, value varchar )';
    EXECUTE 'DELETE FROM __pypgtap_data where name=' ||
                quote_literal($1);
    EXECUTE
            'INSERT INTO __pypgtap_data (name, value)
            VALUES ('
                        || quote_literal($1) || ',' || quote_literal($2) ||
            ')';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION _get_pypgtap_key(key varchar)
RETURNS varchar AS $$
DECLARE
    ret varchar;
BEGIN
    EXECUTE 'SELECT value FROM __pypgtap_data where name='
                    || quote_literal($1) INTO  ret;
    RETURN ret;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION set_project_path(project_dir varchar)
RETURNS VOID AS $$
BEGIN
        EXECUTE 'SELECT _set_pypgtap_key_value('
                    || quote_literal('project_dir')  ||','
                    || quote_literal($1) || ')';
END;
$$ LANGUAGE plpgsql;

-- This simply gets the project_dir from the PG global data directory
CREATE OR REPLACE FUNCTION get_project_path()
RETURNS varchar AS $$
DECLARE
    ret varchar;
BEGIN
    EXECUTE 'SELECT _get_pypgtap_key('
                    || quote_literal('project_dir') || ')' INTO  ret;
    RETURN ret;
END;
$$ LANGUAGE plpgsql;

-- This fix is the secret sauce for getting plpython in postgres to be aware of
-- the virtualenv you started it from so that it may find pypgtap libs.
-- The set_virtual_env is called before the tests beginIt is
-- called with the path of the activate script typically from
-- pypgtap_testing.PyPGTAPTestManager._activate_virtual_env
CREATE OR REPLACE FUNCTION set_virtual_env_dir(venv text)
RETURNS VOID AS $$
BEGIN
        EXECUTE 'SELECT _set_pypgtap_key_value('
                    || quote_literal('venv_dir') ||','
                    || quote_literal($1) ||
                    ')';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION get_virtual_env_dir()
RETURNS varchar AS $$
DECLARE
    ret varchar;
BEGIN
    EXECUTE 'SELECT _get_pypgtap_key('
                    || quote_literal('venv_dir') || ')' INTO  ret;
    RETURN ret;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION activate_virtual_env()
  RETURNS void AS
$BODY$
        venv_dir_data = plpy.execute('SELECT get_virtual_env_dir() as venv_dir')
        venv = venv_dir_data[0]['venv_dir']
        import os, sys, subprocess, shlex
        if sys.platform in ('win32', 'win64', 'cygwin'):
            activate_this = os.path.join(venv, 'Scripts', 'activate_this.py')
        else:
            if 'PATH' not in os.environ:
                cmd_list = shlex.split('echo -n $PATH')
                p = subprocess.Popen(cmd_list, stdout=subprocess.PIPE, shell=True)
                (stdoutdata, stderrdata) = p.communicate()
                log_msg = "Command output: {}\nCommand Error:{}".format(stdoutdata, stderrdata)
                print "Command output: {}\nCommand Error:{}".format(stdoutdata, stderrdata)
                if p.returncode != 0:
                    raise OSError(
                        "Error in executing {}. Process output:\n{}".format(str(cmd_list), log_msg),
                        rc=p.returncode)
                os.environ['PATH'] = stdoutdata
            activate_this = os.path.join(venv, 'bin', 'activate_this.py')
            exec(open(activate_this).read(), dict(__file__=activate_this))
$BODY$
LANGUAGE plpythonu;

CREATE EXTENSION if not exists dblink;
