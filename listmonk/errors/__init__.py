class ValidationError(Exception):
    pass


class OperationNotAllowedError(ValidationError):
    pass


class ListmonkFileNotFoundError(FileNotFoundError):
    pass
