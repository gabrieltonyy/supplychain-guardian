const { test, expect } = require("@playwright/test");

test.describe("RFQ Decision Center", () => {
  test("loads seeded backend RFQs and supports search/filter", async ({ page }) => {
    await page.goto("/rfqs");

    await expect(page.getByRole("heading", { name: "RFQ Decision Center" })).toBeVisible();
    await expect(page.getByText("Backend RFQ records")).toBeVisible();
    await expect(page.getByText("EuroTech Components").first()).toBeVisible();

    await page.getByPlaceholder("Search supplier, RFQ, or workflow context").fill("EuroTech Components");
    await expect(page.getByText("EuroTech Components").first()).toBeVisible();

    await page.locator("select").selectOption("PENDING_APPROVAL");
    await expect(page.getByText("Pending Approval").first()).toBeVisible();
  });

  test("persists approve, review, and reject actions after reload", async ({ page }) => {
    await page.goto("/rfqs");
    await page.getByPlaceholder("Search supplier, RFQ, or workflow context").fill("RFQ-SEED-002");
    await page.getByRole("button", { name: "Approve RFQ" }).click();
    await expect(page.getByText("updated to Approved")).toBeVisible();
    await page.reload();
    await expect(page.getByText("Approved").first()).toBeVisible();

    await page.getByPlaceholder("Search supplier, RFQ, or workflow context").fill("RFQ-SEED-003");
    await page.getByRole("button", { name: "Request Review" }).click();
    await expect(page.getByText("updated to Review Requested")).toBeVisible();
    await page.reload();
    await expect(page.getByText("Review Requested").first()).toBeVisible();

    await page.getByPlaceholder("Search supplier, RFQ, or workflow context").fill("RFQ-SEED-004");
    await page.getByRole("button", { name: "Reject" }).click();
    await expect(page.getByText("updated to Rejected")).toBeVisible();
    await page.reload();
    await expect(page.getByText("Rejected").first()).toBeVisible();
  });
});
