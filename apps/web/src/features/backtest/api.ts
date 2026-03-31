import { useMutation, useQuery } from "@tanstack/react-query";

import { apiRequest } from "@/lib/api/client";

import type {
  BacktestResultResponse,
  BacktestRunResponse,
  ConclusionResponse,
  ConclusionUpsertPayload,
  HandbookCreatePayload,
  HandbookEntryResponse,
} from "./types";

export const backtestRunQueryKey = (runId: string) =>
  ["backtest-run", runId] as const;

export const backtestResultQueryKey = (runId: string) =>
  ["backtest-result", runId] as const;

export async function startBacktest(strategyCardId: string) {
  return apiRequest<BacktestRunResponse>(`/strategy-cards/${strategyCardId}/backtests`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export async function getBacktestRun(runId: string) {
  return apiRequest<BacktestRunResponse>(`/backtests/${runId}`);
}

export async function getBacktestResult(runId: string) {
  return apiRequest<BacktestResultResponse>(`/backtests/${runId}/result`);
}

export async function createConclusion(
  strategyCardId: string,
  payload: ConclusionUpsertPayload,
) {
  return apiRequest<ConclusionResponse>(
    `/strategy-cards/${strategyCardId}/conclusions`,
    {
      method: "POST",
      body: JSON.stringify(payload),
    },
  );
}

export function useBacktestRunQuery(runId: string | undefined) {
  return useQuery({
    queryKey: runId ? backtestRunQueryKey(runId) : ["backtest-run", "idle"],
    queryFn: () => getBacktestRun(runId as string),
    enabled: Boolean(runId),
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      if (status === "queued" || status === "running") {
        return 2500;
      }
      return false;
    },
  });
}

export function useBacktestResultQuery(runId: string | undefined, enabled: boolean) {
  return useQuery({
    queryKey: runId ? backtestResultQueryKey(runId) : ["backtest-result", "idle"],
    queryFn: () => getBacktestResult(runId as string),
    enabled: Boolean(runId) && enabled,
    retry: false,
  });
}

export function useCreateConclusionMutation(strategyCardId: string | undefined) {
  return useMutation({
    mutationFn: (payload: ConclusionUpsertPayload) => {
      if (!strategyCardId) throw new Error("Strategy card id is missing.");
      return createConclusion(strategyCardId, payload);
    },
  });
}

export async function createHandbookEntry(payload: HandbookCreatePayload) {
  return apiRequest<HandbookEntryResponse>("/handbook", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function useCreateHandbookEntryMutation() {
  return useMutation({
    mutationFn: (payload: HandbookCreatePayload) => createHandbookEntry(payload),
  });
}

export function useStartBacktestMutation(strategyCardId?: string) {
  return useMutation({
    mutationFn: async () => {
      if (!strategyCardId) {
        throw new Error("Strategy card id is missing.");
      }
      return startBacktest(strategyCardId);
    },
  });
}
