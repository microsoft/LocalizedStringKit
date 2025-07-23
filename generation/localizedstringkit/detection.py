"""Detection methods handling tools."""

import re
from typing import ClassVar, List, Optional, Pattern, Tuple

from dotstrings import LocalizedString

from localizedstringkit import logger
from localizedstringkit.exceptions import InvalidLocalizedCallException

log = logger.get()


class Detector:
    """Base file string detector class."""

    _INVALID_CALL_PATTERN: ClassVar[Pattern] = re.compile(
        r'(.*Localized(?:WithKeyExtension)?\([\s\n]*[^"@\n\r ].*)'
    )
    QUOTE_ESCAPE_SEQUENCE: ClassVar[str] = r"\""
    TEMPORARY_ESCAPE_SEQUENCE: ClassVar[str] = "$$$"

    file_path: str
    contents: str
    sanitized_contents: str

    def __init__(self, file_path: str) -> None:
        """Create a new detector.

        :param file_path: The path to the file to detect the strings in
        """
        self.file_path = file_path

        with open(file_path, "r", encoding="utf-8") as file_contents:
            self.contents = "".join(file_contents.readlines())

        self.sanitized_contents = self.contents.replace(
            Detector.QUOTE_ESCAPE_SEQUENCE, Detector.TEMPORARY_ESCAPE_SEQUENCE
        )

    def find_strings(self) -> List[LocalizedString]:
        """Method which finds localized strings in files.

        This should be overridden by each subclass.

        :returns: List of localized strings in the code file
        """
        raise NotImplementedError()

    def _get_matches(self, pattern: Pattern, expected_match_count: int) -> List[Tuple]:
        """Get all matches in a file, confirming the match count expected.

        :param pattern: The regex pattern to match against the contents
        :param expected_match_count: The number of matches we expect to find

        :returns: The list of matches

        :raises Exception: If the number of matches doesn't match the expected number
        """

        matches_in_buffer: List[Tuple] = []

        sanitized_matches = pattern.findall(self.sanitized_contents)

        for match in sanitized_matches:
            if len(match) != expected_match_count:
                raise Exception("Found match with invalid number of capture groups: " + str(match))

            result: Tuple = match + (pattern,)
            matches_in_buffer.append(result)

        return matches_in_buffer

    def confirm_string_args_only(self) -> None:
        """Confirm that there are only string arguments passed in.

        For example, this is invalid:

        `Localized(String(format: "You are %@ years old", age), "Comment")`

        Instead, this should be:

        `String(format: Localized("You are %@ years old", "Comment"), age)`

        :raises InvalidLocalizedCallException: If passed in an invalid file type or if there are invalid calls
        """

        matches = Detector._INVALID_CALL_PATTERN.findall(self.sanitized_contents)

        # Strip spaces
        matches = [match.strip() for match in matches]

        # Filter out redefinitions
        matches = [match for match in matches if not match.startswith("func ")]

        if len(matches) > 0:
            raise InvalidLocalizedCallException(
                f"Found invalid calls to Localized in file: {self.file_path}, {matches}"
            )

    def _process_match(self, found_match: Tuple) -> List[str]:
        """Process a regex match to extract string parameters.

        Can be overridden by subclasses for custom match processing.

        :param found_match: Raw match tuple from regex with pattern appended
        :returns: List of processed string parameters (without pattern)
        """
        processed = []
        for i in range(len(found_match) - 1):
            processed.append(
                found_match[i].replace(
                    Detector.TEMPORARY_ESCAPE_SEQUENCE,
                    Detector.QUOTE_ESCAPE_SEQUENCE,
                ),
            )
        return processed

    def _create_localized_string(
        self, strings: List[str], pattern: Pattern, bundle_pattern: Pattern
    ) -> LocalizedString:
        """Create a LocalizedString object from processed strings.

        :param strings: List of processed string parameters
        :param pattern: The regex pattern that matched
        :param bundle_pattern: Pattern used to identify bundle overrides
        :returns: LocalizedString object
        """
        num_strings = len(strings)

        if num_strings == 2:
            # Standard Localized call
            return LocalizedString(
                key=None,
                value=strings[0],
                language="en",
                table="LocalizedStringKit",
                comment=strings[1],
                key_extension=None,
                bundle="LocalizedStringKit.bundle",
            )
        elif num_strings == 3:
            if pattern == bundle_pattern:
                # Localized call with custom bundle
                return LocalizedString(
                    key=None,
                    value=strings[0],
                    language="en",
                    table="LocalizedStringKit",
                    comment=strings[1],
                    key_extension=None,
                    bundle=strings[2],
                )
            else:
                # Localized call with key extension
                return LocalizedString(
                    key=None,
                    value=strings[0],
                    language="en",
                    table="LocalizedStringKit",
                    comment=strings[1],
                    key_extension=strings[2],
                    bundle="LocalizedStringKit.bundle",
                )
        else:
            # Localized call with key extension and custom bundle
            return LocalizedString(
                key=None,
                value=strings[0],
                language="en",
                table="LocalizedStringKit",
                comment=strings[1],
                key_extension=strings[2],
                bundle=strings[3],
            )

    def _detect_strings(
        self, patterns: List[Tuple[Pattern, int]], bundle_pattern: Pattern
    ) -> List[LocalizedString]:
        """Find all matching localized calls with a key specified in the buffer.

        :param patterns: The list of patterns and their expected match counts to
                         detect in the code file
        :param bundle_pattern: A Pattern used to match strings with overridden bundle

        :returns: The list of localized strings
        """

        # The first thing to do is make sure there are no invalid calls to the
        # function
        self.confirm_string_args_only()

        # Find occurrences of `Localized` function calls
        matches_in_buffer: List[Tuple] = []
        for pattern, count in patterns:
            matches_in_buffer += self._get_matches(pattern, count)

        results = []

        for found_match in matches_in_buffer:
            # Extract the pattern from the match
            pattern = found_match[-1]

            # Process the match (can be overridden by subclasses)
            processed_strings = self._process_match(found_match)

            # Create LocalizedString object
            localized_string = self._create_localized_string(
                processed_strings, pattern, bundle_pattern
            )
            results.append(localized_string)

        return results


class SwiftDetector(Detector):
    """Detect localized strings in Swift code files."""

    # Override the invalid call pattern to allow both regular and raw strings for Swift
    _SWIFT_INVALID_CALL_PATTERN: ClassVar[Pattern] = re.compile(
        r'(.*Localized(?:WithKeyExtension)?\([\s\n]*[^"#@\n\r ].*)'
    )

    LOCALIZED_PATTERN: Pattern = re.compile(r'Localized\(\s*(?:#*"(.*?)"#*|"(.*?)")\s*,\s*(?:#*"(.*?)"#*|"(.*?)")\s*\)', re.DOTALL)
    LOCALIZED_BUNDLE_PATTERN: Pattern = re.compile(
        r'LocalizedWithBundle\(\s*(?:#*"(.*?)"#*|"(.*?)")\s*,\s*(?:#*"(.*?)"#*|"(.*?)")\s*,\s*(?:#*"(.*?)"#*|"(.*?)")\s*\)', re.DOTALL
    )
    LOCALIZED_EXTENSION_PATTERN: Pattern = re.compile(
        r'LocalizedWithKeyExtension\(\s*(?:#*"(.*?)"#*|"(.*?)")\s*,\s*(?:#*"(.*?)"#*|"(.*?)")\s*,\s*(?:#*"(.*?)"#*|"(.*?)")\s*\)', re.DOTALL
    )
    LOCALIZED_EXTENSION_BUNDLE_PATTERN: Pattern = re.compile(
        r'LocalizedWithKeyExtensionAndBundle\(\s*(?:#*"(.*?)"#*|"(.*?)")\s*,\s*(?:#*"(.*?)"#*|"(.*?)")\s*,\s*(?:#*"(.*?)"#*|"(.*?)")\s*,\s*(?:#*"(.*?)"#*|"(.*?)")\s*\)', re.DOTALL
    )

    def confirm_string_args_only(self) -> None:
        """Confirm that there are only string arguments passed in for Swift files.

        Overrides the base class method to allow raw strings (#"..."#) in addition to regular strings.

        :raises InvalidLocalizedCallException: If there are invalid calls
        """
        matches = SwiftDetector._SWIFT_INVALID_CALL_PATTERN.findall(self.sanitized_contents)

        # Strip spaces
        matches = [match.strip() for match in matches]

        # Filter out redefinitions
        matches = [match for match in matches if not match.startswith("func ")]

        if len(matches) > 0:
            raise InvalidLocalizedCallException(
                f"Found invalid calls to Localized in file: {self.file_path}, {matches}"
            )

    def _extract_string_content(self, raw_capture: str, regular_capture: str) -> str:
        """Extract the actual string content from raw or regular string captures.

        :param raw_capture: The capture group for raw string content (may be None/empty)
        :param regular_capture: The capture group for regular string content (may be None/empty)
        :returns: The actual string content
        """
        return raw_capture if raw_capture else regular_capture

    def _process_match(self, found_match: Tuple) -> List[str]:
        """Process a Swift regex match to extract string parameters from raw/regular pairs.

        Swift patterns produce pairs of capture groups (raw, regular) for each string parameter.
        This method processes those pairs and extracts the actual content.

        :param found_match: Raw match tuple from regex with pattern appended
        :returns: List of processed string parameters (without pattern)
        """
        processed = []

        # Process pairs of capture groups (raw_content, regular_content)
        for i in range(0, len(found_match) - 1, 2):
            raw_content = found_match[i] if found_match[i] else ""
            regular_content = found_match[i + 1] if found_match[i + 1] else ""
            actual_content = self._extract_string_content(raw_content, regular_content)

            # Replace temporary escape sequences
            actual_content = actual_content.replace(
                Detector.TEMPORARY_ESCAPE_SEQUENCE,
                Detector.QUOTE_ESCAPE_SEQUENCE,
            )
            processed.append(actual_content)

        return processed

    def find_strings(self) -> List[LocalizedString]:
        """Find all matching localized calls with a key specified in the buffer.

        :returns: The list of localized strings
        """
        return self._detect_strings(
            [
                (SwiftDetector.LOCALIZED_PATTERN, 4),  # 2 strings * 2 capture groups each
                (SwiftDetector.LOCALIZED_EXTENSION_PATTERN, 6),  # 3 strings * 2 capture groups each
                (SwiftDetector.LOCALIZED_BUNDLE_PATTERN, 6),  # 3 strings * 2 capture groups each
                (SwiftDetector.LOCALIZED_EXTENSION_BUNDLE_PATTERN, 8),  # 4 strings * 2 capture groups each
            ],
            SwiftDetector.LOCALIZED_BUNDLE_PATTERN,
        )


class ObjcDetector(Detector):
    """Detect localized strings in Objective-C code files."""

    LOCALIZED_PATTERN: Pattern = re.compile(r'Localized\(\s*@"(.+?)",\s*@"(.*?)"\s*\)')
    LOCALIZED_EXTENSION_PATTERN: Pattern = re.compile(
        r'LocalizedWithKeyExtension\(\s*@"(.+?)",\s*@"(.*?)",\s*@"(.*?)"\s*\)'
    )
    LOCALIZED_BUNDLE_PATTERN: Pattern = re.compile(
        r'LocalizedWithBundle\(\s*@"(.+?)",\s*@"(.*?)",\s*@"(.*?)"\s*\)'
    )
    LOCALIZED_EXTENSION_BUNDLE_PATTERN: Pattern = re.compile(
        r'LocalizedWithKeyExtensionAndBundle\(\s*@"(.+?)",\s*@"(.*?)",\s*@"(.*?)",\s*@"(.*?)"\s*\)'
    )

    def find_strings(self) -> List[LocalizedString]:
        """Find all matching localized calls with a key specified in the buffer.

        :returns: The list of localized strings
        """

        return self._detect_strings(
            [
                (ObjcDetector.LOCALIZED_PATTERN, 2),
                (ObjcDetector.LOCALIZED_EXTENSION_PATTERN, 3),
                (ObjcDetector.LOCALIZED_BUNDLE_PATTERN, 3),
                (ObjcDetector.LOCALIZED_EXTENSION_BUNDLE_PATTERN, 4),
            ],
            ObjcDetector.LOCALIZED_BUNDLE_PATTERN,
        )


def strings_in_code_file(file_path: str) -> List[LocalizedString]:
    """Find all tokens we should localize.

    :param file_path: The file to scan for localized strings

    :returns: The list of found localized strings

    :raises Exception: If the file is an unknown type
    """

    log.debug(f"Finding localized strings in file: {file_path}")

    file_detector: Optional[Detector] = None

    if file_path.endswith(".swift"):
        file_detector = SwiftDetector(file_path)
    elif file_path.endswith(".m"):
        file_detector = ObjcDetector(file_path)
    else:
        raise Exception("Unknown file type: " + file_path)

    return file_detector.find_strings()


def strings_in_code_files(code_files: List[str]) -> List[LocalizedString]:
    """Return the localized strings in a list of code files.

    :param code_files: The list of file paths to generate the localized strings for

    :returns: The list of localized strings from the codebase
    """

    strings: List[LocalizedString] = []

    for file_path in code_files:
        strings += strings_in_code_file(file_path)

    return strings