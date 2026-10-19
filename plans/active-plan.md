# M1: delivery data model
User authorized 2026-10-19: build clients, profile versions, notices, assessments, delivery history.
Base: verified M0 tree 7390d3ef. Work on feature/urakkaluotsi-data-model, PR depends on #5.
Implement PostgreSQL schema source (not an applied Supabase migration), TypeScript domain contracts and validators.
Enforce version identity, client/profile ownership, immutable historical snapshots, explicit unknown facts, org RLS.
Test on ephemeral PostgreSQL 16 in CI, plus existing tests/lint/typecheck/build. No cloud changes, paid services, dependencies or live ingest.
M2 will generate the actual Supabase migration with the CLI and connect a dedicated project after its account is selected.

User expanded scope in same turn: complete profile → review → digest → approval → export, source/deadline/missing-data QA and invalidation.
Implement /ops + authenticated API, pure domain workflow, five export formats and opt-in local simulation persistence.
Production store remains closed until dedicated cloud identity/database wiring exists; no real-data deployment claimed.
