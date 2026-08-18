---
name: cube-configure-agent
description: >-
  Inspect and tune Cube's in-product AI agent — its rules, certified queries and Agent Skills — by authoring markdown in the semantic model with the Cube CLI. Use whenever someone wants the Cube agent to answer better: teach it a business definition, stop it making a recurring mistake, certify a trusted query, capture a repeatable workflow as a skill, or find out why it answered the way it did. Triggers on "the agent keeps getting X wrong", "teach the agent that", "make the agent always", "add a certified query", "create an agent skill", "why did the agent say that", "what rules does the agent have". To change the underlying model use cube-build-model; to explore what is queryable use cube-explore-model.
license: Apache-2.0
---

# Configure the Cube agent

Mostly know-how rather than commands. Two CLI calls read the current state;
everything else is writing markdown into the data model, which means the
dev-mode workflow from `cube-build-model` applies.

## Preflight

```bash
command -v cube >/dev/null || echo "Cube CLI not installed: curl -fsSL https://raw.githubusercontent.com/cube-js/cube/master/install-cli.sh | sh"
cube whoami || echo "Not authenticated. Interactive: cube login. Headless: set CUBE_API_URL + CUBE_API_KEY."
cube context list
```

## See what's configured

```bash
cube agents list <deployment>
cube agents skills <deployment>
cube agents skills <deployment> --space <space> --branch <branch>
```

`cube agents skills` returns name, title and description — the metadata the
agent matches on. It does not return the instructions; read those from the
model files below.

## Agent config lives in the data model

Under `agents/` in the project, as markdown:

```
agents/
  rules/               always-on instructions
  certified_queries/   trusted, named queries
  skills/              named multi-step workflows, run from the / menu
```

Read and write them with `cube data-model`, on a dev-mode branch:

```bash
cube data-model get <deployment> agents/rules/revenue-definitions.md
cube data-model dev-mode <deployment> main
cube data-model put <deployment> agents/skills/weekly-revenue-report.md --file ./skill.md --branch <dev-branch>
cube data-model commit <deployment> -m "Add weekly revenue report skill" --branch <dev-branch>
```

The filename is the identity. `weekly-revenue-report.md` becomes the skill
`weekly-revenue-report`. Because these are project files, they inherit the
project's git flow, review and access policies — a rule on a dev branch is
testable before it reaches anyone.

## Which one to reach for

This is the judgement the skill exists to carry.

| Use | When |
| --- | --- |
| **Rule** | A fact or constraint that should apply to *every* answer. "Revenue excludes refunds." "Never show data before 2024." Always in context, so keep them few and short. |
| **Certified query** | A specific question with one correct query. Pins the answer so the agent stops re-deriving it. |
| **Skill** | A repeatable multi-step workflow a person would otherwise re-type. "Weekly revenue report" — pull, break down, compare, summarize. |

The common mistake is writing a rule for something that should be a skill.
Rules are always loaded, so every rule is charged to every conversation; a
long list of them dilutes all of them. If the instruction only matters when
someone asks for a particular thing, it is a skill.

## Writing a good rule

- State the fact, not the behaviour. "Active user means logged in within 28
  days" beats "always calculate active users correctly".
- One idea per rule. Split compound rules; they are easier to review and to
  delete when they go stale.
- Prefer fixing the model. A rule that explains what a badly named measure
  means is a workaround — renaming the measure with `cube-build-model` fixes
  it for every consumer, not just the agent.

## Writing a good skill

Frontmatter `title` and `description` (both required), markdown body for the
instructions. The `description` is what the agent matches free-text requests
against, so write it the way a user would ask, not the way you would file it.

Number the steps. Say what the output should look like. If a step depends on
a certified query or a specific view, name it.

## Diagnosing a bad answer

When someone says the agent got something wrong, check in this order:

1. **Is the model right?** A wrong measure produces a wrong answer no amount
   of instruction fixes. Verify with `cube-run-query`.
2. **Is the field exposed?** If it is not in a view, the agent cannot use it.
3. **Is there a conflicting rule?** Read every rule, not just the relevant
   one. Contradictory rules are common and the symptom is inconsistency.
4. **Only then** add a rule or certified query.

Skipping to step 4 is how deployments end up with thirty rules that paper
over four model problems.

## When something fails

| Symptom | Cause |
| --- | --- |
| Skill does not appear | Not on the branch the chat is using, or the branch has not been built |
| Write rejected | Not on a dev-mode branch — see `cube-build-model` |
| `cube agents skills` returns nothing | No skills authored, or the wrong `--space`/`--branch` |
