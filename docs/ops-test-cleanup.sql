-- PREVIEW TEST PROJECT ONLY. Apply separately; never grant table DELETE to the app.
begin;
create or replace function public.urakkaluotsi_cleanup_e2e(
 p_workspace text, p_run uuid, p_version bigint
) returns boolean
language plpgsql security definer set search_path = '' as $$
declare saved public.urakkaluotsi_ops_state%rowtype;
begin
 if p_workspace is null or p_run is null or p_version is null or p_version < 1
  or p_workspace !~ '^(preview-e2e-|pr12-e2e-)[a-z0-9_-]+$' then
  raise exception 'Not an isolated E2E workspace' using errcode='22023';
 end if;
 select * into saved from public.urakkaluotsi_ops_state
  where workspace_id=p_workspace for update;
 if not found then return false; end if;
 if saved.storage_version <> p_version then
  raise exception 'Workspace changed; cleanup refused' using errcode='40001';
 end if;
 if saved.state->>'mode' <> 'SIMULATION'
  or jsonb_array_length(saved.state->'clients')=0
  or exists(select 1 from jsonb_array_elements(saved.state->'clients') c
    where coalesce(c->>'name','') not like 'E2E-SYNTHETIC-%'||p_run::text||'%'
       or coalesce(c->>'delivery_email','') not like '%@example.invalid')
  or exists(select 1 from jsonb_array_elements(saved.state->'notices') n
    where coalesce(n->>'source_url','') not like 'https://example.invalid/%') then
  raise exception 'Run ownership or synthetic data check failed' using errcode='22023';
 end if;
 delete from public.urakkaluotsi_ops_state
  where workspace_id=p_workspace and storage_version=p_version;
 return true;
end;
$$;
revoke all on function public.urakkaluotsi_cleanup_e2e(text,uuid,bigint) from public,anon,authenticated;
grant execute on function public.urakkaluotsi_cleanup_e2e(text,uuid,bigint) to service_role;
commit;
