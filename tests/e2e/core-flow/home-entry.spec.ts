import { expect, test } from "@playwright/test";

test("home page exposes strategy list area and navigates to new strategy page", async ({
  page,
}) => {
  await page.goto("/");

  await expect(page.getByTestId("home-page")).toBeVisible();
  await expect(page.getByRole("heading", { name: "从策略假设到可验证闭环" })).toBeVisible();
  await expect(page.getByText("假设 → 回测 → 结果 → 结论 → 沉淀")).toBeVisible();
  await expect(
    page
      .getByTestId("strategy-card-list")
      .or(page.getByTestId("strategy-card-list-empty"))
      .or(page.getByTestId("strategy-card-list-loading"))
      .or(page.getByTestId("strategy-card-list-error")),
  ).toBeVisible();
  await expect(
    page
      .getByTestId("recent-backtests")
      .or(page.getByTestId("recent-backtests-empty"))
      .or(page.getByTestId("recent-backtests-loading"))
      .or(page.getByTestId("recent-backtests-error")),
  ).toBeVisible();
  await expect(page.getByTestId("home-create-strategy-link")).toBeVisible();
  await expect(page.getByTestId("home-create-strategy-link")).toHaveText("新建策略假设");

  await page.getByTestId("home-create-strategy-link").click();

  await page.waitForURL(/\/strategy-cards\/new$/);
  await expect(page.getByRole("heading", { name: "新建策略假设卡" })).toBeVisible();
  await expect(page.getByTestId("strategy-card-form")).toBeVisible();
  await expect(page.getByTestId("strategy-card-submit-button")).toContainText(
    "保存并进入编辑页",
  );
});
