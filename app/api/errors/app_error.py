class AppError(Exception):
    """Base class for application-specific errors."""

    status_code: int
    title: str
    detail: str
