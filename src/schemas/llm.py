from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class LlmModelInfo(BaseModel):
    id: UUID = Field(..., description="模型 ID")
    display_name: str = Field(..., description="显示名称")
    provider: str = Field(..., description="提供商")
    model_id: str = Field(..., description="模型标识")
    base_url: str | None = Field(None, description="基础 URL")
    context_window: int | None = Field(None, description="上下文窗口大小")
    max_tokens: int | None = Field(None, description="最大 tokens")
    supports_tool_call: bool = Field(True, description="是否支持工具调用")
    supports_vision: bool = Field(False, description="是否支持视觉")
    is_active: bool = Field(True, description="是否启用")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")


class LlmModelCreate(BaseModel):
    display_name: str = Field(..., description="显示名称")
    provider: str = Field(..., description="提供商")
    model_id: str = Field(..., description="模型标识")
    base_url: str | None = Field(None, description="基础 URL")
    api_key: str | None = Field(None, description="API Key")
    context_window: int | None = Field(None, description="上下文窗口大小")
    max_tokens: int | None = Field(None, description="最大 tokens")
    supports_tool_call: bool = Field(True, description="是否支持工具调用")
    supports_vision: bool = Field(False, description="是否支持视觉")
    is_active: bool = Field(True, description="是否启用")


class LlmModelUpdate(BaseModel):
    display_name: str | None = Field(None, description="显示名称")
    provider: str | None = Field(None, description="提供商")
    model_id: str | None = Field(None, description="模型标识")
    base_url: str | None = Field(None, description="基础 URL")
    api_key: str | None = Field(None, description="API Key")
    context_window: int | None = Field(None, description="上下文窗口大小")
    max_tokens: int | None = Field(None, description="最大 tokens")
    supports_tool_call: bool | None = Field(None, description="是否支持工具调用")
    supports_vision: bool | None = Field(None, description="是否支持视觉")
    is_active: bool | None = Field(None, description="是否启用")


class LlmModelBatchDelete(BaseModel):
    ids: list[UUID] = Field(..., description="模型 ID 列表")