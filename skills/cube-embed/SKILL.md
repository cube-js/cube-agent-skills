---
name: cube-embed
description: >-
  Set up and debug Cube embedded analytics — embed sessions, embed tokens, embeddable dashboards and embed tenants — using the Cube CLI. Use whenever someone is shipping Cube analytics inside their own product: mint a session for an end user, enable a dashboard for embedding, set up multi-tenant isolation so each customer sees only their data, or debug why an embedded view is empty or unauthorized. Triggers on "embed this dashboard", "embedded analytics", "our customers need to see", "multi-tenant analytics", "the iframe is blank", "embed token", "sign the embed URL", "customer-facing dashboard". For internal access control use cube-admin; for the dashboards themselves use cube-build-content.
license: Apache-2.0
---

# Embed Cube in your product

Embedding is where analytics leaves your team and reaches your customers, so
the isolation model matters more than the mechanics. Most of the work is
getting the security context right; the CLI part is short.

## Preflight

```bash
command -v cube >/dev/null || echo "Cube CLI not installed: curl -fsSL https://raw.githubusercontent.com/cube-js/cube/master/install-cli.sh | sh"
cube whoami || echo "Not authenticated. Interactive: cube login. Headless: set CUBE_API_URL + CUBE_API_KEY."
cube context list
```

## The model, before the commands

Four things, and conflating them is the usual source of confusion:

- **Embed tenant** — one of your customers. The isolation boundary.
- **Embed user** — an end user inside one of those customers.
- **Embed session / token** — short-lived credentials carrying that user's
  security context. This is what makes row-level security apply.
- **Embeddable dashboard** — a dashboard explicitly enabled for embedding.
  Dashboards are not embeddable by default.

The security context in the token is what the model's row-level security
reads. **Isolation is a property of the token you mint, not of the dashboard
you embed.** A correct dashboard with a wrong token shows one customer
another customer's data — which is the failure mode worth being paranoid
about.

## Commands

```bash
cube embed generate-session --data '<session>'
cube embed token --session-id <session>

cube embed enable-dashboard <public-id>
cube embed dashboard <public-id>
cube embed disable-dashboard <public-id>

cube embed tenant groups <tenant>
cube embed tenant delete <tenant>
cube embed tenant delete-group <tenant> <group>
```

Sessions and tokens are minted server-side. They must never be generated in
browser code or checked into a repository — anyone holding one has that
user's access until it expires.

## Setting up a new embedded dashboard

1. Build and publish the dashboard (`cube-build-content`).
2. Get the dashboard's public id, then run `cube embed enable-dashboard` —
   until this runs, embedding it fails.
3. Confirm the model has row-level security keyed on the attribute your
   security context carries. Check with `cube-explore-model`; if it does not,
   stop and fix the model first.
4. Mint a session for a **test** embed user of one tenant.
5. Verify that user sees only that tenant's rows — query the same measure via
   `cube-run-query` with a different context and confirm the numbers differ.

Step 5 is the one that catches broken isolation, and it is the one people
skip because step 4 appeared to work.

## Debugging an embedded view

| Symptom | Where to look |
| --- | --- |
| Blank iframe, no error | Dashboard not enabled for embedding — run `cube embed dashboard` to check |
| 401 / 403 in the iframe | Token expired or minted for the wrong tenant |
| Renders but no rows | Security context has no matching value — the token is valid but scoped to nothing |
| Shows **too much** data | Row-level security is not applied. Stop and treat this as an incident, not a bug to iterate on |
| Works for you, not customers | You are testing with an internal account that bypasses the tenant scope |

## Conventions

- Never print a full token in output. Say that one was minted and for which
  user.
- Always test with a real embed user, never an admin account. Admin accounts
  see everything, which makes broken isolation invisible.
- When something is wrong with isolation, say so directly and stop.
