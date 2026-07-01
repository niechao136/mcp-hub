import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { mcpApi } from "@/api/mcp";
import type { McpListQuery, McpCreate, McpUpdate } from "@/api/mcp";

export function useMcpServers(query: McpListQuery) {
  return useQuery({
    queryKey: ["mcpServers", query],
    queryFn: () => mcpApi.list(query),
    select: (data) => ({
      ...data,
      data: data.data,
    }),
  });
}

export function useMcpServerCount() {
  return useQuery({
    queryKey: ["mcpServersCount"],
    queryFn: () => mcpApi.count(),
  });
}

export function useGetMcpServer(serverId: string) {
  return useQuery({
    queryKey: ["mcpServer", serverId],
    queryFn: () => mcpApi.get(serverId),
    enabled: !!serverId,
  });
}

export function useCreateMcpServer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: McpCreate) => mcpApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mcpServers"] });
      queryClient.invalidateQueries({ queryKey: ["mcpServersCount"] });
    },
  });
}

export function useUpdateMcpServer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ serverId, data }: { serverId: string; data: McpUpdate }) => mcpApi.update(serverId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mcpServers"] });
    },
  });
}

export function useDeleteMcpServers() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ids: string[]) => mcpApi.delete(ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["mcpServers"] });
      queryClient.invalidateQueries({ queryKey: ["mcpServersCount"] });
    },
  });
}