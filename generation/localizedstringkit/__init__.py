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


log = logger.get()


def generate_code_strings_file(code_files: List[str]) -> dict:
    """Generate a single code file with all strings per bundle.

    :param code_files: The list of file paths to generate the code strings for

    :returns: A dictionary of bundle name and path to the temporary source code file with the standard NSLocalizedString calls for that bundle
    """

    # Get & dedupe localized strings
    localized_strings = detection.strings_in_code_files(code_files)
    localized_strings = list(set(localized_strings))

    bundles = {
        localized_string.bundle for localized_string in localized_strings if localized_string.bundle
    }

    # Create output bundle and path dictionary for each unique bundle
    output_paths: dict = {}
    for bundle in bundles:
        output_paths[bundle] = tempfile.mktemp(suffix=".m")

    localized_strings.sort(key=lambda string: (string.key, string.key_extension, string.comment))

    # Create map of bundle and list of associated LocalizedStrings
    string_map: dict = {}
    for localized_string in localized_strings:
        if string_map.get(localized_string.bundle) is None:
            string_map[localized_string.bundle] = []
            string_map[localized_string.bundle].append(localized_string)

    for bundle, path in output_paths.items():
        log.debug(f"Writing temporary source file at {path} for bundle {bundle}")

        with open(path, "w") as temporary_source_file:
            strings: List = string_map[bundle]
            if strings is not None:
                for localized_string in strings:
                    temporary_source_file.write(localized_string.ns_localized_format())
                    temporary_source_file.write("\n")

    return output_paths


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

    code_strings_file: Optional[dict] = None

    # Generate a .m file per unique bundle with all NSLocalizedStrings in it if we haven't
    # been given files explicitly
    code_strings_file = generate_code_strings_file(code_files)

    # Iterate through output_paths dictionary and generate strings for each bundle
    for bundle_name, path in code_strings_file.items():
        # Generate strings
        generate_strings(
            output_directory=os.path.join(localized_string_kit_path, bundle_name + ".bundle"),
            file_paths=[path],
        )

        # We need to track the code file as well so that we can tell if things
        # have changed or not between successive runs
        source_code_file_path = os.path.join(localized_string_kit_path, bundle_name + ".m")

        # Update the code strings file
        if os.path.exists(source_code_file_path):
            os.remove(source_code_file_path)

        shutil.move(path, source_code_file_path)

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

    # Generate current code file paths
    current_strings_paths = generate_code_strings_file(code_files)

    # Iterate through code files (1 per bundle)
    for code_file in code_files:
        existing_strings_path = os.path.join(localized_string_kit_path, code_file)

        if not os.path.exists(existing_strings_path):
            return True

        files_differ = not filecmp.cmp(existing_strings_path, current_strings_paths[code_file])

        if os.path.exists(current_strings_paths[code_file]):
            os.remove(current_strings_paths[code_file])

        if files_differ:
            return True

    # Assume no changes after iteration of code_files
    return False
