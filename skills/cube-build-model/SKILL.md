---
name: cube-build-model
description: Author and change a Cube semantic model — add or edit cubes, views, measures, dimensions, joins and pre-aggregations in YAML — on a dev-mode branch through the Cube MCP tools or the Cube CLI, then commit and build. Use whenever someone wants to add a metric, define a measure or dimension, create a cube or view, join two cubes, fix a model error, rename a field, or expose a field to business users. Triggers on "add a metric", "define revenue", "create a view for", "expose this field", "join orders to customers", "fix the model", "add a pre-aggregation". Read the model first with cube-explore-model. To run a query against the result use cube-run-query; to deploy or check build status use cube-deploy.
license: Apache-2.0
compatibility: Needs the Cube MCP server (bundled in the Cube plugin, or the Cube connector) or the Cube CLI, and network access to Cube Cloud.
---

# Build and change a Cube semantic model

Writes state. The API rejects file writes on any branch that is not a
dev-mode branch, so the branch dance below is not optional ceremony — skip it
and every write fails.

## Choose the path

Cube MCP tools are written `cube:<tool>` below: the `cube` server this plugin
bundles. Through the Cube connector, the same tools carry the connector's name.

**If the Cube MCP tools are available** (this plugin's
`cube` server or the Cube connector), use them. The loop:

1. `cube:startDataModelEdit` — returns the dev `branchName`. Pass it to every call
   below and reuse it; calling this again starts a new edit session.
2. `cube:listDataModelFiles`, `cube:readDataModelFile` — read before you write.
3. `cube:writeDataModelFile` — whole-file replacement. It recompiles and returns
   `valid` and any `validationError`; fix and write again until it is valid.
4. `cube:getDataModelChanges` — review the diff.
5. `cube:searchDataModel` and `cube:runQuery` with the same `branchName` — confirm the
   new member is exposed and returns the right number.
6. `cube:commitDataModelChanges` — until this runs, nobody else can see the work.
   Name the branch it reports and offer `cube:switchUserBranch`.
7. `cube:mergeToDefaultBranch` — **only** when the user explicitly asks to
   publish. It makes the change live for everyone.

For a new pre-aggregation, check it with `cube:getPreAggregationStatus`, then
`cube:buildPreAggregation` for that one rollup, passing the dev `branchName`. A
build runs real queries against the warehouse.

Use the CLI path when the MCP tools are not connected, or to deploy a whole
local project with `cube deploy`. Reading first and the
[conventions](#conventions) apply to both paths.

## Preflight (CLI)

```bash
command -v cube >/dev/null || echo "Cube CLI not installed: curl -fsSL https://raw.githubusercontent.com/cube-js/cube/master/install-cli.sh | sh"
cube whoami || echo "Not authenticated. Interactive: cube login. Headless: set CUBE_API_URL + CUBE_API_KEY."
cube context list   # confirm the tenant before writing anything
```

## Read before you write

Never author against an assumed model. Pull the current state first — over
MCP with `cube:listDataModelFiles` and `cube:readDataModelFile`, or with the CLI:

```bash
cube data-model list <deployment> --content --json > /tmp/model.json
```

Match the project's existing conventions — file layout, naming, whether
measures live on cubes or views, how joins are declared. A correct cube that
looks nothing like its neighbours is a bad contribution.

## The dev-mode workflow

```bash
# 1. See what branches exist, and which one is the deploy branch
cube data-model branches <deployment>

# 2. Create a feature branch to work on
cube data-model create-branch <deployment> <feature-branch>

# 3. Enter dev mode on the feature branch. This forks a personal `dev-…`
#    branch and PRINTS ITS NAME. Capture it — writes must target it.
cube data-model dev-mode <deployment> <feature-branch>

# 4. Write files to the dev branch
cube data-model put <deployment> model/cubes/orders.yml --file ./orders.yml --branch <dev-branch>
cube data-model put <deployment> model/views/revenue.yml --content - --branch <dev-branch>   # stdin

# 5. Validate the uncommitted working copy; fix and repeat until it passes
cube validate <deployment> --dev-mode

# 6. Commit — this lands on <feature-branch>, not production
cube data-model commit <deployment> -m "Add revenue view" --branch <dev-branch>

# 7. Wait for the build; exits non-zero if it fails
cube deployments build-status <deployment> --branch <dev-branch> --wait

# 8. Leave dev mode when done
cube data-model exit-dev-mode <deployment>
```

**Never enter dev mode directly on the deploy branch.** `commit` pushes into
the branch dev mode was forked from, so a dev branch of the deploy branch
commits straight to production. Step 2 is what keeps the change reviewable.

Publishing is a separate step, and only when the user explicitly asks for it:

```bash
cube data-model merge-to-default <deployment> --branch <feature-branch> -m "Add revenue view"
```

It merges into the deploy branch — live for everyone — and deletes the
feature branch unless you pass `--keep-branch`.

`--branch` defaults to your active dev-mode branch, so once step 3 has run you
can usually omit it. Pass it explicitly anyway when you are working across
more than one deployment in a session — the default is per-user, not
per-command, and it is easy to write to the wrong place.

Other file operations, same branch rules:

```bash
cube data-model rename <deployment> model/cubes/old.yml model/cubes/new.yml --branch <dev-branch>
cube data-model delete <deployment> model/cubes/dead.yml --branch <dev-branch>
```

## Validate before you commit (CLI)

```bash
cube validate <deployment> --dev-mode            # your uncommitted working copy
cube validate <deployment> --branch <branch>     # any named branch
```

It compiles the model on that branch's own runtime and exits non-zero with the
errors listed per file. Report them verbatim rather than guessing at the cause
— Cube's model errors name the file and the member. After committing,
`cube deployments build-status --wait` is the final word on the build.

After a green build, confirm the change is actually queryable. A measure can
compile and still not be exposed in any view:

```bash
cube meta --selectors '[{"type":"cube","deploymentId":<id>,"environment":"<dev-branch>"}]'
```

Then hand off to `cube-run-query` to check the number is right. Compiling is
not the same as being correct, and a measure whose SQL is wrong builds
perfectly.

## Deploying a local project instead

When the user has the project on disk rather than wanting file-by-file edits:

```bash
cube deploy <deployment> -m "<message>"   # uploads the local directory and builds
```

This is a different workflow from the dev-mode one above — it replaces the
project from local files. It deploys to your active dev-mode branch if you
have one, otherwise the deploy branch, and **deletes remote files that are not
in the local directory** unless you pass `--keep-missing`. Say which branch it
will land on before running it, and do not mix the two workflows in one task
without saying so.

## Conventions

- Cubes are the physical layer; views are what users query. New business
  metrics usually belong on a view, or on a cube and then exposed via a view.
- Keep one cube per file, named after the cube.
- Quote the user's own definition back when you write a `sql` expression. If
  they said "revenue excludes refunds", that belongs in the SQL and in a
  `description`, not just in the chat.

## When something fails

| Symptom | Cause |
| --- | --- |
| Write rejected | Not on a dev-mode branch — run `cube data-model dev-mode` and use the branch it prints |
| `validate` fails | Real model error — fix the named file and validate again before committing |
| `not logged in` | Rerun the preflight; do not retry the write |
| Build fails after commit | Real model error — read the build status output and fix the named file |
| Change builds but is not queryable | Not exposed in a view; check `cube meta` |
