"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { ApiClientError } from "@/lib/api/client";

import { useBacktestRunQuery } from "../api";
import styles from "../backtest-run.module.css";

function formatDateTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.valueOf())) {
    return "-";
  }
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function BacktestRunView() {
  const params = useParams<{ run_id: string }>();
  const runId = typeof params?.run_id === "string" ? params.run_id : undefined;
  const query = useBacktestRunQuery(runId);

  if (!runId) {
    return (
      <main className={styles.page} data-testid="backtest-run-page">
        <div className={styles.container}>
          <p className={styles.subtitle}>缺少 run_id 参数。</p>
        </div>
      </main>
    );
  }

  if (query.isPending) {
    return (
      <main className={styles.page} data-testid="backtest-run-page">
        <div className={styles.container}>
          <header className={styles.header}>
            <p className={styles.eyebrow}>Backtest</p>
            <h1 className={styles.title}>回测运行</h1>
            <p className={styles.subtitle}>正在从真实 API 加载回测运行信息。</p>
          </header>
          <section
            className={`${styles.panel} ${styles.statePanel}`}
            data-testid="backtest-run-loading"
          >
            <p>加载中…</p>
            <p className={styles.valueMono} data-testid="backtest-run-id">
              {runId}
            </p>
          </section>
        </div>
      </main>
    );
  }

  if (query.error) {
    const err =
      query.error instanceof ApiClientError
        ? query.error
        : new ApiClientError({
            status: 500,
            fallbackMessage: "加载回测运行失败。",
          });
    const isNotFound =
      err.status === 404 || err.code === "BACKTEST_RUN_NOT_FOUND";

    return (
      <main className={styles.page} data-testid="backtest-run-page">
        <div className={styles.container}>
          <header className={styles.header}>
            <p className={styles.eyebrow}>Backtest</p>
            <h1 className={styles.title}>回测运行</h1>
          </header>
          <section
            className={`${styles.panel} ${styles.statePanel}`}
            data-testid={
              isNotFound ? "backtest-run-not-found" : "backtest-run-load-error"
            }
          >
            <div
              className={`${styles.message} ${styles.messageError}`}
              role="alert"
            >
              <p>{isNotFound ? "回测运行不存在。" : err.message}</p>
            </div>
            <div className={styles.inlineActions}>
              {!isNotFound ? (
                <button
                  className={styles.linkButton}
                  type="button"
                  onClick={() => query.refetch()}
                >
                  重试
                </button>
              ) : null}
              <Link className={styles.linkButton} href="/strategy-cards/new">
                新建策略卡
              </Link>
            </div>
          </section>
        </div>
      </main>
    );
  }

  const data = query.data;
  const status = data.status;

  return (
    <main className={styles.page} data-testid="backtest-run-page">
      <div className={styles.container}>
        <header className={styles.header}>
          <p className={styles.eyebrow}>Backtest</p>
          <h1 className={styles.title}>回测运行</h1>
          <p className={styles.subtitle}>
            本页仅绑定真实 API 状态；指标与曲线尚未接入，不展示伪造结果。
          </p>
        </header>

        <section className={styles.panel}>
          <div className={styles.kv}>
            <span className={styles.label}>run_id</span>
            <span className={styles.valueMono} data-testid="backtest-run-id">
              {data.run_id}
            </span>
          </div>
          <div className={styles.kv}>
            <span className={styles.label}>status</span>
            <span className={styles.value} data-testid="backtest-run-status">
              {status}
            </span>
          </div>
          <div className={styles.kv}>
            <span className={styles.label}>strategy_card_id</span>
            <span className={styles.valueMono}>{data.strategy_card_id}</span>
          </div>
          <div className={styles.kv}>
            <span className={styles.label}>strategy_snapshot_id</span>
            <span className={styles.valueMono}>{data.strategy_snapshot_id}</span>
          </div>
          <div className={styles.kv}>
            <span className={styles.label}>created_at</span>
            <span className={styles.value}>{formatDateTime(data.created_at)}</span>
          </div>

          {status === "queued" ? (
            <div
              className={`${styles.message} ${styles.messageNeutral}`}
              data-testid="backtest-run-state-queued"
            >
              <p>回测已排队（queued），当前后端不执行真实回测，状态可能长期保持在此。</p>
            </div>
          ) : null}

          {status === "running" ? (
            <div
              className={`${styles.message} ${styles.messageNeutral}`}
              data-testid="backtest-run-state-running"
            >
              <p>回测运行中（running）。结果指标尚未接入，本页仅展示状态轮询占位。</p>
            </div>
          ) : null}

          {status === "failed" ? (
            <div
              className={`${styles.message} ${styles.messageError}`}
              data-testid="backtest-run-state-failed"
            >
              <p>回测失败（failed）。</p>
              {data.error_code ? (
                <p className={styles.valueMono}>code: {data.error_code}</p>
              ) : null}
              {data.error_message ? <p>{data.error_message}</p> : null}
            </div>
          ) : null}

          {status === "cancelled" ? (
            <div
              className={`${styles.message} ${styles.messageWarn}`}
              data-testid="backtest-run-state-cancelled"
            >
              <p>回测已取消（cancelled）。</p>
              {data.error_message ? <p>{data.error_message}</p> : null}
            </div>
          ) : null}

          {status === "succeeded" ? (
            <div
              className={`${styles.message} ${styles.messageSuccess}`}
              data-testid="backtest-run-state-succeeded-placeholder"
            >
              <p>
                状态为 succeeded，但当前阶段结果接口与指标展示尚未接入。请勿在此页伪造
                BacktestResult；后续将基于真实结果接口扩展。
              </p>
              {data.result_url ? (
                <p className={styles.valueMono}>result_url: {data.result_url}</p>
              ) : (
                <p className={styles.valueMono}>result_url: （空）</p>
              )}
            </div>
          ) : null}

          {!["queued", "running", "failed", "cancelled", "succeeded"].includes(
            String(status),
          ) ? (
            <div className={`${styles.message} ${styles.messageWarn}`}>
              <p>未知状态：{String(status)}</p>
            </div>
          ) : null}

          <div className={styles.inlineActions}>
            <Link
              className={styles.linkButton}
              href={`/strategy-cards/${data.strategy_card_id}/edit`}
            >
              返回策略编辑
            </Link>
          </div>
        </section>
      </div>
    </main>
  );
}
