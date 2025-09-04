import unittest
import jsonpatcher
from click.testing import CliRunner

class PatcherTestSuite(unittest.TestCase):
    def test_existent_path(self):
        self.assertEqual(
            jsonpatcher.check_path({"user": {"name": {"initials": "EG"}, "ID": 1486}},
                                   ["user", "name", "initials"]),"key")

    def test_nonexistent_path(self):
        self.assertEqual(
            jsonpatcher.check_path({"user": {"name": {"initials": "EG"}, "ID": 1486}},
                                   ["user", "name", "initials", "EG", "E"]),"non")

    def test_array_path(self):
        self.assertEqual(
            jsonpatcher.check_path({"user": {"name": {"initials": "EG"}, "IDs": [1486, 2483, 1932]}},
                                   ["user", "IDs"]),"arr")

    def test_add_legal_primitive(self):
        self.assertEqual(
            jsonpatcher.add({"user": {"name": {"initials": "EG"}, "ID": 1486}}, ["user", "name", "full_name"], "EthanGalatzer"),
            {"user": {"name": {"initials": "EG", "full_name": "EthanGalatzer"}, "ID": 1486}})

    def test_add_illegal(self):
        self.assertRaises(ValueError, jsonpatcher.add, {"user": {"name": {"initials": "EG"}, "ID": 1486}}, ["user", "name"], "EthanGalatzer")

    def test_add_to_array(self):
        self.assertEqual(
            jsonpatcher.add({"user": {"name": {"initials": "EG"}, "IDs": [1486, 2483, 1932]}},
                            ["user", "IDs"], 3294), {"user": {"name": {"initials": "EG"}, "IDs": [1486, 2483, 1932, 3294]}})

    def test_modify_legal_primitive(self):
        self.assertEqual(
            jsonpatcher.modify({"user": {"name": {"initials": "EG"}, "ID": 1486}}, ["user", "name"], "EthanGalatzer"),
            {"user": {"name": "EthanGalatzer", "ID": 1486}})

    def test_modify_illegal(self):
        self.assertRaises(ValueError, jsonpatcher.modify, {"user": {"name": {"initials": "EG"}, "ID": 1486}}, ["user", "name", "full_name"], "EthanGalatzer")

    def test_modify_array(self):
        self.assertEqual(
            jsonpatcher.modify({"user": {"name": {"initials": "EG"}, "IDs": [1486, 2483, 1932]}},
                               ["user", "IDs"], 3294),
            {"user": {"name": {"initials": "EG"}, "IDs": 3294}})

    def test_delete_legal_primitive(self):
        self.assertEqual(
            jsonpatcher.delete({"user": {"name": {"initials": "EG"}, "ID": 1486}}, ["user", "name"], "EthanGalatzer"),
            {"user": {"ID": 1486}})

    def test_delete_illegal(self):
        self.assertRaises(ValueError, jsonpatcher.delete, {"user": {"name": {"initials": "EG"}, "ID": 1486}},
                          ["user", "name", "full_name"], "EthanGalatzer")

    def test_delete_array_value(self):
        self.assertEqual(
            jsonpatcher.delete({"user": {"name": {"initials": "EG"}, "IDs": [1486, 2483, 1932, 1486]}},
                               ["user", "IDs"], 1486),
            {"user": {"name": {"initials": "EG"}, "IDs": [2483, 1932]}})

    def test_delete_array(self):
        self.assertEqual(
            jsonpatcher.delete({"user": {"name": {"initials": "EG"}, "IDs": [1486, 2483, 1932, 1486]}},
                               ["user", "IDs"]),
            {"user": {"name": {"initials": "EG"}}})

    def test_operation_values(self):
        self.assertEqual(jsonpatcher.operation_values({"op": "modify", "path": "user.name", "value": "Alice"}), ("modify", "user.name", ["user", "name"], "Alice"))

    def test_full(self):
        runner = CliRunner()
        result = runner.invoke(jsonpatcher.patch, '--input testdata.json --patch testpatch1.json --patch testpatch2.json --output output.json')
        with open("expected_output.json", "r") as expected_output, open("output.json", "r") as actual_output:
            self.assertEqual(expected_output.read(), actual_output.read())

if __name__ == '__main__':
    unittest.main()

