import { request } from "./base";
import type { DataResult } from "./base";

export interface Agent {
  id: string;
  name: string;
  description: string | null;
  llm_model_id: string;
  llm_model_name: string | null;
  system_prompt: string;
  temperature: number;
  max_tokens: number | null;
  memory_strategy: string;
  memory_window: number;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string | null;
}

export interface AgentListQuery {
  page: number;
  size: number;
  keyword?: string;
  order_by?: string;
  direction?: "asc" | "desc";
}

export interface AgentCreate {
  name: string;
  description?: string;
  llm_model_id: string;
  system_prompt: string;
  temperature?: number;
  max_tokens?: number;
  memory_strategy?: string;
  memory_window?: number;
  is_active?: boolean;
}

export interface AgentUpdate {
  name?: string;
  description?: string;
  llm_model_id?: string;
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
  memory_strategy?: string;
  memory_window?: number;
  is_active?: boolean;
}

export interface AgentMcpServer {
  id: string;
  agent_id: string;
  mcp_server_id: string;
  mcp_server_name: string;
  mcp_server_endpoint: string;
  created_at: string;
}

export const agentApi = {
  list: async (params: AgentListQuery): Promise<DataResult<Agent[]>> => {
    return request.get("/agent/list", { params });
  },

  count: async (): Promise<DataResult<number>> => {
    return request.get("/agent/count");
  },

  get: async (agentId: string): Promise<DataResult<Agent>> => {
    return request.get(`/agent/${agentId}`);
  },

  create: async (data: AgentCreate): Promise<DataResult<Agent>> => {
    return request.post("/agent", data);
  },

  update: async (agentId: string, data: AgentUpdate): Promise<DataResult<Agent>> => {
    return request.put(`/agent/${agentId}`, data);
  },

  delete: async (ids: string[]): Promise<DataResult<{ id: string; name: string }[]>> => {
    return request.post("/agent/batch-delete", { ids });
  },

  getMcpServers: async (agentId: string): Promise<DataResult<AgentMcpServer[]>> => {
    return request.get(`/agent/${agentId}/mcp-servers`);
  },

  addMcpServer: async (agentId: string, mcpServerId: string): Promise<DataResult<AgentMcpServer>> => {
    return request.post(`/agent/${agentId}/mcp-servers`, { mcp_server_id: mcpServerId });
  },

  removeMcpServer: async (agentId: string, mcpServerId: string): Promise<DataResult<void>> => {
    return request.delete(`/agent/${agentId}/mcp-servers/${mcpServerId}`);
  },
};