-- M1 schema source, applied in filename order to an empty PostgreSQL/Supabase DB.
-- This is not a deployed Supabase migration. All dates are timestamptz (UTC storage).
begin;
create table public.organizations (
 id uuid primary key default gen_random_uuid(), name text not null check(length(trim(name))>0),
 created_at timestamptz not null default now()
);
create table public.operator_memberships (
 org_id uuid not null references public.organizations(id), user_id uuid not null references auth.users(id),
 role text not null check(role in ('ADMIN','EDITOR','VIEWER')), active boolean not null default true,
 created_at timestamptz not null default now(), primary key(org_id,user_id)
);
create table public.clients (
 id uuid primary key default gen_random_uuid(), org_id uuid not null references public.organizations(id),
 name text not null check(length(trim(name))>0), business_id text check(business_id ~ '^\d{7}-\d$'),
 status text not null default 'DRAFT' check(status in ('DRAFT','PILOT','ACTIVE','PAUSED','ARCHIVED')),
 delivery_email text, row_version integer not null default 1 check(row_version>0),
 created_at timestamptz not null default now(), unique(org_id,id)
);
create table public.client_profile_versions (
 id uuid primary key default gen_random_uuid(), org_id uuid not null, client_id uuid not null,
 version integer not null check(version>0), services text[] not null default '{}',
 cpv_codes text[] not null default '{}', regions text[] not null default '{}', exclusions text[] not null default '{}',
 facts jsonb not null default '[]' check(jsonb_typeof(facts)='array'),
 created_by uuid not null references auth.users(id), created_at timestamptz not null default now(),
 unique(org_id,client_id,version), unique(org_id,client_id,id),
 foreign key(org_id,client_id) references public.clients(org_id,id)
);
create table public.notices (
 id uuid primary key default gen_random_uuid(), org_id uuid not null references public.organizations(id),
 source text not null default 'HILMA' check(source='HILMA'), external_id text not null check(external_id ~ '^\d+$'),
 created_at timestamptz not null default now(), unique(org_id,source,external_id), unique(org_id,id)
);
create table public.notice_versions (
 id uuid primary key default gen_random_uuid(), org_id uuid not null, notice_id uuid not null,
 version integer not null check(version>0), source_hash text not null check(source_hash ~ '^[a-f0-9]{64}$'),
 raw_json jsonb not null check(jsonb_typeof(raw_json)='object'), title text not null check(length(trim(title))>0),
 buyer text, source_url text not null check(source_url ~ '^https://'),
 published_at timestamptz not null, deadline timestamptz, fetched_at timestamptz not null,
 cancelled boolean, cpv_codes text[] not null default '{}',
 created_at timestamptz not null default now(), unique(org_id,notice_id,version), unique(org_id,notice_id,source_hash),
 unique(org_id,id), foreign key(org_id,notice_id) references public.notices(org_id,id)
);
create table public.source_evidence (
 id uuid primary key default gen_random_uuid(), org_id uuid not null, notice_version_id uuid not null,
 field_path text not null check(length(trim(field_path))>0), excerpt text not null check(length(trim(excerpt))>0),
 source_url text not null check(source_url ~ '^https://'), locator text, checked_at timestamptz not null,
 created_at timestamptz not null default now(), unique(org_id,notice_version_id,id),
 foreign key(org_id,notice_version_id) references public.notice_versions(org_id,id)
);
create table public.assessments (
 id uuid primary key default gen_random_uuid(), org_id uuid not null, client_id uuid not null,
 profile_version_id uuid not null, notice_version_id uuid not null,
 rule_version text not null check(length(trim(rule_version))>0),
 queue_state text not null default 'NEW' check(queue_state in ('NEW','REVIEWING','READY','EXCLUDED','NEEDS_REVIEW')),
 checks_decision text not null default 'CONDITIONAL' check(checks_decision in ('CONDITIONAL','CHECKS_PASS','NO_GO')),
 review_coverage text not null default 'NONE' check(review_coverage in ('NONE','PARTIAL','COMPLETE')),
 facts jsonb not null default '[]' check(jsonb_typeof(facts)='array'),
 assessment text, missing text[] not null default '{}', next_action text, exclusion_reason text,
 row_version integer not null default 1 check(row_version>0),
 created_by uuid not null references auth.users(id), created_at timestamptz not null default now(),
 check(queue_state<>'EXCLUDED' or length(trim(exclusion_reason))>0 and exclusion_reason is not null),
 unique(org_id,client_id,profile_version_id,notice_version_id,rule_version),
 unique(org_id,client_id,profile_version_id,id),
 foreign key(org_id,client_id,profile_version_id) references public.client_profile_versions(org_id,client_id,id),
 foreign key(org_id,notice_version_id) references public.notice_versions(org_id,id)
);
create table public.assessment_evidence (
 org_id uuid not null, assessment_id uuid not null, notice_version_id uuid not null, evidence_id uuid not null,
 created_at timestamptz not null default now(), primary key(assessment_id,evidence_id),
 foreign key(org_id,notice_version_id,evidence_id) references public.source_evidence(org_id,notice_version_id,id)
);
alter table public.assessments add unique(org_id,notice_version_id,id);
alter table public.assessment_evidence add foreign key(org_id,notice_version_id,assessment_id)
 references public.assessments(org_id,notice_version_id,id);
create table public.digests (
 id uuid primary key default gen_random_uuid(), org_id uuid not null, client_id uuid not null,
 delivery_date date not null, mode text not null check(mode in ('REAL','SIMULATION')),
 row_version integer not null default 1 check(row_version>0), created_at timestamptz not null default now(),
 unique(org_id,client_id,id), foreign key(org_id,client_id) references public.clients(org_id,id)
);
-- Each version is an immutable snapshot, even before approval. A correction creates a new version.
create table public.digest_versions (
 id uuid primary key default gen_random_uuid(), org_id uuid not null, client_id uuid not null,
 digest_id uuid not null, profile_version_id uuid not null, version integer not null check(version>0),
 template_version text not null, snapshot jsonb not null check(jsonb_typeof(snapshot)='object'),
 content_hash text not null check(content_hash ~ '^[a-f0-9]{64}$'),
 approval text not null default 'SNAPSHOT' check(approval in ('SNAPSHOT','APPROVED')),
 qa_pass boolean not null default false, approved_by uuid references auth.users(id), approved_at timestamptz,
 created_by uuid not null references auth.users(id), created_at timestamptz not null default now(),
 check((approval='APPROVED' and qa_pass and approved_by is not null and approved_at is not null)
 or (approval='SNAPSHOT' and approved_by is null and approved_at is null)),
 unique(org_id,digest_id,version), unique(org_id,client_id,profile_version_id,id), unique(org_id,id),
 foreign key(org_id,client_id,digest_id) references public.digests(org_id,client_id,id),
 foreign key(org_id,client_id,profile_version_id) references public.client_profile_versions(org_id,client_id,id)
);
create table public.digest_items (
 org_id uuid not null, client_id uuid not null, profile_version_id uuid not null, digest_version_id uuid not null,
 assessment_id uuid not null, position integer not null check(position between 1 and 10),
 snapshot jsonb not null check(jsonb_typeof(snapshot)='object'),
 created_at timestamptz not null default now(), primary key(digest_version_id,position),
 unique(digest_version_id,assessment_id),
 foreign key(org_id,client_id,profile_version_id,digest_version_id)
 references public.digest_versions(org_id,client_id,profile_version_id,id),
 foreign key(org_id,client_id,profile_version_id,assessment_id)
 references public.assessments(org_id,client_id,profile_version_id,id)
);
create table public.delivery_events (
 id uuid primary key default gen_random_uuid(), org_id uuid not null, digest_version_id uuid not null,
 event_type text not null check(event_type in ('EXPORT_CREATED','SENT_RECORDED','CORRECTION')),
 evidence_reference text not null check(length(trim(evidence_reference))>0),
 idempotency_key uuid not null, actor_id uuid not null references auth.users(id),
 occurred_at timestamptz not null, created_at timestamptz not null default now(),
 unique(org_id,idempotency_key), foreign key(org_id,digest_version_id) references public.digest_versions(org_id,id)
);
create index memberships_user on public.operator_memberships(user_id,active,org_id);
create index clients_queue on public.clients(org_id,status);
create index profile_history on public.client_profile_versions(client_id,version desc);
create index notice_history on public.notice_versions(notice_id,version desc);
create index assessment_queue on public.assessments(org_id,client_id,queue_state);
create index digest_history on public.digests(org_id,client_id,delivery_date desc);
create index delivery_history on public.delivery_events(org_id,digest_version_id,occurred_at);
commit;
