"""
This module contains errors and exceptions for the pypgtap Core API. Again the
core API is in the package pypgtap.core
"""

class PyPGTAPSubprocessError(Exception):
    """
    There was no class that was storing the return code and the command that
    failed as a part of its data, so I created one. This is useful with all the
    subprocess calls going around the framework, where you can use this.
    """

    def __init__(self, message, rc, cmd):
        super(PyPGTAPSubprocessError, self).__init__(message, rc, cmd)
        if not isinstance(rc, int):
            raise ValueError('return code must be an integer')
        if not (cmd and isinstance(cmd, basestring)):
            raise ValueError('The cmd argument must be a non empty string')
        self.msg = message
        self.rc = rc
        self.cmd = cmd

    def __str__(self):
        return 'A framework subprocess command failed. {}\n{}'.format(
            self.msg, 'The Return Code was: {}. Command args '
               'to subprocess.call were {}'.format(self.rc, self.cmd))
