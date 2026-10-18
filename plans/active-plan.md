# M0: foundation stabilization
User authorized 2026-10-19: integrate local ingest improvements, fix authentication, verify tests.
Use isolated feature branch based on sales PR #3. Preserve original uncommitted work.
Import only reusable offline-tested workers; omit prospect/client data and delivery scripts.
Replace hardcoded auth with environment-only scrypt credentials and signed expiring sessions; fail closed.
Check authentication at data access as well as middleware. No new dependencies or services.
Combine Python and JS tests; repair obsolete lint command using existing TypeScript checks.
Run tests, lint, typecheck, build, browser QA and PDF check. Open reviewable PR; no production merge.
