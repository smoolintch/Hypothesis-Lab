import { expect, test } from "@playwright/test";

/**
 * 使用引擎支持的 ma_cross 策略 + BTCUSDT/4H fixture 覆盖范围内的日期，
 * 确保回测可同步执行至 succeeded。
 */
async function fillStrategyCardForm(page: import("@playwright/test").Page) {
  await page.getByTestId("strategy-card-name-input").fill("Playwright Backtest Real");
  await page.getByTestId("strategy-card-symbol-select").selectOption("BTCUSDT");
  await page.getByTestId("strategy-card-timeframe-select").selectOption("4H");
  await page.getByTestId("strategy-card-start-at-input").fill("2024-01-01T00:00");
  await page.getByTestId("strategy-card-end-at-input").fill("2024-01-02T00:00");
  await page.getByTestId("strategy-card-initial-capital-input").fill("10000");
  await page.getByTestId("strategy-card-fee-rate-input").fill("0.001");
  await page.getByTestId("entry-template-select").selectOption("ma_cross");
  await page.getByTestId("entry-fast_period-input").fill("3");
  await page.getByTestId("entry-slow_period-input").fill("5");
  await page.getByTestId("entry-cross_direction-input").selectOption("golden");
  await page.getByTestId("exit-template-select").selectOption("ma_cross");
  await page.getByTestId("exit-fast_period-input").fill("3");
  await page.getByTestId("exit-slow_period-input").fill("5");
  await page.getByTestId("exit-cross_direction-input").selectOption("dead");
}

test("start backtest runs real execution and redirects to succeeded result page", async ({ page }) => {
  await page.goto("/strategy-cards/new");

  await expect(page.getByRole("heading", { name: "新建策略假设卡" })).toBeVisible();
  await fillStrategyCardForm(page);

  await page.getByTestId("strategy-card-submit-button").click();
  await page.waitForURL(/\/strategy-cards\/[^/]+\/edit$/);

  await expect(page.getByRole("heading", { name: "编辑策略假设卡" })).toBeVisible();
  await expect(page.getByTestId("strategy-card-start-backtest-button")).toBeVisible();

  await page.getByTestId("strategy-card-start-backtest-button").click();
  await page.waitForURL(/\/backtests\/[^/]+$/);

  const runId = page.url().split("/").at(-1);
  expect(runId).toBeTruthy();

  await expect(page.getByTestId("backtest-run-page")).toBeVisible();
  await expect(page.getByTestId("backtest-run-id")).toHaveText(runId ?? "");
  await expect(page.getByTestId("backtest-run-status")).toHaveText("succeeded");
  await expect(page.getByTestId("backtest-result-panel")).toBeVisible();
});

test("non-existent backtest run shows not-found state", async ({ page }) => {
  await page.goto("/backtests/00000000-0000-0000-0000-000000000099");

  await expect(page.getByTestId("backtest-run-page")).toBeVisible();
  await expect(page.getByTestId("backtest-run-not-found")).toBeVisible();
  await expect(page.getByText("回测运行不存在。")).toBeVisible();
  await expect(page.getByRole("link", { name: "新建策略卡" })).toBeVisible();
});
