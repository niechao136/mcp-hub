from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Path, Body

from src.dbs.postgre import get_db_pool
from src.dbs import dml
from src.schemas.api import DataResult, PageResult, PageParams
from src.schemas.auth import TokenDict
from src.schemas.llm import LlmModelInfo, LlmModelCreate, LlmModelUpdate, LlmModelBatchDelete
from src.utils.auth import get_current_user, get_current_admin_user


llm_router = APIRouter(
    prefix="/llm",
    tags=["LLM 管理"]
)


@llm_router.get(
    path="/models",
    response_model=DataResult[list[LlmModelInfo]],
    summary="获取启用的模型列表",
    description="获取所有启用的 LLM 模型列表，用于前端选择。",
)
async def get_active_models(
    user: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_LLM_MODEL_LIST_ACTIVE)
            rows = await cur.fetchall()

    return DataResult(status=1, data=[LlmModelInfo(**row) for row in rows])


@llm_router.get(
    path="/models/list",
    response_model=DataResult[PageResult[LlmModelInfo]],
    summary="模型列表",
    description="获取模型列表，支持分页、排序。",
)
async def get_model_list(
    params: Annotated[PageParams, Depends()],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    order_by = params.order_by or "created_at"
    direction = params.direction or "desc"

    allowed_columns = ["id", "display_name", "provider", "model_id", "is_active", "created_at", "updated_at"]
    if order_by not in allowed_columns:
        order_by = "created_at"

    if direction not in ["asc", "desc"]:
        direction = "desc"

    sql_list = dml.DML_LLM_MODEL_LIST.format(order_by=order_by, direction=direction)

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(sql_list, (params.size, params.offset))
            rows = await cur.fetchall()

            cur_count = await conn.execute(dml.DML_LLM_MODEL_COUNT)
            count_row = await cur_count.fetchone()

    total = count_row["total"] if count_row else 0

    return DataResult(
        status=1,
        data=PageResult(
            total=total,
            data=[LlmModelInfo(**row) for row in rows],
            page=params.page,
            size=params.size,
        ),
    )


@llm_router.get(
    path="/models/count",
    response_model=DataResult[int],
    summary="模型总数",
    description="获取未删除模型的总数。",
)
async def get_model_count(
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_LLM_MODEL_COUNT)
            row = await cur.fetchone()

    total = row["total"] if row else 0
    return DataResult(status=1, data=total)


@llm_router.post(
    path="/models",
    response_model=DataResult[LlmModelInfo],
    summary="新增模型",
    description="创建新的 LLM 模型配置。",
)
async def create_model(
    model: Annotated[LlmModelCreate, Body(description="模型信息")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(
                dml.DML_LLM_MODEL_CREATE,
                (
                    model.display_name,
                    model.provider,
                    model.model_id,
                    model.base_url,
                    model.api_key,
                    model.context_window,
                    model.max_tokens,
                    model.supports_tool_call,
                    model.supports_vision,
                    model.is_active,
                ),
            )
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Model already exists")

    return DataResult(status=1, data=LlmModelInfo(**row))


@llm_router.get(
    path="/models/{model_id}",
    response_model=DataResult[LlmModelInfo],
    summary="获取模型信息",
    description="获取指定模型的详细信息。",
)
async def get_model_info(
    model_id: Annotated[UUID, Path(description="模型 ID")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_LLM_MODEL_GET_BY_ID, (model_id,))
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Model not found")

    return DataResult(status=1, data=LlmModelInfo(**row))


@llm_router.put(
    path="/models/{model_id}",
    response_model=DataResult[LlmModelInfo],
    summary="修改模型",
    description="修改指定模型的配置。",
)
async def update_model(
    model_id: Annotated[UUID, Path(description="模型 ID")],
    model: Annotated[LlmModelUpdate, Body(description="模型信息")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur_get = await conn.execute(dml.DML_LLM_MODEL_GET_BY_ID_WITH_KEY, (model_id,))
            existing = await cur_get.fetchone()

            if not existing:
                return DataResult(status=0, msg="Model not found")

            display_name = model.display_name if model.display_name is not None else existing["display_name"]
            provider = model.provider if model.provider is not None else existing["provider"]
            model_id_val = model.model_id if model.model_id is not None else existing["model_id"]
            base_url = model.base_url if model.base_url is not None else existing["base_url"]
            api_key = model.api_key if model.api_key is not None else existing["api_key"]
            context_window = model.context_window if model.context_window is not None else existing["context_window"]
            max_tokens = model.max_tokens if model.max_tokens is not None else existing["max_tokens"]
            supports_tool_call = model.supports_tool_call if model.supports_tool_call is not None else existing["supports_tool_call"]
            supports_vision = model.supports_vision if model.supports_vision is not None else existing["supports_vision"]
            is_active = model.is_active if model.is_active is not None else existing["is_active"]

            cur = await conn.execute(
                dml.DML_LLM_MODEL_UPDATE,
                (
                    display_name,
                    provider,
                    model_id_val,
                    base_url,
                    api_key,
                    context_window,
                    max_tokens,
                    supports_tool_call,
                    supports_vision,
                    is_active,
                    model_id,
                ),
            )
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Update failed")

    return DataResult(status=1, data=LlmModelInfo(**row))


@llm_router.post(
    path="/models/batch-delete",
    response_model=DataResult[list[dict]],
    summary="批量删除模型",
    description="软删除指定的多个模型。",
)
async def delete_models(
    body: Annotated[LlmModelBatchDelete, Body(description="模型 ID 列表")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    if not body.ids:
        return DataResult(status=0, msg="ids cannot be empty")

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_LLM_MODEL_DELETE, (body.ids,))
            rows = await cur.fetchall()

    deleted = [{"id": row["id"], "display_name": row["display_name"]} for row in rows]
    return DataResult(status=1, data=deleted)