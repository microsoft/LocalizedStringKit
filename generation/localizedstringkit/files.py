"""Utilities for dealing with localized strings."""

import os
import subprocess
from typing import List, Optional

from localizedstringkit import logger

log = logger.get()


def localizable_files(
    *,
    root_path: str,
    excluded_folders: Optional[List[str]] = None,
    exclusion_file_path: Optional[str] = None,
) -> List[str]:
    """Find all source files which should be processed.

    :param str root_path: The path to start the search from
    :param Optional[List[str]] excluded_folders: The paths to any folders to
                                                 exclude from the results. This
                                                 should be relative to the root
                                                 path. _Note:_ Only this OR
                                                 `exclusion_file_path` should be
                                                 set.
    :param Optional[str] exclusion_file_path: The paths to the exclusion file
                                              which contains all the excluded
                                              paths. These paths should be
                                              relative to the root path, but
                                              this parameter should be an
                                              absolute path. _Note:_ Only this
                                              OR `excluded_folders` should be
                                              set.

    :raises Exception: If neither excluded_folders not exclusion_file_path is set.

    :returns: The list of files which should be processed
    """

    if excluded_folders is None and exclusion_file_path is None:
        excluded_folders = []
    elif excluded_folders is not None and exclusion_file_path is not None:
        raise Exception("Either excluded_folders or exclusion_file_path should be set")
    elif exclusion_file_path is not None:
        with open(exclusion_file_path) as exclusion_file:
            excluded_folders = list(map(lambda x: x.strip(), exclusion_file.readlines()))

    assert excluded_folders is not None

    excluded_folders = [os.path.join(root_path, folder) for folder in excluded_folders]

    log.debug("Fetching localizable files")

    results = []

    # Execute find commands
    find_cmd = ["find", root_path, "-type", "f", "-name", "*.swift", "-o", "-name", "*.m"]

    log.debug(f"Running find command: {find_cmd}")

    find_result = subprocess.run(
        find_cmd, universal_newlines=True, check=True, stdout=subprocess.PIPE
    ).stdout

    for file_path in find_result.split("\n"):
        if len(file_path) == 0:
            continue

        is_excluded = False

        for excluded_folder in excluded_folders:
            if os.path.commonpath([excluded_folder, file_path]) == excluded_folder:
                is_excluded = True
                break

        if is_excluded:
            continue

        if len(file_path) > 0:
            # Save source file path
            results.append(file_path)

    results.sort()
    return results
