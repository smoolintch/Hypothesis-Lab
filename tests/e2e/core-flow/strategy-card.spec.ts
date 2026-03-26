import { expect, test } from "@playwright/test";

async function fillStrategyCardForm(page: import("@playwright/test").Page) {
  await page.getByTestId("strategy-card-name-input").fill("Playwright Strategy Card");
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

test("StrategyCard create -> edit -> reload -> update roundtrip works", async ({
  page,
}) => {
  await page.goto("/strategy-cards/new");

  await expect(page.getByRole("heading", { name: "新建策略假设卡" })).toBeVisible();
  await fillStrategyCardForm(page);

  await page.getByTestId("strategy-card-submit-button").click();

  await page.waitForURL(/\/strategy-cards\/[^/]+\/edit$/);
  await expect(page.getByRole("heading", { name: "编辑策略假设卡" })).toBeVisible();
  await expect(page.getByTestId("strategy-card-meta")).toBeVisible();
  await expect(page.getByTestId("strategy-card-name-input")).toHaveValue(
    "Playwright Strategy Card",
  );
  await expect(page.getByTestId("strategy-card-symbol-select")).toHaveValue("ETHUSDT");
  await expect(page.getByTestId("strategy-card-timeframe-select")).toHaveValue("1D");
  await expect(page.getByTestId("entry-template-select")).toHaveValue("price_breakout");
  await expect(page.getByTestId("entry-lookback_bars-input")).toHaveValue("33");
  await expect(page.getByTestId("exit-template-select")).toHaveValue("streak_reversal");
  await expect(page.getByTestId("exit-streak_count-input")).toHaveValue("4");

  await page.getByTestId("strategy-card-name-input").fill(
    "Playwright Strategy Card Updated",
  );
  await page.getByTestId("strategy-card-fee-rate-input").fill("0.003");
  await page.getByTestId("entry-lookback_bars-input").fill("55");
  await page.getByTestId("strategy-card-submit-button").click();

  await expect(page.getByTestId("strategy-card-save-success")).toBeVisible();
  await expect(page.getByTestId("strategy-card-name-input")).toHaveValue(
    "Playwright Strategy Card Updated",
  );
  await expect(page.getByTestId("strategy-card-fee-rate-input")).toHaveValue("0.003");
  await expect(page.getByTestId("entry-lookback_bars-input")).toHaveValue("55");

  await page.reload();

  await expect(page.getByRole("heading", { name: "编辑策略假设卡" })).toBeVisible();
  await expect(page.getByTestId("strategy-card-name-input")).toHaveValue(
    "Playwright Strategy Card Updated",
  );
  await expect(page.getByTestId("strategy-card-fee-rate-input")).toHaveValue("0.003");
  await expect(page.getByTestId("entry-lookback_bars-input")).toHaveValue("55");
});

test("non-existent strategy card edit page shows not-found state", async ({ page }) => {
  await page.goto("/strategy-cards/00000000-0000-0000-0000-000000000999/edit");

  await expect(page.getByTestId("strategy-card-not-found-state")).toBeVisible();
  await expect(page.getByRole("heading", { name: "策略卡不存在" })).toBeVisible();
  await expect(page.getByRole("link", { name: "新建策略卡" })).toBeVisible();
});

test("invalid rule params surface field validation feedback before submit", async ({
  page,
}) => {
  await page.goto("/strategy-cards/new");

  await page.getByTestId("strategy-card-name-input").fill("Invalid Param Draft");
  await page.getByTestId("entry-template-select").selectOption("ma_cross");
  await page.getByTestId("entry-fast_period-input").fill("20");
  await page.getByTestId("entry-slow_period-input").fill("10");

  await page.getByTestId("strategy-card-submit-button").click();

  await expect(page.getByText("字段校验失败")).toBeVisible();
  await expect(page.getByText("请先修正表单中的错误，再重新保存。")).toBeVisible();
  await expect(page.getByText("慢线周期必须大于快线周期")).toBeVisible();
  await expect(page).toHaveURL(/\/strategy-cards\/new$/);
  await expect(page.getByTestId("strategy-card-submit-button")).toContainText(
    "保存并进入编辑页",
  );
});
