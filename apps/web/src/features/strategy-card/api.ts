import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { ApiClientError, apiRequest } from "@/lib/api/client";

import type {
  StrategyCardDetail,
  StrategyCardListResponse,
  StrategyCardUpsertPayload,
} from "./types";

export { ApiClientError };

export const strategyCardQueryKey = (strategyCardId: string) =>
  ["strategy-card", strategyCardId] as const;

export const strategyCardListQueryKey = () => ["strategy-cards"] as const;

export async function createStrategyCard(payload: StrategyCardUpsertPayload) {
  return apiRequest<StrategyCardDetail>("/strategy-cards", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function getStrategyCardList(page = 1, pageSize = 20) {
  const params = new URLSearchParams({
    page: String(page),
    page_size: String(pageSize),
  });
  return apiRequest<StrategyCardListResponse>(`/strategy-cards?${params}`);
}

export async function getStrategyCard(strategyCardId: string) {
  return apiRequest<StrategyCardDetail>(`/strategy-cards/${strategyCardId}`);
}

export async function updateStrategyCard(
  strategyCardId: string,
  payload: StrategyCardUpsertPayload,
) {
  return apiRequest<StrategyCardDetail>(`/strategy-cards/${strategyCardId}`, {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export async function duplicateStrategyCard(strategyCardId: string) {
  return apiRequest<StrategyCardDetail>(`/strategy-cards/${strategyCardId}/duplicate`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function useStrategyCardQuery(strategyCardId?: string) {
  return useQuery({
    queryKey: strategyCardId
      ? strategyCardQueryKey(strategyCardId)
      : ["strategy-card", "idle"],
    queryFn: () => getStrategyCard(strategyCardId as string),
    enabled: Boolean(strategyCardId),
  });
}

export function useStrategyCardListQuery() {
  return useQuery({
    queryKey: strategyCardListQueryKey(),
    queryFn: () => getStrategyCardList(),
  });
}

export function useCreateStrategyCardMutation() {
  return useMutation({
    mutationFn: createStrategyCard,
  });
}

export function useDuplicateStrategyCardMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: duplicateStrategyCard,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: strategyCardListQueryKey() });
    },
  });
}

export function useUpdateStrategyCardMutation(strategyCardId?: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: StrategyCardUpsertPayload) => {
      if (!strategyCardId) {
        throw new ApiClientError({
          status: 500,
          fallbackMessage: "Strategy card id is missing.",
        });
      }

      return updateStrategyCard(strategyCardId, payload);
    },
    onSuccess: (detail) => {
      if (strategyCardId) {
        queryClient.setQueryData(strategyCardQueryKey(strategyCardId), detail);
      }
    },
  });
}
