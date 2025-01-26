from fastapi import APIRouter, Request, Depends
from db.database import direct_get_conn, context_get_conn
from sqlalchemy import text, Connection
from sqlalchemy.exc import SQLAlchemyError
from schemas.blog_schema import Blog, BlogData


# router 생성
router = APIRouter(prefix="/blogs", tags=["blogs"])


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
                content=row.content,
                image_loc=row.image_loc,
                modified_dt=row.modified_dt,
            )
            for row in result
        ]
        result.close()
        return rows
    except SQLAlchemyError as e:
        print(e)
        raise e
    finally:
        if conn:
            conn.close()


@router.get("/show/{id}")
def get_blog_by_id(
    request: Request, id: int, conn: Connection = Depends(context_get_conn)
):
    try:
        query = f"""
        SELECT id, title, author, content, image_loc, modified_dt FROM blog WHERE id = {id}
        """
        stmt = text(query)
        result = conn.execute(stmt)

        row = result.fetchone()
        blog = BlogData(
            id=row[0],
            title=row[1],
            author=row[2],
            content=row[3],
            image_loc=row[4],
            modified_dt=row[5],
        )
        result.close()
        return blog
    except SQLAlchemyError as e:
        print(e)
        raise e
