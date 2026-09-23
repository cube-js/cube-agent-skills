---
name: cube-admin
description: >-
  Administer a Cube tenant — users, groups, user attributes, access policies, tenant settings, API keys, SCIM provisioning and OIDC — using the Cube CLI. Use whenever someone wants to manage who can access what: add or remove a user, grant or revoke a user's or group's access to a deployment or resource, set user attributes for row-level security, configure SSO, rotate an API key, or audit current permissions. Triggers on "add someone to", "give access to", "who can see", "remove this user", "set up SSO", "create an API key", "what are this user's permissions", "audit access". To manage deployments themselves use cube-deploy; for embedded end-user access use cube-embed.
license: Apache-2.0
compatibility: Needs the Cube CLI, installed and logged in, and network access to Cube Cloud.
---

# Administer a Cube tenant

The widest surface in this plugin, and the one where mistakes affect other
people. Everything here is real: removing a user removes their access.

CLI-only. The Cube MCP tools do not administer users, groups or access.
Without a terminal and the Cube CLI, say so, and point the user to
**Admin** in the Cube console.

## Preflight

```bash
command -v cube >/dev/null || echo "Cube CLI not installed: curl -fsSL https://raw.githubusercontent.com/cube-js/cube/master/install-cli.sh | sh"
cube whoami || echo "Not authenticated. Interactive: cube login. Headless: set CUBE_API_URL + CUBE_API_KEY."
cube context list   # the wrong tenant here changes the wrong company's access
```

## Read before you write

Access questions are answered by reading, and most requests are questions
even when phrased as instructions. Establish the current state first:

```bash
cube users list
cube users me
cube groups list
cube policies get --resource-type <type> --resource-id <id>
cube attributes list
```

Report what you find before changing it. "Alice is already in the analysts
group" resolves a lot of requests without a write.

## Users and groups

```bash
cube users create --data '<user>'
cube users update <user> --data '<changes>'
cube users delete <user>

cube groups list
cube groups delete <group>
```

The CLI cannot create a group or change who is in one. When groups come from
an identity provider over SCIM, membership belongs there — say so. Otherwise
go through SCIM, reading the group first:

```bash
cube scim groups get <group>
cube scim groups patch <group> --data '<SCIM PatchOp JSON>'
cube scim groups create --data '<SCIM group JSON>'
```

## Access policies

```bash
cube policies get --resource-type <type> --resource-id <id>
cube policies set-group --resource-type <type> --resource-id <id> --group <group> --action <action>
cube policies set-user --resource-type <type> --resource-id <id> --user <user> --action <action>
```

**Always pass `--action`.** Without it, `set-group` and `set-user` *clear* the
policy — the command meant to grant access removes it. Actions are named per
resource, such as `WorkbookRead`; `policies get` shows the ones in use. Resource
types are `Global`, `Deployment`, `Report`, `ReportFolder`, `Agent`,
`AgentSpace`, `Workbook`, `Dashboard`, `Folder` and `ChatThread`.

Prefer `set-group` over `set-user`. Per-user grants are invisible at review
time — nobody audits them, and they outlive the person's reason for having
them. If a request is "give Alice access to X", the better answer is usually
"which group should Alice be in".

## User attributes and row-level security

```bash
cube attributes list
cube attributes create --name <name> --type string|number|boolean|string_array|number_array --display-name "<label>"
cube attributes values get <user>
```

To set a user's value, call the API directly — `cube attributes values set`
has no way to pass a value, so do not use it:

```bash
cube api POST /api/v1/user-attribute-values/ -d '{"userId":"<user-id>","userAttributeId":"<attribute-id>","value":<value>}'
cube attributes values get <user>    # confirm it took
```

Attributes feed the security context, which is what row-level security in the
model reads. Changing an attribute value changes what that user sees in every
query and every saved report — including scheduled ones that will send new
numbers to the same recipients. Say that when you change one.

## Tenant settings, SSO, keys

```bash
cube tenant settings
cube tenant update --data '<TenantSettingsInput JSON>'   # read settings first

cube oidc list / get / create / update / delete
cube scim users|groups list / get / create / patch / replace / delete   # SCIM JSON via --data
cube scim service-provider-config
cube api-keys list
cube api-keys create --name <name>     # prints the secret once — never echo it
cube api-keys delete <key>             # revokes it immediately
cube integrations list / get / create / update / delete
cube integrations tokens list / get / revoke / initiate
```

SCIM and OIDC changes affect how everyone authenticates. Read the current
config and state what will change before touching either.

When an operation has no command, `cube spec <text>` finds the API endpoint
and its request schema, and `cube api <METHOD> <path> -d '<json>'` calls it.

## Auditing

To answer "who can see X", combine:

1. `cube policies get` for the resource.
2. `cube groups list` and the user records for who that resolves to.
3. `cube attributes values get` for any row-level filtering on top.

An access answer that skips step 3 is incomplete — two users with identical
policies can see different rows.

## Conventions

- Report ids, not just names. Names collide; ids are what you act on.
- Say what changed, for whom, in plain terms. "Removed Alice from analysts;
  she loses access to deployments 1 and 4" is the useful form.
- Never rotate or revoke a credential as a side effect of another task.

## When something fails

| Symptom | Cause |
| --- | --- |
| 403 | The account is not an admin on this tenant — report it, do not work around it |
| User not found | Often the wrong tenant; check `cube context list` |
| Policy set but access unchanged | Group membership or an attribute is overriding it — audit all three layers |
| SCIM write rejected | Provisioning is managed by the IdP; changes belong there, not here |
| API keys returns the web app instead of JSON | That endpoint is unavailable on this tenant, often because the server is older — report it as unavailable, not as an empty list |
| OIDC returns `not available` | OIDC is disabled or unsupported on this tenant — do not treat the 404 as an empty configuration |
