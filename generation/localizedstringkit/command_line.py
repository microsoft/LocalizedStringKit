#!/usr/bin/env python3

"""Generate the .strings files for the Localized() calls in the codebase."""

import argparse
import os
import sys

try:
    import localizedstringkit
except ImportError:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
    import localizedstringkit

log = localizedstringkit.logger.get()


def _handle_arguments() -> int:
    """Handle the command line arguments.

    :raises Exception: If any conflicting arguments are passed in

    :returns: An exit code
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--force",
        dest="force",
        action="store_true",
        default=False,
        help="Update the strings even if it is not required",
    )
    parser.add_argument(
        "-c",
        "--check",
        dest="check",
        action="store_true",
        default=False,
        help="Perform a check to see if localize needs run or not",
    )

    parser.add_argument(
        "-p",
        "--path",
        dest="path",
        type=str,
        action="store",
        required=True,
        help="Set the root code path to search for code files from",
    )

    parser.add_argument(
        "-l",
        "--localized-string-kit-path",
        dest="localized_string_kit_path",
        type=str,
        action="store",
        required=False,
        help=(
            "Set the path to the LocalizedStringKit folder in your project. This is optional. "
            + "If not defined, the LOCALIZED_STRING_KIT_PATH environment variable will be used instead. If neither are defined an error will occur."
        ),
    )

    exclusion_group = parser.add_mutually_exclusive_group()

    exclusion_group.add_argument(
        "--exclusion-file",
        dest="exclusion_file",
        type=str,
        help="The path to a file containing the folders to exclude (relative to the root path)",
    )

    exclusion_group.add_argument(
        "--exclude",
        dest="exclude",
        nargs="+",
        type=str,
        required=False,
        help="Set folders to exclude (paths should be relative to root path)",
    )

    args = parser.parse_args()

    if args.localized_string_kit_path is None:
        args.localized_string_kit_path = os.environ.get("LOCALIZED_STRING_KIT_PATH")

    if args.localized_string_kit_path is None:
        raise Exception(
            "Neither the --localized-string-kit-path flag was passed in, nor the LOCALIZED_STRING_KIT_PATH environment variable set."
        )

    if args.exclusion_file is not None:
        with open(args.exclusion_file) as exclusion_file:
            exclusions = list(map(lambda s: s.strip(), exclusion_file.readlines()))
    elif args.exclude is not None:
        exclusions = args.exclude
    else:
        exclusions = []

    exclusions = [os.path.join(args.path, path) for path in exclusions]

    log.info("Searching for code files...")
    code_files = localizedstringkit.localizable_files(
        root_path=args.path, excluded_folders=exclusions
    )
    log.info(f"{len(code_files)} file(s) found")

    try:
        if args.check:
            if localizedstringkit.has_changes(
                localized_string_kit_path=args.localized_string_kit_path, code_files=code_files
            ):
                log.info("There are string changes. Please run `olm localize`")
                return 1
        else:
            if args.force or localizedstringkit.has_changes(
                localized_string_kit_path=args.localized_string_kit_path, code_files=code_files
            ):
                localizedstringkit.generate_dot_strings_files(
                    code_files=code_files, localized_string_kit_path=args.localized_string_kit_path
                )
    except localizedstringkit.InvalidLocalizedCallException as ex:
        log.error(ex)
        return 1

    return 0


def run() -> int:
    """Entry point for poetry generated command line tool.

    :returns: An exit code
    """
    try:
        return _handle_arguments()
    except Exception as ex:
        log.error(str(ex))
        return 1


if __name__ == "__main__":
    sys.exit(run())
