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

- `cube-build-model`'s CLI workflow no longer commits into production. It
  forked dev mode from the deploy branch, and `commit` pushes into the branch
  dev mode came from. It now works on a feature branch, validates with
  `cube validate --dev-mode`, waits on `build-status --wait`, and publishes
  with `merge-to-default` only when asked.
- `cube-admin` sets user attribute values through the API, because
  `cube attributes values set` cannot pass a value. The access-policy commands
  now always pass `--action`, since leaving it out clears the policy. The skill
  no longer promises to create groups, which the CLI can only do over SCIM.
- Wrong claims: the CLI has had `cube validate` since 1.7.25; `workspace shared`
  lists items shared with embed users, not with you; and `reports list` returns
  one page, so impact checks now page through every report.
- `cube-run-query` queries a dev branch at its own `/dev-mode/<branch>/`
  endpoint instead of production, and retries on `Continue wait`.
- `cube-embed` tests tenant isolation with per-tenant tokens from
  `environments create-token`, not the caller's own token.
- `cube-configure-agent` covers `agents/config.yml`, per-space folders, and the
  `CUBE_CLOUD_AGENTS_CONFIG_ENABLED` opt-in that older deployments need.
- Replace every `...` placeholder with the real signature, including the
  required `--data` bodies for notifications and tenant settings.
- `cube deploy` guidance warns that it prunes remote files missing locally
  unless `--keep-missing` is passed.
- Following Anthropic's skill guidance, MCP tools are named in full
  (`cube:runQuery`), and every skill declares `compatibility`, which
  `scripts/validate-skills.py` now checks against the spec's 500-character
  limit.
- Make all nine skill descriptions valid strict YAML so `npx skills add`
  discovers the complete package.
- Correct Cube CLI signatures and read/write classification across
  `cube-admin`, `cube-embed`, `cube-deploy`, `cube-build-model`,
  `cube-explore-content`, and `cube-build-content`.

### Verified

- `claude plugin eval . --runs 1 --ablation none` (Claude Code 2.1.280)
  passed 10/10 cases. Every routing case fired the intended skill; an
  unrelated request pulled in no Cube skill or tool. On the mocked Cube
  server, querying went `searchDataModel` → `runQuery`; the model edit went
  `startDataModelEdit` → read → write → `runQuery` → `commitDataModelChanges`
  and never called `mergeToDefaultBranch`; and the dashboard was built and
  published in the documented order.
- Installed all nine skills into a clean Codex project with `skills@1.5.22`.
- Validated and installed the Claude Code plugin with Claude Code 2.1.234.
- Exercised the read-only paths against d3-demo deployment 75 with Cube CLI
  1.7.21, including compiled metadata, saved content, agents, administration,
  deployment state, embed eligibility, and a real aggregate query.
- Confirmed all 103 Cube command paths referenced by the skills resolve in
  Cube CLI 1.7.21, and confirmed a natural-language Codex request implicitly
  selects `cube-explore-model` from a clean install.

### Not yet verified

- The MCP path has been exercised only against the mocked Cube server in
  `evals/`, not end to end against a real tenant in a Claude Code session.
- The eval suite has only had one run per case, on the default model, with no
  no-plugin baseline. Anthropic's guidance also asks for runs on Haiku,
  Sonnet and Opus.
- Several fixes follow the CLI docs and API schema but have not been run: that
  `commit` pushes into the parent branch, the attribute-value API call, and the
  `/dev-mode/<branch>/` query endpoint. The commands and flags were checked
  against `--help` in Cube CLI 1.7.37, the version they were written against;
  1.7.43 is the latest release.

Mutating paths were intentionally not executed against the shared d3-demo
tenant. Creating or changing models, content, agents, users, embed sessions,
or deployments still needs an end-to-end pass in a disposable tenant before
those write workflows can be considered verified.
