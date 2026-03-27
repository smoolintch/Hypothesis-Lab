import { expect, test } from "@playwright/test";

async function fillStrategyCardForm(page: import("@playwright/test").Page) {
  await page.getByTestId("strategy-card-name-input").fill("Playwright Backtest Draft");
  await page.getByTestId("strategy-card-symbol-select").selectOption("ETHUSDT");
  await page.getByTestId("strategy-card-timeframe-select").selectOption("1D");
  await page.getByTestId("strategy-card-start-at-input").fill("2023-02-01T00:00");
  await page.getByTestId("strategy-card-end-at-input").fill("2024-02-01T00:00");
  await page.getByTestId("strategy-card-initial-capital-input").fill("15000");
  await page.getByTestId("strategy-card-fee-rate-input").fill("0.002");
  await page.getByTestId("entry-template-select").selectOption("price_breakout");
  await page.getByTestId("entry-lookback_bars-input").fill("33");
  await page.getByTestId("entry-breakout_side-input").selectOption("break_high");
  await page.getByTestId("exit-template-select").selectOption("streak_reversal");
  await page.getByTestId("exit-direction-input").selectOption("down");
  await page.getByTestId("exit-streak_count-input").fill("4");
  await page.getByTestId("stop_loss-template-select").selectOption("fixed_stop_loss");
  await page.getByTestId("stop_loss-stop_loss_rate-input").fill("0.06");
}

test("start backtest redirects to queued placeholder run page", async ({ page }) => {
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
  await expect(page.getByTestId("backtest-run-status")).toHaveText("queued");
  await expect(page.getByTestId("backtest-run-state-queued")).toBeVisible();
  await expect(page.getByText("回测已排队（queued）")).toBeVisible();
});

test("non-existent backtest run shows not-found state", async ({ page }) => {
  await page.goto("/backtests/00000000-0000-0000-0000-000000000099");

  await expect(page.getByTestId("backtest-run-page")).toBeVisible();
  await expect(page.getByTestId("backtest-run-not-found")).toBeVisible();
  await expect(page.getByText("回测运行不存在。")).toBeVisible();
  await expect(page.getByRole("link", { name: "新建策略卡" })).toBeVisible();
});
