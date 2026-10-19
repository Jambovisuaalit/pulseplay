begin;
create function public.reject_history_change() returns trigger language plpgsql
 security invoker set search_path='' as $$
begin
 raise exception 'Immutable history: insert a new version' using errcode='23514';
end $$;
create function public.bump_row_version() returns trigger language plpgsql
 security invoker set search_path='' as $$
begin
 if new.org_id<>old.org_id or new.id<>old.id or new.created_at<>old.created_at then
  raise exception 'Identity cannot change' using errcode='23514';
 end if;
 if tg_table_name='assessments' and ((to_jsonb(new)->'client_id')<>(to_jsonb(old)->'client_id') or (to_jsonb(new)->'profile_version_id')<>(to_jsonb(old)->'profile_version_id') or (to_jsonb(new)->'notice_version_id')<>(to_jsonb(old)->'notice_version_id') or (to_jsonb(new)->'created_by')<>(to_jsonb(old)->'created_by')) then
  raise exception 'Assessment version references cannot change' using errcode='23514';
 end if;
 if new.row_version<>old.row_version+1 then
  raise exception 'Expected next row_version' using errcode='40001';
 end if;
 return new;
end $$;
create function public.validate_profile_facts(facts jsonb) returns boolean language plpgsql
 immutable security invoker set search_path='' as $$
declare fact jsonb; keys text[] := '{}';
begin
 if jsonb_typeof(facts)<>'array' then return false; end if;
 for fact in select value from jsonb_array_elements(facts) loop
  if jsonb_typeof(fact)<>'object' or not (fact ?& array['key','value','verification','source','verified_at'])
   or jsonb_typeof(fact->'key')<>'string' or length(trim(fact->>'key'))=0
   or (fact->>'key')=any(keys) then return false; end if;
  keys := array_append(keys,fact->>'key');
  if fact->>'verification'='UNKNOWN' then
   if fact->'value'<>'null'::jsonb or fact->'source'<>'null'::jsonb or fact->'verified_at'<>'null'::jsonb then return false; end if;
  elsif fact->>'verification' in ('INFERRED','CONFIRMED') then
   if jsonb_typeof(fact->'value') not in ('string','number','boolean') or jsonb_typeof(fact->'source')<>'string'
    or length(trim(fact->>'source'))=0 then return false; end if;
   if fact->>'verification'='CONFIRMED' then
    if jsonb_typeof(fact->'verified_at')<>'string' or (fact->>'verified_at') !~ '(Z|[+-][0-9]{2}:[0-9]{2})$'
     then return false; end if;
    perform (fact->>'verified_at')::timestamptz;
   elsif fact->'verified_at'<>'null'::jsonb then return false; end if;
  else return false;
  end if;
 end loop;
 return true;
exception when invalid_datetime_format or datetime_field_overflow then return false;
end $$;
alter table public.client_profile_versions add check(public.validate_profile_facts(facts));
create function public.guard_delivery_event() returns trigger language plpgsql
 security invoker set search_path='' as $$
begin
 if not exists(select 1 from public.digest_versions v where v.org_id=new.org_id
   and v.id=new.digest_version_id and v.approval='APPROVED') then
  raise exception 'Delivery event requires approved version' using errcode='23514';
 end if;
 return new;
end $$;
create trigger delivery_approval before insert on public.delivery_events
 for each row execute function public.guard_delivery_event();
do $$ declare t text; begin
 foreach t in array array['client_profile_versions','notice_versions','source_evidence','digest_versions','digest_items','delivery_events'] loop
  execute format('create trigger immutable_history before update or delete on public.%I for each row execute function public.reject_history_change()',t);
 end loop;
 foreach t in array array['clients','assessments','digests'] loop
  execute format('create trigger optimistic_version before update on public.%I for each row execute function public.bump_row_version()',t);
 end loop;
end $$;
-- No functions run with elevated privileges; trigger functions are not public RPCs.
revoke all on function public.reject_history_change(), public.bump_row_version(), public.guard_delivery_event(),
 public.validate_profile_facts(jsonb) from public,anon;
grant execute on function public.validate_profile_facts(jsonb) to authenticated;
commit;
