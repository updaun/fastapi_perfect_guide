from fastapi import APIRouter, Request, Depends, Form, status
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from db.database import direct_get_conn, context_get_conn
from sqlalchemy import text, Connection
from sqlalchemy.exc import SQLAlchemyError
from schemas.blog_schema import Blog, BlogData
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
    conn: Connection = Depends(context_get_conn),
):
    blog_svc.create_blog(conn, title, author, content)
    return RedirectResponse("/blogs", status_code=status.HTTP_302_FOUND)


@router.get("/modify/{id}")
def update_blog_ui(request: Request, id: int, conn=Depends(context_get_conn)):
    blog = blog_svc.get_blog_by_id(conn, id)

    return templates.TemplateResponse(
        request=request,
        name="modify_blog.html",
        context={"blog": blog},
    )


@router.post("/modify/{id}")
def update_blog(
    request: Request,
    id: int,
    title=Form(min_length=2, max_length=200),
    author=Form(max_length=100),
    content=Form(min_length=2, max_length=4000),
    conn: Connection = Depends(context_get_conn),
):

    try:
        query = f"""
        UPDATE blog 
        SET title = :title , author= :author, content= :content
        where id = :id
        """
        bind_stmt = text(query).bindparams(
            id=id, title=title, author=author, content=content
        )
        result = conn.execute(bind_stmt)
        # 해당 id로 데이터가 존재하지 않아 update 건수가 없으면 오류를 던진다.
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"해당 id {id}는(은) 존재하지 않습니다.",
            )
        conn.commit()
        return RedirectResponse(f"/blogs/show/{id}", status_code=status.HTTP_302_FOUND)
    except SQLAlchemyError as e:
        print(e)
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="요청데이터가 제대로 전달되지 않았습니다. ",
        )


@router.post("/delete/{id}")
def delete_blog(
    request: Request, id: int, conn: Connection = Depends(context_get_conn)
):
    try:
        query = f"""
        DELETE FROM blog
        where id = :id
        """

        bind_stmt = text(query).bindparams(id=id)
        result = conn.execute(bind_stmt)
        # 해당 id로 데이터가 존재하지 않아 delete 건수가 없으면 오류를 던진다.
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"해당 id {id}는(은) 존재하지 않습니다.",
            )
        conn.commit()
        return RedirectResponse("/blogs", status_code=status.HTTP_302_FOUND)

    except SQLAlchemyError as e:
        print(e)
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="요청하신 서비스가 잠시 내부적으로 문제가 발생하였습니다.",
        )
