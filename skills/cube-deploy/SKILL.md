---
name: cube-deploy
description: Manage Cube deployments and their lifecycle — create deployments, deploy a project, check build status, manage environments and environment variables, connect a GitHub repo, and tail logs — using the Cube CLI. Use whenever someone wants to ship, configure or debug a deployment rather than change the model inside one. Triggers on "deploy this", "did the build pass", "why did the build fail", "set an environment variable", "create a deployment", "connect our repo", "show me the logs", "what regions are available", "the deployment is down". To change model files use cube-build-model; for users and access use cube-admin.
license: Apache-2.0
---

# Deploy and operate Cube deployments

Infrastructure, not modeling. Environment variables and deployment settings
affect everyone using that deployment.

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
cube deployments create --bootstrap ...     # scaffolds and builds a serving deployment
cube deployments update <deployment> ...
cube deployments delete <deployment>
cube regions list
```

`--bootstrap` does the whole first-run path — scaffold, then build. Without
it you get an empty deployment you then have to populate.

## Shipping code

Two different routes, and they do not mix:

```bash
cube deploy                                  # upload the local project directory and build
cube github connect ...                      # link a repo; Cube builds from git
```

```bash
cube github status
cube github installations
cube github repos
cube github branches
```

`cube deploy` pushes what is on your disk. `cube github connect` makes git the
source of truth. Using both against one deployment means whichever ran last
wins, silently. Ask which the project uses before deploying.

## Build status — the answer to "did it work"

```bash
cube deployments build-status <deployment>
cube deployments build-status <deployment> --branch <branch>
```

Defaults to the active dev-mode branch if there is one, otherwise the deploy
branch. A deploy command returning successfully means the upload succeeded,
not that the build did — always follow with build status before telling
anyone it shipped.

## Environments and variables

```bash
cube environments list <deployment>
cube environments tokens <deployment>
cube environments create-token <deployment> --meta-sync

cube variables list <deployment>
cube variables set <deployment> KEY=VALUE
```

`cube variables set` upserts. Read the current value first and say what it
was — a silently overwritten database URL is hard to trace back later.

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

1. `cube deployments build-status --branch <branch>` — read the error verbatim.
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
