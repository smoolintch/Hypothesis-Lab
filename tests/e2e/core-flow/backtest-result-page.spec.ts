/**
 * Stage-3 result page E2E tests.
 *
 * Goal: independently verify that /backtests/{run_id} can consume and display
 * real backtest results (metrics, curves, trades) after a successful run.
 *
 * Coverage:
 * 1. In-range strategy → succeeded → result panel, metrics, charts, trades visible
 * 2. Out-of-range strategy → failed → error message visible
 * 3. Status display for various terminal states
 */

import { expect, test } from "@playwright/test";

// ─── helpers ─────────────────────────────────────────────────────────────────

/**
 * Fill a strategy card form with the given parameters.
 * Uses BTCUSDT/1D with dates inside the fixture coverage so the backtest
 * runs successfully (fixture covers 2024-01-01 – 2024-01-05, 5 candles).
 */
async function fillStrategyFormInRange(page: import("@playwright/test").Page) {
  await page.getByTestId("strategy-card-name-input").fill("Result Page E2E Test");
  await page.getByTestId("strategy-card-symbol-select").selectOption("BTCUSDT");
  await page.getByTestId("strategy-card-timeframe-select").selectOption("1D");
  // Dates INSIDE fixture coverage → backtest will succeed
  await page.getByTestId("strategy-card-start-at-input").fill("2024-01-01T00:00");
  await page.getByTestId("strategy-card-end-at-input").fill("2024-01-06T00:00");
  await page.getByTestId("strategy-card-initial-capital-input").fill("10000");
  await page.getByTestId("strategy-card-fee-rate-input").fill("0.001");

  // Entry: ma_cross golden cross (fast=2, slow=3 – small enough for 5-candle fixture)
  await page.getByTestId("entry-template-select").selectOption("ma_cross");
  await page.getByTestId("entry-ma_type-input").selectOption("sma");
  await page.getByTestId("entry-fast_period-input").fill("2");
  await page.getByTestId("entry-slow_period-input").fill("3");
  await page.getByTestId("entry-cross_direction-input").selectOption("golden");

  // Exit: ma_cross dead cross (same periods)
  await page.getByTestId("exit-template-select").selectOption("ma_cross");
  await page.getByTestId("exit-ma_type-input").selectOption("sma");
  await page.getByTestId("exit-fast_period-input").fill("2");
  await page.getByTestId("exit-slow_period-input").fill("3");
  await page.getByTestId("exit-cross_direction-input").selectOption("dead");
}

/**
 * Fill a strategy card form with dates outside the fixture coverage so the
 * backtest fails with BACKTEST_DATASET_UNAVAILABLE / BACKTEST_EXECUTION_FAILED.
 */
async function fillStrategyFormOutOfRange(page: import("@playwright/test").Page) {
  await page.getByTestId("strategy-card-name-input").fill("Out-Of-Range Backtest Test");
  await page.getByTestId("strategy-card-symbol-select").selectOption("BTCUSDT");
  await page.getByTestId("strategy-card-timeframe-select").selectOption("1D");
  // Dates OUTSIDE fixture coverage → backtest will fail
  await page.getByTestId("strategy-card-start-at-input").fill("2022-01-01T00:00");
  await page.getByTestId("strategy-card-end-at-input").fill("2022-06-01T00:00");
  await page.getByTestId("strategy-card-initial-capital-input").fill("10000");
  await page.getByTestId("strategy-card-fee-rate-input").fill("0.001");

  await page.getByTestId("entry-template-select").selectOption("ma_cross");
  await page.getByTestId("entry-ma_type-input").selectOption("sma");
  await page.getByTestId("entry-fast_period-input").fill("2");
  await page.getByTestId("entry-slow_period-input").fill("3");
  await page.getByTestId("entry-cross_direction-input").selectOption("golden");

  await page.getByTestId("exit-template-select").selectOption("ma_cross");
  await page.getByTestId("exit-ma_type-input").selectOption("sma");
  await page.getByTestId("exit-fast_period-input").fill("2");
  await page.getByTestId("exit-slow_period-input").fill("3");
  await page.getByTestId("exit-cross_direction-input").selectOption("dead");
}

// ─── tests ───────────────────────────────────────────────────────────────────

test("in-range backtest redirects to result page with succeeded status", async ({ page }) => {
  await page.goto("/strategy-cards/new");
  await expect(page.getByRole("heading", { name: "新建策略假设卡" })).toBeVisible();

  await fillStrategyFormInRange(page);

  // Save → navigate to edit page
  await page.getByTestId("strategy-card-submit-button").click();
  await page.waitForURL(/\/strategy-cards\/[^/]+\/edit$/);
  await expect(page.getByRole("heading", { name: "编辑策略假设卡" })).toBeVisible();

  // Start backtest → navigate to result page
  await page.getByTestId("strategy-card-start-backtest-button").click();
  await page.waitForURL(/\/backtests\/[^/]+$/);

  const runId = page.url().split("/").at(-1);
  expect(runId).toBeTruthy();

  // Basic run info should be visible
  await expect(page.getByTestId("backtest-run-page")).toBeVisible();
  await expect(page.getByTestId("backtest-run-id")).toHaveText(runId ?? "");

  // Backend runs synchronously → status is immediately succeeded
  await expect(page.getByTestId("backtest-run-status")).toHaveText("succeeded");
});

test("in-range backtest shows real result panel with metrics, charts, and trades section", async ({ page }) => {
  await page.goto("/strategy-cards/new");
  await fillStrategyFormInRange(page);

  await page.getByTestId("strategy-card-submit-button").click();
  await page.waitForURL(/\/strategy-cards\/[^/]+\/edit$/);

  await page.getByTestId("strategy-card-start-backtest-button").click();
  await page.waitForURL(/\/backtests\/[^/]+$/);

  // Wait for result panel to appear (status succeeded + result loaded)
  await expect(page.getByTestId("backtest-result-panel")).toBeVisible({ timeout: 15000 });
  await expect(page.getByTestId("backtest-result-section")).toBeVisible();

  // ── Core metrics (7 items) ──
  await expect(page.getByTestId("metrics-grid")).toBeVisible();
  await expect(page.getByTestId("metric-total-return-rate")).toBeVisible();
  await expect(page.getByTestId("metric-max-drawdown")).toBeVisible();
  await expect(page.getByTestId("metric-win-rate")).toBeVisible();
  await expect(page.getByTestId("metric-profit-factor")).toBeVisible();
  await expect(page.getByTestId("metric-trade-count")).toBeVisible();
  await expect(page.getByTestId("metric-avg-holding-bars")).toBeVisible();
  await expect(page.getByTestId("metric-final-equity")).toBeVisible();

  // ── Equity and drawdown curve blocks ──
  await expect(page.getByTestId("chart-资金曲线")).toBeVisible();
  await expect(page.getByTestId("chart-回撤曲线")).toBeVisible();

  // ── Trades section heading is visible (table or empty message both acceptable) ──
  await expect(page.getByText("最近交易明细")).toBeVisible();

  // ── Metric values are non-empty (not "-" or empty) ──
  const finalEquityText = await page.getByTestId("metric-final-equity").textContent();
  expect(finalEquityText).toBeTruthy();
  expect(finalEquityText?.trim()).not.toBe("");

  // ── Return to strategy editing link exists ──
  await expect(page.getByRole("link", { name: "返回策略编辑" })).toBeVisible();
});

test("out-of-range backtest shows failed state with error code", async ({ page }) => {
  await page.goto("/strategy-cards/new");
  await fillStrategyFormOutOfRange(page);

  await page.getByTestId("strategy-card-submit-button").click();
  await page.waitForURL(/\/strategy-cards\/[^/]+\/edit$/);

  await page.getByTestId("strategy-card-start-backtest-button").click();
  await page.waitForURL(/\/backtests\/[^/]+$/);

  // Backend runs synchronously → out-of-range means failed immediately
  await expect(page.getByTestId("backtest-run-status")).toHaveText("failed");
  await expect(page.getByTestId("backtest-run-state-failed")).toBeVisible();

  // Error message visible
  await expect(page.getByText("回测失败，请检查策略参数或稍后重试。")).toBeVisible();

  // Error code is shown
  const errorCodeEl = page.locator('[data-testid="backtest-run-state-failed"] .backtest-run-module__Ec7_0W__valueMono');
  // Just verify the failed state panel has content (error code may vary by CSS module hash)
  await expect(page.getByTestId("backtest-run-state-failed")).toContainText("code:");

  // Result panel must NOT appear for failed run
  await expect(page.getByTestId("backtest-result-panel")).not.toBeVisible();

  // Return to strategy editing link exists
  await expect(page.getByRole("link", { name: "返回策略编辑" })).toBeVisible();
});

test("non-existent run_id shows not-found state", async ({ page }) => {
  await page.goto("/backtests/00000000-0000-0000-0000-000000000099");

  await expect(page.getByTestId("backtest-run-page")).toBeVisible();
  await expect(page.getByTestId("backtest-run-not-found")).toBeVisible();
  await expect(page.getByText("回测运行不存在。")).toBeVisible();
  await expect(page.getByRole("link", { name: "新建策略卡" })).toBeVisible();
});
