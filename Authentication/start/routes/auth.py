from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from db.database import context_get_conn
from sqlalchemy import Connection
from services import blog_svc, auth_svc
from utils import util
from schemas.blog_schema import BlogInput
from passlib.context import CryptContext
from pydantic import EmailStr

# router 생성
router = APIRouter(prefix="/auth", tags=["auth"])
# jinja2 Template 엔진 생성
templates = Jinja2Templates(directory="templates")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_hashed_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@router.get("/register")
async def register_user_ui(request: Request):
    return templates.TemplateResponse(
        request=request, name="register_user.html", context={}
    )


@router.post("/register")
async def register_uesr(
    request: Request,
    name: str = Form(min_length=2, max_length=100),
    email: EmailStr = Form(),
    password: str = Form(min_length=2, max_length=30),
    conn: Connection = Depends(context_get_conn),
):
    user = await auth_svc.get_user_by_email(conn=conn, email=email)
    if user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 사용자입니다. 다른 이메일을 사용해주세요.",
        )
    hashed_password = get_hashed_password(password)
    await auth_svc.register_user(
        conn=conn, name=name, email=email, hashed_password=hashed_password
    )
    return RedirectResponse("/blogs", status_code=status.HTTP_302_FOUND)


@router.get("/login")
async def login_ui(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={})


@router.post("/login")
async def login(
    request: Request,
    email: EmailStr = Form(),
    password: str = Form(min_length=2, max_length=30),
    conn: Connection = Depends(context_get_conn),
):
    userpass = await auth_svc.get_userpass_by_email(conn=conn, email=email)
    if userpass is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="해당 이메일 사용자는 존재하지 않습니다.",
        )
    is_correct_pw = verify_password(password, userpass.hashed_password)
    if not is_correct_pw:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="등록하신 이메일과 패스워드 정보가 입력 정보와 다릅니다.",
        )

    response = RedirectResponse("/blogs", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="user_id", value=str(userpass.id))
    return response
