"""
Here shall go the integration tests that you shall fire off to test any
regressions you might introduce when working on pypgTAP. Do remember that you
should have postgresql 9.3 with python support installed to get this to work!
"""
import logging
import os
import tempfile
import unittest

import pypgtap.core.test_kit.postgres_env as pe
from pypgtap.core.test_kit.utils import\
    ExecuteQueryHelper, PG_HARNESS_DATA_DIR
from pypgtap.core.test_kit.pypgtap_testing import PyPGTAPTestManager, _execute_sql_script
from pypgtap.tests.integration import BaseHarnessTestManager
from pypgtap.core.test_kit.pypgtap_error import PyPGTAPSubprocessError


_logger = logging.getLogger(__name__)


class HarnessTest(unittest.TestCase):
    """
    Test if the harness can be started and stopped programaticaly only
    """
    def test_harness_start_stop(self):
        """
        Starts and stops the test harness. Assumes the postgres installation
        is in place.
        """
        try:
            pe.start_postgres_harness()
            self.assertTrue(pe.is_harness_running())
        finally:
            # No matter what the outcome we must attempt to stop the harness.
            pe.stop_postgres_harness()
            self.assertFalse(pe.is_harness_running())
            self.assertFalse(os.path.exists(PG_HARNESS_DATA_DIR))


class PyPGTAPTestManagerIntegration(BaseHarnessTestManager):
    """
    This class has tests that will test the aspects of pypgTAPTestManager
    class in pypgtap.core.test_kit.pypgtap_testing. Most importantly
    it tests if the harness was bootstrapped properly.
    It will setup the test harness and tear it down as needed.
    """
    @ExecuteQueryHelper()
    def _internal_base_script_verify(
            self, under_test_function, cursor):
        """
        Internal utility to verify that an arbitrary function,
        under_test_function, exists as a stored procedure. We use this typically
        to test the successful bootstrapping of the test harness. Returns True
        if the said function is found else False.

        :param str under_test_function: The function you want to check.
        :param psycopg2.cursor cursor : Used to execute queries
        :return: Returns true if the said function is found else not.
        :rtype: int
        """
        self.assertNotEquals(cursor, None)
        self.assertNotEquals(under_test_function, None)
        sql_query = \
            "select 1 from pg_proc where proname=%s"
        cursor.execute(sql_query, (under_test_function,))
        results = cursor.fetchall()
        flattened_result = [i for i, in results if i]
        return len(flattened_result) == 1

    def test_base_scripts_execution(self):
        """
        If the base scripts were executed by the RsTAOtestManager._init_pgtap().
        """
        with PyPGTAPTestManager() as manager:
            self.assertEquals(
                manager._is_initialized, True,
                msg='The test manager was not initialized properly')
            self.assertTrue(self._internal_base_script_verify(
                under_test_function='set_project_path'),
                msg='get_project_path function not found. Perhaps you '
                    ' intended to change or remove this in which case you'
                    ' should fix this test')
            self.assertTrue(self._internal_base_script_verify(
                under_test_function='get_project_path'),
                msg='get_project_path function not found. Perhaps you '
                    ' intended to change or remove this in which case you'
                    ' should fix this test')

    def test_setting_project_dir(self):
        """
        Tests if the project directory is stored properly. We create a mock
        directory and test if its set properly.
        """
        mock_project_path = tempfile.mkdtemp()
        with PyPGTAPTestManager() as manager:
            manager._set_project_dir(mock_project_path)
            results = manager.get_project_dir()
            self.assertEquals(
                len(results), 1,
                msg='The project dir was not set properly!')
            self.assertEquals(
                results[0], mock_project_path,
                msg='The actual project directory differ from one under test')
        os.rmdir(mock_project_path)

    def test_fail_setting_project_dir(self):
        """
        Tries setting the project directory to a path that does not exist and
        fails expectedly on it.
        """
        with PyPGTAPTestManager() as manager:
            # Note that because it comes through the ExecuteQueryHelper
            # the exception asserted for is not the same thats thrown by
            # the method itself(IOError).
            with self.assertRaises(IOError):
                manager._set_project_dir('path_that_does_not_exist')

    def test_failing_command(self):
        with self.assertRaises(PyPGTAPSubprocessError) as error_info:
            _execute_sql_script("something that will not execute")
        _logger.info("Failing Command Output {}".format(error_info.exception.msg))
        # What the output looks like
        self.assertTrue('psql: FATAL:  role "will" does not exist' in error_info.exception.msg)
        self.assertNotEqual(1, error_info.exception.rc)
        self.assertEquals("something that will not execute", error_info.exception.cmd)
