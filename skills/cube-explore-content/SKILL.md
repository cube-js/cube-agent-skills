---
name: cube-explore-content
description: >-
  Find and inspect saved content in a Cube workspace — workbooks, dashboards, reports, folders and scheduled notifications — using the Cube CLI. Use whenever someone wants to know what already exists rather than build something new: locate a dashboard, list reports, see what a report queries, find who a notification goes to, or check what saved content references a model field before renaming it. Triggers on "what dashboards do we have", "find the revenue report", "where is that workbook", "what's in this folder", "who gets this scheduled report", "is anything using this field". To create or edit content use cube-build-content; to inspect the semantic model itself use cube-explore-model.
license: Apache-2.0
---

# Explore saved Cube content

Read-only. Workbooks, reports, dashboards, folders and notifications — the
things people made, as opposed to the model underneath them.

## Preflight

```bash
command -v cube >/dev/null || echo "Cube CLI not installed: curl -fsSL https://raw.githubusercontent.com/cube-js/cube/master/install-cli.sh | sh"
cube whoami || echo "Not authenticated. Interactive: cube login. Headless: set CUBE_API_URL + CUBE_API_KEY."
cube context list
```

## The shape of a workspace

Worth knowing before you go looking, because the names are not
interchangeable:

- **Workbook** — the authoring surface. Holds reports; can be published as a
  dashboard.
- **Report** — a saved query with a visualization. Lives in a workbook, and
  can also be filed in folders.
- **Dashboard** — the published output of a workbook, what viewers consume.
- **Folder** — organizes saved content; nests.
- **Notification** — a schedule that sends content to recipients.

## Start broad

```bash
cube workspace list <deployment>            # everything in your workspace
cube workspace shared <deployment>          # shared with you
cube folders list <deployment>
cube folders ancestors <deployment> <folder>   # where a folder sits in the tree
```

## Workbooks, reports, dashboards

```bash
cube workbooks list <deployment>
cube workbooks get <deployment> <workbook>          # includes draft and published dashboards

cube reports list <deployment>
cube reports get <deployment> <report>             # includes the saved query
cube reports folders <deployment>                  # folders that contain reports
```

Despite their names, `cube workbooks dashboard` updates a dashboard draft and
`cube workbooks ai-thread` attaches a thread to a published dashboard. They
are writes owned by `cube-build-content`, not inspection commands.

`cube reports get` is the one that answers "what does this actually show" —
it returns the saved query, so you can name the measures and dimensions
rather than describing the chart.

## Notifications

```bash
cube notifications list <deployment>
cube notifications get <deployment> <notification>
cube notifications recipients list <deployment> <notification>
```

Check recipients before anyone edits or deletes a schedule. A notification
with recipients is something people are receiving.

## Finding what references a model field

This is the half of impact analysis that `cube-explore-model` cannot do.
Renaming a measure is only safe if no saved content queries it:

1. `cube reports list <deployment> --json` to enumerate.
2. `cube reports get` the candidates and look at the saved query for the
   member name.
3. Report every report that references it, by name and id.

Saved queries reference members by name. A rename in the model does not
rewrite them, so anything you miss breaks silently the next time it runs.
Say how many reports you checked — "no references found" across three reports
means something different from across three hundred.

## Conventions

- List commands print tables; `--json` when you need to filter. Get commands
  always print JSON.
- Report ids alongside names. Names are not unique and the user needs the id
  to act.

## When something fails

| Symptom | Cause |
| --- | --- |
| Empty list | Real — a new deployment or an empty workspace. Say so rather than retrying |
| 403 on a workbook | Not shared with this account; `cube workspace shared` shows what is |
| Report has no query | A report that was never configured — a finding, not an error |
