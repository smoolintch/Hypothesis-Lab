"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { ApiClientError, useDuplicateStrategyCardMutation, useStrategyCardListQuery } from "../api";
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
  const router = useRouter();
  const query = useStrategyCardListQuery();
  const duplicateMutation = useDuplicateStrategyCardMutation();
  const [duplicateError, setDuplicateError] = useState<string | null>(null);
  const [duplicatingStrategyCardId, setDuplicatingStrategyCardId] = useState<string | null>(null);
  const items = query.data?.items ?? [];

  async function handleDuplicate(strategyCardId: string) {
    setDuplicateError(null);
    setDuplicatingStrategyCardId(strategyCardId);

    try {
      const duplicatedCard = await duplicateMutation.mutateAsync(strategyCardId);
      const searchParams = new URLSearchParams({
        sourceId: strategyCardId,
        sourceName:
          items.find((item) => item.id === strategyCardId)?.name ?? "原策略卡",
        duplicatedFrom: "true",
      });
      router.push(`/strategy-cards/${duplicatedCard.id}/edit?${searchParams.toString()}`);
    } catch (error) {
      if (error instanceof ApiClientError) {
        setDuplicateError(error.message);
      } else {
        setDuplicateError("复制策略卡失败，请稍后重试。");
      }
      setDuplicatingStrategyCardId(null);
    }
  }

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
      {duplicateError ? (
        <p className={styles.note} data-testid="strategy-card-duplicate-error">
          {duplicateError}
        </p>
      ) : null}
      <ul className={styles.loop} data-testid="strategy-card-list-items">
        {items.map((item) => {
          const isDuplicating = duplicatingStrategyCardId === item.id;

          return (
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
                <button
                  type="button"
                  className={styles.cta}
                  data-testid={`strategy-card-duplicate-button-${item.id}`}
                  onClick={() => void handleDuplicate(item.id)}
                  disabled={isDuplicating || duplicateMutation.isPending}
                >
                  {isDuplicating ? "复制中…" : "复制策略卡"}
                </button>
              </div>
            </li>
          );
        })}
      </ul>
    </section>
  );
}
