import { expect, test } from "@playwright/test";

async function mockStrategyCardDetail(page: import("@playwright/test").Page, strategyCardId: string) {
  await page.route(`**/api/strategy-cards/${strategyCardId}`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          id: strategyCardId,
          name: "History Strategy",
          symbol: "BTCUSDT",
          timeframe: "1D",
          backtest_range: {
            start_at: "2024-01-01T00:00:00Z",
            end_at: "2024-01-10T00:00:00Z",
          },
          initial_capital: 10000,
          fee_rate: 0.001,
          rule_set: {
            entry: {
              template_key: "ma_cross",
              params: {
                ma_type: "sma",
                fast_period: 5,
                slow_period: 20,
                cross_direction: "golden",
              },
            },
            exit: {
              template_key: "ma_cross",
              params: {
                ma_type: "sma",
                fast_period: 5,
                slow_period: 20,
                cross_direction: "dead",
              },
            },
            stop_loss: null,
            take_profit: null,
          },
          status: "ready",
          updated_at: "2024-01-11T12:00:00Z",
          latest_backtest_run_id: "run-history-1",
          created_at: "2024-01-01T00:00:00Z",
        },
        error: null,
      }),
    });
  });
}

async function mockHistoryLoading(page: import("@playwright/test").Page, strategyCardId: string) {
  await mockStrategyCardDetail(page, strategyCardId);
  await page.route(`**/api/backtests/strategy-cards/${strategyCardId}/history`, async () => {
    await new Promise((resolve) => setTimeout(resolve, 1_000));
  });
}

async function mockHistoryEmpty(page: import("@playwright/test").Page, strategyCardId: string) {
  await mockStrategyCardDetail(page, strategyCardId);
  await page.route(`**/api/backtests/strategy-cards/${strategyCardId}/history`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          strategy_card_id: strategyCardId,
          items: [],
        },
        error: null,
      }),
    });
  });
}

async function mockHistoryError(page: import("@playwright/test").Page, strategyCardId: string) {
  await mockStrategyCardDetail(page, strategyCardId);
  await page.route(`**/api/backtests/strategy-cards/${strategyCardId}/history`, async (route) => {
    await route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({
        success: false,
        data: null,
        error: {
          code: "INTERNAL_SERVER_ERROR",
          message: "加载历史回测记录失败。",
          details: {},
          request_id: "req-history-error",
        },
      }),
    });
  });
}

async function mockHistoryData(page: import("@playwright/test").Page, strategyCardId: string) {
  await mockStrategyCardDetail(page, strategyCardId);
  await page.route(`**/api/backtests/strategy-cards/${strategyCardId}/history`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          strategy_card_id: strategyCardId,
          items: [
            {
              run_id: "run-history-1",
              status: "succeeded",
              result_url: "/api/backtests/run-history-1/result",
              started_at: "2024-01-11T09:00:00Z",
              finished_at: "2024-01-11T09:10:00Z",
              created_at: "2024-01-11T08:58:00Z",
            },
          ],
        },
        error: null,
      }),
    });
  });
}

test("edit page shows history loading state", async ({ page }) => {
  const strategyCardId = "strategy-history-loading";
  await mockHistoryLoading(page, strategyCardId);

  await page.goto(`/strategy-cards/${strategyCardId}/edit`);

  await expect(page.getByTestId("strategy-backtest-history-loading")).toBeVisible();
  await expect(page.getByText("正在加载该策略的历史回测记录…")).toBeVisible();
});

test("edit page shows empty history state", async ({ page }) => {
  const strategyCardId = "strategy-history-empty";
  await mockHistoryEmpty(page, strategyCardId);

  await page.goto(`/strategy-cards/${strategyCardId}/edit`);

  await expect(page.getByTestId("strategy-backtest-history-empty")).toBeVisible();
  await expect(
    page.getByText("当前策略还没有历史回测记录。你可以先保存当前策略，再发起第一次回测。"),
  ).toBeVisible();
});

test("edit page shows history error state without breaking editor", async ({ page }) => {
  const strategyCardId = "strategy-history-error";
  await mockHistoryError(page, strategyCardId);

  await page.goto(`/strategy-cards/${strategyCardId}/edit`);

  await expect(page.getByTestId("strategy-backtest-history-error")).toBeVisible();
  await expect(page.getByText("加载历史回测记录失败。")).toBeVisible();
  await expect(page.getByTestId("strategy-card-form")).toBeVisible();
});

test("edit page shows history data and result link", async ({ page }) => {
  const strategyCardId = "strategy-history-data";
  await mockHistoryData(page, strategyCardId);

  await page.goto(`/strategy-cards/${strategyCardId}/edit`);

  await expect(page.getByTestId("strategy-backtest-history")).toBeVisible();
  await expect(page.getByTestId("strategy-backtest-history-items")).toBeVisible();

  const item = page.getByTestId("strategy-backtest-history-item-run-history-1");
  await expect(item).toBeVisible();
  await expect(item.getByText(/run_id: run-history-1/)).toBeVisible();
  await expect(item.getByText(/状态：已完成/)).toBeVisible();
  await expect(item.getByText(/创建于/)).toBeVisible();
  await expect(item.getByText(/开始于/)).toBeVisible();
  await expect(item.getByText(/结束于/)).toBeVisible();

  const resultLink = page.getByTestId("strategy-backtest-history-result-link-run-history-1");
  await expect(resultLink).toBeVisible();
  await expect(resultLink).toHaveAttribute("href", "/backtests/run-history-1");
});
