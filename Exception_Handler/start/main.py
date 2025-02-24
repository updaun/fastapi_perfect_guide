from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from routes import blog
from utils import exc_handler
from utils.common import lifespan


app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(blog.router)

app.add_exception_handler(
    StarletteHTTPException, exc_handler.custom_http_exception_handler
)
app.add_exception_handler(
    RequestValidationError, exc_handler.validation_exception_handler
)
