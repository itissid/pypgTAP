"""
This module will contain python utilities called from plpython inside postgres
scripts. A lot of these are meant for just pypgTAP to do its magic so it can parse
load and prepare Redshift SQL to run it on the postgres harness. You should not
really call these from outside plpython methods; See utils.sql for examples.

TODO(Sid): Logger instantiation when called from inside the plpython methods is
not simple:

1. How to instantiate loggers using a config file every time one of these
functions is called? Because remember each plpython function gets its own python
interpreter and so one may have to save it all in the SD, GD:
    http://www.postgresql.org/docs/9.3/static/plpython-sharing.html

2. Another concern is how to instantiate the logger for unit tests.

Since these are internal functions(only called by plpython) we should be able to
decorate them with utilities that can instantiate the loggers.
"""
import logging
import os
import json
import jsonpath_rw
import yaml

from pypgtap.core.test_kit.utils import RegExLexers

_logger = logging.getLogger(__name__)


def copy_json(project_path, schema, table, json_file, json_path_file, database_accessor):
    """
    See the copy_json() documentation in utils.sql.

    :param str project_path: The project path reachable from postgres harness's python runtime.
    :param str table: The table where you want to insert the data.
    :param str json_file: The json data file, typically, relative to the project directory and
        should be some where reachable from postgres harness's python runtime.
    :param str json_path_file: File containing the JSONPath expressions.  Path requirements are
        same as the json_file argument.
    :param plpy database_accessor: The plpy module to access the database:
        http://www.postgresql.org/docs/9.3/static/plpython-database.html

    """
    plan = database_accessor.prepare(
        "SELECT column_name, data_type from information_schema.columns where"
        " table_schema = $1 and table_name = $2", ["text", "text"])
    rows = database_accessor.execute(plan, [schema, table])
    if not rows:
        raise ValueError('Seems there is no table {}.{}'.format(schema, table))
    columns = [row['column_name'] for row in rows]
    data_types = [row['data_type'] for row in rows]
    _logger.debug('Column order: %s' % columns)
    _logger.debug('Data types: %s' % data_types)
    # The data types of the columns
    data_type_format_str = ', '.join('$%d' % (i + 1) for i in xrange(len(data_types)))
    # Prepare a plan for executing efficiently
    plan = database_accessor.prepare(
        "INSERT into {}.{} values ({})".format(schema, table, data_type_format_str),
        data_types)
    # Get the function that will parse the json data.
    fn_json_path_parser = get_json_path_parser_fn(
        os.path.join(project_path, json_path_file))
    # Now open the json file
    with(open(os.path.join(project_path, json_file))) as json_file:
        for line in json_file:
            # Parse the json file line by line, to get the values
            data_values = fn_json_path_parser(line)
            # Insert all the values.
            database_accessor.execute(plan, data_values)


def get_json_path_parser_fn(json_path_file):
    """
    Given a JSONPath expression file returns a function that can then be applied to a json string.
    The application of the function will return a list of values in the same order as the list of
    json path expression in json_path_file. Factoring this function out can later facilitate the
    modularity of the callee, copy_json(...)

    :param str json_path_file: The JSONPath file that follows the format specified here:
        http://goo.gl/5ZOLyQ
    :returns: A function that you can call with a JSON Document which will return you a list of
        data items matching the JSONPath expressions in json_path_file
    :raises ValueError: If there are no expressions in the json_path_file
    """
    json_path_parsers = []
    with open(json_path_file) as f:
        json_path_obj = json.load(f)
        json_paths = json_path_obj['jsonpaths']
        json_path_parsers = [jsonpath_rw.parse(expr) for expr in json_paths]
    if not json_path_parsers:
        raise ValueError('No json parsed paths found in %s' % json_path_file)

    def apply_parsers(json_doc):
        """
        Given a JSON document apply the json_path_parsers to json_doc and return the values
        associated with the JSONPath expressions in the json_path_parser list.

        :param str json_doc: a string representing the json line, read from a file. Note that
        :return: a list of values that are gotten by applying the json path expressions.
        :raises ValueError: If more that one value is found corresponding to the JSONPath
            expression
        """
        data_list = []
        data_keys = []
        for json_path_parser in json_path_parsers:
            # We don't want the u' prefix in the json objects because this messes up JSON
            # parsing of embedded objects.
            parsed_paths = json_path_parser.find(json.loads(json_doc, object_hook=_decode_dict))
            if len(parsed_paths) > 1:
                    raise ValueError(
                        " JSONPath expression must specify the explicit path to a single name"
                        " element in a JSON hierarchical data structure; Multiple paths"
                        " were found: {}".format(parsed_paths))
            if parsed_paths:
                data_list.append(json.dumps(parsed_paths[0].value))
                data_keys.append(parsed_paths[0].path.fields[0])
            else:
                # If no data is found for a parsed JSONPath expression we insert null into it as
                # per http://goo.gl/0jdkjc. Adding None here does the trick.
                msg = 'JSON path parser: {} returned no results on json doc {}'.format(
                    json_path_parser, json_doc)
                _logger.error(msg)
                data_list.append(None)
                data_keys.append(None)
        _logger.debug("Data values: {}".format(data_list))
        _logger.debug("Data keys: {}".format(data_keys))
        return data_list
    return apply_parsers

def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv

def _decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv
