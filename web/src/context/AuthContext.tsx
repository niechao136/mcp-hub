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

  const { data, isFetching } = useProfile();

  useEffect(() => {
    if (data?.status === 1 && data.data) {
      setUser(data.data);
      setStoreUser(data.data);
      setIsLoading(false);
    } else if (data?.status === 0) {
      setUser(null);
      setStoreUser(null);
      logoutStore();
      setIsLoading(false);
    }
  }, [data, setStoreUser, logoutStore]);

  useEffect(() => {
    if (storeUser && !isFetching && !data) {
      setUser(storeUser);
      setIsLoading(false);
    }
  }, [storeUser, isFetching, data]);

  useEffect(() => {
    if (!authApi.getToken()) {
      setUser(null);
      setIsLoading(false);
    }
  }, []);

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}