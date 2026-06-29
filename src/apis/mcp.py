from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Path, Body

from src.dbs.postgre import get_db_pool
from src.dbs import dml
from src.schemas.api import DataResult, PageResult, PageParams
from src.schemas.auth import TokenDict
from src.schemas.mcp import McpServerInfo, McpServerCreate, McpServerUpdate, McpServerBatchDelete
from src.utils.auth import get_current_user, get_current_admin_user


mcp_router = APIRouter(
    prefix="/mcp",
    tags=["MCP 管理"]
)


@mcp_router.get(
    path="/servers",
    response_model=DataResult[list[McpServerInfo]],
    summary="获取 MCP Server 列表",
    description="获取所有未删除的 MCP Server 列表。",
)
async def get_mcp_servers(
    user: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_MCP_SERVER_LIST_ACTIVE)
            rows = await cur.fetchall()

    return DataResult(status=1, data=[McpServerInfo(**row) for row in rows])


@mcp_router.get(
    path="/servers/list",
    response_model=DataResult[PageResult[McpServerInfo]],
    summary="MCP Server 列表",
    description="获取 MCP Server 列表，支持分页、排序。",
)
async def get_mcp_server_list(
    params: Annotated[PageParams, Depends()],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    order_by = params.order_by or "created_at"
    direction = params.direction or "desc"

    allowed_columns = ["id", "name", "transport", "status", "created_by", "created_at", "updated_at"]
    if order_by not in allowed_columns:
        order_by = "created_at"

    if direction not in ["asc", "desc"]:
        direction = "desc"

    sql_list = dml.DML_MCP_SERVER_LIST.format(order_by=order_by, direction=direction)

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(sql_list, (params.size, params.offset))
            rows = await cur.fetchall()

            cur_count = await conn.execute(dml.DML_MCP_SERVER_COUNT)
            count_row = await cur_count.fetchone()

    total = count_row["total"] if count_row else 0

    return DataResult(
        status=1,
        data=PageResult(
            total=total,
            data=[McpServerInfo(**row) for row in rows],
            page=params.page,
            size=params.size,
        ),
    )


@mcp_router.get(
    path="/servers/count",
    response_model=DataResult[int],
    summary="MCP Server 总数",
    description="获取未删除 MCP Server 的总数。",
)
async def get_mcp_server_count(
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_MCP_SERVER_COUNT)
            row = await cur.fetchone()

    total = row["total"] if row else 0
    return DataResult(status=1, data=total)


@mcp_router.post(
    path="/servers",
    response_model=DataResult[McpServerInfo],
    summary="新增 MCP Server",
    description="创建新的 MCP Server 配置。",
)
async def create_mcp_server(
    server: Annotated[McpServerCreate, Body(description="MCP Server 信息")],
    user: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(
                dml.DML_MCP_SERVER_CREATE,
                (
                    server.name,
                    server.description,
                    server.transport,
                    server.command,
                    server.args or [],
                    server.env or {},
                    server.url,
                    server.headers or {},
                    "unknown",
                    user.id,
                ),
            )
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Server name already exists")

    return DataResult(status=1, data=McpServerInfo(**row))


@mcp_router.get(
    path="/servers/{server_id}",
    response_model=DataResult[McpServerInfo],
    summary="获取 MCP Server 信息",
    description="获取指定 MCP Server 的详细信息。",
)
async def get_mcp_server_info(
    server_id: Annotated[UUID, Path(description="MCP Server ID")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_MCP_SERVER_GET_BY_ID, (server_id,))
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Server not found")

    return DataResult(status=1, data=McpServerInfo(**row))


@mcp_router.put(
    path="/servers/{server_id}",
    response_model=DataResult[McpServerInfo],
    summary="修改 MCP Server",
    description="修改指定 MCP Server 的配置。",
)
async def update_mcp_server(
    server_id: Annotated[UUID, Path(description="MCP Server ID")],
    server: Annotated[McpServerUpdate, Body(description="MCP Server 信息")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur_get = await conn.execute(dml.DML_MCP_SERVER_GET_BY_ID, (server_id,))
            existing = await cur_get.fetchone()

            if not existing:
                return DataResult(status=0, msg="Server not found")

            name = server.name if server.name is not None else existing["name"]
            description = server.description if server.description is not None else existing["description"]
            transport = server.transport if server.transport is not None else existing["transport"]
            command = server.command if server.command is not None else existing["command"]
            args = server.args if server.args is not None else existing["args"]
            env = server.env if server.env is not None else existing["env"]
            url = server.url if server.url is not None else existing["url"]
            headers = server.headers if server.headers is not None else existing["headers"]

            cur = await conn.execute(
                dml.DML_MCP_SERVER_UPDATE,
                (
                    name,
                    description,
                    transport,
                    command,
                    args,
                    env,
                    url,
                    headers,
                    server_id,
                ),
            )
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Update failed")

    return DataResult(status=1, data=McpServerInfo(**row))


@mcp_router.post(
    path="/servers/batch-delete",
    response_model=DataResult[list[dict]],
    summary="批量删除 MCP Server",
    description="软删除指定的多个 MCP Server。",
)
async def delete_mcp_servers(
    body: Annotated[McpServerBatchDelete, Body(description="MCP Server ID 列表")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    if not body.ids:
        return DataResult(status=0, msg="ids cannot be empty")

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_MCP_SERVER_DELETE, (body.ids,))
            rows = await cur.fetchall()

    deleted = [{"id": row["id"], "name": row["name"]} for row in rows]
    return DataResult(status=1, data=deleted)