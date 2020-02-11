"""Log handling tools."""

import logging
from typing import Optional

_LOG: Optional[logging.Logger] = None


def get() -> logging.Logger:
    """Get (and configure if it's the first call) the logger.

    :returns: A configured logger
    """

    global _LOG  # pylint:disable=global-statement

    if _LOG is not None:
        return _LOG

    _LOG = logging.getLogger("localizedstringkit")
    _LOG.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] [%(name)s] [%(levelname)s] %(message)s"
    )
    formatter.datefmt = "%Y-%m-%d %H:%M:%S"

    consolehandler = logging.StreamHandler()
    consolehandler.setFormatter(formatter)

    _LOG.addHandler(consolehandler)

    return _LOG
