import { expect, test } from "@playwright/test";

test("home page exposes create strategy entry and navigates to new strategy page", async ({
  page,
}) => {
  await page.goto("/");

  await expect(page.getByTestId("home-page")).toBeVisible();
  await expect(page.getByRole("heading", { name: "从策略假设到可验证闭环" })).toBeVisible();
  await expect(page.getByText("MVP 核心闭环")).toBeVisible();
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
