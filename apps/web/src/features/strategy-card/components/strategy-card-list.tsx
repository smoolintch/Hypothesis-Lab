"use client";

import Link from "next/link";

import { useStrategyCardListQuery } from "../api";
import styles from "@/app/page.module.css";

function formatUpdatedAt(value: string) {
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

export function StrategyCardList() {
  const query = useStrategyCardListQuery();
  const items = query.data?.items ?? [];

  if (query.isLoading) {
    return (
      <section className={styles.panel} data-testid="strategy-card-list-loading">
        <h2 className={styles.panelTitle}>已有策略卡</h2>
        <p className={styles.note}>正在加载策略列表…</p>
      </section>
    );
  }

  if (query.isError) {
    return (
      <section className={styles.panel} data-testid="strategy-card-list-error">
        <h2 className={styles.panelTitle}>已有策略卡</h2>
        <p className={styles.note}>策略列表加载失败，请刷新后重试。</p>
      </section>
    );
  }

  if (items.length === 0) {
    return (
      <section className={styles.panel} data-testid="strategy-card-list-empty">
        <h2 className={styles.panelTitle}>已有策略卡</h2>
        <p className={styles.note}>还没有任何策略卡。先创建第一张策略卡，开始一次完整验证闭环。</p>
      </section>
    );
  }

  return (
    <section className={styles.panel} data-testid="strategy-card-list">
      <h2 className={styles.panelTitle}>已有策略卡</h2>
      <ul className={styles.loop} data-testid="strategy-card-list-items">
        {items.map((item) => (
          <li key={item.id} data-testid={`strategy-card-list-item-${item.id}`}>
            <div>
              <strong>{item.name}</strong>
              <div>
                {item.symbol} · {item.timeframe} · 最近更新 {formatUpdatedAt(item.updated_at)}
              </div>
            </div>
            <div className={styles.actions}>
              <Link
                className={styles.cta}
                href={`/strategy-cards/${item.id}/edit`}
                data-testid={`strategy-card-edit-link-${item.id}`}
              >
                进入编辑
              </Link>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
