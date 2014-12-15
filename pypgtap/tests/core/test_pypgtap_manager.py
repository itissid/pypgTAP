"""
Here in go the unit tests for the PyPGTAPTestManager
in the pypgtap.core.test_kit.pypgtap_testing module.

"""
import itertools as its
import os
import unittest
from mock import patch

from pypgtap.core.test_kit import pypgtap_testing as under_test


class PyPGTAPTestManager(unittest.TestCase):

    """Unit tests for the PyPGTAPManager"""
    # These scripts are expected. If you add more scripts or delete one the test
    # will detect a regression.
    expected_base_scripts = ['base.sql', 'pgtap.sql', 'utils.sql']

    def test_execute_project_tests(self):
        """
        This test tests if the PyPGTAPTestManager runs the tests by calling the
        execute_project_test() method. It mocks out the actual execution
        of the sql scripts and the setting of the project directory.
        It asserts if the mock of those methods get called.
        """
        with patch.object(under_test, '_execute_sql_script') as mock_executor:
            with under_test.PyPGTAPTestManager() as manager:
                with patch.object(manager, '_set_virtual_env_dir'):
                    with patch.object(manager, '_set_project_dir') \
                            as mock_wf_setter:
                        manager.execute_project_test('example')
                        call_arg_flattener = lambda mock: list(
                            its.chain(*its.chain(*mock.call_args_list))
                        )
                        sql_scripts = its.imap(os.path.basename, call_arg_flattener(mock_executor))
                        self.assertIn('test_hello_world.sql', sql_scripts)
                        actual_project_dirs = call_arg_flattener(mock_wf_setter)
                        self.assertEqual(1, len(actual_project_dirs))
                        self.assertEquals(
                            os.path.abspath('example'), actual_project_dirs[0])

   def test_is_valid_project_test_dir(self):
        """
        Tests under_test.PyPGTAPTestManager.is_valid_project_test_dir with a
        project test directory containing a test(s) directory and then with one
        that does not. In the former case the test returns a true and in the
        latter case it returns an exception.
        """
        under_test_manager = under_test.PyPGTAPTestManager()
        self.assertTrue(under_test_manager.is_valid_project_test_dir('example'))
        project_dir = 'pypgtap/core/'
        # Match the error output with a regular expression.
        with self.assertRaisesRegexp(
                IOError, 'Project dir {} is not a valid ETL directory.*'.format(project_dir)):
            under_test_manager.is_valid_project_test_dir(project_dir)

    def test_get_test_scripts(self):
        """
        under_test.PyPGTAPTestManager.get_test_scripts should only return test
        files that satisfy test_*.sql pattern.
        """
        under_test_manager = under_test.PyPGTAPTestManager()
        test_scripts = [
            i for i in under_test_manager.get_test_scripts('example')]
        self.assertEquals(7, len(test_scripts))
        self.assertIn('example/test/ddl/test_hello_world.sql', test_scripts)
        self.assertIn('example/test/ddl/test_format_sql_module.sql', test_scripts)
        self.assertIn('example/test/ddl/test_copy_json.sql', test_scripts)
        self.assertIn('example/test/ddl/test_table_names.sql', test_scripts)
        self.assertIn('example/test/dml/test_parse_assessment_log_table.sql', test_scripts)
        self.assertIn('example/test/dml/test_compatibility_functions.sql', test_scripts)
        self.assertIn('example/test/dml/test_assessment_histograms.sql', test_scripts)

        test_scripts = [
            i for i in under_test_manager.get_test_scripts('pypgtap')]
        self.assertEquals(0, len(test_scripts))

    def test_base_scripts_inclusion(self):
        """
        This test will test the mocked out execution of of the base scripts that
        bootstrap the pypgTAP harness. We just test the discovery of the scripts
        and make sure they don't differ from the expected list:
        self.expected_base_scripts; we also mock the execution part out. See the
        integration tests for the execution part as well.
        """
        with patch.object(under_test, '_execute_sql_script') as mock_executor:
            under_test_test_manager = under_test.PyPGTAPTestManager()
            with patch.object(under_test_test_manager, '_set_virtual_env_dir'):
                under_test_test_manager._init_pgtap()
                # At least the base.sql and the pgtap.sql scripts
                self.assertTrue(mock_executor.call_count >= 2)
                # Flatten and get the base name of the scripts!
                sql_scripts = list(
                    its.imap(os.path.basename, its.chain(
                            *its.chain(*mock_executor.call_args_list)))
                )
                extra_scripts = set(sql_scripts).difference(self.expected_base_scripts)
                fewer_scripts = set(self.expected_base_scripts).difference(sql_scripts)
                self.assertEquals(
                    len(extra_scripts), 0,
                    msg='{} extra script(s) detected, expected only {}'.format(
                        extra_scripts, self.expected_base_scripts))

                self.assertEquals(
                    len(fewer_scripts), 0,
                    msg='{} fewer script(s) detected, expected only {}'.format(
                        fewer_scripts, self.expected_base_scripts))
