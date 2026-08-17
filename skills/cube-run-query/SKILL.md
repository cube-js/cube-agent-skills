---
name: cube-run-query
description: Run queries against a Cube deployment's semantic layer and interpret the results, from the terminal. Use whenever someone wants numbers out of Cube — pull a metric, check a total, compare periods, verify that a measure returns what it should, sanity-check a model change. Triggers on "how many", "what's the total", "show me revenue by month", "did that measure work", "what's our MoM growth", "pull the numbers for", and any request to verify a model change against real data. To find out what is queryable first use cube-explore-model; to change the model use cube-build-model; to save a result as a report or dashboard use cube-build-content.
license: Apache-2.0
---

# Run a query against Cube

This is the one skill that steps outside the CLI. `cube api` is bound to
Cube's console API and cannot reach a deployment's query endpoint, so
querying is two CLI calls to get a URL and a token, then a direct request to
the deployment.

## Preflight

```bash
command -v cube >/dev/null || echo "Cube CLI not installed: curl -fsSL https://raw.githubusercontent.com/cube-js/cube/master/install-cli.sh | sh"
cube whoami || echo "Not authenticated. Interactive: cube login. Headless: set CUBE_API_URL + CUBE_API_KEY."
cube context list
```

`jq` and `curl` are also required here, unlike every other skill in this
plugin. Check for them and say so if they are missing.

## Get the endpoint and a token

```bash
DEPLOYMENT=<id>
URL=$(cube deployments get "$DEPLOYMENT" --json | jq -r .deploymentUrl)
TOKEN=$(cube deployments token "$DEPLOYMENT")
```

`cube deployments token` prints the Cube API token on its own; add `--json`
if you want the wrapping object. The token carries the calling user's
security context, so row-level security applies exactly as it would in the
UI — a query here returns what *that user* is allowed to see, not everything.

## Know what you can query first

Do not guess member names. Ask the compiled model:

```bash
cube meta --selectors '[{"type":"cube","deploymentId":'"$DEPLOYMENT"',"environment":"production"}]'
```

Members are `Cube.member` or `View.member`. A dimension that exists on a cube
but is not exposed in a view is not queryable through that view — `cube meta`
is what tells you which is which.

## Run it

```bash
curl -s "$URL/cubejs-api/v1/load" \
  -H "Authorization: $TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"query":{
        "measures":["Orders.count","Orders.totalRevenue"],
        "dimensions":["Orders.status"],
        "timeDimensions":[{"dimension":"Orders.createdAt","granularity":"month","dateRange":"Last 6 months"}],
        "limit":100
      }}' | jq
```

Query shape, in the order you usually need it:

- `measures` — the numbers. Always fully qualified.
- `dimensions` — what to break down by.
- `timeDimensions` — `dimension` plus `granularity` (`day`/`week`/`month`/…)
  and `dateRange`, which accepts natural ranges like `"Last 30 days"` or an
  explicit `["2026-01-01","2026-06-30"]`.
- `filters` — `[{"member":"Orders.status","operator":"equals","values":["paid"]}]`.
- `order`, `limit`.

The response carries `data` plus `annotation`, which holds the human titles
and formats for each member. Use `annotation` when presenting results — it is
where a measure's display name and unit live.

## Interpreting results

- **Report the number, then how it was derived.** Which measure, which range,
  which filters. A number without its query is not checkable.
- **An empty `data` array is a result, not an error.** Say the query succeeded
  and returned no rows; do not retry with a different query and present that
  instead without saying you changed it.
- **Never fill in a value you did not receive.** If the query failed, report
  the error.

## Verifying a model change

The common case after `cube-build-model`: query the new measure on the dev
branch before merging. Point the environment at the branch when getting meta,
and query the deployment the same way — the token and URL are per-deployment,
not per-branch.

## When something fails

| Symptom | Cause |
| --- | --- |
| `deploymentUrl` is null | The deployment has never finished a build; check `cube deployments build-status` |
| 401 from the load endpoint | Token expired — they are short-lived, just mint another |
| `Member not found` | Wrong name or not exposed in that view — re-check `cube meta`, do not guess a variant |
| Query hangs | A large uncached query; report it rather than silently retrying |
