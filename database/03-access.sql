begin;
-- auth.uid() is supplied by Supabase Auth. The M0 bootstrap cookie does not grant database access.
alter table public.operator_memberships enable row level security;
create policy membership_self on public.operator_memberships for select to authenticated
 using(user_id=(select auth.uid()) and active);
revoke all on public.operator_memberships from public,anon,authenticated;
grant select on public.operator_memberships to authenticated;
alter table public.organizations enable row level security;
create policy organization_read on public.organizations for select to authenticated
 using(exists(select 1 from public.operator_memberships m where m.org_id=id and m.user_id=(select auth.uid()) and m.active));
revoke all on public.organizations from public,anon,authenticated;
grant select on public.organizations to authenticated;
do $$ declare t text; begin
 foreach t in array array['clients','client_profile_versions','notices','notice_versions','source_evidence',
  'assessments','assessment_evidence','digests','digest_versions','digest_items','delivery_events'] loop
  execute format('alter table public.%I enable row level security',t);
  execute format('revoke all on public.%I from public,anon,authenticated',t);
  execute format('grant select,insert on public.%I to authenticated',t);
  execute format('create policy member_read on public.%I for select to authenticated using(exists(select 1 from public.operator_memberships m where m.org_id=%I.org_id and m.user_id=(select auth.uid()) and m.active))',t,t);
  execute format('create policy editor_insert on public.%I for insert to authenticated with check(exists(select 1 from public.operator_memberships m where m.org_id=%I.org_id and m.user_id=(select auth.uid()) and m.active and m.role in (''ADMIN'',''EDITOR'')))',t,t);
 end loop;
 foreach t in array array['clients','assessments','digests'] loop
  execute format('grant update on public.%I to authenticated',t);
  execute format('create policy editor_update on public.%I for update to authenticated using(exists(select 1 from public.operator_memberships m where m.org_id=%I.org_id and m.user_id=(select auth.uid()) and m.active and m.role in (''ADMIN'',''EDITOR''))) with check(exists(select 1 from public.operator_memberships m where m.org_id=%I.org_id and m.user_id=(select auth.uid()) and m.active and m.role in (''ADMIN'',''EDITOR'')))',t,t,t);
 end loop;
end $$;
-- Bind recorded actors to the authenticated operator, without trusting user_metadata.
do $$ declare t text; begin
 foreach t in array array['client_profile_versions','assessments','digest_versions'] loop
  execute format('create policy actor_binding on public.%I as restrictive for insert to authenticated with check(created_by=(select auth.uid()))',t);
 end loop;
end $$;
create policy approval_actor on public.digest_versions as restrictive for insert to authenticated
 with check(approved_by is null or approved_by=(select auth.uid()));
create policy event_actor on public.delivery_events as restrictive for insert to authenticated
 with check(actor_id=(select auth.uid()));
-- No UPDATE/DELETE on versions/events, no self-enrollment or membership escalation.
commit;
