import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { userApi } from "@/api/user";
import type { UserListQuery, UserCreate, UserUpdate, ChangePassword, ResetPassword } from "@/api/user";

export function useUsers(query: UserListQuery) {
  return useQuery({
    queryKey: ["users", query],
    queryFn: () => userApi.list(query),
  });
}

export function useUserCount() {
  return useQuery({
    queryKey: ["usersCount"],
    queryFn: () => userApi.count(),
  });
}

export function useGetUser(userId: string) {
  return useQuery({
    queryKey: ["user", userId],
    queryFn: () => userApi.get(userId),
    enabled: !!userId,
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: UserCreate) => userApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      queryClient.invalidateQueries({ queryKey: ["usersCount"] });
    },
  });
}

export function useUpdateUser() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, data }: { userId: string; data: UserUpdate }) => userApi.update(userId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });
}

export function useDeleteUsers() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ids: string[]) => userApi.delete(ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] });
      queryClient.invalidateQueries({ queryKey: ["usersCount"] });
    },
  });
}

export function useResetPassword() {
  return useMutation({
    mutationFn: (data: ResetPassword) => userApi.resetPassword(data),
  });
}

export function useChangePassword() {
  return useMutation({
    mutationFn: (data: ChangePassword) => userApi.changePassword(data),
  });
}