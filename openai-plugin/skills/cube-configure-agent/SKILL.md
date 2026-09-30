---
name: cube-configure-agent
description: Inspect or improve Cube's in-product agent rules, certified queries, and Agent Skills stored with the semantic model. Use when a Cube agent repeatedly answers a business question incorrectly or someone wants to teach it a repeatable workflow.
license: Apache-2.0
---

# Configure the Cube agent

This skill concerns Agent Skills **inside Cube**, stored under the deployment's `agents/` model files. They are separate from the skills bundled in this ChatGPT plugin.

Use the Cube MCP server. Identify the deployment with `listDeployments`, then inspect the relevant files under `agents/` with `listDataModelFiles` and `readDataModelFile`. Rules are always-on instructions, certified queries pin a trusted answer to a specific question, and Agent Skills are named multi-step workflows. Choose the smallest change that addresses the user's problem.

When diagnosing a bad answer, verify the underlying metric with `searchDataModel` and `runQuery` first. Check whether it is exposed in a view and whether existing rules conflict. Do not add a rule to conceal a model error. For edits, follow the isolated development-branch workflow in `cube-build-model`, review the diff, and test the question against the development branch with `chat`. A new chat is needed to compare before and after because each chat stays on the branch where it started.

The published plugin does not expose a commit or merge tool. Report the changed file, development branch, and observed test result, then explain that the user must finish review and commit in Cube. If the deployment does not support agent configuration through model files, explain the limitation rather than claiming the change took effect.
