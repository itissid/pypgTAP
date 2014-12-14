import unittest

import pypgtap.core.test_kit.postgres_env as pe


class BaseHarnessTestManager(unittest.TestCase):
    """
    If you want to start or stop a harness extend this class.
    """
    def setUp(self):
        """
        Sets up the test harness

        """
        pe.start_postgres_harness()

    def tearDown(self):
        """
        Tear down the test harness
        """
        pe.stop_postgres_harness()
