# ! python3

# https://stackoverflow.com/questions/7100125/storing-python-dictionaries
import unittest
import json
import io
from io import StringIO

"""
# run with
# python3 -m unittest json_export.py -v
"""


# https://docs.python.org/3/library/json.html
# [Doc](https://docs.python.org/3/library/json.html)
class TestJSON(unittest.TestCase):

    def test_store_json(self):
        data = {'key1': "value1", 'key2': "value2"}

        with open('some_data/data.json', 'w') as fp:
            json.dump(data, fp, sort_keys=True, indent=4)


    def test_store_to_string_json(self):
        data = {'key1': 'value1', 'key2': 'value2'}
        data_string = '{"key1": "value1", "key2": "value2"}'
        json_string = json.dumps(data)
        self.assertEqual(data_string, json_string)


    def test_read_json(self):
        with open('some_data/json_export_file.json', 'r') as fp:
            data = json.load(fp)
            expected = {'key1': 'value1', 'key2': 'value2', 'key3': 'value3'}
            self.assertEqual(expected, data)


if __name__ == '__main__':
    unittest.main()
