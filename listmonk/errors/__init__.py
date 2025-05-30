class ValidationError(Exception):
    pass


class OperationNotAllowedError(ValidationError):
    pass


class ListmonkFileNotFoundError(ValidationError):
    pass
