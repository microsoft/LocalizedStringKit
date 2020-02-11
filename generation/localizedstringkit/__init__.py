"""LocalizedStringKit handling tools."""

import filecmp
import os
import re
import shutil
import tempfile
from typing import Any, List, Optional, Tuple

from dotstrings.genstrings import generate_strings
from dotstrings import LocalizedString

from localizedstringkit import detection
from localizedstringkit import logger
from localizedstringkit.exceptions import InvalidLocalizedCallException
from localizedstringkit.files import localizable_files


SOURCE_CODE_FILE_NAME: str = "source_strings.m"
BUNDLE_NAME: str = "LocalizedStringKit.bundle"

log = logger.get()


def generate_code_strings_file(code_files: List[str]) -> str:
    """Generate a single code file with all strings.

    :param code_files: The list of file paths to generate the code strings for

    :returns: The path to the temporary source code file with the standard NSLocalizedString calls
    """

    output_path = tempfile.mktemp(suffix=".m")

    localized_strings = detection.strings_in_code_files(code_files)
    localized_strings = list(set(localized_strings))

    localized_strings.sort(key=lambda string: (string.key, string.key_extension, string.comment))

    log.debug("Writing temporary source file at " + output_path)

    with open(output_path, "w") as temporary_source_file:
        for localized_string in localized_strings:
            temporary_source_file.write(localized_string.ns_localized_format())
            temporary_source_file.write("\n")

    return output_path


def generate_dot_strings_files(*, code_files: List[str], localized_string_kit_path: str) -> None:
    """Run the localization substitution process.

    :param List[str] code_files: The list of file paths to generate the .strings
                                 for.
    :param str localized_string_kit_path: Path to the LocalizedStringsKit
                                           folder which contains the strings
                                           bundle and other library data.

    :raises Exception: If we can't generate the .strings files
    """

    log.info("Generating LocalizedStringKit.strings...")

    code_strings_file: Optional[str] = None

    # Generate a single .m file with all NSLocalizedStrings in it if we haven't
    # been given files explicitly
    code_strings_file = generate_code_strings_file(code_files)

    generate_strings(
        output_directory=os.path.join(localized_string_kit_path, BUNDLE_NAME),
        file_paths=[code_strings_file],
    )

    # We need to track the code file as well so that we can tell if things
    # have changed or not between successive runs
    source_code_file_path = os.path.join(localized_string_kit_path, SOURCE_CODE_FILE_NAME)

    # Update the code strings file
    if os.path.exists(source_code_file_path):
        os.remove(source_code_file_path)

    shutil.move(code_strings_file, source_code_file_path)

    # Success
    log.info("Generation complete")


def has_changes(*, localized_string_kit_path: str, code_files: List[str]) -> bool:
    """Check if there are outstanding LocalizedStringKit changes.

    :param str localized_string_kit_path: Path to the LocalizedStringsKit
                                           folder which contains the strings
                                           bundle and other library data.
    :param List[str] code_files: The list of file paths to check for changes to.

    :returns: True if there are changes, False otherwise
    """

    log.info("Determining if localization needs run")

    existing_strings_path = os.path.join(localized_string_kit_path, SOURCE_CODE_FILE_NAME)

    if not os.path.exists(existing_strings_path):
        return True

    current_strings_path = generate_code_strings_file(code_files)

    files_differ = not filecmp.cmp(existing_strings_path, current_strings_path)

    if os.path.exists(current_strings_path):
        os.remove(current_strings_path)

    return files_differ
