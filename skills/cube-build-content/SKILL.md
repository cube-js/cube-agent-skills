---
name: cube-build-content
description: Create and update saved content in Cube — workbooks, reports, dashboards, folders and scheduled notifications — using the Cube CLI. Use whenever someone wants to build or change something people will look at: make a dashboard, save a query as a report, add a chart, organize content into folders, publish a workbook, or schedule a report to go out on a cadence. Triggers on "build me a dashboard", "save this as a report", "add a chart for", "publish this workbook", "schedule this weekly", "move these into a folder", "duplicate that dashboard". To find existing content first use cube-explore-content; to check a query returns the right numbers before saving it use cube-run-query.
license: Apache-2.0
---

# Build Cube content

Writes state. Reports and dashboards are what people see, so a mistake here
is visible to more than the person who made it.

## Preflight

```bash
command -v cube >/dev/null || echo "Cube CLI not installed: curl -fsSL https://raw.githubusercontent.com/cube-js/cube/master/install-cli.sh | sh"
cube whoami || echo "Not authenticated. Interactive: cube login. Headless: set CUBE_API_URL + CUBE_API_KEY."
cube context list
```

## Order of operations

Content hangs off a workbook, so build outward from one:

1. **Verify the query first.** Run it with `cube-run-query` and confirm the
   numbers are right. Saving a wrong query is how a bad number gets an
   audience.
2. **Create or pick a workbook.**
3. **Add reports to it.**
4. **Publish it as a dashboard** if people need to consume it.
5. **Schedule it** if it should arrive on a cadence.

## Workbooks

```bash
cube workbooks create <deployment> --name "Revenue review"
cube workbooks update <deployment> <workbook> --name "Revenue review Q3"
cube workbooks duplicate <deployment> <workbook>
cube workbooks publish <deployment> <workbook>      # makes the dashboard
cube workbooks delete <deployment> <workbook>
```

Duplicating an existing workbook is usually a better starting point than
creating an empty one — it inherits layout and conventions the team already
uses.

## Reports

```bash
cube reports create <deployment> --name "Revenue by month" --json-query '<query>'
cube reports update <deployment> <report> --json-query '<query>'
cube reports connect-workbook <deployment> <report> <workbook>
cube reports refresh <deployment> <report>
cube reports delete <deployment> <report>
```

`--json-query` takes the same query shape `cube-run-query` sends to the load
endpoint — measures, dimensions, timeDimensions, filters. Take the query you
already verified rather than retyping it; retyping is where a filter goes
missing.

Complex bodies go through `-d/--data`, which accepts inline JSON, `@file.json`
or `-` for stdin. Dedicated flags override values in `--data`.

## Folders

```bash
cube folders create <deployment> --name "Finance"
cube folders update <deployment> <folder> --name "Finance & RevOps"
cube workspace move <deployment> ...      # move content between folders
cube folders delete <deployment> <folder>
```

## Scheduled notifications

```bash
cube notifications create <deployment> ...
cube notifications recipients add <deployment> <notification> ...
cube notifications recipients list <deployment> <notification>
cube notifications update <deployment> <notification> ...
```

Before changing or deleting a schedule, list its recipients and say who is
currently receiving it. People notice when a report stops arriving, and they
rarely connect it to a change someone made.

## Conventions

- Name things the way the user said them. Do not tidy "MRR" into "Monthly
  Recurring Revenue" unless asked.
- Report the id of everything you create, and the URL if the output carries
  one. The user's next step is opening it.
- Creating is cheap and deleting is not. When a request is ambiguous between
  "change the existing one" and "make a new one", make a new one and say so.

## When something fails

| Symptom | Cause |
| --- | --- |
| Report saves but shows no data | The query is wrong, not the report — verify with `cube-run-query` |
| `Member not found` | Stale member name; the model changed. Re-check with `cube-explore-model` |
| Publish does nothing visible | The workbook had no reports yet — add them first |
| 403 | The account can read the workspace but not write to it |
