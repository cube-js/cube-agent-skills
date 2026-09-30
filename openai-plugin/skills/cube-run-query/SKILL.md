---
name: cube-run-query
description: Query a Cube deployment's governed business metrics and explain the result. Use for requests for totals, breakdowns, trends, period comparisons, or checks of a new measure on a development branch.
license: Apache-2.0
---

# Query Cube data

Use the Cube MCP server. If the deployment is unknown, call `listDeployments`; ask the user to choose if several match. Find the relevant view and exact member names with `searchDataModel` before writing Cube SQL. Do not guess members or silently switch to a different measure.

For a specific result, call `runQuery` with a bounded Cube SQL query. For an open-ended investigation, `chat` may use Cube's own agent; give the user its Cube chat URL when returned. If the question concerns a development branch, pass the same `branchName` to model search and query. Follow `hasMore` and `offset` when additional rows are needed, without presenting a partial result as complete.

Report the answer with the deployment, measure, date range, filters, and useful grouping. Distinguish an empty result from a failed query. Never fill in a value the tools did not return. If a member is missing, search the model again or explain the limitation.
