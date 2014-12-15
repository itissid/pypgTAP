"""
This contains a part of the core API that helps in
bootstrapping the pypgTAP test harness and executing tests on it.
The running state of the harness is not managed by this module.
In addition it also contains utilities to execute sql scripts.
"""
import logging
import os
import pkg_resources
import subprocess
import shlex
import sys

from pypgtap.core.test_kit.pypgtap_error import PyPGTAPSubprocessError
from pypgtap.core.test_kit.utils import ExecuteQueryHelper

_logger = logging.getLogger(__name__)


def _execute_sql_script(sql_script):
    """
    Execute any psql script that is postgres compatible. This is used internally
    only by this module(See NOTE below).

    :param str sql_script: A string that is an sql scripts that people want to
        execute in their tests. Typically these are your not just your DDL and
        DML files but also psql files.
    :return: A byte string from the successful execution of the process. If the underlying command
        fails with a non zero exit code a PyPGTAPSubprocessError is raised
    :rtype: str
    :raises PyPGTAPSubprocessError: if the underlying subprocess call to execute
        the script fails.

    NOTE: This function is intended to be used by PyPGTAPTestManager.
    PyPGTAPTestManager reads the contents of the project_dir test directory and calls
    this method to execute the scripts. In the wild this execution is done only
    from our ci tests. So SQL injection is possible if you have managed to
    upload a malacious project_dir project and created a ci test to execute it, but
    then you have bigger problems.
    """

    cmd_lst = shlex.split(
        "psql -P format=unaligned -P pager -t -v QUIET=1 "
        "-v ON_ERROR_STOP=true -v ON_ERROR_ROLLBACK=1 -q -Xf {}".format(sql_script))
    p = subprocess.Popen(cmd_lst, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (stdoutdata, stderrdata) = p.communicate()
    _logger.debug("Command output {}".format(stdoutdata))
    if p.returncode != 0:
        raise PyPGTAPSubprocessError(
                "Error executing a sql script. Process Output(may be empty): %s" % stderrdata,
                rc=p.returncode, cmd=str(sql_script))
    return stdoutdata


class PyPGTAPTestManager(object):
    """
    This class takes care of bootstrapping the pypgTAP harness with pgtap and
    whatever custom sql scripts you have in the project. It also takes care of
    executing the tests in the project_dir directory when you call the
    execute_project_test() function. Under the hood this class first
    bootstraps the harness by creating stored procedures in the temporary
    postgres environement set up by the postgres_env module.

    *This class is not responsible for cleaning up the stored procedures; That
    is done automatically when the harness is stopped.*

    Here is how you use this class. It's a Context Manager pypgtap tests:

    >>> with PyPGTAPTestKitManager() as r: # This bootstraps the started harnes
    ...    r.execute_project_test(project_dir)
    ...    # Execute the tests (duh!)

    You can even reuse the manager object again and again; It's perfectly safe
    to do so to execute tests in multiple project directories. You should
    however not create multiple objects of this class.

    TODO(Sid): Maybe we can enforce the singleton(ish) behavior so API is not
    misused? Till then this is:
    *Not Thread Safe*
    """
    def __init__(self):
        self._is_initialized = False

    def __enter__(self):
        if self._is_initialized is False:
            self._init_pgtap()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        We don't need any cleanup at this point. But we propagate exceptions
        """
        return False

    def execute_project_test(self, project_dir, test_file=None):
        '''
        Execute the given tests in a project_dir directory. If there is a
        test(s)/ directory then the method looks for test_*.sql files in it.
        If there are test scripts it goes ahead and executes them.

        :param str project_dir: The project directory.
        :raises IOError: If the project_dir is not present or accessible
            from the current path. Or if there is no test/tests directory in
            the project_dir dir Or if test_file was not present in the test
            directory in project_dir
        :param str test_file: If this argument is given only that test is run.
            This argument is the location of the test file relative to
            project_dir/test(s)/. For example if the test file is located
            in my_project/tests/ddl/my_first_test.ddl. The this param is
            'ddl/my_first_test.sql'
        :return: A list of TAP outputs
        :rtype: list[str]
        :raises PyPGTAPSubprocessError: If there is an error in executing the
            underlying script
        '''
        if not os.path.exists(project_dir):
            raise IOError(
                'Project dir: {} does not exist'.format(project_dir))
        # Next validate if its a valid project dir.
        # See docs of called method for validity criteria.
        if not self.is_valid_project_test_dir(project_dir):
            _logger.warn(
                'No tests found to exist in project dir {}'.format(
                    project_dir))
            return
        sub_dirs = os.listdir(project_dir)
        test_dir = os.path.join(
            project_dir, 'test' if 'test' in sub_dirs else 'tests')

        # Your test must be in the test_dir dir!
        if (test_file is not None
                and not os.path.exists(os.path.join(test_dir, test_file))):
            raise IOError('Test file {} not found in test dir {}'.format(
                test_file, test_dir))

        # Let the test infrastructure be aware of the project directory.
        self._set_project_dir(os.path.abspath(project_dir))

        self._set_virtual_env_dir()
        # Finally execute each of the test scripts OR if you asked for one
        # we execute that.
        test_output = []
        for test in self.get_test_scripts(test_dir):
            if test_file is None or test.endswith(test_file):
                p = _execute_sql_script(test)
                test_output.append(p)
            else:
                _logger.warn(
                    'Ignoring {} test, because {} test'
                    ' was specifically requested'.format(test, test_file))
        return test_output

    def is_valid_project_test_dir(self, project_dir):
        """
        checks if there are any test_*.sql files in project_dir
        If yes it returns True else false

        :param str project_dir: A project directory possibly containing tests
        """
        sub_dirs = os.listdir(project_dir)
        if 'test' not in sub_dirs and 'tests' not in sub_dirs:
            raise IOError((
                'Project dir {} is not a valid ETL directory.'
                'It does not have a test/ or tests/ directory').format(
                    project_dir))
        test_dir = os.path.join(
            project_dir, 'test' if 'test' in sub_dirs else 'tests')
        return any(self.get_test_scripts(test_dir))

    def get_test_scripts(self, test_dir):
        """
        A generator to get the test_*.sql files given a test_dir.  directory. If
        the test_dir does not exist this function just returns silently with
        None.

        >>> for file  in get_test_scripts(my_dir):
        ...        print 'SQL test file:{}'.format(file)
        ...        # Do something with this file

        :param str test_dir: A string that represents a directory on your file
            system.
        :raises ValueError: If the test_dir argument is None.
        """
        if test_dir is None:
            raise ValueError('test_dir argument cannot be None')
        if len(os.listdir(test_dir)) > 0:
            for dir_name, sub_dir, files in os.walk(test_dir):
                for f in files:
                    if f.endswith('.sql') and f.startswith('test_'):
                        yield os.path.join(dir_name, f)

    @ExecuteQueryHelper()
    def _set_project_dir(self, project_dir, cursor):
        """
        Sets the project directory in an internal table. The path
        must exist and be absolute.
        When project test writers refer to data files, DDL/DML scripts they
        specify paths relative to the project directory. To qualify the paths
        this method adds the absolute path of the project directory to
        an internal table.
        """
        if not os.path.exists(project_dir):
            raise IOError('%s project directory does not exist' % project_dir)
        cursor.execute("SELECT set_project_path(%s);", (project_dir,))

    @ExecuteQueryHelper()
    def _set_virtual_env_dir(self, cursor):
        """
        If the virtual env has executed this program then set it for plpython to discover it later.
        """
        if sys.real_prefix:
            venv = sys.prefix
            cursor.execute("SELECT set_virtual_env_dir(%s);", (venv,))
        else:
            # You probably executed pypgtap from outside a virtualenv.  Generally you never want to
            # do that. This branch may be reachable in cases, if say you sudo pip installed pypgTAP
            _logger.warn(
                '** Seems like you are not using a virtualenv! This could end in an import error'
                'if pypgTAP library cannot be found. You have been warned **')

    @ExecuteQueryHelper()
    def get_project_dir(self, cursor):
        """
        Get the project directory in the postgres GD that was set by the
        _set_project_dir

        :param psycopg2._psycopg.cursor cursor: The cursor passed to this
            function by the ExecuteQueryHelper decorator
        :return: A list that has the project directory
        :rtype: list
        """
        cursor.execute("SELECT get_project_path();")
        result = cursor.fetchall()
        flattened_result = [r for r, in result if r]
        return flattened_result

    def _init_pgtap(self):
        """
        Internal call that executes the base.sql and other *.sql scripts needed
        by the pypgTAP framework.
        See the FAQ in the README for an elaborate explanation of how we read
        these in.
        """
        # Place all base scripts in the parent directory.  TODO(Sid): this is
        # fine for now but we may want to walk and find all the .sql files to
        # execute.
        pypgtap_init_scripts = pkg_resources.resource_listdir(
            'pypgtap.core', 'glue')
        base_script = 'base.sql'  # This script needs to be there!
        if base_script not in pypgtap_init_scripts:
            raise EnvironmentError(
                'base script %s not present in %s.' %
                base_script, ', '.join(pypgtap_init_scripts))

        # Execute all the other scripts, but execute the base script first
        # Does important setup before anything can and should execute.
        pypgtap_init_scripts.remove(base_script)
        abs_basescript_path = pkg_resources.resource_filename(
            'pypgtap.core.glue', base_script)
        _execute_sql_script(abs_basescript_path)

        for pypgtap_init_script in pypgtap_init_scripts:
            if pypgtap_init_script.endswith('.sql'):
                _execute_sql_script(pkg_resources.resource_filename(
                    'pypgtap.core.glue', pypgtap_init_script))
        self._is_initialized = True
