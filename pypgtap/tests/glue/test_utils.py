import json
import unittest

from mock import patch, mock_open, call
import pypgtap.core.project.utils as under_test_module


class TestJSONPathParsing(unittest.TestCase):

    """This test suite will test the get_json_path_parser_fn in pypgtap.core.project.utils """

    mock_json_path_file = mock_open(read_data="""{
                    "jsonpaths":
                    [ "$.key1", "$.key2", "$.key4", "$.key3"]
            }""")
    def test_json_path_parser_correct_parse(self):
        """This test case will pass a json_path_file to get_json_path_parser_fn and then call the
        returned function with a JSON document; The document will be parsed and non None values for
        all the specified JSONPath expressions will be returned. The JSON value types will be
        varied to test all possible cases.
        We also asserts that the values are returned in the same order as the json path expression.
        """

        with patch('__builtin__.open', self.mock_json_path_file, create=True) as mock_obj:
            parse_function = under_test_module.get_json_path_parser_fn("does_not_matter")
            test_json_str = """{
                "key1": 999,
                "key2": "test_string",
                "key3": ["mixed", "types", {"a": "b"}, 999, [1, 2, 3]],
                "key4": {"inner_key": "inner_test_value"}
            }"""
            test_json = json.loads(test_json_str, object_hook=under_test_module._decode_dict)
            test_values = parse_function(test_json_str)
            mock_obj.assert_has_calls(call("does_not_matter"))
            # test_values should occur in the order defined in the mock_json_path_file expression
            # list
            self.assertSequenceEqual(
                test_values, [json.dumps(test_json['key1']),
                json.dumps(test_json['key2']), json.dumps(test_json['key4']),
                json.dumps(test_json['key3'])])

    def test_json_path_parser_null_values(self):
        """
        If a JSONPath expression key is not found we assert that we add None for it in the
        return list"""
        with patch('__builtin__.open', self.mock_json_path_file, create=True) as mock_obj:
            parse_function = under_test_module.get_json_path_parser_fn("does_not_matter")
            test_json_str = """{
                "key1": 999,
                "key4": {"inner_key": "inner_test_value"}
            }"""
            test_json = json.loads(test_json_str, object_hook=under_test_module._decode_dict)
            test_values = parse_function(test_json_str)
            mock_obj.assert_has_calls(call("does_not_matter"))
            # test_values should occur in the order defined in the mock_json_path_file expression
            # list
            self.assertSequenceEqual(
                test_values, [json.dumps(test_json['key1']),
                None, json.dumps(test_json['key4']), None])
