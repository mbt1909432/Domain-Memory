
# 导入resume相关数据库模型

from models import user_profile_facts_database
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import sessionmaker
from utils.config import DATABASE_URL, LOG,REDIS_URL
from sqlalchemy.exc import OperationalError

from database.reg_instance import REG

import redis.exceptions
import redis.asyncio as redis

engine = create_engine(DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():  # ->Generator[SessionLocal, None, None]:
    db = SessionLocal()
    #TODO: 因为healthcheck这里或许可以删除 fastapi部分不需要再注入了
    try:
        yield db
    finally:
        db.close()


def check_table_exists():
    """检查table是否存在"""
    inspector = inspect(engine)
    return inspector.get_table_names()


def create_tables():
    LOG.info(f"当前数据表为:{str(check_table_exists())}")
    REG.metadata.create_all(engine)
    LOG.info("表创建成功")
    LOG.info(f"当前数据表为:{str(check_table_exists())}")


def check_table(table_name):
    with next(get_db()) as session:
        selected_table = select(table_name)
        print(selected_table)
        results = session.execute(selected_table).scalars().all()  # 需要all否则无法检测none
        if results:
            for data in results:
                print(data)
        else:
            print("____")
            LOG.info("此表无数据")


def db_health_check() -> bool:
    try:
        conn = engine.connect()
    except OperationalError as e:
        LOG.error(f"Database connection failed: {e}")
        return False
    else:
        conn.close()
        return True


async def redis_health_check() -> bool:
    """检查Redis连接健康状态"""
    try:
        async with get_redis_client() as redis_client:
            LOG.info("正在进行Redis健康检查...")
            await redis_client.ping()
            LOG.info("Redis连接正常")
    except redis.ConnectionError as e:
        LOG.error(f"Redis连接失败: {e}")
        return False
    else:
        return True






def init_redis_pool():
    global REDIS_POOL
    REDIS_POOL = redis.ConnectionPool.from_url(REDIS_URL, decode_responses=True)


def get_redis_client() -> redis.Redis:
    if REDIS_POOL is not None:
        return redis.Redis(connection_pool=REDIS_POOL, decode_responses=True)
    else:
        return redis.Redis.from_url(REDIS_URL, decode_responses=True)



async def close_connection():
    """关闭database redis链接"""
    engine.dispose()
    if REDIS_POOL is not None:
        await REDIS_POOL.aclose()
    LOG.info("Connections closed")

create_tables()

if __name__ == "__main__":
    pass
