from fastapi import APIRouter, Request, Depends, Form, status, File, UploadFile
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from db.database import context_get_conn
from sqlalchemy import Connection
from services import blog_svc
from utils import util


# router 생성
router = APIRouter(prefix="/blogs", tags=["blogs"])
# jinja2 Template 엔진 생성
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def get_all_blogs(request: Request, conn: Connection = Depends(context_get_conn)):
    all_blogs = blog_svc.get_all_blogs(conn)

    return templates.TemplateResponse(
        request=request, name="index.html", context={"all_blogs": all_blogs}
    )


@router.get("/show/{id}")
def get_blog_by_id(
    request: Request, id: int, conn: Connection = Depends(context_get_conn)
):
    blog = blog_svc.get_blog_by_id(conn, id)
    blog.content = util.newline_to_br(blog.content)

    return templates.TemplateResponse(
        request=request, name="show_blog.html", context={"blog": blog}
    )


@router.get("/new")
def create_blog_ui(request: Request):
    return templates.TemplateResponse(request=request, name="new_blog.html", context={})


@router.post("/new")
def create_blog(
    request: Request,
    title=Form(min_length=2, max_length=200),
    author=Form(max_length=100),
    content=Form(min_length=2, max_length=4000),
    imagefile: UploadFile | None = File(None),
    conn: Connection = Depends(context_get_conn),
):
    image_loc = None
    if len(imagefile.filename.strip()) > 0:
        image_loc = blog_svc.upload_file(author=author, imagefile=imagefile)
    blog_svc.create_blog(
        conn,
        title=title,
        author=author,
        content=content,
        image_loc=image_loc,
    )

    return RedirectResponse("/blogs", status_code=status.HTTP_302_FOUND)


@router.get("/modify/{id}")
def update_blog_ui(request: Request, id: int, conn=Depends(context_get_conn)):
    blog = blog_svc.get_blog_by_id(conn, id=id)

    return templates.TemplateResponse(
        request=request, name="modify_blog.html", context={"blog": blog}
    )


@router.post("/modify/{id}")
def update_blog(
    request: Request,
    id: int,
    title=Form(min_length=2, max_length=200),
    author=Form(max_length=100),
    content=Form(min_length=2, max_length=4000),
    imagefile: UploadFile | None = File(None),
    conn: Connection = Depends(context_get_conn),
):
    image_loc = None
    if len(imagefile.filename.strip()) > 0:
        image_loc = blog_svc.upload_file(author=author, imagefile=imagefile)
    blog_svc.update_blog(
        conn=conn,
        id=id,
        title=title,
        author=author,
        content=content,
        image_loc=image_loc,
    )
    return RedirectResponse(f"/blogs/show/{id}", status_code=status.HTTP_302_FOUND)


@router.delete("/delete/{id}")
def delete_blog(
    request: Request, id: int, conn: Connection = Depends(context_get_conn)
):
    blog = blog_svc.get_blog_by_id(conn, id=id)
    blog_svc.delete_blog(conn=conn, id=id, image_loc=blog.image_loc)
    return JSONResponse(
        content="블로그가 삭제되었습니다.", status_code=status.HTTP_200_OK
    )
    # return RedirectResponse("/blogs", status_code=status.HTTP_302_FOUND)
