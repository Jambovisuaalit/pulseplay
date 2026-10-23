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

Set `PREVIEW_E2E_URL`, `PREVIEW_E2E_USERNAME`,
`PREVIEW_E2E_PASSWORD` and `VERCEL_AUTOMATION_BYPASS_SECRET` in a
secure local or CI secret store. Explicitly opt in to a persistent synthetic
record with `PREVIEW_E2E_PERSIST_SYNTHETIC=yes`, then execute:

```sh
node tests/preview-hosted-e2e.mjs
```

This tests: unauthenticated access denied; wrong Origin login denied; genuine
login 303 + secure HttpOnly session cookie; GET /api/ops succeeds; simultaneous
POST operations using the same expected_revision yield exactly HTTP 200 and
409; a fresh GET sees exactly one synthetic record; cross-origin writes are
blocked. It never logs authentication credentials, cookies or the Supabase key.

Afterwards check the database row in Supabase and the Vercel request logs.
For disaster recovery approval, additionally export a separate verified backup,
recover into a fresh isolated workspace and confirm the same state. This HTTP
script **does not** demonstrate cross-deployment restart persistence or
independent backup restoration. These remain separate release gates.

If an authentication, protection bypass or storage check fails, leave PR #12
as Draft and do not switch any Production settings.
