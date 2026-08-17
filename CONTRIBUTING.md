# Contributing

## Authoring a skill

A skill is a directory under `skills/` containing a `SKILL.md`. The directory
name and the frontmatter `name` must match.

```
skills/cube-explore-model/
  SKILL.md          required
  references/       optional — detail loaded only when needed
  scripts/          optional
```

### Naming

`cube-<verb>-<object>`, imperative: `cube-explore-model`, `cube-build-content`.
Where the domain noun already names the whole job, the bare noun is fine —
`cube-admin`, `cube-embed`, `cube-deploy`.

### The description is the whole activation mechanism

Agents load only `name` and `description` at startup and decide from those
whether to pull in the rest. A vague description makes a skill unreachable no
matter how good its body is. Write one that covers:

1. **What it does**, concretely, naming the CLI it drives.
2. **When to use it** — including the phrasings a user would actually type,
   not the canonical terminology. Someone asking "what's our MoM growth" never
   says the word "query".
3. **Where to go instead**, naming sibling skills. Without this, two skills
   with similar descriptions fight over the same request.

### Keep SKILL.md short

The whole body loads on activation, so it is charged to every conversation
that triggers the skill. Under 500 lines; the validator warns past that. Move
reference material into `references/` and link it — the agent will read it
when it needs it.

### Write against commands that exist

Every command in a skill must exist in the Cube CLI as shipped. Check with
`cube <group> --help` rather than assuming a subcommand or flag by analogy —
the CLI is generated from the public API and does not always name things the
way the UI does. An invented flag fails at the worst possible moment, in
someone else's terminal.

## Validating

```bash
python3 scripts/validate-skills.py
```

This runs in CI on every PR and checks the spec rules: frontmatter parses,
`name` matches the directory and is well-formed, `description` is present and
within limits, and `SKILL.md` is not oversized.

CI does **not** run the skills against a live Cube tenant. This is a public
repository and tenant credentials do not belong in its Actions secrets, so
that testing is manual.

## Smoke testing before a release

Static validation says a skill is well-formed, not that it works. Before any
release, each changed skill gets driven end to end against a real deployment,
in a real agent:

1. Install the plugin locally from your branch.
2. Give the agent a request the skill's description claims to handle — phrased
   the way a user would, not by naming the skill.
3. Confirm it picks the right skill, that every command it runs succeeds, and
   that it does not invent output.
4. Note what you tested in the PR.

Step 2 is the one people skip. A skill that only works when invoked by name
has a broken description, and that is the most common defect here.

## Pull requests

- Sign off your commits: `git commit -s` ([DCO](DCO.md)).
- One skill per PR where possible.
- Add a `CHANGELOG.md` entry under `## Unreleased`.
- Say in the PR description which deployment you smoke-tested against, and
  which requests you used.

## Releases

Independent semver, tracked in `CHANGELOG.md` — the version is not tied to the
Cube CLI or the Cube release train. Bump `version` in
`.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` together;
they are read by different consumers and drift between them is silent.
