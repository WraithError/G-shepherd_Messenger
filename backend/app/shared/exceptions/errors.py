"""Application exceptions (placeholders)."""

class AppError(Exception):
    """Base application exception."""
    pass

class NotFoundError(AppError):
    pass

class ValidationError(AppError):
    pass
