CREATE OR REPLACE FUNCTION execute_sql_statements(setup_statement varchar)
RETURNS SETOF void
AS $$
BEGIN
    EXECUTE setup_statement;
    RETURN;
END
$$ LANGUAGE plpgsql strict;

CREATE OR REPLACE FUNCTION copy_json(
    schema varchar,
    table_name varchar,
    json_file varchar,
    json_path_file varchar)

--    This function copies JSON lines from json_file by parsing each line using
--    JSONPath specification in the json_path_file and inserting it into the
--    table. Read further for details on how this works. *Its important that the
--    order of expressions in the json_path_file is the same as the column order
--    of table, otherwise data could be inserted into the wrong columns*.  This
--    command is thus a narrow substitute for COPY command and it does not seek
--    to replace it completely, which is inline with pypgTAP requirements:
--    http://goo.gl/0jdkjc.
--
--    The json_path_file should follow the specification: http://goo.gl/pyX2RQ.
--    A small subset of these rules is re-stated here for clarity; There are
--    some changes made to it for matching the current context.
--
--    The json_path_file must contain only a single JSON object (not an array).
--    The JSON object is a name/value pair. The object key, which is the name in
--    the name/value pair, must be "jsonpaths".  The value in the name/value
--    pair is an array of JSONPath expressions. Each JSONPath expression
--    references a single element in the JSON data hierarchy, similarly to how
--    an XPath expression refers to elements in an XML document.  Each JSONPath
--    expression corresponds to one column in the target table. The order of the
--    JSONPaths array elements must match the order of the columns in the target
--    table. If an element referenced by a JSONPath expression is not found in
--    the JSON data, this function will load a null value for it.
RETURNS SETOF void
AS $$
    plpy.execute('SELECT activate_virtual_env()')
    import os
    project_path_data = plpy.execute('SELECT get_project_path()')
    from pypgtap.core.project.utils import copy_json
    copy_json(
        project_path_data[0]['get_project_path'], schema,
        table_name, json_file, json_path_file, plpy)
    return ''
$$ LANGUAGE plpythonu strict;
