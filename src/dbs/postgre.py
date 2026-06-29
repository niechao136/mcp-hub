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
        # 如果当前 loop 已经是 Proactor，或者尚未设置，强制更换
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
            "autocommit": True
        }
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
    if _pool is None:
        return await init_pool()
    return _pool


async def init_db():
    pool = await get_db_pool()

    async with pool.connection() as conn:
        async with conn.transaction():
            print("开始执行数据库初始化 (Schema)...")

            # 创建自动更新 updated_at 的触发器函数
            await conn.execute(ddl.DDL_UPDATE_MODIFIED_COLUMN)

            # 创建用户表
            await conn.execute(ddl.DDL_USERS)
            # 创建用户表索引
            await conn.execute(ddl.DDL_USER_INDEXES)
            # 绑定 updated_at 触发器
            await conn.execute(ddl.DDL_USER_TRIGGER)

            # 加入初始管理员
            hash_pwd = pwd_context.hash(admin_pwd)
            await conn.execute(
                dml.DML_INIT_USER,
                (admin_usr, hash_pwd, admin_usr)
            )

            # 创建 LLM 模型表
            await conn.execute(ddl.DDL_LLM_MODELS)
            # 创建 LLM 模型表索引
            await conn.execute(ddl.DDL_LLM_MODELS_INDEXES)
            # 绑定 updated_at 触发器
            await conn.execute(ddl.DDL_LLM_MODELS_TRIGGER)

            # 创建 MCP 服务器表
            await conn.execute(ddl.DDL_MCP_SERVERS)
            # 创建 MCP 服务器表索引
            await conn.execute(ddl.DDL_MCP_SERVERS_INDEXES)
            # 绑定 updated_at 触发器
            await conn.execute(ddl.DDL_MCP_SERVERS_TRIGGER)

            # 创建 Agent 配置表
            await conn.execute(ddl.DDL_AGENTS)
            # 创建 Agent 配置表索引
            await conn.execute(ddl.DDL_AGENTS_INDEXES)
            # 绑定 updated_at 触发器
            await conn.execute(ddl.DDL_AGENTS_TRIGGER)

            # 创建 Agent 与 MCP 绑定表
            await conn.execute(ddl.DDL_AGENT_MCP_SERVERS)
            # 创建 Agent 与 MCP 绑定表索引
            await conn.execute(ddl.DDL_AGENT_MCP_SERVERS_INDEXES)

            # 创建 Agent 与 会话绑定表
            await conn.execute(ddl.DDL_AGENT_THREADS)
            # 创建 Agent 与 会话绑定表索引
            await conn.execute(ddl.DDL_AGENT_THREADS_INDEXES)
            # 绑定 updated_at 触发器
            await conn.execute(ddl.DDL_AGENT_THREADS_TRIGGER)

            print("数据库初始化完成 ✓")
