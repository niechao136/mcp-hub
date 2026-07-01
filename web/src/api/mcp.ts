import { request } from "./base";
import type { DataResult } from "./base";

export interface McpServer {
  id: string;
  name: string;
  description: string | null;
  transport: string;
  command: string | null;
  args: any[] | null;
  env: Record<string, string> | null;
  url: string | null;
  headers: Record<string, string> | null;
  status: string;
  last_checked_at: string | null;
  tools_cache: any[] | null;
  created_by: string;
  created_at: string;
  updated_at: string | null;
}

export interface McpListQuery {
  page: number;
  size: number;
  keyword?: string;
  order_by?: string;
  direction?: "asc" | "desc";
}

export interface McpCreate {
  name: string;
  description?: string;
  transport: string;
  command?: string;
  args?: any[];
  env?: Record<string, string>;
  url?: string;
  headers?: Record<string, string>;
}

export interface McpUpdate {
  name?: string;
  description?: string;
  transport?: string;
  command?: string;
  args?: any[];
  env?: Record<string, string>;
  url?: string;
  headers?: Record<string, string>;
}

export const mcpApi = {
  list: async (params: McpListQuery): Promise<DataResult<McpServer[]>> => {
    return request.get("/mcp/servers/list", { params });
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