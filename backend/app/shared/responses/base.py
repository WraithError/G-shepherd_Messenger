"""Standardized response helpers."""

def success(data: dict = None):
    return {"status": "success", "data": data}

def error(message: str, code: int = 400):
    return {"status": "error", "message": message, "code": code}
