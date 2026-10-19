begin;
create table public.work_sessions (
 id uuid primary key default gen_random_uuid(),org_id uuid not null,client_id uuid not null,
 actor_id uuid not null references auth.users(id),phase text not null check(phase in ('ONBOARDING','DELIVERY')),
 mode text not null check(mode in ('REAL','SIMULATION')),started_at timestamptz not null,ended_at timestamptz,
 created_at timestamptz not null default now(),check(ended_at is null or ended_at>=started_at),
 foreign key(org_id,client_id) references public.clients(org_id,id)
);
create unique index one_active_timer on public.work_sessions(actor_id) where ended_at is null;
create index timed_client_days on public.work_sessions(org_id,client_id,started_at);
create table public.delivery_corrections (
 id uuid primary key default gen_random_uuid(),org_id uuid not null,digest_version_id uuid not null,
 category text not null check(category in ('SOURCE','PROFILE','CONTENT','EXPORT')),
 reason text not null check(length(trim(reason))>0),actor_id uuid not null references auth.users(id),
 created_at timestamptz not null default now(),
 foreign key(org_id,digest_version_id) references public.digest_versions(org_id,id)
);
create table public.feedback (
 id uuid primary key default gen_random_uuid(),org_id uuid not null,digest_version_id uuid not null,
 assessment_id uuid not null,label text not null check(label in ('USEFUL','NOT_USEFUL','UNKNOWN')),
 mode text not null check(mode in ('REAL','SIMULATION')),
 source text not null check(source in ('CUSTOMER','INTERNAL_SIMULATION')),
 reason text not null check(length(trim(reason))>0),evidence_reference text not null check(length(trim(evidence_reference))>0),
 actor_id uuid not null references auth.users(id),created_at timestamptz not null default now(),
 check((source='CUSTOMER' and mode='REAL') or (source='INTERNAL_SIMULATION' and mode='SIMULATION')),
 foreign key(digest_version_id,assessment_id) references public.digest_items(digest_version_id,assessment_id),
 foreign key(org_id,digest_version_id) references public.digest_versions(org_id,id)
);
create index feedback_versions on public.feedback(org_id,digest_version_id,assessment_id,created_at desc);
create function public.stop_work_session() returns trigger language plpgsql security invoker set search_path='' as $$
begin
 if tg_op='DELETE' then raise exception 'Timer history immutable' using errcode='23514'; end if;
 if old.ended_at is not null or new.ended_at is null or (to_jsonb(new)-'ended_at')<>(to_jsonb(old)-'ended_at') then
  raise exception 'Only stop an active timer' using errcode='23514';
 end if;
 return new;
end $$;
create trigger timer_history before update or delete on public.work_sessions for each row execute function public.stop_work_session();
create function public.guard_feedback_source() returns trigger language plpgsql security invoker set search_path='' as $$
declare actual_mode text;
begin
 select d.mode into actual_mode from public.digest_versions v join public.digests d on d.id=v.digest_id where v.org_id=new.org_id and v.id=new.digest_version_id;
 if new.mode is distinct from actual_mode then raise exception 'Feedback mode mismatch' using errcode='23514'; end if;
 if new.source='CUSTOMER' and not exists(select 1 from public.delivery_events where org_id=new.org_id and digest_version_id=new.digest_version_id and event_type='SENT_RECORDED') then
  raise exception 'Customer feedback requires recorded delivery' using errcode='23514';
 end if;
 return new;
end $$;
create function public.guard_correction_export() returns trigger language plpgsql security invoker set search_path='' as $$
begin
 if not exists(select 1 from public.delivery_events where org_id=new.org_id and digest_version_id=new.digest_version_id and event_type='EXPORT_CREATED') then
  raise exception 'Correction requires exported version' using errcode='23514';
 end if;
 return new;
end $$;
revoke all on function public.guard_correction_export() from public,anon,authenticated;
create trigger correction_export before insert on public.delivery_corrections for each row execute function public.guard_correction_export();
create trigger feedback_origin before insert on public.feedback for each row execute function public.guard_feedback_source();
create trigger corrections_immutable before update or delete on public.delivery_corrections for each row execute function public.reject_history_change();
create trigger feedback_immutable before update or delete on public.feedback for each row execute function public.reject_history_change();
revoke all on function public.stop_work_session(),public.guard_feedback_source() from public,anon,authenticated;
do $$ declare t text; begin
 foreach t in array array['work_sessions','delivery_corrections','feedback'] loop
  execute format('alter table public.%I enable row level security',t);
  execute format('revoke all on public.%I from public,anon,authenticated',t);
  execute format('grant select,insert on public.%I to authenticated',t);
  execute format('create policy metrics_read on public.%I for select to authenticated using(exists(select 1 from public.operator_memberships m where m.org_id=%I.org_id and m.user_id=(select auth.uid()) and m.active))',t,t);
  execute format('create policy metrics_write on public.%I for insert to authenticated with check(actor_id=(select auth.uid()) and exists(select 1 from public.operator_memberships m where m.org_id=%I.org_id and m.user_id=(select auth.uid()) and m.active and m.role in (''ADMIN'',''EDITOR'')))',t,t);
 end loop;
end $$;
grant update(ended_at) on public.work_sessions to authenticated;
create policy timer_stop on public.work_sessions for update to authenticated
 using(actor_id=(select auth.uid()) and exists(select 1 from public.operator_memberships m where m.org_id=work_sessions.org_id and m.user_id=(select auth.uid()) and m.active and m.role in ('ADMIN','EDITOR')))
 with check(actor_id=(select auth.uid()) and exists(select 1 from public.operator_memberships m where m.org_id=work_sessions.org_id and m.user_id=(select auth.uid()) and m.active and m.role in ('ADMIN','EDITOR')));
commit;
