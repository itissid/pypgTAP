from functools import update_wrapper, wraps
import tempfile
import os
import logging
from logging import config as logging_config
import re

import psycopg2 as psyc

PG_HARNESS_DATA_DIR = os.path.join(
        tempfile.gettempdir(),
        '__rs_tap_process_flags')

_logger = logging.getLogger(__name__)


def pre_create_harness_data_dir(f):
    """
    Use as a decorator for pre creating the PG_HARNESS_DATA_DIR

        :param function f: The wrapped function.
    """
    @wraps(f)
    def inner(*args, **kwargs):
        if not os.path.exists(PG_HARNESS_DATA_DIR):
            os.makedirs(PG_HARNESS_DATA_DIR)
        return f(*args, **kwargs)
    return inner


class ExecuteQueryHelper(object):
    """
    A Convenient decorator that manages the closing and opening of connection to
    a postgreSQL datastore and passing that as an argument to the decorated
    function. This will help in executing some of the internal queries needed
    by the test harness.

    A note: When a user starts a harness, a db with his name is also created
    ; Thus this class uses the following connection string:

    psycopg.connect('dbname=%s user=%s'.format(user_name, user_name))
    By default the user name is chosen to be the USER environment variable.
    """
    def __init__(self, user_name=None):
        self.user_name = os.environ.get('USER', user_name)
        if not self.user_name:
            raise EnvironmentError(
                'Passed in a None user ID and the fallback $USER was also not '
                'set. You probably want to figure out who the user is '
                'because he will be used to connect to the temporary test '
                'data base')

    def __call__(self, function):
        self.function = function
        update_wrapper(self, function)

        def wrapped_f(*args, **kwargs):
            _logger.debug("Starting execute of %s" % (self.function.__name__))
            try:
                with psyc.connect('dbname={} user={}'.format(
                        self.user_name, self.user_name)) as conn:
                    with conn.cursor() as cursor:
                        res = self.function(*args, cursor=cursor, **kwargs)
                        conn.commit()
                        _logger.debug(
                            "Completed executing %s" % (self.function.__name__))
                        return res
            except Exception as exception:
                _logger.error('Exception was raised while executing %s' % (
                    self.function.__name__), exc_info=1)
                raise exception
        return wrapped_f


