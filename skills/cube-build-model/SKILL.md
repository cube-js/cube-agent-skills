---
name: cube-build-model
description: Author and change a Cube semantic model — add or edit cubes, views, measures, dimensions, joins and pre-aggregations in YAML — using the Cube CLI, on a dev-mode branch, then commit and build. Use whenever someone wants to add a metric, define a measure or dimension, create a cube or view, join two cubes, fix a model error, rename a field, or expose a field to business users. Triggers on "add a metric", "define revenue", "create a view for", "expose this field", "join orders to customers", "fix the model", "add a pre-aggregation". Read the model first with cube-explore-model. To run a query against the result use cube-run-query; to deploy or check build status use cube-deploy.
license: Apache-2.0
---

# Build and change a Cube semantic model

Writes state. The API rejects file writes on any branch that is not a
dev-mode branch, so the branch dance below is not optional ceremony — skip it
and every write fails.

## Preflight

```bash
command -v cube >/dev/null || echo "Cube CLI not installed: curl -fsSL https://raw.githubusercontent.com/cube-js/cube/master/install-cli.sh | sh"
cube whoami || echo "Not authenticated. Interactive: cube login. Headless: set CUBE_API_URL + CUBE_API_KEY."
cube context list   # confirm the tenant before writing anything
```

## Read before you write

Never author against an assumed model. Pull the current state first:

```bash
cube data-model list <deployment> --content --json > /tmp/model.json
```

Match the project's existing conventions — file layout, naming, whether
measures live on cubes or views, how joins are declared. A correct cube that
looks nothing like its neighbours is a bad contribution.

## The dev-mode workflow

```bash
# 1. See what branches exist
cube data-model branches <deployment>

# 2. Enter dev mode on a base branch. This forks a personal `dev-…` branch
#    and PRINTS ITS NAME. Capture it — writes must target it.
cube data-model dev-mode <deployment> main

# 3. Write files to that branch
cube data-model put <deployment> model/cubes/orders.yml --file ./orders.yml --branch <dev-branch>
cube data-model put <deployment> model/views/revenue.yml --content - --branch <dev-branch>   # stdin

# 4. Commit
cube data-model commit <deployment> -m "Add revenue view" --branch <dev-branch>

# 5. Confirm it actually builds
cube deployments build-status <deployment> --branch <dev-branch>

# 6. Leave dev mode when done
cube data-model exit-dev-mode <deployment>
```

`--branch` defaults to your active dev-mode branch, so once step 2 has run you
can usually omit it. Pass it explicitly anyway when you are working across
more than one deployment in a session — the default is per-user, not
per-command, and it is easy to write to the wrong place.

Other file operations, same branch rules:

```bash
cube data-model rename <deployment> model/cubes/old.yml model/cubes/new.yml --branch <dev-branch>
cube data-model delete <deployment> model/cubes/dead.yml --branch <dev-branch>
```

## Validation is a build, not a linter

There is no offline validate command. The way to know a change is good is to
commit it and read the build:

```bash
cube deployments build-status <deployment> --branch <dev-branch>
```

A failing build is the real error message. Report it verbatim rather than
guessing at the cause — Cube's model errors name the file and the member.

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
cube deploy <deployment>   # uploads the local directory to the deployment and builds
```

This is a different workflow from the dev-mode one above — it replaces the
project from local files. Do not mix the two in one task without saying so.

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
| `not logged in` | Rerun the preflight; do not retry the write |
| Build fails after commit | Real model error — read the build status output and fix the named file |
| Change builds but is not queryable | Not exposed in a view; check `cube meta` |
