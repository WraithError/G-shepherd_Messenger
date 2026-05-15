class GShepherdError(Exception):
    """Base exception for all G-Shepherd errors."""
    pass


class NotFoundError(GShepherdError):
    """Resource does not exist."""
    pass


class ForbiddenError(GShepherdError):
    """User lacks permission."""
    pass


class ValidationError(GShepherdError):
    """Business rule validation failed."""
    pass


class UnauthorizedError(GShepherdError):
    """User is not authenticated."""
    pass


class ConflictError(GShepherdError):
    """Resource already exists."""
    pass
