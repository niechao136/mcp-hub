import { request } from "./base";
import type { DataResult } from "./base";

export interface UserInfo {
  id: string;
  username: string;
  email: string | null;
  role: string;
  avatar: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface UserListQuery {
  page: number;
  page_size: number;
  keyword?: string;
  sort_by?: string;
  sort_order?: "asc" | "desc";
}

export interface UserCreate {
  username: string;
  password: string;
  email?: string;
  role?: string;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  role?: string;
  is_active?: boolean;
}

export interface ChangePassword {
  old_password: string;
  new_password: string;
}

export interface ResetPassword {
  user_id: string;
  new_password: string;
}

export const userApi = {
  list: async (params: UserListQuery): Promise<DataResult<UserInfo[]>> => {
    return request.get("/users", { params });
  },

  count: async (): Promise<DataResult<number>> => {
    return request.get("/users/count");
  },

  get: async (userId: string): Promise<DataResult<UserInfo>> => {
    return request.get(`/users/${userId}`);
  },

  create: async (data: UserCreate): Promise<DataResult<UserInfo>> => {
    return request.post("/users", data);
  },

  update: async (userId: string, data: UserUpdate): Promise<DataResult<UserInfo>> => {
    return request.put(`/users/${userId}`, data);
  },

  delete: async (ids: string[]): Promise<DataResult<{ id: string; username: string }[]>> => {
    return request.post("/users/batch-delete", { ids });
  },

  resetPassword: async (data: ResetPassword): Promise<DataResult<void>> => {
    return request.post("/users/reset-password", data);
  },

  changePassword: async (data: ChangePassword): Promise<DataResult<void>> => {
    return request.post("/users/change-password", data);
  },

  profile: async (): Promise<DataResult<UserInfo>> => {
    return request.get("/users/profile");
  },
};