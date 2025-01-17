from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import QueuePool, NullPool

# database connection URL
DATABASE_CONN = "mysql+mysqlconnector://test:root1234@192.168.45.147:3306/blog_db"

engine = create_engine(
    DATABASE_CONN,
    # echo=True,
    poolclass=QueuePool,
    # poolclass=NullPool,
    pool_size=10,
    max_overflow=0,
)


def context_execute_sleep():
    # with절을 사용하면 conn.close()를 호출하지 않아도 자동으로 close()를 호출한다.
    with engine.connect() as conn:
        query = "select sleep(5)"
        result = conn.execute(text(query))
        result.close()
        # conn.close()


for ind in range(20):
    print("loop index:", ind)
    context_execute_sleep()

print("end of loop")
