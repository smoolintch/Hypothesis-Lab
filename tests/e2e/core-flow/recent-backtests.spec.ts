import { expect, test } from "@playwright/test";

async function mockRecentBacktestsLoading(page: import("@playwright/test").Page) {
  await page.route("**/api/backtests/recent", async () => {
    await new Promise((resolve) => setTimeout(resolve, 1_000));
  });
}

async function mockRecentBacktestsEmpty(page: import("@playwright/test").Page) {
  await page.route("**/api/backtests/recent", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          items: [],
        },
        error: null,
      }),
    });
  });
}

async function mockRecentBacktestsError(page: import("@playwright/test").Page) {
  await page.route("**/api/backtests/recent", async (route) => {
    await route.fulfill({
      status: 500,
      contentType: "application/json",
      body: JSON.stringify({
        success: false,
        data: null,
        error: {
          code: "INTERNAL_SERVER_ERROR",
          message: "Internal server error.",
          details: {},
          request_id: "req-recent-backtests-error",
        },
      }),
    });
  });
}

async function mockRecentBacktestsData(page: import("@playwright/test").Page) {
  await page.route("**/api/backtests/recent", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: {
          items: [
            {
              run_id: "run-recent-1",
              strategy_card_id: "strategy-1",
              strategy_card_name: "Recent Backtest Strategy",
              status: "succeeded",
              result_url: "/api/backtests/run-recent-1/result",
              started_at: "2024-01-02T08:00:00Z",
              finished_at: "2024-01-02T08:05:00Z",
              created_at: "2024-01-02T07:59:00Z",
            },
          ],
        },
        error: null,
      }),
    });
  });
}

test("home page shows recent backtests loading state", async ({ page }) => {
  await mockRecentBacktestsLoading(page);
  await page.goto("/");

  await expect(page.getByTestId("recent-backtests-loading")).toBeVisible();
  await expect(page.getByText("正在加载最近实验记录…")).toBeVisible();
});

test("home page shows recent backtests empty state", async ({ page }) => {
  await mockRecentBacktestsEmpty(page);
  await page.goto("/");

  await expect(page.getByTestId("recent-backtests-empty")).toBeVisible();
  await expect(
    page.getByText("最近还没有新的实验记录。先发起一次回测，形成第一条实验记录。"),
  ).toBeVisible();
});

test("home page shows recent backtests error state without breaking strategy list", async ({ page }) => {
  await mockRecentBacktestsError(page);
  await page.goto("/");

  await expect(page.getByTestId("recent-backtests-error")).toBeVisible();
  await expect(page.getByText("最近实验记录加载失败，请刷新后重试。")).toBeVisible();
  await expect(
    page
      .getByTestId("strategy-card-list")
      .or(page.getByTestId("strategy-card-list-empty"))
      .or(page.getByTestId("strategy-card-list-loading"))
      .or(page.getByTestId("strategy-card-list-error")),
  ).toBeVisible();
});

test("home page shows recent backtests data and links to result page", async ({ page }) => {
  await mockRecentBacktestsData(page);
  await page.goto("/");

  await expect(page.getByTestId("recent-backtests")).toBeVisible();
  await expect(page.getByTestId("recent-backtests-items")).toBeVisible();

  const item = page.getByTestId("recent-backtest-item-run-recent-1");
  await expect(item).toBeVisible();
  await expect(item.getByText("Recent Backtest Strategy")).toBeVisible();
  await expect(item.getByText(/状态：已完成/)).toBeVisible();
  await expect(item.getByText(/创建于/)).toBeVisible();
  await expect(item.getByText(/开始于/)).toBeVisible();
  await expect(item.getByText(/结束于/)).toBeVisible();

  const resultLink = page.getByTestId("recent-backtest-result-link-run-recent-1");
  await expect(resultLink).toBeVisible();
  await expect(resultLink).toHaveAttribute("href", "/backtests/run-recent-1/result");
});
