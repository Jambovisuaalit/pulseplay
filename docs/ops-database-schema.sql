-- Desired schema, not yet applied to a project. Apply only to the chosen
-- Urakkaluotsi project, then pull a migration with the Supabase CLI.
begin;
create table public.urakkaluotsi_ops_state (
  workspace_id text primary key check (workspace_id ~ '^[a-z0-9][a-z0-9_-]{2,79}$'),
  storage_version bigint not null check (storage_version between 1 and 9007199254740991),
  state jsonb not null check ((
    jsonb_typeof(state) = 'object'
    and state @> '{"schema_version":1,"mode":"SIMULATION"}'::jsonb
    and jsonb_typeof(state->'revision') = 'number'
    and (state->>'revision')::numeric >= 0
    and jsonb_typeof(state->'clients') = 'array'
    and jsonb_typeof(state->'profiles') = 'array'
    and jsonb_typeof(state->'notices') = 'array'
    and jsonb_typeof(state->'assessments') = 'array'
    and jsonb_typeof(state->'digests') = 'array'
    and jsonb_typeof(state->'events') = 'array'
    and octet_length(state::text) <= 5000000
  ) is true)
);
alter table public.urakkaluotsi_ops_state enable row level security;
revoke all on public.urakkaluotsi_ops_state from public, anon, authenticated, service_role;
-- Supabase defaults may grant service_role DELETE/TRUNCATE/TRIGGER/REFERENCES.
-- The server adapter only needs SELECT, INSERT and conditional UPDATE.
grant select, insert, update on public.urakkaluotsi_ops_state to service_role;
comment on table public.urakkaluotsi_ops_state is
 'Private single-operator simulation workspace. Next.js session authorization precedes every access. No public/anonymous policies.';
commit;
