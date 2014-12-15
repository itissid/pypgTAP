"""
This test suite will test some real world ETL using pypgTAP. It will essentially
start the harness run ETL test using PyPGTAPManager and finally stop the
harness.
The tests are all present in the example/test/ folder and
can also be run on the CLI:

$ run_all_tests -w <Path to example/">

"""
import logging

from pypgtap.core.test_kit.pypgtap_testing import PyPGTAPTestManager
from pypgtap.tests.integration import BaseHarnessTestManager
from pypgtap.lib.tap import tapOutputParser

_logger = logging.getLogger(__name__)


class PyPGTAPETLIntegrationTest(BaseHarnessTestManager):
    """
    This integration test tests specific ETL queries
    in the example/ project project.
    """
    def test_hello_world(self):
        with PyPGTAPTestManager() as manager:
            output = manager.execute_project_test('example_project/', 'test_hello_world.sql')
            #  Only one test output
            self.assertEquals(1, len(output))
            tapResult = tapOutputParser.parseString(output[0])[0]
            _logger.info('* pypgTAP Test Output\n{}\n{}'.format(tapResult.summary(), output[0]))
            self.assertEquals(0, len(tapResult.failedTests))
            self.assertEquals(1, len(tapResult.passedTests))
