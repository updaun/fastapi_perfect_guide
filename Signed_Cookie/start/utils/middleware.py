from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class DummyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        print("### request info:", request.url, request.method)
        print("### request type:", type(request))

        response = await call_next(request)
        return response
    
class MethodOverrideMiddlware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # print("#### request url, query_params, method", 
        #       request.url, request.query_params, request.method)
        if request.method == "POST":
            query = request.query_params
            if query:
                method_override = query["_method"]
                if method_override:
                    method_override = method_override.upper()
                    if method_override in ("PUT", "DELETE"):
                        request.scope["method"] = method_override
        
        response = await call_next(request)
        return response


        
