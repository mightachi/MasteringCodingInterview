# How to Publish Confluence Pages

The Atlassian MCP available in this workspace **does not include a "create Confluence page" tool** (only read operations: get page, get children, search). Pages must be created **manually** in Confluence.

---

## Option A: DAS-5702 Architecture Page (Acceptance Criteria)

**File:** `DAS_5702_ARCHITECTURE_PAGE.md`  
**Purpose:** Standalone architecture document for [DAS-5702](https://borobudur.atlassian.net/browse/DAS-5702) acceptance criteria: HLD + components, daily/multi-daily workflow, input/output data contracts, guardrails, model/versioning, run history, monitoring/alerts. Uses VELA only as reference.

**Where to create:** Create a **new page** (e.g. under **4. Explorations** or as a child of the DAS-5702 ticket link). Suggested title: **"End-to-End Architecture for Dynamic Pricing (RL) – DAS-5702"** or **"MUSCA / RL Dynamic Pricing – Architecture"**.

**Steps:** Create page → paste content from `DAS_5702_ARCHITECTURE_PAGE.md` → add link to DAS-5702 in description → Publish. Share the Confluence link in DAS-5702 as the “architecture document” deliverable.

---

## Option B: RL Pipeline POC (Exploration) Page

**File:** `CONFLUENCE_PAGE.md`  
**Purpose:** Exploration summary (Jira link, objective, conclusion, HLD/LLD summary).  
**Where to create:** Under **4. Explorations** (parent ID 3908632601).

---

## Step 1: Open the parent page (4. Explorations)

1. Go to: **https://borobudur.atlassian.net/wiki/spaces/DSMLE/pages/3908632601/4.+Explorations**
2. Log in with your Atlassian account if prompted.

## Step 2: Create a new child page

1. On the **4. Explorations** page, click **Create** (or the **+** in the sidebar).
2. Choose **Page**.
3. Select the **parent**: ensure the page is created **under "4. Explorations"** (you can set parent when creating or in Page settings).
4. **Title:** e.g. **Generic RL Pipeline POC** or **[new] Generic RL Pipeline POC** (to mirror the [new] FalkorDB style).

## Step 3: Paste the content

1. Open **`CONFLUENCE_PAGE.md`** in this repo (`rl_pipeline_poc/CONFLUENCE_PAGE.md`).
2. Copy the full content.
3. In Confluence:
   - **Option A:** Paste into the editor. Confluence Cloud often converts markdown on paste.
   - **Option B:** Use **Insert** → **Markup** → **Markdown**, then paste and insert.
   - **Option C:** If needed, use **Insert** → **Table**, **Insert** → **Expand**, etc., and replicate the structure from the markdown (summary table first, then headings and sections).

## Step 4: Adjust and publish

1. Fix any formatting (tables, headings, links).
2. Add a label if your space uses them (e.g. `exploration`, `poc`, `rl`, `kubeflow`).
3. Click **Publish**.

## Reference page (same format)

For structure and tone, use the same style as:

- **https://borobudur.atlassian.net/wiki/spaces/DSMLE/pages/4663804126/new+FalkorDB**

That page has: summary table (Exploration Date, Jira Link, Objective, Conclusion), Overview, Task Description with a table, benchmark/sections, Conclusion, and references.
