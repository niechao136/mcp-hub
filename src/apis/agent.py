from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Path, Body

from src.dbs.postgre import get_db_pool
from src.dbs import dml
from src.schemas.api import DataResult, PageResult, PageParams
from src.schemas.auth import TokenDict
from src.schemas.agent import (
    AgentInfo, AgentCreate, AgentUpdate, AgentBatchDelete,
    AgentMcpInfo, AgentMcpCreate,
    AgentThreadInfo, AgentThreadCreate
)
from src.utils.auth import get_current_user, get_current_admin_user


agent_router = APIRouter(
    prefix="/agent",
    tags=["智能体管理"]
)


@agent_router.get(
    path="/list",
    response_model=DataResult[PageResult[AgentInfo]],
    summary="Agent 列表",
    description="获取 Agent 列表，支持分页、排序。admin 可以查看所有，普通用户只能查看自己创建的。",
)
async def get_agent_list(
    params: Annotated[PageParams, Depends()],
    user: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    order_by = params.order_by or "created_at"
    direction = params.direction or "desc"

    allowed_columns = ["id", "name", "is_active", "created_by", "created_at", "updated_at"]
    if order_by not in allowed_columns:
        order_by = "created_at"

    if direction not in ["asc", "desc"]:
        direction = "desc"

    is_admin = user.role == "admin"
    sql_list = dml.DML_AGENT_LIST.format(order_by=order_by, direction=direction)

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(sql_list, (user.id, is_admin, params.size, params.offset))
            rows = await cur.fetchall()

            cur_count = await conn.execute(dml.DML_AGENT_COUNT, (user.id, is_admin))
            count_row = await cur_count.fetchone()

    total = count_row["total"] if count_row else 0

    return DataResult(
        status=1,
        data=PageResult(
            total=total,
            data=[AgentInfo(**row) for row in rows],
            page=params.page,
            size=params.size,
        ),
    )


@agent_router.get(
    path="/count",
    response_model=DataResult[int],
    summary="Agent 总数",
    description="获取未删除 Agent 的总数。admin 可以查看所有，普通用户只能查看自己创建的。",
)
async def get_agent_count(
    user: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    is_admin = user.role == "admin"

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_AGENT_COUNT, (user.id, is_admin))
            row = await cur.fetchone()

    total = row["total"] if row else 0
    return DataResult(status=1, data=total)


@agent_router.get(
    path="/active",
    response_model=DataResult[list[AgentInfo]],
    summary="启用的 Agent 列表",
    description="获取所有启用的 Agent 列表，用于前端选择。",
)
async def get_active_agents(
    user: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_AGENT_LIST_ACTIVE)
            rows = await cur.fetchall()

    return DataResult(status=1, data=[AgentInfo(**row) for row in rows])


@agent_router.post(
    path="",
    response_model=DataResult[AgentInfo],
    summary="新增 Agent",
    description="创建新的 Agent 配置。",
)
async def create_agent(
    agent: Annotated[AgentCreate, Body(description="Agent 信息")],
    user: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(
                dml.DML_AGENT_CREATE,
                (
                    agent.name,
                    agent.description,
                    agent.llm_model_id,
                    agent.system_prompt,
                    agent.temperature,
                    agent.max_tokens,
                    agent.memory_strategy.value,
                    agent.memory_window,
                    agent.is_active,
                    user.id,
                ),
            )
            row = await cur.fetchone()

            if not row:
                return DataResult(status=0, msg="Agent name already exists")

            cur_model = await conn.execute(dml.DML_LLM_MODEL_GET_BY_ID, (agent.llm_model_id,))
            model_row = await cur_model.fetchone()
            llm_model_name = model_row["display_name"] if model_row else None

    agent_data = AgentInfo(**row, llm_model_name=llm_model_name)
    return DataResult(status=1, data=agent_data)


@agent_router.get(
    path="/{agent_id}",
    response_model=DataResult[AgentInfo],
    summary="获取 Agent 信息",
    description="获取指定 Agent 的详细信息。",
)
async def get_agent_info(
    agent_id: Annotated[UUID, Path(description="Agent ID")],
    _: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_AGENT_GET_BY_ID, (agent_id,))
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Agent not found")

    return DataResult(status=1, data=AgentInfo(**row))


@agent_router.put(
    path="/{agent_id}",
    response_model=DataResult[AgentInfo],
    summary="修改 Agent",
    description="修改指定 Agent 的配置。",
)
async def update_agent(
    agent_id: Annotated[UUID, Path(description="Agent ID")],
    agent: Annotated[AgentUpdate, Body(description="Agent 信息")],
    _: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur_get = await conn.execute(dml.DML_AGENT_GET_BY_ID, (agent_id,))
            existing = await cur_get.fetchone()

            if not existing:
                return DataResult(status=0, msg="Agent not found")

            name = agent.name if agent.name is not None else existing["name"]
            description = agent.description if agent.description is not None else existing["description"]
            llm_model_id = agent.llm_model_id if agent.llm_model_id is not None else existing["llm_model_id"]
            system_prompt = agent.system_prompt if agent.system_prompt is not None else existing["system_prompt"]
            temperature = agent.temperature if agent.temperature is not None else existing["temperature"]
            max_tokens = agent.max_tokens if agent.max_tokens is not None else existing["max_tokens"]
            memory_strategy = agent.memory_strategy.value if agent.memory_strategy is not None else existing["memory_strategy"]
            memory_window = agent.memory_window if agent.memory_window is not None else existing["memory_window"]
            is_active = agent.is_active if agent.is_active is not None else existing["is_active"]

            cur = await conn.execute(
                dml.DML_AGENT_UPDATE,
                (
                    name,
                    description,
                    llm_model_id,
                    system_prompt,
                    temperature,
                    max_tokens,
                    memory_strategy,
                    memory_window,
                    is_active,
                    agent_id,
                ),
            )
            row = await cur.fetchone()

            if not row:
                return DataResult(status=0, msg="Update failed")

            cur_model = await conn.execute(dml.DML_LLM_MODEL_GET_BY_ID, (llm_model_id,))
            model_row = await cur_model.fetchone()
            llm_model_name = model_row["display_name"] if model_row else None

    agent_data = AgentInfo(**row, llm_model_name=llm_model_name)
    return DataResult(status=1, data=agent_data)


@agent_router.post(
    path="/batch-delete",
    response_model=DataResult[list[dict]],
    summary="批量删除 Agent",
    description="软删除指定的多个 Agent。",
)
async def delete_agents(
    body: Annotated[AgentBatchDelete, Body(description="Agent ID 列表")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    if not body.ids:
        return DataResult(status=0, msg="ids cannot be empty")

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_AGENT_DELETE, (body.ids,))
            rows = await cur.fetchall()

    deleted = [{"id": row["id"], "name": row["name"]} for row in rows]
    return DataResult(status=1, data=deleted)


@agent_router.get(
    path="/{agent_id}/mcp-servers",
    response_model=DataResult[list[AgentMcpInfo]],
    summary="获取 Agent 关联的 MCP Server",
    description="获取指定 Agent 关联的所有 MCP Server。",
)
async def get_agent_mcp_servers(
    agent_id: Annotated[UUID, Path(description="Agent ID")],
    _: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_AGENT_MCP_LIST, (agent_id,))
            rows = await cur.fetchall()

    return DataResult(status=1, data=[AgentMcpInfo(**row) for row in rows])


@agent_router.post(
    path="/{agent_id}/mcp-servers",
    response_model=DataResult[AgentMcpInfo],
    summary="关联 MCP Server",
    description="为指定 Agent 关联 MCP Server。",
)
async def add_agent_mcp_server(
    agent_id: Annotated[UUID, Path(description="Agent ID")],
    mcp: Annotated[AgentMcpCreate, Body(description="MCP Server 关联信息")],
    _: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(
                dml.DML_AGENT_MCP_CREATE,
                (agent_id, mcp.mcp_server_id, mcp.allowed_tools, mcp.priority),
            )
            row = await cur.fetchone()

            if not row:
                return DataResult(status=0, msg="Failed to add MCP server")

            cur_server = await conn.execute(dml.DML_MCP_SERVER_GET_BY_ID, (mcp.mcp_server_id,))
            server_row = await cur_server.fetchone()
            mcp_server_name = server_row["name"] if server_row else None

    mcp_data = AgentMcpInfo(**row, mcp_server_name=mcp_server_name)
    return DataResult(status=1, data=mcp_data)


@agent_router.delete(
    path="/{agent_id}/mcp-servers/{mcp_server_id}",
    response_model=DataResult[dict],
    summary="取消关联 MCP Server",
    description="取消指定 Agent 与 MCP Server 的关联。",
)
async def remove_agent_mcp_server(
    agent_id: Annotated[UUID, Path(description="Agent ID")],
    mcp_server_id: Annotated[UUID, Path(description="MCP Server ID")],
    _: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_AGENT_MCP_DELETE, (agent_id, mcp_server_id))
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Association not found")

    return DataResult(status=1, data={"id": row["id"], "mcp_server_id": row["mcp_server_id"]})


@agent_router.get(
    path="/{agent_id}/threads",
    response_model=DataResult[PageResult[AgentThreadInfo]],
    summary="Agent 会话列表",
    description="获取指定 Agent 的会话列表。",
)
async def get_agent_threads(
    agent_id: Annotated[UUID, Path(description="Agent ID")],
    params: Annotated[PageParams, Depends()],
    _: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_AGENT_THREAD_LIST, (agent_id, params.size, params.offset))
            rows = await cur.fetchall()

            cur_count = await conn.execute(dml.DML_AGENT_THREAD_COUNT, (agent_id,))
            count_row = await cur_count.fetchone()

    total = count_row["total"] if count_row else 0

    return DataResult(
        status=1,
        data=PageResult(
            total=total,
            data=[AgentThreadInfo(**row) for row in rows],
            page=params.page,
            size=params.size,
        ),
    )


@agent_router.post(
    path="/threads",
    response_model=DataResult[AgentThreadInfo],
    summary="创建会话",
    description="创建新的 Agent 会话。",
)
async def create_agent_thread(
    thread: Annotated[AgentThreadCreate, Body(description="会话信息")],
    user: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(
                dml.DML_AGENT_THREAD_CREATE,
                (thread.thread_id, thread.agent_id, user.id, thread.title, thread.agent_snapshot),
            )
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Failed to create thread")

    return DataResult(status=1, data=AgentThreadInfo(**row))


@agent_router.get(
    path="/threads/{thread_id}",
    response_model=DataResult[AgentThreadInfo],
    summary="获取会话信息",
    description="获取指定会话的详细信息。",
)
async def get_agent_thread_info(
    thread_id: Annotated[str, Path(description="会话 ID")],
    _: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_AGENT_THREAD_GET_BY_ID, (thread_id,))
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Thread not found")

    return DataResult(status=1, data=AgentThreadInfo(**row))


@agent_router.delete(
    path="/threads/{thread_id}",
    response_model=DataResult[dict],
    summary="删除会话",
    description="软删除指定会话。",
)
async def delete_agent_thread(
    thread_id: Annotated[str, Path(description="会话 ID")],
    _: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_AGENT_THREAD_DELETE, (thread_id,))
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Thread not found")

    return DataResult(status=1, data={"thread_id": row["thread_id"]})