from fastapi import FastAPI, HTTPException, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError

from contextlib import asynccontextmanager
from db.database import engine
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from routes import blog


@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI 인스턴스 기동시 필요한 작업 수행.
    print("Starting up...")
    yield

    # FastAPI 인스턴스 종료시 필요한 작업 수행
    print("Shutting down...")
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(blog.router)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    # return JSONResponse(
    #     status_code=exc.status_code,
    #     content={
    #         "error": "처리 중 에러가 발생하였습니다.",
    #         "detail": exc.detail,
    #         "code": exc.status_code,
    #     },
    # )
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


@app.exception_handler(RequestValidationError)
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
