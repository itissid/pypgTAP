"""
This contains a part of the core API that is the glue that helps in constructing
and managing the pypgTAP test environment. Its responsibility is managing the
temporary postgres environment that runs the test on local and ci(jenkins).
It just wraps the pg_ctl interface that is consistent across dev ci and platforms.
See: http://www.postgresql.org/docs/9.3/static/app-pg-ctl.html
for more.
Couple of important things:

* The USER variable should be in the list of env variables
* The pg_ctl, createdb command should be present in the PATH or reachable.
* The output of the command is not redirected so it will go to stdout/stderr.
"""
import os
import subprocess
import sys
import shutil
import shlex

from pypgtap.core.test_kit.utils import pre_create_harness_data_dir
from pypgtap.core.test_kit.utils import PG_HARNESS_DATA_DIR
from pypgtap.core.test_kit.pypgtap_error import PyPGTAPSubprocessError


@pre_create_harness_data_dir
def start_postgres_harness(user_name=None):
    """
    Using a writable PG_HARNESS_DATA_DIR we initialize a postgres process.

    :param str user_name: Typically the USER set in the underlying
        environment firing the query.
    :raises pypgTAPSubprocessError: if there was an error in the underlying
        subprocess call to pg_ctl.
    :raises EnvironmentError: If USER environment variable is not present
    """
    user_name = os.environ.get('USER', user_name)
    if user_name is None:
        raise EnvironmentError('USER env variable not set!')

    if len(os.listdir(PG_HARNESS_DATA_DIR)) > 0:
        raise EnvironmentError(
            'The harness dir is not empty, did you forget to run stop_harness?')

    if not os.path.exists(PG_HARNESS_DATA_DIR):
        raise ValueError('data dir {} for PG does not exist'.format(
            PG_HARNESS_DATA_DIR))
    cmd_lst = shlex.split("pg_ctl initdb -w -D {}".format(PG_HARNESS_DATA_DIR))
    rc1 = subprocess.call(cmd_lst, stdout=sys.stdout, stderr=sys.stderr)
    if rc1 != 0:
        # clean the data dir so that we can start afresh.
        # since the harness has not started yet this is fine
        shutil.rmtree(PG_HARNESS_DATA_DIR)
        raise PyPGTAPSubprocessError(
            'There was an error initializing the postgres DB.',
            rc=rc1, cmd=str(cmd_lst))
    # Note to self(sid):
    # A few of the options like -h and -k are present to guard config options
    # that postgres pick things from the postgres.conf file causing issues in
    # starting the process.
    # A better way to handle this may be to configure the options at install
    # time and standardize them there.
    # But we have to engineer scripts that works for installers like apt and
    # brew.
    # Maybe some postgres admin can help me iron out all the additional options
    # that make the subprocess call robust?(Psst! Review request here)
    cmd_lst = shlex.split(
        "pg_ctl start -w -D {} -o '-h localhost -k /tmp'".format(
            PG_HARNESS_DATA_DIR))

    rc2 = subprocess.call(cmd_lst, stdout=sys.stdout, stderr=sys.stderr)
    if rc2 != 0:
        # clean the data dir so that we can start afresh.
        # since the harness failed to start this is fine
        shutil.rmtree(PG_HARNESS_DATA_DIR)
        raise PyPGTAPSubprocessError(
            'There was an error starting the postgres DB.',
            rc=rc2, cmd=str(cmd_lst))

    # Finally create the default database
    try:
        create_default_db(user_name)
    except Exception as e:
        print ('Caught exception while creating default db'
                ' If the harness is still running you'
                ' SHOULD shut it down using stop_harness')
        raise e


@pre_create_harness_data_dir
def stop_postgres_harness():
    """
    Stop a postgres test harness. Also cleans up the data dir of the underlying
    harness. If this process is invoked and the harness is not running it cleans
    up the data dir only.

    :raises PyPGTAPSubprocessError: if there was an error in the underlying
        subprocess call to pg_ctl.
    """
    try:
        if is_harness_running():
            cmd_lst = shlex.split("pg_ctl stop -w -D {}".format(
                PG_HARNESS_DATA_DIR))
            rc = subprocess.call(cmd_lst, stdout=sys.stdout, stderr=sys.stderr)
            if rc != 0:
                raise PyPGTAPSubprocessError(
                    'There was an issue stopping postgres.',
                    rc=rc, cmd=str(cmd_lst))
    finally:
        shutil.rmtree(PG_HARNESS_DATA_DIR)


###### Helper Utilities ########


def is_harness_running():
    """
    Determines the status of an underlying harness and return True if its
    running and False otherwise.

    :raises PyPGTAPSubprocessError: if there was an error in the underlying
        subprocess call to pg_ctl.
    """
    if not os.path.exists(PG_HARNESS_DATA_DIR):
        return False
    cmd_lst = shlex.split("pg_ctl status -D {}".format(PG_HARNESS_DATA_DIR))
    rc1 = subprocess.call(cmd_lst, stdout=sys.stdout, stderr=sys.stderr)
    if rc1 == 0:
        return True
    elif rc1 == 3:
        return False
    else:
        raise PyPGTAPSubprocessError(
            'There was an issue in determining the postgres process status.'
            ' See: http://www.postgresql.org/docs/9.3/static/app-pg-ctl.html',
            rc=rc1, cmd=str(cmd_lst))


def create_default_db(user_name):
    """
    We need to create a default database because the tests rely on using the
    database created by the user who made it. When PG installs it has a role
    which is the name of the user that installed the database and starts the
    process. A few things to keep in mind:

    1. We create the database that is same as the given user_name arg. Note
    that this "should" be the same as the user that actually installs the DB and
    also starts the database process. The function does not assert on this as
    its not technically invalid to do this. But calling it in the former way,
    generally assures that the user has the privileges to create the database.

    2. Also additional assumptions may hold as per documentation:
    http://www.postgresql.org/docs/9.3/static/app-createdb.html

    :param str user_name: The user name. Typically the USER argument set
        in the environment.

    :raises PyPGTAPSubprocessError: if the underlying command to createdb
        fails
    """
    if not (user_name and isinstance(user_name, basestring)):
        raise ValueError('User name arguments must be non-empty string')
    cmd_lst = shlex.split(
        "createdb -U {} -h localhost {}".format(user_name, user_name))
    rc = subprocess.call(cmd_lst, stdout=sys.stdout, stderr=sys.stderr)
    if rc != 0:
        raise PyPGTAPSubprocessError(
            'There was an issue creating the default DB.',
            rc=rc, cmd=str(cmd_lst))
