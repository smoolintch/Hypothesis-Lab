import { expect, test } from "@playwright/test";

/**
 * Conclusion save E2E tests.
 *
 * Coverage:
 * 1. Success path: submit conclusion → conclusion-saved view visible
 * 2. Duplicate path: reload same run → submit again → 409 error message visible
 */

// ─── helpers ─────────────────────────────────────────────────────────────────

/**
 * Fill strategy form with in-range dates so the backtest succeeds synchronously.
 * Uses BTCUSDT/1D + SMA(2,3) ma_cross — minimal periods for 5-candle fixture.
 */
async function fillStrategyFormInRange(page: import("@playwright/test").Page) {
  await page.getByTestId("strategy-card-name-input").fill("Conclusion Save E2E Test");
  await page.getByTestId("strategy-card-symbol-select").selectOption("BTCUSDT");
  await page.getByTestId("strategy-card-timeframe-select").selectOption("1D");
  await page.getByTestId("strategy-card-start-at-input").fill("2024-01-01T00:00");
  await page.getByTestId("strategy-card-end-at-input").fill("2024-01-06T00:00");
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

/**
 * Create a new strategy card, run a backtest, and return the run_id.
 * Waits until the result panel and conclusion form are both visible.
 */
async function createSucceededRunAndWaitForConclusion(
  page: import("@playwright/test").Page,
): Promise<string> {
  await page.goto("/strategy-cards/new");
  await expect(page.getByRole("heading", { name: "新建策略假设卡" })).toBeVisible();
  await fillStrategyFormInRange(page);

  await page.getByTestId("strategy-card-submit-button").click();
  await page.waitForURL(/\/strategy-cards\/[^/]+\/edit$/);

  await page.getByTestId("strategy-card-start-backtest-button").click();
  await page.waitForURL(/\/backtests\/[^/]+$/);

  const runId = page.url().split("/").at(-1) ?? "";
  expect(runId).toBeTruthy();

  // Wait for real result to load (backend is synchronous, but React Query is async)
  await expect(page.getByTestId("backtest-result-panel")).toBeVisible({ timeout: 15000 });
  await expect(page.getByTestId("conclusion-section")).toBeVisible();
  await expect(page.getByTestId("conclusion-form")).toBeVisible();

  return runId;
}

// ─── tests ───────────────────────────────────────────────────────────────────

test("submit conclusion shows saved view on success", async ({ page }) => {
  await createSucceededRunAndWaitForConclusion(page);

  // Fill optional fields to verify they appear in the saved summary
  await page.getByTestId("conclusion-is-worth-researching").check();
  await page.getByTestId("conclusion-next-action").selectOption("refine_rules");
  await page.getByTestId("conclusion-notes").fill("首次测试备注");

  await page.getByTestId("conclusion-submit-button").click();

  // Saved view must appear
  await expect(page.getByTestId("conclusion-saved")).toBeVisible();
  await expect(page.getByText("结论已保存。")).toBeVisible();

  // Summary should reflect submitted values
  await expect(page.getByTestId("conclusion-saved")).toContainText("优化规则");
  await expect(page.getByTestId("conclusion-saved")).toContainText("首次测试备注");

  // Form must no longer be visible
  await expect(page.getByTestId("conclusion-form")).not.toBeVisible();
});

test("submitting conclusion twice shows CONCLUSION_ALREADY_EXISTS error", async ({ page }) => {
  const runId = await createSucceededRunAndWaitForConclusion(page);

  // First save
  await page.getByTestId("conclusion-submit-button").click();
  await expect(page.getByTestId("conclusion-saved")).toBeVisible();

  // Reload the same result page — React state resets, form reappears
  await page.goto(`/backtests/${runId}`);
  await expect(page.getByTestId("backtest-result-panel")).toBeVisible({ timeout: 15000 });
  await expect(page.getByTestId("conclusion-form")).toBeVisible();

  // Second save → backend returns 409
  await page.getByTestId("conclusion-submit-button").click();
  await expect(page.getByTestId("conclusion-save-error")).toBeVisible();
  await expect(
    page.getByText("该回测结果已有结论，无法重复保存。"),
  ).toBeVisible();
});
