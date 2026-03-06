"""Localization exceptions."""


class InvalidLocalizedCallException(Exception):
    """Raised if there is an invalid call to Localized."""


class UnsupportedFileTypeError(ValueError):
    """Raised when attempting to process an unsupported file type."""
