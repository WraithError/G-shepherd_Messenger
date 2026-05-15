"""General helper utilities."""

from time import timezone


def timestamp_now():
    from datetime import datetime
    return datetime.now(timezone.utc)

