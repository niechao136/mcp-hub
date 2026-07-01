import { useMutation, useQuery } from "@tanstack/react-query";
import { authApi, UserLogin, UserRegister } from "@/api/auth";
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
  return useQuery({
    queryKey: ["profile"],
    queryFn: () => authApi.getProfile(),
    enabled: !!authApi.getToken(),
  });
};

export const useLogout = () => {
  const logout = useAuthStore((state) => state.logout);

  return useMutation({
    mutationFn: async () => {
      authApi.removeToken();
      logout();
      return Promise.resolve();
    },
  });
};