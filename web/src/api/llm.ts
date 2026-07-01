import { request } from "./base";
import type { DataResult } from "./base";

export interface LlmModel {
  id: string;
  display_name: string;
  provider: string;
  model_id: string;
  base_url: string | null;
  context_window: number | null;
  max_tokens: number | null;
  supports_tool_call: boolean;
  supports_vision: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface LlmListQuery {
  page: number;
  size: number;
  keyword?: string;
  order_by?: string;
  direction?: "asc" | "desc";
}

export interface LlmCreate {
  display_name: string;
  provider: string;
  model_id: string;
  base_url?: string;
  api_key?: string;
  context_window?: number;
  max_tokens?: number;
  supports_tool_call?: boolean;
  supports_vision?: boolean;
  is_active?: boolean;
}

export interface LlmUpdate {
  display_name?: string;
  provider?: string;
  model_id?: string;
  base_url?: string;
  api_key?: string;
  context_window?: number;
  max_tokens?: number;
  supports_tool_call?: boolean;
  supports_vision?: boolean;
  is_active?: boolean;
}

export const llmApi = {
  list: async (params: LlmListQuery): Promise<DataResult<LlmModel[]>> => {
    return request.get("/llm/models/list", { params });
  },

  count: async (): Promise<DataResult<number>> => {
    return request.get("/llm/models/count");
  },

  get: async (modelId: string): Promise<DataResult<LlmModel>> => {
    return request.get(`/llm/models/${modelId}`);
  },

  create: async (data: LlmCreate): Promise<DataResult<LlmModel>> => {
    return request.post("/llm/models", data);
  },

  update: async (modelId: string, data: LlmUpdate): Promise<DataResult<LlmModel>> => {
    return request.put(`/llm/models/${modelId}`, data);
  },

  delete: async (ids: string[]): Promise<DataResult<{ id: string; name: string }[]>> => {
    return request.post("/llm/models/batch-delete", { ids });
  },
};