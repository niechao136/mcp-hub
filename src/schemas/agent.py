from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, Field


class MemoryStrategy(str, Enum):
    WINDOW = "window"
    SUMMARY = "summary"
    FULL = "full"
    NONE = "none"


class AgentInfo(BaseModel):
    id: UUID = Field(..., description="Agent ID")
    name: str = Field(..., description="名称")
    description: str | None = Field(None, description="描述")
    llm_model_id: UUID = Field(..., description="LLM 模型 ID")
    llm_model_name: str | None = Field(None, description="LLM 模型名称")
    system_prompt: str = Field("", description="系统提示词")
    temperature: float = Field(0.0, description="温度参数")
    max_tokens: int | None = Field(None, description="最大 tokens")
    memory_strategy: str = Field("window", description="记忆策略: window / summary / full / none")
    memory_window: int = Field(20, description="记忆窗口大小")
    is_active: bool = Field(True, description="是否启用")
    created_by: UUID = Field(..., description="创建者 ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")


class AgentCreate(BaseModel):
    name: str = Field(..., description="名称")
    description: str | None = Field(None, description="描述")
    llm_model_id: UUID = Field(..., description="LLM 模型 ID")
    system_prompt: str = Field("", description="系统提示词")
    temperature: float = Field(0.0, description="温度参数")
    max_tokens: int | None = Field(None, description="最大 tokens")
    memory_strategy: MemoryStrategy = Field(MemoryStrategy.WINDOW, description="记忆策略")
    memory_window: int = Field(20, description="记忆窗口大小")
    is_active: bool = Field(True, description="是否启用")


class AgentUpdate(BaseModel):
    name: str | None = Field(None, description="名称")
    description: str | None = Field(None, description="描述")
    llm_model_id: UUID | None = Field(None, description="LLM 模型 ID")
    system_prompt: str | None = Field(None, description="系统提示词")
    temperature: float | None = Field(None, description="温度参数")
    max_tokens: int | None = Field(None, description="最大 tokens")
    memory_strategy: MemoryStrategy | None = Field(None, description="记忆策略")
    memory_window: int | None = Field(None, description="记忆窗口大小")
    is_active: bool | None = Field(None, description="是否启用")


class AgentBatchDelete(BaseModel):
    ids: list[UUID] = Field(..., description="Agent ID 列表")


class AgentMcpInfo(BaseModel):
    id: UUID = Field(..., description="关联 ID")
    agent_id: UUID = Field(..., description="Agent ID")
    mcp_server_id: UUID = Field(..., description="MCP Server ID")
    mcp_server_name: str | None = Field(None, description="MCP Server 名称")
    allowed_tools: list | None = Field(None, description="允许的工具列表（白名单，NULL 表示全部）")
    priority: int = Field(0, description="优先级")
    created_at: datetime = Field(..., description="创建时间")


class AgentMcpCreate(BaseModel):
    mcp_server_id: UUID = Field(..., description="MCP Server ID")
    allowed_tools: list | None = Field(None, description="允许的工具列表（白名单，NULL 表示全部）")
    priority: int = Field(0, description="优先级")


class AgentThreadInfo(BaseModel):
    thread_id: str = Field(..., description="线程 ID")
    agent_id: UUID = Field(..., description="Agent ID")
    user_id: UUID = Field(..., description="用户 ID")
    title: str | None = Field(None, description="会话标题")
    agent_snapshot: dict | None = Field(None, description="Agent 配置快照")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime | None = Field(None, description="更新时间")


class AgentThreadCreate(BaseModel):
    thread_id: str = Field(..., description="线程 ID")
    agent_id: UUID = Field(..., description="Agent ID")
    title: str | None = Field(None, description="会话标题")
    agent_snapshot: dict | None = Field(None, description="Agent 配置快照")