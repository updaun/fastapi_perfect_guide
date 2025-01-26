from sqlalchemy import create_engine, Connection
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool, NullPool
from contextlib import contextmanager
from fastapi import status
from fastapi.exceptions import HTTPException
import os

# database connection URL
DATABASE_CONN = "mysql+mysqlconnector://test:root1234@192.168.45.147:3306/blog_db"


engine = create_engine(
    DATABASE_CONN,  # echo=True,
    poolclass=QueuePool,
    # poolclass=NullPool, # Connection Pool 사용하지 않음.
    pool_size=10,
    max_overflow=0,
    pool_recycle=300,
)


def direct_get_conn():
    conn = None
    try:
        conn = engine.connect()
        return conn
    except SQLAlchemyError as e:
        print(e)
        raise e


def context_get_conn():
    conn = None
    try:
        conn = engine.connect()
        yield conn
    except SQLAlchemyError as e:
        print(e)
        raise e
    finally:
        if conn:
            conn.close()
