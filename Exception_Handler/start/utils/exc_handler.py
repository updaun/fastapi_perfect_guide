from fastapi import Request, status
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError


templates = Jinja2Templates(directory="templates")


async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return templates.TemplateResponse(
        request=request,
        name="http_error.html",
        context={
            "status_code": exc.status_code,
            "title_message": "불편을 드려 죄송합니다",
            "detail": exc.detail,
        },
        status_code=exc.status_code,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return templates.TemplateResponse(
        request=request,
        name="validation_error.html",
        context={
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "title_message": "잘못된 값을 입력하셨습니다.",
            "detail": exc.errors(),
        },
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )
