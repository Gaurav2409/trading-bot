import { expect, test } from "@playwright/test";

test("operator can read state and disable entries for one broker", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: /Operator Console/ })).toBeVisible();

  // Zerodha and Alpaca are distinct partitions.
  await expect(page.getByTestId("account-kite-1")).toBeVisible();
  await expect(page.getByTestId("account-alpaca-1")).toBeVisible();

  // A manual holding is visible and affects the portfolio.
  await expect(page.getByTestId("external-TESTCO")).toContainText("manual_matched_broker");

  // A blocked momentum candidate explains why.
  await expect(page.getByTestId("candidate-ILLIQ")).toContainText("circuit_locked");

  // Disabling entries for Zerodha does not change Alpaca.
  await page.getByRole("button", { name: "Disable new entries" }).first().click();
  await expect(page.getByTestId("kill-kite-1")).toHaveText("entry_disabled");
  await expect(page.getByTestId("kill-alpaca-1")).toHaveText("active");

  // No family or FX execution control is present.
  await expect(page.getByText(/family/i)).toHaveCount(0);
  await expect(page.getByText(/forex/i)).toHaveCount(0);
});
