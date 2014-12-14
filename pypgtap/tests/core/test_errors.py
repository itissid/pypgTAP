import unittest

from pypgtap.core.test_kit.pypgtap_error import RsTAPSubprocessError


class ErrorTest(unittest.TestCase):

    """Tests the pypgtap_errors modules"""

    def test_pypgtap_subprocess_error(self):
        """
        Test the RsTAPSubprocessError __init__ and its data
        """
        with self.assertRaises(RsTAPSubprocessError) as info:
            raise RsTAPSubprocessError(
                'Error encountered', rc=1, cmd='testcommand -e')
        exception = info.exception
        self.assertEqual(exception.msg, 'Error encountered')
        self.assertEqual(exception.rc, 1)
        self.assertEqual(exception.cmd, 'testcommand -e')
