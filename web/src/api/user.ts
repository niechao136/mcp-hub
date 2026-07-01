import { request } from "./base";
import type { DataResult, PageResult } from "./base";

export interface UserInfo {
  id: string;
  username: string;
  email: string | null;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface UserListQuery {
  page: number;
  size: number;
  keyword?: string;
  order_by?: string;
  direction?: "asc" | "desc";
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
  list: async (params: UserListQuery): Promise<DataResult<PageResult<UserInfo>>> => {
    return request.get("/user/list", { params });
  },

  count: async (): Promise<DataResult<number>> => {
    return request.get("/user/count");
  },

  get: async (userId: string): Promise<DataResult<UserInfo>> => {
    return request.get(`/user/${userId}`);
  },

  create: async (data: UserCreate): Promise<DataResult<UserInfo>> => {
    return request.post("/user", data);
  },

  update: async (userId: string, data: UserUpdate): Promise<DataResult<UserInfo>> => {
    return request.put(`/user/${userId}`, data);
  },

  delete: async (ids: string[]): Promise<DataResult<{ id: string; username: string }[]>> => {
    return request.post("/user/batch", { ids });
  },

  resetPassword: async (userId: string, newPassword: string): Promise<DataResult<void>> => {
    return request.post(`/user/${userId}/reset-password`, { new_password: newPassword });
  },

  changePassword: async (data: ChangePassword): Promise<DataResult<void>> => {
    return request.post("/user/change-password", data);
  },

  profile: async (): Promise<DataResult<UserInfo>> => {
    return request.get("/user/me");
  },
};