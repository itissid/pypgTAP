"""
Pure python utilities to do some regular maintenance
TODO(Sid): Move this to the test kit directory so that
it does not muck up the test directory where all the
base utilities are.
"""
import os
import datetime as dt


def append_libs(project_root, path=[]):
    lib_dir = os.path.join(project_root, '../commons/lib/')
    top_library_paths = os.walk(lib_dir).next()[1]
    for lib in top_library_paths:
        path.append(os.path.join(lib_dir, lib))
    return path


def parse_redshift_json_path(redshift_json_path_json, data):
    """
    The job of this utility is to parse the json path file that has many
    JSONPath expressions and return an iterable of them.

    """
    from jsonpath_rw import parse as jp_parse

    if 'jsonpaths' in redshift_json_path_json:
        redshift_json_path_json = redshift_json_path_json['jsonpaths']

    if isinstance(redshift_json_path_json, list):
        for json_path in redshift_json_path_json:
            for v in jp_parse(json_path).find(data):
                yield v.path.fields[0], v.value
    elif isinstance(redshift_json_path_json, str):
            for v in jp_parse(json_path).find(data):
                yield v.path.fields[0], v.value
    else:
        raise ValueError(
            'type {} is unrecognized for json path object {}'
                .format(type(
                    redshift_json_path_json), redshift_json_path_json))

def return_table_type_mapping(table_name):
    """
    Given a table name this would return
    a mapping to the type
    """
    pass


def validate_pg_ts_guess(f):
    """
    Validates the final timestamp that comes out of the timestamp
    guessers.
    Probably validate that ts is not whacky
    """
    def inner(*args, **kwargs):
        time_stamp = f(*args, **kwargs)
        # TODO(Sid): validation on the string
        # timestamp that was returned.
        return time_stamp
    return inner


@validate_pg_ts_guess
def try_guess_and_convert_pg_timestamp(ts):
    """
    If the interger time
    """
    if isinstance(ts, int) or isinstance(ts, long):
        return try_guess_pg_time_stamp_from_int(ts)
    elif isinstance(ts, str):
        try:
            return dt.datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            # May be its a number try converting to int, else give up.
            ts = int(ts)
            return try_guess_pg_time_stamp_from_int(ts)
    else:
        raise ValueError('{} is not a string'.format(ts))


def try_guess_pg_time_stamp_from_int(ts):
    """
    If the int time stamp is convertable to [O[I[Oj
    """
    try:
        return dt.datetime.fromtimestamp(ts).strftime(
            '%Y-%m-%d %H:%M:%S')
    except ValueError:
        print 'Maybe the time stamp {} is in ' \
                'milliseconds trying divide by 1e3'.format(ts)
        return dt.datetime.fromtimestamp(ts / 1000.).strftime(
            '%Y-%m-%d %H:%M:%S')


##### Some utilities to encode strings when a json.loads is called on a string
####


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


def get_file_if_exists(file_name):
	project_root_path = os.path.abspath('../../')
	project_file = os.path.exists(
		os.path.join(
			project_root_path, file_name))
	if os.path.exists(file_name):
		return open(file_name)
	elif project_file is True:
		return open(project_file)
	else:
		raise ValueError(
			'file not found: {} '.format(file_name))
