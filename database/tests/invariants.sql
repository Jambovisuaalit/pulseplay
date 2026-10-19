\set ON_ERROR_STOP on
begin;
create function public.test_assert(ok boolean,label text) returns void language plpgsql as $$
begin if ok is not true then raise exception 'FAIL: %',label; end if; raise notice 'PASS: %',label; end $$;
create function public.test_reject(query text,code text,label text) returns void language plpgsql as $$
declare actual text; begin
 begin execute query; exception when others then get stacked diagnostics actual=returned_sqlstate; end;
 if actual is distinct from code then raise exception 'FAIL: %, expected %, got %',label,code,actual; end if;
 raise notice 'PASS: %',label;
end $$;
insert into auth.users values ('10000000-0000-0000-0000-000000000001'),('10000000-0000-0000-0000-000000000002'),('10000000-0000-0000-0000-000000000003');
insert into public.organizations(id,name) values ('20000000-0000-0000-0000-000000000001','Synthetic A'),('20000000-0000-0000-0000-000000000002','Synthetic B');
insert into public.operator_memberships(org_id,user_id,role) values
 ('20000000-0000-0000-0000-000000000001','10000000-0000-0000-0000-000000000001','EDITOR'),
 ('20000000-0000-0000-0000-000000000001','10000000-0000-0000-0000-000000000002','VIEWER');
insert into public.clients(id,org_id,name) values
 ('30000000-0000-0000-0000-000000000001','20000000-0000-0000-0000-000000000001','Synthetic A'),
 ('30000000-0000-0000-0000-000000000002','20000000-0000-0000-0000-000000000002','Synthetic B');
set local role anon;
select public.test_reject('select * from public.clients','42501','anonymous cannot read clients');
reset role;
set local request.jwt.claim.sub='10000000-0000-0000-0000-000000000001';
set local role authenticated;
select public.test_assert((select count(*)=1 from public.clients),'operator sees only own organization');
select public.test_assert((select count(*)=1 from public.organizations),'organization RLS');
select public.test_reject($q$insert into public.clients(org_id,name) values ('20000000-0000-0000-0000-000000000002','Cross org')$q$,'42501','cross organization write blocked');
select public.test_reject($q$insert into public.operator_memberships(org_id,user_id,role) values ('20000000-0000-0000-0000-000000000002','10000000-0000-0000-0000-000000000001','ADMIN')$q$,'42501','self enrollment blocked');
insert into public.client_profile_versions(id,org_id,client_id,version,created_by) values
 ('40000000-0000-0000-0000-000000000001','20000000-0000-0000-0000-000000000001','30000000-0000-0000-0000-000000000001',1,'10000000-0000-0000-0000-000000000001');
select public.test_reject($q$insert into public.client_profile_versions(org_id,client_id,version,created_by) values ('20000000-0000-0000-0000-000000000001','30000000-0000-0000-0000-000000000001',2,'10000000-0000-0000-0000-000000000002')$q$,'42501','forged actor blocked');
select public.test_reject($q$update public.clients set name='Clobber' where id='30000000-0000-0000-0000-000000000001'$q$,'40001','missing row version blocked');
update public.clients set name='Updated',row_version=2 where id='30000000-0000-0000-0000-000000000001' and row_version=1;
select public.test_assert((select row_version=2 from public.clients limit 1),'optimistic update succeeds');
select public.test_reject($q$update public.clients set org_id='20000000-0000-0000-0000-000000000002',row_version=3$q$,'23514','organization reassignment blocked');
reset role;
select public.test_reject($q$update public.client_profile_versions set services=array['Changed']$q$,'23514','profile versions immutable even for owner');
select public.test_reject($q$insert into public.client_profile_versions(org_id,client_id,version,created_by) values ('20000000-0000-0000-0000-000000000001','30000000-0000-0000-0000-000000000002',1,'10000000-0000-0000-0000-000000000001')$q$,'23503','cross client/org foreign key blocked');
select public.test_reject($q$insert into public.client_profile_versions(org_id,client_id,version,created_by) values ('20000000-0000-0000-0000-000000000001','30000000-0000-0000-0000-000000000001',1,'10000000-0000-0000-0000-000000000001')$q$,'23505','duplicate profile version blocked');
select public.test_assert(not public.validate_profile_facts('[{"key":"cert","value":false,"verification":"UNKNOWN","source":null,"verified_at":null}]'),'unknown is not confirmed false');
select public.test_assert(public.validate_profile_facts('[{"key":"cert","value":false,"verification":"CONFIRMED","source":"Synthetic interview","verified_at":"2026-10-19T00:00:00Z"}]'),'confirmed negative is explicit');
insert into public.notices(id,org_id,external_id) values ('50000000-0000-0000-0000-000000000001','20000000-0000-0000-0000-000000000001','123');
insert into public.notice_versions(id,org_id,notice_id,version,source_hash,raw_json,title,source_url,published_at,fetched_at) values
 ('60000000-0000-0000-0000-000000000001','20000000-0000-0000-0000-000000000001','50000000-0000-0000-0000-000000000001',1,repeat('a',64),'{}','Synthetic','https://example.invalid',now(),now());
select public.test_reject($q$update public.notice_versions set title='Changed'$q$,'23514','source versions immutable');
insert into public.assessments(id,org_id,client_id,profile_version_id,notice_version_id,rule_version,created_by) values
 ('70000000-0000-0000-0000-000000000001','20000000-0000-0000-0000-000000000001','30000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000001','60000000-0000-0000-0000-000000000001','v1','10000000-0000-0000-0000-000000000001');
select public.test_reject($q$update public.assessments set queue_state='EXCLUDED',row_version=2$q$,'23514','exclusion needs reason');
insert into public.digests(id,org_id,client_id,delivery_date,mode) values
 ('80000000-0000-0000-0000-000000000001','20000000-0000-0000-0000-000000000001','30000000-0000-0000-0000-000000000001',current_date,'SIMULATION');
insert into public.digest_versions(id,org_id,client_id,digest_id,profile_version_id,version,template_version,snapshot,content_hash,created_by) values
 ('90000000-0000-0000-0000-000000000001','20000000-0000-0000-0000-000000000001','30000000-0000-0000-0000-000000000001','80000000-0000-0000-0000-000000000001','40000000-0000-0000-0000-000000000001',1,'v1','{}',repeat('b',64),'10000000-0000-0000-0000-000000000001');
select public.test_reject($q$update public.digest_versions set snapshot='{"changed":true}'$q$,'23514','delivery snapshot immutable');
select public.test_reject($q$insert into public.delivery_events(org_id,digest_version_id,event_type,evidence_reference,idempotency_key,actor_id,occurred_at) values ('20000000-0000-0000-0000-000000000001','90000000-0000-0000-0000-000000000001','EXPORT_CREATED','synthetic',gen_random_uuid(),'10000000-0000-0000-0000-000000000001',now())$q$,'23514','unapproved export blocked');
set local request.jwt.claim.sub='10000000-0000-0000-0000-000000000002';
set local role authenticated;
select public.test_assert((select count(*)=1 from public.clients),'viewer reads own org');
select public.test_reject($q$insert into public.clients(org_id,name) values ('20000000-0000-0000-0000-000000000001','Viewer write')$q$,'42501','viewer cannot write');
with changed as (update public.clients set name='Viewer overwrite',row_version=row_version+1 returning id)
select public.test_assert((select count(*)=0 from changed),'viewer update affects zero rows');
reset role;
update public.operator_memberships set active=false where user_id='10000000-0000-0000-0000-000000000002';
set local role authenticated;
select public.test_assert((select count(*)=0 from public.clients),'revoked operator denied despite same JWT subject');
reset role;
set local request.jwt.claim.sub='10000000-0000-0000-0000-000000000003';
set local role authenticated;
select public.test_assert((select count(*)=0 from public.clients),'authenticated nonmember sees nothing');
reset role;
select public.test_assert((select bool_and(relrowsecurity) from pg_class where relnamespace='public'::regnamespace and relkind='r'),'RLS on all public tables');
rollback;
