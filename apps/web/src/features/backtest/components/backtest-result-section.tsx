"use client";

import type { BacktestResultResponse, CurvePoint, TradeRecord } from "../types";
import styles from "../backtest-run.module.css";

// ─── helpers ─────────────────────────────────────────────────────────────────

function fmtPct(v: number) {
  return `${(v * 100).toFixed(2)}%`;
}

function fmtNum(v: number, digits = 2) {
  return v.toFixed(digits);
}

function fmtCurrency(v: number) {
  return v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function fmtDateTime(v: string) {
  const d = new Date(v);
  if (Number.isNaN(d.valueOf())) return "-";
  return d.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function fmtDate(v: string) {
  const d = new Date(v);
  if (Number.isNaN(d.valueOf())) return "-";
  return d.toLocaleDateString("zh-CN", { year: "numeric", month: "2-digit", day: "2-digit" });
}

// ─── SVG line chart ───────────────────────────────────────────────────────────

const CHART_W = 600;
const CHART_H = 120;
const PAD = { top: 8, right: 8, bottom: 24, left: 48 };

function curveToPolyline(points: CurvePoint[]) {
  if (points.length === 0) return "";
  const values = points.map((p) => p.value);
  const minV = Math.min(...values);
  const maxV = Math.max(...values);
  const rangeV = maxV - minV || 1;
  const w = CHART_W - PAD.left - PAD.right;
  const h = CHART_H - PAD.top - PAD.bottom;

  return points
    .map((p, i) => {
      const x = PAD.left + (i / Math.max(points.length - 1, 1)) * w;
      const y = PAD.top + h - ((p.value - minV) / rangeV) * h;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}

function axisLabels(points: CurvePoint[], isDrawdown = false) {
  if (points.length === 0) return null;
  const values = points.map((p) => p.value);
  const minV = Math.min(...values);
  const maxV = Math.max(...values);

  const fmt = isDrawdown
    ? (v: number) => `-${(Math.abs(v) * 100).toFixed(1)}%`
    : (v: number) => (v >= 1000 ? `${(v / 1000).toFixed(1)}k` : v.toFixed(0));

  const h = CHART_H - PAD.top - PAD.bottom;

  // first and last date labels
  const firstDate = fmtDate(points[0].ts);
  const lastDate = fmtDate(points[points.length - 1].ts);

  return (
    <>
      {/* y-axis: max */}
      <text
        x={PAD.left - 4}
        y={PAD.top + 4}
        textAnchor="end"
        fontSize={9}
        fill="var(--muted)"
      >
        {fmt(maxV)}
      </text>
      {/* y-axis: min */}
      <text
        x={PAD.left - 4}
        y={PAD.top + h + 2}
        textAnchor="end"
        fontSize={9}
        fill="var(--muted)"
      >
        {fmt(minV)}
      </text>
      {/* x-axis: first date */}
      <text
        x={PAD.left}
        y={CHART_H - 4}
        textAnchor="start"
        fontSize={9}
        fill="var(--muted)"
      >
        {firstDate}
      </text>
      {/* x-axis: last date */}
      <text
        x={CHART_W - PAD.right}
        y={CHART_H - 4}
        textAnchor="end"
        fontSize={9}
        fill="var(--muted)"
      >
        {lastDate}
      </text>
    </>
  );
}

interface MiniChartProps {
  points: CurvePoint[];
  color: string;
  label: string;
  isDrawdown?: boolean;
}

function MiniChart({ points, color, label, isDrawdown = false }: MiniChartProps) {
  const polyline = curveToPolyline(points);
  return (
    <div className={styles.chartBlock} data-testid={`chart-${label}`}>
      <p className={styles.chartLabel}>{label}</p>
      {points.length < 2 ? (
        <p className={styles.chartEmpty}>数据点不足，无法绘制曲线。</p>
      ) : (
        <svg
          viewBox={`0 0 ${CHART_W} ${CHART_H}`}
          preserveAspectRatio="none"
          className={styles.chartSvg}
          aria-label={label}
        >
          {/* grid line */}
          <line
            x1={PAD.left}
            y1={PAD.top}
            x2={CHART_W - PAD.right}
            y2={PAD.top}
            stroke="var(--border)"
            strokeWidth={0.5}
          />
          <line
            x1={PAD.left}
            y1={CHART_H - PAD.bottom}
            x2={CHART_W - PAD.right}
            y2={CHART_H - PAD.bottom}
            stroke="var(--border)"
            strokeWidth={0.5}
          />
          {/* curve */}
          <polyline
            points={polyline}
            fill="none"
            stroke={color}
            strokeWidth={1.5}
            vectorEffect="non-scaling-stroke"
          />
          {axisLabels(points, isDrawdown)}
        </svg>
      )}
    </div>
  );
}

// ─── trades table ─────────────────────────────────────────────────────────────

const TRADE_DISPLAY_LIMIT = 20;

interface TradesTableProps {
  trades: TradeRecord[];
}

function TradesTable({ trades }: TradesTableProps) {
  const displayed = trades.slice(-TRADE_DISPLAY_LIMIT).reverse();

  if (displayed.length === 0) {
    return <p className={styles.chartEmpty}>暂无交易记录。</p>;
  }

  return (
    <div className={styles.tableWrapper} data-testid="trades-table">
      <table className={styles.table}>
        <thead>
          <tr>
            <th>入场时间</th>
            <th>出场时间</th>
            <th>入场价</th>
            <th>出场价</th>
            <th>盈亏金额</th>
            <th>收益率</th>
            <th>出场原因</th>
          </tr>
        </thead>
        <tbody>
          {displayed.map((t) => {
            const isProfit = t.pnl_amount >= 0;
            return (
              <tr key={t.trade_id}>
                <td className={styles.tdMono}>{fmtDateTime(t.entry_at)}</td>
                <td className={styles.tdMono}>{fmtDateTime(t.exit_at)}</td>
                <td className={styles.tdNum}>{fmtCurrency(t.entry_price)}</td>
                <td className={styles.tdNum}>{fmtCurrency(t.exit_price)}</td>
                <td className={`${styles.tdNum} ${isProfit ? styles.profit : styles.loss}`}>
                  {isProfit ? "+" : ""}
                  {fmtCurrency(t.pnl_amount)}
                </td>
                <td className={`${styles.tdNum} ${isProfit ? styles.profit : styles.loss}`}>
                  {isProfit ? "+" : ""}
                  {fmtPct(t.pnl_rate)}
                </td>
                <td className={styles.tdReason}>{t.exit_reason}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
      {trades.length > TRADE_DISPLAY_LIMIT && (
        <p className={styles.tableNote}>
          共 {trades.length} 笔交易，仅显示最近 {TRADE_DISPLAY_LIMIT} 笔。
        </p>
      )}
    </div>
  );
}

// ─── metrics cards ────────────────────────────────────────────────────────────

interface MetricCardProps {
  label: string;
  value: string;
  highlight?: "positive" | "negative" | "neutral";
  testId?: string;
}

function MetricCard({ label, value, highlight = "neutral", testId }: MetricCardProps) {
  return (
    <div className={`${styles.metricCard} ${styles[`metric_${highlight}`]}`} data-testid={testId}>
      <span className={styles.metricLabel}>{label}</span>
      <span className={styles.metricValue}>{value}</span>
    </div>
  );
}

// ─── main export ──────────────────────────────────────────────────────────────

interface BacktestResultSectionProps {
  result: BacktestResultResponse;
}

export function BacktestResultSection({ result }: BacktestResultSectionProps) {
  const m = result.summary_metrics;
  const totalReturnHighlight =
    m.total_return_rate > 0 ? "positive" : m.total_return_rate < 0 ? "negative" : "neutral";

  return (
    <div data-testid="backtest-result-section">
      {/* ── 核心指标卡片 ── */}
      <section className={styles.resultBlock}>
        <h2 className={styles.sectionTitle}>核心指标</h2>
        <div className={styles.metricsGrid} data-testid="metrics-grid">
          <MetricCard
            label="总收益率"
            value={fmtPct(m.total_return_rate)}
            highlight={totalReturnHighlight}
            testId="metric-total-return-rate"
          />
          <MetricCard
            label="最大回撤"
            value={`-${fmtPct(Math.abs(m.max_drawdown_rate))}`}
            highlight="negative"
            testId="metric-max-drawdown"
          />
          <MetricCard
            label="胜率"
            value={fmtPct(m.win_rate)}
            highlight={m.win_rate >= 0.5 ? "positive" : "neutral"}
            testId="metric-win-rate"
          />
          <MetricCard
            label="盈亏比"
            value={fmtNum(m.profit_factor)}
            highlight={m.profit_factor >= 1 ? "positive" : "negative"}
            testId="metric-profit-factor"
          />
          <MetricCard
            label="交易次数"
            value={String(m.trade_count)}
            testId="metric-trade-count"
          />
          <MetricCard
            label="平均持仓 K 线数"
            value={fmtNum(m.avg_holding_bars, 1)}
            testId="metric-avg-holding-bars"
          />
          <MetricCard
            label="期末权益"
            value={fmtCurrency(m.final_equity)}
            highlight={m.final_equity > 0 ? "positive" : "negative"}
            testId="metric-final-equity"
          />
        </div>
      </section>

      {/* ── 资金曲线与回撤曲线 ── */}
      <section className={styles.resultBlock}>
        <h2 className={styles.sectionTitle}>曲线</h2>
        <MiniChart
          points={result.equity_curve}
          color="var(--color-equity)"
          label="资金曲线"
        />
        <MiniChart
          points={result.drawdown_curve}
          color="var(--color-drawdown)"
          label="回撤曲线"
          isDrawdown
        />
      </section>

      {/* ── 交易明细 ── */}
      <section className={styles.resultBlock}>
        <h2 className={styles.sectionTitle}>
          最近交易明细
          {result.trades.length > 0 && (
            <span className={styles.sectionBadge}>共 {result.trades.length} 笔</span>
          )}
        </h2>
        <TradesTable trades={result.trades} />
      </section>

      {/* ── meta ── */}
      <p className={styles.resultMeta}>
        数据版本：{result.dataset_version}　·　结果生成于 {fmtDateTime(result.created_at)}
      </p>
    </div>
  );
}
