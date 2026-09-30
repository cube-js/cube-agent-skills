---
name: cube-build-content
description: Create or update Cube reports, workbooks, and dashboards using the Cube MCP server. Use when someone asks to save an analysis, make a chart or dashboard, or publish a workbook.
license: Apache-2.0
---

# Build Cube analytics content

Use the Cube MCP server. Verify the requested measure, grouping, filters, and date range with `searchDataModel` and `runQuery` before saving a query as a report. Ask about any business choice that would materially change the result.

For new content, call `createWorkbook` when the user needs a workbook, then `createReport` with the verified Cube SQL and appropriate `chartCategory`. Call `readWorkbook` before `updateDashboard`, and send the complete widget array when updating the dashboard draft. Call `publishDashboard` only when the user has asked to publish the dashboard; a saved draft and a published dashboard are different states. Return the report or workbook URL provided by Cube.

For existing content, use `readReport` and `updateReport` to keep its report ID and dashboard references. Do not recreate it merely to change the query or chart. If the user asks for folder organization, scheduled notifications, workbook duplication, or another operation absent from the plugin's MCP tools, explain that this plugin cannot perform it; do not suggest that it succeeded.
