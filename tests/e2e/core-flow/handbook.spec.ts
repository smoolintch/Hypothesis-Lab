import { expect, test } from "@playwright/test";

/**
 * Handbook entry E2E tests.
 *
 * Coverage:
 * 1. Success path: save conclusion with add_to_handbook → handbook section visible
 *    → submit → handbook-entry-saved visible
 * 2. Duplicate path: pre-seed entry via API → submit from UI → 409 error visible
 */

const apiPort = process.env.PLAYWRIGHT_API_PORT ?? "8000";
const apiBaseUrl = `http://127.0.0.1:${apiPort}/api`;

// ─── helpers ─────────────────────────────────────────────────────────────────

/**
 * Fill strategy form with in-range dates so the backtest succeeds synchronously.
 * Uses BTCUSDT/1D + SMA(2,3) ma_cross — minimal periods for 5-candle fixture.
 */
async function fillStrategyFormInRange(page: import("@playwright/test").Page) {
  await page.getByTestId("strategy-card-name-input").fill("Handbook E2E Test");
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
 * Create a new strategy card, run a backtest, and wait until the conclusion form
 * is visible. The caller is responsible for filling conclusion form fields.
 */
async function createSucceededRunAndWaitForConclusion(
  page: import("@playwright/test").Page,
) {
  await page.goto("/strategy-cards/new");
  await expect(page.getByRole("heading", { name: "新建策略假设卡" })).toBeVisible();
  await fillStrategyFormInRange(page);

  await page.getByTestId("strategy-card-submit-button").click();
  await page.waitForURL(/\/strategy-cards\/[^/]+\/edit$/);

  await page.getByTestId("strategy-card-start-backtest-button").click();
  await page.waitForURL(/\/backtests\/[^/]+$/);

  // Wait for real result to load (backend is synchronous, React Query is async)
  await expect(page.getByTestId("backtest-result-panel")).toBeVisible({ timeout: 15000 });
  await expect(page.getByTestId("conclusion-section")).toBeVisible();
  await expect(page.getByTestId("conclusion-form")).toBeVisible();
}

// ─── tests ───────────────────────────────────────────────────────────────────

test("submit handbook shows saved view on success", async ({ page }) => {
  await createSucceededRunAndWaitForConclusion(page);

  // Select add_to_handbook as next action
  await page.getByTestId("conclusion-next-action").selectOption("add_to_handbook");

  // Submit conclusion
  await page.getByTestId("conclusion-submit-button").click();
  await expect(page.getByTestId("conclusion-saved")).toBeVisible();

  // Handbook section must appear because next_action = add_to_handbook
  await expect(page.getByTestId("handbook-section")).toBeVisible();

  // Submit handbook entry (no memo)
  await page.getByTestId("handbook-submit-button").click();

  // Success state
  await expect(page.getByTestId("handbook-entry-saved")).toBeVisible();
  await expect(page.getByText("已加入交易手册。")).toBeVisible();

  // Link to handbook page must be present
  await expect(page.getByRole("link", { name: "前往交易手册" })).toBeVisible();

  // Form must no longer be visible
  await expect(page.getByTestId("handbook-submit-button")).not.toBeVisible();
});

test("adding same conclusion to handbook twice shows HANDBOOK_ENTRY_ALREADY_EXISTS error", async ({
  page,
}) => {
  await createSucceededRunAndWaitForConclusion(page);

  // Select add_to_handbook as next action
  await page.getByTestId("conclusion-next-action").selectOption("add_to_handbook");

  // Capture the conclusion creation response to obtain conclusion_id
  const conclusionRespPromise = page.waitForResponse(
    (resp) =>
      /\/conclusions$/.test(resp.url()) && resp.request().method() === "POST",
  );
  await page.getByTestId("conclusion-submit-button").click();
  const conclusionResp = await conclusionRespPromise;
  const conclusionJson = await conclusionResp.json();
  const conclusionId: string = conclusionJson.data.id;
  expect(conclusionId).toBeTruthy();

  // Wait for handbook section to appear
  await expect(page.getByTestId("conclusion-saved")).toBeVisible();
  await expect(page.getByTestId("handbook-section")).toBeVisible();

  // Pre-seed the handbook entry directly via API so the next UI click will conflict
  const seedResp = await page.request.post(`${apiBaseUrl}/handbook`, {
    data: JSON.stringify({ conclusion_id: conclusionId }),
    headers: { "Content-Type": "application/json" },
  });
  expect(seedResp.status()).toBe(201);

  // Submit from UI → backend returns 409
  await page.getByTestId("handbook-submit-button").click();

  await expect(page.getByTestId("handbook-save-error")).toBeVisible();
  await expect(
    page.getByText("该结论已加入交易手册，无法重复加入。"),
  ).toBeVisible();
});
