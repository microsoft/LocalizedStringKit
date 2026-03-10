"""Utilities for dealing with localized strings."""

import os
import shutil
import subprocess
from typing import List, Optional

from localizedstringkit import logger

log = logger.get()


def _is_ripgrep_available() -> bool:
    """Check if ripgrep is available on the system."""

    return shutil.which("rg") is not None


def _build_ripgrep_command(root_path: str, excluded_folders: List[str]) -> List[str]:
    """Build a ripgrep command to find source files."""

    rg_cmd = ["rg", "--files", "--glob", "*.swift", "--glob", "*.m"]

    for folder in excluded_folders:
        # Convert absolute path to relative path for ripgrep glob
        rel_path = os.path.relpath(folder, root_path).rstrip(os.sep)
        # Exclude the directory and all its contents
        rg_cmd.extend(["--glob", f"!{rel_path}/"])

    rg_cmd.append(root_path)
    return rg_cmd


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
    use_ripgrep: bool = False,
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
    :param bool use_ripgrep: Whether to use ripgrep for finding files.
                             If False, the find command will be used.
                             If True, ripgrep will be used if it is available,
                             otherwise the find command will be used.

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

    if use_ripgrep and _is_ripgrep_available():
        cmd = _build_ripgrep_command(root_path=root_path, excluded_folders=excluded_folders)
        log.debug("Using ripgrep command: %s", cmd)
    else:
        cmd = _build_find_command(root_path=root_path, excluded_folders=excluded_folders)
        log.debug("Using find command: %s", cmd)

    results = []
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        assert process.stdout is not None

        for line in process.stdout:
            file_path = line.rstrip("\n")
            if file_path:
                if not os.path.isabs(file_path):
                    file_path = os.path.join(root_path, file_path)
                results.append(file_path)

        return_code = process.wait()
        if return_code != 0:
            stderr = ""
            if process.stderr is not None:
                stderr = process.stderr.read()
            raise subprocess.CalledProcessError(return_code, cmd, stderr=stderr)

    results.sort()
    return results
