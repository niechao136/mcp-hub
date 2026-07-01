from enum import Enum
from datetime import datetime
from uuid import UUID
from typing import Any
from pydantic import BaseModel, Field, model_validator


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserInfo(BaseModel):
    id: UUID = Field(..., description="用户 ID")
    username: str = Field(..., description="用户名")
    email: str | None = Field(None, description="邮箱")
    role: UserRole = Field(..., description="用户权限")
    is_active: bool = Field(True, description="是否启用")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")

    @model_validator(mode="before")
    @classmethod
    def set_default_is_active(cls, data: Any) -> Any:
        if isinstance(data, dict) and "is_active" not in data:
            data["is_active"] = True
        return data


class UserCreate(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    email: str | None = Field(None, description="邮箱")
    role: UserRole = Field(UserRole.USER, description="用户权限")


class UserUpdate(BaseModel):
    username: str | None = Field(None, description="用户名")
    email: str | None = Field(None, description="邮箱")
    role: UserRole | None = Field(None, description="用户权限")


class ChangePassword(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., description="新密码")


class ResetPassword(BaseModel):
    new_password: str = Field(..., description="新密码")


class UserBatchDelete(BaseModel):
    ids: list[UUID] = Field(..., description="用户 ID 列表")