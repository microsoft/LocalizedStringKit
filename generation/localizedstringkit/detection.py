"""Detection methods handling tools."""

import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import ClassVar, List, Optional, Pattern

from dotstrings import LocalizedString

from localizedstringkit import logger
from localizedstringkit.exceptions import InvalidLocalizedCallException, UnsupportedFileTypeError

log = logger.get()


# Swift combined pattern - matches both VALID and INVALID calls in one pattern
# Valid calls populate named groups, invalid calls populate the 'invalid' group
_SWIFT_COMBINED_PATTERN: Pattern = re.compile(
    r"(?:"
    # Valid patterns with named groups
    r'LocalizedWithKeyExtensionAndBundle\(\s*"(?P<ext_bundle_value>.+?)",\s*"(?P<ext_bundle_comment>.*?)",\s*"(?P<ext_bundle_extension>.*?)",\s*"(?P<ext_bundle_bundle>.*?)"\s*\)|'
    r'LocalizedWithBundle\(\s*"(?P<bundle_value>.+?)",\s*"(?P<bundle_comment>.*?)",\s*"(?P<bundle_bundle>.*?)"\s*\)|'
    r'LocalizedWithKeyExtension\(\s*"(?P<ext_value>.+?)",\s*"(?P<ext_comment>.*?)",\s*"(?P<ext_extension>.*?)"\s*\)|'
    r'Localized\(\s*"(?P<basic_value>.+?)",\s*"(?P<basic_comment>.*?)"\s*\)|'
    # Invalid pattern - catch any Localized call that doesn't match above
    r"(?P<invalid>Localized(?:WithKeyExtension|WithBundle|WithKeyExtensionAndBundle)?\([^)]+\))"
    r")"
)

# Objective-C combined pattern - matches both VALID and INVALID calls
# Valid calls populate named groups, invalid calls populate the 'invalid' group
_OBJC_COMBINED_PATTERN: Pattern = re.compile(
    r"(?:"
    # Valid patterns with named groups
    r'LocalizedWithKeyExtensionAndBundle\(\s*@"(?P<ext_bundle_value>.+?)",\s*@"(?P<ext_bundle_comment>.*?)",\s*@"(?P<ext_bundle_extension>.*?)",\s*@"(?P<ext_bundle_bundle>.*?)"\s*\)|'
    r'LocalizedWithBundle\(\s*@"(?P<bundle_value>.+?)",\s*@"(?P<bundle_comment>.*?)",\s*@"(?P<bundle_bundle>.*?)"\s*\)|'
    r'LocalizedWithKeyExtension\(\s*@"(?P<ext_value>.+?)",\s*@"(?P<ext_comment>.*?)",\s*@"(?P<ext_extension>.*?)"\s*\)|'
    r'Localized\(\s*@"(?P<basic_value>.+?)",\s*@"(?P<basic_comment>.*?)"\s*\)|'
    # Invalid pattern - catch any Localized call that doesn't match above
    r"(?P<invalid>Localized(?:WithKeyExtension|WithBundle|WithKeyExtensionAndBundle)?\([^)]+\))"
    r")"
)


class Detector:
    """Base file string detector class."""

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
            self.contents = file_contents.read()

        self.sanitized_contents = self.contents.replace(
            Detector.QUOTE_ESCAPE_SEQUENCE, Detector.TEMPORARY_ESCAPE_SEQUENCE
        )

    def find_strings(self) -> List[LocalizedString]:
        """Method which finds localized strings in files.

        This should be overridden by each subclass.

        :returns: List of localized strings in the code file
        """
        raise NotImplementedError()

    def restore_quotes(self, text: str) -> Optional[str]:
        """Restore original quotes in the text by replacing the temporary escape sequence.

        :param text: The text to restore quotes in

        :returns: The text with quotes restored, or None if input is None
        """
        if text is None:
            return None
        return text.replace(
            Detector.TEMPORARY_ESCAPE_SEQUENCE,
            Detector.QUOTE_ESCAPE_SEQUENCE,
        )

    def _detect_strings(self, combined_pattern: Pattern) -> List[LocalizedString]:
        """Find all matching localized calls using a combined pattern with named groups.

        This method makes a single pass through the file. The pattern matches both
        valid calls (with proper string literals) and invalid calls (with variables/expressions).
        Valid calls populate specific named groups, while invalid calls populate the 'invalid' group.

        :param combined_pattern: Combined pattern with named groups for all variants

        :returns: The list of localized strings

        :raises InvalidLocalizedCallException: If there are Localized calls with non-string arguments
        """

        results = []
        invalid_calls = []

        # Extract valid calls AND detect invalid calls in one iteration
        for match in combined_pattern.finditer(self.sanitized_contents):
            groupdict = match.groupdict()

            if groupdict.get("invalid"):
                # Skip function definitions (check the line for 'func')
                line_start = self.sanitized_contents.rfind("\n", 0, match.start()) + 1
                line_end = self.sanitized_contents.find("\n", match.start())
                if line_end == -1:
                    line_end = len(self.sanitized_contents)
                line = self.sanitized_contents[line_start:line_end].strip()

                if not line.startswith("func "):
                    invalid_calls.append(groupdict["invalid"])
            elif groupdict.get("ext_bundle_value") is not None:
                # LocalizedWithKeyExtensionAndBundle - 4 params
                results.append(
                    LocalizedString(
                        key=None,
                        value=self.restore_quotes(groupdict["ext_bundle_value"]),
                        language="en",
                        table="LocalizedStringKit",
                        comment=self.restore_quotes(groupdict["ext_bundle_comment"]),
                        key_extension=self.restore_quotes(groupdict["ext_bundle_extension"]),
                        bundle=self.restore_quotes(groupdict["ext_bundle_bundle"]),
                    )
                )
            elif groupdict.get("bundle_value") is not None:
                # LocalizedWithBundle - 3 params (value, comment, bundle)
                results.append(
                    LocalizedString(
                        key=None,
                        value=self.restore_quotes(groupdict["bundle_value"]),
                        language="en",
                        table="LocalizedStringKit",
                        comment=self.restore_quotes(groupdict["bundle_comment"]),
                        key_extension=None,
                        bundle=self.restore_quotes(groupdict["bundle_bundle"]),
                    )
                )
            elif groupdict.get("ext_value") is not None:
                # LocalizedWithKeyExtension - 3 params (value, comment, extension)
                results.append(
                    LocalizedString(
                        key=None,
                        value=self.restore_quotes(groupdict["ext_value"]),
                        language="en",
                        table="LocalizedStringKit",
                        comment=self.restore_quotes(groupdict["ext_comment"]),
                        key_extension=self.restore_quotes(groupdict["ext_extension"]),
                        bundle="LocalizedStringKit.bundle",
                    )
                )
            elif groupdict.get("basic_value") is not None:
                # Localized - 2 params (value, comment)
                results.append(
                    LocalizedString(
                        key=None,
                        value=self.restore_quotes(groupdict["basic_value"]),
                        language="en",
                        table="LocalizedStringKit",
                        comment=self.restore_quotes(groupdict["basic_comment"]),
                        key_extension=None,
                        bundle="LocalizedStringKit.bundle",
                    )
                )

        # After the single pass, check if we found any invalid calls
        if invalid_calls:
            raise InvalidLocalizedCallException(
                f"Found invalid calls to Localized in file: {self.file_path}. "
                f"Ensure all arguments are string literals (not variables or expressions). "
                f"Invalid calls: {invalid_calls[:3]}"  # Show first 3 to avoid overwhelming output
            )

        return results


class SwiftDetector(Detector):
    """Detect localized strings in Swift code files."""

    def find_strings(self) -> List[LocalizedString]:
        """Find all matching localized calls with a key specified in the buffer.

        Uses a combined pattern with named groups for optimal performance -
        single pass through the file instead of multiple passes.

        :returns: The list of localized strings
        """
        return self._detect_strings(_SWIFT_COMBINED_PATTERN)


class ObjcDetector(Detector):
    """Detect localized strings in Objective-C code files."""

    def find_strings(self) -> List[LocalizedString]:
        """Find all matching localized calls with a key specified in the buffer.

        Uses a combined pattern with named groups for optimal performance -
        single pass through the file instead of multiple passes.

        :returns: The list of localized strings
        """
        return self._detect_strings(_OBJC_COMBINED_PATTERN)


def strings_in_code_file(file_path: str) -> List[LocalizedString]:
    """Find all tokens we should localize.

    :param file_path: The file to scan for localized strings

    :returns: The list of found localized strings

    :raises UnsupportedFileTypeError: If the file is an unknown type
    """

    log.debug("Finding localized strings in file: %s", file_path)

    file_detector: Optional[Detector] = None

    if file_path.endswith(".swift"):
        file_detector = SwiftDetector(file_path)
    elif file_path.endswith(".m"):
        file_detector = ObjcDetector(file_path)
    else:
        raise UnsupportedFileTypeError(f"Unknown file type: {file_path}")

    return file_detector.find_strings()


def _process_single_file(file_path: str) -> List[LocalizedString]:
    """Process a single file for parallel execution.

    :param file_path: The file to scan
    :returns: The list of found localized strings
    """
    try:
        return strings_in_code_file(file_path)
    except (IOError, InvalidLocalizedCallException, UnsupportedFileTypeError) as exception:
        log.error("Error processing %s: %s", file_path, exception)
        return []


def strings_in_code_files(
    code_files: List[str], parallel: bool = True, max_workers: Optional[int] = None
) -> List[LocalizedString]:
    """Return the localized strings in a list of code files.

    :param code_files: The list of file paths to generate the localized strings for
    :param parallel: Whether to process files in parallel (default: True)
    :param max_workers: Maximum number of parallel workers (default: CPU count)

    :returns: The list of localized strings from the codebase
    """

    strings: List[LocalizedString] = []

    # For small number of files, sequential is faster due to no overhead
    if len(code_files) <= 100 or not parallel:
        for file_path in code_files:
            strings += strings_in_code_file(file_path)
        return strings

    # Parallel processing for larger file sets
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all files for processing
        future_to_file = {
            executor.submit(_process_single_file, file_path): file_path for file_path in code_files
        }

        # Collect results as they complete
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                file_strings = future.result()
                strings += file_strings
            except (IOError, InvalidLocalizedCallException, UnsupportedFileTypeError) as exception:
                log.error("Error processing %s: %s", file_path, exception)

    return strings
