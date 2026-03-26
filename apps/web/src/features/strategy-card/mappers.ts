import { cloneRuleInstance, createDefaultRuleInstance } from "./rule-templates";
import type { StrategyCardFormValues } from "./schema";
import type { StrategyCardDetail, StrategyCardUpsertPayload } from "./types";

const DEFAULT_START_AT = "2023-01-01T00:00:00Z";
const DEFAULT_END_AT = "2024-01-01T00:00:00Z";

export function toDateTimeLocalValue(value: string): string {
  const date = new Date(value);

  if (Number.isNaN(date.valueOf())) {
    return "";
  }

  const localDate = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return localDate.toISOString().slice(0, 16);
}

export function toUtcIsoString(value: string): string {
  return new Date(value).toISOString();
}

export const defaultStrategyCardFormValues: StrategyCardFormValues = {
  name: "",
  symbol: "BTCUSDT",
  timeframe: "4H",
  backtest_range: {
    start_at: toDateTimeLocalValue(DEFAULT_START_AT),
    end_at: toDateTimeLocalValue(DEFAULT_END_AT),
  },
  initial_capital: 10000,
  fee_rate: 0.001,
  rule_set: {
    entry: createDefaultRuleInstance("ma_cross"),
    exit: createDefaultRuleInstance("rsi_threshold"),
    stop_loss: createDefaultRuleInstance("fixed_stop_loss"),
    take_profit: null,
  },
};

export function createDefaultStrategyCardFormValues(): StrategyCardFormValues {
  return {
    name: defaultStrategyCardFormValues.name,
    symbol: defaultStrategyCardFormValues.symbol,
    timeframe: defaultStrategyCardFormValues.timeframe,
    backtest_range: {
      start_at: defaultStrategyCardFormValues.backtest_range.start_at,
      end_at: defaultStrategyCardFormValues.backtest_range.end_at,
    },
    initial_capital: defaultStrategyCardFormValues.initial_capital,
    fee_rate: defaultStrategyCardFormValues.fee_rate,
    rule_set: {
      entry: cloneRuleInstance(defaultStrategyCardFormValues.rule_set.entry),
      exit: cloneRuleInstance(defaultStrategyCardFormValues.rule_set.exit),
      stop_loss: cloneRuleInstance(defaultStrategyCardFormValues.rule_set.stop_loss),
      take_profit: cloneRuleInstance(
        defaultStrategyCardFormValues.rule_set.take_profit,
      ),
    },
  };
}

export function toStrategyCardPayload(
  values: StrategyCardFormValues,
): StrategyCardUpsertPayload {
  return {
    name: values.name.trim(),
    symbol: values.symbol,
    timeframe: values.timeframe,
    backtest_range: {
      start_at: toUtcIsoString(values.backtest_range.start_at),
      end_at: toUtcIsoString(values.backtest_range.end_at),
    },
    initial_capital: values.initial_capital,
    fee_rate: values.fee_rate,
    rule_set: {
      entry: cloneRuleInstance(values.rule_set.entry),
      exit: cloneRuleInstance(values.rule_set.exit),
      stop_loss: cloneRuleInstance(values.rule_set.stop_loss),
      take_profit: cloneRuleInstance(values.rule_set.take_profit),
    },
  };
}

export function toStrategyCardFormValues(
  detail: StrategyCardDetail,
): StrategyCardFormValues {
  return {
    name: detail.name,
    symbol: detail.symbol,
    timeframe: detail.timeframe,
    backtest_range: {
      start_at: toDateTimeLocalValue(detail.backtest_range.start_at),
      end_at: toDateTimeLocalValue(detail.backtest_range.end_at),
    },
    initial_capital: detail.initial_capital,
    fee_rate: detail.fee_rate,
    rule_set: {
      entry: cloneRuleInstance(detail.rule_set.entry),
      exit: cloneRuleInstance(detail.rule_set.exit),
      stop_loss: cloneRuleInstance(detail.rule_set.stop_loss),
      take_profit: cloneRuleInstance(detail.rule_set.take_profit),
    },
  };
}
