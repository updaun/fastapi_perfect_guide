from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles

from contextlib import asynccontextmanager
from db.database import engine
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates


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

from routes import blog

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
    )
