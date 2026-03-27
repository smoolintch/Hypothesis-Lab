export type BacktestRunStatus =
  | "queued"
  | "running"
  | "succeeded"
  | "failed"
  | "cancelled";

export interface BacktestRunResponse {
  run_id: string;
  strategy_card_id: string;
  strategy_snapshot_id: string;
  status: BacktestRunStatus | string;
  error_code: string | null;
  error_message: string | null;
  started_at: string | null;
  finished_at: string | null;
  result_url: string | null;
  created_at: string;
}
