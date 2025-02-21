from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from routes import blog
from contextlib import asynccontextmanager
from db.database import engine
from fastapi.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # FastAPI 인스턴스 기동시 필요한 작업 수행.
    print("Starting up...")
    yield

    # FastAPI 인스턴스 종료시 필요한 작업 수행
    print("Shutting down...")
    await engine.dispose()


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(blog.router)


@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "처리 중 에러가 발생하였습니다.",
            "detail": exc.detail,
            "code": exc.status_code,
        },
    )
