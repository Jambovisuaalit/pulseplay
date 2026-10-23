# PR #12 — protected Vercel Preview → Supabase E2E

This procedure tests **the deployed Next.js app**, not a local mock. It remains
separate from the synthetic CI tests. Never run it against urakkaluotsi.fi or
a Production deployment.

## Preconditions

- Deployment URL is `https://<deployment>.vercel.app` and the deployment
  is Vercel Preview from `feature/urakkaluotsi-durable-storage`.
- Vercel Deployment Protection stays enabled. Obtain the **Automation Bypass**
  secret from Vercel's Deployment Protection settings without putting it in git.
- Operator login is the separate Preview username and password in Vercel's
  Preview credentials. Do not reuse the Production password.
- Preview's `TP_OPS_STORE=supabase`, `TP_OPS_WORKSPACE` and server-only
  Supabase values are correctly scoped to the PR branch.
- The test adds one identifiable synthetic client record to the isolated
  Preview workspace. The record **persists** by design: the operator's table
  grants intentionally do not include DELETE. Do not run on real customer data.

## Run with secrets held outside source control

Set `PREVIEW_E2E_URL`, `PREVIEW_E2E_USERNAME`, `PREVIEW_E2E_PASSWORD`,
`VERCEL_AUTOMATION_BYPASS_SECRET` and `PREVIEW_E2E_WORKSPACE` in the test
environment. The workspace must equal the branch-scoped Vercel
`TP_OPS_WORKSPACE` and be an isolated Preview/test workspace. Also bind
`TP_SUPABASE_URL=https://kzcmzelxydrhxxhcmmua.supabase.co` and the server-only
`TP_SUPABASE_SECRET_KEY` securely. The test independently reads this documented
Urakkaluotsi Preview project to verify that the HTTP write reached Supabase.
Do not paste secret values into a command, git, an issue, a report or chat.
Existing proxy-backed bindings can be used; the runner does not require a raw
key to be printed or extracted.

Also set `PREVIEW_E2E_DEPLOYMENT_ID` to the GitHub deployment ID. Before sending
credentials or writing data, the runner checks public GitHub metadata: the
environment must be `Preview – tenderpulse`, its latest status must be successful,
and its URL must equal the supplied URL. It compares that deployment's application
source paths against the local checkout and records both source commits. Fetch
the exact deployed commit through the existing Git proxy if it is absent locally.
For the inspected deployment these non-secret settings are deployment ID
`7267251281` and URL
`https://tenderpulse-fch3db8x2-info-32533854s-projects.vercel.app`.

Explicitly opt in to a persistent synthetic record with
`PREVIEW_E2E_PERSIST_SYNTHETIC=yes`, then execute:

```sh
node tests/preview-hosted-e2e.mjs
```

This tests: unauthenticated access denied; wrong Origin login denied; two genuine
logins issue distinct Secure/HttpOnly/SameSite session cookies; both sessions
read the same revision; simultaneous POSTs through those sessions yield exactly
HTTP 200 and 409. Distinct writer markers identify the winner. Exactly one new
client and one revision must persist, while every previous client remains
unchanged. A separate read of the actual Supabase row verifies the winner and
exactly one storage-version increment. A stale replay remains 409 without a
write; cross-origin writes remain 403 without a write. It never logs credentials,
cookies or the server key. Success writes a uniquely named, credential-free
`qa-output/pr12-hosted-e2e-<run>.json` evidence file. No PASS report is generated
by the missing-credential preflight.

Afterwards check the database row in Supabase and the Vercel request logs.
The HTTP test does not demonstrate backup restoration or Vercel restart
persistence. Run the independent procedure below for the workspace-backup gate.

If an authentication, protection bypass or storage check fails, leave PR #12
as Draft and do not switch any Production settings.

## Separate committed backup and restore

Use the same isolated Supabase project and secure server-key binding. This
procedure creates **two** identifiable synthetic workspaces: a source and a
fresh restore target. It never reads or modifies an existing operator workspace,
never uses DELETE, never overwrites an existing restore target, and grants no
additional database privileges. The two rows persist because the adapter's
service role intentionally cannot delete them. Any later cleanup requires an
explicitly scoped owner operation; do not broaden the adapter's grants.

Run from the checkout with Node 24. Each command is a separate process:

```sh
set -e
export PREVIEW_E2E_PERSIST_SYNTHETIC=yes
mkdir -p .local/pr12-backups
urakkaluotsi_backup_dir=$(mktemp -d "$PWD/.local/pr12-backups/run.XXXXXX")
export PREVIEW_E2E_BACKUP_FILE="$urakkaluotsi_backup_dir/snapshot.json"
node tests/preview-backup-restore.mjs backup
node tests/preview-backup-restore.mjs restore
node tests/preview-backup-restore.mjs verify
```

`backup` creates a complete synthetic workflow using the real domain commands:
client, profile, notice, assessment, approved digest, immutable approval history
and a closed measurement session. It inserts the source, reads it back and
writes an independent owner-only (0600), checksummed JSON backup, then exits.
The private artifact lives in ignored `.local/`, outside reports.

`restore` loads and validates that disk artifact in a new process and commits a
new row in its separate target workspace. This is not a transaction rolled back
after verification. Duplicate targets fail without an overwrite. `verify` starts
another process and compares every stored snapshot field, storage version,
approval-history entry and measurement against the file. It also reads the
restored state using a fresh production application adapter and checks that the
source is unchanged. Verification can be repeated without modifying either row.
Each successful verification writes a unique credential-free
`qa-output/pr12-backup-restore-<run>-<verification>.json` report.

Scope: this proves an application-workspace backup/restore only **after the real
hosted procedure passes**. It does not prove restoration of the entire Supabase
project, provider-managed PITR, or persistence after an actual Vercel deployment
restart. The report labels those broader claims NOT_TESTED. Re-read the state
after an explicitly scoped Preview restart before closing that remaining
readiness requirement.

## Local regression versus hosted evidence

`npm test` checks evidence validation, lost writes, corruption and unsafe restore
retargeting. PR12 CI also runs `tests/preview-backup-runner.mjs` with the existing
isolated PGlite installation. That integration executes the three CLI processes
against a local persisted PostgreSQL fixture using the real schema/grants; it
checks committed restoration, a fresh application adapter, repeated verification,
overwrite refusal and corrupted-backup rejection. Its fetch transport intercepts
all requests, so it cannot contact Supabase or Vercel. Local mock reports are
removed with the fixtures and cannot serve as hosted acceptance evidence.

The existing GitHub Actions QA does not consume Preview secrets automatically.
Adding local regression coverage or passing syntax checks does not close any of
the three hosted gates. Keep PR #12 Draft until real results have been reviewed.
