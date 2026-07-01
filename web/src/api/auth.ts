import Cookies from "js-cookie";

import { API_BASE_URL } from "./base";

export interface UserLogin {
  username: string;
  password: string;
}

export interface UserRegister {
  username: string;
  password: string;
  email?: string;
}

export interface TokenDict {
  id: string;
  name: string;
  role: string;
}

export interface DataResult<T> {
  status: number;
  msg: string;
  data: T;
}

const getAuthHeaders = () => {
  const token = Cookies.get("access_token");
  return {
    "Content-Type": "application/json",
    Authorization: token ? `Bearer ${token}` : "",
  };
};

export const authApi = {
  login: async (data: UserLogin): Promise<DataResult<string>> => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  register: async (data: UserRegister): Promise<DataResult<string>> => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    return response.json();
  },

  getProfile: async (): Promise<DataResult<TokenDict>> => {
    const response = await fetch(`${API_BASE_URL}/user/me`, {
      method: "GET",
      headers: getAuthHeaders(),
    });
    return response.json();
  },

  setToken: (token: string) => {
    Cookies.set("access_token", token, { expires: 1 });
  },

  getToken: () => {
    return Cookies.get("access_token");
  },

  removeToken: () => {
    Cookies.remove("access_token");
  },
};