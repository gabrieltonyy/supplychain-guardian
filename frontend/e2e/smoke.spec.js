const { test, expect } = require("@playwright/test");

const pages = [
  ["/", "Operations Center"],
  ["/suppliers", "Suppliers"],
  ["/workflows", "Incident Management"],
  ["/analytics", "Risk Intelligence"],
  ["/risks", "Risk Workbench"],
  ["/settings", "Platform Settings"],
];

for (const [path, heading] of pages) {
  test(`${heading} loads`, async ({ page }) => {
    await page.goto(path);
    await expect(page.getByRole("heading", { name: heading })).toBeVisible();
  });
}
