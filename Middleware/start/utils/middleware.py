from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class DummyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print("### request info:", request.url, request.method)
        print("### request type:", type(request))

        response = await call_next(request)
        return response
