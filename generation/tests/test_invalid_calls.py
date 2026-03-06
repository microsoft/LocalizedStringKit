"""Test that invalid Localized calls are properly detected and reported."""

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
from localizedstringkit import detection
from localizedstringkit.exceptions import InvalidLocalizedCallException

# pylint: enable=wrong-import-position


class InvalidCallTestSuite(unittest.TestCase):
    """Test suite for invalid localized call detection."""

    def setUp(self) -> None:
        tests_path = os.path.abspath(os.path.dirname(__file__))
        self.data_path = os.path.join(tests_path, "data")

    def test_invalid_call_with_variable_swift(self) -> None:
        """Test that Swift calls with variables as arguments are caught."""
        code_file = os.path.join(self.data_path, "swift", "invalid_variable.swift")
        with self.assertRaises(InvalidLocalizedCallException):
            detection.strings_in_code_file(code_file)

    def test_invalid_call_with_expression_swift(self) -> None:
        """Test that Swift calls with expressions are caught."""
        code_file = os.path.join(self.data_path, "swift", "invalid_expression.swift")
        with self.assertRaises(InvalidLocalizedCallException):
            detection.strings_in_code_file(code_file)

    def test_function_definition_ignored_swift(self) -> None:
        """Test that Swift function definitions with Localized in the name are ignored."""
        code_file = os.path.join(self.data_path, "swift", "function_definition.swift")
        strings = detection.strings_in_code_file(code_file)
        self.assertEqual(len(strings), 1)

    def test_mixed_valid_and_invalid_swift(self) -> None:
        """Test that invalid Swift calls are caught even when valid calls exist."""
        code_file = os.path.join(self.data_path, "swift", "mixed_valid_invalid.swift")
        with self.assertRaises(InvalidLocalizedCallException):
            detection.strings_in_code_file(code_file)

    def test_invalid_call_with_variable_objc(self) -> None:
        """Test that Objective-C calls with variables are caught."""
        code_file = os.path.join(self.data_path, "objc", "invalid_variable.m")
        with self.assertRaises(InvalidLocalizedCallException):
            detection.strings_in_code_file(code_file)
