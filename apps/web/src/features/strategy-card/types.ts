export const SYMBOLS = ["BTCUSDT", "ETHUSDT"] as const;
export const TIMEFRAMES = ["4H", "1D"] as const;

export const ENTRY_EXIT_TEMPLATE_KEYS = [
  "ma_cross",
  "rsi_threshold",
  "price_breakout",
  "streak_reversal",
] as const;
export const STOP_LOSS_TEMPLATE_KEYS = ["fixed_stop_loss"] as const;
export const TAKE_PROFIT_TEMPLATE_KEYS = ["fixed_take_profit"] as const;

export type SymbolValue = (typeof SYMBOLS)[number];
export type TimeframeValue = (typeof TIMEFRAMES)[number];
export type EntryExitTemplateKey = (typeof ENTRY_EXIT_TEMPLATE_KEYS)[number];
export type StopLossTemplateKey = (typeof STOP_LOSS_TEMPLATE_KEYS)[number];
export type TakeProfitTemplateKey = (typeof TAKE_PROFIT_TEMPLATE_KEYS)[number];
export type RuleTemplateKey =
  | EntryExitTemplateKey
  | StopLossTemplateKey
  | TakeProfitTemplateKey;
export type RulePosition = "entry" | "exit" | "stop_loss" | "take_profit";

export interface MaCrossParams {
  ma_type: "sma" | "ema";
  fast_period: number;
  slow_period: number;
  cross_direction: "golden" | "dead";
}

export interface RsiThresholdParams {
  period: number;
  comparison: "lte" | "gte";
  threshold: number;
}

export interface PriceBreakoutParams {
  lookback_bars: number;
  breakout_side: "break_high" | "break_low";
}

export interface StreakReversalParams {
  direction: "up" | "down";
  streak_count: number;
}

export interface FixedStopLossParams {
  stop_loss_rate: number;
}

export interface FixedTakeProfitParams {
  take_profit_rate: number;
}

export interface RuleParamsByTemplateKey {
  ma_cross: MaCrossParams;
  rsi_threshold: RsiThresholdParams;
  price_breakout: PriceBreakoutParams;
  streak_reversal: StreakReversalParams;
  fixed_stop_loss: FixedStopLossParams;
  fixed_take_profit: FixedTakeProfitParams;
}

export interface RuleInstanceByTemplateKey {
  ma_cross: {
    template_key: "ma_cross";
    params: MaCrossParams;
  };
  rsi_threshold: {
    template_key: "rsi_threshold";
    params: RsiThresholdParams;
  };
  price_breakout: {
    template_key: "price_breakout";
    params: PriceBreakoutParams;
  };
  streak_reversal: {
    template_key: "streak_reversal";
    params: StreakReversalParams;
  };
  fixed_stop_loss: {
    template_key: "fixed_stop_loss";
    params: FixedStopLossParams;
  };
  fixed_take_profit: {
    template_key: "fixed_take_profit";
    params: FixedTakeProfitParams;
  };
}

export type EntryExitRuleInstance =
  | RuleInstanceByTemplateKey["ma_cross"]
  | RuleInstanceByTemplateKey["rsi_threshold"]
  | RuleInstanceByTemplateKey["price_breakout"]
  | RuleInstanceByTemplateKey["streak_reversal"];

export type StopLossRuleInstance = RuleInstanceByTemplateKey["fixed_stop_loss"];
export type TakeProfitRuleInstance = RuleInstanceByTemplateKey["fixed_take_profit"];

export interface StrategyRuleSet {
  entry: EntryExitRuleInstance;
  exit: EntryExitRuleInstance;
  stop_loss: StopLossRuleInstance | null;
  take_profit: TakeProfitRuleInstance | null;
}

export interface StrategyCardUpsertPayload {
  name: string;
  symbol: SymbolValue;
  timeframe: TimeframeValue;
  backtest_range: {
    start_at: string;
    end_at: string;
  };
  initial_capital: number;
  fee_rate: number;
  rule_set: StrategyRuleSet;
}

export interface StrategyCardDetail extends StrategyCardUpsertPayload {
  id: string;
  status: "draft" | "ready" | "archived";
  updated_at: string;
  latest_backtest_run_id: string | null;
  created_at: string;
}

export type StrategyCardEditorMode = "create" | "edit";
