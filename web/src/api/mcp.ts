import { request } from "./base";
import type { DataResult } from "./base";

export interface McpServer {
  id: string;
  name: string;
  transport: string;
  endpoint: string;
  config: string | null;
  status: string;
  health_check_url: string | null;
  description: string | null;
  created_at: string;
  updated_at: string;
}

export interface McpListQuery {
  page: number;
  page_size: number;
  keyword?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export interface McpCreate {
  name: string;
  transport: string;
  endpoint: string;
  config?: string;
  status?: string;
  health_check_url?: string;
  description?: string;
}

export interface McpUpdate {
  name?: string;
  transport?: string;
  endpoint?: string;
  config?: string;
  status?: string;
  health_check_url?: string;
  description?: string;
}

export const mcpApi = {
  list: async (params: McpListQuery): Promise<DataResult<McpServer[]>> => {
    return request.get("/mcp/servers", { params });
  },

  count: async (): Promise<DataResult<number>> => {
    return request.get("/mcp/servers/count");
  },

  get: async (serverId: string): Promise<DataResult<McpServer>> => {
    return request.get(`/mcp/servers/${serverId}`);
  },

  create: async (data: McpCreate): Promise<DataResult<McpServer>> => {
    return request.post("/mcp/servers", data);
  },

  update: async (serverId: string, data: McpUpdate): Promise<DataResult<McpServer>> => {
    return request.put(`/mcp/servers/${serverId}`, data);
  },

  delete: async (ids: string[]): Promise<DataResult<{ id: string; name: string }[]>> => {
    return request.post("/mcp/servers/batch-delete", { ids });
  },
};