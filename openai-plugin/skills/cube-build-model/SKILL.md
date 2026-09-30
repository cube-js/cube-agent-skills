---
name: cube-build-model
description: Edit a Cube semantic model on a development branch and verify the result with Cube MCP tools. Use for requests to add or change a measure, dimension, view, cube, join, or pre-aggregation.
license: Apache-2.0
---

# Edit the Cube semantic model

Use the Cube MCP server. Identify the deployment and read the compiled model plus the relevant source files before editing. Preserve the project's naming and file conventions. If a requested business definition is ambiguous, ask before encoding it in SQL.

1. Start an isolated edit with `startDataModelEdit`; retain the returned `branchName` for every subsequent call. If the user named a branch, pass it explicitly when the tool supports it.
2. Read files with `listDataModelFiles` and `readDataModelFile`. `writeDataModelFile` replaces a whole file, so send the complete revised content. Resolve validation errors before proceeding.
3. Review the change with `getDataModelChanges` or `getBranchDiff`. Search and query the modified model with the same `branchName` to verify that the member is exposed and returns the intended result.
4. Report the development branch, diff, validation result, and query check. The published Cube plugin does not currently expose a commit or merge tool, so explain that the user must finish review and commit in Cube.

A successful compile does not establish that the metric is correct; report the actual query check. For a pre-aggregation, inspect `getPreAggregationStatus` before `buildPreAggregation`, which runs warehouse work.
