"""Example auth middleware (placeholder)."""

from starlette.requests import Request
from starlette.responses import Response

class AuthMiddleware:
    async def __call__(self, request: Request, call_next):
        # placeholder: implement auth checks
        response: Response = await call_next(request)
        return response
