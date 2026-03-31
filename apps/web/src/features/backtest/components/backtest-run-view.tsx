"use client";

import Link from "next/link";
import { useParams } from "next/navigation";

import { ApiClientError } from "@/lib/api/client";

import { useBacktestResultQuery, useBacktestRunQuery } from "../api";
import styles from "../backtest-run.module.css";
import { BacktestResultSection } from "./backtest-result-section";
import { ConclusionForm } from "./conclusion-form";

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

  const runQuery = useBacktestRunQuery(runId);
  const runData = runQuery.data;
  const isSucceeded = runData?.status === "succeeded";
  const hasResultUrl = Boolean(runData?.result_url);

  // 只在 succeeded + result_url 存在时才拉结果
  const resultQuery = useBacktestResultQuery(runId, isSucceeded && hasResultUrl);

  // ── 缺少 run_id ──
  if (!runId) {
    return (
      <main className={styles.page} data-testid="backtest-run-page">
        <div className={styles.container}>
          <p className={styles.subtitle}>缺少 run_id 参数。</p>
        </div>
      </main>
    );
  }

  // ── run 加载中 ──
  if (runQuery.isPending) {
    return (
      <main className={styles.page} data-testid="backtest-run-page">
        <div className={styles.container}>
          <header className={styles.header}>
            <p className={styles.eyebrow}>Backtest</p>
            <h1 className={styles.title}>回测运行</h1>
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

  // ── run 加载失败 ──
  if (runQuery.error) {
    const err =
      runQuery.error instanceof ApiClientError
        ? runQuery.error
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
                  onClick={() => runQuery.refetch()}
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

  const data = runData!;
  const status = data.status;

  return (
    <main className={styles.page} data-testid="backtest-run-page">
      <div className={styles.container}>
        <header className={styles.header}>
          <p className={styles.eyebrow}>Backtest</p>
          <h1 className={styles.title}>回测结果</h1>
        </header>

        {/* ── run 基础信息 ── */}
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
            <span className={styles.label}>策略卡</span>
            <span className={styles.valueMono}>{data.strategy_card_id}</span>
          </div>
          <div className={styles.kv}>
            <span className={styles.label}>创建时间</span>
            <span className={styles.value}>{formatDateTime(data.created_at)}</span>
          </div>

          {/* queued */}
          {status === "queued" && (
            <div
              className={`${styles.message} ${styles.messageNeutral}`}
              data-testid="backtest-run-state-queued"
            >
              <p>回测已提交，正在等待执行。</p>
            </div>
          )}

          {/* running */}
          {status === "running" && (
            <div
              className={`${styles.message} ${styles.messageNeutral}`}
              data-testid="backtest-run-state-running"
            >
              <p>回测执行中，请稍候…</p>
            </div>
          )}

          {/* failed */}
          {status === "failed" && (
            <div
              className={`${styles.message} ${styles.messageError}`}
              data-testid="backtest-run-state-failed"
            >
              <p>回测失败，请检查策略参数或稍后重试。</p>
              {data.error_code && (
                <p className={styles.valueMono}>code: {data.error_code}</p>
              )}
              {data.error_message && <p>{data.error_message}</p>}
            </div>
          )}

          {/* cancelled */}
          {status === "cancelled" && (
            <div
              className={`${styles.message} ${styles.messageWarn}`}
              data-testid="backtest-run-state-cancelled"
            >
              <p>回测已取消。</p>
              {data.error_message && <p>{data.error_message}</p>}
            </div>
          )}

          {/* succeeded — result_url 缺失（异常态） */}
          {status === "succeeded" && !hasResultUrl && (
            <div
              className={`${styles.message} ${styles.messageWarn}`}
              data-testid="backtest-run-state-no-result-url"
            >
              <p>回测已完成，但结果暂不可用。请稍后刷新或重新发起回测。</p>
            </div>
          )}

          {/* unknown status */}
          {!["queued", "running", "failed", "cancelled", "succeeded"].includes(
            String(status),
          ) && (
            <div className={`${styles.message} ${styles.messageWarn}`}>
              <p>未知状态：{String(status)}</p>
            </div>
          )}

          <div className={styles.inlineActions}>
            <Link
              className={styles.linkButton}
              href={`/strategy-cards/${data.strategy_card_id}/edit`}
            >
              返回策略编辑
            </Link>
          </div>
        </section>

        {/* ── succeeded：结果区块 ── */}
        {status === "succeeded" && hasResultUrl && (
          <>
            {/* 结果加载中 */}
            {resultQuery.isPending && (
              <section
                className={`${styles.panel} ${styles.resultSkeleton}`}
                data-testid="backtest-result-loading"
              >
                <p>正在加载结果…</p>
              </section>
            )}

            {/* 结果加载失败 */}
            {resultQuery.error && (() => {
              const err =
                resultQuery.error instanceof ApiClientError
                  ? resultQuery.error
                  : new ApiClientError({
                      status: 500,
                      fallbackMessage: "加载回测结果失败。",
                    });
              return (
                <section
                  className={`${styles.panel} ${styles.statePanel}`}
                  data-testid="backtest-result-error"
                >
                  <div
                    className={`${styles.message} ${styles.messageError}`}
                    role="alert"
                  >
                    <p>
                      {err.code === "BACKTEST_RESULT_NOT_READY"
                        ? "回测结果尚未就绪，请稍后刷新。"
                        : err.code === "BACKTEST_RESULT_UNAVAILABLE"
                          ? "回测执行失败，无法提供结果。"
                          : err.message}
                    </p>
                  </div>
                  <div className={styles.inlineActions}>
                    <button
                      className={styles.linkButton}
                      type="button"
                      onClick={() => resultQuery.refetch()}
                    >
                      重试
                    </button>
                  </div>
                </section>
              );
            })()}

            {/* 结果成功 */}
            {resultQuery.data && (
              <section className={styles.panel} data-testid="backtest-result-panel">
                <BacktestResultSection result={resultQuery.data} />
              </section>
            )}

            {/* 结论区块：仅在结果成功后显示 */}
            {resultQuery.data && (
              <section className={styles.panel} data-testid="conclusion-section">
                <ConclusionForm
                  resultId={resultQuery.data.result_id}
                  strategyCardId={data.strategy_card_id}
                />
              </section>
            )}
          </>
        )}
      </div>
    </main>
  );
}
