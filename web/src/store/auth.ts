import { create } from "zustand";
import { TokenDict } from "@/api/auth";

interface AuthState {
  user: TokenDict | null;
  isLoading: boolean;
  setUser: (user: TokenDict | null) => void;
  setLoading: (loading: boolean) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isLoading: false,
  setUser: (user) => set({ user }),
  setLoading: (loading) => set({ isLoading: loading }),
  logout: () => set({ user: null }),
}));