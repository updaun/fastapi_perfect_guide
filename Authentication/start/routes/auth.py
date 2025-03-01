from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from db.database import context_get_conn
from sqlalchemy import Connection
from services import blog_svc
from utils import util
from schemas.blog_schema import BlogInput
from passlib.context import CryptContext

# router 생성
router = APIRouter(prefix="/auth", tags=["auth"])
# jinja2 Template 엔진 생성
templates = Jinja2Templates(directory="templates")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/register")
async def register_user_ui(request: Request):
    return templates.TemplateResponse(
        request=request, name="register_user.html", context={}
    )


@router.get("/login")
async def login_ui(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={})
