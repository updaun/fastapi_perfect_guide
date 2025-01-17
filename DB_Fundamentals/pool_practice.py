from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.exc import SQLAlchemyError

# database connection URL
DATABASE_CONN = "mysql+mysqlconnector://test:root1234@192.168.45.147:3306/blog_db"
# engine 생성
# engine = create_engine(DATABASE_CONN)
# engine = create_engine(
#     DATABASE_CONN,
#     poolclass=QueuePool,
#     pool_size=10,  # pool에 유지할 connection 수 제한
#     max_overflow=0,  # pool에 추가로 생성할 connection 수 제한
# )
engine = create_engine(
    DATABASE_CONN,
    poolclass=NullPool,  # NullPool은 connection pool을 사용하지 않음. # 새로운 커넥션이 계속 생김
)
print("#### engine created")


def direct_execute_sleep(is_close: bool = False):
    conn = engine.connect()
    query = "select sleep(5)"
    result = conn.execute(text(query))
    # rows = result.fetchall()
    # print(rows)
    result.close()

    if is_close:
        conn.close()
        print("conn closed")


for ind in range(20):
    print("loop index:", ind)
    direct_execute_sleep(is_close=True)  # False라면 계속 connection을 유지하고 있음.
    # connection pool로 반환 후, 다시 connection을 얻어옴.

print("#### end of script")

# 커넥션 풀 확인 SQL
# select * from sys.session where db='blog_db' order by conn_id;

# 커넥션 풀 초과
# sqlalchemy.exc.TimeoutError: QueuePool limit of size 10 overflow 0 reached, connection timed out, timeout 30.00 (Background on this error at: https://sqlalche.me/e/20/3o7r)
