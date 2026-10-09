"""Finite diagnostic error categories; never retain an exception message."""

ERROR_TYPES = frozenset(
    {
        "OperationalError",
        "ProgrammingError",
        "IntegrityError",
        "DatabaseError",
        "InterfaceError",
        "ConnectionError",
        "TimeoutError",
        "ClientError",
        "EndpointConnectionError",
        "ConnectTimeoutError",
        "ReadTimeoutError",
        "ImproperlyConfigured",
        "ImportError",
        "ModuleNotFoundError",
        "PermissionError",
        "RuntimeError",
        "ValueError",
        "TypeError",
        "AttributeError",
        "OSError",
        "FileNotFoundError",
        "PytestUnhandledThreadExceptionWarning",
        "PytestUnraisableExceptionWarning",
        "AssertionError",
        "OtherError",
    }
)


def error_category(error):
    name = type(error).__name__
    return name if name in ERROR_TYPES else "OtherError"
