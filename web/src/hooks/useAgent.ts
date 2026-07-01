import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { agentApi } from "@/api/agent";
import type { AgentListQuery, AgentCreate, AgentUpdate } from "@/api/agent";

export function useAgents(query: AgentListQuery) {
  return useQuery({
    queryKey: ["agents", query],
    queryFn: () => agentApi.list(query),
    select: (data) => ({
      ...data,
      data: data.data,
    }),
  });
}

export function useAgentCount() {
  return useQuery({
    queryKey: ["agentsCount"],
    queryFn: () => agentApi.count(),
  });
}

export function useGetAgent(agentId: string) {
  return useQuery({
    queryKey: ["agent", agentId],
    queryFn: () => agentApi.get(agentId),
    enabled: !!agentId,
  });
}

export function useCreateAgent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: AgentCreate) => agentApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
      queryClient.invalidateQueries({ queryKey: ["agentsCount"] });
    },
  });
}

export function useUpdateAgent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ agentId, data }: { agentId: string; data: AgentUpdate }) => agentApi.update(agentId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
    },
  });
}

export function useDeleteAgents() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ids: string[]) => agentApi.delete(ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["agents"] });
      queryClient.invalidateQueries({ queryKey: ["agentsCount"] });
    },
  });
}

export function useAgentMcpServers(agentId: string) {
  return useQuery({
    queryKey: ["agentMcpServers", agentId],
    queryFn: () => agentApi.getMcpServers(agentId),
    enabled: !!agentId,
  });
}

export function useAddAgentMcpServer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ agentId, mcpServerId }: { agentId: string; mcpServerId: string }) =>
      agentApi.addMcpServer(agentId, mcpServerId),
    onSuccess: (_data, { agentId }) => {
      queryClient.invalidateQueries({ queryKey: ["agentMcpServers", agentId] });
    },
  });
}

export function useRemoveAgentMcpServer() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ agentId, mcpServerId }: { agentId: string; mcpServerId: string }) =>
      agentApi.removeMcpServer(agentId, mcpServerId),
    onSuccess: (_data, { agentId }) => {
      queryClient.invalidateQueries({ queryKey: ["agentMcpServers", agentId] });
    },
  });
}