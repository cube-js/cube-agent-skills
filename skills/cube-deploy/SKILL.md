---
name: cube-deploy
description: Manage Cube deployments and their lifecycle — create deployments, deploy a project, check build status, manage environments and environment variables, connect a GitHub repo, and tail logs — using the Cube CLI. Use whenever someone wants to ship, configure or debug a deployment rather than change the model inside one. Triggers on "deploy this", "did the build pass", "why did the build fail", "set an environment variable", "create a deployment", "connect our repo", "show me the logs", "what regions are available", "the deployment is down". To change model files use cube-build-model; for users and access use cube-admin.
license: Apache-2.0
compatibility: Needs the Cube MCP server (bundled in the Cube plugin, or the Cube connector) or the Cube CLI, and network access to Cube Cloud.
---

# Deploy and operate Cube deployments

Infrastructure, not modeling. Environment variables and deployment settings
affect everyone using that deployment.

## Choose the path

Cube MCP tools are written `cube:<tool>` below: the `cube` server this plugin
bundles. Through the Cube connector, the same tools carry the connector's name.

Deployment lifecycle is CLI-only: creating deployments, setting environment
variables, connecting a repo, build status and logs. The Cube MCP tools can
help diagnose — `cube:listDeployments`, `cube:getDeploymentEnv` (read-only, secrets
redacted), and `cube:getPreAggregationStatus` for a rollup that will not build —
but cannot change a deployment. Without a terminal and the Cube CLI, say so,
and point the user to the deployment's settings in the Cube console.

## Preflight

```bash
command -v cube >/dev/null || echo "Cube CLI not installed: curl -fsSL https://raw.githubusercontent.com/cube-js/cube/master/install-cli.sh | sh"
cube whoami || echo "Not authenticated. Interactive: cube login. Headless: set CUBE_API_URL + CUBE_API_KEY."
cube context list
```

## Deployments

```bash
cube deployments list
cube deployments get <deployment>
cube deployments create --name <name> --region <region>   # see `cube regions`
cube deployments update <deployment> --name <name>
cube deployments versions <deployment>                      # Cube versions available
cube deployments update <deployment> --release-channel-version <version>
cube deployments delete <deployment>
cube regions
```

By default, creation scaffolds the project and runs the first build. There is
no separate bootstrap step. Changing the Cube version rebuilds the deployment
— say so before doing it.

## Shipping code

Two different routes, and they do not mix:

```bash
cube deploy <deployment> -m "<message>"      # upload the local project directory and build
cube github connect <deployment> <repo> --installation <installation>  # link git and build
```

```bash
cube github status
cube github installations
cube github repos <installation>
cube github branches <owner/repo> --installation <installation>
```

`cube deploy` pushes what is on your disk — to your active dev-mode branch if
you have one, otherwise the deploy branch — and deletes remote files that are
not in the local directory unless you pass `--keep-missing`. `cube github
connect` makes git the source of truth. Using both against one deployment means whichever ran last
wins, silently. Ask which the project uses before deploying.

## Build status — the answer to "did it work"

```bash
cube deployments build-status <deployment>
cube deployments build-status <deployment> --branch <branch>
cube deployments build-status <deployment> --branch <branch> --wait   # blocks; non-zero exit on failure
cube validate <deployment> --branch <branch>                          # model compile errors only
```

Defaults to the active dev-mode branch if there is one, otherwise the deploy
branch. A deploy command returning successfully means the upload succeeded,
not that the build did — always follow with build status before telling
anyone it shipped.

## Environments and variables

```bash
cube environments list <deployment>
cube environments tokens <deployment> <environment>
cube environments create-token <deployment> <environment> --security-context '<json>'
cube environments create-token <deployment> <environment> --security-context '{}' --meta-sync

cube variables list <deployment>
cube variables set <deployment> KEY=VALUE
```

`create-token` prints a credential. Never echo it back, write it to the
repository, or include it in a transcript; report only that it was created,
for which environment, and when it expires.

`cube variables set` upserts. Run `variables list` first and say whether the
key already exists. Secret values are masked, so never claim to know or print
the old value — a silently overwritten database URL is hard to trace later.

Never print secret values into a transcript. Confirm that a variable was set
without echoing what it was set to.

## Logs

```bash
cube logs <deployment>
cube logs <deployment> --pod <pod>
cube logs <deployment> -c <container>     # defaults to the Cube API container
```

Tail logs when a build passed but behaviour is wrong. For a build that
failed, `build-status` carries the error and is the better starting point.

## Debugging a failed deployment

1. `cube deployments build-status <deployment> --branch <branch>` — read the error verbatim.
2. If it is a model error, hand to `cube-build-model`; that is where the fix
   goes.
3. If the build passed but queries fail, check `cube variables list` for
   connection settings, then `cube logs`.
4. If the deployment has never built, `deploymentUrl` will be null and
   nothing downstream will work — that is the thing to fix first.

Report the error text rather than a paraphrase. Cube's build errors name the
file and the member, and the paraphrase always loses that.

## When something fails

| Symptom | Cause |
| --- | --- |
| Deploy succeeds, build fails | Normal and expected — they are separate steps |
| 403 on a deployment | Account lacks access to that deployment |
| Variable set but unchanged behaviour | Needs a rebuild to take effect |
| Logs empty | Wrong pod or container, or the deployment is not running |
