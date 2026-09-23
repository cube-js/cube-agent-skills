# Changelog

Notable changes to Cube agent skills. Independent semver — this version is not
tied to the Cube CLI or the Cube release train.

## Unreleased

### Added

- The hosted Cube MCP server (`https://cubecloud.dev/mcp`) is bundled in the
  Claude plugin via `.mcp.json`. It points at the same endpoint as the Cube
  connector, so Claude Code treats the two as one server rather than
  connecting twice.
- Every skill now says which path to take: the Cube MCP tools when they are
  connected, the Cube CLI otherwise. `cube-admin` and `cube-embed` are
  CLI-only, and `cube-deploy` uses MCP only for read-only checks.
- An eval suite under `evals/` for `claude plugin eval`: routing cases for
  all nine skills, MCP-path cases for querying, model editing and dashboards
  against a mocked Cube server, and a negative case.
- CI runs `claude plugin validate --strict` on the marketplace, plugin and
  skills.
- Nine skills: `cube-explore-model`, `cube-build-model`, `cube-explore-content`,
  `cube-build-content`, `cube-run-query`, `cube-configure-agent`, `cube-admin`,
  `cube-embed`, `cube-deploy`.
- Plugin manifests for the Claude Code marketplace (`.claude-plugin/`), and
  skills.sh install via `npx skills add`.
- `scripts/validate-skills.py` and the PR validation workflow.

### Fixed

- Make all nine skill descriptions valid strict YAML so `npx skills add`
  discovers the complete package.
- Correct Cube CLI signatures and read/write classification across
  `cube-admin`, `cube-embed`, `cube-deploy`, `cube-build-model`,
  `cube-explore-content`, and `cube-build-content`.

### Verified

- Installed all nine skills into a clean Codex project with `skills@1.5.22`.
- Validated and installed the Claude Code plugin with Claude Code 2.1.234.
- Exercised the read-only paths against d3-demo deployment 75 with Cube CLI
  1.7.21, including compiled metadata, saved content, agents, administration,
  deployment state, embed eligibility, and a real aggregate query.
- Confirmed all 103 Cube command paths referenced by the skills resolve in
  Cube CLI 1.7.21, and confirmed a natural-language Codex request implicitly
  selects `cube-explore-model` from a clean install.

### Not yet verified

- The eval suite has not been run yet: it needs a logged-in `claude` CLI.
- The MCP path has not been driven end to end in a Claude Code session with
  the plugin installed.

Mutating paths were intentionally not executed against the shared d3-demo
tenant. Creating or changing models, content, agents, users, embed sessions,
or deployments still needs an end-to-end pass in a disposable tenant before
those write workflows can be considered verified.
