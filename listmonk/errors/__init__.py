class ValidationError(Exception):
    """Raised when an argument fails client-side validation before a request is sent,
    or when the server returns an empty or malformed JSON response."""


class OperationNotAllowedError(ValidationError):
    """Raised when an operation is not permitted in the client's current state.

    For example, calling an API before the base URL has been set, or before a successful login.
    """


class ListmonkFileNotFoundError(FileNotFoundError):
    """Raised when a local file referenced for upload (e.g. a transactional email attachment) cannot be found."""
