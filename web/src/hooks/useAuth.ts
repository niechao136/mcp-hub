import { useMutation, useQuery } from "@tanstack/react-query";
import { authApi, UserLogin, UserRegister, TokenDict } from "@/api/auth";
import { useAuthStore } from "@/store/auth";

export const useLogin = () => {
  const setUser = useAuthStore((state) => state.setUser);

  return useMutation({
    mutationFn: (data: UserLogin) => authApi.login(data),
    onSuccess: (result) => {
      if (result.status === 1 && result.data) {
        authApi.setToken(result.data);
        const tokenParts = result.data.split(".");
        const base64Url = tokenParts[1].replace(/-/g, "+").replace(/_/g, "/");
        const padding = "=".repeat((4 - (base64Url.length % 4)) % 4);
        const decodedPayload = JSON.parse(atob(base64Url + padding));
        setUser({
          id: decodedPayload.id,
          name: decodedPayload.name,
          role: decodedPayload.role,
        });
      }
    },
  });
};

export const useRegister = () => {
  return useMutation({
    mutationFn: (data: UserRegister) => authApi.register(data),
  });
};

export const useProfile = () => {
  const setUser = useAuthStore((state) => state.setUser);

  return useQuery<TokenDict, Error>({
    queryKey: ["profile"],
    queryFn: async () => {
      const result = await authApi.getProfile();
      if (result.status === 1 && result.data) {
        setUser(result.data);
        return result.data;
      }
      throw new Error(result.msg);
    },
    enabled: !!authApi.getToken(),
  });
};

export const useLogout = () => {
  const logout = useAuthStore((state) => state.logout);

  const handleLogout = () => {
    authApi.removeToken();
    logout();
  };

  return handleLogout;
};