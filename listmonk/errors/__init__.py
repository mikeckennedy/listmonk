class ValidationError(Exception):
    """Raised when an argument fails client-side validation before a request is sent,
    or when the server returns an empty or malformed JSON response.

    Examples:
        >>> import listmonk
        >>> from listmonk.errors import ValidationError
        >>> try:
        ...     listmonk.set_url_base('listmonk.somedomain.tech')  # no scheme
        ... except ValidationError as e:
        ...     print(e)
        The url must start with the HTTP scheme (http:// or https://).
    """


class OperationNotAllowedError(ValidationError):
    """Raised when an operation is not permitted in the client's current state.

    For example, calling an API before the base URL has been set, or before a successful login.
    It subclasses ValidationError, so an ``except ValidationError`` clause catches it too.

    Examples:
        >>> import listmonk
        >>> from listmonk.errors import OperationNotAllowedError
        >>> try:
        ...     listmonk.lists()  # before set_url_base() and login()
        ... except OperationNotAllowedError as e:
        ...     print(e)
        URL Base must be set to proceed.
    """


class ListmonkFileNotFoundError(FileNotFoundError):
    """Raised when a local file referenced for upload (e.g. a transactional email attachment) cannot be found.

    Examples:
        >>> import listmonk
        >>> from pathlib import Path
        >>> from listmonk.errors import ListmonkFileNotFoundError
        >>> try:
        ...     listmonk.upload_media(Path('/no/such/chart.png'))
        ... except ListmonkFileNotFoundError as e:
        ...     print(e)
        File /no/such/chart.png does not exist
    """
