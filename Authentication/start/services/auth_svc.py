from fastapi import status, UploadFile
from fastapi.exceptions import HTTPException
from sqlalchemy import text, Connection
from sqlalchemy.exc import SQLAlchemyError
from schemas.blog_schema import BlogData
from utils import util
from typing import List
from dotenv import load_dotenv
import os
import time
import aiofiles as aio


async def register_user(conn: Connection, name: str, email: str, hashed_password: str):
    try:
        query = f"""
        INSERT INTO user(name, email, hashed_password)
        values ('{name}', '{email}', '{hashed_password}')
        """

        await conn.execute(text(query))
        await conn.commit()

    except SQLAlchemyError as e:
        print(e)
        await conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="요청하신 서비스가 잠시 내부적으로 문제가 발생하였습니다.",
        )
