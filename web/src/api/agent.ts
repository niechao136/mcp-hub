import { request } from "./base";
import type { DataResult } from "./base";

export interface Agent {
  id: string;
  name: string;
  description: string | null;
  model_id: string;
  model_name: string;
  system_prompt: string;
  temperature: number;
  max_tokens: number;
  context_window: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AgentListQuery {
  page: number;
  page_size: number;
  keyword?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export interface AgentCreate {
  name: string;
  description?: string;
  model_id: string;
  system_prompt: string;
  temperature?: number;
  max_tokens?: number;
  context_window?: number;
}

export interface AgentUpdate {
  name?: string;
  description?: string;
  model_id?: string;
  system_prompt?: string;
  temperature?: number;
  max_tokens?: number;
  context_window?: number;
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
    return request.get("/agent/agents", { params });
  },

  count: async (): Promise<DataResult<number>> => {
    return request.get("/agent/agents/count");
  },

  get: async (agentId: string): Promise<DataResult<Agent>> => {
    return request.get(`/agent/agents/${agentId}`);
  },

  create: async (data: AgentCreate): Promise<DataResult<Agent>> => {
    return request.post("/agent/agents", data);
  },

  update: async (agentId: string, data: AgentUpdate): Promise<DataResult<Agent>> => {
    return request.put(`/agent/agents/${agentId}`, data);
  },

  delete: async (ids: string[]): Promise<DataResult<{ id: string; name: string }[]>> => {
    return request.post("/agent/agents/batch-delete", { ids });
  },

  getMcpServers: async (agentId: string): Promise<DataResult<AgentMcpServer[]>> => {
    return request.get(`/agent/agents/${agentId}/mcp-servers`);
  },

  addMcpServer: async (agentId: string, mcpServerId: string): Promise<DataResult<AgentMcpServer>> => {
    return request.post(`/agent/agents/${agentId}/mcp-servers`, { mcp_server_id: mcpServerId });
  },

  removeMcpServer: async (agentId: string, mcpServerId: string): Promise<DataResult<void>> => {
    return request.delete(`/agent/agents/${agentId}/mcp-servers/${mcpServerId}`);
  },
};