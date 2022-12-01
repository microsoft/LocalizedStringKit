"""Test basic features."""

import filecmp
import hashlib
import os
import sys
import tempfile
from typing import Any, Dict, List
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# pylint: disable=wrong-import-position
import localizedstringkit

# pylint: enable=wrong-import-position


class BasicTestSuite(unittest.TestCase):
    """Placeholder test cases."""

    def setUp(self) -> None:
        tests_path = os.path.abspath(os.path.dirname(__file__))
        self.data_path = os.path.join(tests_path, "data")

    def check_string_detection(self, code_file: str) -> None:
        """Check strings are detected.

        :param code_file: The code file to get the strings from
        """

        detected_strings = localizedstringkit.detection.strings_in_code_file(code_file)

        expectation_list: List[Dict[str, Any]] = [
            {"text": "Value", "comment": "Comment", "extension": "Key Extension"},
            {"text": "Calendar", "comment": "The name of the calendar tab."},
            {"text": "Email", "comment": "Some email label"},
            {
                "text": "Apple Watch App",
                "comment": "The title of the what's new content for the new Apple Watch support.",
            },
            {
                "text": "Clear through out Outlook inbox or calendar just by swiping up from the Watch face.",
                "comment": "The body of the what's new content for the new Apple Watch support",
            },
            {
                "text": 'Send invitation to "%@"?',
                "comment": "Prompt whether or not to send an invitation for event with subject name.",
                "skip_value": True,
            },
            {
                "text": "People",
                "comment": 'Comment containing \\") but the sentence continues.',
                "skip_value": True,
            },
            {"text": "Settings", "comment": "The name of the settings tab."},
            {"text": "Files", "comment": "The name of the files tab."},
            {"text": "Close", "comment": "The name of the close menu button."},
            {
                "text": 'First special token: \n and second special token: "',
                "comment": "This value contains some special tokens.",
                "skip_value": True,
            },
            {"text": "Another value", "comment": "Some comment", "bundle": "info.bundle"},
            {
                "text": "Another value",
                "comment": "Some comment",
                "extension": "Verb",
                "bundle": "info.bundle",
            },
            {"text": "%#@firstValue@ and %#@secondValue@", "comment": "Some comment"},
            {
                "text": "%#@firstValue@ and %#@secondValue@",
                "comment": "Some comment",
                "bundle": "info.bundle",
            },
        ]

        self.assertEqual(len(detected_strings) - 1, len(expectation_list))

        strings = {}
        for string in detected_strings:
            strings[string.key] = string

        # TODO: One of the problems we face for testing is that we generate the
        # key from the raw string we get from the regex. Take this as an
        # example: `Localized("Hello \"World\"", "")`
        # Our regex will give us the raw string `Hello \"World\"` back out. To
        # make it clear, if I was to store that string in a variable in Python
        # I'd write it like: `x = 'Hello \\"World\\"'` i.e. The backslashes are
        # actually in the string.
        # This is fine until Swift tries to generate the key. It doesn't get the
        # backslashes. It just gets the regular string `Hello "World"`.
        # So we can't always determine the string Swift will have.

        for index, expectation in enumerate(expectation_list):

            text = expectation["text"]
            if "extension" in expectation:
                text += ":" + expectation["extension"]
            key = hashlib.md5(text.encode("utf-8")).hexdigest()

            string = strings[key]

            if index > 10:
                self.assertEqual(string.bundle, "info.bundle")
            else:
                self.assertEqual(string.bundle, "LocalizedStringKit.bundle")

            self.assertEqual(string.comment, expectation.get("comment"))
            self.assertEqual(string.key_extension, expectation.get("extension"))
            self.assertEqual(string.language, "en")
            self.assertEqual(string.table, "LocalizedStringKit")
            if not expectation.get("skip_value", False):
                self.assertEqual(string.value, expectation.get("text"))

    def check_generated_source_matches(
        self, code_file: str, expectations_output_directory: str, language_hint: str
    ) -> None:
        """Test that the generated source file matches.

        :param code_file: The code file to get the strings from
        :param expectations_output_directory: The directory to compare to
        :param language_hint: A debug string to show what language this is running for
        """

        temp_dir = tempfile.mkdtemp()
        localizedstringkit.generate_files(
            code_files=[code_file],
            localized_string_kit_path=temp_dir,
            generate_stringsdict_files=True,
        )

        for bundle in os.listdir(temp_dir):
            if not bundle.endswith(".bundle"):
                continue

            generated_bundle_path = os.path.join(temp_dir, bundle)
            expectations_bundle_path = os.path.join(expectations_output_directory, bundle)

            self.assertTrue(
                os.path.exists(expectations_bundle_path),
                f"Mismatch in cases for {language_hint}, {expectations_bundle_path} not found",
            )

            generated_m_path = os.path.join(temp_dir, bundle.replace(".bundle", ".m"))
            expectations_m_path = os.path.join(
                expectations_output_directory, bundle.replace(".bundle", ".m")
            )

            self.assertTrue(
                os.path.exists(expectations_m_path),
                f"Mismatch in cases for {language_hint}, {expectations_m_path} not found",
            )
            self.assertTrue(
                os.path.exists(generated_m_path),
                f"Mismatch in cases for {language_hint}, {generated_m_path} not found",
            )

            self.assertTrue(
                filecmp.cmp(generated_m_path, expectations_m_path),
                f"Mismatch in cases for {language_hint}, {generated_m_path} has different content then expected in {expectations_m_path}",
            )

            for file_name in ["LocalizedStringKit.strings", "LocalizedStringKit.stringsdict"]:
                generated_file_path = os.path.join(generated_bundle_path, "en.lproj", file_name)
                expectations_file_path = os.path.join(
                    expectations_bundle_path, "en.lproj", file_name
                )

                if os.path.exists(generated_file_path):
                    self.assertTrue(
                        os.path.exists(expectations_file_path),
                        f"Mismatch in cases for {language_hint}, {generated_file_path} not found",
                    )
                    self.assertTrue(
                        filecmp.cmp(generated_file_path, expectations_file_path),
                        f"Mismatch in cases for {language_hint}, {generated_file_path} has different content then expected in {expectations_file_path}",
                    )

    def test_swift_detection_script(self) -> None:
        """Test that Swift strings are detected."""
        self.check_string_detection(os.path.join(self.data_path, "swift", "sample.swift"))

    def test_localize_script_swift(self) -> None:
        """Test that the localization script can execute successfully."""

        self.check_generated_source_matches(
            os.path.join(self.data_path, "swift", "sample.swift"),
            os.path.join(self.data_path, "swift", "expectation"),
            "Swift",
        )

    def test_objc_detection_script(self) -> None:
        """Test that Objective-C strings are detected."""

        self.check_string_detection(os.path.join(self.data_path, "objc", "sample.m"))

    def test_localize_script_objc(self) -> None:
        """Test that the localization script can execute successfully."""

        self.check_generated_source_matches(
            os.path.join(self.data_path, "objc", "sample.m"),
            os.path.join(self.data_path, "objc", "expectation"),
            "ObjC",
        )
