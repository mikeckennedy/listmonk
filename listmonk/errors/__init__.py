class ValidationError(Exception):
    pass


class OperationNotAllowedError(ValidationError):
    pass


class FileNotFoundError(ValidationError):
    pass
