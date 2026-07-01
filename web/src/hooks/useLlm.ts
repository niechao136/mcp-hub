import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { llmApi } from "@/api/llm";
import type { LlmListQuery, LlmCreate, LlmUpdate } from "@/api/llm";

export function useLlmModels(query: LlmListQuery) {
  return useQuery({
    queryKey: ["llmModels", query],
    queryFn: () => llmApi.list(query),
  });
}

export function useLlmModelCount() {
  return useQuery({
    queryKey: ["llmModelsCount"],
    queryFn: () => llmApi.count(),
  });
}

export function useGetLlmModel(modelId: string) {
  return useQuery({
    queryKey: ["llmModel", modelId],
    queryFn: () => llmApi.get(modelId),
    enabled: !!modelId,
  });
}

export function useCreateLlmModel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: LlmCreate) => llmApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["llmModels"] });
      queryClient.invalidateQueries({ queryKey: ["llmModelsCount"] });
    },
  });
}

export function useUpdateLlmModel() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ modelId, data }: { modelId: string; data: LlmUpdate }) => llmApi.update(modelId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["llmModels"] });
    },
  });
}

export function useDeleteLlmModels() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (ids: string[]) => llmApi.delete(ids),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["llmModels"] });
      queryClient.invalidateQueries({ queryKey: ["llmModelsCount"] });
    },
  });
}