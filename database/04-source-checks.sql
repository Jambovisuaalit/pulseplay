begin;
-- Refreshing an unchanged source appends a check; it does not rewrite an immutable version.
create table public.source_checks (
 id uuid primary key default gen_random_uuid(),org_id uuid not null,notice_version_id uuid not null,
 source_hash text not null check(source_hash ~ '^[a-f0-9]{64}$'),
 checked_at timestamptz not null,checked_by uuid not null references auth.users(id),
 outcome text not null check(outcome in ('UNCHANGED','CHANGED','FAILED')),
 created_at timestamptz not null default now(),
 foreign key(org_id,notice_version_id) references public.notice_versions(org_id,id)
);
create index source_check_latest on public.source_checks(org_id,notice_version_id,checked_at desc);
alter table public.source_checks enable row level security;
revoke all on public.source_checks from public,anon,authenticated;
grant select,insert on public.source_checks to authenticated;
create policy source_checks_read on public.source_checks for select to authenticated
 using(exists(select 1 from public.operator_memberships m where m.org_id=source_checks.org_id and m.user_id=(select auth.uid()) and m.active));
create policy source_checks_insert on public.source_checks for insert to authenticated
 with check(checked_by=(select auth.uid()) and exists(select 1 from public.operator_memberships m
 where m.org_id=source_checks.org_id and m.user_id=(select auth.uid()) and m.active and m.role in ('ADMIN','EDITOR')));
create trigger immutable_history before update or delete on public.source_checks
 for each row execute function public.reject_history_change();
-- Item rows can only mirror the authoritative frozen snapshot, never extend its contents.
create function public.guard_digest_item() returns trigger language plpgsql security invoker set search_path='' as $$
declare item jsonb;
begin
 select snapshot->'items'->(new.position-1) into item from public.digest_versions where id=new.digest_version_id and org_id=new.org_id;
 if item is null or item<>new.snapshot or (item->>'assessment_id') is distinct from new.assessment_id::text then
  raise exception 'Item does not match frozen snapshot' using errcode='23514';
 end if;
 return new;
end $$;
revoke all on function public.guard_digest_item() from public,anon,authenticated;
create trigger frozen_item before insert on public.digest_items for each row execute function public.guard_digest_item();
commit;
