---
name: cube-explore-model
description: Search and inspect a Cube semantic model — cubes, views, measures, dimensions, joins, and the files they live in — through the Cube MCP tools or the Cube CLI. Use whenever someone wants to know what data is available in Cube, where a metric is defined, which cube a field belongs to, how two cubes join, or what a change would affect. Triggers on "what can I query", "what measures do we have", "where is revenue defined", "show me the data model", "what's in this deployment", "which cube has customer email", and impact questions like "what breaks if I rename this". Read the model with this skill before changing it. To edit the model use cube-build-model; to run a query and get numbers back use cube-run-query; to browse workbooks, dashboards and reports use cube-explore-content.
license: Apache-2.0
compatibility: Needs the Cube MCP server (bundled in the Cube plugin, or the Cube connector) or the Cube CLI, and network access to Cube Cloud.
---

# Explore a Cube semantic model

Read-only. Nothing here changes state, so you never need a dev-mode branch —
which also means you can run any of it before you know what you're doing.

## Choose the path

Cube MCP tools are written `cube:<tool>` below: the `cube` server this plugin
bundles. Through the Cube connector, the same tools carry the connector's name.

**If the Cube MCP tools are available** (this plugin's
`cube` server or the Cube connector), use them — no install, no login step:

| Question | MCP tool |
| --- | --- |
| What can I query; which view has a field | `cube:searchDataModel` — the compiled model, searched by meaning. Omit `query` to list everything |
| Which files exist; what does one say | `cube:listDataModelFiles`, `cube:readDataModelFile` |
| What did a branch change | `cube:getBranchDiff` |
| Which deployments exist | `cube:listDeployments`, then pass `deploymentId` |

`cube:searchDataModel` plays the role of `cube meta` below: it answers availability
("is this exposed"), and the files answer authorship ("where is this
written"). That distinction, and the impact-analysis checklist, hold on both
paths.

Use the CLI path when the MCP tools are not connected, when you need every
file's content in one request for a text search, or for `file-hashes`.

## Preflight (CLI)

Run this once at the start. Stop and report if either check fails; do not
guess at credentials or invent a deployment id.

```bash
command -v cube >/dev/null || echo "Cube CLI not installed: curl -fsSL https://raw.githubusercontent.com/cube-js/cube/master/install-cli.sh | sh"
cube whoami || echo "Not authenticated. Interactive: cube login. Headless: set CUBE_API_URL + CUBE_API_KEY."
cube context list   # multi-tenant: confirm you are pointed at the right tenant
```

`cube context list` matters more than it looks. A user with staging and
production contexts will not mention which one they mean, and every command
below takes a deployment id that is only unique within a tenant.

## Pick the deployment

Every data-model command needs a deployment id.

```bash
cube deployments list            # table: ID, NAME, URL, STEP
cube deployments list --json     # when you need to filter programmatically
```

If exactly one deployment exists, use it. If several do and the user hasn't
said which, ask — do not assume the lowest id.

## Map the model

Start with the file tree. This is the cheapest way to see the shape of a
project before reading anything.

```bash
cube data-model list <deployment>
cube data-model list <deployment> --branch <branch>   # a specific branch
```

Cube projects conventionally separate cubes from views:

```
model/
  cubes/       one file per cube — the physical layer, joined to tables
  views/       one file per view — the curated layer users query
```

Views are what business users should be querying; cubes are the building
blocks underneath. When someone asks "what can I query", the answer is
usually the views, not every cube.

## Read a file

```bash
cube data-model get <deployment> model/cubes/orders.yml
cube data-model get <deployment> model/views/revenue.yml --branch <branch>
```

## Find where something is defined

The CLI has no server-side search. The primitive is to pull every file's
content in one request and search locally:

```bash
cube data-model list <deployment> --content --json > /tmp/model.json
```

Then search that JSON for the measure, dimension, or SQL fragment you're
after. One request, then as many searches as you like — do **not** loop
`cube data-model get` over every path, which is slower and noisier.

This is the right tool for:

- "where is `revenue` defined" → find the measure, report its file and cube
- "which cube has customer email" → search dimension names
- "what does `active_user` actually mean" → read the `sql` of the measure and
  quote it back rather than paraphrasing

## Ask the compiled model, not the files

The files are the source. The **compiled** model is what is actually
queryable — after extends, joins and view exposure are resolved. When the
question is "what can I query right now", ask the compiled model:

```bash
cube meta --selectors '[{"type":"cube","deploymentId":<id>,"environment":"production"}]'
```

- `type` is `cube` (the semantic layer) or `d3` (the analytics layer).
- `environment` is a branch name, or `production` for the deployed model.
  Omit it to get the default.

Use the files when the question is about authoring ("where is this written",
"what should I change"). Use `cube meta` when the question is about
availability ("is this exposed", "what fields does this view actually have").
A field can exist in a cube and still be absent from every view — the files
will not tell you that on their own, and `cube meta` will.

## Impact analysis before a change

When asked what a rename or deletion would break, do all three — the first
alone is not an answer:

1. **Direct references.** Search the `--content` dump for the field name
   across cubes and views: joins, `sql` expressions, view `includes`.
2. **View exposure.** Check `cube:searchDataModel` or `cube meta` for whether the
   field surfaces in a view. A field exposed in a view has downstream consumers you cannot see
   from the model alone.
3. **Saved content.** Reports and workbooks reference members by name. Hand
   off to `cube-explore-content` to check saved content before calling a
   rename safe.

Say plainly which of the three you checked. "No direct references in the
model files, but I did not check saved reports" is a useful answer; "safe to
rename" without that qualification is not.

## Branches

```bash
cube data-model branches <deployment>
cube data-model file-hashes <deployment> --branch <branch>
```

`file-hashes` returns server-side content hashes — the cheap way to see
whether a branch has diverged from the default without pulling every file.

## Conventions

- List commands print tables; add `--json` for machine-readable output. Get
  commands always print JSON.
- Reads default to the deployment's default branch. Pass `--branch` whenever
  the user is talking about work in progress.
- Report file paths and cube names exactly as they appear. `orders.yml` and
  `Orders` are different things and the user needs the one they can act on.

## When something fails

| Symptom | Cause |
| --- | --- |
| `not logged in` | No credentials resolved — rerun the preflight, don't retry the command |
| `session expired — run cube login` | Refresh token is dead; the user must re-authenticate |
| 403 on a deployment | The account lacks access to that deployment, not a bad id |
| Empty file list | Real, and usually means an unbuilt or newly created deployment — say so rather than retrying |

Never invent a cube, measure, or file path that you have not seen in output.
If the model does not contain what the user is asking about, say that — it is
a finding, and often the actual answer.
