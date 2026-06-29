from pydantic import BaseModel, Field

from .user import UserRole


class TokenDict(BaseModel):
    id: str = Field(..., description="用户 ID")
    name: str = Field(..., description="用户名")
    role: UserRole = Field(..., description="用户权限")

class UserLogin(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")

class UserRegister(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    email: str | None = Field(None, description="邮箱")
