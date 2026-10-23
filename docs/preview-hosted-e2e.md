# Protected integration Preview → Supabase QA

This is a real deployed-app test, distinct from local PGlite/browser regressions.
Never target Production or urakkaluotsi.fi. See [exact variable placement](integration-environment.md).

## Prerequisites

- Use a successful GitHub deployment in `Preview – tenderpulse` for the integration branch.
- Bind the exact deployment URL and ID. The runner checks GitHub metadata and application-source equivalence before sending Preview credentials.
- Keep Vercel Deployment Protection enabled; supply the Automation Bypass secret to the **runner header**, not the application login.
- Supply the separate Preview operator password as `PREVIEW_E2E_PASSWORD` to the **runner login form**. Vercel uses its scrypt hash, not this variable.
- Explicitly configure the durable Supabase store and an empty dedicated `preview-e2e-` workspace for that branch.
- Bind the selected Preview project's server key to the runner for independent readback and scoped cleanup. Current test-project allowlist: `kzcmzelxydrhxxhcmmua.supabase.co`.
- Apply `docs/ops-test-cleanup.sql` only to that test project. It grants a narrow cleanup RPC, never table DELETE. Its absence is detected before creating test data.

Do not paste secret values into source, command arguments, chat, reports or logs.
When using proxy-backed credentials, scope each binding to its exact HTTPS destination.

## Authenticated full workflow

```sh
PREVIEW_E2E_PERSIST_SYNTHETIC=yes node tests/preview-hosted-e2e.mjs
```

The test checks unauthenticated access, Origin protection and distinct signed
Secure/HttpOnly/SameSite session cookies. Two simultaneous same-revision writers
must return 200/409 and persist exactly one marker and one version increment.
A direct Supabase read must confirm the result. Stale replay and CSRF must not write.

It then edits the created client, reloads, logs into a fresh session and checks
persistence. It creates a profile, synthetic notice, source assessment, digest,
approval and PDF/JSON exports. Sources, deadlines and missing information must
survive export. A new profile version must invalidate approval without modifying
delivery history; another export must be refused. Both profile versions and the
history are checked in Supabase.

The test requires an initially absent workspace row. Only data created by this
run may be removed. A `finally` block invokes the run/version-scoped cleanup and
verifies the row is absent, including after a failed workflow. No PASS report is
written unless workflow and cleanup both succeed. A uniquely named, credential-free
`qa-output/pr12-hosted-e2e-<run>.json` records the actual deployment and runner
commits. The run ID is logged so failed writes remain traceable without secrets.

## Independent backup and committed restore

The backup fixture contains a synthetic client, profile, notice, assessment,
approved snapshot, immutable approval event and a closed measurement session.
Run each phase as a separate process, from the checkout with the same secure
Supabase bindings:

```sh
set -e
export PREVIEW_E2E_PERSIST_SYNTHETIC=yes
mkdir -p .local/pr12-backups
urakkaluotsi_backup_dir=$(mktemp -d "$PWD/.local/pr12-backups/run.XXXXXX")
export PREVIEW_E2E_BACKUP_FILE="$urakkaluotsi_backup_dir/snapshot.json"
node tests/preview-backup-restore.mjs backup
node tests/preview-backup-restore.mjs restore
node tests/preview-backup-restore.mjs verify
node tests/preview-backup-restore.mjs cleanup
```

Backup is an independent owner-only file (0600) with a canonical SHA-256 check.
Restore commits a separate new workspace, refuses any existing target, and does
not use a rollback-only transaction. Verification uses a fresh process and the
production application adapter, compares every state/history/measurement field,
and confirms the source was unchanged. It may be repeated. Cleanup reads the
same verified artifact and removes only its unchanged source and target rows;
if an earlier phase fails, run the cleanup command explicitly with that artifact
after inspecting the failure. Keep the private artifact outside uploaded reports.

Successful verification and cleanup write separate credential-free JSON reports.
Neither local nor hosted workspace restoration proves full-project PITR or an
actual Vercel process restart. Those claims remain NOT_TESTED until separately
observed; a fresh Node process is not a Vercel restart.

## Local regression evidence

`npm test` covers state validation, lost writes, source-bound relevance and
backup corruption. `tests/preview-backup-runner.mjs` exercises the backup CLI in
separate processes against persisted PGlite storage. The transport intercepts
all external requests, uses the real schema/grants/cleanup RPC and checks that
only the two created rows disappear. `tests/ops-test-cleanup-sql.mjs` verifies
ownership, null inputs, stale versions, namespaces and denied role privileges.

`OPS_HTTP_STORE=supabase node tests/ops-http.cjs`, with `PGLITE_MODULE` set,
executes the real Next production HTTP workflow against a local PostgreSQL
transport. It verifies new-session persistence and a database outage without
file-store fallback. This is valuable integration evidence, **not hosted QA**.

`CHROME_PATH=/usr/bin/chromium OPS_BROWSER_QA=true node tests/ops-http.cjs`
checks local responsive portal UI plus duplicate submission, client editing,
HTML save/export failures and expired sessions. Public-page QA uses
`tests/sales-polish-qa.cjs`; email responses are simulated and no mail is sent.

The integration CI intentionally does not use live Preview secrets. Syntax,
local PostgreSQL and browser success cannot close the hosted acceptance gates.
