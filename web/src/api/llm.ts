import { request } from "./base";
import type { DataResult } from "./base";

export interface LlmModel {
  id: string;
  name: string;
  provider: string;
  model: string;
  api_key: string | null;
  base_url: string | null;
  max_tokens: number;
  temperature: number;
  top_p: number;
  frequency_penalty: number;
  presence_penalty: number;
  created_at: string;
  updated_at: string;
}

export interface LlmListQuery {
  page: number;
  page_size: number;
  keyword?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export interface LlmCreate {
  name: string;
  provider: string;
  model: string;
  api_key?: string;
  base_url?: string;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
}

export interface LlmUpdate {
  name?: string;
  provider?: string;
  model?: string;
  api_key?: string;
  base_url?: string;
  max_tokens?: number;
  temperature?: number;
  top_p?: number;
  frequency_penalty?: number;
  presence_penalty?: number;
}

export const llmApi = {
  list: async (params: LlmListQuery): Promise<DataResult<LlmModel[]>> => {
    return request.get("/llm/models", { params });
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