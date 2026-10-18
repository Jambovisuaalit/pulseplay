# Urakkaluotsi: M0 foundation stabilization

Scope: reusable local ingest + existing single-operator authentication + regression checks. Based on sales branch commit a0e723c. Original uncommitted working tree remains untouched. No new packages, services, paid APIs, live collection or outbound messages.

## Ingest

Imported fetch_hilma, hilma_http/cpv/detail/store/screen/draft and their 18 synthetic regression tests. Official HTTPS host only; redirects rejected before credential forwarding; bounded retries; locked UTC window; schema and count checks; pagination duplicates rejected; raw responses preserved locally; atomic idempotent store by notice ID. This JSON store replaces a notice's latest revision and is single-writer: immutable source versions and concurrency belong to M2.

Removed the hardcoded prospect name from reusable email drafts. Private prospect profiles, source exports and prospect-specific delivery scripts were not imported. Draft generation has no send transport. Source review flag alone does not constitute final human delivery approval.

Updated ingest workflow to metadata-only manual execution. Removed the daily schedule and incompatible attachment/OCR/old scoring stages from this branch. Activate live collection only after key rotation and API scope review. No live calls were made. Original production branch workflow is unchanged until this PR is merged there.

## Authentication

Removed hardcoded username/password hash and static bearer cookie. Required runtime variables:

- `TP_AUTH_USERNAME`: operator username, maximum 128 characters.
- `TP_AUTH_PASSWORD_SCRYPT`: 32 hexadecimal salt characters, colon, 128 hexadecimal scrypt digest characters; scrypt N=16384, r=8, p=1, length=64, salt is the UTF-8 hex string.
- `TP_SESSION_SECRET`: independent cryptographically random 32-byte secret as 64 hex characters. Rotate to invalidate every existing session.

Run `python3 scripts/configure_auth.py` locally to create a new owner-only `.env.local` without echoing passwords. It refuses to overwrite an existing file. Use a unique random password (24+ characters). For Vercel, copy the three values directly to the correct project's environment settings, scoped independently for preview and production; never paste them in Git, tickets or logs. Local env creation does not configure Vercel. Deployment configuration has not been changed.

Session: Web Crypto HMAC-SHA256, random 128-bit nonce, one-hour expiry; no shared permanent token. HTTP-only, SameSite=Lax, Secure production cookie. Missing configuration fails closed. POST login/logout require matching Origin. Login has input limits and a five-attempt/minute per-instance limit. This limit is not distributed and is not sufficient protection for a public multi-user login; managed auth and platform limits remain M2 requirements. Logout deletes the browser cookie; copied bearer tokens remain valid until expiry or signing-key rotation. Password change alone does not revoke already signed sessions: also rotate session secret.

Data access verifies the signed session again and makes private routes dynamic. Middleware adds private/no-store headers. Public landing/privacy/demo remain available. No client capabilities should be introduced before managed identity/RLS and preview isolation are verified.

## Verification

- `npm test`: 8 JS tests and 18 Python offline tests pass.
- `npm run lint`: existing TypeScript compiler with unused-symbol checks; this is a type-based check, not ESLint. The previous `next lint` command is unsupported by the installed Next version. No dependency was added.
- `npm run typecheck`: passes.
- `npm run build`: passes with installed Next 15.5.28; private dashboard is dynamic.
- HTTP production-build tests: missing config, login credentials, static/tampered session rejection, protected/public route isolation, Origin, secure cookie, logout and throttle. Run `node tests/auth-http.cjs --missing` then `node tests/auth-http.cjs` after build.
- Public PDF SHA-256 and four-page count preserved.
- Full 375/390/768/1440 browser regression is part of CI. Local Chromium executable is unavailable; CI outcome is recorded in PR after execution.

No relevance/classification algorithm was changed, no LLM evaluation or precision claim was produced. Original local screening/draft behavior is imported with its synthetic regression tests. No production merge or deployment activation in this task.

Technical reference consulted: https://nextjs.org/docs/15/pages/guides/authentication — session expiry, cookie attributes and authentication at data access. This bootstrap implementation adds no auth library; migrate to managed auth in M2.
