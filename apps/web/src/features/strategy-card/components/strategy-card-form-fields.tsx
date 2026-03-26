"use client";

import { useFormContext } from "react-hook-form";

import type { StrategyCardFormInput } from "../schema";
import { SYMBOLS, TIMEFRAMES, type StrategyCardEditorMode } from "../types";
import { RuleSection } from "./rule-section";
import styles from "./strategy-card-editor.module.css";

type StrategyCardFormFieldsProps = {
  mode: StrategyCardEditorMode;
};

function getErrorMessage(error: unknown): string | undefined {
  if (
    error &&
    typeof error === "object" &&
    "message" in error &&
    typeof error.message === "string"
  ) {
    return error.message;
  }

  return undefined;
}

export function StrategyCardFormFields({
  mode,
}: StrategyCardFormFieldsProps) {
  const {
    register,
    formState: { errors },
  } = useFormContext<StrategyCardFormInput>();

  return (
    <>
      <section className={styles.section} data-testid="strategy-card-basic-section">
        <div className={styles.sectionHeader}>
          <div className={styles.sectionTitleRow}>
            <h2 className={styles.sectionTitle}>基础信息</h2>
          </div>
          <p className={styles.sectionDescription}>
            {mode === "create"
              ? "填写策略名称、市场和回测基础参数，首次保存后会自动进入编辑页。"
              : "当前正在编辑已保存的策略卡，保存后会停留在当前页面并回填最新数据。"}
          </p>
        </div>

        <div className={styles.grid}>
          <div className={`${styles.field} ${styles.fieldWide}`}>
            <label className={styles.label} htmlFor="name">
              策略名称
            </label>
            <input
              data-testid="strategy-card-name-input"
              id="name"
              className={styles.control}
              type="text"
              placeholder="例如：EMA Breakout Draft"
              {...register("name")}
            />
            <span className={styles.hint}>1 到 120 个字符。</span>
            {getErrorMessage(errors.name) ? (
              <p className={styles.errorText}>{getErrorMessage(errors.name)}</p>
            ) : null}
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="symbol">
              标的
            </label>
            <select
              id="symbol"
              data-testid="strategy-card-symbol-select"
              className={styles.control}
              {...register("symbol")}
            >
              {SYMBOLS.map((symbol) => (
                <option key={symbol} value={symbol}>
                  {symbol}
                </option>
              ))}
            </select>
            {getErrorMessage(errors.symbol) ? (
              <p className={styles.errorText}>{getErrorMessage(errors.symbol)}</p>
            ) : null}
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="timeframe">
              周期
            </label>
            <select
              id="timeframe"
              data-testid="strategy-card-timeframe-select"
              className={styles.control}
              {...register("timeframe")}
            >
              {TIMEFRAMES.map((timeframe) => (
                <option key={timeframe} value={timeframe}>
                  {timeframe}
                </option>
              ))}
            </select>
            {getErrorMessage(errors.timeframe) ? (
              <p className={styles.errorText}>
                {getErrorMessage(errors.timeframe)}
              </p>
            ) : null}
          </div>
        </div>
      </section>

      <section className={styles.section} data-testid="strategy-card-backtest-section">
        <div className={styles.sectionHeader}>
          <div className={styles.sectionTitleRow}>
            <h2 className={styles.sectionTitle}>回测范围与执行参数</h2>
          </div>
          <p className={styles.sectionDescription}>
            所有时间会在提交时转换为 UTC ISO 8601 字符串，提交结构与冻结契约保持一致。
          </p>
        </div>

        <div className={styles.grid}>
          <div className={styles.field}>
            <label className={styles.label} htmlFor="backtest-range-start-at">
              开始时间
            </label>
            <input
              id="backtest-range-start-at"
              data-testid="strategy-card-start-at-input"
              className={styles.control}
              type="datetime-local"
              {...register("backtest_range.start_at")}
            />
            {getErrorMessage(errors.backtest_range?.start_at) ? (
              <p className={styles.errorText}>
                {getErrorMessage(errors.backtest_range?.start_at)}
              </p>
            ) : null}
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="backtest-range-end-at">
              结束时间
            </label>
            <input
              id="backtest-range-end-at"
              data-testid="strategy-card-end-at-input"
              className={styles.control}
              type="datetime-local"
              {...register("backtest_range.end_at")}
            />
            {getErrorMessage(errors.backtest_range?.end_at) ? (
              <p className={styles.errorText}>
                {getErrorMessage(errors.backtest_range?.end_at)}
              </p>
            ) : null}
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="initial-capital">
              初始资金
            </label>
            <input
              id="initial-capital"
              data-testid="strategy-card-initial-capital-input"
              className={styles.control}
              type="number"
              min={1}
              step={0.01}
              inputMode="decimal"
              {...register("initial_capital", {
                valueAsNumber: true,
              })}
            />
            {getErrorMessage(errors.initial_capital) ? (
              <p className={styles.errorText}>
                {getErrorMessage(errors.initial_capital)}
              </p>
            ) : null}
          </div>

          <div className={styles.field}>
            <label className={styles.label} htmlFor="fee-rate">
              手续费率
            </label>
            <input
              id="fee-rate"
              data-testid="strategy-card-fee-rate-input"
              className={styles.control}
              type="number"
              min={0}
              max={0.01}
              step={0.0001}
              inputMode="decimal"
              {...register("fee_rate", {
                valueAsNumber: true,
              })}
            />
            <span className={styles.hint}>允许范围：0 到 0.01。</span>
            {getErrorMessage(errors.fee_rate) ? (
              <p className={styles.errorText}>{getErrorMessage(errors.fee_rate)}</p>
            ) : null}
          </div>
        </div>
      </section>

      <RuleSection
        position="entry"
        title="入场规则"
        description="只能选择允许的 entry 模板，切换模板时会清理旧参数。"
        required
      />

      <RuleSection
        position="exit"
        title="出场规则"
        description="只能选择允许的 exit 模板，切换模板时会清理旧参数。"
        required
      />

      <RuleSection
        position="stop_loss"
        title="止损规则"
        description="可选的风险规则，只能使用风险模板。"
      />

      <RuleSection
        position="take_profit"
        title="止盈规则"
        description="可选的风险规则，只能使用风险模板。"
      />
    </>
  );
}
