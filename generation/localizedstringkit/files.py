"""Utilities for dealing with localized strings."""

import os
import subprocess
from typing import List, Optional

from localizedstringkit import logger

log = logger.get()


def _build_find_command(root_path: str, excluded_folders: List[str]) -> List[str]:
    """Build a find command that prunes excluded folders before file matching."""

    find_cmd = ["find", root_path]

    if excluded_folders:
        find_cmd.extend(["("])
        for index, folder in enumerate(excluded_folders):
            if index > 0:
                find_cmd.extend(["-o"])
            find_cmd.extend(["-path", folder])
        find_cmd.extend([")", "-prune", "-o"])

    find_cmd.extend(["-type", "f", "(", "-name", "*.swift", "-o", "-name", "*.m", ")", "-print"])

    return find_cmd


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

    :raises ValueError: If neither excluded_folders nor exclusion_file_path is set.
    :raise CalledProcessError: If the find command fails.

    :returns: The list of files which should be processed
    """

    if excluded_folders is None and exclusion_file_path is None:
        excluded_folders = []
    elif excluded_folders is not None and exclusion_file_path is not None:
        raise ValueError("Either excluded_folders or exclusion_file_path should be set")
    elif exclusion_file_path is not None:
        with open(exclusion_file_path, encoding="utf-8") as exclusion_file:
            excluded_folders = list(map(lambda x: x.strip(), exclusion_file.readlines()))

    assert excluded_folders is not None

    excluded_folders = [
        os.path.normpath(os.path.join(root_path, folder))
        for folder in excluded_folders
        if folder.strip()
    ]

    log.debug("Fetching localizable files")

    results = []

    # Prune excluded directories in find to reduce traversal work.
    find_cmd = _build_find_command(root_path=root_path, excluded_folders=excluded_folders)

    log.debug("Running find command: %s", find_cmd)

    with subprocess.Popen(
        find_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        assert process.stdout is not None

        for line in process.stdout:
            file_path = line.rstrip("\n")
            if file_path:
                results.append(file_path)

        return_code = process.wait()
        if return_code != 0:
            stderr = ""
            if process.stderr is not None:
                stderr = process.stderr.read()
            raise subprocess.CalledProcessError(return_code, find_cmd, stderr=stderr)

    results.sort()
    return results
