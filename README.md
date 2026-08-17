# Cube agent skills

Official [Cube](https://cube.dev) skills for Claude Code, Cursor, OpenAI Codex,
GitHub Copilot, Gemini CLI, and other [Agent Skills](https://agentskills.io)
compatible agents.

Explore and build your semantic model, manage workbooks and dashboards, run
queries, administer access, and ship deployments — from the agent you already
work in. The skills drive the [Cube CLI](https://docs.cube.dev/reference/cli),
so anything you can do through Cube's public API, your agent can do too.

> Cube agent skills run in your coding agent and operate Cube through the CLI.
> They are not Agent Skills in Cube, which your data team authors in the
> semantic model and runs from Analytics Chat.

## Install

**Claude Code**

```
/plugin marketplace add cube-js/cube-agent-skills
/plugin install cube@cube
```

**Codex, Copilot, Gemini CLI, and other skills.sh-compatible agents**

```
npx skills add cube-js/cube-agent-skills
```

Cursor and Snowflake Cortex Code are coming next; until then, copy `skills/`
into that agent's skills directory.

## Prerequisites

Install the Cube CLI:

```bash
curl -fsSL https://raw.githubusercontent.com/cube-js/cube/master/install-cli.sh | sh
```

Then authenticate, either way:

```bash
cube login                       # interactive — opens a browser
export CUBE_API_URL=... CUBE_API_KEY=...   # headless, CI, agent loops
```

Every skill checks both before doing anything, and stops with instructions
rather than guessing.

## Skills

| Skill | What it does |
| --- | --- |
| `cube-explore-model` | Search and inspect the semantic model — cubes, views, measures, joins, and impact analysis before a change |
| `cube-build-model` | Author cubes and views in YAML on a dev-mode branch, validate, commit, deploy |
| `cube-explore-content` | Browse workbooks, dashboards, reports and folders |
| `cube-build-content` | Create and update workbooks, reports, dashboards and scheduled notifications |
| `cube-run-query` | Run semantic-layer queries and interpret the results |
| `cube-configure-agent` | Inspect and tune the in-product agent — agents, rules, certified queries, skills |
| `cube-admin` | Users, groups, attributes, access policies, tenant settings, SCIM and OIDC |
| `cube-embed` | Embed sessions, tokens and embed tenants for embedded analytics |
| `cube-deploy` | Deployments, environments, environment variables, build status and logs |

Skills activate on their own when a request matches. You can also name one
directly: *"use cube-build-model to add a churn measure."*

## Three things called "skills"

Cube has three agent-facing surfaces and the names are close enough to be
worth stating plainly:

| | What it is | Where it runs |
| --- | --- | --- |
| **Cube connector** | Ask Cube questions in natural language | Claude — desktop, web, Code |
| **Cube agent skills** (this repo) | Operate Cube — model, content, access, deployments | Your coding agent, over the `cube` CLI |
| **Agent Skills in Cube** | Saved workflows your data team authors in the semantic model | Analytics Chat, via the `/` menu |

The [Cube connector](https://docs.cube.dev/docs/integrations/mcp-server) and
these skills compose: connect both, and Claude can ask questions of your data
*and* act on the platform.

## Contributing

Issues and pull requests welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
Commits need a [DCO](DCO.md) sign-off (`git commit -s`), the same as
[cube-js/cube](https://github.com/cube-js/cube).

## License

[Apache 2.0](LICENSE)
