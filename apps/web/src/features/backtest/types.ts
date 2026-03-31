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

export interface SummaryMetrics {
  total_return_rate: number;
  max_drawdown_rate: number;
  win_rate: number;
  profit_factor: number;
  trade_count: number;
  avg_holding_bars: number;
  final_equity: number;
}

export interface CurvePoint {
  ts: string;
  value: number;
}

export interface TradeRecord {
  trade_id: string;
  entry_at: string;
  exit_at: string;
  entry_price: number;
  exit_price: number;
  quantity: number;
  pnl_amount: number;
  pnl_rate: number;
  exit_reason: string;
}

export interface BacktestResultResponse {
  result_id: string;
  run_id: string;
  strategy_card_id: string;
  strategy_snapshot_id: string;
  dataset_version: string;
  summary_metrics: SummaryMetrics;
  equity_curve: CurvePoint[];
  drawdown_curve: CurvePoint[];
  trades: TradeRecord[];
  result_summary: Record<string, unknown>;
  created_at: string;
}

export type ConclusionNextAction =
  | "rerun"
  | "refine_rules"
  | "observe_only"
  | "add_to_handbook"
  | "discard";

export const CONCLUSION_NEXT_ACTION_LABELS: Record<ConclusionNextAction, string> = {
  rerun: "重新回测",
  refine_rules: "优化规则",
  observe_only: "仅观察",
  add_to_handbook: "加入交易手册",
  discard: "放弃此策略",
};

export interface ConclusionUpsertPayload {
  backtest_result_id: string;
  is_worth_researching: boolean;
  can_accept_drawdown: boolean;
  market_condition_notes?: string;
  next_action: ConclusionNextAction;
  notes?: string;
}

export interface ConclusionResponse {
  id: string;
  strategy_card_id: string;
  backtest_result_id: string;
  is_worth_researching: boolean;
  can_accept_drawdown: boolean;
  market_condition_notes: string | null;
  next_action: ConclusionNextAction;
  notes: string | null;
  created_at: string;
  updated_at: string;
}
