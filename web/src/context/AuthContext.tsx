"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { useAuthStore } from "@/store/auth";
import { useProfile } from "@/hooks/useAuth";
import { authApi } from "@/api/auth";
import type { TokenDict } from "@/api/auth";

interface AuthContextType {
  user: TokenDict | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export const AuthContext = createContext<AuthContextType | null>(null);

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<TokenDict | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const storeUser = useAuthStore((state) => state.user);
  const setStoreUser = useAuthStore((state) => state.setUser);
  const logoutStore = useAuthStore((state) => state.logout);

  const { data, isFetching, isError } = useProfile();

  useEffect(() => {
    const token = authApi.getToken();
    if (!token) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    if (storeUser) {
      setUser(storeUser);
      setIsLoading(false);
      return;
    }

    if (data?.status === 1 && data.data) {
      setUser(data.data);
      setStoreUser(data.data);
      setIsLoading(false);
    } else if (data?.status === 0 && data.msg === "Token expired" || data?.msg === "Invalid token") {
      setUser(null);
      setStoreUser(null);
      logoutStore();
      setIsLoading(false);
    } else if (!isFetching && !isError) {
      setIsLoading(false);
    }
  }, [data, isFetching, isError, storeUser, setStoreUser, logoutStore]);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}