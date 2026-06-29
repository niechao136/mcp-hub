from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field


class McpTransport(str, Enum):
    STDIO = "stdio"
    SSE = "sse"
    STREAMABLE_HTTP = "streamable_http"


class McpStatus(str, Enum):
    UNKNOWN = "unknown"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"


class McpServerInfo(BaseModel):
    id: UUID = Field(..., description="MCP Server ID")
    name: str = Field(..., description="名称")
    description: str | None = Field(None, description="描述")
    transport: str = Field(..., description="传输方式: stdio / sse / streamable_http")
    command: str | None = Field(None, description="命令路径 (stdio)")
    args: list | None = Field(None, description="命令参数 (stdio)")
    env: dict | None = Field(None, description="环境变量 (stdio)")
    url: str | None = Field(None, description="URL (sse / streamable_http)")
    headers: dict | None = Field(None, description="请求头 (sse / streamable_http)")
    status: str = Field("unknown", description="健康状态")
    last_checked_at: datetime | None = Field(None, description="最后检查时间")
    tools_cache: list | None = Field(None, description="工具快照缓存")
    created_by: UUID = Field(..., description="创建者 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")


class McpServerCreate(BaseModel):
    name: str = Field(..., description="名称")
    description: str | None = Field(None, description="描述")
    transport: McpTransport = Field(McpTransport.SSE, description="传输方式: stdio / sse / streamable_http")
    command: str | None = Field(None, description="命令路径 (stdio)")
    args: list | None = Field(None, description="命令参数 (stdio)")
    env: dict | None = Field(None, description="环境变量 (stdio)")
    url: str | None = Field(None, description="URL (sse / streamable_http)")
    headers: dict | None = Field(None, description="请求头 (sse / streamable_http)")


class McpServerUpdate(BaseModel):
    name: str | None = Field(None, description="名称")
    description: str | None = Field(None, description="描述")
    transport: McpTransport | None = Field(None, description="传输方式: stdio / sse / streamable_http")
    command: str | None = Field(None, description="命令路径 (stdio)")
    args: list | None = Field(None, description="命令参数 (stdio)")
    env: dict | None = Field(None, description="环境变量 (stdio)")
    url: str | None = Field(None, description="URL (sse / streamable_http)")
    headers: dict | None = Field(None, description="请求头 (sse / streamable_http)")


class McpServerBatchDelete(BaseModel):
    ids: list[UUID] = Field(..., description="MCP Server ID 列表")