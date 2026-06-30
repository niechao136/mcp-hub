import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import os
from dotenv import load_dotenv
from typing import Optional

from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection
from psycopg.rows import dict_row, DictRow

from src.utils.security import pwd_context
from src.dbs import ddl, dml


load_dotenv()


host = os.getenv("POSTGRESQL_HOST", "localhost")
port = os.getenv("POSTGRESQL_PORT", 5432)
user = os.getenv("POSTGRESQL_USER", "root")
password = os.getenv("POSTGRESQL_PASS")
database = os.getenv("POSTGRESQL_NAME", "mcp_hub")

admin_usr = os.getenv("ADMIN_USERNAME", "admin")
admin_pwd = os.getenv("ADMIN_PASSWORD", "admin@123")

CONN_INFO = f"postgresql://{user}:{password}@{host}:{port}/{database}"

_pool: Optional[AsyncConnectionPool[AsyncConnection[DictRow]]] = None


def force_selector_loop():
    if sys.platform == 'win32':
        if not isinstance(asyncio.get_event_loop_policy(), asyncio.WindowsSelectorEventLoopPolicy):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


async def init_pool():
    force_selector_loop()
    global _pool

    if _pool is not None:
        return _pool
    
    print(f"正在初始化数据库连接池...")
    pool = AsyncConnectionPool(
        conninfo=CONN_INFO,
        min_size=2,
        max_size=20,
        open=False,
        connection_class=AsyncConnection[DictRow],
        kwargs={
            "row_factory": dict_row,
        },
    )
    await pool.open()
    _pool = pool
    print(f"连接池初始化成功: {_pool}")
    return pool


async def close_pool():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        print("数据库连接池已关闭")


async def get_db_pool() -> AsyncConnectionPool[AsyncConnection[DictRow]]:
    global _pool
    if _pool is None:
        return await init_pool()
    
    try:
        async with _pool.connection() as conn:
            await conn.execute("SELECT 1")
    except Exception:
        print("检测到连接池失效，重新初始化...")
        await close_pool()
        return await init_pool()
    
    return _pool


async def init_db():
    pool = await get_db_pool()

    async with pool.connection() as conn:
        async with conn.transaction():
            print("开始执行数据库初始化 (Schema)...")

            await conn.execute(ddl.DDL_UPDATE_MODIFIED_COLUMN)

            await conn.execute(ddl.DDL_USERS)
            await conn.execute(ddl.DDL_USER_INDEXES)
            await conn.execute(ddl.DDL_USER_TRIGGER)

            hash_pwd = pwd_context.hash(admin_pwd)
            await conn.execute(
                dml.DML_INIT_USER,
                (admin_usr, hash_pwd, admin_usr)
            )

            await conn.execute(ddl.DDL_LLM_MODELS)
            await conn.execute(ddl.DDL_LLM_MODELS_INDEXES)
            await conn.execute(ddl.DDL_LLM_MODELS_TRIGGER)

            await conn.execute(ddl.DDL_MCP_SERVERS)
            await conn.execute(ddl.DDL_MCP_SERVERS_INDEXES)
            await conn.execute(ddl.DDL_MCP_SERVERS_TRIGGER)

            await conn.execute(ddl.DDL_AGENTS)
            await conn.execute(ddl.DDL_AGENTS_INDEXES)
            await conn.execute(ddl.DDL_AGENTS_TRIGGER)

            await conn.execute(ddl.DDL_AGENT_MCP_SERVERS)
            await conn.execute(ddl.DDL_AGENT_MCP_SERVERS_INDEXES)

            await conn.execute(ddl.DDL_AGENT_THREADS)
            await conn.execute(ddl.DDL_AGENT_THREADS_INDEXES)
            await conn.execute(ddl.DDL_AGENT_THREADS_TRIGGER)

            print("数据库初始化完成 ✓")