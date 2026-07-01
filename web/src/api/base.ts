import Cookies from "js-cookie";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "/api";

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

const buildUrl = (url: string, params?: object): string => {
    if (!params) return url;
    const searchParams = new URLSearchParams();
    Object.entries(params as Record<string, unknown>).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
            searchParams.append(key, String(value));
        }
    });
    return `${url}?${searchParams.toString()}`;
};

export const request = {
    get: async <T>(url: string, options?: { params?: object }): Promise<DataResult<T>> => {
        const fullUrl = buildUrl(url, options?.params);
        const response = await fetch(`${API_BASE_URL}${fullUrl}`, {
            method: "GET",
            headers: getAuthHeaders(),
        });
        return response.json();
    },

    post: async <T>(url: string, data?: object): Promise<DataResult<T>> => {
        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: "POST",
            headers: getAuthHeaders(),
            body: data ? JSON.stringify(data) : undefined,
        });
        return response.json();
    },

    put: async <T>(url: string, data?: object): Promise<DataResult<T>> => {
        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: "PUT",
            headers: getAuthHeaders(),
            body: data ? JSON.stringify(data) : undefined,
        });
        return response.json();
    },

    delete: async <T>(url: string): Promise<DataResult<T>> => {
        const response = await fetch(`${API_BASE_URL}${url}`, {
            method: "DELETE",
            headers: getAuthHeaders(),
        });
        return response.json();
    },
};