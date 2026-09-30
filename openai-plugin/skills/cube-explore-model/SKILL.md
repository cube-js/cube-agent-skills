---
name: cube-explore-model
description: Explore a Cube deployment's semantic model to find queryable views, measures, dimensions, joins, and source files. Use when someone asks what data or metrics are available, where a metric is defined, or what a model change could affect.
license: Apache-2.0
---

# Explore the Cube model

Use the Cube MCP server. Start with `listDeployments` when the deployment is unknown. If several deployments are available and the request does not identify one, ask which to use.

- For what can be queried now, use `searchDataModel`. It returns the compiled model, including the members exposed through views. Search by the user's business term; do not invent a member name.
- For where a definition is authored, use `listDataModelFiles` and `readDataModelFile`. Cite the exact file path and member. A field in a source file may not be exposed in a queryable view.
- For work on a branch, pass the same `branchName` to every relevant tool and use `getBranchDiff` to inspect its changes.

For an impact question, check direct model references in the relevant files and whether the member is exposed in a view. The MCP server cannot enumerate every saved report or workbook, so do not call a rename safe for all downstream content on that evidence alone. State what was checked and what remains unknown.

Return the exact model members or file paths found. If nothing matches, say so rather than guessing a name or claiming that the model has no such data.
