from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Path, Body

from src.dbs.postgre import get_db_pool
from src.dbs import dml
from src.schemas.api import DataResult, PageResult, PageParams
from src.schemas.auth import TokenDict
from src.schemas.user import UserInfo, UserCreate, UserUpdate, ChangePassword, ResetPassword, UserBatchDelete
from src.utils.auth import get_current_user, get_current_admin_user
from src.utils.security import pwd_context


user_router = APIRouter(
    prefix="/user",
    tags=["User 管理"]
)


@user_router.get(
    path="/me",
    response_model=DataResult[UserInfo],
    summary="获取自己信息",
    description="获取当前登录用户的详细信息。",
)
async def get_own_profile(
    user: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_USER_GET_BY_ID, (user.id,))
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="User not found")

    return DataResult(status=1, data=UserInfo(**row))


@user_router.get(
    path="/list",
    response_model=DataResult[PageResult[UserInfo]],
    summary="用户列表",
    description="获取用户列表，支持分页、排序、关键字搜索。",
)
async def get_user_list(
    params: Annotated[PageParams, Depends()],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    order_by = params.order_by or "created_at"
    direction = params.direction or "desc"

    allowed_columns = ["id", "username", "email", "role", "created_at", "updated_at"]
    if order_by not in allowed_columns:
        order_by = "created_at"

    if direction not in ["asc", "desc"]:
        direction = "desc"

    keyword = params.keyword

    if keyword:
        like_pattern = f"%{keyword}%"
        where_clause = "AND (username ILIKE %s OR email ILIKE %s)"
        list_params = (like_pattern, like_pattern, params.size, params.offset)
        count_params = (like_pattern, like_pattern)
    else:
        where_clause = ""
        list_params = (params.size, params.offset)
        count_params = ()

    sql_list = dml.DML_USER_LIST.format(order_by=order_by, direction=direction, where_clause=where_clause)
    sql_count = dml.DML_USER_COUNT.format(where_clause=where_clause)

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(sql_list, list_params)
            rows = await cur.fetchall()

            cur_count = await conn.execute(sql_count, count_params)
            count_row = await cur_count.fetchone()

    total = count_row["total"] if count_row else 0

    return DataResult(
        status=1,
        data=PageResult(
            total=total,
            data=[UserInfo(**row) for row in rows],
            page=params.page,
            size=params.size,
        ),
    )


@user_router.get(
    path="/count",
    response_model=DataResult[int],
    summary="用户总数",
    description="获取未删除用户的总数。",
)
async def get_user_count(
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    sql_count = dml.DML_USER_COUNT.format(where_clause="")
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(sql_count)
            row = await cur.fetchone()

    total = row["total"] if row else 0
    return DataResult(status=1, data=total)


@user_router.post(
    path="",
    response_model=DataResult[UserInfo],
    summary="新增用户",
    description="创建新用户。",
)
async def create_user(
    user: Annotated[UserCreate, Body(description="用户信息")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    hash_pwd = pwd_context.hash(user.password)

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(
                dml.DML_USER_CREATE,
                (user.username, hash_pwd, user.email, user.role),
            )
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Username already exists")

    return DataResult(status=1, data=UserInfo(**row))


@user_router.get(
    path="/{user_id}",
    response_model=DataResult[UserInfo],
    summary="获取用户信息",
    description="获取指定用户的详细信息。",
)
async def get_user_info(
    user_id: Annotated[UUID, Path(description="用户 ID")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_USER_GET_BY_ID, (user_id,))
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="User not found")

    return DataResult(status=1, data=UserInfo(**row))


@user_router.put(
    path="/{user_id}",
    response_model=DataResult[UserInfo],
    summary="修改用户",
    description="修改指定用户的信息。",
)
async def update_user(
    user_id: Annotated[UUID, Path(description="用户 ID")],
    user: Annotated[UserUpdate, Body(description="用户信息")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur_get = await conn.execute(dml.DML_USER_GET_BY_ID, (user_id,))
            existing = await cur_get.fetchone()

            if not existing:
                return DataResult(status=0, msg="User not found")

            username = user.username if user.username is not None else existing["username"]
            email = user.email if user.email is not None else existing["email"]
            role = user.role if user.role is not None else existing["role"]

            cur = await conn.execute(
                dml.DML_USER_UPDATE,
                (username, email, role, user_id),
            )
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Update failed")

    return DataResult(status=1, data=UserInfo(**row))


@user_router.delete(
    path="/batch",
    response_model=DataResult[list[dict]],
    summary="批量删除用户",
    description="软删除指定的多个用户。",
)
async def delete_users(
    body: Annotated[UserBatchDelete, Body(description="用户 ID 列表")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    if not body.ids:
        return DataResult(status=0, msg="ids cannot be empty")

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_USER_DELETE, (body.ids,))
            rows = await cur.fetchall()

    deleted = [{"id": row["id"], "username": row["username"]} for row in rows]
    return DataResult(status=1, data=deleted)


@user_router.post(
    path="/{user_id}/reset-password",
    response_model=DataResult[dict],
    summary="重置用户密码",
    description="重置指定用户的密码。",
)
async def reset_user_password(
    user_id: Annotated[UUID, Path(description="用户 ID")],
    body: Annotated[ResetPassword, Body(description="新密码")],
    _: TokenDict = Depends(get_current_admin_user),
    pool=Depends(get_db_pool),
):
    hash_pwd = pwd_context.hash(body.new_password)

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_USER_UPDATE_PASSWORD, (hash_pwd, user_id))
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="User not found")

    return DataResult(status=1, data={"id": row["id"]})


@user_router.post(
    path="/change-password",
    response_model=DataResult[dict],
    summary="修改自己密码",
    description="当前用户修改自己的密码。",
)
async def change_own_password(
    body: Annotated[ChangePassword, Body(description="密码信息")],
    user: TokenDict = Depends(get_current_user),
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_USER_GET_BY_ID_WITH_PWD, (user.id,))
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="User not found")

    if not pwd_context.verify(body.old_password, row["password"]):
        return DataResult(status=0, msg="Old password is incorrect")

    hash_pwd = pwd_context.hash(body.new_password)

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(dml.DML_USER_UPDATE_PASSWORD, (hash_pwd, user.id))
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Update failed")

    return DataResult(status=1, data={"id": row["id"]})