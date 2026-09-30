# Cube agent skills

The official [Cube](https://cube.dev) plugin for Claude, plus skills for Cursor,
OpenAI Codex, GitHub Copilot, Gemini CLI, and other
[Agent Skills](https://agentskills.io) compatible agents.

The `openai-plugin/` directory is the package source for the public Cube plugin
in ChatGPT and Codex. It connects the same hosted MCP server and includes five
MCP-backed workflows adapted from this repository. The CLI-only administration,
embedding, and deployment workflows stay in the coding-agent skills below;
they are not bundled in the public OpenAI plugin.

Ask questions of your governed semantic layer, explore and build the model,
create dashboards, administer access, and ship deployments — from the agent you
already work in.

> Cube agent skills run in your coding agent. They are not Agent Skills in
> Cube, which your data team authors in the semantic model and runs from
> Analytics Chat.

## What's in the Claude plugin

- **The Cube MCP server** at `https://cubecloud.dev/mcp`, hosted by Cube. You
  sign in with OAuth the first time you use it; there is nothing to install.
  It answers data questions, searches and edits the semantic model on a dev
  branch, and builds dashboards — always as the signed-in user, with their
  access rules applied.
- **Nine skills** that carry Cube's workflows. They use the MCP tools when
  they're connected and the [Cube CLI](https://docs.cube.dev/reference/cli)
  for what MCP doesn't cover: administration, embedding, and the deployment
  lifecycle.

## Install

**Claude Code**

```
/plugin marketplace add cube-js/cube-agent-skills
/plugin install cube@cube
```

Then run `/mcp`, select `plugin:cube:cube`, and sign in to Cube.

If you already connected the [Cube connector](https://docs.cube.dev/docs/integrations/mcp-server)
in Claude, you don't get two servers: both point at the same endpoint, so
Claude Code connects once, using the plugin's definition, and `/mcp` lists the
connector as hidden.

**Codex, Copilot, Gemini CLI, and other skills.sh-compatible agents**

```
npx skills add cube-js/cube-agent-skills
```

This installs the skills only. Add the MCP server to your agent as described
in [Cube MCP server](https://docs.cube.dev/docs/integrations/mcp-server), or
install the Cube CLI below.

Cursor and Snowflake Cortex Code are coming next; until then, copy `skills/`
into that agent's skills directory.

## The Cube CLI

Optional when the MCP server is connected. Required for `cube-admin`,
`cube-embed` and most of `cube-deploy`, and for any skill when the MCP server
isn't available, as in a CI job.

```bash
curl -fsSL https://raw.githubusercontent.com/cube-js/cube/master/install-cli.sh | sh
```

Then authenticate, either way:

```bash
cube login                       # interactive — opens a browser
export CUBE_API_URL=... CUBE_API_KEY=...   # headless, CI, agent loops
```

Every skill checks for the MCP tools or the CLI before doing anything, and
stops with instructions rather than guessing.

## Skills

| Skill | What it does | Runs over |
| --- | --- | --- |
| `cube-explore-model` | Search and inspect the semantic model — cubes, views, measures, joins, and impact analysis before a change | MCP or CLI |
| `cube-build-model` | Author cubes and views in YAML on a dev-mode branch, validate, commit, deploy | MCP or CLI |
| `cube-explore-content` | Browse workbooks, dashboards, reports and folders | CLI; MCP reads a known workbook or report |
| `cube-build-content` | Create and update workbooks, reports, dashboards and scheduled notifications | MCP or CLI; schedules are CLI-only |
| `cube-run-query` | Run semantic-layer queries and interpret the results | MCP or CLI |
| `cube-configure-agent` | Inspect and tune the in-product agent — agents, rules, certified queries, skills | MCP or CLI |
| `cube-admin` | Users, groups, attributes, access policies, tenant settings, SCIM and OIDC | CLI |
| `cube-embed` | Embed sessions, tokens and embed tenants for embedded analytics | CLI |
| `cube-deploy` | Deployments, environments, environment variables, build status and logs | CLI; MCP for read-only checks |

Skills activate on their own when a request matches. You can also name one
directly: *"use cube-build-model to add a churn measure."*

## Three things called "skills"

Cube has three agent-facing surfaces and the names are close enough to be
worth stating plainly:

| | What it is | Where it runs |
| --- | --- | --- |
| **Cube MCP server** | Ask questions, edit the model, build dashboards — the Cube connector in Claude, and bundled in this plugin | Claude — desktop, web, Code — and any MCP client |
| **Cube agent skills** (this repo) | Workflows for operating Cube — model, content, access, deployments | Your coding agent, over the MCP server and the `cube` CLI |
| **Agent Skills in Cube** | Saved workflows your data team authors in the semantic model | Analytics Chat, via the `/` menu |

## Contributing

Issues and pull requests welcome — see [CONTRIBUTING.md](CONTRIBUTING.md).
Commits need a [DCO](DCO.md) sign-off (`git commit -s`), the same as
[cube-js/cube](https://github.com/cube-js/cube).

## License

[Apache 2.0](LICENSE)
