"use client";

import Link from "next/link";

import { useRecentBacktestsQuery } from "../api";
import styles from "@/app/page.module.css";

function formatDateTime(value: string | null) {
  if (!value) {
    return null;
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
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

export function RecentBacktestList() {
  const query = useRecentBacktestsQuery();
  const items = query.data?.items ?? [];

  if (query.isLoading) {
    return (
      <section className={styles.panel} data-testid="recent-backtests-loading">
        <h2 className={styles.panelTitle}>最近实验记录</h2>
        <p className={styles.note}>正在加载最近实验记录…</p>
      </section>
    );
  }

  if (query.isError) {
    return (
      <section className={styles.panel} data-testid="recent-backtests-error">
        <h2 className={styles.panelTitle}>最近实验记录</h2>
        <p className={styles.note}>最近实验记录加载失败，请刷新后重试。</p>
      </section>
    );
  }

  if (items.length === 0) {
    return (
      <section className={styles.panel} data-testid="recent-backtests-empty">
        <h2 className={styles.panelTitle}>最近实验记录</h2>
        <p className={styles.note}>最近还没有新的实验记录。先发起一次回测，形成第一条实验记录。</p>
      </section>
    );
  }

  return (
    <section className={styles.panel} data-testid="recent-backtests">
      <h2 className={styles.panelTitle}>最近实验记录</h2>
      <ul className={styles.loop} data-testid="recent-backtests-items">
        {items.map((item) => {
          const createdAt = formatDateTime(item.created_at);
          const finishedAt = formatDateTime(item.finished_at);
          const startedAt = formatDateTime(item.started_at);

          return (
            <li key={item.run_id} className={styles.recentBacktestItem} data-testid={`recent-backtest-item-${item.run_id}`}>
              <div className={styles.recentBacktestSummary}>
                <strong>{item.strategy_card_name}</strong>
                <div>
                  状态：{formatStatus(item.status)}
                  {createdAt ? ` · 创建于 ${createdAt}` : ""}
                  {startedAt ? ` · 开始于 ${startedAt}` : ""}
                  {finishedAt ? ` · 结束于 ${finishedAt}` : ""}
                </div>
              </div>
              {item.result_url ? (
                <Link
                  className={styles.cta}
                  href={item.result_url.replace(/^\/api/, "")}
                  data-testid={`recent-backtest-result-link-${item.run_id}`}
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
