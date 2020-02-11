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

        with open(file_path, "r") as file_contents:
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

            matches_in_buffer.append(match)

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

    def _detect_strings(self, patterns: List[Tuple[Pattern, int]]) -> List[LocalizedString]:
        """Find all matching localized calls with a key specified in the buffer.

        :param patterns: The list of patterns and their expected match counts to
                         detect in the code file

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

        for match in matches_in_buffer:
            match = tuple(
                map(
                    lambda component: component.replace(
                        Detector.TEMPORARY_ESCAPE_SEQUENCE, Detector.QUOTE_ESCAPE_SEQUENCE
                    ),
                    match,
                )
            )

            if len(match) == 2:
                results.append(
                    LocalizedString(
                        key=None,
                        value=match[0],
                        language="en",
                        table="LocalizedStringKit",
                        comment=match[1],
                    )
                )
            else:
                results.append(
                    LocalizedString(
                        key=None,
                        value=match[0],
                        language="en",
                        table="LocalizedStringKit",
                        comment=match[1],
                        key_extension=match[2],
                    )
                )

        return results


class SwiftDetector(Detector):
    """Detect localized strings in Swift code files."""

    LOCALIZED_PATTERN: Pattern = re.compile(r'Localized\(\s*"(.+?)",\s*"(.*?)"\s*\)')
    LOCALIZED_EXTENSION_PATTERN: Pattern = re.compile(
        r'LocalizedWithKeyExtension\(\s*"(.+?)",\s*"(.*?)",\s*"(.*?)"\s*\)'
    )

    def find_strings(self) -> List[LocalizedString]:
        """Find all matching localized calls with a key specified in the buffer.

        :returns: The list of localized strings
        """

        return self._detect_strings(
            [(SwiftDetector.LOCALIZED_PATTERN, 2), (SwiftDetector.LOCALIZED_EXTENSION_PATTERN, 3)]
        )


class ObjcDetector(Detector):
    """Detect localized strings in Objective-C code files."""

    LOCALIZED_PATTERN: Pattern = re.compile(r'Localized\(\s*@"(.+?)",\s*@"(.*?)"\s*\)')
    LOCALIZED_EXTENSION_PATTERN: Pattern = re.compile(
        r'LocalizedWithKeyExtension\(\s*@"(.+?)",\s*@"(.*?)",\s*@"(.*?)"\s*\)'
    )

    def find_strings(self) -> List[LocalizedString]:
        """Find all matching localized calls with a key specified in the buffer.

        :returns: The list of localized strings
        """

        return self._detect_strings(
            [(ObjcDetector.LOCALIZED_PATTERN, 2), (ObjcDetector.LOCALIZED_EXTENSION_PATTERN, 3)]
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
