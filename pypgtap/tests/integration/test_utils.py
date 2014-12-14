import unittest
import os

from pypgtap.core.test_kit.utils import ExecuteQueryHelper
import pypgtap.core.test_kit.postgres_env as pe

from pypgtap.core.test_kit import utils

class TestExecuteQueryHelper(unittest.TestCase):

    """Test the ExecuteQueryHelper"""

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

    @ExecuteQueryHelper(user_name=os.environ.get('USER'))
    def test_execute_query_helper(self, cursor):
        """
        Test an arbitrary SQL table to test if the ExecuteQueryHelper
        works.
        """
        self.assertNotEquals(cursor, None)
        cursor.execute("CREATE TABLE test_table (id varchar);")
        cursor.execute("INSERT INTO test_table (id) VALUES (%s)", ('foo',))
        cursor.execute("SELECT * FROM test_table;")
        results = cursor.fetchall()
        self.assertEquals(1, len(results))
        for res in results:
            for id_ in res:
                self.assertEquals(id_, 'foo')
