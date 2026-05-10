# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: rfqs.spec.js >> RFQ Decision Center >> persists approve, review, and reject actions after reload
- Location: e2e/rfqs.spec.js:18:3

# Error details

```
Test timeout of 30000ms exceeded.
```

```
Error: locator.click: Test timeout of 30000ms exceeded.
Call log:
  - waiting for getByRole('button', { name: 'Approve RFQ' })

```

# Page snapshot

```yaml
- generic [ref=e2]:
  - complementary [ref=e3]:
    - generic [ref=e4]:
      - generic [ref=e6]:
        - img [ref=e8]
        - generic [ref=e10]:
          - generic [ref=e11]: SupplyChain Guardian
          - generic [ref=e12]: AI Operations Center
      - navigation [ref=e13]:
        - link "OperationsLive risk overview" [ref=e14] [cursor=pointer]:
          - /url: /
          - img [ref=e15]
          - generic [ref=e17]: OperationsLive risk overview
        - link "InvestigateAsk AI or run analysis" [ref=e18] [cursor=pointer]:
          - /url: /demo/run
          - img [ref=e19]
          - generic [ref=e21]: InvestigateAsk AI or run analysis
        - link "IncidentsWorkflow investigations" [ref=e22] [cursor=pointer]:
          - /url: /workflows
          - img [ref=e23]
          - generic [ref=e25]: IncidentsWorkflow investigations
        - link "IntelligenceRisk trends and insights" [ref=e26] [cursor=pointer]:
          - /url: /analytics
          - img [ref=e27]
          - generic [ref=e29]: IntelligenceRisk trends and insights
        - link "RFQsQuotes and approvals" [ref=e30] [cursor=pointer]:
          - /url: /rfqs
          - img [ref=e31]
          - generic [ref=e38]: RFQsQuotes and approvals
        - link "SettingsRules and integrations" [ref=e39] [cursor=pointer]:
          - /url: /settings
          - img [ref=e40]
          - generic [ref=e43]: SettingsRules and integrations
      - generic [ref=e44]:
        - generic [ref=e45]:
          - generic [ref=e46]:
            - img [ref=e47]
            - text: Operational Mode
          - generic [ref=e51]: Monitoring supplier risk, RFQs, and compliance signals.
        - generic [ref=e52]:
          - generic [ref=e53]: AMD ROCm + vLLM
          - generic [ref=e54]: Agent reasoning badges appear where AI inference is used.
  - generic [ref=e55]:
    - banner [ref=e56]:
      - generic [ref=e57]:
        - generic [ref=e58]:
          - img [ref=e60]
          - generic [ref=e62]:
            - generic [ref=e63]: SupplyChain Guardian
            - generic [ref=e64]: RFQ Command Center
            - generic [ref=e65]: Review generated RFQs, approvals, and supplier quote actions.
        - link "Investigate" [ref=e66] [cursor=pointer]:
          - /url: /demo/run
          - img [ref=e67]
          - text: Investigate
    - main [ref=e69]:
      - generic [ref=e70]:
        - generic [ref=e71]:
          - generic [ref=e72]:
            - heading "RFQ Decision Center" [level=1] [ref=e73]
            - paragraph [ref=e74]: Compare alternate suppliers, review approval blockers, and persist sourcing decisions to the backend audit trail.
          - button "Refresh" [disabled] [ref=e75]:
            - img [ref=e76]
            - text: Refresh
        - generic [ref=e78]:
          - generic [ref=e80]:
            - generic [ref=e81]:
              - generic [ref=e82]: Pending Approval
              - generic [ref=e83]: "0"
              - generic [ref=e84]: Need procurement decision
            - img [ref=e86]
          - generic [ref=e90]:
            - generic [ref=e91]:
              - generic [ref=e92]: Approved
              - generic [ref=e93]: "0"
              - generic [ref=e94]: Persisted approval decisions
            - img [ref=e96]
          - generic [ref=e100]:
            - generic [ref=e101]:
              - generic [ref=e102]: Compliance Review
              - generic [ref=e103]: "0"
              - generic [ref=e104]: Review or compliance queue
            - img [ref=e106]
          - generic [ref=e110]:
            - generic [ref=e111]:
              - generic [ref=e112]: Total RFQs
              - generic [ref=e113]: "0"
              - generic [ref=e114]: Backend RFQ records
            - img [ref=e116]
        - generic [ref=e123]:
          - generic [ref=e124]:
            - heading "Find RFQs" [level=3] [ref=e125]
            - paragraph [ref=e126]: Search by supplier name, supplier code, RFQ ID, or workflow context.
          - generic [ref=e127]:
            - generic [ref=e128]:
              - img [ref=e129]
              - textbox "Search supplier, RFQ, or workflow context" [active] [ref=e132]: RFQ-SEED-002
            - generic [ref=e133]:
              - img [ref=e134]
              - combobox [ref=e136]:
                - option "All statuses" [selected]
                - option "Pending Approval"
                - option "Approved"
                - option "Review Requested"
                - option "Compliance Review"
                - option "Draft"
                - option "Rejected"
        - generic [ref=e137]:
          - generic [ref=e138]:
            - heading "Supplier RFQ Recommendations" [level=3] [ref=e139]
            - paragraph [ref=e140]: Compare price, lead time, risk, and review status before acting.
          - generic [ref=e142]:
            - img [ref=e143]
            - text: Loading RFQ recommendations
```

# Test source

```ts
  1  | const { test, expect } = require("@playwright/test");
  2  | 
  3  | test.describe("RFQ Decision Center", () => {
  4  |   test("loads seeded backend RFQs and supports search/filter", async ({ page }) => {
  5  |     await page.goto("/rfqs");
  6  | 
  7  |     await expect(page.getByRole("heading", { name: "RFQ Decision Center" })).toBeVisible();
  8  |     await expect(page.getByText("Backend RFQ records")).toBeVisible();
  9  |     await expect(page.getByText("EuroTech Components").first()).toBeVisible();
  10 | 
  11 |     await page.getByPlaceholder("Search supplier, RFQ, or workflow context").fill("EuroTech Components");
  12 |     await expect(page.getByText("EuroTech Components").first()).toBeVisible();
  13 | 
  14 |     await page.locator("select").selectOption("PENDING_APPROVAL");
  15 |     await expect(page.getByText("Pending Approval").first()).toBeVisible();
  16 |   });
  17 | 
  18 |   test("persists approve, review, and reject actions after reload", async ({ page }) => {
  19 |     await page.goto("/rfqs");
  20 |     await page.getByPlaceholder("Search supplier, RFQ, or workflow context").fill("RFQ-SEED-002");
> 21 |     await page.getByRole("button", { name: "Approve RFQ" }).click();
     |                                                             ^ Error: locator.click: Test timeout of 30000ms exceeded.
  22 |     await expect(page.getByText("updated to Approved")).toBeVisible();
  23 |     await page.reload();
  24 |     await expect(page.getByText("Approved").first()).toBeVisible();
  25 | 
  26 |     await page.getByPlaceholder("Search supplier, RFQ, or workflow context").fill("RFQ-SEED-003");
  27 |     await page.getByRole("button", { name: "Request Review" }).click();
  28 |     await expect(page.getByText("updated to Review Requested")).toBeVisible();
  29 |     await page.reload();
  30 |     await expect(page.getByText("Review Requested").first()).toBeVisible();
  31 | 
  32 |     await page.getByPlaceholder("Search supplier, RFQ, or workflow context").fill("RFQ-SEED-004");
  33 |     await page.getByRole("button", { name: "Reject" }).click();
  34 |     await expect(page.getByText("updated to Rejected")).toBeVisible();
  35 |     await page.reload();
  36 |     await expect(page.getByText("Rejected").first()).toBeVisible();
  37 |   });
  38 | });
  39 | 
```