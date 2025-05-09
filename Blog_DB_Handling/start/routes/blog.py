from fastapi import APIRouter, Request, Depends, status, Form
from fastapi.responses import RedirectResponse
from fastapi.exceptions import HTTPException
from fastapi.templating import Jinja2Templates
from db.database import direct_get_conn, context_get_conn
from sqlalchemy import text, Connection
from sqlalchemy.exc import SQLAlchemyError
from schemas.blog_schema import Blog, BlogData
from utils import util

# router 생성
router = APIRouter(prefix="/blogs", tags=["blogs"])
# Jinja2 템플릿을 사용하여 HTML 파일을 렌더링하는 라우터를 추가
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def get_all_blogs(request: Request):
    conn = None
    try:
        conn = direct_get_conn()
        query = """
        SELECT id, title, author, content, image_loc, modified_dt FROM blog
        """
        result = conn.execute(text(query))
        # rows = result.fetchall()
        rows = [
            BlogData(
                id=row.id,
                title=row.title,
                author=row.author,
                content=util.truncate_text(row.content),
                image_loc=row.image_loc,
                modified_dt=row.modified_dt,
            )
            for row in result
        ]
        result.close()
        return templates.TemplateResponse(
            request, "index.html", context={"all_blogs": rows}
        )
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="요청하신 서비스가 잠시 내부적으로 문제가 발생하였습니다.",
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="알수없는 이유로 서비스 오류가 발생했습니다.",
        )
    finally:
        if conn:
            conn.close()


@router.get("/show/{id}")
def get_blog_by_id(
    request: Request, id: int, conn: Connection = Depends(context_get_conn)
):
    try:
        query = f"""
        SELECT id, title, author, content, image_loc, modified_dt FROM blog WHERE id = :id
        """
        stmt = text(query)
        bind_stmt = stmt = stmt.bindparams(id=id)
        result = conn.execute(bind_stmt)
        # 만약에 한건도 찾지 못하면 오류를 던진다.
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"해당 id {id}는(은) 존재하지 않습니다.",
            )

        row = result.fetchone()
        blog = BlogData(
            id=row[0],
            title=row[1],
            author=row[2],
            content=util.newline_to_br(row[3]),
            image_loc=row[4],
            modified_dt=row[5],
        )
        result.close()
        return templates.TemplateResponse(
            request, "show_blog.html", context={"blog": blog}
        )
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="요청하신 서비스가 잠시 내부적으로 문제가 발생하였습니다.",
        )


@router.get("/new")
def create_blog_ui(request: Request):
    return templates.TemplateResponse(request, "new_blog.html", context={})


@router.post("/new")
def create_blog(
    request: Request,
    title=Form(min_length=2, max_length=200),
    author=Form(max_length=100),
    content=Form(min_length=2, max_length=4000),
    conn: Connection = Depends(context_get_conn),
):
    try:
        query = """
        INSERT INTO blog (title, author, content, modified_dt) VALUES (:title, :author, :content, NOW())
        """
        stmt = text(query)
        bind_stmt = stmt.bindparams(title=title, author=author, content=content)
        conn.execute(bind_stmt)
        conn.commit()
        return RedirectResponse(url="/blogs", status_code=status.HTTP_302_FOUND)
    except SQLAlchemyError as e:
        print(e)
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="요청데이터가 제대로 전달되지 않았습니다.",
        )


@router.get("/modify/{id}")
def modify_blog_ui(
    request: Request, id: int, conn: Connection = Depends(context_get_conn)
):
    try:
        query = """
        select id, title, author, content from blog where id = :id
        """
        stmt = text(query)
        bind_stmt = stmt.bindparams(id=id)
        result = conn.execute(bind_stmt)

        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"해당 id {id}는(은) 존재하지 않습니다.",
            )

        row = result.fetchone()
        blog = BlogData(
            id=row[0],
            title=row[1],
            author=row[2],
            content=row[3],
        )
        result.close()
        return templates.TemplateResponse(
            request, "modify_blog.html", context={"blog": blog}
        )
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="요청하신 서비스가 잠시 내부적으로 문제가 발생하였습니다.",
        )


@router.post("/modify/{id}")
def modify_blog(
    request: Request,
    id: int,
    title=Form(min_length=2, max_length=200),
    author=Form(max_length=100),
    content=Form(min_length=2, max_length=4000),
    conn: Connection = Depends(context_get_conn),
):
    try:
        query = """
        UPDATE blog SET title = :title, author = :author, content = :content, modified_dt = NOW() WHERE id = :id
        """
        stmt = text(query)
        bind_stmt = stmt.bindparams(title=title, author=author, content=content, id=id)
        result = conn.execute(bind_stmt)
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"해당 id {id}는(은) 존재하지 않습니다.",
            )
        conn.commit()
        return RedirectResponse(url="/blogs", status_code=status.HTTP_302_FOUND)
    except SQLAlchemyError as e:
        print(e)
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="요청하신 서비스가 잠시 내부적으로 문제가 발생하였습니다.",
        )


@router.post("/delete/{id}")
def delete_blog(
    request: Request, id: int, conn: Connection = Depends(context_get_conn)
):
    try:
        query = """
        DELETE FROM blog WHERE id = :id
        """
        stmt = text(query)
        bind_stmt = stmt.bindparams(id=id)
        result = conn.execute(bind_stmt)
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"해당 id {id}는(은) 존재하지 않습니다.",
            )
        conn.commit()
        return RedirectResponse(url="/blogs", status_code=status.HTTP_302_FOUND)
    except SQLAlchemyError as e:
        print(e)
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="요청하신 서비스가 잠시 내부적으로 문제가 발생하였습니다.",
        )
