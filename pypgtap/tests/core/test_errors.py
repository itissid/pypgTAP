import unittest

from pypgtap.core.test_kit.pypgtap_error import PyPGTAPSubprocessError


class ErrorTest(unittest.TestCase):

    """Tests the pypgtap_errors modules"""

    def test_pypgtap_subprocess_error(self):
        """
        Test the PyPGTAPSubprocessError __init__ and its data
        """
        with self.assertRaises(PyPGTAPSubprocessError) as info:
            raise PyPGTAPSubprocessError(
                'Error encountered', rc=1, cmd='testcommand -e')
        exception = info.exception
        self.assertEqual(exception.msg, 'Error encountered')
        self.assertEqual(exception.rc, 1)
        self.assertEqual(exception.cmd, 'testcommand -e')
