from fastapi import APIRouter, Request, Depends, Form, UploadFile, File, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import HTTPException
from db.database import context_get_conn
from sqlalchemy import Connection
from services import blog_svc, auth_svc
from utils import util
from schemas.blog_schema import BlogInput

# router 생성
router = APIRouter(prefix="/blogs", tags=["blogs"])
# jinja2 Template 엔진 생성
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def get_all_blogs(
    request: Request,
    conn: Connection = Depends(context_get_conn),
    session_user=Depends(auth_svc.get_session_user_opt),
):
    all_blogs = await blog_svc.get_all_blogs(conn)

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "all_blogs": all_blogs,
            "session_user": session_user,
        },
    )


@router.get("/show/{id}")
async def get_blog_by_id(
    request: Request,
    id: int,
    conn: Connection = Depends(context_get_conn),
    session_user=Depends(auth_svc.get_session_user_opt),
):
    blog = await blog_svc.get_blog_by_id(conn, id)
    is_valid_auth = auth_svc.check_valid_auth(session_user, blog.author_id, blog.email)

    blog.content = util.newline_to_br(blog.content)

    return templates.TemplateResponse(
        request=request,
        name="show_blog.html",
        context={
            "blog": blog,
            "session_user": session_user,
            "is_valid_auth": is_valid_auth,
        },
    )


@router.get("/new")
async def create_blog_ui(
    request: Request,
    session_user=Depends(auth_svc.get_session_user_prt),
):
    return templates.TemplateResponse(
        request=request, name="new_blog.html", context={"session_user": session_user}
    )


@router.post("/new")
async def create_blog(
    request: Request,
    title=Form(min_length=2, max_length=200),
    content=Form(min_length=2, max_length=4000),
    imagefile: UploadFile | None = File(None),
    conn: Connection = Depends(context_get_conn),
    session_user=Depends(auth_svc.get_session_user_prt),
):
    # print("##### imagefile:", imagefile)
    # print("#### filename:", imagefile.filename)
    image_loc = None
    author = session_user["name"]
    author_id = session_user["id"]
    if len(imagefile.filename.strip()) > 0:
        # 반드시 transactional 한 처리를 위해 upload_file()이 먼저 수행되어야 함.
        image_loc = await blog_svc.upload_file(author=author, imagefile=imagefile)
        await blog_svc.create_blog(
            conn, title=title, author_id=author_id, content=content, image_loc=image_loc
        )
    else:
        await blog_svc.create_blog(
            conn, title=title, author_id=author_id, content=content, image_loc=image_loc
        )

    return RedirectResponse("/blogs", status_code=status.HTTP_302_FOUND)


@router.get("/modify/{id}")
async def update_blog_ui(
    request: Request,
    id: int,
    conn=Depends(context_get_conn),
    session_user=Depends(auth_svc.get_session_user_prt),
):
    blog = await blog_svc.get_blog_by_id(conn, id=id)
    is_valid_auth = auth_svc.check_valid_auth(session_user, blog.author_id, blog.email)

    if not is_valid_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="해당 블로그를 수정할 권한이 없습니다.",
        )

    return templates.TemplateResponse(
        request=request,
        name="modify_blog.html",
        context={"blog": blog, "session_user": session_user},
    )


@router.put("/modify/{id}")
async def update_blog(
    request: Request,
    id: int,
    title=Form(min_length=2, max_length=200),
    content=Form(min_length=2, max_length=4000),
    imagefile: UploadFile | None = File(None),
    conn: Connection = Depends(context_get_conn),
    session_user=Depends(auth_svc.get_session_user_prt),
):
    blog = await blog_svc.get_blog_by_id(conn, id=id)
    is_valid_auth = auth_svc.check_valid_auth(session_user, blog.author_id, blog.email)

    if not is_valid_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="해당 블로그를 수정할 권한이 없습니다.",
        )

    image_loc = None
    author = session_user["name"]
    if len(imagefile.filename.strip()) > 0:
        image_loc = await blog_svc.upload_file(author=author, imagefile=imagefile)
        await blog_svc.update_blog(
            conn=conn,
            id=id,
            title=title,
            content=content,
            image_loc=image_loc,
        )
    else:
        await blog_svc.update_blog(
            conn=conn,
            id=id,
            title=title,
            content=content,
            image_loc=image_loc,
        )

    return RedirectResponse(f"/blogs/show/{id}", status_code=status.HTTP_302_FOUND)


@router.delete("/delete/{id}")
async def delete_blog(
    request: Request,
    id: int,
    conn: Connection = Depends(context_get_conn),
    session_user=Depends(auth_svc.get_session_user_prt),
):
    blog = await blog_svc.get_blog_by_id(conn=conn, id=id)
    is_valid_auth = auth_svc.check_valid_auth(session_user, blog.author_id, blog.email)

    if not is_valid_auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="해당 블로그를 삭제할 권한이 없습니다.",
        )

    await blog_svc.delete_blog(conn=conn, id=id, image_loc=blog.image_loc)
    return JSONResponse(
        content="메시지가 삭제되었습니다", status_code=status.HTTP_200_OK
    )
    # return RedirectResponse("/blogs", status_code=status.HTTP_302_FOUND)


@router.get("/show_json/{id}")
async def get_blog_by_id_json(
    request: Request, id: int, conn: Connection = Depends(context_get_conn)
):
    blog = await blog_svc.get_blog_by_id(conn, id)
    blog.content = util.newline_to_br(blog.content)

    return blog
