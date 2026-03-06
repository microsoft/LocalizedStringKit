"""LocalizedStringKit handling tools."""

import filecmp
import os
import plistlib
import re
import shutil
import tempfile

from collections import defaultdict

from typing import Any, List, Optional, Tuple

from dotstrings import stringsdict_file_path
from dotstrings import DotStringsDictEntry, Variable
from dotstrings import load_dict
from dotstrings.dot_strings_entry import DotStringsEntry

from localizedstringkit import detection
from localizedstringkit import logger
from localizedstringkit.exceptions import InvalidLocalizedCallException
from localizedstringkit.files import localizable_files


log = logger.get()


def get_strings(code_files: List[str], generate_stringsdict_entires: bool) -> Tuple[dict, dict]:
    """Scan and get strings per bundle.

    :param code_files: The list of file paths to generate the code strings for
    :param bool generate_stringsdict_entires: Whether or not to generate stringsdict entries based on regex

    :returns: A tuple with first value as the bundle name to normal strings list, the second value as the bundle name to plural strings
    """

    # Get & dedupe localized strings
    localized_strings = detection.strings_in_code_files(code_files)
    localized_strings = list(set(localized_strings))
    localized_strings.sort(key=lambda string: (string.key, string.key_extension, string.comment))

    stringsdict_pattern = re.compile(r"%#@(.*?)@")

    normal_strings = defaultdict(list)
    plural_strings = defaultdict(list)

    for localized_string in localized_strings:
        matches = stringsdict_pattern.findall(localized_string.value)
        if not generate_stringsdict_entires or matches is None or len(matches) == 0:
            # No match for plural pattern or not asked to generate stringsdict entries, added to normal strings
            normal_strings[localized_string.bundle].append(localized_string)
            continue

        variables = {}
        for match in matches:
            variables[match] = Variable()

        stringsdict_entry = DotStringsDictEntry(
            localized_string.key, localized_string.value, variables
        )
        plural_strings[localized_string.bundle].append(stringsdict_entry)

    return (normal_strings, plural_strings)


def generate_code_strings_file(
    code_files: List[str], generate_stringsdict_entires: bool
) -> Tuple[dict, dict]:
    """Generate a single code file with all strings per bundle.

    :param code_files: The list of file paths to generate the code strings for
    :param bool generate_stringsdict_entires: Whether or not to generate stringsdict entries based on regex

    :returns: A tuple with first as the bundle name to the path to the temporary source code file with the standard NSLocalizedString, the second as the bundle name to plural strings
    """

    normal_strings_by_bundle, plural_strings_by_bundle = get_strings(
        code_files, generate_stringsdict_entires
    )

    strings_bundles = normal_strings_by_bundle.keys()

    # Create output bundle and path dictionary for each unique bundle
    output_paths: dict = {}
    for bundle in strings_bundles:
        output_paths[bundle] = tempfile.mktemp(suffix=".m")

    for bundle, path in output_paths.items():
        log.debug(f"Writing temporary source file at {path} for bundle {bundle}")

        with open(path, "w", encoding="utf-8") as temporary_source_file:
            strings: List = normal_strings_by_bundle[bundle]
            if strings is not None:
                for localized_string in strings:
                    temporary_source_file.write(localized_string.ns_localized_format())
                    temporary_source_file.write("\n")

    return (output_paths, plural_strings_by_bundle)


def create_or_merge_stringsdict_file(
    existing_stringsdict_path: str, entries: List[DotStringsDictEntry]
):
    """Create (if not exists) or merge the local .stringsdict file with entries given.

    :param str existing_stringsdict_path: Path to the existing .stringsdict file to merge.
                                          Will be created if not exists.
    :param List[DotStringsDictEntry] entries: The list of .stringsdict entries to write.

    :raises Exception: If the .stringsdict files has contradicting values/variables with entries
    """
    existing_entries = []

    # Check if .stringsdict for given bundle exists
    if os.path.exists(existing_stringsdict_path):
        existing_entries = load_dict(existing_stringsdict_path)

    results = {}
    for entry in entries:
        existing_entry = next(
            (
                potential_entry
                for potential_entry in existing_entries
                if potential_entry.key == entry.key
            ),
            None,
        )
        if existing_entry is not None:
            sorted_variables_for_existing_entry = sorted(existing_entry.variables.keys())
            sorted_variables_for_entry = sorted(entry.variables.keys())

            if existing_entry.value != entry.value:
                raise Exception("value names are inconsistent")
            if sorted_variables_for_entry != sorted_variables_for_existing_entry:
                raise Exception("variables names are inconsistent")

            entry.merge(existing_entry)
        results[entry.key] = entry.stringsdict_format()

    with open(existing_stringsdict_path, "wb") as stringsdict_file:
        plistlib.dump(results, stringsdict_file, sort_keys=True)


def generate_files(
    *,
    code_files: List[str],
    localized_string_kit_path: str,
    generate_stringsdict_files: bool,
) -> None:
    """Run the localization substitution process.

    :param List[str] code_files: The list of file paths to generate the .strings
                                  and .stringsdict for.
    :param str localized_string_kit_path: Path to the LocalizedStringsKit
                                           folder which contains the strings
                                           bundle and other library data.
    :param bool generate_stringsdict_files: Whether or not to generate stringsdict files.

    :raises Exception: If we can't generate the .strings/.stringdict files
    """

    if generate_stringsdict_files:
        log.info("Generating LocalizedStringKit.strings and LocalizedStringKit.stringsdict...")
    else:
        log.info("Generating LocalizedStringKit.strings...")

    # Extract strings from code files
    normal_strings_by_bundle, stringsdict_by_bundle = get_strings(
        code_files, generate_stringsdict_files
    )

    # Write .strings files directly for each bundle
    for bundle_name, strings in normal_strings_by_bundle.items():
        name = bundle_name
        if ".bundle" not in name:
            name = bundle_name + ".bundle"

        # Write .strings file directly from LocalizedString objects
        _write_strings_file(
            output_directory=os.path.join(localized_string_kit_path, name),
            strings=strings,
        )

        # We need to track the code file as well so that we can tell if things
        # have changed or not between successive runs
        m_file_name = name.replace(".bundle", ".m")
        source_code_file_path = os.path.join(localized_string_kit_path, m_file_name)
        # Write the temporary .m file with NSLocalizedString calls for tracking
        with open(source_code_file_path, "w", encoding="utf-8") as temporary_source_file:
            for localized_string in strings:
                temporary_source_file.write(localized_string.ns_localized_format())
                temporary_source_file.write("\n")

    for bundle_name, stringsdict_entries in stringsdict_by_bundle.items():
        name = bundle_name
        if ".bundle" not in name:
            name = bundle_name + ".bundle"

        # Default path is en.lproj/LocalizedStringKit.stringsdict
        file_path = stringsdict_file_path(
            os.path.join(localized_string_kit_path, name), "en", "LocalizedStringKit"
        )

        create_or_merge_stringsdict_file(file_path, stringsdict_entries)

    # Success
    log.info("Generation complete")


def _write_strings_file(output_directory: str, strings: List[Any]) -> None:
    """Write a .strings file directly from LocalizedString objects.

    :param str output_directory: The directory to write the .strings file to (will contain en.lproj)
    :param List[LocalizedString] strings: The list of LocalizedString objects to write

    :raises Exception: If we can't write the .strings file
    """
    # Create output directory
    english_strings_directory = os.path.join(output_directory, "en.lproj")
    os.makedirs(english_strings_directory, exist_ok=True)

    # Group strings by table
    strings_by_table = defaultdict(list)
    for localized_string in strings:
        strings_by_table[localized_string.table].append(localized_string)

    # Write each table to its own .strings file
    for table, table_strings in strings_by_table.items():
        output_path = os.path.join(english_strings_directory, f"{table}.strings")

        # Deduplicate by key and merge comments
        # Use a dictionary to track entries by key
        entries_by_key = {}
        for localized_string in table_strings:
            key = localized_string.key

            if key not in entries_by_key:
                # First occurrence of this key
                comments = []
                if localized_string.comment:
                    comments = [localized_string.comment]

                entries_by_key[key] = DotStringsEntry(
                    key=key,
                    value=localized_string.value,
                    comments=comments,
                )
            else:
                # Key already exists, merge comments
                existing_entry = entries_by_key[key]
                if (
                    localized_string.comment
                    and localized_string.comment not in existing_entry.comments
                ):
                    existing_entry.comments.append(localized_string.comment)

        # Write to file in sorted order by key
        with open(output_path, "w", encoding="utf-8") as strings_file:
            for key in sorted(entries_by_key.keys()):
                entry = entries_by_key[key]
                # Sort comments alphabetically
                entry.comments.sort()
                strings_file.write(entry.strings_format())
                strings_file.write("\n\n")


def generate_dot_strings_files(*, code_files: List[str], localized_string_kit_path: str) -> None:
    """Run the localization substitution process only creating .strings files.

    :param List[str] code_files: The list of file paths to generate the .strings
                                 for.
    :param str localized_string_kit_path: Path to the LocalizedStringsKit
                                           folder which contains the strings
                                           bundle and other library data.

    :raises Exception: If we can't generate the .strings files
    """

    generate_files(
        code_files=code_files,
        localized_string_kit_path=localized_string_kit_path,
        generate_stringsdict_files=False,
    )


def has_strings_dict_changes(localized_string_kit_path: str, stringsdict_by_bundle: dict) -> bool:
    """Check if there are outstanding LocalizedStringKit changes in stringsdict.

    :param str localized_string_kit_path: Path to the LocalizedStringsKit
                                          folder which contains the strings
                                          bundle and other library data.
    :param dict stringsdict_by_bundle: Expected stringsdict entries to include.
                                       Keys: bundle name, values: list of
                                       stringdict entries

    :returns: True if there are changes, False otherwise
    """
    for bundle_name, entries in stringsdict_by_bundle.items():
        name = bundle_name
        if ".bundle" not in name:
            name = bundle_name + ".bundle"
        existing_stringsdict_path = stringsdict_file_path(
            os.path.join(localized_string_kit_path, name), "en", "LocalizedStringKit"
        )

        # Check if .stringsdict for given bundle exists
        if not os.path.exists(existing_stringsdict_path):
            return True

        entries_from_file = load_dict(existing_stringsdict_path)

        # We only check if the keys and corresponding variables are the same
        # Create a list of tuples of (key, [variable names])
        keys_and_variable_names_from_file = []
        for entry in entries_from_file:
            sorted_variable_names = sorted(entry.variables.keys())
            keys_and_variable_names_from_file.append((entry.key, sorted_variable_names))

        keys_and_variable_names_from_file = sorted(
            keys_and_variable_names_from_file, key=lambda entry: entry[0]
        )

        keys_and_variable_names_from_code = []
        for entry in entries:
            sorted_variable_names = sorted(entry.variables.keys())
            keys_and_variable_names_from_code.append((entry.key, sorted_variable_names))

        keys_and_variable_names_from_code = sorted(
            keys_and_variable_names_from_code, key=lambda entry: entry[0]
        )

        if keys_and_variable_names_from_code != keys_and_variable_names_from_file:
            return True

    return False


def has_changes(
    *,
    localized_string_kit_path: str,
    code_files: List[str],
    including_stringsdict_files=False,
) -> bool:
    """Check if there are outstanding LocalizedStringKit changes.

    :param str localized_string_kit_path: Path to the LocalizedStringsKit
                                          folder which contains the strings
                                          bundle and other library data.
    :param List[str] code_files: The list of file paths to check for changes to.
    :param bool including_stringsdict_files: Whether or not to check stringsdict
                                             changes as well

    :returns: True if there are changes, False otherwise
    """

    log.info("Determining if localization needs run")

    # Generate current code file paths; Dict of bundle: output_path
    current_strings_paths, stringsdict_by_bundle = generate_code_strings_file(
        code_files, including_stringsdict_files
    )

    for bundle, path in current_strings_paths.items():
        m_file = bundle.replace(".bundle", ".m")
        if not m_file:
            # Localized calls with empty bundle get defaulted to this source file names
            m_file = "source_strings.m"

        existing_strings_path = os.path.join(localized_string_kit_path, m_file)

        # Check if .m for given bundle exists
        if not os.path.exists(existing_strings_path):
            return True

        files_differ = not filecmp.cmp(existing_strings_path, path)

        if os.path.exists(path):
            os.remove(path)

        if files_differ:
            return True

    if not including_stringsdict_files:
        return False

    return has_strings_dict_changes(
        localized_string_kit_path,
        stringsdict_by_bundle,
    )
