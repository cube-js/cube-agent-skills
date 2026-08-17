# Changelog

Notable changes to Cube agent skills. Independent semver — this version is not
tied to the Cube CLI or the Cube release train.

## Unreleased

### Added

- Nine skills: `cube-explore-model`, `cube-build-model`, `cube-explore-content`,
  `cube-build-content`, `cube-run-query`, `cube-configure-agent`, `cube-admin`,
  `cube-embed`, `cube-deploy`.
- Plugin manifests for the Claude Code marketplace (`.claude-plugin/`), and
  skills.sh install via `npx skills add`.
- `scripts/validate-skills.py` and the PR validation workflow.

### Not yet verified

None of the nine has been driven end to end against a live deployment. Every
command is checked against the CLI source rather than executed, so this is
release-blocking — see the smoke-test section of CONTRIBUTING.md.
