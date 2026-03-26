import { z } from "zod";

import { SYMBOLS, TIMEFRAMES } from "./types";

const dateTimeLocalSchema = z
  .string()
  .trim()
  .min(1, "请选择时间")
  .refine((value) => !Number.isNaN(new Date(value).valueOf()), "请输入有效时间");

const maCrossParamsSchema = z
  .object({
    ma_type: z.enum(["sma", "ema"], {
      error: "请选择均线类型",
    }),
    fast_period: z
      .number()
      .int("快线周期必须是整数")
      .min(2, "快线周期最小为 2")
      .max(200, "快线周期最大为 200"),
    slow_period: z
      .number()
      .int("慢线周期必须是整数")
      .min(3, "慢线周期最小为 3")
      .max(400, "慢线周期最大为 400"),
    cross_direction: z.enum(["golden", "dead"], {
      error: "请选择穿越方向",
    }),
  })
  .superRefine((value, ctx) => {
    if (value.slow_period <= value.fast_period) {
      ctx.addIssue({
        code: z.ZodIssueCode.custom,
        path: ["slow_period"],
        message: "慢线周期必须大于快线周期",
      });
    }
  });

const rsiThresholdParamsSchema = z.object({
  period: z
    .number()
    .int("RSI 周期必须是整数")
    .min(2, "RSI 周期最小为 2")
    .max(100, "RSI 周期最大为 100"),
  comparison: z.enum(["lte", "gte"], {
    error: "请选择比较方式",
  }),
  threshold: z
    .number()
    .min(0, "阈值最小为 0")
    .max(100, "阈值最大为 100"),
});

const priceBreakoutParamsSchema = z.object({
  lookback_bars: z
    .number()
    .int("回看 K 线数必须是整数")
    .min(2, "回看 K 线数最小为 2")
    .max(200, "回看 K 线数最大为 200"),
  breakout_side: z.enum(["break_high", "break_low"], {
    error: "请选择突破方向",
  }),
});

const streakReversalParamsSchema = z.object({
  direction: z.enum(["up", "down"], {
    error: "请选择连续方向",
  }),
  streak_count: z
    .number()
    .int("连续根数必须是整数")
    .min(2, "连续根数最小为 2")
    .max(10, "连续根数最大为 10"),
});

const fixedStopLossParamsSchema = z.object({
  stop_loss_rate: z
    .number()
    .gt(0, "止损比例必须大于 0")
    .lt(1, "止损比例必须小于 1"),
});

const fixedTakeProfitParamsSchema = z.object({
  take_profit_rate: z
    .number()
    .gt(0, "止盈比例必须大于 0")
    .lt(1, "止盈比例必须小于 1"),
});

const entryExitRuleSchema = z.discriminatedUnion("template_key", [
  z.object({
    template_key: z.literal("ma_cross"),
    params: maCrossParamsSchema,
  }),
  z.object({
    template_key: z.literal("rsi_threshold"),
    params: rsiThresholdParamsSchema,
  }),
  z.object({
    template_key: z.literal("price_breakout"),
    params: priceBreakoutParamsSchema,
  }),
  z.object({
    template_key: z.literal("streak_reversal"),
    params: streakReversalParamsSchema,
  }),
]);

const stopLossRuleSchema = z
  .union([
    z.object({
      template_key: z.literal("fixed_stop_loss"),
      params: fixedStopLossParamsSchema,
    }),
    z.null(),
    z.undefined(),
  ])
  .transform((value) => value ?? null);

const takeProfitRuleSchema = z
  .union([
    z.object({
      template_key: z.literal("fixed_take_profit"),
      params: fixedTakeProfitParamsSchema,
    }),
    z.null(),
    z.undefined(),
  ])
  .transform((value) => value ?? null);

export const strategyCardFormSchema = z.object({
  name: z
    .string()
    .trim()
    .min(1, "请输入策略名称")
    .max(120, "策略名称最多 120 个字符"),
  symbol: z.enum(SYMBOLS, {
    error: "请选择支持的标的",
  }),
  timeframe: z.enum(TIMEFRAMES, {
    error: "请选择支持的周期",
  }),
  backtest_range: z
    .object({
      start_at: dateTimeLocalSchema,
      end_at: dateTimeLocalSchema,
    })
    .superRefine((value, ctx) => {
      if (new Date(value.end_at) <= new Date(value.start_at)) {
        ctx.addIssue({
          code: z.ZodIssueCode.custom,
          path: ["end_at"],
          message: "结束时间必须晚于开始时间",
        });
      }
    }),
  initial_capital: z
    .number()
    .gt(0, "初始资金必须大于 0"),
  fee_rate: z
    .number()
    .min(0, "手续费率不能小于 0")
    .max(0.01, "手续费率不能大于 0.01"),
  rule_set: z.object({
    entry: entryExitRuleSchema,
    exit: entryExitRuleSchema,
    stop_loss: stopLossRuleSchema,
    take_profit: takeProfitRuleSchema,
  }),
});

export type StrategyCardFormInput = z.input<typeof strategyCardFormSchema>;
export type StrategyCardFormValues = z.output<typeof strategyCardFormSchema>;
