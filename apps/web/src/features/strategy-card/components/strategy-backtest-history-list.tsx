"use client";

import Link from "next/link";

import { ApiClientError } from "@/lib/api/client";

import { useStrategyBacktestHistoryQuery } from "../api";
import styles from "./strategy-card-editor.module.css";

function formatDateTime(value: string | null) {
  if (!value) {
    return null;
  }

  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) {
    return value;
  }

  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatStatus(status: "queued" | "running" | "succeeded" | "failed" | "cancelled") {
  switch (status) {
    case "queued":
      return "排队中";
    case "running":
      return "运行中";
    case "succeeded":
      return "已完成";
    case "failed":
      return "失败";
    case "cancelled":
      return "已取消";
    default:
      return status;
  }
}

export function StrategyBacktestHistoryList({ strategyCardId }: { strategyCardId: string }) {
  const query = useStrategyBacktestHistoryQuery(strategyCardId);
  const items = query.data?.items ?? [];

  if (query.isLoading) {
    return (
      <section className={styles.historySection} data-testid="strategy-backtest-history-loading">
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>历史回测记录</h2>
          <p className={styles.sectionDescription}>正在加载该策略的历史回测记录…</p>
        </div>
      </section>
    );
  }

  if (query.isError) {
    const error =
      query.error instanceof ApiClientError
        ? query.error
        : new ApiClientError({
            status: 500,
            fallbackMessage: "加载历史回测记录失败。",
          });
    const isNotFound =
      error.status === 404 || error.code === "STRATEGY_CARD_NOT_FOUND";

    return (
      <section className={styles.historySection} data-testid="strategy-backtest-history-error">
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>历史回测记录</h2>
        </div>
        <div className={`${styles.message} ${styles.messageError}`} role="alert">
          <p>{isNotFound ? "策略卡不存在，无法加载历史回测记录。" : error.message}</p>
        </div>
        {!isNotFound ? (
          <div className={styles.inlineActions}>
            <button className={styles.buttonSecondary} type="button" onClick={() => query.refetch()}>
              重试
            </button>
          </div>
        ) : null}
      </section>
    );
  }

  if (items.length === 0) {
    return (
      <section className={styles.historySection} data-testid="strategy-backtest-history-empty">
        <div className={styles.sectionHeader}>
          <h2 className={styles.sectionTitle}>历史回测记录</h2>
          <p className={styles.sectionDescription}>
            当前策略还没有历史回测记录。你可以先保存当前策略，再发起第一次回测。
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className={styles.historySection} data-testid="strategy-backtest-history">
      <div className={styles.sectionHeader}>
        <h2 className={styles.sectionTitle}>历史回测记录</h2>
        <p className={styles.sectionDescription}>展示该策略最近形成的历史回测记录，便于回到已有结果继续查看。</p>
      </div>
      <ul className={styles.historyList} data-testid="strategy-backtest-history-items">
        {items.map((item) => {
          const createdAt = formatDateTime(item.created_at);
          const startedAt = formatDateTime(item.started_at);
          const finishedAt = formatDateTime(item.finished_at);

          return (
            <li
              key={item.run_id}
              className={styles.historyItem}
              data-testid={`strategy-backtest-history-item-${item.run_id}`}
            >
              <div className={styles.historySummary}>
                <strong className={styles.historyRunId}>run_id: {item.run_id}</strong>
                <div className={styles.historyMeta}>状态：{formatStatus(item.status)}</div>
                <div className={styles.historyMeta}>
                  {createdAt ? `创建于 ${createdAt}` : null}
                  {startedAt ? ` · 开始于 ${startedAt}` : null}
                  {finishedAt ? ` · 结束于 ${finishedAt}` : null}
                </div>
              </div>
              {item.result_url ? (
                <Link
                  className={styles.buttonSecondary}
                  href={`/backtests/${item.run_id}`}
                  data-testid={`strategy-backtest-history-result-link-${item.run_id}`}
                >
                  查看结果
                </Link>
              ) : null}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
