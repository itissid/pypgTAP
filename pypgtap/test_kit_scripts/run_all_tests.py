"""
The purpose of this script is to be able to run the tests in etl projects
projects. You can run multiple project tests by just repeating  the "-w"
argument to the script as argument.

TODO(Sid): The output of the tests must be captured and sent to a TAP
parser because remember that underlying TAP generating tests don't return
exceptions or -1 return code(See http://testanything.org/).
To achieve this there is a jenkins TAP plugin that can be used for this
purpose:
    https://wiki.jenkins-ci.org/display/JENKINS/TAP+Plugin
Another implementation would be to have the callee send the output to a
TAP parser in python which will then just signal failure were any tests
to fail.
"""

from optparse import OptionParser

from pypgtap.core.test_kit.pypgtap_testing import PyPGTAPTestManager
from pypgtap.lib.tap import tapOutputParser


def get_cli_options():
    """
    Returns the result of parser.parse_args() where parser is of type
    OptionParser.
    """
    usage = "usage: %prog options"
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-w", "--project_dirs", dest="project_dirs",
        help=(
            'specify the project dirs: -w foo -w bam ... default is the pwd '
            'from where you run the script.'),
        action="append")
    return parser.parse_args()


def run_tests(project_dirs):
    """
    Takes a list of valid project directories and runs the tests using PyPGTAPTestManager
    """
    if project_dirs is None:
        raise ValueError(
            'must supply project directories or test scripts as argument')

    # This will actually create all the functions that pgtap
    # needs. After this you can actually run the tests
    # Now just execute each of the projects
    for w in project_dirs or []:
        with PyPGTAPTestManager() as manager:
            outputs = manager.execute_project_test(w)
            failed_tests = []
            print '{} project test summary:\n'.format(w)
            for i, test_output in enumerate(outputs):
                tapResult = tapOutputParser.parseString(test_output)[0]
                print test_output
                if len(tapResult.failedTests):
                    failed_tests.append(tapResult.failedTests)
            if failed_tests:
                raise ValueError('Failed Tests. See the TAP outputs above.')


def main():
    options, args = get_cli_options()
    run_tests(options.project_dirs)
