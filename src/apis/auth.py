from typing import Annotated
from fastapi import APIRouter, Depends, Body

from src.dbs.postgre import get_db_pool
from src.dbs import dml
from src.schemas.api import DataResult
from src.schemas.auth import UserLogin, TokenDict, UserRegister
from src.schemas.user import UserInfo
from src.utils.jwt import create_access_token
from src.utils.security import pwd_context


auth_router = APIRouter(
    prefix="/auth",
    tags=["Auth 模块"]
)


@auth_router.post(
    path="/login",
    response_model=DataResult[str],
    summary="用户登录",
    description="验证用户名和密码，成功后返回 JWT Token。",
)
async def login(
    user: Annotated[UserLogin, Body(description="用户登录凭证")],
    pool=Depends(get_db_pool),
):
    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(
                dml.DML_USER_GET_BY_USERNAME_WITH_PWD,
                (user.username,),
            )
            row = await cur.fetchone()

    if not row or not pwd_context.verify(user.password, row["password"]):
        return DataResult(status=0, msg="Username or password is incorrect")

    user_id = str(row["id"])
    token = create_access_token(TokenDict(id=user_id, username=user.username, role=row["role"]))
    return DataResult(status=1, data=token)


@auth_router.post(
    path="/register",
    response_model=DataResult[UserInfo],
    summary="用户注册",
    description="创建新用户，默认角色为 user。",
)
async def register(
    user: Annotated[UserRegister, Body(description="用户注册信息")],
    pool=Depends(get_db_pool),
):
    hash_pwd = pwd_context.hash(user.password)

    async with pool.connection() as conn:
        async with conn.transaction():
            cur = await conn.execute(
                dml.DML_USER_REGISTER,
                (user.username, hash_pwd, user.email),
            )
            row = await cur.fetchone()

    if not row:
        return DataResult(status=0, msg="Username already exists")

    return DataResult(status=1, data=UserInfo(**row))