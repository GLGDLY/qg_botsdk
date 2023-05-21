class IdTokenMissing(Exception):
    """Raised when id or token is missing"""

    ...


class IdTokenError(Exception):
    """Raised when id or token is invalid"""

    ...


class WaitTimeoutError(Exception):
    """Raised when api.wait_for() is timeout"""

    ...


class WaitError(Exception):
    """Raised when api.wait_for() got an error"""

    ...
