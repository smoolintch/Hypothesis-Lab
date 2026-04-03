import { expect, test } from "@playwright/test";

async function mockEmptyStrategyCardList(page: import("@playwright/test").Page) {
  await page.route("**/api/strategy-cards?page=1&page_size=20", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          items: [],
          pagination: {
            page: 1,
            page_size: 20,
            total: 0,
          },
        },
        error: null,
      }),
    });
  });
}

async function fillStrategyCardForm(page: import("@playwright/test").Page, name: string) {
  await page.goto("/strategy-cards/new");
  await expect(page.getByRole("heading", { name: "新建策略假设卡" })).toBeVisible();

  await page.getByTestId("strategy-card-name-input").fill(name);
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

test("home page shows empty strategy list state when there are no cards", async ({ page }) => {
  await mockEmptyStrategyCardList(page);
  await page.goto("/");

  await expect(page.getByTestId("home-page")).toBeVisible();
  await expect(page.getByTestId("strategy-card-list-empty")).toBeVisible();
  await expect(
    page.getByText("还没有任何策略卡。先创建第一张策略卡，开始一次完整验证闭环。"),
  ).toBeVisible();
});

test("home page shows populated strategy list and allows navigating to edit page", async ({ page }) => {
  const strategyName = "Homepage Strategy List E2E";

  await fillStrategyCardForm(page, strategyName);
  await page.getByTestId("strategy-card-submit-button").click();
  await page.waitForURL(/\/strategy-cards\/[^/]+\/edit$/);

  const strategyId = page.url().match(/\/strategy-cards\/([^/]+)\/edit$/)?.[1];
  expect(strategyId).toBeTruthy();

  await page.goto("/");

  await expect(page.getByTestId("strategy-card-list")).toBeVisible();
  await expect(page.getByTestId("strategy-card-list-items")).toBeVisible();

  const strategyListItem = page.getByTestId(`strategy-card-list-item-${strategyId}`);
  await expect(strategyListItem).toBeVisible();
  await expect(strategyListItem.getByText(strategyName)).toBeVisible();
  await expect(strategyListItem.getByText(/^BTCUSDT · 1D · 最近更新 /)).toBeVisible();

  const editLink = page.getByTestId(`strategy-card-edit-link-${strategyId}`);
  await expect(editLink).toBeVisible();
  await editLink.click();

  await page.waitForURL(new RegExp(`/strategy-cards/${strategyId}/edit$`));
  await expect(page.getByRole("heading", { name: "编辑策略假设卡" })).toBeVisible();
  await expect(page.getByTestId("strategy-card-form")).toBeVisible();
  await expect(page.getByTestId("strategy-card-name-input")).toHaveValue(strategyName);
});

test("home page duplicates a strategy card, shows handoff feedback, and allows saving the duplicated card", async ({ page }) => {
  const strategyName = "Homepage Strategy Duplicate E2E";
  const duplicatedStrategyName = `${strategyName} Copy`;

  await fillStrategyCardForm(page, strategyName);
  await page.getByTestId("strategy-card-submit-button").click();
  await page.waitForURL(/\/strategy-cards\/[^/]+\/edit$/);

  const sourceStrategyId = page.url().match(/\/strategy-cards\/([^/]+)\/edit$/)?.[1];
  expect(sourceStrategyId).toBeTruthy();

  await page.goto("/");

  const sourceStrategyListItem = page.getByTestId(`strategy-card-list-item-${sourceStrategyId}`);
  await expect(sourceStrategyListItem).toBeVisible();

  const duplicateButton = sourceStrategyListItem.getByTestId(
    `strategy-card-duplicate-button-${sourceStrategyId}`,
  );
  await duplicateButton.click();
  await expect(duplicateButton).toContainText("复制中");

  await page.waitForURL(/\/strategy-cards\/[^/]+\/edit\?/);

  const duplicatedStrategyId = page.url().match(/\/strategy-cards\/([^/?]+)\/edit/)?.[1];
  expect(duplicatedStrategyId).toBeTruthy();
  expect(duplicatedStrategyId).not.toBe(sourceStrategyId);

  await expect(page.getByRole("heading", { name: "编辑策略假设卡" })).toBeVisible();
  await expect(page.getByTestId("strategy-card-form")).toBeVisible();
  await expect(page.getByTestId("strategy-card-name-input")).toHaveValue(strategyName);
  await expect(page.getByTestId("strategy-card-symbol-select")).toHaveValue("BTCUSDT");
  await expect(page.getByTestId("strategy-card-timeframe-select")).toHaveValue("1D");

  const handoff = page.getByTestId("strategy-card-duplicate-handoff");
  await expect(handoff).toBeVisible();
  await expect(handoff).toContainText("复制成功，已进入新策略卡");
  await expect(handoff).toContainText(`来源：${strategyName}`);
  await expect(handoff).toContainText(`来源策略卡 ID：${sourceStrategyId}`);

  await page.getByTestId("strategy-card-name-input").fill(duplicatedStrategyName);
  await page.getByTestId("strategy-card-submit-button").click();

  await expect(page.getByTestId("strategy-card-save-success")).toBeVisible();
  await expect(page.getByTestId("strategy-card-save-success")).toContainText("策略已保存");
  await expect(page.getByTestId("strategy-card-name-input")).toHaveValue(duplicatedStrategyName);
  await expect(handoff).toBeVisible();
});
