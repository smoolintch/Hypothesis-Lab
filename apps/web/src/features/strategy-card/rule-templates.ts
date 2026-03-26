import type {
  EntryExitRuleInstance,
  RuleInstanceByTemplateKey,
  RulePosition,
  RuleTemplateKey,
  StopLossRuleInstance,
  TakeProfitRuleInstance,
} from "./types";
import {
  ENTRY_EXIT_TEMPLATE_KEYS,
  STOP_LOSS_TEMPLATE_KEYS,
  TAKE_PROFIT_TEMPLATE_KEYS,
} from "./types";

type RuleTemplateFieldOption = {
  value: string;
  label: string;
};

export type RuleTemplateFieldConfig = {
  name: string;
  label: string;
  input: "number" | "select";
  description?: string;
  min?: number;
  max?: number;
  step?: number;
  integer?: boolean;
  options?: RuleTemplateFieldOption[];
};

type RuleTemplateInstance =
  | EntryExitRuleInstance
  | StopLossRuleInstance
  | TakeProfitRuleInstance;

type RuleTemplateDefinition<T extends RuleTemplateKey = RuleTemplateKey> = {
  key: T;
  label: string;
  description: string;
  positions: RulePosition[];
  defaultValue: RuleInstanceByTemplateKey[T];
  fields: RuleTemplateFieldConfig[];
};

export const RULE_TEMPLATE_DEFINITIONS: Record<
  RuleTemplateKey,
  RuleTemplateDefinition
> = {
  ma_cross: {
    key: "ma_cross",
    label: "均线穿越",
    description: "根据快慢均线穿越信号触发入场或出场。",
    positions: ["entry", "exit"],
    defaultValue: {
      template_key: "ma_cross",
      params: {
        ma_type: "ema",
        fast_period: 20,
        slow_period: 50,
        cross_direction: "golden",
      },
    },
    fields: [
      {
        name: "ma_type",
        label: "均线类型",
        input: "select",
        options: [
          { value: "sma", label: "SMA" },
          { value: "ema", label: "EMA" },
        ],
      },
      {
        name: "fast_period",
        label: "快线周期",
        input: "number",
        integer: true,
        min: 2,
        max: 200,
        step: 1,
      },
      {
        name: "slow_period",
        label: "慢线周期",
        input: "number",
        integer: true,
        min: 3,
        max: 400,
        step: 1,
      },
      {
        name: "cross_direction",
        label: "穿越方向",
        input: "select",
        options: [
          { value: "golden", label: "金叉" },
          { value: "dead", label: "死叉" },
        ],
      },
    ],
  },
  rsi_threshold: {
    key: "rsi_threshold",
    label: "RSI 阈值",
    description: "根据 RSI 高于或低于阈值触发信号。",
    positions: ["entry", "exit"],
    defaultValue: {
      template_key: "rsi_threshold",
      params: {
        period: 14,
        comparison: "gte",
        threshold: 70,
      },
    },
    fields: [
      {
        name: "period",
        label: "RSI 周期",
        input: "number",
        integer: true,
        min: 2,
        max: 100,
        step: 1,
      },
      {
        name: "comparison",
        label: "比较方式",
        input: "select",
        options: [
          { value: "lte", label: "<= 阈值" },
          { value: "gte", label: ">= 阈值" },
        ],
      },
      {
        name: "threshold",
        label: "阈值",
        input: "number",
        min: 0,
        max: 100,
        step: 1,
      },
    ],
  },
  price_breakout: {
    key: "price_breakout",
    label: "价格突破",
    description: "根据最近区间高点或低点突破触发信号。",
    positions: ["entry", "exit"],
    defaultValue: {
      template_key: "price_breakout",
      params: {
        lookback_bars: 20,
        breakout_side: "break_high",
      },
    },
    fields: [
      {
        name: "lookback_bars",
        label: "回看 K 线数",
        input: "number",
        integer: true,
        min: 2,
        max: 200,
        step: 1,
      },
      {
        name: "breakout_side",
        label: "突破方向",
        input: "select",
        options: [
          { value: "break_high", label: "突破高点" },
          { value: "break_low", label: "跌破低点" },
        ],
      },
    ],
  },
  streak_reversal: {
    key: "streak_reversal",
    label: "连续反转",
    description: "根据连续上涨或下跌后的反转触发信号。",
    positions: ["entry", "exit"],
    defaultValue: {
      template_key: "streak_reversal",
      params: {
        direction: "down",
        streak_count: 3,
      },
    },
    fields: [
      {
        name: "direction",
        label: "连续方向",
        input: "select",
        options: [
          { value: "up", label: "连涨" },
          { value: "down", label: "连跌" },
        ],
      },
      {
        name: "streak_count",
        label: "连续根数",
        input: "number",
        integer: true,
        min: 2,
        max: 10,
        step: 1,
      },
    ],
  },
  fixed_stop_loss: {
    key: "fixed_stop_loss",
    label: "固定止损",
    description: "按固定比例设置止损。",
    positions: ["stop_loss"],
    defaultValue: {
      template_key: "fixed_stop_loss",
      params: {
        stop_loss_rate: 0.08,
      },
    },
    fields: [
      {
        name: "stop_loss_rate",
        label: "止损比例",
        input: "number",
        min: 0.001,
        max: 0.999,
        step: 0.001,
      },
    ],
  },
  fixed_take_profit: {
    key: "fixed_take_profit",
    label: "固定止盈",
    description: "按固定比例设置止盈。",
    positions: ["take_profit"],
    defaultValue: {
      template_key: "fixed_take_profit",
      params: {
        take_profit_rate: 0.15,
      },
    },
    fields: [
      {
        name: "take_profit_rate",
        label: "止盈比例",
        input: "number",
        min: 0.001,
        max: 0.999,
        step: 0.001,
      },
    ],
  },
};

export const RULE_TEMPLATES_BY_POSITION: Record<RulePosition, readonly RuleTemplateKey[]> =
  {
    entry: ENTRY_EXIT_TEMPLATE_KEYS,
    exit: ENTRY_EXIT_TEMPLATE_KEYS,
    stop_loss: STOP_LOSS_TEMPLATE_KEYS,
    take_profit: TAKE_PROFIT_TEMPLATE_KEYS,
  };

export function getRuleTemplateDefinition(templateKey: RuleTemplateKey) {
  return RULE_TEMPLATE_DEFINITIONS[templateKey];
}

export function createDefaultRuleInstance<T extends RuleTemplateKey>(
  templateKey: T,
): RuleInstanceByTemplateKey[T] {
  const template = RULE_TEMPLATE_DEFINITIONS[templateKey];

  return {
    template_key: template.defaultValue.template_key,
    params: { ...template.defaultValue.params },
  } as RuleInstanceByTemplateKey[T];
}

export function cloneRuleInstance<T extends RuleTemplateInstance | null>(
  rule: T,
): T {
  if (rule === null) {
    return null as T;
  }

  return {
    template_key: rule.template_key,
    params: { ...rule.params },
  } as T;
}
